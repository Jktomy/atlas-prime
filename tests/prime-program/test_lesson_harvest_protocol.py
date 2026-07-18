from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class LessonHarvestProtocolTests(unittest.TestCase):
    def test_singular_roles_and_semantic_routes_are_explicit(self) -> None:
        protocol = (ROOT / "governance/lesson-harvest-protocol.md").read_text(encoding="utf-8")
        for marker in (
            "full Atlas Sunset", "continuity snapshot", "Feather** is exact-context evidence",
            "Golden Wing** is the sole reusable-lesson candidate", "Lessons never self-promote",
            "python -B -m tools.atlas_lifecycle sunset candidate",
            "python -B -m tools.prime_continuity.cli sunset --continuity-id ID",
            "Passing checks cannot cure a misleading",
        ):
            self.assertIn(marker, protocol)
        self.assertNotIn("continuity snapshot is the full Atlas Sunset", protocol)

    def test_dependent_sources_reconcile_the_same_claims(self) -> None:
        sources = {
            path: " ".join((ROOT / path).read_text(encoding="utf-8").split())
            for path in (
                "governance/atlas-aegis.md", "governance/atlas-strikeforce.md",
                "operations/protocol-library.md", "routing/command-surfaces.md",
                "knowledge/atlas-source-compendium.md", "lifecycle/lifecycle-contract.md",
                "lifecycle/README.md", "templates/preview-bundle-template.md",
                "tools/prime_continuity/README.md",
            )
        }
        self.assertIn("semantic objective", sources["governance/atlas-aegis.md"])
        self.assertIn("assurance-controls.json", sources["governance/atlas-strikeforce.md"])
        self.assertIn("Full Atlas Sunset", sources["operations/protocol-library.md"])
        self.assertIn("Full Atlas Sunset or continuity snapshot", sources["routing/command-surfaces.md"])
        self.assertIn("Golden Wing candidate", sources["knowledge/atlas-source-compendium.md"])
        self.assertIn("not a continuity snapshot", sources["lifecycle/lifecycle-contract.md"])
        self.assertIn("full Atlas Sunset", sources["lifecycle/README.md"])
        self.assertIn("Assurance-control applicability", sources["templates/preview-bundle-template.md"])
        self.assertIn("not a full Atlas Sunset", sources["tools/prime_continuity/README.md"])

    def test_historical_lifecycle_v1_contract_remains_present(self) -> None:
        expected = (
            "common-v1.schema.json", "feather-v1.schema.json", "feather-archive-v1.schema.json",
            "golden-wing-v1.schema.json", "quest-emberline-v1.schema.json",
            "quest-checkpoint-v1.schema.json", "sunset-v1.schema.json", "sunrise-v1.schema.json",
            "continuity-v1.schema.json", "lifecycle-receipt-v1.schema.json",
        )
        self.assertEqual([name for name in expected if not (ROOT / "lifecycle/schemas" / name).is_file()], [])


if __name__ == "__main__":
    unittest.main()
