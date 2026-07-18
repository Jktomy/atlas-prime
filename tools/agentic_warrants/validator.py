from __future__ import annotations

import copy
import fnmatch
import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Callable

from tools.athena_routes.schema import SchemaValidationError, validate_schema


ROOT = Path(__file__).resolve().parents[2]
WARRANT_SCHEMA = ROOT / "schemas" / "agentic-capability-warrant-v1.schema.json"
RECEIPT_SCHEMA = ROOT / "schemas" / "agentic-warrant-receipt-v1.schema.json"
APPROVAL_SCHEMA = ROOT / "schemas" / "agentic-approval-record-v1.schema.json"
PROTECTED_POLICY = ROOT / "policies" / "protected-paths.json"
MAX_TTL = timedelta(hours=24)
TERMINAL = {"REVOKED", "EXPIRED", "REPLACED"}
ALLOWED_TRANSITIONS = {
    ("DRAFT", "ACTIVE"), ("ACTIVE", "SUSPENDED"), ("SUSPENDED", "ACTIVE"),
    ("ACTIVE", "REVOKED"), ("ACTIVE", "EXPIRED"), ("ACTIVE", "REPLACED"),
    ("SUSPENDED", "REVOKED"), ("SUSPENDED", "EXPIRED"), ("SUSPENDED", "REPLACED"),
}
ROUTE_ACTIONS = {
    "READ_ONLY": {"READ"},
    "SPEAR_THREAD_ENGINE": {"READ", "ADD", "REPLACE", "DELETE", "EXECUTE"},
    "ARROW_BOW_THREAD_ENGINE": {"READ", "ADD", "REPLACE", "DELETE", "EXECUTE"},
    "PHOENIX_BLADE": {"READ", "ADD", "REPLACE", "DELETE", "RENAME", "MOVE"},
    "SWORD_OATHBRINGER": {"READ", "ADD", "REPLACE", "DELETE", "RENAME", "MOVE", "EXECUTE"},
    "AEGIS_BREAK_PROTECTED": {"READ", "ADD", "REPLACE", "DELETE", "RENAME", "MOVE", "EXECUTE"},
    "SHARDBLADE_PERMANENCE": {"READ", "READY", "MERGE"},
    "ADMIN_SETTINGS": {"READ", "SETTINGS"},
    "PROVIDER_GATE": {"READ", "PROVIDER_ACTIVATE"},
}
APPROVAL_ACTION = {
    "EXECUTE": "EXECUTE", "READY": "READY", "MERGE": "MERGE", "SETTINGS": "SETTINGS",
    "PROVIDER_ACTIVATE": "PROVIDER_ACTIVATE", "DELETE": "DESTRUCTIVE_ACTION", "MOVE": "DESTRUCTIVE_ACTION",
}
DEDICATED_PERMANENCE_ACTIONS = {"READY", "MERGE"}
AuthorizerVerifier = Callable[[dict[str, Any]], bool]
ReplayGuard = Callable[[str, str, str, str], bool]


