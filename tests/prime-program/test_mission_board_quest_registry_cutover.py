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
ODYSSEY_EVENT = "ODYSSEY-QUEST-ADMISSION-AND-SUPERSESSION-R01"
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
        self.assertEqual(
            self.board["successor_registry"],
            "continuity/mission-board-quest-registry-r01.json",
        )
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
        self.assertEqual(
            set(self.registry["cutover"]["baseline_active_quest_ids"]),
            frozen_active,
        )

    def test_odyssey_is_the_only_active_registry_parent(self) -> None:
        validate_quest_registry(self.registry, self.board)
        self.assertEqual(self.registry["authority"], "CANONICAL_ADMITTED_QUEST_REGISTRY")
        self.assertEqual(self.registry["registry_revision"], 5)
        self.assertFalse(self.registry["live_issue_availability_required_for_recovery"])
        self.assertEqual(len(self.registry["entries"]), 1)
        entry = self.registry["entries"][0]
        self.assertEqual(entry["quest_id"], ODYSSEY_ID)
        self.assertEqual(entry["source"], "quests/the-odyssey.md")
        self.assertEqual(entry["parent_issue_number"], 359)
        self.assertEqual(
            entry["parent_mission_id"],
            "MISSION-QUEST-PARENT-THE-ODYSSEY-R01",
        )
        self.assertEqual(
            entry["parent_attempt_id"],
            "MISSION-QUEST-PARENT-THE-ODYSSEY-R01-ATTEMPT-01",
        )
        self.assertEqual(entry["parent_issue_label"], "mission/quest")
        self.assertEqual(
            entry["emberline_id"],
            "EMBERLINE-QUEST-THE-ODYSSEY-R01",
        )
        self.assertEqual(entry["state"], "IN_PROGRESS")

    def test_continuity_is_bound_only_to_odyssey(self) -> None:
        validate_register(
            self.continuity,
            self.board,
            registry=self.registry,
        )
        self.assertEqual(
            self.continuity["quest_registry_sha256"],
            sha256(self.registry),
        )
        self.assertEqual(
            {item["quest_id"] for item in self.continuity["entries"]},
            {ODYSSEY_ID},
        )
        entry = self.continuity["entries"][0]
        self.assertEqual(entry["continuity_id"], "CONT-THE-ODYSSEY-R01")
        self.assertEqual(entry["campaign_id"], "OD-C02")
        self.assertEqual(entry["gate_id"], "OD-C02-PREVIEW")
        self.assertEqual(entry["last_event_id"], ODYSSEY_EVENT)
        self.assertEqual(self.continuity["event_ids"].count(MISSION_278_EVENT), 1)
        self.assertEqual(self.continuity["event_ids"].count(ODYSSEY_EVENT), 1)

    def test_startup_and_routing_point_to_the_living_odyssey_parent(self) -> None:
        surfaces = {
            "start": (ROOT / "atlas-start-here.md").read_text(encoding="utf-8"),
            "routing": (ROOT / "routing/command-surfaces.md").read_text(encoding="utf-8"),
            "quest": (ROOT / "quests/the-odyssey.md").read_text(encoding="utf-8"),
            "portfolio": (ROOT / "governance/atlas-quest-portfolio-contract.md").read_text(encoding="utf-8"),
            "mission_board": (ROOT / "governance/mission-board-contract.md").read_text(encoding="utf-8"),
            "recovery": (ROOT / "recovery/elantris-recovery.md").read_text(encoding="utf-8"),
        }
        joined = "\n".join(surfaces.values())
        for marker in (
            "Issue #359",
            "Mission #358",
            "QUEST-THE-ODYSSEY-20260727",
            "OD-C02",
            "preserved superseded history",
            "quest-board/quest-board-v1.json",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker.casefold(), joined.casefold())
        self.assertIn(
            "12. `quests/the-odyssey.md`",
            surfaces["start"],
        )
        self.assertIn("prior parents #307–#309", surfaces["routing"])
        self.assertIn("| The Odyssey | #359 |", surfaces["portfolio"])
        self.assertIn("| The Odyssey | #359 |", surfaces["mission_board"])
        self.assertIn("The active portfolio is The Odyssey (#359)", surfaces["recovery"])

    def test_mission_278_and_predecessor_lineage_remain_historical(self) -> None:
        portfolio = (ROOT / "governance/atlas-quest-portfolio-contract.md").read_text(encoding="utf-8")
        mission_board = (ROOT / "governance/mission-board-contract.md").read_text(encoding="utf-8")
        continuity_contract = (
            ROOT / "governance/quest-engine-continuity-contract.md"
        ).read_text(encoding="utf-8")
        for marker in (
            "| Prime Ascendant | #307 |",
            "| Prometheus's Fire | #308 |",
            "| Notum's Watch | #309 |",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, portfolio)
                self.assertIn(marker, mission_board)
        self.assertIn("Mission #278", portfolio)
        self.assertIn("Mission #278", mission_board)
        self.assertIn("Mission #278", continuity_contract)
        self.assertIn("many-to-one recomposition", continuity_contract.casefold())

    def test_required_program_paths_exist(self) -> None:
        required = (
            "schemas/mission-board-quest-registry-v1.schema.json",
            "continuity/mission-board-quest-registry-r01.json",
            "continuity/prime-continuity-register-r01.json",
            "quest-board/quest-board-v1.json",
            "quests/the-odyssey.md",
            "quests/prime-ascendant.md",
            "quests/prometheus-fire.md",
            "quests/notums-watch.md",
            "tools/prime_continuity/engine.py",
        )
        self.assertEqual(
            [path for path in required if not (ROOT / path).is_file()],
            [],
        )


if __name__ == "__main__":
    unittest.main()
