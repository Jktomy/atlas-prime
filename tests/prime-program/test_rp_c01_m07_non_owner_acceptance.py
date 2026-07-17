from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROOF = ROOT / "proof/repairing-prime/rp-c01-m07-non-owner-acceptance-r01.json"
RECEIPT_SHA256 = "2b96117650e426b2fdea9b830b5ef8da1ee69ee74fb6127f90c9de648e13999b"

class RpC01M07NonOwnerAcceptanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.proof = json.loads(PROOF.read_text(encoding="utf-8"))
        cls.route = json.loads((ROOT / "proof/repairing-prime/rp-c01-route-evidence-r01.json").read_text(encoding="utf-8"))
        cls.identities = json.loads((ROOT / "continuity/quest-engine-identities-r01.json").read_text(encoding="utf-8"))
        cls.continuity = json.loads((ROOT / "continuity/prime-continuity-register-r01.json").read_text(encoding="utf-8"))
        cls.board = json.loads((ROOT / "quest-board/quest-board-v1.json").read_text(encoding="utf-8"))
        cls.capabilities = json.loads((ROOT / "governance/capability-parity-register.json").read_text(encoding="utf-8"))

    def test_exact_live_identity_and_rejection_are_bound(self) -> None:
        live = self.proof["live_non_owner_rejection"]
        receipt = self.proof["sanitized_receipt"]
        self.assertEqual(live["workflow_run"], 29421543076)
        self.assertEqual(live["preflight_job"]["id"], 87372991737)
        self.assertEqual(live["thread_engine_job"], {"id": 87373032342, "conclusion": "SKIPPED"})
        self.assertEqual(live["non_owner_actor"], "jaysontomyod")
        self.assertEqual(receipt["identity"]["event_actor"], "jaysontomyod")
        self.assertEqual(receipt["identity"]["triggering_actor"], "jaysontomyod")
        self.assertEqual(receipt["error_code"], "OWNER_IDENTITY_REJECTED")
        self.assertEqual(receipt["stage"], "PRE_MUTATION_REJECTION")
        self.assertEqual(receipt["stop_point"], "PRE_MUTATION_REJECTION")

    def test_receipt_and_post_run_readback_prove_zero_mutation(self) -> None:
        receipt = self.proof["sanitized_receipt"]
        readback = self.proof["post_run_readback"]
        self.assertFalse(receipt["mutation"]["occurred"])
        self.assertIsNone(receipt["mutation"]["branch"])
        self.assertIsNone(receipt["mutation"]["pull_request"])
        self.assertIsNone(receipt["mutation"]["head_sha"])
        self.assertTrue(all(value is False for value in receipt["forbidden_action_confirmation"].values()))
        self.assertTrue(readback["canonical_main_unchanged"])
        self.assertEqual(readback["canonical_main_sha"], "bd10062b87e2c2f26f3b99969b0d1bab30e76ac0")
        self.assertIsNone(readback["new_branch"])
        self.assertIsNone(readback["new_pull_request"])
        self.assertFalse(readback["thread_engine_invoked"])
        self.assertTrue(readback["temporary_access_removed"])
        self.assertEqual(readback["observed_permission_after"], "none")

    def test_artifact_and_receipt_hashes_are_exact(self) -> None:
        artifact = self.proof["artifact_binding"]
        self.assertEqual(artifact["artifact_id"], 8345413762)
        self.assertEqual(artifact["artifact_zip_sha256"], "77795a9da645a6788f369f31ed84a2141445366dff1f81807dec2d6ce47e5699")
        self.assertEqual(artifact["receipt_sha256"], RECEIPT_SHA256)
        canonical_receipt = (json.dumps(self.proof["sanitized_receipt"], sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")
        self.assertEqual(hashlib.sha256(canonical_receipt).hexdigest(), RECEIPT_SHA256)

    def test_only_m07_aj03_and_rp_c01_transition(self) -> None:
        self.assertEqual(set(self.proof["transitions"]), {"RP-C01-M07", "AJ-03", "RP-C01", "ATHENA_NATIVE_EXECUTION_ROUTES_PROVEN"})
        self.assertEqual(self.proof["mission_state"], "PROVEN")
        self.assertEqual(self.proof["acceptance_journey_state"], "PROVEN")
        self.assertEqual(self.proof["campaign_state"], "COMPLETE")
        self.assertEqual(self.proof["capability_promotion"], "NONE")
        self.assertFalse(self.proof["capability_counts_changed"])
        self.assertTrue(all(value is False for value in self.proof["forbidden_promotions"].values()))
        campaign = next(item for item in self.identities["campaigns"] if item["campaign_id"] == "RP-C01")
        self.assertEqual(campaign["state"], "COMPLETE")
        self.assertTrue(all(item["state"] == "PROVEN" for item in campaign["missions"]))
        self.assertEqual(self.route["campaign_gate_state"], "ACCEPTED")

    def test_later_final_closeout_preserves_non_owner_evidence(self) -> None:
        board = next(item for item in self.board["entries"] if item["quest_id"] == "QUEST-REPAIRING-PRIME-R01")
        cap027 = next(item for item in self.capabilities["capabilities"] if item["id"] == "CAP-027")
        self.assertEqual(board["state"], "COMPLETE")
        self.assertEqual(board["next_gate"], "CLOSED")
        self.assertIn("Sunset PR #224", board["completion_basis"])
        self.assertNotIn("QUEST-REPAIRING-PRIME-R01", {item["quest_id"] for item in self.continuity["entries"]})
        self.assertEqual(self.continuity["event_ids"].count("RP-C01-M07-AJ03-NON-OWNER-ACCEPTANCE-R05"), 1)
        self.assertEqual(self.continuity["event_ids"][-1], "RP-C08-FINAL-REPAIRING-PRIME-COMPLETION-R05")
        self.assertEqual(cap027["capability_disposition"], "RESTORED")
        self.assertEqual(cap027["activation_state"], "ACTIVE")
        self.assertIn("AJ-01 through AJ-12 are PROVEN", cap027["current_state"])
        self.assertIn("rp-c08-cap027-final-capability-reconciliation-r01.md", cap027["required_proof"])

if __name__ == "__main__":
    unittest.main()
