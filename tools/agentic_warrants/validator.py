from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any

from tools.athena_routes.schema import SchemaValidationError, validate_schema


ROOT = Path(__file__).resolve().parents[2]
WARRANT_SCHEMA = ROOT / "schemas" / "agentic-capability-warrant-v1.schema.json"
RECEIPT_SCHEMA = ROOT / "schemas" / "agentic-warrant-receipt-v1.schema.json"
TERMINAL = {"REVOKED", "EXPIRED", "REPLACED"}
ALLOWED_TRANSITIONS = {
    ("DRAFT", "ACTIVE"), ("ACTIVE", "SUSPENDED"), ("SUSPENDED", "ACTIVE"),
    ("ACTIVE", "REVOKED"), ("ACTIVE", "EXPIRED"), ("ACTIVE", "REPLACED"),
    ("SUSPENDED", "REVOKED"), ("SUSPENDED", "EXPIRED"), ("SUSPENDED", "REPLACED"),
}


class WarrantValidationError(ValueError):
    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def stable_json(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")


def warrant_sha256(warrant: dict[str, Any]) -> str:
    return hashlib.sha256(stable_json(warrant)).hexdigest()


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


def validate_warrant(warrant: dict[str, Any], *, parent: dict[str, Any] | None = None, now: datetime | None = None) -> None:
    try:
        validate_schema(load_schema(WARRANT_SCHEMA), warrant)
    except SchemaValidationError as exc:
        raise WarrantValidationError("WARRANT_SCHEMA_INVALID") from exc
    scope = warrant["scope"]
    if len(scope["actions"]) != len(set(scope["actions"])) or len(scope["paths"]) != len(set(scope["paths"])):
        raise WarrantValidationError("SCOPE_DUPLICATE")
    if [safe_path(path) for path in scope["paths"]] != scope["paths"]:
        raise WarrantValidationError("PATH_SCOPE_INVALID")
    lifecycle = warrant["lifecycle"]
    issued = parse_time(lifecycle["issued_at"])
    expires = parse_time(lifecycle["expires_at"])
    if issued >= expires:
        raise WarrantValidationError("EXPIRY_ORDER_INVALID")
    status = warrant["status"]
    required_field = {"SUSPENDED": "suspended_at", "REVOKED": "revoked_at", "REPLACED": "replaced_by"}.get(status)
    if required_field and lifecycle[required_field] is None:
        raise WarrantValidationError("LIFECYCLE_STATE_INVALID")
    if status in {"DRAFT", "ACTIVE", "EXPIRED"} and any(lifecycle[key] is not None for key in ("suspended_at", "revoked_at", "replaced_by")):
        raise WarrantValidationError("LIFECYCLE_STATE_INVALID")
    observed_now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    if status == "ACTIVE" and observed_now >= expires:
        raise WarrantValidationError("WARRANT_EXPIRED")
    approvals = warrant["human_approval"]
    action_approval = {"EXECUTE": "execute", "READY": "ready", "MERGE": "merge", "SETTINGS": "settings", "PROVIDER_ACTIVATE": "provider_activation", "DELETE": "destructive_action", "MOVE": "destructive_action"}
    if any(not approvals[field] for action, field in action_approval.items() if action in scope["actions"]):
        raise WarrantValidationError("HUMAN_APPROVAL_REQUIRED")
    if scope["protected_paths_allowed"] and not approvals["protected_action"]:
        raise WarrantValidationError("HUMAN_APPROVAL_REQUIRED")
    delegation = warrant["delegation"]
    if delegation["depth"] not in {0, 1}:
        raise WarrantValidationError("DELEGATION_DEPTH_REJECTED")
    if parent is None:
        if delegation["parent_warrant_id"] is not None or delegation["depth"] != 0:
            raise WarrantValidationError("PARENT_WARRANT_REQUIRED")
        return
    validate_warrant(parent, now=now)
    if not parent["delegation"]["allowed"] or delegation["parent_warrant_id"] != parent["warrant_id"] or delegation["depth"] != 1 or not delegation["subset_verified"]:
        raise WarrantValidationError("DELEGATION_REJECTED")
    if scope["repository"] != parent["scope"]["repository"] or scope["base_sha"] != parent["scope"]["base_sha"]:
        raise WarrantValidationError("DELEGATION_BASE_MISMATCH")
    if not set(scope["actions"]).issubset(parent["scope"]["actions"]) or not set(scope["paths"]).issubset(parent["scope"]["paths"]):
        raise WarrantValidationError("DELEGATION_SCOPE_WIDENED")
    if scope["route"] not in {parent["scope"]["route"], "READ_ONLY"}:
        raise WarrantValidationError("DELEGATION_ROUTE_WIDENED")
    if scope["protected_paths_allowed"] and not parent["scope"]["protected_paths_allowed"]:
        raise WarrantValidationError("DELEGATION_SCOPE_WIDENED")
    if expires > parse_time(parent["lifecycle"]["expires_at"]):
        raise WarrantValidationError("DELEGATION_EXPIRY_WIDENED")
    if any(parent["human_approval"][key] and not approvals[key] for key in approvals):
        raise WarrantValidationError("DELEGATION_APPROVAL_RELAXED")


def assert_transition(previous: str, current: str) -> None:
    if previous in TERMINAL or (previous, current) not in ALLOWED_TRANSITIONS:
        raise WarrantValidationError("LIFECYCLE_TRANSITION_REJECTED")


def validate_receipt(receipt: dict[str, Any], warrant: dict[str, Any], *, parent: dict[str, Any] | None = None, now: datetime | None = None) -> None:
    validate_warrant(warrant, parent=parent, now=now)
    try:
        validate_schema(load_schema(RECEIPT_SCHEMA), receipt)
    except SchemaValidationError as exc:
        raise WarrantValidationError("RECEIPT_SCHEMA_INVALID") from exc
    expected = {
        "warrant_id": warrant["warrant_id"], "warrant_sha256": warrant_sha256(warrant),
        "observed_agent_id": warrant["agent_identity"]["agent_id"],
        "observed_credential_principal": warrant["authority"]["credential_principal"],
        "repository": warrant["scope"]["repository"], "base_sha": warrant["scope"]["base_sha"], "route": warrant["scope"]["route"],
    }
    if any(receipt[key] != value for key, value in expected.items()):
        raise WarrantValidationError("RECEIPT_IDENTITY_MISMATCH")
    if not receipt["actions"] or not receipt["paths"] or not set(receipt["actions"]).issubset(warrant["scope"]["actions"]) or not set(receipt["paths"]).issubset(warrant["scope"]["paths"]):
        raise WarrantValidationError("RECEIPT_SCOPE_MISMATCH")
    if receipt["result"] == "SUCCESS" and receipt["error_code"] is not None:
        raise WarrantValidationError("RECEIPT_RESULT_MISMATCH")
    if receipt["result"] != "SUCCESS" and not receipt["error_code"]:
        raise WarrantValidationError("RECEIPT_RESULT_MISMATCH")
    approval_actions = {"EXECUTE", "READY", "MERGE", "SETTINGS", "PROVIDER_ACTIVATE", "DELETE", "MOVE"}
    if set(receipt["actions"]) & approval_actions and receipt["approval_record_sha256"] is None:
        raise WarrantValidationError("RECEIPT_APPROVAL_MISSING")
    if receipt["result"] == "SUCCESS" and warrant["status"] != "ACTIVE":
        raise WarrantValidationError("INACTIVE_WARRANT_SUCCESS")
