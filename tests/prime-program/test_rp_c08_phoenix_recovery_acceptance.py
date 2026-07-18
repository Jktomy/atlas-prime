from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

from tools.prime_continuity.engine import sha256 as continuity_sha256

ROOT = Path(__file__).resolve().parents[2]
PROOF_MD = ROOT / "proof" / "repairing-prime" / "rp-c08-phoenix-recovery-acceptance-r01.md"
PROOF_JSON = ROOT / "proof" / "repairing-prime" / "rp-c08-phoenix-recovery-acceptance-r01.json"
QUEST = ROOT / "quests" / "repairing-prime.md"
BOARD = ROOT / "quest-board" / "quest-board-v1.json"
CONTINUITY = ROOT / "continuity" / "prime-continuity-register-r01.json"
ACCEPTANCE = ROOT / "governance" / "capability-acceptance-contract.md"

def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))

def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

class PhoenixRecoveryAcceptanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.proof = load_json(PROOF_JSON)
        cls.board = load_json(BOARD)
        cls.continuity = load_json(CONTINUITY)

    def test_exact_evidence_and_main_bindings_are_preserved(self) -> None:
        accepted = self.proof["accepted_recovery_proof"]
        self.assertEqual(self.proof["transaction_base_sha"], "797fb2a1add829ccc304086a56f6d223d130d90d")
        self.assertEqual(accepted["expected_sha"], "797fb2a1add829ccc304086a56f6d223d130d90d")
        self.assertEqual(accepted["observed_sha"], "797fb2a1add829ccc304086a56f6d223d130d90d")
        self.assertEqual(accepted["remote_main_before"], "797fb2a1add829ccc304086a56f6d223d130d90d")
        self.assertEqual(accepted["remote_main_after"], "797fb2a1add829ccc304086a56f6d223d130d90d")
        self.assertEqual(accepted["oathbringer_carrier_sha256"], "a1083ca9c5123b1bfa552602b008a45314cab847c50e143cc58d80275ed8fa75")
        self.assertEqual(accepted["receipt_gemstone_sha256"], "9dc2726e30f6b3ff8748804e991feb1441a03dcd715212d9cf391203dbfc22e7")
        self.assertEqual(accepted["original_private_evidence_zip_sha256"], "b4049ff69a9347ad7ca7ee2fd0712966c8a45888faba86df1d656127fc156103")
        self.assertEqual(accepted["sanitized_detached_audit_envelope_sha256"], "a920e86fa22a548521e619bd1d77d267b39b617b221ee36c63d53b4dcc832617")
        self.assertEqual(accepted["mission_sha256"], "3dc5d82aa0bccf8f6bde2b897913ad5072fc823e88d2c58c6d78de2f4a8efb98")
        self.assertEqual(accepted["receipt_self_sha256"], "7fc50f501ae4599081c62abcd7f126163247568c4140604c342f80f8b0d36b02")
        self.assertEqual(accepted["receipt_file_sha256"], "1705807d142c361d61b039b5cca6f7eeebe3ba893e398c1d5a0e78ea8701fbab")
        self.assertEqual(accepted["receipt_sidecar_file_sha256"], "00667cdda52ec0012225326d3d9f4f31ac4215472c927d12d56b016db7fa79f7")
        self.assertEqual(accepted["original_transcript_sha256"], "9f575cf72279097117c77a44197a99eab2eb5697537f65706d8c0837a49323f3")
        self.assertEqual(accepted["sanitized_transcript_sha256"], "50c3209b71d8bbb7c5e59f57fa8b615e0d74f38a364e8e989fc9e90422740477")

    def test_recovery_substance_and_zero_mutation_are_accepted(self) -> None:
        accepted = self.proof["accepted_recovery_proof"]
        self.assertTrue(accepted["clone_isolated"])
        self.assertTrue(accepted["detached_exact_head"])
        self.assertTrue(accepted["symlink_free"])
        self.assertEqual(accepted["inherited_hooks"], [])
        self.assertEqual(accepted["inherited_worktrees"], [])
        self.assertTrue(accepted["working_tree_clean_before"])
        self.assertTrue(accepted["working_tree_clean_after"])
        self.assertEqual(accepted["validation"], {"result": "GREEN", "command_count": 13, "pass_count": 13, "all_commands_passed": True})
        self.assertEqual(accepted["generated_state"], {"status": "CURRENT", "changed_paths": [], "projection_count": 5, "all_outputs_byte_equal": True})
        self.assertFalse(accepted["normal_atlas_codex_dependency"])
        self.assertEqual(accepted["rollback_classification"]["source_rollback"], "NEW_REVIEWED_PR")
        self.assertEqual(accepted["rollback_classification"]["force_push"], "FORBIDDEN")
        self.assertEqual(accepted["rollback_classification"]["history_rewrite"], "FORBIDDEN")
        self.assertTrue(all(value is False for value in accepted["mutation"].values()))

    def test_detached_audit_and_stage_limitation_are_truthful(self) -> None:
        audit = self.proof["detached_audit"]
        self.assertEqual(audit["checks_passed"], 22)
        self.assertEqual(audit["privacy_scan"], "GREEN")
        self.assertEqual(audit["canonical_main_readback"], "797fb2a1add829ccc304086a56f6d223d130d90d")
        self.assertEqual(audit["canonical_main_comparison"], "IDENTICAL")
        self.assertEqual(audit["ahead_by"], 0)
        self.assertEqual(audit["behind_by"], 0)
        self.assertEqual(audit["result"], "GREEN")
        limitation = self.proof["preserved_stage_ledger_limitation"]
        self.assertEqual(limitation["original_receipt_current_stage"], "EVIDENCE_SEAL")
        self.assertEqual(limitation["original_receipt_last_completed_stage"], "FINAL_READBACK")
        self.assertEqual(limitation["original_transcript_endpoint"], "STAGE_ENTER EVIDENCE_SEAL")
        self.assertFalse(limitation["original_zip_self_contains_evidence_seal_completion"])
        self.assertFalse(limitation["original_zip_self_contains_stop_boundary_completion"])
        self.assertTrue(limitation["limitation_disclosed_not_rewritten"])

    def test_historical_recovery_transition_remains_exact(self) -> None:
        self.assertEqual(self.proof["transitions"], {"PHOENIX_RECOVERY": {"from": "PENDING", "to": "PROVEN/ACCEPTED"}})
        self.assertEqual(self.proof["preserved_open"], ["RESTART_SAFE_SUNSET", "RP-C08", "QUEST-REPAIRING-PRIME-R01"])
        self.assertTrue(all(value is False for value in self.proof["forbidden_promotions"].values()))
        self.assertEqual(self.proof["capability_counts"], {"PRESERVED": 4, "IMPROVED": 7, "RESTORED": 15, "REPLACED": 1, "INTENTIONALLY_RETIRED": 1, "BLOCKED": 0, "STILL_MISSING": 0})
        self.assertFalse(self.proof["protected_data"]["original_private_evidence_embedded"])
        self.assertFalse(self.proof["protected_data"]["sanitized_envelope_embedded"])
        self.assertEqual(self.proof["next_gate"], "RESTART_SAFE_SUNSET")

    def test_current_surfaces_close_after_later_sunset_and_completion(self) -> None:
        quest = QUEST.read_text(encoding="utf-8")
        acceptance = ACCEPTANCE.read_text(encoding="utf-8")
        repairing_board = next(item for item in self.board["entries"] if item["quest_id"] == "QUEST-REPAIRING-PRIME-R01")
        events = self.continuity["event_ids"]
        creation_event = "PA-C01-QUEST-CREATION-R01"
        sunset_event = "PA-C01-HOSTED-ACTIONS-SUNSET-R01"
        self.assertIn("PHOENIX RECOVERY: PROVEN / ACCEPTED", quest)
        self.assertIn("NEXT GATE: CLOSED", quest)
        self.assertIn("Final Phoenix recovery is `PROVEN` and `ACCEPTED`", acceptance)
        self.assertEqual(repairing_board["state"], "COMPLETE")
        self.assertEqual(repairing_board["next_gate"], "CLOSED")
        self.assertIn("Sunset PR #224", repairing_board["completion_basis"])
        self.assertNotIn("CONT-REPAIRING-PRIME-R01", {item["continuity_id"] for item in self.continuity["entries"]})
        self.assertGreaterEqual(self.continuity["register_revision"], 33)
        self.assertEqual(self.continuity["source_base_sha"], "e87dbf05252fd80829143474b83b7fa180d66fb7")
        self.assertEqual(events.count(creation_event), 1)
        self.assertEqual(events.count(sunset_event), 1)
        self.assertLess(events.index(creation_event), events.index(sunset_event))
        self.assertEqual(self.continuity["quest_board_sha256"], continuity_sha256(self.board))
        self.assertTrue(PROOF_MD.is_file())

if __name__ == "__main__":
    unittest.main()
