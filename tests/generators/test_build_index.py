from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "prime_build_index",
    ROOT / "tools/build_index.py",
)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot load Prime generator")
GENERATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(GENERATOR)


class PrimeGeneratorTests(unittest.TestCase):
    def test_repeated_build_is_byte_identical(self) -> None:
        with tempfile.TemporaryDirectory(prefix="prime-generator-") as raw:
            root = Path(raw) / "repo"
            root.mkdir()
            (root / "README.md").write_text(
                "# Prime\n",
                encoding="utf-8",
                newline="\n",
            )
            (root / "source.md").write_text(
                "---\n"
                "title: Source\n"
                "status: ACTIVE\n"
                "source_type: SUPPORT\n"
                "canonical_scope: Test\n"
                "protected_level: LOW\n"
                "---\n\n"
                "# Source\n",
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
            (root / "README.md").write_text(
                "# Prime\n",
                encoding="utf-8",
                newline="\n",
            )
            _outputs, before = GENERATOR.build_outputs(root)
            (root / "generated").mkdir()
            (root / "generated/report.md").write_text(
                "ignored\n",
                encoding="utf-8",
                newline="\n",
            )
            _outputs, after = GENERATOR.build_outputs(root)
            self.assertEqual(before, after)

    def test_invalid_utf8_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory(prefix="prime-generator-") as raw:
            root = Path(raw)
            (root / "bad.md").write_bytes(b"\xff\xfe")
            with self.assertRaises(UnicodeDecodeError):
                GENERATOR.build_outputs(root)

    def test_recognized_readme_route_controls_routing_and_orphan_reports(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory(
            prefix="prime-generator-routing-"
        ) as raw:
            root = Path(raw)
            contract_relative = (
                "governance/athena-route-architecture-r01.md"
            )
            contract_path = root / contract_relative
            contract_path.parent.mkdir(parents=True)
            contract_path.write_text(
                "---\n"
                'title: "Athena Route Architecture R01"\n'
                'status: "CANONICAL_ACTIVE"\n'
                'source_type: "PROTOCOL"\n'
                'protected_level: "CRITICAL"\n'
                "---\n\n"
                "# Athena Route Architecture R01\n",
                encoding="utf-8",
                newline="\n",
            )
            readme_path = root / "README.md"
            readme_path.write_text(
                "# Prime\n",
                encoding="utf-8",
                newline="\n",
            )

            unrouted, _unrouted_fingerprint = GENERATOR.build_outputs(root)
            unrouted_row = f"| `{contract_relative}` | no |"
            orphan_row = (
                f"| `{contract_relative}` | "
                "active metadata-bearing file not found in routing surfaces |"
            )
            self.assertIn(
                unrouted_row,
                unrouted["atlas-routing-inventory.md"],
            )
            self.assertIn(
                orphan_row,
                unrouted["atlas-orphan-report.md"],
            )

            readme_path.write_text(
                "# Prime\n\n"
                "Current Athena route architecture is documented in "
                f"`{contract_relative}`.\n",
                encoding="utf-8",
                newline="\n",
            )
            routed, _routed_fingerprint = GENERATOR.build_outputs(root)
            self.assertIn(
                f"| `{contract_relative}` | yes |",
                routed["atlas-routing-inventory.md"],
            )
            self.assertNotIn(
                orphan_row,
                routed["atlas-orphan-report.md"],
            )


if __name__ == "__main__":
    unittest.main()
