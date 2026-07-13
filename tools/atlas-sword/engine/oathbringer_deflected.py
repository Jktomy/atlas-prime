from __future__ import annotations

import ctypes
import hashlib
import io
import json
import os
import re
import stat
import tempfile
import zipfile
from pathlib import Path
from typing import Any


ZIP_EPOCH = (1980, 1, 1, 0, 0, 0)
MAX_MEMBER_BYTES = 1_048_576
MAX_TOTAL_BYTES = 4_194_304
MAX_MEMBERS = 32

_SENSITIVE_KEY = re.compile(
    r"(?:authorization|password|secret|token|private[_-]?key|api[_-]?key|"
    r"access[_-]?key|credential|recovery[_-]?code|cookie)",
    re.IGNORECASE,
)
_PEM_BLOCK = re.compile(
    r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----.*?"
    r"-----END (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
    re.DOTALL,
)
_SECRET_VALUE = re.compile(
    r"(?:\b(?:Bearer|Basic)\s+[A-Za-z0-9._~+/=-]{8,}|"
    r"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}(?:\.[A-Za-z0-9_-]{8,})?\b|"
    r"\bgh[pousr]_[A-Za-z0-9]{20,}\b|\bgithub_pat_[A-Za-z0-9_]{20,}\b|"
    r"\bsk-[A-Za-z0-9_-]{20,}\b|\bAKIA[0-9A-Z]{16}\b|"
    r"[\"']?(?:authorization|api[_-]?key|access[_-]?token|password|secret|"
    r"private[_-]?key|recovery[_-]?code|cookie)[\"']?\s*[:=]\s*"
    r"[\"']?[^\s,}\r\n\"']{4,}[\"']?)",
    re.IGNORECASE,
)
_WINDOWS_HOME = re.compile(r"(?i)\b[A-Z]:\\[^\r\n\"']+")
_POSIX_HOME = re.compile(r"/(?:home|Users)/[^\r\n\"']+")
_EMAIL = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
_IPV4 = re.compile(r"(?<![0-9])(?:[0-9]{1,3}\.){3}[0-9]{1,3}(?![0-9])")
_SAFE_BOOLEAN_POLICY_KEYS = {"credential_persistence", "token_persisted"}


class DeflectedSwordError(RuntimeError):
    """A failure evidence bundle could not be safely created or verified."""


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def sanitize_text(value: str) -> str:
    """Redact protected value shapes and private runtime locations from text."""

    text = value.replace("\r\n", "\n").replace("\r", "\n")
    text = _PEM_BLOCK.sub("<redacted>", text)
    text = _SECRET_VALUE.sub("<redacted>", text)
    text = _WINDOWS_HOME.sub("<redacted-home>", text)
    text = _POSIX_HOME.sub("<redacted-home>", text)
    text = _EMAIL.sub("<redacted-email>", text)
    return _IPV4.sub("<redacted-ip>", text)


def sanitize_evidence(value: Any) -> Any:
    """Return a recursively sanitized copy suitable for durable clean evidence."""

    if isinstance(value, dict):
        result: dict[str, Any] = {}
        for key, item in value.items():
            name = str(key)
            sanitized_name = sanitize_text(name)
            output_name = name if sanitized_name == name else "<redacted-key>"
            suffix = 2
            while output_name in result:
                output_name = f"<redacted-key-{suffix}>"
                suffix += 1
            if sanitized_name != name:
                result[output_name] = None if item is None else "<redacted>"
            elif _SENSITIVE_KEY.search(name) is not None:
                if name.casefold() in _SAFE_BOOLEAN_POLICY_KEYS and isinstance(item, bool):
                    result[output_name] = item
                elif item is None:
                    result[output_name] = None
                else:
                    result[output_name] = "<redacted>"
            else:
                result[output_name] = sanitize_evidence(item)
        return result
    if isinstance(value, (list, tuple)):
        return [sanitize_evidence(item) for item in value]
    if isinstance(value, str):
        return sanitize_text(value)
    return value


def _assert_clean(data: bytes, field: str) -> None:
    if len(data) > MAX_MEMBER_BYTES:
        raise DeflectedSwordError(f"evidence member exceeds limit: {field}")
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise DeflectedSwordError(f"evidence member is not UTF-8 text: {field}") from exc
    scanned = text
    for placeholder in ("<redacted>", "<redacted-home>", "<redacted-email>", "<redacted-ip>"):
        scanned = scanned.replace(placeholder, "")
    if _PEM_BLOCK.search(scanned) or _SECRET_VALUE.search(scanned) or sanitize_text(scanned) != scanned:
        raise DeflectedSwordError(f"evidence member still contains protected material: {field}")


