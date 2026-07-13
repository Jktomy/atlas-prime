from __future__ import annotations

import json
import unicodedata
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable, Protocol

from tools.athena_routes.schema import SchemaValidationError, validate_schema
from tools.agentic_warrants.validator import WarrantValidationError, parse_time, protected_path, safe_path, sha256


ROOT = Path(__file__).resolve().parents[2]
REQUEST_SCHEMA = ROOT / "schemas" / "shardblade-permanence-request-v1.schema.json"
APPROVAL_SCHEMA = ROOT / "schemas" / "shardblade-permanence-approval-v1.schema.json"
RECEIPT_SCHEMA = ROOT / "schemas" / "shardblade-permanence-receipt-v1.schema.json"
MAX_APPROVAL_TTL = timedelta(hours=24)
Verifier = Callable[[dict[str, Any]], bool]
ReplayGuard = Callable[[tuple[str, ...]], bool]


class ReservationLedger(Protocol):
    """Durable adapter-owned reservation state; validation never fabricates it."""

    def reserve(self, identity: tuple[str, ...]) -> str | None: ...

    def bind_receipt(
        self, identity: tuple[str, ...], reservation_sha256: str, receipt_identity: tuple[str, ...]
    ) -> bool: ...

    def verify_receipt_binding(
        self, identity: tuple[str, ...], reservation_sha256: str, receipt_identity: tuple[str, ...]
    ) -> bool: ...


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _schema(path: Path, value: dict[str, Any], code: str) -> None:
    try:
        validate_schema(_load(path), value)
    except SchemaValidationError as exc:
        raise WarrantValidationError(code) from exc


def _pr_readback_body(request: dict[str, Any]) -> dict[str, Any]:
    return {key: request[key] for key in (
        "repository", "base_branch", "base_sha", "pull_request", "pr_state",
        "source_branch", "head_sha", "tree_sha", "changed_paths", "protected_paths",
    )}


def _request_identity(request: dict[str, Any], approval: dict[str, Any]) -> tuple[str, ...]:
    return (sha256(request), request["request_id"], request["nonce"], approval["approval_id"], approval["nonce"])


def _receipt_identity(receipt: dict[str, Any]) -> tuple[str, ...]:
    return (sha256(receipt), receipt["request_sha256"], receipt["receipt_id"], receipt["attempt_id"], receipt["nonce"])


def _validate_approval(
    approval: dict[str, Any], request: dict[str, Any], *, authority_at: datetime, verifier: Verifier
) -> None:
    _schema(APPROVAL_SCHEMA, approval, "SHARDBLADE_APPROVAL_SCHEMA_INVALID")
    expected = {
        "request_id": request["request_id"],
        "request_sha256": sha256(request),
        "action": request["action"],
        "authorizer": "Jayson",
    }
    if any(approval[key] != value for key, value in expected.items()):
        raise WarrantValidationError("SHARDBLADE_APPROVAL_BINDING_MISMATCH")
    issued, expires = parse_time(approval["issued_at"]), parse_time(approval["expires_at"])
    readback = parse_time(request["readback_at"])
    if (issued < readback or issued > authority_at or expires <= authority_at
            or issued >= expires or expires - issued > MAX_APPROVAL_TTL):
        raise WarrantValidationError("SHARDBLADE_APPROVAL_TIME_INVALID")
    if verifier is None or not verifier(approval):
        raise WarrantValidationError("SHARDBLADE_AUTHORIZER_REJECTED")


