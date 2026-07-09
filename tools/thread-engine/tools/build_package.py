from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from pathlib import Path

EXCLUDED_NAMES = {"__pycache__", ".pytest_cache"}
EXCLUDED_SUFFIXES = {".pyc", ".pyo", ".zip"}
FIXED_ZIP_DATE = (2026, 7, 3, 0, 0, 0)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def should_include(path: Path) -> bool:
    if any(part in EXCLUDED_NAMES for part in path.parts):
        return False
    if path.suffix in EXCLUDED_SUFFIXES:
        return False
    return path.is_file()


def package_entries(root: Path) -> list[tuple[str, bytes]]:
    entries: list[tuple[str, bytes]] = []
    for path in sorted(root.rglob("*"), key=lambda item: item.relative_to(root).as_posix()):
        if should_include(path):
            rel = path.relative_to(root).as_posix()
            entries.append((rel, path.read_bytes()))
    return entries


def build_package(root: Path, output: Path) -> str:
    root = root.resolve()
    output = output.resolve()
    entries = [(rel, data) for rel, data in package_entries(root) if rel != "PACKAGE-MANIFEST.json"]
    manifest = {
        "package_identity": "atlas-thread-engine-gate7b-fixture",
        "implementation_state": "PILOT_DISABLED",
        "runtime_mode": "FIXTURE_ONLY",
        "persistent_writer": "ABSENT",
        "production_adapters": "ABSENT",
        "github_mutation": "DISABLED",
        "network_access": "DISABLED",
        "repository_checkout_mutation": "DISABLED",
        "workflow_authority": "ABSENT",
        "standing_authority": "NO",
        "files": [
            {
                "path": rel,
                "size": len(data),
                "sha256": sha256_bytes(data),
            }
            for rel, data in entries
        ],
    }
    manifest_bytes = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode("utf-8")
    all_entries = [("PACKAGE-MANIFEST.json", manifest_bytes)] + entries
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as package:
        for rel, data in all_entries:
            info = zipfile.ZipInfo(rel, FIXED_ZIP_DATE)
            info.create_system = 3
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            package.writestr(info, data)
    return hashlib.sha256(output.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description="Build deterministic Gate 7B Thread Engine package")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    digest = build_package(Path(args.root), Path(args.output))
    print(digest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
