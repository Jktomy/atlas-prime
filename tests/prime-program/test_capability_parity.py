from __future__ import annotations

import json
import unittest
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REGISTER_PATH = ROOT / "governance/capability-parity-register.json"
SCHEMA_PATH = ROOT / "schemas/capability-parity-register.schema.json"
DISPOSITIONS = (
    "PRESERVED",
    "IMPROVED",
    "RESTORED",
    "REPLACED",
    "INTENTIONALLY_RETIRED",
    "BLOCKED",
    "STILL_MISSING",
)


class CapabilityParityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.register = json.loads(REGISTER_PATH.read_text(encoding="utf-8"))
        self.schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

    def test_register_is_exactly_the_frozen_28_capability_set(self) -> None:
        records = self.register["capabilities"]
        self.assertEqual(len(records), 28)
        self.assertEqual(
            [record["id"] for record in records],
            [f"CAP-{number:03d}" for number in range(1, 29)],
        )
        self.assertEqual(len({record["capability"] for record in records}), 28)
        self.assertEqual(
            self.register["predecessor_head"],
            "c892dc05ea56db0134a0e865f56d491f9c02ff85",
        )

    def test_path_and_capability_dispositions_are_separate(self) -> None:
        authority = self.register["path_disposition_authority"]
        self.assertEqual(
            (authority["tracked_paths"], authority["closed_paths"], authority["open_paths"]),
            (525, 525, 0),
        )
        self.assertIn("never establishes capability parity", authority["authority_boundary"])
        self.assertTrue(
            all(
                "path_disposition" in record and "capability_disposition" in record
                for record in self.register["capabilities"]
            )
        )

    def test_disposition_vocabulary_and_counts_are_exact(self) -> None:
        self.assertEqual(tuple(self.register["capability_disposition_vocabulary"]), DISPOSITIONS)
        observed = Counter(
            record["capability_disposition"] for record in self.register["capabilities"]
        )
        expected_nonzero = {
            key: value
            for key, value in self.register["capability_disposition_counts"].items()
            if value
        }
        self.assertEqual(dict(observed), expected_nonzero)
        self.assertEqual(sum(self.register["capability_disposition_counts"].values()), 28)
        self.assertEqual(
            set(
                self.schema["properties"]["capabilities"]["items"]["properties"][
                    "capability_disposition"
                ]["enum"]
            ),
            set(DISPOSITIONS),
        )

    def test_control_plane_does_not_claim_unproven_activation(self) -> None:
        records = {record["id"]: record for record in self.register["capabilities"]}
        for capability_id in (
            "CAP-002",
            "CAP-003",
            "CAP-004",
            "CAP-005",
            "CAP-006",
            "CAP-008",
            "CAP-009",
            "CAP-010",
            "CAP-011",
            "CAP-015",
            "CAP-017",
            "CAP-019",
            "CAP-020",
            "CAP-022",
            "CAP-023",
            "CAP-027",
        ):
            self.assertEqual(records[capability_id]["capability_disposition"], "STILL_MISSING")
            self.assertEqual(records[capability_id]["activation_state"], "MISSING")

    def test_route_terms_are_not_conflated(self) -> None:
        change_routes = (ROOT / "governance/change-routes.md").read_text(encoding="utf-8")
        phoenix = (ROOT / "methods/phoenix-blade.md").read_text(encoding="utf-8")
        spear = (ROOT / "methods/athenas-spear.md").read_text(encoding="utf-8")
        sword = (ROOT / "methods/atlas-sword.md").read_text(encoding="utf-8")
        acceptance = (ROOT / "governance/capability-acceptance-contract.md").read_text(
            encoding="utf-8"
        )

        for term in (
            "Authorizer",
            "Operator",
            "Delivery route",
            "launcher",
            "Normal repository engine",
            "Repository substrate",
            "AI-assisted work surface",
            "AI/model processing source",
        ):
            self.assertIn(term, change_routes)

        self.assertIn("Shardplate is the AI-assisted work surface", phoenix)
        self.assertIn("fresh Work context", spear)
        self.assertIn(
            "Production BUILD, REPAIR, and EXECUTE mechanics are not yet present",
            sword,
        )

        self.assertIn("Aegis Break -> equivalent safe route", change_routes)
        self.assertNotIn("Aegis Break -> Phoenix Blade", change_routes)
        self.assertIn("not hardwired to Phoenix Blade", phoenix)

        self.assertIn("Stormlight identifies the source of AI/model processing", phoenix)
        self.assertNotIn("Stormlight describes the execution environment", phoenix)

        self.assertIn("PowerShell is the thin interactive client", sword)
        self.assertIn("GitHub-native", sword)
        self.assertIn("exact multi-file GitHub commit", acceptance)
        self.assertNotIn("clone-first BUILD", acceptance)


if __name__ == "__main__":
    unittest.main()
