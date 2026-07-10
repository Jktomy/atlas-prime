from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
STANDARD_PATH = ROOT / "methods/sword-forge-standard.md"
LESSONS_PATH = ROOT / "methods/sword-lessons.json"
SWORD_PATH = ROOT / "methods/atlas-sword.md"
FRAMEWORK_PATH = ROOT / "tools/atlas-sword/README.md"
ROUTING_PATH = ROOT / "routing/command-surfaces.md"


class SwordForgeStandardTests(unittest.TestCase):
    def setUp(self) -> None:
        self.standard = STANDARD_PATH.read_text(encoding="utf-8")
        self.lessons = json.loads(LESSONS_PATH.read_text(encoding="utf-8"))
        self.sword = SWORD_PATH.read_text(encoding="utf-8")
        self.framework = FRAMEWORK_PATH.read_text(encoding="utf-8")
        self.routing = ROUTING_PATH.read_text(encoding="utf-8")

    def test_forge_standard_identity_and_power_are_canonical(self) -> None:
        self.assertIn("SWORD_FORGE_STANDARD_V1", self.standard)
        for operation in ("ADD", "REPLACE", "DELETE", "RENAME", "MOVE"):
            self.assertIn(operation, self.standard)
        self.assertIn("arbitrary authorized multi-file", self.standard)
        self.assertIn("not construction vetoes", self.standard)
        self.assertIn("branch and pull request", self.standard)
        self.assertIn("GitHub-native blob, tree, commit, ref, and pull-request", self.standard)
        self.assertIn("PowerShell is the thin interactive client", self.standard)

    def test_every_sword_request_routes_through_standard_and_lessons(self) -> None:
        for source in (self.routing, self.sword, self.framework):
            self.assertIn("methods/sword-forge-standard.md", source)
            self.assertIn("methods/sword-lessons.json", source)
        self.assertIn("automatically routes", self.routing)
        self.assertIn("does not need to invoke a separate preflight command", self.routing)
        self.assertIn("No separate user phrase", self.sword)

    def test_lessons_register_is_machine_readable_and_unique(self) -> None:
        self.assertEqual(self.lessons["schema_version"], "prime-sword-lessons-v1")
        self.assertEqual(self.lessons["forge_standard"], "SWORD_FORGE_STANDARD_V1")
        self.assertEqual(
            self.lessons["register_role"], "CANONICAL_VERIFIED_SWORD_LESSONS"
        )
        lessons = self.lessons["lessons"]
        lesson_ids = [lesson["lesson_id"] for lesson in lessons]
        self.assertEqual(len(lessons), 13)
        self.assertEqual(len(lesson_ids), len(set(lesson_ids)))
        self.assertEqual(lesson_ids, [f"SWORD-L{number:03d}" for number in range(1, 14)])

    def test_only_verified_or_absorbed_lessons_control_forging(self) -> None:
        maturity = set(self.lessons["maturity_vocabulary"])
        controlling = set(self.lessons["controlling_maturities"])
        self.assertEqual(
            maturity,
            {"OBSERVED", "CORROBORATED", "VERIFIED", "ABSORBED", "SUPERSEDED"},
        )
        self.assertEqual(controlling, {"VERIFIED", "ABSORBED"})
        for lesson in self.lessons["lessons"]:
            self.assertIn(lesson["maturity"], controlling)
            for field in (
                "lesson_id",
                "title",
                "trigger",
                "failure",
                "required_control",
            ):
                self.assertTrue(lesson[field].strip())
            self.assertTrue(lesson["applies_to"])
            self.assertTrue(lesson["evidence"])

    def test_applicability_is_explicit_and_unknown_blocks(self) -> None:
        self.assertIn("APPLIED", self.standard)
        self.assertIn("NOT_APPLICABLE", self.standard)
        self.assertIn("UNKNOWN", self.standard)
        self.assertIn("blocks the forge", self.standard)
        self.assertIn("UNKNOWN or missing classification blocks forging", self.lessons["application_rule"])

    def test_strikeforce_findings_cannot_self_promote(self) -> None:
        self.assertIn("never self-promote", self.lessons["promotion_rule"])
        self.assertIn("do not silently rewrite", self.standard)
        self.assertIn("separate bounded source transaction", self.sword)

    def test_wave_two_adds_adapter_without_claiming_live_restoration(self) -> None:
        self.assertIn("PILOT_READY_PROOF_PENDING", self.sword)
        self.assertIn("production adapter is **present but not yet capability-proven**", self.sword)
        self.assertIn("Production mutation adapter:** present; harmless live proof pending", self.framework)
        self.assertIn("Wave 3 must prove AJ-04, AJ-05, and AJ-06", self.framework)
        for path in (
            "tools/atlas-sword/engine/oathbringer_api.py",
            "tools/atlas-sword/engine/oathbringer_core.py",
            "tools/atlas-sword/engine/oathbringer_github.py",
            "tools/atlas-sword/engine/oathbringer_runtime.py",
            "tools/atlas-sword/engine/oathbringer_support.py",
            "tools/atlas-sword/engine/oathbringer_tree.py",
            "tools/atlas-sword/schema/oathbringer-production-mission-v2.schema.json",
        ):
            self.assertTrue((ROOT / path).is_file(), path)


if __name__ == "__main__":
    unittest.main()
