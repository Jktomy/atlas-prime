from __future__ import annotations

import copy
import hashlib
import json
import unittest
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

from tools.agentic_warrants.permanence import validate_action_receipt, validate_action_request  # noqa: E402
from tools.agentic_warrants.validator import WarrantValidationError, sha256, validate_warrant, warrant_body_sha256  # noqa: E402


class ReplayLedger:
    def __init__(self) -> None:
        self.seen: set[tuple[int, str]] = set()

    def consume(self, identity: tuple[str, ...]) -> bool:
        components = {(index, value) for index, value in enumerate(identity)}
        if components & self.seen:
            return False
        self.seen.update(components)
        return True


class ShardbladePermanenceTests(unittest.TestCase):
    now = datetime(2026, 7, 13, 1, tzinfo=timezone.utc)

    @staticmethod
    def trusted(record: dict) -> bool:
        return record["authorizer"] == "Jayson" and record["signature"].startswith("trusted-shardblade-")

    def ready_request(self) -> dict:
        request = {
            "schema_version": "atlas.shardblade-permanence-request.v1",
            "request_id": "SHARDBLADE-READY-REQUEST-R01",
            "nonce": "shardblade-ready-request-r01",
            "action": "READY",
            "created_at": "2026-07-13T00:06:00Z",
            "readback_at": "2026-07-13T00:07:00Z",
            "authorizer": "Jayson",
            "operator": "Athena",
            "credential_principal": "Jktomy",
            "invoking_mechanism": "GitHub exact-state adapter",
            "repository": "Jktomy/atlas-prime",
            "base_branch": "main",
            "base_sha": "a" * 40,
            "pull_request": 130,
            "pr_state": "DRAFT",
            "source_branch": "agent/shardblade-fixture-r01",
            "head_sha": "b" * 40,
            "tree_sha": "c" * 40,
            "changed_paths": ["governance/shard-doctrine.md", "tests/prime-program/test_shardblade_permanence.py"],
            "changed_paths_sha256": "",
            "protected_paths": ["governance/shard-doctrine.md"],
            "protected_paths_sha256": "",
            "protected_construction_approval_sha256": "4" * 64,
            "preview_sha256": "d" * 64,
            "construction_receipt_sha256": "e" * 64,
            "pr_readback_sha256": "",
            "ci": [
                {"platform": "UBUNTU", "workflow_name": "Prime read-only validation", "check_name": "validate (ubuntu-latest)", "run_id": 1001, "run_attempt": 1, "workflow_source_sha": "f" * 40, "head_sha": "b" * 40, "conclusion": "SUCCESS"},
                {"platform": "WINDOWS", "workflow_name": "Prime read-only validation", "check_name": "validate (windows-latest)", "run_id": 1001, "run_attempt": 1, "workflow_source_sha": "f" * 40, "head_sha": "b" * 40, "conclusion": "SUCCESS"},
            ],
            "detached_review": {"review_id": "DETACHED-R01", "reviewer_context": "fresh-read-only-review", "head_sha": "b" * 40, "verdict": "GREEN", "receipt_sha256": "1" * 64},
            "prior_ready_receipt_sha256": None,
            "merge_method": None,
            "forbidden_actions": {"author": False, "modify": False, "widen": False, "substitute": False, "bypass_checks": False, "automatic_retry": False, "standing_authority": False},
        }
        self.bind_readback(request)
        return request

    @staticmethod
    def bind_readback(request: dict) -> None:
        request["changed_paths_sha256"] = sha256(request["changed_paths"])
        request["protected_paths_sha256"] = sha256(request["protected_paths"])
        body = {key: request[key] for key in (
            "repository", "base_branch", "base_sha", "pull_request", "pr_state",
            "source_branch", "head_sha", "tree_sha", "changed_paths", "protected_paths",
        )}
        request["pr_readback_sha256"] = sha256(body)

    def approval(self, request: dict, *, label: str, issued: str) -> dict:
        return {
            "schema_version": "atlas.shardblade-permanence-approval.v1",
            "approval_id": f"SHARDBLADE-{label.upper()}-APPROVAL-R01",
            "nonce": f"shardblade-{label}-approval-r01",
            "request_id": request["request_id"],
            "request_sha256": sha256(request),
            "action": request["action"],
            "authorizer": "Jayson",
            "issued_at": issued,
            "expires_at": "2026-07-13T02:00:00Z",
            "signature_scheme": "TRUSTED_SESSION_READBACK",
            "signature": f"trusted-shardblade-{label}",
        }

    def ready_receipt(self, request: dict, approval: dict) -> dict:
        return {
            "schema_version": "atlas.shardblade-permanence-receipt.v1",
            "receipt_id": "SHARDBLADE-READY-RECEIPT-R01",
            "attempt_id": "SHARDBLADE-READY-ATTEMPT-R01",
            "nonce": "shardblade-ready-receipt-r01",
            "request_id": request["request_id"],
            "request_sha256": sha256(request),
            "approval_record_sha256": sha256(approval),
            "action": "READY",
            "executed_at": "2026-07-13T00:10:00Z",
            "repository": request["repository"],
            "pull_request": request["pull_request"],
            "base_sha": request["base_sha"],
            "head_sha": request["head_sha"],
            "tree_sha": request["tree_sha"],
            "changed_paths_sha256": request["changed_paths_sha256"],
            "prior_ready_receipt_sha256": None,
            "result": "SUCCESS",
            "error_code": None,
            "observed_pr_state": "OPEN_READY",
            "observed_head_sha": request["head_sha"],
            "observed_tree_sha": request["tree_sha"],
            "merge_commit_sha": None,
            "canonical_main_sha": None,
            "canonical_tree_sha": None,
            "mutation": {"ready": True, "merge": False, "candidate_modified": False, "head_changed": False},
            "stop_point": "READY_READBACK",
            "rollback": "CLOSE_PR_BEFORE_MERGE",
        }

    def merge_chain(self) -> tuple[dict, dict, dict, dict, dict, dict]:
        ready = self.ready_request()
        ready_approval = self.approval(ready, label="ready", issued="2026-07-13T00:08:00Z")
        ready_receipt = self.ready_receipt(ready, ready_approval)
        merge = copy.deepcopy(ready)
        merge.update({
            "request_id": "SHARDBLADE-MERGE-REQUEST-R01",
            "nonce": "shardblade-merge-request-r01",
            "action": "MERGE",
            "created_at": "2026-07-13T00:11:00Z",
            "readback_at": "2026-07-13T00:12:00Z",
            "pr_state": "OPEN_READY",
            "prior_ready_receipt_sha256": sha256(ready_receipt),
            "merge_method": "MERGE_COMMIT",
        })
        self.bind_readback(merge)
        merge_approval = self.approval(merge, label="merge", issued="2026-07-13T00:13:00Z")
        merge_receipt = copy.deepcopy(ready_receipt)
        merge_receipt.update({
            "receipt_id": "SHARDBLADE-MERGE-RECEIPT-R01",
            "attempt_id": "SHARDBLADE-MERGE-ATTEMPT-R01",
            "nonce": "shardblade-merge-receipt-r01",
            "request_id": merge["request_id"],
            "request_sha256": sha256(merge),
            "approval_record_sha256": sha256(merge_approval),
            "action": "MERGE",
            "executed_at": "2026-07-13T00:15:00Z",
            "prior_ready_receipt_sha256": sha256(ready_receipt),
            "observed_pr_state": "MERGED",
            "merge_commit_sha": "2" * 40,
            "canonical_main_sha": "2" * 40,
            "canonical_tree_sha": merge["tree_sha"],
            "mutation": {"ready": False, "merge": True, "candidate_modified": False, "head_changed": False},
            "stop_point": "MERGED_MAIN_READBACK",
            "rollback": "REVIEWED_REVERT_PR",
        })
        return ready, ready_approval, ready_receipt, merge, merge_approval, merge_receipt

    def test_ready_and_merge_require_distinct_exact_chain(self) -> None:
        ready, ready_approval, ready_receipt, merge, merge_approval, merge_receipt = self.merge_chain()
        validate_action_request(ready, ready_approval, verifier=self.trusted, reserve_guard=ReplayLedger().consume, now=self.now)
        validate_action_receipt(ready_receipt, ready, ready_approval, verifier=self.trusted, receipt_guard=ReplayLedger().consume, now=self.now)
        validate_action_request(
            merge, merge_approval, verifier=self.trusted, reserve_guard=ReplayLedger().consume,
            ready_request=ready, ready_approval=ready_approval, ready_receipt=ready_receipt, now=self.now,
        )
        validate_action_receipt(merge_receipt, merge, merge_approval, verifier=self.trusted, receipt_guard=ReplayLedger().consume, ready_request=ready, ready_approval=ready_approval, ready_receipt=ready_receipt, now=self.now)

    def test_combined_action_and_merge_without_ready_fail_closed(self) -> None:
        ready = self.ready_request()
        combined = copy.deepcopy(ready)
        combined["action"] = ["READY", "MERGE"]
        with self.assertRaisesRegex(WarrantValidationError, "SHARDBLADE_REQUEST_SCHEMA_INVALID"):
            validate_action_request(combined, self.approval(ready, label="ready", issued="2026-07-13T00:08:00Z"), verifier=self.trusted, reserve_guard=ReplayLedger().consume, now=self.now)
        _, _, _, merge, merge_approval, _ = self.merge_chain()
        with self.assertRaisesRegex(WarrantValidationError, "SHARDBLADE_READY_RECEIPT_REQUIRED"):
            validate_action_request(merge, merge_approval, verifier=self.trusted, reserve_guard=ReplayLedger().consume, now=self.now)

    def test_approval_reuse_and_candidate_drift_fail_closed(self) -> None:
        ready, ready_approval, ready_receipt, merge, merge_approval, _ = self.merge_chain()
        reused = copy.deepcopy(merge_approval)
        reused.update({"approval_id": ready_approval["approval_id"], "nonce": ready_approval["nonce"]})
        with self.assertRaisesRegex(WarrantValidationError, "SHARDBLADE_APPROVAL_IDENTITY_REUSED"):
            validate_action_request(merge, reused, verifier=self.trusted, reserve_guard=ReplayLedger().consume, ready_request=ready, ready_approval=ready_approval, ready_receipt=ready_receipt, now=self.now)
        drifted = copy.deepcopy(merge)
        drifted["head_sha"] = "9" * 40
        for item in drifted["ci"]:
            item["head_sha"] = drifted["head_sha"]
        drifted["detached_review"]["head_sha"] = drifted["head_sha"]
        self.bind_readback(drifted)
        drifted_approval = self.approval(drifted, label="drift", issued="2026-07-13T00:13:00Z")
        with self.assertRaisesRegex(WarrantValidationError, "SHARDBLADE_CANDIDATE_DRIFT"):
            validate_action_request(drifted, drifted_approval, verifier=self.trusted, reserve_guard=ReplayLedger().consume, ready_request=ready, ready_approval=ready_approval, ready_receipt=ready_receipt, now=self.now)
        missing_protected = copy.deepcopy(ready)
        missing_protected.update({"protected_paths": [], "protected_construction_approval_sha256": None})
        self.bind_readback(missing_protected)
        missing_approval = self.approval(missing_protected, label="protected", issued="2026-07-13T00:08:00Z")
        with self.assertRaisesRegex(WarrantValidationError, "SHARDBLADE_PROTECTED_BINDING_MISMATCH"):
            validate_action_request(missing_protected, missing_approval, verifier=self.trusted, reserve_guard=ReplayLedger().consume, now=self.now)

    def test_ci_review_and_success_readback_drift_fail_closed(self) -> None:
        ready, ready_approval, ready_receipt, merge, merge_approval, merge_receipt = self.merge_chain()
        wrong_ci = copy.deepcopy(ready)
        wrong_ci["ci"][0]["head_sha"] = "9" * 40
        wrong_approval = self.approval(wrong_ci, label="wrong-ci", issued="2026-07-13T00:08:00Z")
        with self.assertRaisesRegex(WarrantValidationError, "SHARDBLADE_CI_BINDING_MISMATCH"):
            validate_action_request(wrong_ci, wrong_approval, verifier=self.trusted, reserve_guard=ReplayLedger().consume, now=self.now)
        modified = copy.deepcopy(ready_receipt)
        modified["mutation"]["candidate_modified"] = True
        with self.assertRaises(WarrantValidationError):
            validate_action_receipt(modified, ready, ready_approval, verifier=self.trusted, receipt_guard=ReplayLedger().consume, now=self.now)
        missing_main = copy.deepcopy(merge_receipt)
        missing_main["canonical_main_sha"] = None
        with self.assertRaisesRegex(WarrantValidationError, "SHARDBLADE_SUCCESS_READBACK_MISMATCH"):
            validate_action_receipt(missing_main, merge, merge_approval, verifier=self.trusted, receipt_guard=ReplayLedger().consume, ready_request=ready, ready_approval=ready_approval, ready_receipt=ready_receipt, now=self.now)
        reused_identity = copy.deepcopy(merge_receipt)
        reused_identity["receipt_id"] = ready_receipt["receipt_id"]
        with self.assertRaisesRegex(WarrantValidationError, "SHARDBLADE_RECEIPT_IDENTITY_REUSED"):
            validate_action_receipt(reused_identity, merge, merge_approval, verifier=self.trusted, receipt_guard=ReplayLedger().consume, ready_request=ready, ready_approval=ready_approval, ready_receipt=ready_receipt, now=self.now)

    def test_request_and_receipt_replay_are_rejected(self) -> None:
        ready = self.ready_request()
        approval = self.approval(ready, label="ready", issued="2026-07-13T00:08:00Z")
        request_ledger = ReplayLedger()
        validate_action_request(ready, approval, verifier=self.trusted, reserve_guard=request_ledger.consume, now=self.now)
        with self.assertRaisesRegex(WarrantValidationError, "SHARDBLADE_REQUEST_REPLAYED"):
            validate_action_request(ready, approval, verifier=self.trusted, reserve_guard=request_ledger.consume, now=self.now)
        reused_approval = copy.deepcopy(ready)
        reused_approval.update({"request_id": "SHARDBLADE-READY-REQUEST-R02", "nonce": "shardblade-ready-request-r02"})
        self.bind_readback(reused_approval)
        relabeled = self.approval(reused_approval, label="ready", issued="2026-07-13T00:08:00Z")
        relabeled.update({"approval_id": approval["approval_id"], "nonce": approval["nonce"]})
        with self.assertRaisesRegex(WarrantValidationError, "SHARDBLADE_REQUEST_REPLAYED"):
            validate_action_request(reused_approval, relabeled, verifier=self.trusted, reserve_guard=request_ledger.consume, now=self.now)
        receipt, receipt_ledger = self.ready_receipt(ready, approval), ReplayLedger()
        validate_action_receipt(receipt, ready, approval, verifier=self.trusted, receipt_guard=receipt_ledger.consume, now=self.now)
        with self.assertRaisesRegex(WarrantValidationError, "SHARDBLADE_RECEIPT_REPLAYED"):
            validate_action_receipt(receipt, ready, approval, verifier=self.trusted, receipt_guard=receipt_ledger.consume, now=self.now)

    def test_generic_v1_permanence_is_blocked_and_accepted_v1_bytes_are_unchanged(self) -> None:
        fixtures = json.loads((ROOT / "proof/repairing-prime/rp-c02-agentic-warrant-fixtures-r01.json").read_text(encoding="utf-8"))
        legacy = copy.deepcopy(fixtures["parent"])
        legacy["scope"].update({"route": "SHARDBLADE_PERMANENCE", "actions": ["READ", "READY"]})
        legacy["authority"]["activation_record_sha256"] = None
        with self.assertRaisesRegex(WarrantValidationError, "SHARDBLADE_DEDICATED_CONTRACT_REQUIRED"):
            validate_warrant(legacy, now=self.now)
        expected = {
            "schemas/agentic-capability-warrant-v1.schema.json": "0a1888398e68e9835f9ba2db04206f95a7ef9dd2f6a23ba80e9a19b4d38949ee",
            "schemas/agentic-approval-record-v1.schema.json": "96aaaabfe781eb2b0f8a4b06e7f87b37a98b875526c4b6ca0ff80e9c28cb07ca",
            "schemas/agentic-warrant-receipt-v1.schema.json": "38e4525c4a40ac126653def7dee5bc35809a2e5e775654f1aaac9c1b96ab0989",
            "proof/repairing-prime/rp-c02-agentic-warrant-fixtures-r01.json": "3a7b0024eba3e507f6a6b429b1d5aa8ff011fc8eb196b34ed3c2e60637672e3d",
        }
        observed = {path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest() for path in expected}
        self.assertEqual(observed, expected)

    def test_doctrine_forbids_shardplate_authority_and_shardblade_construction(self) -> None:
        doctrine = " ".join((ROOT / "governance/shard-doctrine.md").read_text(encoding="utf-8").split())
        for phrase in (
            "Shardplate grants no mutation, credential, route, launcher, engine, candidate, approval, provider, Light, or permanence authority",
            "Both `READY` and `MERGE` are Shardblade actions, but they are distinct and non-substitutable",
            "READY authority never implies MERGE authority",
            "Shardblade may not author, modify, repair, widen, substitute, bypass checks",
            "Recovery is readback-only reconciliation; never a blind retry",
        ):
            self.assertIn(phrase, doctrine)


if __name__ == "__main__":
    unittest.main()
