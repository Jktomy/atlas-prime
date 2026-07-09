from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT.parent / f"{ROOT.name}.zip"
FIXED_TIME = (2026, 7, 3, 0, 0, 0)

excluded_names = {"MANIFEST.json", "SHA256SUMS.txt"}
excluded_parts = {"__pycache__", ".pytest_cache"}

files: list[Path] = []
for path in sorted(ROOT.rglob("*")):
    if not path.is_file():
        continue
    rel = path.relative_to(ROOT)
    if rel.as_posix() in excluded_names:
        continue
    if any(part in excluded_parts for part in rel.parts):
        continue
    if path.suffix in {".pyc", ".pyo"}:
        continue
    files.append(path)

manifest = {
    "format": "atlas-sword-framework-manifest-v2",
    "framework_state": "PILOT_DISABLED",
    "files": [],
}
sum_lines: list[str] = []

for path in files:
    rel = path.relative_to(ROOT).as_posix()
    data = path.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    manifest["files"].append(
        {"path": rel, "size": len(data), "sha256": digest}
    )
    sum_lines.append(f"{digest}  {rel}")

manifest_bytes = (
    json.dumps(manifest, indent=2) + "\\n"
).encode("utf-8")
sums_bytes = ("\\n".join(sum_lines) + "\\n").encode("utf-8")

(ROOT / "MANIFEST.json").write_bytes(manifest_bytes)
(ROOT / "SHA256SUMS.txt").write_bytes(sums_bytes)

members = [(path.relative_to(ROOT).as_posix(), path.read_bytes()) for path in files]
members.extend(
    [
        ("MANIFEST.json", manifest_bytes),
        ("SHA256SUMS.txt", sums_bytes),
    ]
)

with zipfile.ZipFile(
    OUTPUT,
    "w",
    compression=zipfile.ZIP_DEFLATED,
    compresslevel=9,
) as archive:
    for name, data in sorted(members):
        info = zipfile.ZipInfo(name, date_time=FIXED_TIME)
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = 0o100644 << 16
        info.create_system = 3
        archive.writestr(info, data)

print(OUTPUT)
print(hashlib.sha256(OUTPUT.read_bytes()).hexdigest())
