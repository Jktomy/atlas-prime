from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

class RpC01M05ParityAcceptanceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.acceptance_path = ROOT / "proof/repairing-prime/rp-c01-m05-parity-acceptance-r01.json"
        self.parity_path = ROOT / "proof/repairing-prime/rp-c01-m05-parity-evidence-r01.json"
        self.acceptance = json.loads(self.acceptance_path.read_text(encoding="utf-8"))
        self.parity = json.loads(self.parity_path.read_text(encoding="utf-8"))
        self.route = json.loads((ROOT / "proof/repairing-prime/rp-c01-route-evidence-r01.json").read_text(encoding="utf-8"))
        self.identities = json.loads((ROOT / "continuity/quest-engine-identities-r01.json").read_text(encoding="utf-8"))
        self.continuity = json.loads((ROOT / "continuity/prime-continuity-register-r01.json").read_text(encoding="utf-8"))
        self.board = json.loads((ROOT / "quest-board/quest-board-v1.json").read_text(encoding="utf-8"))

    def test_one_carrier_joins_direct_compiler_guided_and_hosted_evidence(self) -> None:
        journey = self.acceptance["same_carrier_journey"]
        direct = self.acceptance["direct_compilation"]
        hosted = self.acceptance["guided_and_hosted_evidence"]
        self.assertEqual(journey["carrier_sha256"], self.parity["carrier_sha256"])
        self.assertEqual(direct["compile_receipt_sha256"], self.parity["compiler"]["compile_receipt_sha256"])
        self.assertEqual(journey["candidate_tree_sha256"], self.parity["compiler"]["candidate_tree_sha256"])
        self.assertEqual(journey["final_pathset_sha256"], self.parity["compiler"]["final_pathset_sha256"])
        self.assertEqual(hosted["workflow_run"], self.parity["workflow_run_id"])
        self.assertEqual(self.parity["result"], "PARITY_VERIFIED")
        self.assertTrue(all(self.parity["invariants"].values()))

    def test_hosted_route_created_and_read_back_exact_draft_pr(self) -> None:
        live = self.acceptance["live_pull_request"]
        hosted = self.acceptance["guided_and_hosted_evidence"]
        self.assertTrue(live["route_created_draft"])
        self.assertEqual(live["exact_readback"], "VERIFIED")
        self.assertEqual(live["number"], self.parity["adapter"]["pull_request"])
        self.assertEqual(live["head_sha"], self.parity["adapter"]["head_sha"])
        self.assertEqual(hosted["checkpoint_count"], 24)
        self.assertEqual(hosted["pre_push_remote_lock_position"], "BETWEEN_COMMIT_VERIFY_AND_PUSH")
        self.assertTrue(hosted["singular_adapter_execution"])
        self.assertEqual(live["exact_head_ci"]["result"], "GREEN")
        self.assertEqual(live["detached_review"], "GREEN")
        self.assertEqual(live["canonical_payload_readback"]["result"], "EXACT")

    def test_parity_artifact_is_exact_and_separate_reconciliation_promotes_only_m05(self) -> None:
        self.assertEqual(hashlib.sha256(self.parity_path.read_bytes()).hexdigest(), "588306d3a0858d0a477f1aaf0ca170dc8b77e0cac6ab775e76716044559f68e8")
        self.assertEqual(self.parity["promotion_boundary"], "SEPARATE_AUTHORED_RECONCILIATION_REQUIRED")
        self.assertEqual(self.acceptance["mission_state"], "PROVEN")
        self.assertEqual(self.acceptance["campaign_gate_state"], "NOT_PROVEN")
        self.assertEqual(self.acceptance["capability_promotion"], "NONE")
        self.assertEqual(self.acceptance["acceptance_journey_promotion"], "NONE")
        self.assertTrue(all(value is False for value in self.acceptance["forbidden_promotions"].values()))
        campaign = next(item for item in self.identities["campaigns"] if item["campaign_id"] == "RP-C01")
        missions = {item["mission_id"]: item["state"] for item in campaign["missions"]}
        self.assertEqual(missions["RP-C01-M05"], "PROVEN")
        self.assertEqual(campaign["state"], "COMPLETE")
        self.assertEqual(missions["RP-C01-M07"], "PROVEN")

    def test_route_history_and_final_closeout_are_both_preserved(self) -> None:
        self.assertEqual(self.route["m05_same_carrier_parity"]["state"], "PROVEN")
        self.assertIn("PROVEN_SAME_CARRIER", self.route["mission_states"]["RP-C01-M05"])
        events = self.continuity["event_ids"]
        self.assertEqual(self.acceptance["transaction_base_sha"], "df66ae78dac1991db3902537fe338a4191d0da11")
        self.assertEqual(events.count("RP-C01-M05-PARITY-ACCEPTANCE-R01"), 1)
        self.assertEqual(events.count("RP-C08-FINAL-REPAIRING-PRIME-COMPLETION-R05"), 1)
        self.assertLess(events.index("RP-C01-M05-PARITY-ACCEPTANCE-R01"), events.index("RP-C08-FINAL-REPAIRING-PRIME-COMPLETION-R05"))
        self.assertGreaterEqual(self.continuity["register_revision"], 32)
        self.assertNotIn("QUEST-REPAIRING-PRIME-R01", {item["quest_id"] for item in self.continuity["entries"]})
        repairing = next(item for item in self.board["entries"] if item["quest_id"] == "QUEST-REPAIRING-PRIME-R01")
        self.assertEqual(repairing["state"], "COMPLETE")
        self.assertEqual(repairing["next_gate"], "CLOSED")

if __name__ == "__main__":
    unittest.main()
