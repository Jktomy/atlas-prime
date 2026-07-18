from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable

from tools.athena_routes.schema import SchemaValidationError, validate_schema
from tools.agentic_warrants.validator import WarrantValidationError, parse_time, safe_path, sha256


ROOT = Path(__file__).resolve().parents[2]
WARRANT_SCHEMA = ROOT / "schemas" / "shardblade-campaign-warrant-v1.schema.json"
REQUEST_SCHEMA = ROOT / "schemas" / "shardblade-campaign-stage-request-v1.schema.json"
RECEIPT_SCHEMA = ROOT / "schemas" / "shardblade-campaign-stage-receipt-v1.schema.json"
MAX_TTL = timedelta(hours=72)
TERMINAL = {"COMPLETED", "STOPPED", "REVOKED", "REPLACED"}
REQUIRED_FORBIDDEN = {
    "DIRECT_MAIN", "FORCE_PUSH", "HISTORY_REWRITE", "BLIND_RETRY",
    "WARRANT_SELF_MODIFICATION", "SCOPE_EXPANSION", "PROTECTED_DATA",
}
ReplayGuard = Callable[[tuple[str, ...]], bool]
AuthorizationVerifier = Callable[[dict[str, Any]], bool]
ReceiptVerifier = Callable[[dict[str, Any]], bool]


def _schema(path: Path, value: dict[str, Any], code: str) -> None:
    try:
        validate_schema(json.loads(path.read_text(encoding="utf-8")), value)
    except SchemaValidationError as exc:
        raise WarrantValidationError(code) from exc


def campaign_sha256(warrant: dict[str, Any]) -> str:
    return sha256(warrant)


def _canonical_paths(paths: list[str]) -> bool:
    folded = [path.casefold() for path in paths]
    return ([safe_path(path) for path in paths] == paths
            and paths == sorted(paths, key=str.casefold)
            and len(folded) == len(set(folded)))


def validate_campaign_warrant(
    warrant: dict[str, Any], *, authorization_verifier: AuthorizationVerifier | None,
    now: datetime | None = None,
) -> None:
    _schema(WARRANT_SCHEMA, warrant, "CAMPAIGN_WARRANT_SCHEMA_INVALID")
    observed = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    issued, expires = parse_time(warrant["issued_at"]), parse_time(warrant["expires_at"])
    if issued >= expires or expires - issued > MAX_TTL:
        raise WarrantValidationError("CAMPAIGN_EXPIRY_INVALID")
    if warrant["status"] == "ACTIVE" and not (issued <= observed < expires):
        raise WarrantValidationError("CAMPAIGN_INACTIVE")
    if warrant["status"] in TERMINAL:
        raise WarrantValidationError("CAMPAIGN_INACTIVE")
    if authorization_verifier is None or not authorization_verifier(warrant):
        raise WarrantValidationError("CAMPAIGN_AUTHORIZATION_REJECTED")
    if not REQUIRED_FORBIDDEN.issubset(warrant["forbidden"]):
        raise WarrantValidationError("CAMPAIGN_FORBIDDEN_SET_INVALID")
    stages = warrant["stages"]
    ids = [item["stage_id"] for item in stages]
    if ids != list(range(len(ids))) or warrant["completion_stage_id"] != ids[-1]:
        raise WarrantValidationError("CAMPAIGN_STAGE_SET_INVALID")
    if stages[0]["route"] != "AEGIS_BREAK_BOOTSTRAP" or any(item["route"] != "CAMPAIGN_SHARDBLADE" for item in stages[1:]):
        raise WarrantValidationError("CAMPAIGN_ROUTE_INVALID")
    if (stages[0]["base_source"] != "EXACT_INITIAL" or stages[0]["initial_base_sha"] is None
            or any(item["base_source"] != "PRIOR_STAGE_MERGE" or item["initial_base_sha"] is not None for item in stages[1:])):
        raise WarrantValidationError("CAMPAIGN_BASE_CHAIN_INVALID")
    for stage in stages:
        paths = stage["allowed_paths"]
        if not _canonical_paths(paths):
            raise WarrantValidationError("CAMPAIGN_PATH_INVALID")


def _stage(warrant: dict[str, Any], stage_id: int) -> dict[str, Any]:
    matches = [item for item in warrant["stages"] if item["stage_id"] == stage_id]
    if len(matches) != 1:
        raise WarrantValidationError("CAMPAIGN_STAGE_UNDECLARED")
    return matches[0]


