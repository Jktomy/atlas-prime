from __future__ import annotations

import json
import re
import shutil
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_SENSITIVE = re.compile(
    r"(?:authorization|password|secret|token|private[_-]?key|api[_-]?key)",
    re.IGNORECASE,
)


def _safe(value: Any, fallback: str) -> str:
    text = re.sub(r"[^A-Za-z0-9._-]+", "-", str(value or "")).strip("-.")
    return text or fallback


def _sanitize(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            str(key): "<redacted>" if _SENSITIVE.search(str(key)) else _sanitize(item)
            for key, item in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [_sanitize(item) for item in value]
    return value


def resolve_path(
    mission: dict[str, Any] | None,
    receipt_path: Path,
    explicit: str | Path | None = None,
) -> Path:
    if explicit:
        return Path(explicit).expanduser().resolve()
    mission = mission or {}
    mission_id = _safe(mission.get("mission_id"), "mission")
    match = re.search(r"(?i)(r[0-9]+)$", str(mission.get("sword_identity") or ""))
    revision = match.group(1).lower() if match else "r00"
    return receipt_path.resolve().parent / f"Atlas-Deflected-Sword-{mission_id}-{revision}.zip"


def _copy(source: Path, destination: Path) -> None:
    try:
        if source.is_file():
            shutil.copy2(source, destination)
    except OSError:
        pass


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
    """Create one sanitized failure archive without reading environment secrets."""

    destination = resolve_path(mission, receipt_path, output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    root = Path(tempfile.mkdtemp(prefix="Atlas-Deflected-Sword-"))
    try:
        _copy(receipt_path, root / "receipt.json")
        _copy(receipt_path.with_name(f"{receipt_path.name}.sha256"), root / "receipt.json.sha256")
        _copy(mission_path, root / "mission.json")
        if transcript_path is not None:
            _copy(transcript_path, root / "terminal-output.txt")
        for name in ("MANIFEST.json", "FORGE-RECEIPT.json", "README-FIRST.txt", "README-FIRST.md"):
            _copy(package_root / name, root / name)
        audit = (mission or {}).get("independent_audit")
        if isinstance(audit, dict) and audit.get("receipt_path"):
            _copy(package_root / str(audit["receipt_path"]), root / "independent-audit.json")

        ledger = receipt.get("stage_ledger") or {}
        flags = receipt.get("completion_flags") or {}
        detail = " ".join(str(receipt.get("detail") or "Unavailable").split())[:2000]
        summary = [
            "ATLAS DEFLECTED SWORD",
            f"Mission: {(mission or {}).get('mission_id') or receipt.get('mission_id') or 'UNKNOWN'}",
            f"Sword: {(mission or {}).get('sword_identity') or receipt.get('sword_identity') or 'UNKNOWN'}",
            f"Lane: {(mission or {}).get('lane') or receipt.get('lane') or 'UNKNOWN'}",
            f"Repository: {(mission or {}).get('repository') or receipt.get('repository') or 'UNKNOWN'}",
            f"Status: {receipt.get('status') or 'UNKNOWN'}",
            f"Failed stage: {ledger.get('current_stage') or 'UNKNOWN'}",
            f"Last completed stage: {ledger.get('last_completed_stage') or 'UNKNOWN'}",
            f"Mutation performed: {'YES' if flags.get('mutation_performed') else 'NO'}",
            f"Detail: {detail}",
            "Automatic retry: NO",
            "Automatic rollback: NO",
            f"Generated UTC: {datetime.now(timezone.utc).isoformat()}",
        ]
        (root / "failure-summary.txt").write_text("\n".join(summary) + "\n", encoding="utf-8")
        result = receipt.get("result") or {}
        remote = _sanitize(receipt.get("remote_state") or {})
        workflow = _sanitize(result.get("workflow_gate") or {}) if isinstance(result, dict) else {}
        (root / "sanitized-remote-state.json").write_text(
            json.dumps(remote, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        (root / "workflow-state.json").write_text(
            json.dumps(workflow, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )

        destination.unlink(missing_ok=True)
        with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED) as archive:
            for member in sorted(root.iterdir(), key=lambda item: item.name):
                if member.is_file():
                    archive.write(member, member.name)
    finally:
        shutil.rmtree(root, ignore_errors=True)
    return destination
