from __future__ import annotations

import json
import unittest
from copy import deepcopy
from pathlib import Path

from tools.mission_board.core import MissionError, changed_paths_digest
from tools.mission_board.quest_sync import (
    affected_parent_quests,
    build_quest_sync_receipt,
    enforce_quest_sync_closure,
    receipt_markdown,
    validate_quest_sync_receipt,
)


ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "tests" / "prime-program" / "fixtures" / "mission-board"


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_mission() -> dict[str, object]:
    mission = load_json(FIXTURES / "canonical-implementation.json")
    mission["issue_number"] = 315
    mission["mission_id"] = "MISSION-315-QUEST-SYNC-ENFORCEMENT-R01"
    mission["attempt_id"] = "MISSION-315-QUEST-SYNC-ENFORCEMENT-R01-ATTEMPT-01"
    mission["relationships"] = {"quest": None, "campaign": None, "gate": None}
    mission["source_binding"]["changed_paths"] = [
        "continuity/mission-board-quest-registry-r01.json",
        "continuity/prime-continuity-register-r01.json",
        "quests/the-odyssey.md",
        "tests/prime-program/test_mission_quest_sync.py",
        "tools/mission_board/quest_sync.py",
    ]
    mission["source_binding"]["changed_paths_digest"] = changed_paths_digest(
        mission["source_binding"]["changed_paths"]
    )
    return mission


class MissionQuestSyncTests(unittest.TestCase):
    def setUp(self) -> None:
        self.registry = load_json(
            ROOT / "continuity" / "mission-board-quest-registry-r01.json"
        )
        self.mission = canonical_mission()
        self.canonical_head = self.mission["source_binding"]["merged_commit"]

    def test_global_mission_board_doctrine_requires_odyssey_parent_receipt(self) -> None:
        affected = affected_parent_quests(self.mission, self.registry)
        self.assertEqual(
            [entry["parent_issue_number"] for entry in affected],
            [359],
        )
        self.assertEqual(
            [entry["quest_id"] for entry in affected],
            ["QUEST-THE-ODYSSEY-20260727"],
        )

    def test_missing_parent_receipt_blocks_closure_with_exact_code(self) -> None:
        with self.assertRaisesRegex(MissionError, "QUEST_SYNC_PENDING"):
            enforce_quest_sync_closure(
                self.mission,
                self.registry,
                {},
                canonical_head=self.canonical_head,
            )

    def test_exact_odyssey_receipt_allows_closure(self) -> None:
        entry = affected_parent_quests(self.mission, self.registry)[0]
        receipt = build_quest_sync_receipt(
            self.mission,
            entry,
            canonical_head=self.canonical_head,
            impact_summary=(
                "Mission #315 updates shared Quest doctrine and synchronizes "
                "the single active Odyssey parent without advancing its gate."
            ),
        )
        self.assertEqual(
            validate_quest_sync_receipt(receipt)["receipt_id"],
            receipt["receipt_id"],
        )
        snapshots = {
            359: {
                "number": 359,
                "is_pull_request": False,
                "body": "",
                "comments": [{"body": receipt_markdown(receipt)}],
            }
        }
        result = enforce_quest_sync_closure(
            self.mission,
            self.registry,
            snapshots,
            canonical_head=self.canonical_head,
        )
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["required_parent_issues"], [359])
        self.assertEqual(len(result["confirmed_receipts"]), 1)

    def test_duplicate_exact_receipt_fails_closed(self) -> None:
        entry = affected_parent_quests(self.mission, self.registry)[0]
        receipt = build_quest_sync_receipt(
            self.mission,
            entry,
            canonical_head=self.canonical_head,
            impact_summary="Exact merged-main synchronization receipt.",
        )
        block = receipt_markdown(receipt)
        snapshots = {
            359: {
                "number": 359,
                "is_pull_request": False,
                "body": "",
                "comments": [{"body": block}, {"body": block}],
            }
        }
        with self.assertRaisesRegex(MissionError, "QUEST_SYNC_DUPLICATE"):
            enforce_quest_sync_closure(
                self.mission,
                self.registry,
                snapshots,
                canonical_head=self.canonical_head,
            )

    def test_stale_or_unread_canonical_head_cannot_issue_receipt(self) -> None:
        entry = affected_parent_quests(self.mission, self.registry)[0]
        with self.assertRaisesRegex(MissionError, "QUEST_SYNC_READBACK_REQUIRED"):
            build_quest_sync_receipt(
                self.mission,
                entry,
                canonical_head="4" * 40,
                impact_summary="Stale evidence must be rejected.",
            )

    def test_nonquest_lifecycle_only_candidate_does_not_invent_quest_sync(self) -> None:
        mission = deepcopy(self.mission)
        mission["mission_type"] = "mission/sunset"
        mission["source_binding"]["changed_paths"] = [
            "lifecycle/feathers/FTR-AAAAAAAAAAAAAAAAAAAAAAAAAA.json",
            "lifecycle/sunrises/SRI-AAAAAAAAAAAAAAAAAAAAAAAAAA.json",
            "lifecycle/sunsets/SUN-AAAAAAAAAAAAAAAAAAAAAAAAAA.json",
        ]
        mission["source_binding"]["changed_paths_digest"] = changed_paths_digest(
            mission["source_binding"]["changed_paths"]
        )
        mission["sunset"] = {
            "conversation_summary": "Synthetic non-Quest lifecycle fixture.",
            "exact_unfinished_work": [],
            "blockers": [],
            "lesson_harvest_dispositions": ["LOCAL_ONLY"],
            "golden_wing_candidate_disposition": "No candidate.",
            "record_plan": "One Feather, Sunset, and Sunrise.",
            "phoenix_processing_pending": False,
            "archival_status": "NOT_APPLICABLE",
            "truth_state": "SUNSET COMPLETE",
        }
        self.assertEqual(
            affected_parent_quests(mission, self.registry),
            [],
        )
        result = enforce_quest_sync_closure(
            mission,
            self.registry,
            {},
            canonical_head=self.canonical_head,
        )
        self.assertEqual(result["status"], "NOT_REQUIRED")


if __name__ == "__main__":
    unittest.main()