class WarrantValidationError(ValueError):
    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def stable_json(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")


def sha256(value: Any) -> str:
    return hashlib.sha256(stable_json(value)).hexdigest()


def warrant_body_sha256(warrant: dict[str, Any]) -> str:
    body = copy.deepcopy(warrant)
    body["authority"]["activation_record_sha256"] = None
    return sha256(body)


def warrant_sha256(warrant: dict[str, Any]) -> str:
    return sha256(warrant)


def parse_time(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError) as exc:
        raise WarrantValidationError("TIME_INVALID") from exc
    if parsed.tzinfo is None:
        raise WarrantValidationError("TIME_INVALID")
    return parsed.astimezone(timezone.utc)


def safe_path(value: str) -> str:
    if "\\" in value or "*" in value or "?" in value or not value or value.startswith("/"):
        raise WarrantValidationError("PATH_SCOPE_INVALID")
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise WarrantValidationError("PATH_SCOPE_INVALID")
    return path.as_posix()


def load_schema(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def protected_path(path: str) -> bool:
    policy = json.loads(PROTECTED_POLICY.read_text(encoding="utf-8"))
    return any(fnmatch.fnmatchcase(path, pattern) for pattern in policy["critical_paths"])


def validate_approval_record(
    record: dict[str, Any], warrant: dict[str, Any], *, action: str, request_sha256: str,
    now: datetime, verifier: AuthorizerVerifier
) -> None:
    try:
        validate_schema(load_schema(APPROVAL_SCHEMA), record)
    except SchemaValidationError as exc:
        raise WarrantValidationError("APPROVAL_SCHEMA_INVALID") from exc
    if record["warrant_id"] != warrant["warrant_id"] or record["warrant_body_sha256"] != warrant_body_sha256(warrant):
        raise WarrantValidationError("APPROVAL_WARRANT_MISMATCH")
    if record["authorizer"] != warrant["authority"]["authorizer"] or record["action"] != action:
        raise WarrantValidationError("APPROVAL_AUTHORITY_MISMATCH")
    if record["request_sha256"] != request_sha256:
        raise WarrantValidationError("APPROVAL_REQUEST_MISMATCH")
    if record["scope_sha256"] != sha256(warrant["scope"]):
        raise WarrantValidationError("APPROVAL_SCOPE_MISMATCH")
    issued, expires = parse_time(record["issued_at"]), parse_time(record["expires_at"])
    if issued > now or expires <= now or issued >= expires or expires - issued > MAX_TTL:
        raise WarrantValidationError("APPROVAL_TIME_INVALID")
    if verifier is None or not verifier(record):
        raise WarrantValidationError("TRUSTED_AUTHORIZER_REJECTED")


def validate_lifecycle(warrant: dict[str, Any], now: datetime) -> tuple[datetime, datetime]:
    lifecycle, status = warrant["lifecycle"], warrant["status"]
    issued, expires = parse_time(lifecycle["issued_at"]), parse_time(lifecycle["expires_at"])
    if issued >= expires or expires - issued > MAX_TTL:
        raise WarrantValidationError("EXPIRY_ORDER_INVALID")
    if status != "DRAFT" and issued > now:
        raise WarrantValidationError("WARRANT_NOT_YET_VALID")
    state_fields = {key: lifecycle[key] for key in ("suspended_at", "revoked_at", "replaced_at")}
    expected = {"SUSPENDED": "suspended_at", "REVOKED": "revoked_at", "REPLACED": "replaced_at"}.get(status)
    for key, value in state_fields.items():
        if (key == expected) != (value is not None):
            raise WarrantValidationError("LIFECYCLE_STATE_INVALID")
        if value is not None:
            observed = parse_time(value)
            if observed < issued or observed > expires or observed > now:
                raise WarrantValidationError("LIFECYCLE_TIME_INVALID")
    if (status == "REPLACED") != (lifecycle["replaced_by"] is not None):
        raise WarrantValidationError("LIFECYCLE_STATE_INVALID")
    if status == "ACTIVE" and now >= expires:
        raise WarrantValidationError("WARRANT_EXPIRED")
    if status == "EXPIRED" and now < expires:
        raise WarrantValidationError("LIFECYCLE_STATE_INVALID")
    return issued, expires


def validate_warrant(
    warrant: dict[str, Any], *, activation_record: dict[str, Any] | None = None,
    verifier: AuthorizerVerifier | None = None, parent: dict[str, Any] | None = None,
    parent_activation_record: dict[str, Any] | None = None, now: datetime | None = None,
) -> None:
    try:
        validate_schema(load_schema(WARRANT_SCHEMA), warrant)
    except SchemaValidationError as exc:
        raise WarrantValidationError("WARRANT_SCHEMA_INVALID") from exc
    observed_now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    issued, expires = validate_lifecycle(warrant, observed_now)
    scope = warrant["scope"]
    if len(scope["actions"]) != len(set(scope["actions"])) or len(scope["paths"]) != len(set(scope["paths"])):
        raise WarrantValidationError("SCOPE_DUPLICATE")
    if [safe_path(path) for path in scope["paths"]] != scope["paths"]:
        raise WarrantValidationError("PATH_SCOPE_INVALID")
    if scope["route"] == "SHARDBLADE_PERMANENCE" or set(scope["actions"]) & DEDICATED_PERMANENCE_ACTIONS:
        raise WarrantValidationError("SHARDBLADE_DEDICATED_CONTRACT_REQUIRED")
    if not set(scope["actions"]).issubset(ROUTE_ACTIONS[scope["route"]]):
        raise WarrantValidationError("ROUTE_ACTION_MISMATCH")
    protected = any(protected_path(path) for path in scope["paths"])
    mutating = bool(set(scope["actions"]) - {"READ"})
    if protected and mutating and (scope["route"] != "AEGIS_BREAK_PROTECTED" or not scope["protected_paths_allowed"]):
        raise WarrantValidationError("PROTECTED_ROUTE_REQUIRED")
    if scope["protected_paths_allowed"] and not protected:
        raise WarrantValidationError("PROTECTED_SCOPE_MISMATCH")
    delegation = warrant["delegation"]
    if delegation["depth"] not in {0, 1}:
        raise WarrantValidationError("DELEGATION_DEPTH_REJECTED")
    if warrant["status"] == "ACTIVE":
        if activation_record is None or warrant["authority"]["activation_record_sha256"] != sha256(activation_record):
            raise WarrantValidationError("ACTIVATION_RECORD_REQUIRED")
        validate_approval_record(activation_record, warrant, action="ACTIVATE", request_sha256=warrant_body_sha256(warrant), now=observed_now, verifier=verifier)  # type: ignore[arg-type]
    approvals = warrant["human_approval"]
    for action, approval in APPROVAL_ACTION.items():
        if action in scope["actions"] and not approvals[approval.lower() if approval != "PROVIDER_ACTIVATE" else "provider_activation"]:
            raise WarrantValidationError("HUMAN_APPROVAL_REQUIRED")
    if protected and mutating and not approvals["protected_action"]:
        raise WarrantValidationError("HUMAN_APPROVAL_REQUIRED")
    if parent is None:
        if delegation["parent_warrant_id"] is not None or delegation["depth"] != 0:
            raise WarrantValidationError("PARENT_WARRANT_REQUIRED")
        return
    validate_warrant(parent, activation_record=parent_activation_record, verifier=verifier, now=observed_now)
    if parent["status"] != "ACTIVE" or not parent["delegation"]["allowed"]:
        raise WarrantValidationError("PARENT_WARRANT_INACTIVE")
    if delegation["parent_warrant_id"] != parent["warrant_id"] or delegation["depth"] != 1 or not delegation["subset_verified"]:
        raise WarrantValidationError("DELEGATION_REJECTED")
    if scope["repository"] != parent["scope"]["repository"] or scope["base_sha"] != parent["scope"]["base_sha"]:
        raise WarrantValidationError("DELEGATION_BASE_MISMATCH")
    if not set(scope["actions"]).issubset(parent["scope"]["actions"]) or not set(scope["paths"]).issubset(parent["scope"]["paths"]):
        raise WarrantValidationError("DELEGATION_SCOPE_WIDENED")
    if scope["route"] not in {parent["scope"]["route"], "READ_ONLY"}:
        raise WarrantValidationError("DELEGATION_ROUTE_WIDENED")
    if scope["protected_paths_allowed"] and not parent["scope"]["protected_paths_allowed"]:
        raise WarrantValidationError("DELEGATION_SCOPE_WIDENED")
    parent_issued, parent_expires = validate_lifecycle(parent, observed_now)
    if issued < parent_issued or expires > parent_expires:
        raise WarrantValidationError("DELEGATION_TIME_WIDENED")
    if any(parent["human_approval"][key] and not approvals[key] for key in approvals):
        raise WarrantValidationError("DELEGATION_APPROVAL_RELAXED")
    if not set(parent["evidence"]["required_checks"]).issubset(warrant["evidence"]["required_checks"]):
        raise WarrantValidationError("DELEGATION_EVIDENCE_RELAXED")
    if scope["route"] == "READ_ONLY":
        if scope["stop_boundary"] != "READ_ONLY_RECEIPT" or warrant["rollback"]["pre_merge"] != "NO_MUTATION" or warrant["rollback"]["post_merge"] != "NO_MUTATION":
            raise WarrantValidationError("DELEGATION_CONTROL_RELAXED")
    elif scope["stop_boundary"] != parent["scope"]["stop_boundary"] or warrant["rollback"] != parent["rollback"]:
        raise WarrantValidationError("DELEGATION_CONTROL_RELAXED")


def assert_transition(previous: str, current: str) -> None:
    if previous in TERMINAL or (previous, current) not in ALLOWED_TRANSITIONS:
        raise WarrantValidationError("LIFECYCLE_TRANSITION_REJECTED")


def validate_replacement(previous: dict[str, Any], successor: dict[str, Any]) -> None:
    try:
        validate_schema(load_schema(WARRANT_SCHEMA), previous)
        validate_schema(load_schema(WARRANT_SCHEMA), successor)
    except SchemaValidationError as exc:
        raise WarrantValidationError("WARRANT_SCHEMA_INVALID") from exc
    if (previous["warrant_id"] == successor["warrant_id"] or previous["status"] != "REPLACED"
            or previous["lifecycle"]["replaced_by"] != successor["warrant_id"]
            or successor["lifecycle"]["supersedes"] != previous["warrant_id"]):
        raise WarrantValidationError("REPLACEMENT_LINK_MISMATCH")


def validate_receipt(
    receipt: dict[str, Any], warrant: dict[str, Any], *, activation_record: dict[str, Any],
    verifier: AuthorizerVerifier, replay_guard: ReplayGuard, request_sha256: str,
    approval_records: list[dict[str, Any]] | None = None,
    parent: dict[str, Any] | None = None, parent_activation_record: dict[str, Any] | None = None,
    now: datetime | None = None,
) -> None:
    observed_now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    try:
        validate_schema(load_schema(RECEIPT_SCHEMA), receipt)
    except SchemaValidationError as exc:
        raise WarrantValidationError("RECEIPT_SCHEMA_INVALID") from exc
    warrant_error: str | None = None
    try:
        validate_warrant(warrant, activation_record=activation_record, verifier=verifier, parent=parent, parent_activation_record=parent_activation_record, now=observed_now)
        if warrant["status"] != "ACTIVE":
            warrant_error = "WARRANT_INACTIVE"
    except WarrantValidationError as exc:
        warrant_error = exc.code
    if receipt["request_sha256"] != request_sha256:
        raise WarrantValidationError("RECEIPT_REQUEST_MISMATCH")
    expected = {
        "warrant_id": warrant["warrant_id"], "warrant_sha256": warrant_sha256(warrant),
        "observed_agent_id": warrant["agent_identity"]["agent_id"], "observed_credential_principal": warrant["authority"]["credential_principal"],
        "repository": warrant["scope"]["repository"], "base_sha": warrant["scope"]["base_sha"], "route": warrant["scope"]["route"],
        "stop_point": warrant["scope"]["stop_boundary"], "preview_sha256": warrant["evidence"]["preview_sha256"],
        "candidate_tree_sha256": warrant["evidence"]["candidate_tree_sha256"], "rollback": warrant["rollback"]["pre_merge"],
    }
    if any(receipt[key] != value for key, value in expected.items()):
        raise WarrantValidationError("RECEIPT_BINDING_MISMATCH")
    if not receipt["actions"] or not receipt["paths"] or not set(receipt["actions"]).issubset(warrant["scope"]["actions"]) or not set(receipt["paths"]).issubset(warrant["scope"]["paths"]):
        raise WarrantValidationError("RECEIPT_SCOPE_MISMATCH")
    if not set(warrant["evidence"]["required_checks"]).issubset(receipt["completed_checks"]):
        raise WarrantValidationError("RECEIPT_EVIDENCE_MISMATCH")
    if receipt["evidence_sha256"] != sha256({"preview_sha256": receipt["preview_sha256"], "candidate_tree_sha256": receipt["candidate_tree_sha256"], "completed_checks": receipt["completed_checks"]}):
        raise WarrantValidationError("RECEIPT_EVIDENCE_MISMATCH")
    if parse_time(receipt["executed_at"]) > observed_now:
        raise WarrantValidationError("RECEIPT_TIME_INVALID")
    if warrant_error is not None:
        if (receipt["result"] not in {"REJECTED", "BLOCKED"} or receipt["error_code"] != warrant_error
                or receipt["head_sha"] is not None or receipt["approval_record_sha256s"]):
            raise WarrantValidationError("REJECTION_RECEIPT_MISMATCH")
        if replay_guard is None or not replay_guard(receipt["request_sha256"], receipt["receipt_id"], receipt["attempt_id"], receipt["nonce"]):
            raise WarrantValidationError("RECEIPT_REPLAYED")
        return
    required_approvals = {APPROVAL_ACTION[action] for action in receipt["actions"] if action in APPROVAL_ACTION}
    if any(protected_path(path) for path in receipt["paths"]) and set(receipt["actions"]) - {"READ"}:
        required_approvals.add("PROTECTED_ACTION")
    observed_records = approval_records or []
    if required_approvals:
        observed_hashes = [sha256(record) for record in observed_records]
        if (len(receipt["approval_record_sha256s"]) != len(set(receipt["approval_record_sha256s"]))
                or len(observed_hashes) != len(set(observed_hashes))
                or set(receipt["approval_record_sha256s"]) != set(observed_hashes)):
            raise WarrantValidationError("RECEIPT_APPROVAL_MISSING")
        observed_actions = {record.get("action") for record in observed_records}
        if observed_actions != required_approvals:
            raise WarrantValidationError("RECEIPT_APPROVAL_MISSING")
        for record in observed_records:
            validate_approval_record(record, warrant, action=record["action"], request_sha256=receipt["request_sha256"], now=observed_now, verifier=verifier)
    elif receipt["approval_record_sha256s"]:
        raise WarrantValidationError("RECEIPT_APPROVAL_MISMATCH")
    if receipt["result"] == "SUCCESS" and receipt["error_code"] is not None:
        raise WarrantValidationError("RECEIPT_RESULT_MISMATCH")
    if receipt["result"] != "SUCCESS" and not receipt["error_code"]:
        raise WarrantValidationError("RECEIPT_RESULT_MISMATCH")
    mutating = bool(set(receipt["actions"]) - {"READ"})
    if receipt["result"] == "SUCCESS" and mutating and receipt["head_sha"] is None:
        raise WarrantValidationError("RECEIPT_HEAD_REQUIRED")
    if receipt["result"] in {"REJECTED", "BLOCKED"} and receipt["head_sha"] is not None:
        raise WarrantValidationError("RECEIPT_HEAD_MISMATCH")
    if replay_guard is None or not replay_guard(receipt["request_sha256"], receipt["receipt_id"], receipt["attempt_id"], receipt["nonce"]):
        raise WarrantValidationError("RECEIPT_REPLAYED")
