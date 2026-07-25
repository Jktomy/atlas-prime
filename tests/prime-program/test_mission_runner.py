from __future__ import annotations

import json
import unittest
from pathlib import Path

from tools.mission_runner.core import (
    MissionRunnerError,
    assert_mission_may_block,
    assert_publication_compare_and_swap,
    assert_single_carrier,
    build_checkpoint,
    build_route_attempt,
    build_working_handoff,
    claim_stage,
    match_worker_to_stage,
    next_authorized_route,
    reconstruct_attempt,
    validate_checkpoint_chain,
    validate_worker_capability,
)
from tools.mission_board.core import validate_mission


ROOT = Path(__file__).resolve().parents[2]
HEAD_A = "a" * 40
HEAD_B = "b" * 40
MISSION_ID = "MISSION-WORLDHOPPER-RELAY-AEGIS-BREAK-REPAIR-R01"
ATTEMPT_ID = f"{MISSION_ID}-ATTEMPT-01"
ROUTES = ["THREAD_ENGINE", "SWORD_OATHBRINGER", "AEGIS_BREAK_GITHUB_NATIVE"]


def worker(*stages: str, worker_id: str = "CODEX-WORLDHOPPER-01") -> dict:
    stage_capabilities = {
        "MISSION_READ": "MISSION_READ",
        "CHECKPOINT": "CHECKPOINT_WRITE",
        "SOURCE_CONSTRUCTION": "COMPLETE_CHECKOUT",
        "COMPILATION": "COMPILER_EXECUTION",
        "VALIDATION": "VALIDATION_EXECUTION",
        "PUBLICATION": "PUBLICATION",
        "REVIEW": "REVIEW_RECONCILIATION",
        "READY": "READY_TRANSITION",
        "PERMANENCE": "EXACT_HEAD_PERMANENCE",
        "CANONICAL_READBACK": "CANONICAL_READBACK",
    }
    order = list(stage_capabilities)
    selected = sorted(set(stages), key=order.index)
    return {
        "schema_version": "atlas.mission-worker-capability.v1",
        "worker_id": worker_id,
        "adapter_id": "CODEX-DESKTOP",
        "provider": "OPENAI",
        "surface": "CHATGPT-CODEX",
        "capabilities": sorted(stage_capabilities[stage] for stage in selected),
        "takeover_evidence": [
            {"stage": stage, "status": "ACCEPTED", "evidence_ref": f"fixture://takeover/{stage}"}
            for stage in selected
        ],
        "declared_at": "2026-07-25T18:00:00-05:00",
    }


def checkpoint(
    sequence: int,
    *,
    previous: dict | None = None,
    worker_id: str = "CODEX-WORLDHOPPER-01",
    lease_disposition: str = "COMPLETED",
) -> dict:
    return build_checkpoint(
        mission_id=MISSION_ID,
        attempt_id=ATTEMPT_ID,
        sequence=sequence,
        worker_id=worker_id,
        stage="SOURCE_CONSTRUCTION",
        observed_main_head=HEAD_A,
        observed_branch_head=HEAD_B,
        completed_work=[f"Completed relay step {sequence}."],
        remaining_work=["Continue the same candidate."],
        stop_reason=None,
        claim_id=f"CLAIM-{sequence}",
        lease_disposition=lease_disposition,
        next_action="Continue exact-head work.",
        created_at=f"2026-07-25T18:0{sequence}:00-05:00",
        previous=previous,
    )


def attempt(route: str, ordinal: int, status: str, *, stage: str = "PUBLICATION") -> dict:
    return build_route_attempt(
        route_id=route,
        ordinal=ordinal,
        stage=stage,
        status=status,
        failed_capability=None if status in {"SUCCEEDED", "PENDING", "IN_PROGRESS", "TRANSFER_REQUIRED"} else "SYNTHETIC_FAILURE",
        evidence_refs=[f"fixture://route/{ordinal}"],
        observed_head=HEAD_B,
        next_route_disposition="Advance or complete according to the terminal result.",
        attempted_at=f"2026-07-25T18:1{ordinal}:00-05:00",
    )


def payloads(*paths: str) -> dict[str, bytes]:
    return {path: f"synthetic public-clean bytes for {path}\n".encode() for path in paths}


