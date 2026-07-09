from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .path_policy import validate_safe_filename


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def stable_json(data: dict[str, Any]) -> str:
    return json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(stable_json(data), encoding="utf-8", newline="\n")


def write_evidence_json(evidence_root: Path, filename: str, data: dict[str, Any]) -> Path:
    safe = validate_safe_filename(filename, reserved={"state-journal.jsonl", "pr-body.md"})
    target = (evidence_root / safe).resolve(strict=False)
    root = evidence_root.resolve(strict=False)
    try:
        target.relative_to(root)
    except ValueError as exc:
        raise ValueError("evidence write escaped evidence root") from exc
    write_json(target, data)
    return target


def tree_hash(root: Path) -> str:
    entries: list[tuple[str, int, str]] = []
    root = root.resolve()
    for path in sorted(root.rglob("*"), key=lambda item: item.relative_to(root).as_posix()):
        if path.is_dir():
            continue
        if not path.is_file() or path.is_symlink():
            raise ValueError(f"non-regular candidate entry: {path.relative_to(root).as_posix()}")
        rel = path.relative_to(root).as_posix()
        entries.append((rel, path.stat().st_size, sha256_file(path)))
    digest = hashlib.sha256()
    for rel, size, data_hash in entries:
        digest.update(rel.encode("utf-8"))
        digest.update(b"\0file\0")
        digest.update(str(size).encode("ascii"))
        digest.update(b"\0")
        digest.update(data_hash.encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def declared_state_hash(root: Path, paths: tuple[str, ...]) -> str:
    digest = hashlib.sha256()
    for rel in sorted(paths):
        target = root.joinpath(*rel.split("/"))
        digest.update(rel.encode("utf-8"))
        if target.exists():
            if not target.is_file() or target.is_symlink():
                raise ValueError(f"non-regular declared entry: {rel}")
            digest.update(b"\0present\0")
            digest.update(sha256_file(target).encode("ascii"))
            digest.update(b"\n")
        else:
            digest.update(b"\0absent\0\n")
    return digest.hexdigest()


def forbidden_confirmation() -> dict[str, object]:
    return {
        "direct_main_write": False,
        "force_push": False,
        "auto_merge": False,
        "ready_transition": False,
        "workflow_dispatch": False,
        "repository_setting_mutation": False,
        "generated_output_mutation": False,
        "workboard_mutation": False,
        "production_authority_activated": False,
        "standing_authority": "NO",
    }
