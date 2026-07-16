from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class RpC01M07LiveRejectionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.proof = json.loads((ROOT / "proof/repairing-prime/rp-c01-m07-live-rejection-reconciliation-r01.json").read_text(encoding="utf-8"))
        self.route = json.loads((ROOT / "proof/repairing-prime/rp-c01-route-evidence-r01.json").read_text(encoding="utf-8"))
        self.non_owner = json.loads((ROOT / "proof/repairing-prime/rp-c01-m07-non-owner-acceptance-r01.json").read_text(encoding="utf-8"))
        self.acceptance = json.loads((ROOT / "proof/repairing-prime/rp-c07-acceptance-reconciliation-r01.json").read_text(encoding="utf-8"))
        self.identities = json.loads((ROOT / "continuity/quest-engine-identities-r01.json").read_text(encoding="utf-8"))
        self.continuity = json.loads((ROOT / "continuity/prime-continuity-register-r01.json").read_text(encoding="utf-8"))

    def test_fixture_is_closed_unmerged_and_canonical_main_did_not_move(self) -> None:
        fixture = self.proof["fixture_setup"]
        self.assertEqual(fixture["pull_request"], 156)
        self.assertEqual(fixture["final_pr_state"], "CLOSED_UNMERGED")
        self.assertTrue(fixture["branch_deleted"])
        self.assertTrue(fixture["canonical_main_unchanged"])
        self.assertEqual(fixture["canonical_base"], self.proof["transaction_base_sha"])

    def test_exact_four_live_cases_reject_before_mutation(self) -> None:
        self.assertEqual(
            self.proof["accepted_matrix_delta"],
            {"EDITED_INPUT": "PROVEN_NO_MUTATION", "REPLAY": "PROVEN_NO_MUTATION", "DUPLICATE_BRANCH": "PROVEN_NO_MUTATION", "DUPLICATE_PR": "PROVEN_NO_MUTATION"},
        )
        self.assertEqual(
            {record["error_code"] for record in self.proof["accepted_live_rejections"].values()},
            {"CARRIER_SHA_REJECTED", "REPLAY_BRANCH_EXISTS", "REPLAY_PULL_REQUEST_EXISTS"},
        )
        for record in self.proof["accepted_live_rejections"].values():
            self.assertEqual(record["result"], "REJECTED")
            self.assertEqual(record["stage"], "PRE_MUTATION_REJECTION")
            self.assertEqual(record["invoke_state"], "SKIPPED")
            self.assertFalse(record["mutation"])

    def test_historical_partial_and_later_non_owner_acceptance_are_both_exact(self) -> None:
        self.assertEqual(self.proof["remaining_boundary"]["missing"], ["NON_OWNER"])
        self.assertEqual(self.acceptance["journeys"]["AJ-03"]["missing"], ["NON_OWNER"])
        self.assertEqual(self.proof["acceptance_journey_state"], "UNPROVEN")
        self.assertTrue(all(value is False for value in self.proof["forbidden_promotions"].values()))
        self.assertEqual(self.non_owner["acceptance_journey_state"], "PROVEN")
        self.assertEqual(self.non_owner["mission_state"], "PROVEN")
        self.assertEqual(self.route["m07_live_rejection_sequence"]["missing"], [])
        self.assertIn("NON_OWNER", self.route["m07_live_rejection_sequence"]["accepted"])
        campaign = next(item for item in self.identities["campaigns"] if item["campaign_id"] == "RP-C01")
        missions = {item["mission_id"]: item["state"] for item in campaign["missions"]}
        self.assertEqual(missions["RP-C01-M07"], "PROVEN")
        self.assertEqual(campaign["state"], "COMPLETE")

    def test_superseded_diagnostics_are_conserved_without_promotion(self) -> None:
        self.assertEqual({item["run"] for item in self.proof["superseded_no_mutation_diagnostics"]}, {29233989153, 29234050494})
        self.assertTrue(all(item["mutation"] is False for item in self.proof["superseded_no_mutation_diagnostics"]))

    def test_continuity_preserves_history_and_advances_through_cap027(self) -> None:
        repairing = next(item for item in self.continuity["entries"] if item["quest_id"] == "QUEST-REPAIRING-PRIME-R01")
        events = self.continuity["event_ids"]
        historical_event = "RP-C01-M07-LIVE-REJECTION-RECONCILIATION-R01"
        m07_event = "RP-C01-M07-AJ03-NON-OWNER-ACCEPTANCE-R05"
        aj11_event = "RP-C08-AJ11-CLEAN-CLONE-ACCEPTANCE-RECONCILIATION-R08"
        aj12_event = "RP-C08-AJ12-MERGED-MAIN-VALIDATION-ACCEPTANCE-R01"
        cap027_event = "RP-C08-CAP027-FINAL-CAPABILITY-RECONCILIATION-R01"
        for event in (historical_event, m07_event, aj11_event, aj12_event, cap027_event):
            self.assertEqual(events.count(event), 1)
        self.assertLess(events.index(historical_event), events.index(m07_event))
        self.assertLess(events.index(m07_event), events.index(aj11_event))
        self.assertLess(events.index(aj11_event), events.index(aj12_event))
        self.assertLess(events.index(aj12_event), events.index(cap027_event))
        self.assertEqual(self.continuity["register_revision"], 29)
        self.assertEqual(repairing["revision"], 24)
        self.assertEqual(repairing["last_event_id"], cap027_event)
        self.assertEqual(repairing["quest_state"], "IN_PROGRESS")
        self.assertFalse(any("genuine non-owner" in blocker for blocker in repairing["blockers"]))
        self.assertFalse(any("AJ-11 requires" in blocker for blocker in repairing["blockers"]))
        self.assertFalse(any("AJ-12 requires complete" in blocker for blocker in repairing["blockers"]))
        self.assertFalse(any("CAP-027 remains missing" in blocker for blocker in repairing["blockers"]))
        self.assertIn("whole-Quest Strikeforce", repairing["next_action"])


if __name__ == "__main__":
    unittest.main()