def _validate_request_core(
    request: dict[str, Any], approval: dict[str, Any], *, authority_at: datetime, verifier: Verifier,
    reservation_ledger: ReservationLedger | None = None,
    ready_request: dict[str, Any] | None = None, ready_approval: dict[str, Any] | None = None,
    ready_receipt: dict[str, Any] | None = None,
) -> None:
    _schema(REQUEST_SCHEMA, request, "SHARDBLADE_REQUEST_SCHEMA_INVALID")
    created, readback = parse_time(request["created_at"]), parse_time(request["readback_at"])
    if created > readback or readback > authority_at:
        raise WarrantValidationError("SHARDBLADE_REQUEST_TIME_INVALID")
    paths = request["changed_paths"]
    if (paths != sorted(paths) or len(paths) != len(set(paths)) or [safe_path(path) for path in paths] != paths
            or any(path != unicodedata.normalize("NFC", path) for path in paths)
            or len({path.casefold() for path in paths}) != len(paths)):
        raise WarrantValidationError("SHARDBLADE_PATH_INVENTORY_INVALID")
    if request["changed_paths_sha256"] != sha256(paths) or request["pr_readback_sha256"] != sha256(_pr_readback_body(request)):
        raise WarrantValidationError("SHARDBLADE_READBACK_DIGEST_MISMATCH")
    protected = [path for path in paths if protected_path(path)]
    if (request["protected_paths"] != protected or request["protected_paths_sha256"] != sha256(protected)
            or bool(protected) != (request["protected_construction_approval_sha256"] is not None)):
        raise WarrantValidationError("SHARDBLADE_PROTECTED_BINDING_MISMATCH")
    platforms = {item["platform"] for item in request["ci"]}
    checks = {item["check_name"] for item in request["ci"]}
    if platforms != {"UBUNTU", "WINDOWS"} or checks != {"validate (ubuntu-latest)", "validate (windows-latest)"}:
        raise WarrantValidationError("SHARDBLADE_CI_SET_INVALID")
    for item in request["ci"]:
        expected_check = "validate (ubuntu-latest)" if item["platform"] == "UBUNTU" else "validate (windows-latest)"
        if item["check_name"] != expected_check or item["head_sha"] != request["head_sha"]:
            raise WarrantValidationError("SHARDBLADE_CI_BINDING_MISMATCH")
    if len({item["workflow_source_sha"] for item in request["ci"]}) != 1:
        raise WarrantValidationError("SHARDBLADE_WORKFLOW_SOURCE_MISMATCH")
    if (request["detached_review"]["head_sha"] != request["head_sha"]
            or request["detached_review"]["reviewer_context"] == request["operator"]):
        raise WarrantValidationError("SHARDBLADE_REVIEW_BINDING_MISMATCH")
    action = request["action"]
    if action == "READY":
        if request["pr_state"] != "DRAFT" or request["prior_ready_receipt_sha256"] is not None or request["merge_method"] is not None:
            raise WarrantValidationError("SHARDBLADE_READY_REQUEST_INVALID")
        if any(item is not None for item in (ready_request, ready_approval, ready_receipt)):
            raise WarrantValidationError("SHARDBLADE_READY_CHAIN_INVALID")
    else:
        if request["pr_state"] != "OPEN_READY" or request["merge_method"] != "MERGE_COMMIT":
            raise WarrantValidationError("SHARDBLADE_MERGE_REQUEST_INVALID")
        if ready_request is None or ready_approval is None or ready_receipt is None:
            raise WarrantValidationError("SHARDBLADE_READY_RECEIPT_REQUIRED")
        _schema(RECEIPT_SCHEMA, ready_receipt, "SHARDBLADE_RECEIPT_SCHEMA_INVALID")
        ready_executed = parse_time(ready_receipt["executed_at"])
        _validate_request_core(
            ready_request, ready_approval, authority_at=ready_executed, verifier=verifier,
            reservation_ledger=reservation_ledger,
        )
        _validate_receipt_core(ready_receipt, ready_request, ready_approval, now=authority_at)
        if ready_receipt["result"] != "SUCCESS" or request["prior_ready_receipt_sha256"] != sha256(ready_receipt):
            raise WarrantValidationError("SHARDBLADE_READY_RECEIPT_MISMATCH")
        if (reservation_ledger is None or not reservation_ledger.verify_receipt_binding(
                _request_identity(ready_request, ready_approval), ready_receipt["request_reservation_sha256"],
                _receipt_identity(ready_receipt))):
            raise WarrantValidationError("SHARDBLADE_READY_RESERVATION_UNPROVEN")
        for key in (
            "repository", "base_branch", "base_sha", "pull_request", "source_branch", "head_sha", "tree_sha",
            "changed_paths", "changed_paths_sha256", "protected_paths", "protected_paths_sha256",
            "protected_construction_approval_sha256", "preview_sha256", "construction_receipt_sha256", "ci", "detached_review",
        ):
            if request[key] != ready_request[key]:
                raise WarrantValidationError("SHARDBLADE_CANDIDATE_DRIFT")
        if readback <= parse_time(ready_receipt["executed_at"]):
            raise WarrantValidationError("SHARDBLADE_FRESH_READBACK_REQUIRED")
        if request["request_id"] == ready_request["request_id"] or request["nonce"] == ready_request["nonce"]:
            raise WarrantValidationError("SHARDBLADE_REQUEST_IDENTITY_REUSED")
        if approval["approval_id"] == ready_approval["approval_id"] or approval["nonce"] == ready_approval["nonce"]:
            raise WarrantValidationError("SHARDBLADE_APPROVAL_IDENTITY_REUSED")
    _validate_approval(approval, request, authority_at=authority_at, verifier=verifier)


