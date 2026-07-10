#!/usr/bin/env python3
"""Verify a hash-bound Prime Context Pack without granting action authority."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path, PurePosixPath
from typing import Any


SHA256_RE = re.compile(r"[0-9a-f]{64}")


class PackError(ValueError):
    """A malformed pack that must fail closed."""


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise PackError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _relative_path(value: object) -> PurePosixPath:
    if not isinstance(value, str) or not value or "\\" in value:
        raise PackError("source path must be a nonempty POSIX relative path")
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise PackError("source path is not normalized and repository-relative")
    return path


def _load_pack(pack_path: Path) -> dict[str, Any]:
    try:
        data = json.loads(pack_path.read_bytes().decode("utf-8"), object_pairs_hook=_unique_object)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PackError(f"pack cannot be read as strict UTF-8 JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise PackError("pack root must be an object")
    if data.get("format_version") != "1.0":
        raise PackError("format_version must be 1.0")
    if not isinstance(data.get("subject"), str) or not data["subject"].strip():
        raise PackError("subject must be nonempty")
    if not isinstance(data.get("sources"), list) or not data["sources"]:
        raise PackError("sources must be a nonempty list")
    return data


def verify_pack(pack_path: Path, repo_root: Path) -> dict[str, Any]:
    data = _load_pack(pack_path)
    root = repo_root.resolve(strict=True)
    seen: set[str] = set()
    results: list[dict[str, Any]] = []

    for item in data["sources"]:
        if not isinstance(item, dict):
            raise PackError("each source must be an object")
        relative = _relative_path(item.get("path"))
        expected = item.get("sha256")
        if not isinstance(expected, str) or SHA256_RE.fullmatch(expected) is None:
            raise PackError(f"invalid SHA-256 for {relative.as_posix()}")
        folded = relative.as_posix().casefold()
        if folded in seen:
            raise PackError(f"duplicate source path: {relative.as_posix()}")
        seen.add(folded)

        target = root.joinpath(*relative.parts)
        status = "CURRENT"
        observed: str | None = None
        try:
            if target.is_symlink() or not target.is_file():
                status = "SOURCE_MISSING_OR_NONREGULAR"
            else:
                resolved = target.resolve(strict=True)
                resolved.relative_to(root)
                observed = hashlib.sha256(target.read_bytes()).hexdigest()
                if observed != expected:
                    status = "SOURCE_HASH_MISMATCH"
        except (OSError, ValueError):
            status = "SOURCE_OUTSIDE_REPOSITORY"

        results.append(
            {
                "path": relative.as_posix(),
                "expected_sha256": expected,
                "observed_sha256": observed,
                "status": status,
            }
        )

    current = all(item["status"] == "CURRENT" for item in results)
    return {
        "format_version": "1.0",
        "subject": data["subject"],
        "status": "CURRENT" if current else "INVALIDATED",
        "sources": results,
        "action_authorized": False,
        "canonical_readback_required": True,
        "authority": "READ_ONLY_NAVIGATION",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pack", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = verify_pack(args.pack, args.repo_root)
    except PackError as exc:
        result = {
            "format_version": "1.0",
            "status": "INVALIDATED",
            "error_code": "PACK_INVALID",
            "detail": str(exc),
            "action_authorized": False,
            "canonical_readback_required": True,
            "authority": "READ_ONLY_NAVIGATION",
        }
        print(json.dumps(result, indent=2, sort_keys=True))
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "CURRENT" else 1


if __name__ == "__main__":
    raise SystemExit(main())
