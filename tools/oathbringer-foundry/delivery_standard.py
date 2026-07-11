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
SENSITIVE = re.compile(
    r"(?:\bgh[pousr]_[A-Za-z0-9]{20,}\b|\bgithub_pat_[A-Za-z0-9_]{20,}\b|"
    r"\bsk-[A-Za-z0-9_-]{20,}\b|\bAKIA[0-9A-Z]{16}\b|"
    r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|"
    r"(?i:(?:authorization|api[_-]?key|access[_-]?token|password|secret)\s*[:=]\s*[^\s]+))"
)


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
    return SENSITIVE.sub("[REDACTED]", normalized)


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
        value = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise DeliveryError(f"Foundry returned invalid JSON: {diagnostic or 'no diagnostic returned'}") from exc
    if not isinstance(value, dict):
        raise DeliveryError("Foundry result must be a JSON object")
    return value


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
        receipt["evidence_sha256"] = _write_evidence_archive(
            evidence_zip,
            receipt,
            captured.stdout,
            captured.stderr,
        )
    if failure is not None:
        raise failure
    return receipt


def verify_evidence(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    with zipfile.ZipFile(path, "r") as archive:
        infos = archive.infolist()
        names = [info.filename for info in infos]
        if len(names) != len(set(names)) or any(info.is_dir() or not stat.S_ISREG(info.external_attr >> 16) for info in infos):
            raise DeliveryError("evidence archive member set is unsafe")
        manifest = json.loads(archive.read("MANIFEST.json"))
        declared = {item["path"]: item for item in manifest["files"]}
        if set(declared) != set(names) - {"MANIFEST.json", "SHA256SUMS.txt"}:
            raise DeliveryError("evidence manifest coverage mismatch")
        for member, item in declared.items():
            payload = archive.read(member)
            if len(payload) != item["bytes"] or _sha256(payload) != item["sha256"]:
                raise DeliveryError(f"evidence manifest mismatch: {member}")
        sums = {}
        for line in archive.read("SHA256SUMS.txt").decode("ascii").splitlines():
            digest, member = line.split("  ", 1)
            sums[member] = digest
        if set(sums) != set(names) - {"SHA256SUMS.txt"}:
            raise DeliveryError("evidence checksum coverage mismatch")
        for member, digest in sums.items():
            if _sha256(archive.read(member)) != digest:
                raise DeliveryError(f"evidence checksum mismatch: {member}")
    return {"status": "PASS", "sha256": _sha256(data), "member_count": len(names)}


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
    args = parser.parse_args()
    try:
        if args.command == "verify-evidence":
            print(json.dumps(verify_evidence(args.evidence_zip), indent=2, sort_keys=True))
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
