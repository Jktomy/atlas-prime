from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from tools.athena_routes.schema import SchemaValidationError, validate_schema


ROOT = Path(__file__).resolve().parents[2]


class AssuranceControlTests(unittest.TestCase):
    def setUp(self) -> None:
        self.schema = json.loads((ROOT / "schemas/assurance-controls-v1.schema.json").read_text(encoding="utf-8"))
        self.register = json.loads((ROOT / "governance/assurance-controls.json").read_text(encoding="utf-8"))

    def test_register_is_closed_unique_and_controlling_only(self) -> None:
        validate_schema(self.schema, self.register)
        controls = self.register["controls"]
        self.assertEqual([item["control_id"] for item in controls], ["ASC-001", "ASC-002"])
        self.assertEqual(len({item["control_id"] for item in controls}), len(controls))
        self.assertLessEqual({item["status"] for item in controls}, {"ACTIVE", "SUPERSEDED"})
        self.assertTrue(all(item["status"] == "ACTIVE" for item in controls if item["control_id"] in {"ASC-001", "ASC-002"}))
        self.assertEqual(self.register["applicability_outcomes"], ["APPLIED", "NOT_APPLICABLE"])
        self.assertEqual(self.register["unknown_applicability"], "FAIL_CLOSED")
        for control in controls:
            self.assertTrue(control["applies_when"].strip())
            self.assertTrue(control["required_evidence"])
            self.assertTrue(control["enforcement_sources"])
            for source in control["enforcement_sources"]:
                self.assertTrue((ROOT / source).is_file(), source)

    def test_schema_rejects_unknown_fields_and_statuses(self) -> None:
        extra = copy.deepcopy(self.register); extra["controls"][0]["candidate_note"] = "not controlling"
        with self.assertRaises(SchemaValidationError):
            validate_schema(self.schema, extra)
        invalid = copy.deepcopy(self.register); invalid["controls"][0]["status"] = "CANDIDATE"
        with self.assertRaises(SchemaValidationError):
            validate_schema(self.schema, invalid)
        ambiguous = copy.deepcopy(self.register); ambiguous["controls"][0]["status"] = "SUPERSEDED"
        with self.assertRaises(SchemaValidationError):
            validate_schema(self.schema, ambiguous)
        active_with_successor = copy.deepcopy(self.register); active_with_successor["controls"][0]["superseded_by"] = "ASC-003"
        with self.assertRaises(SchemaValidationError):
            validate_schema(self.schema, active_with_successor)

    def test_seed_controls_have_real_semantic_enforcement(self) -> None:
        controls = {item["control_id"]: item for item in self.register["controls"]}
        self.assertIn("exactly one new sealed Feather", controls["ASC-001"]["objective"])
        self.assertIn("Golden Wing candidates gain no authority", controls["ASC-002"]["objective"])
        protocol = (ROOT / "governance/lesson-harvest-protocol.md").read_text(encoding="utf-8")
        aegis = (ROOT / "governance/atlas-aegis.md").read_text(encoding="utf-8")
        strikeforce = (ROOT / "governance/atlas-strikeforce.md").read_text(encoding="utf-8")
        for marker in ("APPLIED", "NOT_APPLICABLE", "unknown applicability", "fails closed"):
            self.assertIn(marker, protocol)
        self.assertIn("assurance-control applicability", aegis)
        self.assertIn("objective-to-route alignment", " ".join(strikeforce.split()))


if __name__ == "__main__":
    unittest.main()
