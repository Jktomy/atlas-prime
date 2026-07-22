from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from tools.candidate_seal import (
    CandidateSealError,
    build_candidate_seal,
    build_repair_batch,
    reconcile_publication_state,
    verify_candidate_seal,
)

BASE = "7" * 40
TREE = "8" * 40
HEAD = "9" * 40
BRANCH = "agent/stage-4-candidate-sealing-r01"
CHECKS = {"focused-tests": "a" * 64, "full-validation": "b" * 64}
MISSION = {
    "repository": "Jktomy/atlas-prime",
    "issue_number": 287,
    "mission_id": "GHA-OPT-STAGE-4-CANDIDATE-SEALING-R01",
    "attempt_id": "GHA-OPT-STAGE-4-ATTEMPT-01",
    "objective": "Seal complete candidates and batch candidate-caused repair.",
}
FILES = {
    "tools/candidate_seal/core.py": b"candidate core\n",
    "tests/prime-program/test_candidate_seal.py": b"candidate tests\n",
}


def seal(files=FILES, *, base=BASE, head=HEAD, checks=CHECKS):
    return build_candidate_seal(
        MISSION,
        canonical_base_sha=base,
        branch_intent=BRANCH,
        candidate_files=files,
        expected_candidate_tree_sha=TREE,
        expected_head_sha=head,
        prepublication_checks=checks,
        authorizer="Jayson",
        operator="Codex",
        route="DIRECT_GITHUB_NATIVE_AEGIS_BREAK",
        generated_state="STALE_ALLOWED",
    )


def verify(candidate, files=FILES, *, base=BASE, head=HEAD, checks=CHECKS, consumed=()):
    return verify_candidate_seal(
        candidate,
        canonical_base_sha=base,
        branch_intent=BRANCH,
        candidate_files=files,
        expected_candidate_tree_sha=TREE,
        expected_head_sha=head,
        prepublication_checks=checks,
        consumed_seal_ids=consumed,
    )


