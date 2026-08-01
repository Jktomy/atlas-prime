from __future__ import annotations

import json
import unittest
from pathlib import Path

from tools.prime_continuity.engine import (
    sha256,
    validate_board,
    validate_quest_registry,
    validate_register,
)

ROOT = Path(__file__).resolve().parents[2]
MISSION_278_EVENT = "MISSION-BOARD-QUEST-REGISTRY-CUTOVER-R01"
ODYSSEY_ADMISSION_EVENT = "ODYSSEY-QUEST-ADMISSION-AND-SUPERSESSION-R01"
ODYSSEY_RECONCILIATION_EVENT = "ODYSSEY-CANON-RECONCILIATION-R01"
ODYSSEY_ID = "QUEST-THE-ODYSSEY-20260727"

def load(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))

class MissionBoardQuestRegistryCutoverTests(unittest.TestCase):
    def setUp(self) -> None:
        self.board = load("quest-board/quest-board-v1.json")
        self.registry = load("continuity/mission-board-quest-registry-r01.json")
        self.continuity = load("continuity/prime-continuity-register-r01.json")

    def test_frozen_mission_278_baseline_is_preserved(self) -> None:
        validate_board(self.board)
        self.assertEqual(self.board["registry_role"], "FROZEN_PREDECESSOR_EVIDENCE")
        self.assertEqual(self.board["frozen_by_issue"], 278)
        frozen_active = {
            item["quest_id"]
            for item in self.board["entries"]
            if item["state"] != "COMPLETE"
        }
        self.assertEqual(
            frozen_active,
            {
                "QUEST-PRIME-ASCENDANT-20260717",
                "QUEST-PROMETHEUS-FIRE-20260701",
                "QUEST-NOTUMS-WATCH-20260708",
            },
        )
        self.assertEqual(
            self.registry["cutover"]["predecessor_sha256"],
            sha256(self.board),
        )

    def test_odyssey_is_the_only_active_registry_parent(self) -> None:
        validate_quest_registry(self.registry, self.board)
        self.assertEqual(self.registry["registry_revision"], 5)
        self.assertEqual(len(self.registry["entries"]), 1)
        entry = self.registry["entries"][0]
        self.assertEqual(entry["quest_id"], ODYSSEY_ID)
        self.assertEqual(entry["parent_issue_number"], 359)
        self.assertEqual(entry["parent_issue_label"], "mission/quest")
        self.assertIn("Mission #358", entry["readiness_basis"])

    def test_continuity_is_bound_to_current_reconciliation(self) -> None:
        validate_register(self.continuity, self.board, registry=self.registry)
        self.assertEqual(
            self.continuity["quest_registry_sha256"],
            sha256(self.registry),
        )
        self.assertEqual(self.continuity["register_revision"], 58)
        entry = self.continuity["entries"][0]
        self.assertEqual(entry["revision"], 2)
        self.assertEqual(entry["gate_id"], "OD-C02-PREVIEW")
        self.assertEqual(entry["last_event_id"], ODYSSEY_RECONCILIATION_EVENT)
        self.assertIn("Mission #364", entry["current_position"])
        self.assertEqual(self.continuity["event_ids"].count(MISSION_278_EVENT), 1)
        self.assertEqual(self.continuity["event_ids"].count(ODYSSEY_ADMISSION_EVENT), 1)
        self.assertEqual(self.continuity["event_ids"].count(ODYSSEY_RECONCILIATION_EVENT), 1)

    def test_startup_and_routing_preserve_authority_split(self) -> None:
        surfaces = {
            "readme": (ROOT / "README.md").read_text(encoding="utf-8"),
            "start": (ROOT / "atlas-start-here.md").read_text(encoding="utf-8"),
            "quest": (ROOT / "quests/the-odyssey.md").read_text(encoding="utf-8"),
            "architecture": (
                ROOT / "governance/odyssey-hermes-native-architecture-contract.md"
            ).read_text(encoding="utf-8"),
            "portfolio": (
                ROOT / "governance/atlas-quest-portfolio-contract.md"
            ).read_text(encoding="utf-8"),
        }
        joined = "\n".join(surfaces.values())
        for marker in (
            "Issue #359",
            "Mission #358",
            "Mission #364",
            "QUEST-THE-ODYSSEY-20260727",
            "OD-C02-PREVIEW",
            "preserved superseded history",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker.casefold(), joined.casefold())
        self.assertIn(
            "14. `governance/odyssey-hermes-native-architecture-contract.md`",
            surfaces["start"],
        )

    def test_mission_278_and_predecessor_lineage_remain_historical(self) -> None:
        portfolio = (
            ROOT / "governance/atlas-quest-portfolio-contract.md"
        ).read_text(encoding="utf-8")
        for marker in (
            "| Prime Ascendant | #307 |",
            "| Prometheus's Fire | #308 |",
            "| Notum's Watch | #309 |",
            "| The Odyssey | #359 |",
        ):
            self.assertIn(marker, portfolio)
        self.assertIn("Mission #278", portfolio)

    def test_required_program_paths_exist(self) -> None:
        required = (
            "schemas/mission-board-quest-registry-v1.schema.json",
            "continuity/mission-board-quest-registry-r01.json",
            "continuity/prime-continuity-register-r01.json",
            "quest-board/quest-board-v1.json",
            "quests/the-odyssey.md",
            "governance/atlas-autonomy-and-adaptation-contract.md",
            "governance/odyssey-hermes-native-architecture-contract.md",
            "tools/prime_continuity/engine.py",
        )
        self.assertEqual([path for path in required if not (ROOT / path).is_file()], [])

if __name__ == "__main__":
    unittest.main()
