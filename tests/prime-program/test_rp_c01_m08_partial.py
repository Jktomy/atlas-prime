from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

class RpC01M08PartialTests(unittest.TestCase):
    def setUp(self) -> None:
        self.proof = json.loads((ROOT / "proof/repairing-prime/rp-c01-m08-partial-reconciliation-r01.json").read_text(encoding="utf-8"))
        self.acceptance = json.loads((ROOT / "proof/repairing-prime/rp-c01-m08-free-form-acceptance-r01.json").read_text(encoding="utf-8"))
        self.route = json.loads((ROOT / "proof/repairing-prime/rp-c01-route-evidence-r01.json").read_text(encoding="utf-8"))
        self.cap015 = json.loads((ROOT / "proof/repairing-prime/rp-c08-cap015-architecture-realignment-r02.json").read_text(encoding="utf-8"))
        self.identities = json.loads((ROOT / "continuity/quest-engine-identities-r01.json").read_text(encoding="utf-8"))
        self.continuity = json.loads((ROOT / "continuity/prime-continuity-register-r01.json").read_text(encoding="utf-8"))
        self.board = json.loads((ROOT / "quest-board/quest-board-v1.json").read_text(encoding="utf-8"))

    def test_historical_partial_record_remains_exact(self) -> None:
        self.assertEqual(self.proof["mission_state"], "PARTIAL")
        self.assertEqual(self.proof["accepted_subclaim"]["identity"], "JAYSON_CARRIER_CREATION_ATTACHMENT_PLACEMENT_NOT_REQUIRED")
        self.assertEqual(self.proof["accepted_subclaim"]["retired_routine_dependencies"], ["JAYSON_CARRIER_CREATION", "JAYSON_CARRIER_ATTACHMENT", "JAYSON_CARRIER_PLACEMENT"])
        self.assertEqual(self.proof["remaining_boundary"]["missing"], ["ROUTINE_FREE_FORM_INTAKE_TO_CANONICAL_CARRIER_LIVE_ACCEPTANCE"])

    def test_later_acceptance_closes_only_the_m08_missing_boundary(self) -> None:
        self.assertEqual(self.acceptance["mission_state"], "PROVEN")
        self.assertEqual(self.acceptance["campaign_gate_state"], "NOT_PROVEN")
        self.assertIn("ROUTINE_FREE_FORM_INTAKE_TO_CANONICAL_CARRIER_LIVE_ACCEPTANCE", self.acceptance["accepted_subclaims"])
        self.assertEqual(self.route["guided_dependency_retirement"]["state"], "PROVEN")
        self.assertEqual(self.route["guided_dependency_retirement"]["missing"], [])
        self.assertIn("PROVEN_ROUTINE_FREE_FORM_INTAKE", self.route["mission_states"]["RP-C01-M08"])

    def test_current_identity_preserves_all_rp_c01_missions(self) -> None:
        campaign = next(item for item in self.identities["campaigns"] if item["campaign_id"] == "RP-C01")
        missions = {item["mission_id"]: item["state"] for item in campaign["missions"]}
        self.assertEqual(missions["RP-C01-M08"], "PROVEN")
        self.assertEqual(missions["RP-C01-M02"], "PROVEN")
        self.assertEqual(self.cap015["transitions"]["RP-C01-M02"]["to"], "PROVEN")
        self.assertEqual(missions["RP-C01-M05"], "PROVEN")
        self.assertEqual(missions["RP-C01-M06"], "PROVEN")
        self.assertEqual(missions["RP-C01-M07"], "PROVEN")
        self.assertEqual(campaign["state"], "COMPLETE")
        self.assertTrue(all(value is False for value in self.acceptance["forbidden_promotions"].values()))
        self.assertTrue(all(value is False for value in self.cap015["forbidden_promotions"].values()))

    def test_continuity_history_survives_final_quest_closeout(self) -> None:
        events = self.continuity["event_ids"]
        creation_event = "PA-C01-QUEST-CREATION-R01"
        sunset_event = "PA-C01-HOSTED-ACTIONS-SUNSET-R01"
        self.assertGreaterEqual(self.continuity["register_revision"], 33)
        self.assertIn("RP-C01-M08-FREE-FORM-ACCEPTANCE-R01", events)
        self.assertIn("RP-C08-CAP015-ARCHITECTURE-REALIGNMENT-R02", events)
        self.assertEqual(events.count(creation_event), 1)
        self.assertEqual(events.count(sunset_event), 1)
        self.assertLess(events.index(creation_event), events.index(sunset_event))
        self.assertNotIn("QUEST-REPAIRING-PRIME-R01", {item["quest_id"] for item in self.continuity["entries"]})
        repairing = next(item for item in self.board["entries"] if item["quest_id"] == "QUEST-REPAIRING-PRIME-R01")
        self.assertEqual(repairing["state"], "COMPLETE")
        self.assertEqual(repairing["next_gate"], "CLOSED")

if __name__ == "__main__":
    unittest.main()
