from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from tools.prime_continuity.engine import (
    ContinuityError,
    render_mission_quest_emberline,
    validate_quest_registry,
)


ROOT = Path(__file__).resolve().parents[2]
ODYSSEY_ID = "QUEST-THE-ODYSSEY-20260727"


def load(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


class MissionQuestEmberlineIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.board = load("quest-board/quest-board-v1.json")
        self.registry = load(
            "continuity/mission-board-quest-registry-r01.json"
        )
        self.register = load(
            "continuity/prime-continuity-register-r01.json"
        )

    def test_each_active_quest_has_one_label_and_stable_human_emberline(self) -> None:
        self.assertEqual(
            {
                entry["parent_issue_label"]
                for entry in self.registry["entries"]
            },
            {"mission/quest"},
        )
        self.assertEqual(
            len(
                {
                    entry["emberline_id"]
                    for entry in self.registry["entries"]
                }
            ),
            len(self.registry["entries"]),
        )
        self.assertEqual(len(self.registry["entries"]), 1)
        for entry in self.registry["entries"]:
            rendered = render_mission_quest_emberline(
                self.register,
                self.registry,
                entry["quest_id"],
            )
            self.assertEqual(
                rendered["emberline_id"],
                entry["emberline_id"],
            )
            self.assertEqual(
                rendered["required_label"],
                "mission/quest",
            )
            self.assertIn(
                "Living Emberline",
                rendered["markdown"],
            )
            self.assertIn(
                "Merged registry and continuity remain authoritative",
                rendered["markdown"],
            )

    def test_emberline_id_is_stably_derived_from_parent_mission_identity(self) -> None:
        entry = self.registry["entries"][0]
        self.assertEqual(
            entry["emberline_id"],
            entry["parent_mission_id"].replace(
                "MISSION-QUEST-PARENT-",
                "EMBERLINE-QUEST-",
                1,
            ),
        )

        tampered = copy.deepcopy(self.registry)
        tampered["entries"][0]["emberline_id"] = (
            "EMBERLINE-QUEST-REPLACED-R01"
        )
        with self.assertRaisesRegex(
            ContinuityError,
            "MISSION_QUEST_EMBERLINE_ID_MISMATCH",
        ):
            validate_quest_registry(tampered, self.board)

    def test_renderer_rejects_stale_or_duplicate_registry_binding(self) -> None:
        stale = copy.deepcopy(self.register)
        stale["quest_registry_sha256"] = "0" * 64
        with self.assertRaisesRegex(
            ContinuityError,
            "QUEST_REGISTRY_DIGEST_MISMATCH",
        ):
            render_mission_quest_emberline(
                stale,
                self.registry,
                ODYSSEY_ID,
            )

        duplicate = copy.deepcopy(self.registry)
        duplicate_entry = copy.deepcopy(duplicate["entries"][0])
        duplicate_entry["quest_id"] = "QUEST-DUPLICATE-ODYSSEY-R01"
        duplicate_entry["source"] = "quests/the-odyssey.md"
        duplicate_entry["parent_issue_number"] = 999
        duplicate_entry["parent_mission_id"] = (
            "MISSION-QUEST-PARENT-DUPLICATE-ODYSSEY-R01"
        )
        duplicate_entry["parent_attempt_id"] = (
            "MISSION-QUEST-PARENT-DUPLICATE-ODYSSEY-R01-ATTEMPT-01"
        )
        duplicate_entry["emberline_id"] = (
            duplicate["entries"][0]["emberline_id"]
        )
        duplicate["entries"].append(duplicate_entry)
        with self.assertRaisesRegex(
            ContinuityError,
            "QUEST_REGISTRY_DUPLICATE",
        ):
            render_mission_quest_emberline(
                self.register,
                duplicate,
                ODYSSEY_ID,
            )

    def test_later_reviewed_registry_revision_may_change_odyssey_position(self) -> None:
        candidate = copy.deepcopy(self.registry)
        candidate["registry_revision"] += 1
        candidate["entries"][0]["state"] = "BLOCKED"
        candidate["entries"][0]["next_gate"] = (
            "OD-C02 blocked pending exact Mission proof"
        )
        candidate["entries"][0]["readiness_basis"] = (
            "A later reviewed lifecycle revision may change current Odyssey "
            "position without rewriting the immutable Mission #278 baseline."
        )
        validate_quest_registry(candidate, self.board)


if __name__ == "__main__":
    unittest.main()
