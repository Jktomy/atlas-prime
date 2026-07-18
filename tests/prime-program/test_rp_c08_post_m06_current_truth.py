from __future__ import annotations

import json
import unittest
from pathlib import Path

from tools.prime_continuity.engine import sha256 as continuity_sha256

ROOT = Path(__file__).resolve().parents[2]
STRIKEFORCE_PROOF = ROOT / "proof" / "repairing-prime" / "rp-c08-final-whole-quest-strikeforce-reconciliation-r01.md"
RECOVERY_PROOF = ROOT / "proof" / "repairing-prime" / "rp-c08-phoenix-recovery-acceptance-r01.md"

class PostM06CurrentTruthTests(unittest.TestCase):
    def test_repairing_prime_preserves_history_and_closes_after_recovery(self) -> None:
        quest = (ROOT / "quests" / "repairing-prime.md").read_text(encoding="utf-8")
        self.assertIn("PR `#202`", quest)
        self.assertIn("PR `#203`", quest)
        self.assertIn("29421543076", quest)
        self.assertIn("RP-C08-AJ11-FINAL-MAIN-CLEAN-CLONE-PROOF-R02", quest)
        self.assertIn("AJ-01 through AJ-12 are PROVEN", quest)
        self.assertIn("CAP-027: RESTORED / ACTIVE", quest)
        self.assertIn("FINAL WHOLE-QUEST STRIKEFORCE: GREEN", quest)
        self.assertIn("PHOENIX RECOVERY: PROVEN / ACCEPTED", quest)
        self.assertIn("NEXT GATE: CLOSED", quest)
        self.assertIn("No R04, M07, AJ-11, AJ-12, CAP-027, generated-current, Strikeforce, or Phoenix-recovery standing authority carries forward", quest)
        self.assertTrue(STRIKEFORCE_PROOF.is_file())
        self.assertTrue(RECOVERY_PROOF.is_file())

    def test_continuity_register_records_completion_and_removes_active_row(self) -> None:
        register = json.loads((ROOT / "continuity/prime-continuity-register-r01.json").read_text(encoding="utf-8"))
        events = register["event_ids"]
        completion_event = "RP-C08-FINAL-REPAIRING-PRIME-COMPLETION-R05"
        creation_event = "PA-C01-QUEST-CREATION-R01"
        sunset_event = "PA-C01-HOSTED-ACTIONS-SUNSET-R01"
        self.assertNotIn("QUEST-REPAIRING-PRIME-R01", {item["quest_id"] for item in register["entries"]})
        self.assertGreaterEqual(register["register_revision"], 33)
        self.assertEqual(register["source_base_sha"], "e87dbf05252fd80829143474b83b7fa180d66fb7")
        self.assertEqual(events.count(completion_event), 1)
        self.assertEqual(events.count(creation_event), 1)
        self.assertEqual(events.count(sunset_event), 1)
        self.assertLess(events.index(completion_event), events.index(creation_event))
        self.assertLess(events.index(creation_event), events.index(sunset_event))

    def test_quest_board_is_complete_and_closed(self) -> None:
        board = json.loads((ROOT / "quest-board/quest-board-v1.json").read_text(encoding="utf-8"))
        repairing = next(item for item in board["entries"] if item["quest_id"] == "QUEST-REPAIRING-PRIME-R01")
        self.assertEqual(repairing["state"], "COMPLETE")
        self.assertEqual(repairing["next_gate"], "CLOSED")
        self.assertIn("CAP-027 is RESTORED/ACTIVE", repairing["completion_basis"])
        self.assertIn("Sunset PR #224", repairing["completion_basis"])
        self.assertIn("publisher run 29536662886", repairing["completion_basis"])
        register = json.loads((ROOT / "continuity/prime-continuity-register-r01.json").read_text(encoding="utf-8"))
        self.assertEqual(register["quest_board_sha256"], continuity_sha256(board))

    def test_side_quest_independence_and_living_emberline_closeout(self) -> None:
        quest = (ROOT / "quests" / "repairing-prime.md").read_text(encoding="utf-8")
        for independent in ("Found Silverlight", "Prometheus's Fire", "Notum's Watch", "Prime Continuity Proof"):
            self.assertIn(independent, quest)
        self.assertIn("remain independent", quest)
        qem = json.loads((ROOT / "lifecycle/quest-emberlines/QEM-R6QKBDHLY7I7PVVEKIGTZFMZZT.json").read_text(encoding="utf-8"))
        self.assertEqual(qem["quest_state"], "COMPLETE")
        self.assertEqual(qem["next_gate"], "CLOSED")
        self.assertEqual(qem["unresolved_blockers"], [])

if __name__ == "__main__":
    unittest.main()