def validate_stage_request(
    request: dict[str, Any], warrant: dict[str, Any], *,
    authorization_verifier: AuthorizationVerifier | None,
    receipt_verifier: ReceiptVerifier | None = None,
    prior_stage_merge_receipt: dict[str, Any] | None = None,
    prior_ready_receipt: dict[str, Any] | None = None, replay_guard: ReplayGuard | None = None,
    now: datetime | None = None,
) -> None:
    validate_campaign_warrant(warrant, authorization_verifier=authorization_verifier, now=now)
    _schema(REQUEST_SCHEMA, request, "CAMPAIGN_STAGE_REQUEST_SCHEMA_INVALID")
    observed = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    if request["campaign_id"] != warrant["campaign_id"] or request["campaign_sha256"] != campaign_sha256(warrant):
        raise WarrantValidationError("CAMPAIGN_BINDING_MISMATCH")
    if request["repository"] != warrant["repository"] or request["authorizer"] != warrant["authorizer"]:
        raise WarrantValidationError("CAMPAIGN_AUTHORITY_MISMATCH")
    stage = _stage(warrant, request["stage_id"])
    if request["stage_id"] == 0:
        if request["base_sha"] != stage["initial_base_sha"] or request["predecessor_merge_receipt_sha256"] is not None:
            raise WarrantValidationError("CAMPAIGN_BASE_DRIFT")
    else:
        if prior_stage_merge_receipt is None:
            raise WarrantValidationError("CAMPAIGN_PREDECESSOR_RECEIPT_REQUIRED")
        if receipt_verifier is None or not receipt_verifier(prior_stage_merge_receipt):
            raise WarrantValidationError("CAMPAIGN_RECEIPT_TRUST_REJECTED")
        validate_stage_receipt(prior_stage_merge_receipt, request=None, warrant=warrant)
        if (prior_stage_merge_receipt["action"] != "MERGE" or prior_stage_merge_receipt["result"] != "SUCCESS"
                or prior_stage_merge_receipt["stage_id"] != request["stage_id"] - 1
                or request["predecessor_merge_receipt_sha256"] != sha256(prior_stage_merge_receipt)
                or request["base_sha"] != prior_stage_merge_receipt["canonical_main_sha"]):
            raise WarrantValidationError("CAMPAIGN_BASE_DRIFT")
    paths = request["changed_paths"]
    if not _canonical_paths(paths) or not set(paths).issubset(stage["allowed_paths"]):
        raise WarrantValidationError("CAMPAIGN_SCOPE_WIDENED")
    required_checks = {"validate (ubuntu-latest)", "validate (windows-latest)"}
    if ({item["name"] for item in request["checks"]} != required_checks
            or len(request["checks"]) != len(required_checks)
            or any(item["head_sha"] != request["head_sha"] for item in request["checks"])):
        raise WarrantValidationError("CAMPAIGN_CHECK_HEAD_MISMATCH")
    if any(item["classification"] in {"ACTIONABLE", "REQUIRES_JAYSON_DECISION"} for item in request["copilot_dispositions"]):
        raise WarrantValidationError("CAMPAIGN_REVIEW_UNRESOLVED")
    created, readback = parse_time(request["created_at"]), parse_time(request["readback_at"])
    issued, expires = parse_time(warrant["issued_at"]), parse_time(warrant["expires_at"])
    if not (issued <= created <= readback <= observed < expires):
        raise WarrantValidationError("CAMPAIGN_READBACK_TIME_INVALID")
    if request["action"] == "READY":
        if request["pr_state"] != "DRAFT" or any(request[key] is not None for key in ("prior_ready_receipt_sha256", "fresh_ready_readback_sha256", "merge_method")):
            raise WarrantValidationError("CAMPAIGN_READY_REQUEST_INVALID")
    else:
        if request["pr_state"] != "OPEN_READY" or prior_ready_receipt is None:
            raise WarrantValidationError("CAMPAIGN_READY_RECEIPT_REQUIRED")
        if receipt_verifier is None or not receipt_verifier(prior_ready_receipt):
            raise WarrantValidationError("CAMPAIGN_RECEIPT_TRUST_REJECTED")
        validate_stage_receipt(prior_ready_receipt, request=None, warrant=warrant)
        if prior_ready_receipt["action"] != "READY" or prior_ready_receipt["result"] != "SUCCESS":
            raise WarrantValidationError("CAMPAIGN_READY_RECEIPT_REQUIRED")
        if request["prior_ready_receipt_sha256"] != sha256(prior_ready_receipt):
            raise WarrantValidationError("CAMPAIGN_READY_RECEIPT_MISMATCH")
        if any(request[key] != prior_ready_receipt[key] for key in ("campaign_id", "stage_id", "repository", "pull_request", "base_sha", "head_sha", "tree_sha")):
            raise WarrantValidationError("CAMPAIGN_CANDIDATE_DRIFT")
        ready_executed = parse_time(prior_ready_receipt["executed_at"])
        if (request["fresh_ready_readback_sha256"] is None or request["merge_method"] != "MERGE_COMMIT"
                or parse_time(request["created_at"]) <= ready_executed
                or parse_time(request["readback_at"]) <= ready_executed):
            raise WarrantValidationError("CAMPAIGN_FRESH_READBACK_REQUIRED")
    if replay_guard is not None and not replay_guard((request["request_id"], request["nonce"], sha256(request))):
        raise WarrantValidationError("CAMPAIGN_REQUEST_REPLAYED")


