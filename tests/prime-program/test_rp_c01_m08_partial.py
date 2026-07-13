from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class RpC01M08PartialTests(unittest.TestCase):
    def setUp(self) -> None:
        self.proof = json.loads((ROOT / "proof/repairing-prime/rp-c01-m08-partial-reconciliation-r01.json").read_text(encoding="utf-8"))
        self.route = json.loads((ROOT / "proof/repairing-prime/rp-c01-route-evidence-r01.json").read_text(encoding="utf-8"))
        self.identities = json.loads((ROOT / "continuity/quest-engine-identities-r01.json").read_text(encoding="utf-8"))
        self.continuity = json.loads((ROOT / "continuity/prime-continuity-register-r01.json").read_text(encoding="utf-8"))

    def test_only_the_exact_jayson_carrier_dependency_subclaim_is_proven(self) -> None:
        self.assertEqual(self.proof["mission_state"], "PARTIAL")
        self.assertEqual(self.proof["accepted_subclaim"]["identity"], "JAYSON_CARRIER_CREATION_ATTACHMENT_PLACEMENT_NOT_REQUIRED")
        self.assertEqual(
            self.proof["accepted_subclaim"]["retired_routine_dependencies"],
            ["JAYSON_CARRIER_CREATION", "JAYSON_CARRIER_ATTACHMENT", "JAYSON_CARRIER_PLACEMENT"],
        )
        self.assertTrue(self.proof["live_evidence"]["carrier_created_outside_repository"])
        self.assertEqual(self.proof["live_evidence"]["detached_review"], "GREEN")

    def test_free_form_intake_acceptance_remains_exactly_missing(self) -> None:
        self.assertEqual(
            self.proof["remaining_boundary"]["missing"],
            ["ROUTINE_FREE_FORM_INTAKE_TO_CANONICAL_CARRIER_LIVE_ACCEPTANCE"],
        )
        self.assertEqual(self.route["guided_dependency_retirement"]["state"], "PARTIAL")
        self.assertIn("FREE_FORM_INTAKE_ACCEPTANCE_MISSING", self.route["mission_states"]["RP-C01-M08"])

    def test_identity_and_campaign_boundaries_remain_truthful(self) -> None:
        campaign = next(item for item in self.identities["campaigns"] if item["campaign_id"] == "RP-C01")
        missions = {item["mission_id"]: item["state"] for item in campaign["missions"]}
        self.assertEqual(missions["RP-C01-M08"], "PARTIAL")
        self.assertEqual(missions["RP-C01-M02"], "UNPROVEN")
        self.assertEqual(missions["RP-C01-M05"], "PROVEN")
        self.assertEqual(missions["RP-C01-M06"], "PARTIAL")
        self.assertEqual(missions["RP-C01-M07"], "PARTIAL")
        self.assertEqual(campaign["state"], "IN_PROGRESS")
        self.assertEqual(self.proof["campaign_gate_state"], "NOT_PROVEN")
        self.assertTrue(all(value is False for value in self.proof["forbidden_promotions"].values()))

    def test_continuity_advances_once_without_self_promotion(self) -> None:
        repairing = next(item for item in self.continuity["entries"] if item["quest_id"] == "QUEST-REPAIRING-PRIME-R01")
        self.assertGreaterEqual(self.continuity["register_revision"], 13)
        self.assertGreaterEqual(repairing["revision"], 12)
        self.assertIn("RP-C01-M08-PARTIAL-RECONCILIATION-R01", self.continuity["event_ids"])
        self.assertEqual(repairing["quest_state"], "IN_PROGRESS")
        self.assertTrue(any("free-form" in blocker for blocker in repairing["blockers"]))


if __name__ == "__main__":
    unittest.main()
