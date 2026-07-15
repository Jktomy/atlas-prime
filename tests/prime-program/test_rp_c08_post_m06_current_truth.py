from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

from tools.prime_continuity.engine import sha256 as continuity_sha256


ROOT = Path(__file__).resolve().parents[2]


class PostM06CurrentTruthTests(unittest.TestCase):
    def test_repairing_prime_preserves_post_m06_history_and_accepts_aj12(self) -> None:
        quest = (ROOT / "quests" / "repairing-prime.md").read_text(encoding="utf-8")
        self.assertIn("PR `#202`", quest)
        self.assertIn("PR `#203`", quest)
        self.assertIn("29421543076", quest)
        self.assertIn("RP-C08-AJ11-FINAL-MAIN-CLEAN-CLONE-PROOF-R02", quest)
        self.assertIn("AJ-01 through AJ-12 are PROVEN", quest)
        self.assertIn("AJ-12: PROVEN", quest)
        self.assertIn("No R04, M07, AJ-11, or AJ-12 standing authority carries forward", quest)

    def test_continuity_register_matches_current_gate(self) -> None:
        register = json.loads((ROOT / "continuity/prime-continuity-register-r01.json").read_text(encoding="utf-8"))
        entry = next(item for item in register["entries"] if item["quest_id"] == "QUEST-REPAIRING-PRIME-R01")
        self.assertIsNone(entry["mission_id"])
        self.assertEqual(
            entry["last_event_id"],
            "RP-C08-AJ12-MERGED-MAIN-VALIDATION-ACCEPTANCE-R01",
        )
        self.assertIn("CAP-027", entry["next_action"])
        self.assertIn("separately authorize", entry["next_approval"])
        self.assertNotIn("genuine non-owner", entry["next_action"])
        self.assertFalse(any("AJ-11 requires" in blocker for blocker in entry["blockers"]))
        self.assertFalse(any("AJ-12 requires complete" in blocker for blocker in entry["blockers"]))

    def test_quest_board_routes_through_generated_current_to_cap027(self) -> None:
        board = json.loads((ROOT / "quest-board/quest-board-v1.json").read_text(encoding="utf-8"))
        repairing = next(item for item in board["entries"] if item["quest_id"] == "QUEST-REPAIRING-PRIME-R01")
        self.assertEqual(
            repairing["next_gate"],
            "Generated-current readback after AJ-12 acceptance, then CAP-027 and RP-C08 final capability reconciliation",
        )
        self.assertIn("AJ-12 is accepted", repairing["readiness_basis"])
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