def _safe(value: Any, fallback: str) -> str:
    text = re.sub(r"[^A-Za-z0-9._-]+", "-", str(value or "")).strip("-.")
    return text or fallback


def resolve_path(
    mission: dict[str, Any] | None,
    receipt_path: Path,
    explicit: str | Path | None = None,
) -> Path:
    if explicit:
        return Path(os.path.abspath(os.path.expanduser(str(explicit))))
    mission = mission or {}
    mission_id = _safe(mission.get("mission_id"), "mission")
    match = re.search(r"(?i)(r[0-9]+)$", str(mission.get("sword_identity") or ""))
    revision = match.group(1).lower() if match else "r00"
    return receipt_path.resolve().parent / f"Atlas-Deflected-Sword-{mission_id}-{revision}.zip"


def _read_text(path: Path) -> str | None:
    try:
        if not path.is_file() or path.stat().st_size > MAX_MEMBER_BYTES:
            return None
        return sanitize_text(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError):
        return None


def _read_json(path: Path) -> Any | None:
    try:
        if not path.is_file() or path.stat().st_size > MAX_MEMBER_BYTES:
            return None
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None
    return sanitize_evidence(value)


def _package_member(package_root: Path, relative: str) -> Path | None:
    candidate = (package_root / relative).resolve()
    root = package_root.resolve()
    if candidate != root and root not in candidate.parents:
        return None
    return candidate


def _zip_bytes(members: dict[str, bytes]) -> bytes:
    total = sum(len(data) for data in members.values())
    if not members or len(members) + 2 > MAX_MEMBERS or total > MAX_TOTAL_BYTES:
        raise DeflectedSwordError("evidence member count or total size exceeds limit")
    folded = [name.casefold() for name in members]
    if len(folded) != len(set(folded)):
        raise DeflectedSwordError("evidence member names collide under case folding")
    for name, data in members.items():
        if not name or name.startswith(("/", "\\")) or "\\" in name or ".." in name.split("/"):
            raise DeflectedSwordError(f"unsafe evidence member path: {name}")
        _assert_clean(data, name)

    manifest = {
        "format_version": "atlas.deflected-sword.v2",
        "files": [
            {"path": name, "bytes": len(members[name]), "sha256": _sha256(members[name])}
            for name in sorted(members)
        ],
    }
    sealed = dict(members)
    sealed["MANIFEST.json"] = _canonical_json(manifest)
    sealed["SHA256SUMS.txt"] = "".join(
        f"{_sha256(sealed[name])}  {name}\n" for name in sorted(sealed)
    ).encode("ascii")

    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_STORED, strict_timestamps=True) as archive:
        for name in sorted(sealed):
            info = zipfile.ZipInfo(name, ZIP_EPOCH)
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            info.compress_type = zipfile.ZIP_STORED
            archive.writestr(info, sealed[name])
    return output.getvalue()


