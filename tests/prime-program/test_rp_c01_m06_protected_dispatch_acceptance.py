from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class RpC01M06ProtectedDispatchAcceptanceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.acceptance = json.loads(
            (ROOT / "proof/repairing-prime/rp-c01-m06-protected-dispatch-acceptance-r01.json").read_text(
                encoding="utf-8"
            )
        )
        self.route = json.loads(
            (ROOT / "proof/repairing-prime/rp-c01-route-evidence-r01.json").read_text(encoding="utf-8")
        )
        self.identities = json.loads(
            (ROOT / "continuity/quest-engine-identities-r01.json").read_text(encoding="utf-8")
        )
        self.continuity = json.loads(
            (ROOT / "continuity/prime-continuity-register-r01.json").read_text(encoding="utf-8")
        )

    def test_live_receipt_binds_exact_protected_route_and_operator(self) -> None:
        live = self.acceptance["live_mission"]
        receipt = self.acceptance["adapter_receipt"]
        bindings = self.acceptance["immutable_bindings"]
        self.assertEqual(live["route_identity"], "AEGIS_BREAK_PROTECTED_PATH_V1")
        self.assertEqual(live["expected_operator_login"], "Jktomy")
        self.assertEqual(live["observed_operator_login"], "Jktomy")
        self.assertEqual(live["stop_point"], "DRAFT_PR_READBACK")
        self.assertEqual(
            bindings["adapter_receipt_sha256"],
            "0edaf1e7b7f788ca60ba3cbd6a00228cb7adbf2852a1716107b9fa6e8c7a03aa",
        )
        self.assertEqual(receipt["result"], "SUCCESS")
        self.assertEqual(receipt["authority_scope"], "MISSION_SCOPED")
        self.assertTrue(receipt["draft_pr_only"])
        self.assertTrue(receipt["human_merge_required"])
        self.assertFalse(receipt["production_authority_activated"])
        self.assertEqual(receipt["standing_authority"], "NO")
        self.assertEqual(receipt["checkpoint_count"], 24)
        self.assertEqual(receipt["forbidden_action_confirmation"], "ALL_FALSE_OR_NO")

    def test_live_pr_validation_merge_and_canonical_readback_are_exact(self) -> None:
        live_pr = self.acceptance["live_pull_request"]
        canonical = self.acceptance["canonical_readback"]
        payload = canonical["payload"]
        generated = canonical["generated_checkpoint"]
        self.assertEqual(live_pr["number"], 187)
        self.assertEqual(live_pr["head_sha"], "fa383b816f26160067372fb107120a8a3c4fb2bd")
        self.assertEqual(live_pr["commit_count"], 1)
        self.assertEqual(len(live_pr["changed_files"]), 1)
        self.assertTrue(live_pr["route_created_draft"])
        self.assertEqual(live_pr["exact_readback"], "VERIFIED")
        self.assertEqual(live_pr["exact_head_ci"]["result"], "GREEN")
        self.assertEqual(live_pr["detached_review"], "GREEN")
        self.assertEqual(live_pr["merge_sha"], "c20644641d947485a5d9fad26b6d07ef064dba9b")
        self.assertEqual(payload["git_blob"], "7cad2c8a8bddaa8db171dbf56f6785c8dd98b4e3")
        self.assertEqual(payload["result"], "EXACT")
        self.assertEqual(generated["pull_request"], 188)
        self.assertEqual(generated["merge_sha"], "aee1f837c18dbabf871396ffedf7d9c53e3d8297")
        self.assertEqual(generated["result"], "GREEN_MERGED")

    def test_reconciliation_promotes_only_m06(self) -> None:
        self.assertEqual(self.acceptance["mission_state"], "PROVEN")
        self.assertEqual(self.acceptance["campaign_gate_state"], "NOT_PROVEN")
        self.assertEqual(self.acceptance["capability_promotion"], "NONE")
        self.assertEqual(self.acceptance["acceptance_journey_promotion"], "NONE")
        self.assertTrue(all(value is False for value in self.acceptance["forbidden_promotions"].values()))
        campaign = next(item for item in self.identities["campaigns"] if item["campaign_id"] == "RP-C01")
        missions = {item["mission_id"]: item["state"] for item in campaign["missions"]}
        self.assertEqual(missions["RP-C01-M06"], "PROVEN")
        self.assertEqual(missions["RP-C01-M07"], "PARTIAL")
        self.assertEqual(campaign["state"], "IN_PROGRESS")
        self.assertEqual(self.route["m06_protected_dispatch"]["state"], "PROVEN_MERGED_AUTHENTICATED_PROTECTED_ROUTE")
        self.assertIn("PROVEN_MERGED_AUTHENTICATED_PROTECTED_ROUTE", self.route["mission_states"]["RP-C01-M06"])
        self.assertEqual(self.route["m07_live_rejection_sequence"]["state"], "PARTIAL_NON_OWNER_MISSING")

    def test_continuity_and_quest_preserve_remaining_boundaries(self) -> None:
        repairing = next(
            item for item in self.continuity["entries"] if item["quest_id"] == "QUEST-REPAIRING-PRIME-R01"
        )
        event = "RP-C01-M06-PROTECTED-DISPATCH-ACCEPTANCE-R01"
        self.assertEqual(self.continuity["event_ids"].count(event), 1)
        self.assertEqual(repairing["last_event_id"], event)
        self.assertFalse(any("RP-C01-M06" in blocker for blocker in repairing["blockers"]))
        self.assertTrue(any("RP-C01-M07" in blocker for blocker in repairing["blockers"]))
        quest_path = ROOT / "quests/repairing-prime.md"
        self.assertEqual(repairing["quest_source_sha256"], hashlib.sha256(quest_path.read_bytes()).hexdigest())
        quest = quest_path.read_text(encoding="utf-8")
        self.assertIn("M06 is PROVEN", quest)
        self.assertIn("M07/AJ-03 genuine non-owner rejection remains unproven", quest)
        self.assertIn("CAP-027 remains missing", quest)


if __name__ == "__main__":
    unittest.main()
