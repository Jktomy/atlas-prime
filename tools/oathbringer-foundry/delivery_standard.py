"""Canonical operator boundary for deterministic Atlas PR delivery.

The operator surface compiles a Foundry carrier, preserves diagnostics, and
always emits a sanitized evidence archive. It does not write GitHub state,
persist credentials, ready a pull request, or merge a pull request. The sealed
carrier remains the only input to the Oathbringer runtime.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import stat
import subprocess
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence


IDENTITY = "CONSISTENT_PR_DELIVERY_STANDARD_R01"
FORMAT_VERSION = "1.0"
ZIP_EPOCH = (1980, 1, 1, 0, 0, 0)
REQUIRED_PLATFORMS = ("ubuntu-latest", "windows-latest")
EVIDENCE_MEMBERS = (
    "DELIVERY-RECEIPT.json",
    "MANIFEST.json",
    "SHA256SUMS.txt",
    "stderr.txt",
    "stdout.txt",
)
MAX_ARCHIVE_BYTES = 4_194_304
MAX_MEMBERS = len(EVIDENCE_MEMBERS)
MAX_MEMBER_BYTES = 1_048_576
MAX_TOTAL_BYTES = 2_097_152
MAX_JSON_DEPTH = 16
PEM_BLOCK = re.compile(
    r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----.*?"
    r"-----END (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
    re.DOTALL,
)
SENSITIVE = re.compile(
    r"(?:\b(?:Bearer|Basic)\s+[A-Za-z0-9._~+/=-]{8,}|"
    r"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}(?:\.[A-Za-z0-9_-]{8,})?\b|"
    r"\bgh[pousr]_[A-Za-z0-9]{20,}\b|\bgithub_pat_[A-Za-z0-9_]{20,}\b|"
    r"\bsk-[A-Za-z0-9_-]{20,}\b|\bAKIA[0-9A-Z]{16}\b|"
    r"(?:authorization|api[_-]?key|access[_-]?token|password|secret|recovery[_-]?code)"
    r"\s*[:=]\s*[^\r\n]+)",
    re.IGNORECASE,
)
FOUNDRY_RESULT_KEYS = {
    "carrier_path",
    "carrier_sha256",
    "manifest_sha256",
    "forge_receipt_sha256",
    "member_count",
    "bound_live_state_sha256",
    "compiler_is_writer",
}


class DeliveryError(RuntimeError):
    """The bounded delivery operator could not produce a safe success."""


@dataclass(frozen=True)
class CommandResult:
    returncode: int
    stdout: str
    stderr: str


def _canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sanitize(text: str) -> str:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    return SENSITIVE.sub("[REDACTED]", PEM_BLOCK.sub("[REDACTED]", normalized))


def _pairs_no_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DeliveryError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _json_depth(value: Any) -> int:
    if isinstance(value, dict):
        return 1 + max((_json_depth(item) for item in value.values()), default=0)
    if isinstance(value, list):
        return 1 + max((_json_depth(item) for item in value), default=0)
    return 1


def _bounded_json(data: bytes, field: str) -> Any:
    if len(data) > MAX_MEMBER_BYTES:
        raise DeliveryError(f"{field} exceeds the JSON byte limit")
    try:
        value = json.loads(data.decode("utf-8"), object_pairs_hook=_pairs_no_duplicates)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise DeliveryError(f"{field} is not valid UTF-8 JSON") from exc
    if _json_depth(value) > MAX_JSON_DEPTH:
        raise DeliveryError(f"{field} exceeds the JSON depth limit")
    return value


def _require_sha256(value: Any, field: str) -> str:
    text = str(value or "")
    if re.fullmatch(r"[0-9a-f]{64}", text) is None:
        raise DeliveryError(f"{field} must be a lowercase SHA-256")
    return text


def _validate_foundry_result(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != FOUNDRY_RESULT_KEYS:
        raise DeliveryError("Foundry result does not match the trusted result contract")
    if value.get("compiler_is_writer") is not False:
        raise DeliveryError("Foundry result incorrectly claims writer authority")
    member_count = value.get("member_count")
    if not isinstance(member_count, int) or isinstance(member_count, bool) or not 1 <= member_count <= 256:
        raise DeliveryError("Foundry result member_count is invalid")
    carrier_path = str(value.get("carrier_path") or "")
    carrier_name = Path(carrier_path).name
    if not carrier_name or carrier_name != carrier_path.replace("\\", "/").split("/")[-1] or "\n" in carrier_name:
        raise DeliveryError("Foundry result carrier_path is invalid")
    return {
        "carrier_name": carrier_name,
        "carrier_sha256": _require_sha256(value.get("carrier_sha256"), "carrier_sha256"),
        "manifest_sha256": _require_sha256(value.get("manifest_sha256"), "manifest_sha256"),
        "forge_receipt_sha256": _require_sha256(value.get("forge_receipt_sha256"), "forge_receipt_sha256"),
        "member_count": member_count,
        "bound_live_state_sha256": _require_sha256(value.get("bound_live_state_sha256"), "bound_live_state_sha256"),
        "compiler_is_writer": False,
    }


def parse_ls_tree_record(record: str) -> dict[str, str]:
    """Parse the exact ``git ls-tree`` metadata/TAB/path wire format."""

    metadata, separator, path = record.rstrip("\n").partition("\t")
    fields = metadata.split(" ")
    if separator != "\t" or len(fields) != 3 or not path:
        raise DeliveryError("git ls-tree record must be '<mode> <type> <sha>\\t<path>'")
    mode, object_type, object_sha = fields
    if re.fullmatch(r"[0-7]{6}", mode) is None:
        raise DeliveryError("git ls-tree mode is invalid")
    if object_type not in {"blob", "tree", "commit"}:
        raise DeliveryError("git ls-tree object type is invalid")
    if re.fullmatch(r"[0-9a-f]{40}", object_sha) is None:
        raise DeliveryError("git ls-tree object SHA is invalid")
    return {"mode": mode, "object_type": object_type, "object_sha": object_sha, "path": path}


def classify_branch_response(response: Mapping[str, Any] | None, branch: str) -> str:
    """Turn a read-only 404/None response into an explicit branch state."""

    if response is None:
        return "MISSING"
    if not isinstance(response, Mapping):
        raise DeliveryError("branch response is malformed")
    if response.get("ref") != f"refs/heads/{branch}":
        raise DeliveryError("branch response does not bind the requested branch")
    return "PRESENT"


def validate_exact_audit(receipt: Mapping[str, Any], expected_head: str) -> None:
    if set(receipt) != {"verdict", "exact_head"}:
        raise DeliveryError("audit receipt must contain only verdict and exact_head")
    if receipt.get("verdict") != "GREEN" or receipt.get("exact_head") != expected_head:
        raise DeliveryError("audit receipt is not GREEN at the exact head")


def validate_workflow_platforms(platforms: Sequence[str]) -> tuple[str, str]:
    values = tuple(str(item) for item in platforms)
    if values != REQUIRED_PLATFORMS:
        raise DeliveryError("workflow applicability must name exact ubuntu-latest and windows-latest lanes")
    return REQUIRED_PLATFORMS


def parse_foundry_result(result: CommandResult) -> dict[str, Any]:
    """Preserve the real diagnostic before attempting JSON interpretation."""

    diagnostic = _sanitize("\n".join(item.strip() for item in (result.stderr, result.stdout) if item.strip()))
    if result.returncode != 0:
        raise DeliveryError(f"Foundry command failed: {diagnostic or 'no diagnostic returned'}")
    try:
        value = json.loads(result.stdout, object_pairs_hook=_pairs_no_duplicates)
    except (json.JSONDecodeError, DeliveryError) as exc:
        raise DeliveryError(f"Foundry returned invalid JSON: {diagnostic or 'no diagnostic returned'}") from exc
    return _validate_foundry_result(value)


def retain_primary_success(primary: dict[str, Any], post_stop_probe: Callable[[], Any] | None) -> dict[str, Any]:
    """A nonessential after-stop probe may warn but cannot reverse success."""

    result = dict(primary)
    if post_stop_probe is None:
        return result
    try:
        post_stop_probe()
    except Exception as exc:  # bounded nonessential diagnostic only
        result["post_stop_warning"] = _sanitize(f"{type(exc).__name__}: {exc}")
    return result


def _run(arguments: Sequence[str], cwd: Path) -> CommandResult:
    completed = subprocess.run(list(arguments), cwd=cwd, check=False, capture_output=True, text=True, encoding="utf-8")
    return CommandResult(completed.returncode, completed.stdout, completed.stderr)


def _write_evidence_archive(output_zip: Path, evidence: dict[str, Any], stdout: str, stderr: str) -> str:
    members: dict[str, bytes] = {
        "DELIVERY-RECEIPT.json": _canonical_json(evidence),
        "stdout.txt": _sanitize(stdout).encode("utf-8"),
        "stderr.txt": _sanitize(stderr).encode("utf-8"),
    }
    manifest = {
        "format_version": FORMAT_VERSION,
        "files": [
            {"path": path, "bytes": len(members[path]), "sha256": _sha256(members[path])}
            for path in sorted(members)
        ],
    }
    members["MANIFEST.json"] = _canonical_json(manifest)
    members["SHA256SUMS.txt"] = "".join(
        f"{_sha256(members[path])}  {path}\n" for path in sorted(members)
    ).encode("ascii")
    output_zip.parent.mkdir(parents=True, exist_ok=True)
    if output_zip.is_symlink() or output_zip.with_suffix(output_zip.suffix + ".sha256").is_symlink():
        raise DeliveryError("evidence output and sidecar must not be symlinks")
    with zipfile.ZipFile(output_zip, "w", compression=zipfile.ZIP_STORED, strict_timestamps=True) as archive:
        for path in sorted(members):
            info = zipfile.ZipInfo(path, ZIP_EPOCH)
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            info.compress_type = zipfile.ZIP_STORED
            archive.writestr(info, members[path])
    sidecar = output_zip.with_suffix(output_zip.suffix + ".sha256")
    digest = _sha256(output_zip.read_bytes())
    sidecar.write_text(f"{digest}  {output_zip.name}\n", encoding="ascii", newline="\n")
    return digest


def compile_with_evidence(
    *,
    input_root: Path,
    source_root: Path,
    output_dir: Path,
    evidence_zip: Path,
    platforms: Sequence[str],
    runner: Callable[[Sequence[str], Path], CommandResult] = _run,
    post_stop_probe: Callable[[], Any] | None = None,
) -> dict[str, Any]:
    """Run the canonical Foundry compile and always finish outer evidence."""

    validate_workflow_platforms(platforms)
    command = (
        sys.executable,
        "-B",
        str((source_root / "tools" / "oathbringer-foundry" / "cli.py").resolve()),
        "compile",
        "--input-root",
        str(input_root.resolve()),
        "--source-root",
        str(source_root.resolve()),
        "--output-dir",
        str(output_dir.resolve()),
        "--json",
    )
    captured = CommandResult(1, "", "operator did not start")
    receipt: dict[str, Any] = {
        "format_version": FORMAT_VERSION,
        "identity": IDENTITY,
        "result": "REJECTED",
        "workflow_platforms": list(REQUIRED_PLATFORMS),
        "compiler_is_writer": False,
        "direct_main_write": False,
        "credential_persistence": False,
        "evidence_contract": {
            "archive_filename": evidence_zip.name,
            "sidecar_filename": evidence_zip.name + ".sha256",
            "required_members": list(EVIDENCE_MEMBERS),
            "verification": "SIDECAR_PLUS_INDEPENDENT_SHA256",
        },
    }
    failure: DeliveryError | None = None
    try:
        captured = runner(command, source_root)
        foundry = parse_foundry_result(captured)
        receipt.update({"result": "SUCCESS", "foundry": foundry})
        receipt = retain_primary_success(receipt, post_stop_probe)
    except Exception as exc:
        failure = exc if isinstance(exc, DeliveryError) else DeliveryError(_sanitize(f"{type(exc).__name__}: {exc}"))
        receipt["diagnostic"] = str(failure)
    finally:
        safe_stdout = _canonical_json(receipt.get("foundry", {})).decode("utf-8") if receipt["result"] == "SUCCESS" else ""
        safe_stderr = "" if receipt["result"] == "SUCCESS" else captured.stderr
        receipt["evidence_sha256"] = _write_evidence_archive(
            evidence_zip,
            receipt,
            safe_stdout,
            safe_stderr,
        )
    if failure is not None:
        raise failure
    return receipt


def _validate_receipt(receipt: Any, path: Path, sidecar_path: Path) -> None:
    if not isinstance(receipt, dict):
        raise DeliveryError("delivery receipt must be an object")
    base_keys = {
        "format_version", "identity", "result", "workflow_platforms",
        "compiler_is_writer", "direct_main_write", "credential_persistence",
        "evidence_contract",
    }
    allowed = base_keys | {"foundry", "diagnostic", "post_stop_warning"}
    if not base_keys <= set(receipt) or not set(receipt) <= allowed:
        raise DeliveryError("delivery receipt does not match the trusted contract")
    if receipt["format_version"] != FORMAT_VERSION or receipt["identity"] != IDENTITY:
        raise DeliveryError("delivery receipt identity is untrusted")
    if receipt["workflow_platforms"] != list(REQUIRED_PLATFORMS):
        raise DeliveryError("delivery receipt platform binding is invalid")
    if any(receipt[key] is not False for key in ("compiler_is_writer", "direct_main_write", "credential_persistence")):
        raise DeliveryError("delivery receipt violates authority invariants")
    result = receipt.get("result")
    if result == "SUCCESS":
        if "foundry" not in receipt or "diagnostic" in receipt:
            raise DeliveryError("successful delivery receipt is incomplete")
        _validate_foundry_result({
            "carrier_path": receipt["foundry"].get("carrier_name") if isinstance(receipt["foundry"], dict) else None,
            **({key: value for key, value in receipt["foundry"].items() if key != "carrier_name"} if isinstance(receipt["foundry"], dict) else {}),
        })
    elif result == "REJECTED":
        if "diagnostic" not in receipt or "foundry" in receipt or not isinstance(receipt["diagnostic"], str):
            raise DeliveryError("rejected delivery receipt is incomplete")
    else:
        raise DeliveryError("delivery receipt result is invalid")
    contract = receipt.get("evidence_contract")
    expected_contract = {
        "archive_filename": path.name,
        "sidecar_filename": sidecar_path.name,
        "required_members": list(EVIDENCE_MEMBERS),
        "verification": "SIDECAR_PLUS_INDEPENDENT_SHA256",
    }
    if contract != expected_contract:
        raise DeliveryError("delivery receipt evidence binding is invalid")


def _verify_evidence(path: Path, *, sidecar_path: Path, expected_sha256: str) -> dict[str, Any]:
    expected = _require_sha256(expected_sha256, "expected_sha256")
    if not path.is_file() or path.is_symlink() or path.stat().st_size > MAX_ARCHIVE_BYTES:
        raise DeliveryError("evidence archive is missing, linked, or oversized")
    if not sidecar_path.is_file() or sidecar_path.is_symlink() or sidecar_path.stat().st_size > 256:
        raise DeliveryError("independent evidence sidecar is missing or unsafe")
    try:
        sidecar = sidecar_path.read_text(encoding="ascii").splitlines()
    except (OSError, UnicodeDecodeError) as exc:
        raise DeliveryError("independent evidence sidecar is unreadable") from exc
    if sidecar != [f"{expected}  {path.name}"]:
        raise DeliveryError("independent evidence sidecar binding mismatch")
    data = path.read_bytes()
    if _sha256(data) != expected:
        raise DeliveryError("independent evidence SHA-256 mismatch")
    with zipfile.ZipFile(path, "r") as archive:
        infos = archive.infolist()
        names = [info.filename for info in infos]
        if len(infos) != MAX_MEMBERS or tuple(sorted(names)) != EVIDENCE_MEMBERS:
            raise DeliveryError("evidence archive does not match the exact member contract")
        total = 0
        for info in infos:
            if (
                info.is_dir()
                or info.flag_bits & 0x1
                or not stat.S_ISREG(info.external_attr >> 16)
                or info.compress_type != zipfile.ZIP_STORED
                or info.file_size != info.compress_size
                or info.file_size > MAX_MEMBER_BYTES
                or "\\" in info.filename
                or info.filename.startswith(("/", "//"))
                or any(part in {"", ".", ".."} for part in info.filename.split("/"))
            ):
                raise DeliveryError(f"evidence archive member is unsafe: {info.filename}")
            total += info.file_size
        if total > MAX_TOTAL_BYTES:
            raise DeliveryError("evidence archive exceeds the total byte limit")
        manifest = _bounded_json(archive.read("MANIFEST.json"), "MANIFEST.json")
        if not isinstance(manifest, dict) or set(manifest) != {"format_version", "files"} or manifest["format_version"] != FORMAT_VERSION or not isinstance(manifest["files"], list):
            raise DeliveryError("evidence manifest does not match the trusted contract")
        declared: dict[str, dict[str, Any]] = {}
        for item in manifest["files"]:
            if not isinstance(item, dict) or set(item) != {"path", "bytes", "sha256"}:
                raise DeliveryError("evidence manifest entry is malformed")
            member = item["path"]
            if member in declared or not isinstance(member, str) or not isinstance(item["bytes"], int) or isinstance(item["bytes"], bool):
                raise DeliveryError("evidence manifest entry is malformed")
            _require_sha256(item["sha256"], f"manifest hash {member}")
            declared[member] = item
        if set(declared) != set(EVIDENCE_MEMBERS) - {"MANIFEST.json", "SHA256SUMS.txt"}:
            raise DeliveryError("evidence manifest coverage mismatch")
        for member, item in declared.items():
            payload = archive.read(member)
            if len(payload) != item["bytes"] or _sha256(payload) != item["sha256"]:
                raise DeliveryError(f"evidence manifest mismatch: {member}")
        sums: dict[str, str] = {}
        try:
            sum_lines = archive.read("SHA256SUMS.txt").decode("ascii").splitlines()
        except UnicodeDecodeError as exc:
            raise DeliveryError("evidence checksum ledger is not ASCII") from exc
        for line in sum_lines:
            parts = line.split("  ", 1)
            if len(parts) != 2:
                raise DeliveryError("evidence checksum ledger is malformed")
            digest, member = parts
            _require_sha256(digest, f"checksum {member}")
            if member in sums:
                raise DeliveryError("evidence checksum ledger contains duplicates")
            sums[member] = digest
        if set(sums) != set(EVIDENCE_MEMBERS) - {"SHA256SUMS.txt"}:
            raise DeliveryError("evidence checksum coverage mismatch")
        for member, digest in sums.items():
            if _sha256(archive.read(member)) != digest:
                raise DeliveryError(f"evidence checksum mismatch: {member}")
        receipt = _bounded_json(archive.read("DELIVERY-RECEIPT.json"), "DELIVERY-RECEIPT.json")
        _validate_receipt(receipt, path, sidecar_path)
    return {"status": "PASS", "sha256": _sha256(data), "member_count": len(names)}


def verify_evidence(path: Path, *, sidecar_path: Path, expected_sha256: str) -> dict[str, Any]:
    try:
        return _verify_evidence(path, sidecar_path=sidecar_path, expected_sha256=expected_sha256)
    except DeliveryError:
        raise
    except (OSError, KeyError, ValueError, OverflowError, zipfile.BadZipFile) as exc:
        raise DeliveryError(f"evidence archive verification failed: {type(exc).__name__}") from exc


def main() -> int:
    parser = argparse.ArgumentParser(description="Atlas Consistent PR Delivery Standard R01 operator")
    sub = parser.add_subparsers(dest="command", required=True)
    compile_parser = sub.add_parser("compile")
    compile_parser.add_argument("--input-root", required=True, type=Path)
    compile_parser.add_argument("--source-root", required=True, type=Path)
    compile_parser.add_argument("--output-dir", required=True, type=Path)
    compile_parser.add_argument("--evidence-zip", required=True, type=Path)
    verify_parser = sub.add_parser("verify-evidence")
    verify_parser.add_argument("--evidence-zip", required=True, type=Path)
    verify_parser.add_argument("--sidecar", required=True, type=Path)
    verify_parser.add_argument("--expected-sha256", required=True)
    args = parser.parse_args()
    try:
        if args.command == "verify-evidence":
            print(json.dumps(verify_evidence(args.evidence_zip, sidecar_path=args.sidecar, expected_sha256=args.expected_sha256), indent=2, sort_keys=True))
            return 0
        result = compile_with_evidence(
            input_root=args.input_root,
            source_root=args.source_root,
            output_dir=args.output_dir,
            evidence_zip=args.evidence_zip,
            platforms=REQUIRED_PLATFORMS,
        )
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    except DeliveryError as exc:
        print(f"Delivery rejected: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
