from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

from tools.prime_continuity.engine import sha256 as continuity_sha256


ROOT = Path(__file__).resolve().parents[2]


class PostM06CurrentTruthTests(unittest.TestCase):
    def test_repairing_prime_routes_to_m07(self) -> None:
        quest = (ROOT / "quests" / "repairing-prime.md").read_text(encoding="utf-8")
        self.assertIn("RP-C01-M07 / AJ-03", quest)
        self.assertIn("PR `#200`", quest)
        self.assertIn("PR `#201`", quest)
        self.assertIn("70f8f31c1107e0b59827870cc3803daccf8414c8", quest)
        self.assertIn("No R04 standing authority carries forward", quest)

    def test_continuity_register_matches_current_gate(self) -> None:
        path = ROOT / "continuity" / "prime-continuity-register-r01.json"
        register = json.loads(path.read_text(encoding="utf-8"))
        entry = next(
            item
            for item in register["entries"]
            if item["quest_id"] == "QUEST-REPAIRING-PRIME-R01"
        )
        self.assertIsNone(entry["mission_id"])
        self.assertEqual(
            entry["last_event_id"],
            "RP-C08-POST-M06-CURRENT-TRUTH-R01",
        )
        self.assertIn("genuine non-owner", entry["next_action"])
        self.assertIn("separately authorize", entry["next_approval"])
        self.assertNotIn("Complete the separate Gate 4 generated refresh", entry["next_action"])

    def test_quest_board_routes_to_exact_preview(self) -> None:
        board_path = ROOT / "quest-board" / "quest-board-v1.json"
        board_bytes = board_path.read_bytes()
        board = json.loads(board_bytes)
        repairing = next(
            item
            for item in board["entries"]
            if item["quest_id"] == "QUEST-REPAIRING-PRIME-R01"
        )
        self.assertEqual(
            repairing["next_gate"],
            "RP-C01-M07 / AJ-03 Preview — Genuine non-owner rejection",
        )
        self.assertIn("M06 is PROVEN", repairing["readiness_basis"])

        register = json.loads(
            (ROOT / "continuity" / "prime-continuity-register-r01.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(
            register["quest_board_sha256"],
            continuity_sha256(board),
        )

    def test_quest_digest_and_side_quest_independence(self) -> None:
        quest_path = ROOT / "quests" / "repairing-prime.md"
        quest_bytes = quest_path.read_bytes()
        register = json.loads(
            (ROOT / "continuity" / "prime-continuity-register-r01.json").read_text(
                encoding="utf-8"
            )
        )
        entry = next(
            item
            for item in register["entries"]
            if item["quest_id"] == "QUEST-REPAIRING-PRIME-R01"
        )
        self.assertEqual(
            entry["quest_source_sha256"],
            hashlib.sha256(quest_bytes).hexdigest(),
        )

        quest = quest_bytes.decode("utf-8")
        for independent in (
            "Found Silverlight",
            "Prometheus's Fire",
            "Notum's Watch",
            "Prime Continuity Proof",
        ):
            self.assertIn(independent, quest)
        self.assertIn("remain independent", quest)


if __name__ == "__main__":
    unittest.main()
