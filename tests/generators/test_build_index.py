from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("prime_build_index", ROOT / "tools/build_index.py")
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot load Prime generator")
GENERATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(GENERATOR)


class PrimeGeneratorTests(unittest.TestCase):
    def test_repeated_build_is_byte_identical(self) -> None:
        with tempfile.TemporaryDirectory(prefix="prime-generator-") as raw:
            root = Path(raw) / "repo"
            root.mkdir()
            (root / "README.md").write_text("# Prime\n", encoding="utf-8", newline="\n")
            (root / "source.md").write_text(
                "---\ntitle: Source\nstatus: ACTIVE\nsource_type: SUPPORT\ncanonical_scope: Test\nprotected_level: LOW\n---\n\n# Source\n",
                encoding="utf-8",
                newline="\n",
            )
            first, first_fingerprint = GENERATOR.build_outputs(root)
            second, second_fingerprint = GENERATOR.build_outputs(root)
            self.assertEqual(first_fingerprint, second_fingerprint)
            self.assertEqual(first, second)
            self.assertEqual(set(first), set(GENERATOR.APPROVED_OUTPUTS))

    def test_generated_directory_does_not_change_source_identity(self) -> None:
        with tempfile.TemporaryDirectory(prefix="prime-generator-") as raw:
            root = Path(raw)
            (root / "README.md").write_text("# Prime\n", encoding="utf-8", newline="\n")
            _outputs, before = GENERATOR.build_outputs(root)
            (root / "generated").mkdir()
            (root / "generated/report.md").write_text("ignored\n", encoding="utf-8", newline="\n")
            _outputs, after = GENERATOR.build_outputs(root)
            self.assertEqual(before, after)

    def test_invalid_utf8_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory(prefix="prime-generator-") as raw:
            root = Path(raw)
            (root / "bad.md").write_bytes(b"\xff\xfe")
            with self.assertRaises(UnicodeDecodeError):
                GENERATOR.build_outputs(root)


if __name__ == "__main__":
    unittest.main()
