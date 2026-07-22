from __future__ import annotations

import json
import unittest
from pathlib import Path

from tools.prime_continuity.engine import sha256


ROOT = Path(__file__).resolve().parents[2]
EVENT = "PRIME-CONTINUITY-PROOF-CLOSEOUT-R01"
QUEST = "QUEST-PRIME-CONTINUITY-PROOF-R01"
CONTINUITY_ID = "CONT-PRIME-CONTINUITY-PROOF-R01"


class PrimeContinuityProofCloseoutTests(unittest.TestCase):
    def test_closeout_preserves_admission_evidence_and_retires_active_continuity(self) -> None:
        board = json.loads((ROOT / "quest-board/quest-board-v1.json").read_text(encoding="utf-8"))
        register = json.loads((ROOT / "continuity/prime-continuity-register-r01.json").read_text(encoding="utf-8"))
        evidence = json.loads(
            (ROOT / "proof/repairing-prime/rp-c05-continuity-evidence-r01.json").read_text(encoding="utf-8")
        )
        quest = (ROOT / "quests/prime-continuity-proof.md").read_text(encoding="utf-8")

        entry = next(item for item in board["entries"] if item["quest_id"] == QUEST)
        self.assertEqual(entry["state"], "COMPLETE")
        self.assertEqual(entry["next_gate"], "CLOSED")
        self.assertIn("Mission #277", entry["completion_basis"])
        self.assertEqual(register["quest_board_sha256"], sha256(board))
        self.assertEqual(register["event_ids"].count(EVENT), 1)
        self.assertNotIn(CONTINUITY_ID, {item["continuity_id"] for item in register["entries"]})

        admission = evidence["transactions"]["aj08_admission"]
        self.assertEqual(evidence["journeys"]["AJ-08"], "PROVEN")
        self.assertEqual(admission["pull_request"], 121)
        self.assertEqual(admission["detached_review"], "GREEN")
        self.assertEqual(
            admission["validator_sha256_unchanged"],
            "714ca7e283e9995c8426cc2d789b4d3018678c9145ad2a582fbce21398bbf506",
        )
        self.assertEqual(
            admission["engine_sha256_unchanged"],
            "4bc8b5773b386b030862c44e00a6b7ec837b324c687219b51ad0e0025b71ce05",
        )
        for marker in (
            'status: "COMPLETE"',
            "No remaining independent Quest-scale objective",
            "authorizes no provider, account, runtime, deployment",
            "`CLOSED`",
        ):
            self.assertIn(marker, quest)


if __name__ == "__main__":
    unittest.main()
