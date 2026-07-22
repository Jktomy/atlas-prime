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
EVENT = "MISSION-BOARD-QUEST-REGISTRY-CUTOVER-R01"


def load(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


class MissionBoardQuestRegistryCutoverTests(unittest.TestCase):
    def setUp(self) -> None:
        self.board = load("quest-board/quest-board-v1.json")
        self.registry = load("continuity/mission-board-quest-registry-r01.json")
        self.continuity = load("continuity/prime-continuity-register-r01.json")

    def test_atomic_registry_authority_and_parent_identity_are_exact(self) -> None:
        validate_board(self.board)
        validate_quest_registry(self.registry, self.board)
        validate_register(self.continuity, self.board, registry=self.registry)

        self.assertEqual(self.board["registry_role"], "FROZEN_PREDECESSOR_EVIDENCE")
        self.assertEqual(self.board["frozen_by_issue"], 278)
        self.assertEqual(
            self.board["successor_registry"],
            "continuity/mission-board-quest-registry-r01.json",
        )
        self.assertEqual(self.registry["authority"], "CANONICAL_ADMITTED_QUEST_REGISTRY")
        self.assertEqual(self.registry["cutover"]["issue_number"], 278)
        self.assertEqual(self.registry["cutover"]["predecessor_sha256"], sha256(self.board))
        self.assertFalse(self.registry["live_issue_availability_required_for_recovery"])

        parents = {
            item["quest_id"]: (
                item["parent_issue_number"],
                item["parent_mission_id"],
                item["parent_attempt_id"],
            )
            for item in self.registry["entries"]
        }
        self.assertEqual(
            parents,
            {
                "QUEST-PRIME-ASCENDANT-20260717": (
                    307,
                    "MISSION-QUEST-PARENT-PRIME-ASCENDANT-R01",
                    "MISSION-QUEST-PARENT-PRIME-ASCENDANT-R01-ATTEMPT-01",
                ),
                "QUEST-PROMETHEUS-FIRE-20260701": (
                    308,
                    "MISSION-QUEST-PARENT-PROMETHEUS-FIRE-R01",
                    "MISSION-QUEST-PARENT-PROMETHEUS-FIRE-R01-ATTEMPT-01",
                ),
                "QUEST-NOTUMS-WATCH-20260708": (
                    309,
                    "MISSION-QUEST-PARENT-NOTUMS-WATCH-R01",
                    "MISSION-QUEST-PARENT-NOTUMS-WATCH-R01-ATTEMPT-01",
                ),
            },
        )
        self.assertEqual(
            {item["parent_mission_state"] for item in self.registry["entries"]},
            {"IN_PROGRESS"},
        )
        self.assertEqual(
            {item["parent_source_status"] for item in self.registry["entries"]},
            {"NO_SOURCE_CHANGE_REQUIRED"},
        )

    def test_frozen_board_and_active_registry_have_exact_cutover_parity(self) -> None:
        frozen_active = {
            item["quest_id"]: item
            for item in self.board["entries"]
            if item["state"] != "COMPLETE"
        }
        active = {item["quest_id"]: item for item in self.registry["entries"]}
        self.assertEqual(set(frozen_active), set(active))
        for quest_id, entry in active.items():
            predecessor = frozen_active[quest_id]
            for field in (
                "quest_id",
                "source",
                "owner",
                "state",
                "next_gate",
                "readiness_basis",
            ):
                with self.subTest(quest_id=quest_id, field=field):
                    self.assertEqual(entry[field], predecessor[field])
        self.assertEqual(
            sum(item["state"] == "COMPLETE" for item in self.board["entries"]),
            self.registry["cutover"]["baseline_completed_quest_count"],
        )

    def test_continuity_is_bound_only_to_active_registry_and_preserves_history(self) -> None:
        self.assertEqual(self.continuity["register_revision"], 52)
        self.assertEqual(self.continuity["quest_board_sha256"], sha256(self.board))
        self.assertEqual(self.continuity["quest_registry_sha256"], sha256(self.registry))
        self.assertEqual(self.continuity["event_ids"].count(EVENT), 1)
        self.assertEqual(
            {item["quest_id"] for item in self.continuity["entries"]},
            {item["quest_id"] for item in self.registry["entries"]},
        )
        self.assertIn("RP-C05-AJ08-ADMISSION-R01", self.continuity["event_ids"])
        self.assertIn("FOUND-SILVERLIGHT-DECOMPOSITION-SUNSET-R01", self.continuity["event_ids"])
        self.assertIn("PRIME-CONTINUITY-PROOF-CLOSEOUT-R01", self.continuity["event_ids"])

    def test_startup_routing_recovery_and_contracts_have_one_authority_model(self) -> None:
        surfaces = {
            "README": (ROOT / "README.md").read_text(encoding="utf-8"),
            "bootstrap": (ROOT / "bootstrap.md").read_text(encoding="utf-8"),
            "start": (ROOT / "atlas-start-here.md").read_text(encoding="utf-8"),
            "routing": (ROOT / "routing/command-surfaces.md").read_text(encoding="utf-8"),
            "operations": (ROOT / "operations/operation-registry.md").read_text(encoding="utf-8"),
            "mission": (ROOT / "governance/mission-board-contract.md").read_text(encoding="utf-8"),
            "portfolio": (ROOT / "governance/atlas-quest-portfolio-contract.md").read_text(encoding="utf-8"),
            "continuity": (ROOT / "governance/quest-engine-continuity-contract.md").read_text(encoding="utf-8"),
            "recovery": (ROOT / "recovery/elantris-recovery.md").read_text(encoding="utf-8"),
            "tool": (ROOT / "tools/prime_continuity/README.md").read_text(encoding="utf-8"),
        }
        joined = "\n".join(surfaces.values())
        for marker in (
            "continuity/mission-board-quest-registry-r01.json",
            "FROZEN_PREDECESSOR_EVIDENCE",
            "MISSION-QUEST-PARENT-PRIME-ASCENDANT-R01",
            "MISSION-QUEST-PARENT-PROMETHEUS-FIRE-R01",
            "MISSION-QUEST-PARENT-NOTUMS-WATCH-R01",
            "QUEST_BOARD_FROZEN",
            "live Issue availability is not required",
            "no split-brain",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker.casefold(), joined.casefold())
        self.assertIn("Mission Board: PRIMARY_OPERATIONAL_SURFACE", surfaces["README"])
        self.assertIn("Quest Board: FROZEN PREDECESSOR EVIDENCE", surfaces["README"])
        self.assertIn("cannot admit, advance, or resume work", surfaces["recovery"])
        self.assertNotIn("Prime Continuity Proof remains independent", surfaces["recovery"])

    def test_new_schema_and_required_program_paths_exist(self) -> None:
        required = (
            "schemas/mission-board-quest-registry-v1.schema.json",
            "continuity/mission-board-quest-registry-r01.json",
            "quest-board/quest-board-v1.json",
            "continuity/prime-continuity-register-r01.json",
            "tools/prime_continuity/engine.py",
            "tools/prime_continuity/cli.py",
        )
        self.assertEqual([path for path in required if not (ROOT / path).is_file()], [])


if __name__ == "__main__":
    unittest.main()
