from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

class RpC01M06ProtectedDispatchAcceptanceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.acceptance = json.loads((ROOT / "proof/repairing-prime/rp-c01-m06-protected-dispatch-acceptance-r01.json").read_text(encoding="utf-8"))
        self.route = json.loads((ROOT / "proof/repairing-prime/rp-c01-route-evidence-r01.json").read_text(encoding="utf-8"))
        self.identities = json.loads((ROOT / "continuity/quest-engine-identities-r01.json").read_text(encoding="utf-8"))
        self.continuity = json.loads((ROOT / "continuity/prime-continuity-register-r01.json").read_text(encoding="utf-8"))
        self.board = json.loads((ROOT / "quest-board/quest-board-v1.json").read_text(encoding="utf-8"))

    def test_clean_replacement_is_bound_to_exact_current_main(self) -> None:
        reconciliation = self.acceptance["source_reconciliation"]
        self.assertEqual(self.acceptance["transaction_base_sha"], "91f4392880b7a76f675c933aa429e9f10d1c740e")
        self.assertEqual(reconciliation["decision"], "CLEAN_REPLACEMENT_FROM_EXACT_CURRENT_MAIN")
        self.assertEqual(reconciliation["authored_scope"], "M06_ONLY")
        self.assertEqual(reconciliation["audited_prior_pull_request"], 189)
        self.assertEqual(reconciliation["known_bad_partial_pull_request"], 190)
        self.assertEqual(reconciliation["audited_prior_head_sha"], "b68e3cf33d5b01a95e126189a6d06358c4ee6676")
        self.assertEqual(reconciliation["known_bad_partial_head_sha"], "4a925ef2dfeb3fa461fd4b64e46b8da2242de032")
        self.assertIn("PRESERVED_UNMERGED", reconciliation["audited_prior_disposition"])
        self.assertIn("NEVER_MERGE", reconciliation["known_bad_partial_disposition"])

    def test_live_receipt_binds_exact_protected_route_and_operator(self) -> None:
        live = self.acceptance["live_mission"]
        receipt = self.acceptance["adapter_receipt"]
        bindings = self.acceptance["immutable_bindings"]
        self.assertEqual(live["route_identity"], "AEGIS_BREAK_PROTECTED_PATH_V1")
        self.assertEqual(live["expected_operator_login"], "Jktomy")
        self.assertEqual(live["observed_operator_login"], "Jktomy")
        self.assertEqual(live["base_sha"], "eef4e211d3e4bf6068f1b27cef0dc884a46e2791")
        self.assertEqual(live["stop_point"], "DRAFT_PR_READBACK")
        self.assertEqual(bindings["declared_protected_paths"], ["governance/proof-fixtures/rp-c01-m06-protected-dispatch-marker-r01.md"])
        self.assertEqual(bindings["adapter_receipt_sha256"], "0edaf1e7b7f788ca60ba3cbd6a00228cb7adbf2852a1716107b9fa6e8c7a03aa")
        self.assertEqual(bindings["commit_tree"], "745b553e5c738f56575b80417d0f52eb90ec2de3")
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
        marker = ROOT / payload["path"]
        self.assertEqual(live_pr["number"], 187)
        self.assertEqual(live_pr["base_sha"], "eef4e211d3e4bf6068f1b27cef0dc884a46e2791")
        self.assertEqual(live_pr["head_sha"], "fa383b816f26160067372fb107120a8a3c4fb2bd")
        self.assertEqual(live_pr["commit_tree"], "745b553e5c738f56575b80417d0f52eb90ec2de3")
        self.assertEqual(live_pr["commit_count"], 1)
        self.assertEqual(live_pr["changed_files"], ["governance/proof-fixtures/rp-c01-m06-protected-dispatch-marker-r01.md"])
        self.assertTrue(live_pr["route_created_draft"])
        self.assertEqual(live_pr["exact_readback"], "VERIFIED")
        self.assertEqual(live_pr["comments"], 0)
        self.assertEqual(live_pr["reviews"], 0)
        self.assertEqual(live_pr["review_threads"], 0)
        self.assertEqual(live_pr["exact_head_ci"], {"run": 29333971422, "windows_job": 87088522381, "ubuntu_job": 87088522424, "result": "GREEN"})
        self.assertEqual(live_pr["detached_review"], "GREEN")
        self.assertEqual(live_pr["merge_sha"], "c20644641d947485a5d9fad26b6d07ef064dba9b")
        self.assertEqual(payload["git_blob"], "7cad2c8a8bddaa8db171dbf56f6785c8dd98b4e3")
        self.assertEqual(payload["result"], "EXACT")
        self.assertEqual(hashlib.sha256(marker.read_bytes()).hexdigest(), payload["sha256"])
        self.assertEqual(generated["pull_request"], 188)
        self.assertEqual(generated["workflow_run"], 29334688393)
        self.assertEqual(generated["head_sha"], "12c7a2ef78d1842e0ba5fcc7755a2bc782a09fc1")
        self.assertEqual(generated["merge_sha"], "aee1f837c18dbabf871396ffedf7d9c53e3d8297")
        self.assertEqual(generated["source_fingerprint"], "sha256:b88ddf192094548d522de5c8d92050e24173803861b4c9142670d75253ed3089")
        self.assertEqual(generated["exact_head_ci"], {"run": 29334688393, "windows_job": 87091201859, "ubuntu_job": 87091201983, "result": "GREEN"})
        self.assertEqual(generated["result"], "GREEN_MERGED")

    def test_historical_m06_acceptance_did_not_self_promote_but_later_m07_closes_campaign(self) -> None:
        self.assertEqual(self.acceptance["mission_state"], "PROVEN")
        self.assertEqual(self.acceptance["campaign_gate_state"], "NOT_PROVEN")
        self.assertEqual(self.acceptance["capability_promotion"], "NONE")
        self.assertEqual(self.acceptance["acceptance_journey_promotion"], "NONE")
        self.assertTrue(all(value is False for value in self.acceptance["forbidden_promotions"].values()))
        campaign = next(item for item in self.identities["campaigns"] if item["campaign_id"] == "RP-C01")
        missions = {item["mission_id"]: item["state"] for item in campaign["missions"]}
        self.assertEqual(missions["RP-C01-M06"], "PROVEN")
        self.assertEqual(missions["RP-C01-M07"], "PROVEN")
        self.assertEqual(campaign["state"], "COMPLETE")
        self.assertEqual(self.route["m06_protected_dispatch"]["state"], "PROVEN_MERGED_AUTHENTICATED_PROTECTED_ROUTE")
        self.assertEqual(self.route["m07_live_rejection_sequence"]["state"], "PROVEN_COMPLETE_REJECTION_SET")
        self.assertEqual(self.route["campaign_gate_state"], "ACCEPTED")

    def test_continuity_preserves_m06_history_after_final_closeout(self) -> None:
        m06_event = "RP-C01-M06-PROTECTED-DISPATCH-ACCEPTANCE-R04"
        m07_event = "RP-C01-M07-AJ03-NON-OWNER-ACCEPTANCE-R05"
        aj11_event = "RP-C08-AJ11-CLEAN-CLONE-ACCEPTANCE-RECONCILIATION-R08"
        aj12_event = "RP-C08-AJ12-MERGED-MAIN-VALIDATION-ACCEPTANCE-R01"
        cap027_event = "RP-C08-CAP027-FINAL-CAPABILITY-RECONCILIATION-R01"
        strikeforce_event = "RP-C08-FINAL-WHOLE-QUEST-STRIKEFORCE-RECONCILIATION-R01"
        recovery_event = "RP-C08-PHOENIX-RECOVERY-ACCEPTANCE-R01"
        completion_event = "RP-C08-FINAL-REPAIRING-PRIME-COMPLETION-R05"
        ordered = (m06_event, m07_event, aj11_event, aj12_event, cap027_event, strikeforce_event, recovery_event, completion_event)
        events = self.continuity["event_ids"]
        for event in ordered:
            self.assertEqual(events.count(event), 1)
        for left, right in zip(ordered, ordered[1:]):
            self.assertLess(events.index(left), events.index(right))
        self.assertEqual(self.continuity["register_revision"], 32)
        self.assertEqual(self.continuity["source_base_sha"], "40e58dcf33bae68f8c819c2f65c6474f52381718")
        self.assertNotIn("QUEST-REPAIRING-PRIME-R01", {item["quest_id"] for item in self.continuity["entries"]})
        repairing = next(item for item in self.board["entries"] if item["quest_id"] == "QUEST-REPAIRING-PRIME-R01")
        self.assertEqual(repairing["state"], "COMPLETE")
        self.assertEqual(repairing["next_gate"], "CLOSED")
        quest = (ROOT / "quests/repairing-prime.md").read_text(encoding="utf-8")
        self.assertIn("RP-C01 is `COMPLETE`", quest)
        self.assertIn("AJ-01 through AJ-12 are PROVEN", quest)
        self.assertIn("CAP-027 remains RESTORED and ACTIVE", quest)
        self.assertIn("PHOENIX RECOVERY: PROVEN / ACCEPTED", quest)
        self.assertIn("NEXT GATE: CLOSED", quest)

if __name__ == "__main__":
    unittest.main()
