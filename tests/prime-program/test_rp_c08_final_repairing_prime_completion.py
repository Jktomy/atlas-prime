from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVENT = "RP-C08-FINAL-REPAIRING-PRIME-COMPLETION-R05"
BASE = "40e58dcf33bae68f8c819c2f65c6474f52381718"

def load(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))

def assert_final_state(case: unittest.TestCase) -> None:
    board = load("quest-board/quest-board-v1.json")
    register = load("continuity/prime-continuity-register-r01.json")
    identities = load("continuity/quest-engine-identities-r01.json")
    qem = load("lifecycle/quest-emberlines/QEM-R6QKBDHLY7I7PVVEKIGTZFMZZT.json")
    repairing = next(item for item in board["entries"] if item["quest_id"] == "QUEST-REPAIRING-PRIME-R01")
    case.assertEqual(repairing["state"], "COMPLETE")
    case.assertEqual(repairing["next_gate"], "CLOSED")
    case.assertIn("Sunset PR #224", repairing["completion_basis"])
    case.assertNotIn("QUEST-REPAIRING-PRIME-R01", {item["quest_id"] for item in register["entries"]})
    case.assertEqual(register["register_revision"], 32)
    case.assertEqual(register["source_base_sha"], BASE)
    case.assertEqual(register["event_ids"].count(EVENT), 1)
    case.assertEqual(register["event_ids"][-1], EVENT)
    rp_c08 = next(item for item in identities["campaigns"] if item["campaign_id"] == "RP-C08")
    case.assertEqual(rp_c08["state"], "COMPLETE")
    case.assertEqual(qem["quest_revision"], 4)
    case.assertEqual(qem["quest_state"], "COMPLETE")
    case.assertEqual(qem["current_entry_id"], "Final-Gate-007")
    case.assertEqual(qem["journey_entries"][-1]["entry_type"], "FINAL")
    case.assertEqual(qem["next_gate"], "CLOSED")
    case.assertEqual(qem["unresolved_blockers"], [])

class FinalRepairingPrimeCompletionTests(unittest.TestCase):
    def test_all_final_surfaces_are_coherent(self) -> None:
        assert_final_state(self)
        quest = (ROOT / "quests/repairing-prime.md").read_text(encoding="utf-8")
        proof = (ROOT / "proof/repairing-prime/rp-c08-final-repairing-prime-completion-r05.md").read_text(encoding="utf-8")
        for token in ("**Current state:** `COMPLETE`", "RP-C08: COMPLETE", "Repairing Prime: COMPLETE", "NEXT GATE: CLOSED", BASE, "29536662886", "sha256:2722defc94f60dddaa35cae3faf66796cdf01c1ed1e100ffe10fece6c83b2565"):
            self.assertIn(token, quest)
        self.assertIn("PR `#221` and PR `#226` remain DEFLECTED evidence", proof)

    def test_continuity_digest_and_independent_quest_states(self) -> None:
        from tools.prime_continuity.engine import sha256
        board = load("quest-board/quest-board-v1.json")
        register = load("continuity/prime-continuity-register-r01.json")
        self.assertEqual(register["quest_board_sha256"], sha256(board))
        states = {e["quest_id"]: e["state"] for e in board["entries"]}
        self.assertEqual(states["QUEST-FOUND-SILVERLIGHT-R01"], "IN_PROGRESS")
        self.assertEqual(states["QUEST-PROMETHEUS-FIRE-20260701"], "IN_PROGRESS")
        self.assertEqual(states["QUEST-NOTUMS-WATCH-20260708"], "READY_FOR_JAYSON_EXECUTION_PACKAGE")
        self.assertEqual(states["QUEST-PRIME-CONTINUITY-PROOF-R01"], "READY_FOR_CAMPAIGN_1_PREVIEW")

    def test_living_emberline_parent_and_final_entry_are_exact(self) -> None:
        qem = load("lifecycle/quest-emberlines/QEM-R6QKBDHLY7I7PVVEKIGTZFMZZT.json")
        self.assertEqual(qem["revision_parent_digest"], "sha256:628548a1ea044a5e18c0adef496f7bd2eba7cb243b3112efe9ec4923b0c2b7ff")
        self.assertEqual(qem["journey_entries"][-1]["entry_id"], "Final-Gate-007")
        self.assertIn("PR #224", qem["journey_entries"][-1]["outcome"])
        self.assertIn("sha256:2722defc94f60dddaa35cae3faf66796cdf01c1ed1e100ffe10fece6c83b2565", qem["journey_entries"][-1]["outcome"])

if __name__ == "__main__":
    unittest.main()
