from __future__ import annotations

import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "tools/context-packs/verify_context_pack.py"
SPEC = importlib.util.spec_from_file_location("prime_context_pack", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ContextPackTests(unittest.TestCase):
    def _fixture(self, root: Path) -> tuple[Path, Path]:
        source = root / "source.md"
        source.write_text("Prime source\n", encoding="utf-8", newline="\n")
        pack = root / "pack.json"
        pack.write_text(
            json.dumps(
                {
                    "format_version": "1.0",
                    "subject": "prime.unit.context",
                    "sources": [
                        {
                            "path": "source.md",
                            "sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                        }
                    ],
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
            newline="\n",
        )
        return source, pack

    def test_exact_hash_is_current_and_read_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_text:
            root = Path(tmp_text)
            _, pack = self._fixture(root)
            result = MODULE.verify_pack(pack, root)
            self.assertEqual(result["status"], "CURRENT")
            self.assertFalse(result["action_authorized"])
            self.assertTrue(result["canonical_readback_required"])

    def test_hash_mismatch_invalidates_the_entire_pack(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_text:
            root = Path(tmp_text)
            source, pack = self._fixture(root)
            source.write_text("Changed source\n", encoding="utf-8", newline="\n")
            result = MODULE.verify_pack(pack, root)
            self.assertEqual(result["status"], "INVALIDATED")
            self.assertEqual(result["sources"][0]["status"], "SOURCE_HASH_MISMATCH")
            self.assertFalse(result["action_authorized"])

    def test_unsafe_or_duplicate_path_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_text:
            root = Path(tmp_text)
            _, pack = self._fixture(root)
            data = json.loads(pack.read_text(encoding="utf-8"))
            data["sources"][0]["path"] = "../outside.md"
            pack.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaises(MODULE.PackError):
                MODULE.verify_pack(pack, root)


if __name__ == "__main__":
    unittest.main()