def validate_stage_receipt(
    receipt: dict[str, Any], request: dict[str, Any] | None, warrant: dict[str, Any], *,
    replay_guard: ReplayGuard | None = None, now: datetime | None = None,
) -> None:
    _schema(RECEIPT_SCHEMA, receipt, "CAMPAIGN_STAGE_RECEIPT_SCHEMA_INVALID")
    if receipt["campaign_id"] != warrant["campaign_id"] or receipt["repository"] != warrant["repository"]:
        raise WarrantValidationError("CAMPAIGN_RECEIPT_BINDING_MISMATCH")
    if receipt["warrant_status"] != warrant["status"]:
        raise WarrantValidationError("CAMPAIGN_RECEIPT_BINDING_MISMATCH")
    _stage(warrant, receipt["stage_id"])
    if request is not None:
        expected = ("request_id", "campaign_id", "stage_id", "action", "repository", "pull_request", "base_sha", "head_sha", "tree_sha")
        if receipt["request_sha256"] != sha256(request) or any(receipt[key] != request[key] for key in expected):
            raise WarrantValidationError("CAMPAIGN_RECEIPT_BINDING_MISMATCH")
        executed = parse_time(receipt["executed_at"])
        if executed < parse_time(request["readback_at"]) or (now is not None and executed > now):
            raise WarrantValidationError("CAMPAIGN_RECEIPT_TIME_INVALID")
    if receipt["result"] == "SUCCESS":
        if receipt["error_code"] is not None:
            raise WarrantValidationError("CAMPAIGN_RECEIPT_RESULT_INVALID")
        if receipt["action"] == "READY" and (receipt["observed_pr_state"] != "OPEN_READY" or receipt["merge_commit_sha"] is not None or receipt["canonical_main_sha"] is not None or receipt["rollback"] != "CLOSE_PR_BEFORE_MERGE"):
            raise WarrantValidationError("CAMPAIGN_READY_READBACK_INVALID")
        if receipt["action"] == "MERGE" and (receipt["observed_pr_state"] != "MERGED" or receipt["merge_commit_sha"] is None or receipt["canonical_main_sha"] != receipt["merge_commit_sha"] or receipt["canonical_tree_sha"] is None or receipt["rollback"] != "REVIEWED_REVERT_PR"):
            raise WarrantValidationError("CAMPAIGN_MERGE_READBACK_INVALID")
    else:
        if not receipt["error_code"]:
            raise WarrantValidationError("CAMPAIGN_RECEIPT_RESULT_INVALID")
        if (receipt["observed_pr_state"] != "UNKNOWN" or receipt["merge_commit_sha"] is not None
                or receipt["canonical_main_sha"] is not None or receipt["canonical_tree_sha"] is not None
                or receipt["rollback"] not in {"NO_MUTATION", "PRESERVE_AND_READBACK_ONLY"}):
            raise WarrantValidationError("CAMPAIGN_AMBIGUOUS_RESULT_INVALID")
    if replay_guard is not None and not replay_guard((receipt["receipt_id"], receipt["attempt_id"], receipt["nonce"], receipt["request_sha256"])):
        raise WarrantValidationError("CAMPAIGN_RECEIPT_REPLAYED")
