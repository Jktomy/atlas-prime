from __future__ import annotations

import json
import unittest
from copy import deepcopy
from pathlib import Path

from tools.mission_board.core import (
    CANONICAL_SOURCE_STATES,
    DEPENDENCY_RELATIONS,
    MISSION_STATE_SET,
    MISSION_TYPES,
    MissionError,
    assert_no_duplicate,
    changed_paths_digest,
    extract_manifest,
    parse_json_document,
    reconcile_issue_snapshot,
    resume_plan,
    sequence_missions,
    validate_mission,
    validate_source_transition,
    validate_transition,
)


ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "tests" / "prime-program" / "fixtures" / "mission-board"


def load(name: str) -> dict[str, object]:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


class MissionBoardTests(unittest.TestCase):
    def test_contract_template_schema_and_tool_are_routed(self) -> None:
        required = (
            ".github/ISSUE_TEMPLATE/mission.md",
            "governance/mission-board-contract.md",
            "schemas/mission-v1.schema.json",
            "tools/mission_board/README.md",
            "tools/mission_board/__init__.py",
            "tools/mission_board/__main__.py",
            "tools/mission_board/core.py",
        )
        self.assertEqual([path for path in required if not (ROOT / path).is_file()], [])
        routed = (ROOT / "routing" / "command-surfaces.md").read_text(encoding="utf-8")
        tool_route = (ROOT / "tools/mission_board/README.md").read_text(encoding="utf-8")
        for path in required:
            with self.subTest(path=path):
                self.assertIn(path, routed + tool_route)

    def test_schema_enums_match_runtime(self) -> None:
        schema = json.loads((ROOT / "schemas" / "mission-v1.schema.json").read_text(encoding="utf-8"))
        properties = schema["properties"]
        self.assertEqual(set(properties["mission_type"]["enum"]), set(MISSION_TYPES))
        self.assertEqual(set(properties["mission_state"]["enum"]), set(MISSION_STATE_SET))
        self.assertEqual(set(properties["canonical_source_status"]["enum"]), set(CANONICAL_SOURCE_STATES))
        dependency_enum = properties["dependencies"]["items"]["properties"]["relation"]["enum"]
        self.assertEqual(set(dependency_enum), set(DEPENDENCY_RELATIONS))

    def test_all_public_clean_fixtures_validate(self) -> None:
        names = (
            "captured-sunset.json",
            "canonical-implementation.json",
            "blocked-resumable.json",
            "sequence-5.json",
            "sequence-7.json",
            "sequence-12.json",
        )
        for name in names:
            with self.subTest(name=name):
                self.assertEqual(validate_mission(load(name))["schema_version"], "atlas.mission.v1")

    def test_template_uses_truthful_post_creation_identity_binding(self) -> None:
        template = (ROOT / ".github" / "ISSUE_TEMPLATE" / "mission.md").read_text(encoding="utf-8")
        self.assertIn("```atlas-mission-draft-v1", template)
        self.assertIn('"issue_number": 0', template)
        with self.assertRaisesRegex(MissionError, "MANIFEST_CARDINALITY"):
            extract_manifest(template)
        self.assertNotIn("projects", template.casefold())

    def test_comment_history_rejects_backdated_state_claim(self) -> None:
        body = load("captured-sunset.json")
        body["updated_at"] = "2026-07-21T14:02:00Z"
        comment = deepcopy(body)
        comment["mission_state"] = "TRIAGED"
        comment["updated_at"] = "2026-07-21T14:01:00Z"
        snapshot = {
            "repository": "Jktomy/atlas-prime",
            "number": 259,
            "is_pull_request": False,
            "body": "```atlas-mission-v1\n" + json.dumps(body) + "\n```",
            "comments": [{"body": "```atlas-mission-v1\n" + json.dumps(comment) + "\n```"}],
        }
        with self.assertRaisesRegex(MissionError, "STALE_MISSION_CLAIM"):
            reconcile_issue_snapshot(snapshot, "Jktomy/atlas-prime", 259)

    def test_sequential_5_7_12_order_and_nonblocking_resume(self) -> None:
        missions = {5: load("sequence-5.json"), 7: load("sequence-7.json"), 12: load("sequence-12.json")}
        receipt = sequence_missions(missions, [5, 7, 12])
        self.assertEqual(receipt["requested_order"], [5, 7, 12])
        self.assertEqual([item["result"] for item in receipt["results"]], ["COMPLETE", "BLOCKED_RESUMABLE", "COMPLETE"])
        self.assertFalse(receipt["stopped"])

    def test_sequential_queue_stops_when_block_is_terminal(self) -> None:
        blocked = load("sequence-7.json")
        blocked["queue_behavior"] = "TERMINAL_ON_BLOCK"
        missions = {5: load("sequence-5.json"), 7: blocked, 12: load("sequence-12.json")}
        receipt = sequence_missions(missions, [5, 7, 12])
        self.assertEqual([item["result"] for item in receipt["results"]], ["COMPLETE", "BLOCKED_RESUMABLE", "NOT_STARTED_AFTER_STOP"])
        self.assertTrue(receipt["stopped"])

    def test_sequential_queue_does_not_validate_items_after_stop(self) -> None:
        blocked = load("sequence-7.json")
        blocked["queue_behavior"] = "TERMINAL_ON_BLOCK"
        malformed_later = load("sequence-12.json")
        malformed_later["issue_number"] = True
        missions = {5: load("sequence-5.json"), 7: blocked, 12: malformed_later}
        receipt = sequence_missions(missions, [5, 7, 12])
        self.assertEqual([item["result"] for item in receipt["results"]], ["COMPLETE", "BLOCKED_RESUMABLE", "NOT_STARTED_AFTER_STOP"])

    def test_live_pull_request_objects_are_not_missions(self) -> None:
        snapshot = {
            "repository": "Jktomy/atlas-prime",
            "number": 5,
            "is_pull_request": True,
            "body": "",
            "comments": [],
        }
        with self.assertRaisesRegex(MissionError, "IDENTITY_MISMATCH.*pull request"):
            reconcile_issue_snapshot(snapshot, "Jktomy/atlas-prime", 5)

    def test_resume_rejects_stale_pending_base(self) -> None:
        mission = load("blocked-resumable.json")
        mission["source_binding"]["base_sha"] = "1" * 40
        with self.assertRaisesRegex(MissionError, "STALE_MISSION_CLAIM"):
            resume_plan(mission, "2" * 40)

    def test_resume_requires_exact_pr_readback(self) -> None:
        mission = load("canonical-implementation.json")
        mission["canonical_source_status"] = "PR_OPEN"
        mission["mission_state"] = "PR_OPEN"
        mission["source_binding"]["merged_commit"] = None
        with self.assertRaisesRegex(MissionError, "PR_READBACK_REQUIRED"):
            resume_plan(mission, "1" * 40)
        plan = resume_plan(
            mission,
            "1" * 40,
            pr_snapshot={"number": 260, "head_sha": "2" * 40, "branch": "codex/mission-board-foundation-r01"},
        )
        self.assertEqual(plan["last_proven_state"], "PR_OPEN")
        with self.assertRaisesRegex(MissionError, "pr_snapshot must be an object"):
            resume_plan(mission, "1" * 40, pr_snapshot=[])

    def test_changed_path_digest_is_sorted_and_exact(self) -> None:
        self.assertEqual(
            changed_paths_digest(["governance/mission-board-contract.md"]),
            "6120ee16bde780482c63f50e7d58805374842380c76c8f76fbc1d99206dd6964",
        )
        mission = load("canonical-implementation.json")
        mission["source_binding"]["changed_paths_digest"] = "0" * 64
        with self.assertRaisesRegex(MissionError, "PATH_DIGEST_MISMATCH"):
            validate_mission(mission)

    def test_duplicate_attempt_is_rejected(self) -> None:
        mission = load("blocked-resumable.json")
        with self.assertRaisesRegex(MissionError, "REPLAY"):
            assert_no_duplicate(mission, [deepcopy(mission)])

    def test_conflicting_attempt_binding_is_rejected(self) -> None:
        mission = load("blocked-resumable.json")
        conflicting = deepcopy(mission)
        conflicting["issue_number"] = 256
        with self.assertRaisesRegex(MissionError, "CONFLICTING_BINDING"):
            assert_no_duplicate(mission, [conflicting])

    def test_cross_mission_pr_binding_reuse_is_rejected(self) -> None:
        mission = load("canonical-implementation.json")
        conflicting = deepcopy(mission)
        conflicting["mission_id"] = "DIFFERENT-MISSION-R01"
        conflicting["issue_number"] = 260
        conflicting["attempt_id"] = "DIFFERENT-MISSION-ATTEMPT-01"
        with self.assertRaisesRegex(MissionError, "CONFLICTING_BINDING.*branch"):
            assert_no_duplicate(mission, [conflicting])

    def test_false_sunset_completion_is_rejected(self) -> None:
        mission = load("captured-sunset.json")
        mission["sunset"]["truth_state"] = "SUNSET COMPLETE"
        with self.assertRaisesRegex(MissionError, "FALSE_COMPLETION"):
            validate_mission(mission)

    def test_closed_issue_state_requires_source_and_proof(self) -> None:
        mission = load("sequence-5.json")
        mission["canonical_source_status"] = "PHOENIX_PENDING"
        with self.assertRaisesRegex(MissionError, "FALSE_COMPLETION"):
            validate_mission(mission)

    def test_boolean_issue_and_pr_numbers_fail_closed(self) -> None:
        mission = load("blocked-resumable.json")
        mission["issue_number"] = True
        with self.assertRaisesRegex(MissionError, "ISSUE_IDENTITY"):
            validate_mission(mission)
        mission = load("canonical-implementation.json")
        mission["source_binding"]["pull_request"] = True
        with self.assertRaisesRegex(MissionError, "source_binding.pull_request"):
            validate_mission(mission)

    def test_pending_coppermind_cannot_claim_archive_timestamp(self) -> None:
        mission = load("blocked-resumable.json")
        mission["coppermind"]["archive_timestamp"] = "2026-07-21T14:00:00Z"
        with self.assertRaisesRegex(MissionError, "ARCHIVE_STATE_MISMATCH"):
            validate_mission(mission)

    def test_canonical_state_requires_canonical_source_readback(self) -> None:
        mission = load("blocked-resumable.json")
        mission["mission_state"] = "CANONICAL"
        with self.assertRaisesRegex(MissionError, "FALSE_COMPLETION"):
            validate_mission(mission)
        mission = load("sequence-5.json")
        mission["completion_proof"] = []
        with self.assertRaisesRegex(MissionError, "FALSE_COMPLETION"):
            validate_mission(mission)

    def test_archived_state_requires_real_reference(self) -> None:
        mission = load("canonical-implementation.json")
        mission["mission_state"] = "COPPERMIND_ARCHIVED"
        with self.assertRaisesRegex(MissionError, "ARCHIVE_STATE_MISMATCH"):
            validate_mission(mission)

    def test_protected_patterns_fail_closed(self) -> None:
        mission = load("blocked-resumable.json")
        mission["objective"] = "Connect to 10.20.30.40"
        with self.assertRaisesRegex(MissionError, "PROTECTED_BOUNDARY_FAILURE"):
            validate_mission(mission)

    def test_protected_pointer_uses_closed_schema_grammar(self) -> None:
        mission = load("blocked-resumable.json")
        mission["public_clean_boundary"]["protected_pointer"] = "protected://approved/evidence-01"
        validate_mission(mission)
        mission["public_clean_boundary"]["protected_pointer"] = "protected://approved/evidence-01\nraw note"
        with self.assertRaisesRegex(MissionError, "PROTECTED_POINTER"):
            validate_mission(mission)
        mission = load("blocked-resumable.json")
        mission["objective"] = "Credential github_pat_abcdefghijklmnopqrstuvwxyz123456"
        with self.assertRaisesRegex(MissionError, "PROTECTED_BOUNDARY_FAILURE"):
            validate_mission(mission)

    def test_unsafe_windows_repository_path_fails_closed(self) -> None:
        mission = load("canonical-implementation.json")
        mission["source_binding"]["changed_paths"] = ["C:/outside.txt"]
        mission["source_binding"]["changed_paths_digest"] = changed_paths_digest(["governance/mission-board-contract.md"])
        with self.assertRaisesRegex(MissionError, "UNSAFE_PATH"):
            validate_mission(mission)

    def test_unicode_equivalent_repository_paths_collide(self) -> None:
        mission = load("canonical-implementation.json")
        mission["source_binding"]["changed_paths"] = ["proof/café.txt", "proof/cafe\u0301.txt"]
        mission["source_binding"]["changed_paths_digest"] = "0" * 64
        with self.assertRaisesRegex(MissionError, "DUPLICATE_PATH"):
            validate_mission(mission)

    def test_duplicate_json_keys_fail_closed(self) -> None:
        with self.assertRaisesRegex(MissionError, "DUPLICATE_JSON_KEY"):
            parse_json_document('{"mission_state":"READY","mission_state":"CLOSED"}')

    def test_state_transitions_are_closed(self) -> None:
        validate_transition("CAPTURED", "TRIAGED")
        validate_transition("BLOCKED_RESUMABLE", "IN_PROGRESS")
        validate_source_transition("PHOENIX_PENDING", "PR_OPEN")
        validate_source_transition("MERGED_PENDING_READBACK", "CANONICAL")
        with self.assertRaisesRegex(MissionError, "INVALID_TRANSITION"):
            validate_transition("CAPTURED", "CLOSED")
        with self.assertRaisesRegex(MissionError, "INVALID_SOURCE_TRANSITION"):
            validate_source_transition("PHOENIX_PENDING", "CANONICAL")

    def test_explicit_blocking_edge_stops_the_remaining_queue(self) -> None:
        blocked = load("sequence-7.json")
        blocked["dependencies"] = [{"relation": "BLOCKS", "repository": "Jktomy/atlas-prime", "mission_ref": "Mission 12"}]
        missions = {5: load("sequence-5.json"), 7: blocked, 12: load("sequence-12.json")}
        receipt = sequence_missions(missions, [5, 7, 12])
        self.assertEqual([item["result"] for item in receipt["results"]], ["COMPLETE", "BLOCKED_RESUMABLE", "NOT_STARTED_AFTER_STOP"])


if __name__ == "__main__":
    unittest.main()
