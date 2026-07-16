from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

from tools.prime_continuity.engine import sha256 as continuity_sha256


ROOT = Path(__file__).resolve().parents[2]
PROOF = ROOT / "proof" / "repairing-prime" / "rp-c08-final-whole-quest-strikeforce-reconciliation-r01.md"


class PostM06CurrentTruthTests(unittest.TestCase):
    def test_repairing_prime_preserves_post_m06_history_and_accepts_final_strikeforce(self) -> None:
        quest = (ROOT / "quests" / "repairing-prime.md").read_text(encoding="utf-8")
        self.assertIn("PR `#202`", quest)
        self.assertIn("PR `#203`", quest)
        self.assertIn("29421543076", quest)
        self.assertIn("RP-C08-AJ11-FINAL-MAIN-CLEAN-CLONE-PROOF-R02", quest)
        self.assertIn("AJ-01 through AJ-12 are PROVEN", quest)
        self.assertIn("CAP-027: RESTORED / ACTIVE", quest)
        self.assertIn("FINAL WHOLE-QUEST STRIKEFORCE: GREEN", quest)
        self.assertIn("NEXT GATE: PHOENIX RECOVERY", quest)
        self.assertIn("No R04, M07, AJ-11, AJ-12, CAP-027, generated-current, or Strikeforce standing authority carries forward", quest)
        self.assertTrue(PROOF.is_file())

    def test_continuity_register_matches_current_gate(self) -> None:
        register = json.loads((ROOT / "continuity/prime-continuity-register-r01.json").read_text(encoding="utf-8"))
        entry = next(item for item in register["entries"] if item["quest_id"] == "QUEST-REPAIRING-PRIME-R01")
        self.assertIsNone(entry["mission_id"])
        self.assertEqual(
            entry["last_event_id"],
            "RP-C08-FINAL-WHOLE-QUEST-STRIKEFORCE-RECONCILIATION-R01",
        )
        self.assertIn("Phoenix recovery", entry["next_action"])
        self.assertNotIn("whole-Quest Strikeforce", entry["next_action"])
        self.assertIn("separately authorize", entry["next_approval"])
        self.assertNotIn("genuine non-owner", entry["next_action"])
        self.assertFalse(any("CAP-027 remains missing" in blocker for blocker in entry["blockers"]))
        self.assertFalse(any("AJ-12 requires complete" in blocker for blocker in entry["blockers"]))

    def test_quest_board_routes_to_phoenix_recovery(self) -> None:
        board = json.loads((ROOT / "quest-board/quest-board-v1.json").read_text(encoding="utf-8"))
        repairing = next(item for item in board["entries"] if item["quest_id"] == "QUEST-REPAIRING-PRIME-R01")
        self.assertEqual(
            repairing["next_gate"],
            "Phoenix recovery, then restart-safe Sunset and final Quest closeout",
        )
        self.assertIn("CAP-027 is RESTORED/ACTIVE", repairing["readiness_basis"])
        self.assertIn("final whole-Quest Strikeforce is GREEN", repairing["readiness_basis"])
        register = json.loads((ROOT / "continuity/prime-continuity-register-r01.json").read_text(encoding="utf-8"))
        self.assertEqual(register["quest_board_sha256"], continuity_sha256(board))

    def test_quest_digest_and_side_quest_independence(self) -> None:
        quest_path = ROOT / "quests" / "repairing-prime.md"
        quest_bytes = quest_path.read_bytes()
        register = json.loads((ROOT / "continuity/prime-continuity-register-r01.json").read_text(encoding="utf-8"))
        entry = next(item for item in register["entries"] if item["quest_id"] == "QUEST-REPAIRING-PRIME-R01")
        self.assertEqual(entry["quest_source_sha256"], hashlib.sha256(quest_bytes).hexdigest())
        quest = quest_bytes.decode("utf-8")
        for independent in ("Found Silverlight", "Prometheus's Fire", "Notum's Watch", "Prime Continuity Proof"):
            self.assertIn(independent, quest)
        self.assertIn("remain independent", quest)


if __name__ == "__main__":
    unittest.main()
