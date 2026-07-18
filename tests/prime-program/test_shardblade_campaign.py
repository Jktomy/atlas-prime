from __future__ import annotations

import copy
import unittest
from datetime import datetime, timezone

from tools.agentic_warrants.campaign import campaign_sha256, validate_campaign_warrant, validate_stage_receipt, validate_stage_request
from tools.agentic_warrants.validator import WarrantValidationError, sha256


class CampaignShardbladeTests(unittest.TestCase):
    now = datetime(2026, 7, 18, 18, tzinfo=timezone.utc)
    trusted = staticmethod(lambda warrant: warrant["authorization_receipt_sha256"] == "9" * 64)
    trusted_receipt = staticmethod(lambda receipt: receipt.get("candidate_unchanged") is True)

    def warrant(self) -> dict:
        return {
            "schema_version": "atlas.shardblade-campaign-warrant.v1", "campaign_id": "CAMPAIGN-LESSON-HARVEST-R02",
            "gemstone_id": "GEM-LESSON-HARVEST-R02", "authorization_receipt_sha256": "9" * 64, "authorizer": "Jayson", "repository": "Jktomy/atlas-prime",
            "issued_at": "2026-07-18T12:00:00Z", "expires_at": "2026-07-21T12:00:00Z", "status": "ACTIVE",
            "stages": [
                {"stage_id": 0, "route": "AEGIS_BREAK_BOOTSTRAP", "base_source": "EXACT_INITIAL", "initial_base_sha": "a" * 40, "allowed_paths": ["governance/atlas-aegis.md"], "actions": ["READY", "MERGE"]},
                {"stage_id": 1, "route": "CAMPAIGN_SHARDBLADE", "base_source": "PRIOR_STAGE_MERGE", "initial_base_sha": None, "allowed_paths": ["governance/lesson-harvest-protocol.md"], "actions": ["READY", "MERGE"]},
            ],
            "stop_conditions": ["DRIFT", "SCOPE_EXPANSION"], "forbidden": ["DIRECT_MAIN", "FORCE_PUSH", "HISTORY_REWRITE", "BLIND_RETRY", "WARRANT_SELF_MODIFICATION", "SCOPE_EXPANSION", "PROTECTED_DATA"],
            "completion_stage_id": 1, "no_standing_authority": True,
        }

    def request(self, warrant: dict) -> dict:
        return {
            "schema_version": "atlas.shardblade-campaign-stage-request.v1", "request_id": "CAMPAIGN-STAGE-0-READY-R01", "nonce": "campaign-stage-0-ready-r01",
            "campaign_id": warrant["campaign_id"], "campaign_sha256": campaign_sha256(warrant), "stage_id": 0, "action": "READY",
            "created_at": "2026-07-18T17:00:00Z", "readback_at": "2026-07-18T17:01:00Z", "authorizer": "Jayson", "repository": "Jktomy/atlas-prime",
            "base_sha": "a" * 40, "predecessor_merge_receipt_sha256": None, "pull_request": 240, "pr_state": "DRAFT", "source_branch": "campaign-r02-t0", "head_sha": "c" * 40, "tree_sha": "d" * 40,
            "changed_paths": ["governance/atlas-aegis.md"], "preview_sha256": "1" * 64, "construction_receipt_sha256": "2" * 64,
            "checks": [{"name": name, "head_sha": "c" * 40, "conclusion": "SUCCESS", "run_id": 1} for name in ("validate (ubuntu-latest)", "validate (windows-latest)")],
            "reviews": {"noctua": "GREEN", "ares": "GREEN", "athena": "RECONCILED", "strikeforce": "GREEN"}, "copilot_dispositions": [],
            "prior_ready_receipt_sha256": None, "fresh_ready_readback_sha256": None, "merge_method": None,
            "forbidden_actions": {"author": False, "modify": False, "widen": False, "retry_ambiguous": False, "standing_authority": False},
        }

    def receipt(self, request: dict) -> dict:
        return {
            "schema_version": "atlas.shardblade-campaign-stage-receipt.v1", "receipt_id": "CAMPAIGN-STAGE-0-READY-RECEIPT-R01", "attempt_id": "CAMPAIGN-STAGE-0-READY-ATTEMPT-R01", "nonce": "campaign-stage-0-ready-receipt-r01",
            "request_id": request["request_id"], "request_sha256": sha256(request), "campaign_id": request["campaign_id"], "stage_id": 0, "action": "READY", "executed_at": "2026-07-18T17:02:00Z",
            "result": "SUCCESS", "error_code": None, "repository": request["repository"], "pull_request": request["pull_request"], "base_sha": request["base_sha"], "head_sha": request["head_sha"], "tree_sha": request["tree_sha"],
            "observed_pr_state": "OPEN_READY", "merge_commit_sha": None, "canonical_main_sha": None, "canonical_tree_sha": None, "candidate_unchanged": True, "rollback": "CLOSE_PR_BEFORE_MERGE", "warrant_status": "ACTIVE",
        }

    def merge(self, ready: dict, receipt: dict) -> dict:
        value = copy.deepcopy(ready)
        value.update({"request_id": "CAMPAIGN-STAGE-0-MERGE-R01", "nonce": "campaign-stage-0-merge-r01", "action": "MERGE", "created_at": "2026-07-18T17:03:00Z", "readback_at": "2026-07-18T17:04:00Z", "pr_state": "OPEN_READY", "prior_ready_receipt_sha256": sha256(receipt), "fresh_ready_readback_sha256": "3" * 64, "merge_method": "MERGE_COMMIT"})
        return value

    def test_exact_ready_merge_chain(self) -> None:
        warrant, request = self.warrant(), None
        request = self.request(warrant)
        receipt = self.receipt(request)
        validate_campaign_warrant(warrant, authorization_verifier=self.trusted, now=self.now)
        validate_stage_request(request, warrant, authorization_verifier=self.trusted, now=self.now)
        validate_stage_receipt(receipt, request, warrant)
        validate_stage_request(self.merge(request, receipt), warrant, authorization_verifier=self.trusted, receipt_verifier=self.trusted_receipt, prior_ready_receipt=receipt, now=self.now)

    def test_scope_expiry_reviews_checks_and_terminal_state_fail_closed(self) -> None:
        warrant = self.warrant()
        with self.assertRaisesRegex(WarrantValidationError, "CAMPAIGN_AUTHORIZATION_REJECTED"):
            validate_campaign_warrant(warrant, authorization_verifier=None, now=self.now)
        for mutate, code in (
            (lambda value: value["stages"][0].update({"allowed_paths": ["governance/*"]}), "PATH_SCOPE_INVALID|CAMPAIGN_PATH_INVALID"),
            (lambda value: value.update({"expires_at": "2026-07-22T12:00:01Z"}), "CAMPAIGN_EXPIRY_INVALID"),
            (lambda value: value.update({"status": "COMPLETED"}), "CAMPAIGN_INACTIVE"),
        ):
            candidate = copy.deepcopy(warrant); mutate(candidate)
            with self.assertRaisesRegex(WarrantValidationError, code): validate_campaign_warrant(candidate, authorization_verifier=self.trusted, now=self.now)
        request = self.request(warrant); request["changed_paths"] = ["governance/change-routes.md"]
        with self.assertRaisesRegex(WarrantValidationError, "CAMPAIGN_SCOPE_WIDENED"): validate_stage_request(request, warrant, authorization_verifier=self.trusted, now=self.now)
        request = self.request(warrant); request.update({"created_at": "2026-07-18T17:02:00Z", "readback_at": "2026-07-18T17:01:00Z"})
        with self.assertRaisesRegex(WarrantValidationError, "CAMPAIGN_READBACK_TIME_INVALID"): validate_stage_request(request, warrant, authorization_verifier=self.trusted, now=self.now)
        request = self.request(warrant); request["changed_paths"] = ["Governance/atlas-aegis.md", "governance/atlas-aegis.md"]
        with self.assertRaisesRegex(WarrantValidationError, "CAMPAIGN_SCOPE_WIDENED"): validate_stage_request(request, warrant, authorization_verifier=self.trusted, now=self.now)
        request = self.request(warrant); request["checks"][0]["head_sha"] = "f" * 40
        with self.assertRaisesRegex(WarrantValidationError, "CAMPAIGN_CHECK_HEAD_MISMATCH"): validate_stage_request(request, warrant, authorization_verifier=self.trusted, now=self.now)
        request = self.request(warrant); request["copilot_dispositions"] = [{"id": "c1", "classification": "ACTIONABLE", "reason": "repair"}]
        with self.assertRaisesRegex(WarrantValidationError, "CAMPAIGN_REVIEW_UNRESOLVED"): validate_stage_request(request, warrant, authorization_verifier=self.trusted, now=self.now)

    def test_later_stage_base_is_bound_to_prior_verified_merge(self) -> None:
        warrant = self.warrant(); ready = self.request(warrant); prior = self.receipt(ready)
        prior.update({"action": "MERGE", "observed_pr_state": "MERGED", "merge_commit_sha": "e" * 40,
                      "canonical_main_sha": "e" * 40, "canonical_tree_sha": "f" * 40,
                      "rollback": "REVIEWED_REVERT_PR"})
        request = self.request(warrant)
        request.update({"stage_id": 1, "base_sha": "e" * 40,
                        "predecessor_merge_receipt_sha256": sha256(prior),
                        "changed_paths": ["governance/lesson-harvest-protocol.md"]})
        validate_stage_request(request, warrant, authorization_verifier=self.trusted,
                               receipt_verifier=self.trusted_receipt, prior_stage_merge_receipt=prior, now=self.now)
        request["base_sha"] = "8" * 40
        with self.assertRaisesRegex(WarrantValidationError, "CAMPAIGN_BASE_DRIFT"):
            validate_stage_request(request, warrant, authorization_verifier=self.trusted,
                                   receipt_verifier=self.trusted_receipt, prior_stage_merge_receipt=prior, now=self.now)

    def test_merge_requires_successful_ready_fresh_readback_and_exact_candidate(self) -> None:
        warrant = self.warrant(); ready = self.request(warrant); receipt = self.receipt(ready); merge = self.merge(ready, receipt)
        with self.assertRaisesRegex(WarrantValidationError, "CAMPAIGN_READY_RECEIPT_REQUIRED"): validate_stage_request(merge, warrant, authorization_verifier=self.trusted, now=self.now)
        drifted = copy.deepcopy(merge); drifted["head_sha"] = "e" * 40
        for check in drifted["checks"]: check["head_sha"] = drifted["head_sha"]
        with self.assertRaisesRegex(WarrantValidationError, "CAMPAIGN_CANDIDATE_DRIFT"): validate_stage_request(drifted, warrant, authorization_verifier=self.trusted, receipt_verifier=self.trusted_receipt, prior_ready_receipt=receipt, now=self.now)
        stale = copy.deepcopy(merge); stale["created_at"] = receipt["executed_at"]
        with self.assertRaisesRegex(WarrantValidationError, "CAMPAIGN_FRESH_READBACK_REQUIRED"): validate_stage_request(stale, warrant, authorization_verifier=self.trusted, receipt_verifier=self.trusted_receipt, prior_ready_receipt=receipt, now=self.now)

    def test_ambiguous_receipt_never_infers_success(self) -> None:
        warrant = self.warrant(); request = self.request(warrant); receipt = self.receipt(request)
        receipt.update({"result": "PARTIAL", "error_code": "AMBIGUOUS_REMOTE_RESULT", "observed_pr_state": "UNKNOWN", "rollback": "PRESERVE_AND_READBACK_ONLY"})
        validate_stage_receipt(receipt, request, warrant)
        invented = copy.deepcopy(receipt); invented.update({"result": "SUCCESS", "error_code": None, "observed_pr_state": "MERGED"})
        with self.assertRaises(WarrantValidationError): validate_stage_receipt(invented, request, warrant)
        leaked = copy.deepcopy(receipt); leaked.update({"merge_commit_sha": "f" * 40, "canonical_main_sha": "f" * 40})
        with self.assertRaisesRegex(WarrantValidationError, "CAMPAIGN_AMBIGUOUS_RESULT_INVALID"): validate_stage_receipt(leaked, request, warrant)


if __name__ == "__main__": unittest.main()
