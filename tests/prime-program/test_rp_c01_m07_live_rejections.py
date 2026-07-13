from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class RpC01M07LiveRejectionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.proof = json.loads((ROOT / "proof/repairing-prime/rp-c01-m07-live-rejection-reconciliation-r01.json").read_text(encoding="utf-8"))
        self.route = json.loads((ROOT / "proof/repairing-prime/rp-c01-route-evidence-r01.json").read_text(encoding="utf-8"))
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

    def test_non_owner_is_the_only_remaining_m07_and_aj03_boundary(self) -> None:
        self.assertEqual(self.proof["remaining_boundary"]["missing"], ["NON_OWNER"])
        self.assertEqual(self.acceptance["journeys"]["AJ-03"]["missing"], ["NON_OWNER"])
        self.assertEqual(self.route["m07_live_rejection_sequence"]["missing"], ["NON_OWNER"])
        campaign = next(item for item in self.identities["campaigns"] if item["campaign_id"] == "RP-C01")
        missions = {item["mission_id"]: item["state"] for item in campaign["missions"]}
        self.assertEqual(missions["RP-C01-M07"], "PARTIAL")
        self.assertEqual(self.proof["acceptance_journey_state"], "UNPROVEN")
        self.assertTrue(all(value is False for value in self.proof["forbidden_promotions"].values()))

    def test_superseded_diagnostics_are_conserved_without_promotion(self) -> None:
        self.assertEqual({item["run"] for item in self.proof["superseded_no_mutation_diagnostics"]}, {29233989153, 29234050494})
        self.assertTrue(all(item["mutation"] is False for item in self.proof["superseded_no_mutation_diagnostics"]))

    def test_continuity_advances_once_and_prior_boundaries_remain(self) -> None:
        repairing = next(item for item in self.continuity["entries"] if item["quest_id"] == "QUEST-REPAIRING-PRIME-R01")
        self.assertEqual(self.continuity["register_revision"], 15)
        self.assertEqual(repairing["revision"], 14)
        self.assertEqual(repairing["last_event_id"], "RP-C01-M05-PARITY-ACCEPTANCE-R01")
        self.assertEqual(repairing["quest_state"], "IN_PROGRESS")
        self.assertTrue(any("genuine non-owner" in blocker for blocker in repairing["blockers"]))
        self.assertFalse(any("RP-C01-M05" in blocker for blocker in repairing["blockers"]))


if __name__ == "__main__":
    unittest.main()
