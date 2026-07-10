from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKIP_PARTS = {".git", "__pycache__", ".pytest_cache"}
TEXT_SUFFIXES = {".md", ".json", ".py", ".ps1", ".yml", ".yaml", ".txt"}
APPROVED_GENERATED = {
    "atlas-duplicate-scope-report.md",
    "atlas-file-inventory.md",
    "atlas-metadata-inventory.md",
    "atlas-orphan-report.md",
    "atlas-routing-inventory.md",
}
PATTERNS = {
    "private_key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "github_token": re.compile(r"\bgh(?:p|o|u|s|r)_[A-Za-z0-9]{20,}\b"),
    "aws_access_key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "assigned_secret": re.compile(r"(?i)\b(?:api[_-]?key|access[_-]?token|password)\s*[:=]\s*['\"][^'\"\r\n]{8,}['\"]"),
}


class PrivacyBoundaryTests(unittest.TestCase):
    def test_no_high_confidence_secret_material(self) -> None:
        findings: list[str] = []
        for path in ROOT.rglob("*"):
            if not path.is_file() or path.suffix.casefold() not in TEXT_SUFFIXES or any(part in SKIP_PARTS for part in path.parts):
                continue
            text = path.read_text(encoding="utf-8")
            for label, pattern in PATTERNS.items():
                if pattern.search(text):
                    findings.append(f"{path.relative_to(ROOT).as_posix()}: {label}")
        self.assertEqual(findings, [])

    def test_generated_boundary_and_no_runtime_byproducts(self) -> None:
        generated_root = ROOT / "generated"
        if generated_root.exists():
            generated_files = {
                path.relative_to(generated_root).as_posix()
                for path in generated_root.rglob("*")
                if path.is_file()
            }
            self.assertEqual(generated_files, APPROVED_GENERATED)
            self.assertEqual([path for path in generated_root.rglob("*") if path.is_symlink()], [])
        byproducts = [
            path.relative_to(ROOT).as_posix()
            for path in ROOT.rglob("*")
            if path.is_file() and (path.suffix in {".pyc", ".pyo"} or "__pycache__" in path.parts)
        ]
        self.assertEqual(byproducts, [])


if __name__ == "__main__":
    unittest.main()
