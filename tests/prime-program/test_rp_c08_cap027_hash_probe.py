from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class RpC08Cap027HashProbe(unittest.TestCase):
    def test_emit_exact_source_hashes(self) -> None:
        quest_bytes = (ROOT / "quests/repairing-prime.md").read_bytes()
        board = json.loads((ROOT / "quest-board/quest-board-v1.json").read_text(encoding="utf-8"))
        stable_board = (json.dumps(board, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")
        print("CAP027_QUEST_SHA256=" + hashlib.sha256(quest_bytes).hexdigest())
        print("CAP027_BOARD_SHA256=" + hashlib.sha256(stable_board).hexdigest())


if __name__ == "__main__":
    unittest.main()