def validate_action_request(
    request: dict[str, Any], approval: dict[str, Any], *, verifier: Verifier,
    reservation_ledger: ReservationLedger,
    ready_request: dict[str, Any] | None = None, ready_approval: dict[str, Any] | None = None,
    ready_receipt: dict[str, Any] | None = None, now: datetime | None = None,
) -> str:
    observed_now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    _validate_request_core(
        request, approval, authority_at=observed_now, verifier=verifier, reservation_ledger=reservation_ledger,
        ready_request=ready_request, ready_approval=ready_approval, ready_receipt=ready_receipt,
    )
    if reservation_ledger is None:
        raise WarrantValidationError("SHARDBLADE_RESERVATION_LEDGER_REQUIRED")
    reservation_sha256 = reservation_ledger.reserve(_request_identity(request, approval))
    if reservation_sha256 is None:
        raise WarrantValidationError("SHARDBLADE_REQUEST_REPLAYED")
    if (not isinstance(reservation_sha256, str) or len(reservation_sha256) != 64
            or any(char not in "0123456789abcdef" for char in reservation_sha256)):
        raise WarrantValidationError("SHARDBLADE_RESERVATION_RECORD_INVALID")
    return reservation_sha256


def _validate_receipt_core(receipt: dict[str, Any], request: dict[str, Any], approval: dict[str, Any], *, now: datetime) -> None:
    _schema(RECEIPT_SCHEMA, receipt, "SHARDBLADE_RECEIPT_SCHEMA_INVALID")
    expected = {
        "request_id": request["request_id"], "request_sha256": sha256(request),
        "approval_record_sha256": sha256(approval), "action": request["action"],
        "repository": request["repository"], "pull_request": request["pull_request"],
        "base_sha": request["base_sha"], "head_sha": request["head_sha"], "tree_sha": request["tree_sha"],
        "changed_paths_sha256": request["changed_paths_sha256"],
        "prior_ready_receipt_sha256": request["prior_ready_receipt_sha256"],
    }
    if any(receipt[key] != value for key, value in expected.items()):
        raise WarrantValidationError("SHARDBLADE_RECEIPT_BINDING_MISMATCH")
    executed = parse_time(receipt["executed_at"])
    if executed < parse_time(approval["issued_at"]) or executed > now:
        raise WarrantValidationError("SHARDBLADE_RECEIPT_TIME_INVALID")
    result, mutation = receipt["result"], receipt["mutation"]
    if mutation["candidate_modified"] or mutation["head_changed"]:
        raise WarrantValidationError("SHARDBLADE_CANDIDATE_MUTATION_FORBIDDEN")
    if ((receipt["observed_head_sha"] is not None and receipt["observed_head_sha"] != request["head_sha"])
            or (receipt["observed_tree_sha"] is not None and receipt["observed_tree_sha"] != request["tree_sha"])):
        raise WarrantValidationError("SHARDBLADE_CANDIDATE_MUTATION_FORBIDDEN")
    if result == "SUCCESS":
        if receipt["error_code"] is not None or receipt["observed_head_sha"] != request["head_sha"] or receipt["observed_tree_sha"] != request["tree_sha"]:
            raise WarrantValidationError("SHARDBLADE_SUCCESS_READBACK_MISMATCH")
        if request["action"] == "READY":
            required = (
                receipt["observed_pr_state"] == "OPEN_READY" and mutation == {"ready": True, "merge": False, "candidate_modified": False, "head_changed": False}
                and receipt["merge_commit_sha"] is None and receipt["canonical_main_sha"] is None and receipt["canonical_tree_sha"] is None
                and receipt["stop_point"] == "READY_READBACK" and receipt["rollback"] == "CLOSE_PR_BEFORE_MERGE"
            )
        else:
            required = (
                receipt["observed_pr_state"] == "MERGED" and mutation == {"ready": False, "merge": True, "candidate_modified": False, "head_changed": False}
                and receipt["merge_commit_sha"] is not None and receipt["canonical_main_sha"] == receipt["merge_commit_sha"]
                and receipt["canonical_tree_sha"] == request["tree_sha"] and receipt["stop_point"] == "MERGED_MAIN_READBACK"
                and receipt["rollback"] == "REVIEWED_REVERT_PR"
            )
        if not required:
            raise WarrantValidationError("SHARDBLADE_SUCCESS_READBACK_MISMATCH")
    elif result in {"REJECTED", "BLOCKED"}:
        if (not receipt["error_code"] or any(mutation.values()) or receipt["merge_commit_sha"] is not None
                or receipt["canonical_main_sha"] is not None or receipt["canonical_tree_sha"] is not None
                or receipt["stop_point"] != "PRE_MUTATION_REJECTION" or receipt["rollback"] != "NO_MUTATION"):
            raise WarrantValidationError("SHARDBLADE_REJECTION_MISMATCH")
    else:
        if (not receipt["error_code"] or receipt["stop_point"] != "READBACK_ONLY_RECOVERY"
                or receipt["rollback"] != "PRESERVE_STATE_AND_RECONCILE"):
            raise WarrantValidationError("SHARDBLADE_PARTIAL_MISMATCH")
        action_flag, forbidden_flag = (("ready", "merge") if request["action"] == "READY" else ("merge", "ready"))
        if mutation[forbidden_flag]:
            raise WarrantValidationError("SHARDBLADE_PARTIAL_ACTION_SUBSTITUTION")
        if mutation[action_flag]:
            if request["action"] == "READY":
                observed = (
                    receipt["observed_pr_state"] == "OPEN_READY"
                    and receipt["observed_head_sha"] == request["head_sha"]
                    and receipt["observed_tree_sha"] == request["tree_sha"]
                    and all(receipt[key] is None for key in ("merge_commit_sha", "canonical_main_sha", "canonical_tree_sha"))
                )
            else:
                observed = (
                    receipt["observed_pr_state"] == "MERGED"
                    and receipt["observed_head_sha"] == request["head_sha"]
                    and receipt["observed_tree_sha"] == request["tree_sha"]
                    and receipt["merge_commit_sha"] is not None
                    and receipt["canonical_main_sha"] == receipt["merge_commit_sha"]
                    and receipt["canonical_tree_sha"] == request["tree_sha"]
                )
            if not observed:
                raise WarrantValidationError("SHARDBLADE_PARTIAL_OBSERVED_RESULT_MISMATCH")
        else:
            unknown = (
                receipt["observed_pr_state"] == "UNKNOWN"
                and all(receipt[key] is None for key in (
                    "observed_head_sha", "observed_tree_sha", "merge_commit_sha", "canonical_main_sha", "canonical_tree_sha"
                ))
            )
            unchanged_state = (
                receipt["observed_pr_state"] == request["pr_state"]
                and receipt["observed_head_sha"] == request["head_sha"]
                and receipt["observed_tree_sha"] == request["tree_sha"]
                and all(receipt[key] is None for key in ("merge_commit_sha", "canonical_main_sha", "canonical_tree_sha"))
            )
            if not (unknown or unchanged_state):
                raise WarrantValidationError("SHARDBLADE_PARTIAL_OBSERVED_RESULT_MISMATCH")