class CandidateSealTests(unittest.TestCase):
    def test_seal_creation_is_deterministic_and_path_ordered(self) -> None:
        first = seal(dict(reversed(list(FILES.items()))))
        second = seal()
        self.assertEqual(first, second)
        self.assertEqual(first["path_inventory"], sorted(FILES))
        self.assertEqual(first["seal_state"], "SEALED_PREPUBLICATION")
        self.assertEqual(verify(first)["status"], "VERIFIED")

    def test_seal_digest_tamper_fails_closed(self) -> None:
        candidate = seal()
        candidate["operator"] = "Unknown"
        with self.assertRaisesRegex(CandidateSealError, "SEAL_DIGEST_MISMATCH"):
            verify(candidate)

    def test_stale_base_invalidates_seal(self) -> None:
        with self.assertRaisesRegex(CandidateSealError, "STALE_BASE"):
            verify(seal(), base="c" * 40)

    def test_path_drift_invalidates_seal(self) -> None:
        drifted = dict(FILES)
        drifted["governance/new.md"] = b"new\n"
        with self.assertRaisesRegex(CandidateSealError, "PATH_DRIFT"):
            verify(seal(), drifted)

    def test_byte_tree_head_and_check_drift_invalidate_evidence(self) -> None:
        drifted = dict(FILES)
        drifted["tools/candidate_seal/core.py"] = b"changed\n"
        with self.assertRaisesRegex(CandidateSealError, "BYTE_DRIFT"):
            verify(seal(), drifted)
        with self.assertRaisesRegex(CandidateSealError, "TREE_DRIFT"):
            verify_candidate_seal(
                seal(),
                canonical_base_sha=BASE,
                branch_intent=BRANCH,
                candidate_files=FILES,
                expected_candidate_tree_sha="d" * 40,
                expected_head_sha=HEAD,
                prepublication_checks=CHECKS,
            )
        with self.assertRaisesRegex(CandidateSealError, "HEAD_DRIFT"):
            verify(seal(), head="e" * 40)
        with self.assertRaisesRegex(CandidateSealError, "CHECK_EVIDENCE_DRIFT"):
            verify(seal(), checks={"full-validation": "f" * 64})

    def test_consumed_seal_replay_rejects(self) -> None:
        candidate = seal()
        with self.assertRaisesRegex(CandidateSealError, "SEAL_REPLAY"):
            verify(candidate, consumed=[candidate["seal_id"]])

    def test_interrupted_branch_only_publication_is_resumable_without_repush(self) -> None:
        candidate = seal()
        result = reconcile_publication_state(
            candidate,
            {
                "canonical_main_sha": BASE,
                "branch_head_sha": HEAD,
                "pull_requests": [],
                "consumed_seal_ids": [],
            },
        )
        self.assertEqual(result["status"], "BLOCKED_RESUMABLE")
        self.assertEqual(result["remote_mutation_allowance"], "CREATE_DRAFT_PR_ONLY")
        self.assertFalse(result["blind_retry"])

    def test_exact_draft_is_readback_only_and_duplicate_pr_fails_closed(self) -> None:
        candidate = seal()
        exact_pr = {
            "number": 300,
            "state": "OPEN",
            "draft": True,
            "base_sha": BASE,
            "head_sha": HEAD,
            "branch": BRANCH,
        }
        state = {
            "canonical_main_sha": BASE,
            "branch_head_sha": HEAD,
            "pull_requests": [exact_pr],
            "consumed_seal_ids": [],
        }
        self.assertEqual(reconcile_publication_state(candidate, state)["status"], "PR_OPEN_RECONCILED")
        duplicate = copy.deepcopy(state)
        duplicate["pull_requests"].append(dict(exact_pr, number=301))
        with self.assertRaisesRegex(CandidateSealError, "DUPLICATE_PULL_REQUEST"):
            reconcile_publication_state(candidate, duplicate)

    def test_unknown_or_conflicting_remote_state_fails_closed(self) -> None:
        candidate = seal()
        with self.assertRaisesRegex(CandidateSealError, "UNKNOWN_REMOTE_STATE"):
            reconcile_publication_state(candidate, {"canonical_main_sha": BASE})
        with self.assertRaisesRegex(CandidateSealError, "REMOTE_STATE_CONFLICT"):
            reconcile_publication_state(
                candidate,
                {
                    "canonical_main_sha": BASE,
                    "branch_head_sha": "f" * 40,
                    "pull_requests": [],
                    "consumed_seal_ids": [],
                },
            )

    def test_batched_repair_collects_all_actionable_and_invalidates_evidence(self) -> None:
        candidate = seal()
        findings = [
            {
                "finding_id": "F-002",
                "source": "CI",
                "classification": "ACTIONABLE",
                "candidate_caused": True,
                "readable": True,
                "detail": "second candidate regression",
            },
            {
                "finding_id": "F-001",
                "source": "REVIEW",
                "classification": "ACTIONABLE",
                "candidate_caused": True,
                "readable": True,
                "detail": "first candidate regression",
            },
            {
                "finding_id": "F-003",
                "source": "COPILOT",
                "classification": "UNAVAILABLE",
                "candidate_caused": False,
                "readable": False,
                "detail": "provider quota unavailable",
            },
        ]
        batch = build_repair_batch(candidate, findings)
        self.assertEqual(batch["actionable_finding_ids"], ["F-001", "F-002"])
        self.assertEqual(batch["publication_limit"], "ONE_CONSOLIDATED_REPAIR")
        self.assertTrue(batch["replacement_seal_required"])
        self.assertEqual(
            batch["invalidated_evidence"],
            [
                "CANDIDATE_SEAL",
                "PREPUBLICATION_VALIDATION",
                "HOSTED_VALIDATION",
                "REVIEW",
                "STRIKEFORCE",
                "READY",
                "MERGE",
            ],
        )

    def test_decision_unknown_and_non_candidate_actionable_findings_stop(self) -> None:
        template = {
            "finding_id": "F-001",
            "source": "REVIEW",
            "classification": "DECISION_REQUIRED",
            "candidate_caused": True,
            "readable": True,
            "detail": "human choice required",
        }
        with self.assertRaisesRegex(CandidateSealError, "REPAIR_DECISION_REQUIRED"):
            build_repair_batch(seal(), [template])
        unknown = dict(template, classification="UNKNOWN")
        with self.assertRaisesRegex(CandidateSealError, "REPAIR_UNKNOWN_STATE"):
            build_repair_batch(seal(), [unknown])
        outside = dict(template, classification="ACTIONABLE", candidate_caused=False)
        with self.assertRaisesRegex(CandidateSealError, "ACTIONABLE_FINDING_OUT_OF_SCOPE"):
            build_repair_batch(seal(), [outside])

    def test_paths_are_exact_safe_and_casefold_unique(self) -> None:
        for bad_files in (
            {"../escape.md": b"x"},
            {"tools\\candidate.py": b"x"},
            {" tools/candidate.py": b"x"},
            {"Tools/candidate.py": b"x", "tools/Candidate.py": b"y"},
        ):
            with self.subTest(paths=list(bad_files)):
                with self.assertRaises(CandidateSealError):
                    seal(bad_files)


if __name__ == "__main__":
    unittest.main()
