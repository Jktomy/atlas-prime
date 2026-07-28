from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class QuestPortfolioRecompositionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.contract = (ROOT / "governance/atlas-quest-portfolio-contract.md").read_text(encoding="utf-8")
        self.board = json.loads((ROOT / "quest-board/quest-board-v1.json").read_text(encoding="utf-8"))
        self.registry = json.loads(
            (ROOT / "continuity/mission-board-quest-registry-r01.json").read_text(encoding="utf-8")
        )

    def test_atlas_is_umbrella_and_target_owners_are_unique(self) -> None:
        self.assertIn("Atlas is the umbrella ecosystem, not a Quest", self.contract)
        self.assertNotIn("ATLAS-QUEST", {entry["quest_id"] for entry in self.board["entries"]})
        for destination in (
            "The Odyssey / Operation Glass Codex",
            "The Odyssey / Operation Harmony",
            "Codex / Operation Source Governance bounded Mission family",
            "The Odyssey / Operation Sentinel and Citadel/Gatehouse Infrastructure",
            "The Odyssey / Operation Prometheus Foundation",
        ):
            self.assertIn(destination, self.contract)

    def test_current_odyssey_and_frozen_historical_states_are_distinct(self) -> None:
        self.assertEqual(
            [entry["quest_id"] for entry in self.registry["entries"]],
            ["QUEST-THE-ODYSSEY-20260727"],
        )
        self.assertIn("| The Odyssey | #359 |", self.contract)
        self.assertIn("initial\nthree-parent map remains preserved history", self.contract)
        observed = {entry["quest_id"]: (entry["state"], entry["next_gate"]) for entry in self.board["entries"]}
        self.assertEqual(observed["QUEST-FOUND-SILVERLIGHT-R01"], ("COMPLETE", "CLOSED"))
        self.assertEqual(observed["QUEST-PRIME-CONTINUITY-PROOF-R01"], ("COMPLETE", "CLOSED"))
        self.assertEqual(observed["QUEST-PROMETHEUS-FIRE-20260701"], ("IN_PROGRESS", "PF-C01-M02 Preview — Preserve the Old Flame"))
        self.assertEqual(observed["QUEST-NOTUMS-WATCH-20260708"], ("READY_FOR_JAYSON_EXECUTION_PACKAGE", "NW-C01 readiness package and Jayson-side proof"))
        self.assertEqual(observed["QUEST-PRIME-ASCENDANT-20260717"], ("IN_PROGRESS", "PA-C01 — Write the Covenant"))
        self.assertEqual(observed["PRIME-REBORN-QUEST-R01"], ("COMPLETE", "CLOSED"))
        self.assertEqual(observed["QUEST-REPAIRING-PRIME-R01"], ("COMPLETE", "CLOSED"))

    def test_transfer_does_not_advance_protected_or_runtime_gates(self) -> None:
        for marker in (
            "FS-C01-M01 through M03 remain proven; FS-C01-M04 remains unfinished",
            "Apple Reminders remains authoritative for Seon",
            "no migration, guest, storage, network, Gitea, backup, or\n  runtime gate advances",
            "protected runtime\n   commissioning remains separately gated",
        ):
            self.assertIn(marker, self.contract)


if __name__ == "__main__":
    unittest.main()