class MissionRunnerTests(unittest.TestCase):
    def test_campaign_effort_class_beu_16_is_valid(self) -> None:
        mission = json.loads(
            (ROOT / "tests/prime-program/fixtures/mission-board/canonical-implementation.json").read_text(
                encoding="utf-8"
            )
        )
        mission["effort_class"] = "BEU_16"
        self.assertEqual(validate_mission(mission)["effort_class"], "BEU_16")

    def test_digest_chained_checkpoints_reject_fork_replay_and_stale_worker(self) -> None:
        first = checkpoint(1)
        second = checkpoint(2, previous=first)
        self.assertEqual(len(validate_checkpoint_chain([first, second])), 2)

        replay = dict(second)
        replay["previous_checkpoint_digest"] = None
        with self.assertRaisesRegex(MissionRunnerError, "CHECKPOINT_INTEGRITY"):
            validate_checkpoint_chain([first, replay])

        with self.assertRaisesRegex(MissionRunnerError, "CHECKPOINT_SEQUENCE"):
            checkpoint(3, previous=first)

        with self.assertRaisesRegex(MissionRunnerError, "STALE_WORKER"):
            claim_stage(
                worker("SOURCE_CONSTRUCTION"),
                stage="SOURCE_CONSTRUCTION",
                claim_id="STALE-CLAIM",
                expected_checkpoint_digest="sha256:" + "0" * 64,
                checkpoints=[first, second],
            )

    def test_simultaneous_claim_and_unsupported_worker_are_rejected(self) -> None:
        claimed = checkpoint(1, lease_disposition="CLAIMED")
        with self.assertRaisesRegex(MissionRunnerError, "SIMULTANEOUS_CLAIM"):
            claim_stage(
                worker("SOURCE_CONSTRUCTION"),
                stage="SOURCE_CONSTRUCTION",
                claim_id="SECOND-CLAIM",
                expected_checkpoint_digest=claimed["checkpoint_digest"],
                checkpoints=[claimed],
            )
        with self.assertRaisesRegex(MissionRunnerError, "WORKER_CAPABILITY_MISMATCH"):
            match_worker_to_stage(worker("MISSION_READ"), "PUBLICATION")

    def test_worker_capability_requires_real_stage_takeover_evidence(self) -> None:
        declaration = worker("PUBLICATION")
        self.assertEqual(validate_worker_capability(declaration)["capabilities"], ["PUBLICATION"])
        declaration["takeover_evidence"] = []
        with self.assertRaisesRegex(MissionRunnerError, "WORKER_CAPABILITY_MISMATCH"):
            match_worker_to_stage(declaration, "PUBLICATION")

    def test_working_source_handoff_is_one_branch_cas_and_pr_only_after_seal(self) -> None:
        first = build_working_handoff(
            mission_id=MISSION_ID,
            attempt_id=ATTEMPT_ID,
            branch="repair/mission-339-worldhopper-relay-r01",
            base_sha=HEAD_A,
            expected_head=HEAD_B,
            changed_paths=["tools/mission_runner/core.py"],
            candidate_payloads=payloads("tools/mission_runner/core.py"),
            candidate_state="WORKING_DRAFT",
        )
        with self.assertRaisesRegex(MissionRunnerError, "PREMATURE_PULL_REQUEST"):
            build_working_handoff(
                mission_id=MISSION_ID,
                attempt_id=ATTEMPT_ID,
                branch=first["branch"],
                base_sha=HEAD_A,
                expected_head="c" * 40,
                changed_paths=first["changed_paths"],
                candidate_payloads=payloads(*first["changed_paths"]),
                candidate_state="WORKING_DRAFT",
                pull_request=341,
                previous=first,
                observed_previous_head=HEAD_B,
            )
        with self.assertRaisesRegex(MissionRunnerError, "STALE_WORKER"):
            build_working_handoff(
                mission_id=MISSION_ID,
                attempt_id=ATTEMPT_ID,
                branch=first["branch"],
                base_sha=HEAD_A,
                expected_head="c" * 40,
                changed_paths=first["changed_paths"],
                candidate_payloads=payloads(*first["changed_paths"]),
                candidate_state="SEALED",
                pull_request=341,
                previous=first,
                observed_previous_head="d" * 40,
            )
        sealed = build_working_handoff(
            mission_id=MISSION_ID,
            attempt_id=ATTEMPT_ID,
            branch=first["branch"],
            base_sha=HEAD_A,
            expected_head="c" * 40,
            changed_paths=first["changed_paths"],
            candidate_payloads=payloads(*first["changed_paths"]),
            candidate_state="SEALED",
            pull_request=341,
            previous=first,
            observed_previous_head=HEAD_B,
        )
        self.assertEqual(sealed["candidate_state"], "SEALED")
        with self.assertRaisesRegex(MissionRunnerError, "SEALED_CANDIDATE_IMMUTABLE"):
            build_working_handoff(
                mission_id=MISSION_ID,
                attempt_id=ATTEMPT_ID,
                branch=sealed["branch"],
                base_sha=HEAD_A,
                expected_head="d" * 40,
                changed_paths=sealed["changed_paths"],
                candidate_payloads=payloads(*sealed["changed_paths"]),
                candidate_state="SEALED",
                pull_request=341,
                previous=sealed,
                observed_previous_head=sealed["expected_head"],
            )

    def test_ordered_fallback_exhaustion_is_executable_and_stage_aware(self) -> None:
        first = attempt(ROUTES[0], 1, "REJECTED_CAPABILITY")
        self.assertEqual(next_authorized_route(ROUTES, [first], stage="PUBLICATION"), ROUTES[1])
        with self.assertRaisesRegex(MissionRunnerError, "ROUTE_FALLBACK_PENDING"):
            assert_mission_may_block(ROUTES, [first], stage="PUBLICATION")

        second = attempt(ROUTES[1], 2, "REJECTED_CAPABILITY")
        third = attempt(ROUTES[2], 3, "REJECTED_CAPABILITY")
        self.assertEqual(
            assert_mission_may_block(ROUTES, [first, second, third], stage="PUBLICATION")["basis"],
            "AUTHORIZED_ROUTES_EXHAUSTED",
        )

        wrong_stage = attempt(ROUTES[1], 2, "REJECTED_CAPABILITY", stage="COMPILATION")
        with self.assertRaisesRegex(MissionRunnerError, "ROUTE_STAGE_DRIFT"):
            next_authorized_route(ROUTES, [first, wrong_stage], stage="PUBLICATION")

    def test_forced_relay_thread_engine_then_clone_failure_evaluates_aegis_break(self) -> None:
        spear = attempt(ROUTES[0], 1, "REJECTED_CAPABILITY")
        oathbringer = attempt(ROUTES[1], 2, "REJECTED_CAPABILITY")
        self.assertEqual(
            next_authorized_route(ROUTES, [spear, oathbringer], stage="PUBLICATION"),
            "AEGIS_BREAK_GITHUB_NATIVE",
        )
        aegis = attempt(ROUTES[2], 3, "SUCCEEDED")
        self.assertIsNone(next_authorized_route(ROUTES, [spear, oathbringer, aegis], stage="PUBLICATION"))
        with self.assertRaisesRegex(MissionRunnerError, "ROUTE_ALREADY_SUCCEEDED"):
            assert_mission_may_block(ROUTES, [spear, oathbringer, aegis], stage="PUBLICATION")

    def test_true_gate_stops_fallback_and_rejects_later_attempts(self) -> None:
        safety_gate = attempt(ROUTES[0], 1, "REJECTED_SAFETY")
        self.assertIsNone(next_authorized_route(ROUTES, [safety_gate], stage="PUBLICATION"))
        self.assertEqual(
            assert_mission_may_block(
                ROUTES, [safety_gate], stage="PUBLICATION", true_gate=True
            )["basis"],
            "REJECTED_SAFETY",
        )
        later_attempt = attempt(ROUTES[1], 2, "REJECTED_CAPABILITY")
        with self.assertRaisesRegex(MissionRunnerError, "ROUTE_AFTER_TRUE_GATE"):
            next_authorized_route(
                ROUTES, [safety_gate, later_attempt], stage="PUBLICATION"
            )

    def test_deleted_branch_closed_pr_and_ambiguous_head_fail_closed(self) -> None:
        with self.assertRaisesRegex(MissionRunnerError, "EXPECTED_HEAD_MISMATCH"):
            assert_publication_compare_and_swap(HEAD_A, HEAD_B)

        handoff = build_working_handoff(
            mission_id=MISSION_ID,
            attempt_id=ATTEMPT_ID,
            branch="repair/mission-339-worldhopper-relay-r01",
            base_sha=HEAD_A,
            expected_head=HEAD_B,
            changed_paths=["tools/mission_runner/core.py"],
            candidate_payloads=payloads("tools/mission_runner/core.py"),
            candidate_state="WORKING_DRAFT",
        )

        mission = json.loads(
            (ROOT / "tests/prime-program/fixtures/mission-board/canonical-implementation.json").read_text(
                encoding="utf-8"
            )
        )
        with self.assertRaisesRegex(MissionRunnerError, "WORKER_CAPABILITY_MISMATCH"):
            reconstruct_attempt(
                mission,
                canonical_head=mission["source_binding"]["merged_commit"],
                worker=worker("MISSION_READ"),
                stage="PUBLICATION",
                checkpoints=[],
            )

        mission["mission_id"] = MISSION_ID
        mission["attempt_id"] = ATTEMPT_ID
        mission["source_binding"]["branch"] = handoff["branch"]
        with self.assertRaisesRegex(MissionRunnerError, "WORKING_BRANCH_UNAVAILABLE"):
            reconstruct_attempt(
                mission,
                canonical_head=mission["source_binding"]["merged_commit"],
                worker=worker("MISSION_READ"),
                stage="MISSION_READ",
                checkpoints=[],
                working_handoff=handoff,
                branch_snapshot={"exists": False, "branch": handoff["branch"], "head_sha": None},
            )

    def test_duplicate_undeclared_and_closed_carriers_fail_closed(self) -> None:
        with self.assertRaisesRegex(MissionRunnerError, "UNDECLARED_PATH"):
            build_working_handoff(
                mission_id=MISSION_ID,
                attempt_id=ATTEMPT_ID,
                branch="repair/mission-339-worldhopper-relay-r01",
                base_sha=HEAD_A,
                expected_head=HEAD_B,
                changed_paths=["tools/mission_runner/core.py", "undeclared/path.md"],
                candidate_payloads=payloads("tools/mission_runner/core.py", "undeclared/path.md"),
                declared_path_envelope=["tools/mission_runner/core.py"],
                candidate_state="WORKING_DRAFT",
            )
        branch_snapshot = {"exists": True, "branch": "repair/mission-339-worldhopper-relay-r01", "head_sha": HEAD_B}
        with self.assertRaisesRegex(MissionRunnerError, "DUPLICATE_BRANCH"):
            assert_single_carrier(
                branch=branch_snapshot["branch"],
                branch_snapshots=[branch_snapshot, dict(branch_snapshot)],
                pull_request=None,
                pr_snapshots=[],
            )
        with self.assertRaisesRegex(MissionRunnerError, "DUPLICATE_PULL_REQUEST"):
            assert_single_carrier(
                branch=branch_snapshot["branch"],
                branch_snapshots=[branch_snapshot],
                pull_request=341,
                pr_snapshots=[
                    {"number": 341, "branch": branch_snapshot["branch"], "state": "OPEN"},
                    {"number": 342, "branch": branch_snapshot["branch"], "state": "OPEN"},
                ],
            )
        with self.assertRaisesRegex(MissionRunnerError, "PULL_REQUEST_UNAVAILABLE"):
            assert_single_carrier(
                branch=branch_snapshot["branch"],
                branch_snapshots=[branch_snapshot],
                pull_request=341,
                pr_snapshots=[{"number": 341, "branch": branch_snapshot["branch"], "state": "CLOSED"}],
            )

    def test_public_clean_checkpoint_rejects_protected_content(self) -> None:
        with self.assertRaisesRegex(MissionRunnerError, "PROTECTED_CONTENT"):
            build_checkpoint(
                mission_id=MISSION_ID,
                attempt_id=ATTEMPT_ID,
                sequence=1,
                worker_id="CODEX-WORLDHOPPER-01",
                stage="CHECKPOINT",
                observed_main_head=HEAD_A,
                observed_branch_head=None,
                completed_work=["pass" + "word=" + "'synthetic-secret-value'"],
                remaining_work=[],
                stop_reason=None,
                claim_id="CLAIM-PROTECTED",
                lease_disposition="RELEASED",
                next_action="Reject before publication.",
                created_at="2026-07-25T18:30:00-05:00",
            )


if __name__ == "__main__":
    unittest.main()
