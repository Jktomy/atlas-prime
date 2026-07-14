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
        self.records = {record["id"]: record for record in self.register["capabilities"]}

    def test_register_is_exactly_the_frozen_28_capability_set(self) -> None:
        records = self.register["capabilities"]
        self.assertEqual(len(records), 28)
        self.assertEqual([record["id"] for record in records], [f"CAP-{n:03d}" for n in range(1, 29)])
        self.assertEqual(len({record["capability"] for record in records}), 28)
        self.assertEqual(self.register["predecessor_head"], "c892dc05ea56db0134a0e865f56d491f9c02ff85")

    def test_path_and_capability_dispositions_are_separate(self) -> None:
        authority = self.register["path_disposition_authority"]
        self.assertEqual((authority["tracked_paths"], authority["closed_paths"], authority["open_paths"]), (525, 525, 0))
        self.assertIn("never establishes capability parity", authority["authority_boundary"])
        self.assertTrue(all("path_disposition" in record and "capability_disposition" in record for record in self.register["capabilities"]))

    def test_disposition_vocabulary_and_counts_are_exact(self) -> None:
        self.assertEqual(tuple(self.register["capability_disposition_vocabulary"]), DISPOSITIONS)
        observed = Counter(record["capability_disposition"] for record in self.register["capabilities"])
        expected_nonzero = {key: value for key, value in self.register["capability_disposition_counts"].items() if value}
        self.assertEqual(dict(observed), expected_nonzero)
        self.assertEqual(
            self.register["capability_disposition_counts"],
            {
                "PRESERVED": 4,
                "IMPROVED": 7,
                "RESTORED": 14,
                "REPLACED": 1,
                "INTENTIONALLY_RETIRED": 1,
                "BLOCKED": 0,
                "STILL_MISSING": 1,
            },
        )
        self.assertEqual(sum(self.register["capability_disposition_counts"].values()), 28)
        enum = self.schema["properties"]["capabilities"]["items"]["properties"]["capability_disposition"]["enum"]
        self.assertEqual(set(enum), set(DISPOSITIONS))

    def test_only_cap027_remains_missing(self) -> None:
        missing = [record["id"] for record in self.register["capabilities"] if record["capability_disposition"] == "STILL_MISSING"]
        self.assertEqual(missing, ["CAP-027"])
        self.assertEqual(self.records["CAP-027"]["activation_state"], "MISSING")
        self.assertIn("AJ-03, AJ-11, and AJ-12", self.records["CAP-027"]["current_state"])

    def test_cap015_is_restored_from_direct_spear_evidence(self) -> None:
        cap = self.records["CAP-015"]
        proof = json.loads(
            (ROOT / "proof/repairing-prime/rp-c08-cap015-architecture-realignment-r02.json").read_text(encoding="utf-8")
        )
        self.assertEqual(cap["capability_disposition"], "RESTORED")
        self.assertEqual(cap["activation_state"], "ACTIVE")
        self.assertEqual(cap["audit_status"], "RESTORED_DIRECT_SPEAR_LIVE_PROVEN")
        self.assertIn("through Spear", cap["capability"])
        self.assertIn("PR #102", cap["current_state"])
        self.assertFalse(proof["superseded_premise"]["external_bridge_required"])
        self.assertEqual(proof["transitions"]["CAP-015"]["to"], "RESTORED/ACTIVE")

    def test_hosted_and_generated_capabilities_remain_restored(self) -> None:
        for capability_id in ("CAP-009", "CAP-010", "CAP-011", "CAP-019", "CAP-020", "CAP-022", "CAP-023"):
            self.assertEqual(self.records[capability_id]["capability_disposition"], "RESTORED")
            self.assertEqual(self.records[capability_id]["activation_state"], "ACTIVE")
        self.assertIn("Jayson/Artemis Arrow/Bow", self.records["CAP-009"]["current_state"])

    def test_legacy_oathbringer_capability_is_replaced(self) -> None:
        cap = self.records["CAP-017"]
        acceptance = (ROOT / "governance/capability-acceptance-contract.md").read_text(encoding="utf-8")
        self.assertEqual(cap["capability_disposition"], "REPLACED")
        self.assertEqual(cap["activation_state"], "ACTIVE")
        self.assertIn("AJ-04", cap["required_proof"])
        self.assertIn("AJ-05", cap["required_proof"])
        self.assertIn("AJ-06", cap["required_proof"])
        self.assertIn("AJ-04, AJ-05, and AJ-06 are `PROVEN`", acceptance)

    def test_route_terms_are_not_conflated(self) -> None:
        change_routes = (ROOT / "governance/change-routes.md").read_text(encoding="utf-8")
        command_surfaces = (ROOT / "routing/command-surfaces.md").read_text(encoding="utf-8")
        phoenix = (ROOT / "methods/phoenix-blade.md").read_text(encoding="utf-8")
        spear = (ROOT / "methods/athenas-spear.md").read_text(encoding="utf-8")
        bow = (ROOT / "methods/artemis-bow-and-arrow.md").read_text(encoding="utf-8")

        self.assertIn("Athena -> Spear -> Thread Engine", change_routes)
        self.assertIn("Jayson / Artemis -> Arrow -> Bow -> Thread Engine", change_routes)
        self.assertIn("Phoenix Blade is Athena executing a Sword", phoenix)
        self.assertIn("does not invoke Thread Engine", phoenix)
        self.assertIn("Aegis Break is Athena's bounded route-selection", phoenix)
        self.assertIn("Spear is Athena's direct Thread Engine route", spear)
        self.assertIn("Bow and Arrow belong to Jayson and Artemis", bow)
        self.assertIn("direct GitHub-native construction is an Aegis Break route", command_surfaces)
        self.assertNotIn("Phoenix Blade -> Athena direct repository construction", change_routes)
        self.assertNotIn("Bow and Arrow belong to Athena", bow)

    def test_light_and_work_surface_identity_remain_separate(self) -> None:
        phoenix = (ROOT / "methods/phoenix-blade.md").read_text(encoding="utf-8")
        self.assertIn("Shardplate is the AI-assisted work surface", phoenix)
        self.assertIn("Unreported model use is `UNAVAILABLE`", phoenix)
        self.assertIn("deterministic non-model work has no Light and zero BEU", phoenix)


if __name__ == "__main__":
    unittest.main()