def validate_action_receipt(
    receipt: dict[str, Any], request: dict[str, Any], approval: dict[str, Any], *, verifier: Verifier,
    reservation_ledger: ReservationLedger, receipt_guard: ReplayGuard, ready_request: dict[str, Any] | None = None,
    ready_approval: dict[str, Any] | None = None, ready_receipt: dict[str, Any] | None = None,
    now: datetime | None = None,
) -> None:
    observed_now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    _schema(RECEIPT_SCHEMA, receipt, "SHARDBLADE_RECEIPT_SCHEMA_INVALID")
    executed_at = parse_time(receipt["executed_at"])
    _validate_request_core(
        request, approval, authority_at=executed_at, verifier=verifier, reservation_ledger=reservation_ledger,
        ready_request=ready_request, ready_approval=ready_approval, ready_receipt=ready_receipt,
    )
    _validate_receipt_core(receipt, request, approval, now=observed_now)
    if request["action"] == "MERGE":
        if ready_receipt is None or request["prior_ready_receipt_sha256"] != sha256(ready_receipt):
            raise WarrantValidationError("SHARDBLADE_READY_RECEIPT_REQUIRED")
        if any(receipt[key] == ready_receipt[key] for key in ("receipt_id", "attempt_id", "nonce")):
            raise WarrantValidationError("SHARDBLADE_RECEIPT_IDENTITY_REUSED")
    elif ready_receipt is not None:
        raise WarrantValidationError("SHARDBLADE_READY_CHAIN_INVALID")
    receipt_identity = _receipt_identity(receipt)
    if (reservation_ledger is None or not reservation_ledger.bind_receipt(
            _request_identity(request, approval), receipt["request_reservation_sha256"], receipt_identity)):
        raise WarrantValidationError("SHARDBLADE_REQUEST_RESERVATION_UNPROVEN")
    if receipt_guard is None or not receipt_guard(receipt_identity):
        raise WarrantValidationError("SHARDBLADE_RECEIPT_REPLAYED")