def _publish_no_clobber(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() or path.is_symlink():
        raise DeflectedSwordError(f"immutable evidence destination already exists: {path.name}")
    handle, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(handle, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        if os.name == "nt":
            move_file = ctypes.windll.kernel32.MoveFileExW
            move_file.argtypes = [ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_uint]
            move_file.restype = ctypes.c_int
            if not move_file(str(temporary), str(path), 0x00000008):
                raise OSError(ctypes.get_last_error(), "MoveFileExW failed")
        else:
            os.link(temporary, path, follow_symlinks=False)
            temporary.unlink()
    except FileExistsError as exc:
        raise DeflectedSwordError(f"immutable evidence destination already exists: {path.name}") from exc
    except OSError as exc:
        raise DeflectedSwordError(f"immutable evidence publish failed: {path.name}") from exc
    finally:
        try:
            temporary.unlink(missing_ok=True)
        except OSError:
            pass


def _verify(path: Path, *, require_sidecar: bool = True) -> dict[str, Any]:
    """Verify exact membership, checksums, bounds, and optional sidecar."""

    candidate = path.expanduser()
    if candidate.is_symlink():
        raise DeflectedSwordError("Deflected Sword archive must not be a symlink")
    source = candidate.resolve()
    if not source.is_file() or source.stat().st_size > MAX_TOTAL_BYTES + MAX_MEMBER_BYTES:
        raise DeflectedSwordError("Deflected Sword archive is missing or unsafe")
    with zipfile.ZipFile(source, "r") as archive:
        infos = archive.infolist()
        names = [info.filename for info in infos]
        if (
            not infos
            or len(infos) > MAX_MEMBERS
            or len(names) != len(set(names))
            or len({name.casefold() for name in names}) != len(names)
        ):
            raise DeflectedSwordError("Deflected Sword membership is invalid")
        if any(
            info.is_dir()
            or info.flag_bits & 0x1
            or info.compress_type != zipfile.ZIP_STORED
            or info.compress_size != info.file_size
            or info.file_size > MAX_MEMBER_BYTES
            or not stat.S_ISREG(info.external_attr >> 16)
            or not info.filename
            or info.filename.startswith(("/", "\\"))
            or "\\" in info.filename
            or ".." in info.filename.split("/")
            for info in infos
        ):
            raise DeflectedSwordError("Deflected Sword member policy is invalid")
        if sum(info.file_size for info in infos) > MAX_TOTAL_BYTES:
            raise DeflectedSwordError("Deflected Sword content exceeds limit")
        if not {"MANIFEST.json", "SHA256SUMS.txt"} <= set(names):
            raise DeflectedSwordError("Deflected Sword controls are missing")
        for name in names:
            _assert_clean(name.encode("utf-8"), f"member name {name}")
            _assert_clean(archive.read(name), name)
        manifest = json.loads(archive.read("MANIFEST.json").decode("utf-8"))
        if not isinstance(manifest, dict) or set(manifest) != {"format_version", "files"}:
            raise DeflectedSwordError("Deflected Sword manifest is invalid")
        entries = manifest.get("files")
        if manifest.get("format_version") != "atlas.deflected-sword.v2" or not isinstance(entries, list):
            raise DeflectedSwordError("Deflected Sword manifest is invalid")
        declared = {item.get("path"): item for item in entries if isinstance(item, dict)}
        if (
            set(declared) != set(names) - {"MANIFEST.json", "SHA256SUMS.txt"}
            or len(declared) != len(entries)
            or any(set(item) != {"path", "bytes", "sha256"} for item in entries if isinstance(item, dict))
        ):
            raise DeflectedSwordError("Deflected Sword manifest coverage is invalid")
        for name, item in declared.items():
            data = archive.read(name)
            _assert_clean(data, name)
            if item != {"path": name, "bytes": len(data), "sha256": _sha256(data)}:
                raise DeflectedSwordError(f"Deflected Sword manifest mismatch: {name}")
        sums: dict[str, str] = {}
        for line in archive.read("SHA256SUMS.txt").decode("ascii").splitlines():
            digest, separator, name = line.partition("  ")
            if separator != "  " or name in sums or re.fullmatch(r"[0-9a-f]{64}", digest) is None:
                raise DeflectedSwordError("Deflected Sword checksum ledger is invalid")
            sums[name] = digest
        expected_sum_names = set(names) - {"SHA256SUMS.txt"}
        if set(sums) != expected_sum_names or any(_sha256(archive.read(name)) != digest for name, digest in sums.items()):
            raise DeflectedSwordError("Deflected Sword checksum coverage is invalid")

    digest = _sha256(source.read_bytes())
    sidecar = source.with_suffix(source.suffix + ".sha256")
    expected_sidecar = f"{digest}  {source.name}\n"
    if require_sidecar and not sidecar.is_file():
        raise DeflectedSwordError("Deflected Sword sidecar is missing")
    if sidecar.exists() and (
        sidecar.is_symlink()
        or sidecar.stat().st_size != len(expected_sidecar.encode("ascii"))
        or sidecar.read_text(encoding="ascii") != expected_sidecar
    ):
        raise DeflectedSwordError("Deflected Sword sidecar mismatch")
    return {"archive_path": str(source), "archive_sha256": digest, "sidecar_path": str(sidecar), "member_count": len(infos)}


def verify(path: Path, *, require_sidecar: bool = True) -> dict[str, Any]:
    """Fail closed with one typed diagnostic for malformed or unsafe evidence."""

    try:
        return _verify(path, require_sidecar=require_sidecar)
    except DeflectedSwordError:
        raise
    except Exception as exc:
        raise DeflectedSwordError("Deflected Sword archive could not be safely verified") from exc


def create(
    *,
    package_root: Path,
    mission_path: Path,
    receipt_path: Path,
    mission: dict[str, Any] | None,
    receipt: dict[str, Any],
    transcript_path: Path | None = None,
    output_path: str | Path | None = None,
) -> Path:
    """Create one bounded, sanitized, immutable failure evidence archive."""

    destination = resolve_path(mission, receipt_path, output_path)
    safe_mission = sanitize_evidence(mission or _read_json(mission_path) or {})
    safe_receipt = sanitize_evidence(receipt)
    ledger = safe_receipt.get("stage_ledger") or {}
    flags = safe_receipt.get("completion_flags") or {}
    detail = " ".join(str(safe_receipt.get("detail") or "Unavailable").split())[:2000]
    summary = [
        "ATLAS DEFLECTED SWORD",
        f"Mission: {safe_mission.get('mission_id') or safe_receipt.get('mission_id') or 'UNKNOWN'}",
        f"Sword: {safe_mission.get('sword_identity') or safe_receipt.get('sword_identity') or 'UNKNOWN'}",
        f"Lane: {safe_mission.get('lane') or safe_receipt.get('lane') or 'UNKNOWN'}",
        f"Repository: {safe_mission.get('repository') or safe_receipt.get('repository') or 'UNKNOWN'}",
        f"Status: {safe_receipt.get('status') or 'UNKNOWN'}",
        f"Failed stage: {ledger.get('current_stage') or 'UNKNOWN'}",
        f"Last completed stage: {ledger.get('last_completed_stage') or 'UNKNOWN'}",
        f"Mutation performed: {'YES' if flags.get('mutation_performed') else 'NO'}",
        f"Detail: {detail}",
        "Automatic retry: NO",
        "Automatic rollback: NO",
    ]
    members: dict[str, bytes] = {
        "failure-summary.txt": ("\n".join(summary) + "\n").encode("utf-8"),
        "mission.json": _canonical_json(safe_mission),
        "receipt.json": _canonical_json(safe_receipt),
        "receipt.json.sha256": f"{_sha256(_canonical_json(safe_receipt))}  receipt.json\n".encode("ascii"),
        "sanitized-remote-state.json": _canonical_json(safe_receipt.get("remote_state") or {}),
        "workflow-state.json": _canonical_json((safe_receipt.get("result") or {}).get("workflow_gate") or {}),
    }
    if transcript_path is not None:
        transcript = _read_text(transcript_path)
        if transcript is not None:
            members["terminal-output.txt"] = transcript.encode("utf-8")
    for name in ("FORGE-RECEIPT.json",):
        value = _read_json(package_root / name)
        if value is not None:
            members[name] = _canonical_json(value)
    for name in ("README-FIRST.txt", "README-FIRST.md"):
        value = _read_text(package_root / name)
        if value is not None:
            members[name] = value.encode("utf-8")
    manifest = _read_json(package_root / "MANIFEST.json")
    if manifest is not None:
        members["PACKAGE-MANIFEST.json"] = _canonical_json(manifest)
    audit = safe_mission.get("independent_audit") if isinstance(safe_mission, dict) else None
    if isinstance(audit, dict) and isinstance(audit.get("receipt_path"), str):
        audit_path = _package_member(package_root, audit["receipt_path"])
        value = None if audit_path is None else _read_json(audit_path)
        if value is not None:
            members["independent-audit.json"] = _canonical_json(value)

    archive_bytes = _zip_bytes(members)
    digest = _sha256(archive_bytes)
    sidecar = destination.with_suffix(destination.suffix + ".sha256")
    sidecar_bytes = f"{digest}  {destination.name}\n".encode("ascii")
    if destination.is_symlink() or sidecar.is_symlink():
        raise DeflectedSwordError("immutable evidence outputs must not be symlinks")

    if destination.exists():
        if (
            not destination.is_file()
            or destination.stat().st_size != len(archive_bytes)
            or destination.read_bytes() != archive_bytes
        ):
            raise DeflectedSwordError(f"immutable evidence destination already exists: {destination.name}")
        if sidecar.exists():
            if (
                not sidecar.is_file()
                or sidecar.stat().st_size != len(sidecar_bytes)
                or sidecar.read_bytes() != sidecar_bytes
            ):
                raise DeflectedSwordError("immutable evidence sidecar conflicts with the existing archive")
        else:
            _publish_no_clobber(sidecar, sidecar_bytes)
    elif sidecar.exists():
        if (
            not sidecar.is_file()
            or sidecar.stat().st_size != len(sidecar_bytes)
            or sidecar.read_bytes() != sidecar_bytes
        ):
            raise DeflectedSwordError("orphan immutable evidence sidecar conflicts with the intended archive")
        _publish_no_clobber(destination, archive_bytes)
    else:
        _publish_no_clobber(destination, archive_bytes)
        _publish_no_clobber(sidecar, f"{digest}  {destination.name}\n".encode("ascii"))
    verification = verify(destination)
    if verification["archive_sha256"] != digest:
        raise DeflectedSwordError("Deflected Sword final readback mismatch")
    return destination
