from __future__ import annotations

import base64
import hashlib
import json
import re
import unicodedata
from copy import deepcopy
from datetime import datetime
from pathlib import PurePosixPath
from typing import Any, Mapping, Sequence

from tools.mission_board.core import (
    MissionError,
    normalize_changed_paths,
    resume_plan,
    validate_mission,
)


CHECKPOINT_SCHEMA = "atlas.mission-checkpoint.v1"
WORKER_SCHEMA = "atlas.mission-worker-capability.v1"
HANDOFF_SCHEMA = "atlas.mission-working-source-handoff.v1"
ROUTE_ATTEMPT_SCHEMA = "atlas.mission-route-attempt.v1"
SHA40 = re.compile(r"^[0-9a-f]{40}$")
SHA256_PREFIX = re.compile(r"^sha256:[0-9a-f]{64}$")
IDENTITY = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]{1,159}$")
STAGES = (
    "MISSION_READ",
    "CHECKPOINT",
    "SOURCE_CONSTRUCTION",
    "COMPILATION",
    "VALIDATION",
    "PUBLICATION",
    "REVIEW",
    "READY",
    "PERMANENCE",
    "CANONICAL_READBACK",
)
STAGE_CAPABILITIES = {
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
CAPABILITIES = frozenset(STAGE_CAPABILITIES.values())
ROUTE_STATES = frozenset(
    {
        "PENDING",
        "IN_PROGRESS",
        "SUCCEEDED",
        "REJECTED_CAPABILITY",
        "REJECTED_SAFETY",
        "REJECTED_AUTHORITY",
        "REJECTED_DRIFT",
        "TRANSFER_REQUIRED",
    }
)
TERMINAL_ROUTE_STATES = ROUTE_STATES - {"PENDING", "IN_PROGRESS"}
TRUE_GATE_STATES = frozenset({"REJECTED_SAFETY", "REJECTED_AUTHORITY", "REJECTED_DRIFT", "TRANSFER_REQUIRED"})
LEASE_DISPOSITIONS = frozenset({"CLAIMED", "RELEASED", "COMPLETED", "REJECTED_STALE"})
PROTECTED_PATTERNS = (
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"\bgh(?:p|o|u|s|r)_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"(?i)\b(?:api[_-]?key|access[_-]?token|password|secret)\s*[:=]\s*['\"][^'\"\r\n]{8,}['\"]"),
)


class MissionRunnerError(ValueError):
    """Fail-closed Mission relay validation error."""


def _fail(code: str, detail: str) -> None:
    raise MissionRunnerError(f"{code}: {detail}")


def _canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def _digest(value: Any) -> str:
    return f"sha256:{hashlib.sha256(_canonical_bytes(value)).hexdigest()}"


def _stable_id(prefix: str, value: Any) -> str:
    token = base64.b32encode(hashlib.sha256(_canonical_bytes(value)).digest()).decode("ascii")
    return f"{prefix}-{token.rstrip('=')[:26]}"


def _exact_keys(value: Mapping[str, Any], keys: set[str] | frozenset[str], label: str) -> None:
    missing = sorted(keys - set(value))
    unknown = sorted(set(value) - keys)
    if missing:
        _fail("MISSING_FIELDS", f"{label}: {missing}")
    if unknown:
        _fail("UNKNOWN_FIELDS", f"{label}: {unknown}")


def _text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        _fail("INVALID_FIELD", f"{label} must be nonempty text")
    return value


def _identity(value: Any, label: str) -> str:
    text = _text(value, label)
    if not IDENTITY.fullmatch(text):
        _fail("INVALID_IDENTITY", label)
    return text


def _timestamp(value: Any, label: str) -> str:
    text = _text(value, label)
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as exc:
        _fail("INVALID_TIMESTAMP", f"{label}: {exc}")
    if parsed.tzinfo is None:
        _fail("INVALID_TIMESTAMP", f"{label} must include timezone")
    return text


def _sha(value: Any, label: str, *, nullable: bool = False) -> str | None:
    if value is None and nullable:
        return None
    if not isinstance(value, str) or not SHA40.fullmatch(value):
        _fail("INVALID_SHA", label)
    return value


def _digest_value(value: Any, label: str, *, nullable: bool = False) -> str | None:
    if value is None and nullable:
        return None
    if not isinstance(value, str) or not SHA256_PREFIX.fullmatch(value):
        _fail("INVALID_DIGEST", label)
    return value


def _text_list(value: Any, label: str) -> list[str]:
    if not isinstance(value, list):
        _fail("INVALID_FIELD", f"{label} must be a list")
    result = [_text(item, f"{label}[{index}]") for index, item in enumerate(value)]
    return result


def _public_clean(value: Any, label: str = "record") -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            _public_clean(child, f"{label}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _public_clean(child, f"{label}[{index}]")
    elif isinstance(value, str):
        if any(pattern.search(value) for pattern in PROTECTED_PATTERNS):
            _fail("PROTECTED_CONTENT", label)


def validate_worker_capability(value: Mapping[str, Any]) -> dict[str, Any]:
    keys = frozenset(
        {
            "schema_version",
            "worker_id",
            "adapter_id",
            "provider",
            "surface",
            "capabilities",
            "takeover_evidence",
            "declared_at",
        }
    )
    if not isinstance(value, Mapping):
        _fail("INVALID_WORKER", "worker capability must be an object")
    _exact_keys(value, keys, "worker")
    if value["schema_version"] != WORKER_SCHEMA:
        _fail("SCHEMA_VERSION", "worker")
    for field in ("worker_id", "adapter_id", "provider", "surface"):
        _identity(value[field], field)
    capabilities = _text_list(value["capabilities"], "capabilities")
    if capabilities != sorted(set(capabilities)) or not set(capabilities).issubset(CAPABILITIES):
        _fail("INVALID_CAPABILITY", "capabilities must be sorted, unique, and closed")
    evidence = value["takeover_evidence"]
    if not isinstance(evidence, list):
        _fail("INVALID_FIELD", "takeover_evidence must be a list")
    stages: list[str] = []
    for index, item in enumerate(evidence):
        if not isinstance(item, Mapping):
            _fail("INVALID_FIELD", f"takeover_evidence[{index}]")
        _exact_keys(item, frozenset({"stage", "status", "evidence_ref"}), f"takeover_evidence[{index}]")
        if item["stage"] not in STAGES or item["status"] != "ACCEPTED":
            _fail("TAKEOVER_UNPROVEN", f"takeover_evidence[{index}]")
        _text(item["evidence_ref"], f"takeover_evidence[{index}].evidence_ref")
        stages.append(item["stage"])
    if stages != sorted(set(stages), key=STAGES.index):
        _fail("TAKEOVER_EVIDENCE_ORDER", "takeover evidence must be unique and stage ordered")
    _timestamp(value["declared_at"], "declared_at")
    _public_clean(value)
    return deepcopy(dict(value))


def match_worker_to_stage(worker: Mapping[str, Any], stage: str) -> dict[str, Any]:
    current = validate_worker_capability(worker)
    if stage not in STAGES:
        _fail("UNKNOWN_STAGE", stage)
    capability = STAGE_CAPABILITIES[stage]
    accepted = {item["stage"] for item in current["takeover_evidence"]}
    if capability not in current["capabilities"] or stage not in accepted:
        _fail("WORKER_CAPABILITY_MISMATCH", f"{current['worker_id']} cannot claim {stage}")
    return {"worker_id": current["worker_id"], "stage": stage, "capability": capability, "result": "MATCHED"}


def _checkpoint_seed(checkpoint: Mapping[str, Any]) -> dict[str, Any]:
    return {key: checkpoint[key] for key in checkpoint if key not in {"checkpoint_id", "checkpoint_digest"}}


def validate_checkpoint(value: Mapping[str, Any]) -> dict[str, Any]:
    keys = frozenset(
        {
            "schema_version",
            "checkpoint_id",
            "checkpoint_digest",
            "previous_checkpoint_digest",
            "mission_id",
            "attempt_id",
            "sequence",
            "worker_id",
            "stage",
            "observed_main_head",
            "observed_branch_head",
            "completed_work",
            "remaining_work",
            "stop_reason",
            "lease",
            "next_action",
            "created_at",
        }
    )
    if not isinstance(value, Mapping):
        _fail("INVALID_CHECKPOINT", "checkpoint must be an object")
    _exact_keys(value, keys, "checkpoint")
    if value["schema_version"] != CHECKPOINT_SCHEMA:
        _fail("SCHEMA_VERSION", "checkpoint")
    for field in ("checkpoint_id", "mission_id", "attempt_id", "worker_id"):
        _identity(value[field], field)
    _digest_value(value["checkpoint_digest"], "checkpoint_digest")
    _digest_value(value["previous_checkpoint_digest"], "previous_checkpoint_digest", nullable=True)
    if type(value["sequence"]) is not int or value["sequence"] < 1:
        _fail("INVALID_SEQUENCE", str(value["sequence"]))
    if value["stage"] not in STAGES:
        _fail("UNKNOWN_STAGE", str(value["stage"]))
    _sha(value["observed_main_head"], "observed_main_head")
    _sha(value["observed_branch_head"], "observed_branch_head", nullable=True)
    _text_list(value["completed_work"], "completed_work")
    _text_list(value["remaining_work"], "remaining_work")
    if value["stop_reason"] is not None:
        _text(value["stop_reason"], "stop_reason")
    lease = value["lease"]
    if not isinstance(lease, Mapping):
        _fail("INVALID_LEASE", "lease")
    _exact_keys(lease, frozenset({"claim_id", "disposition", "expected_previous_digest"}), "lease")
    _identity(lease["claim_id"], "lease.claim_id")
    if lease["disposition"] not in LEASE_DISPOSITIONS:
        _fail("INVALID_LEASE", "lease.disposition")
    _digest_value(lease["expected_previous_digest"], "lease.expected_previous_digest", nullable=True)
    _text(value["next_action"], "next_action")
    _timestamp(value["created_at"], "created_at")
    expected_id = _stable_id("MCP", _checkpoint_seed(value))
    expected_digest = _digest({**_checkpoint_seed(value), "checkpoint_id": expected_id})
    if value["checkpoint_id"] != expected_id or value["checkpoint_digest"] != expected_digest:
        _fail("CHECKPOINT_INTEGRITY", "checkpoint identity or digest mismatch")
    _public_clean(value)
    return deepcopy(dict(value))


def build_checkpoint(
    *,
    mission_id: str,
    attempt_id: str,
    sequence: int,
    worker_id: str,
    stage: str,
    observed_main_head: str,
    observed_branch_head: str | None,
    completed_work: Sequence[str],
    remaining_work: Sequence[str],
    stop_reason: str | None,
    claim_id: str,
    lease_disposition: str,
    next_action: str,
    created_at: str,
    previous: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    previous_value = validate_checkpoint(previous) if previous is not None else None
    if previous_value is not None:
        if previous_value["mission_id"] != mission_id or previous_value["attempt_id"] != attempt_id:
            _fail("CHECKPOINT_IDENTITY_DRIFT", "mission or attempt changed")
        if sequence != previous_value["sequence"] + 1:
            _fail("CHECKPOINT_SEQUENCE", "sequence must increment exactly once")
    elif sequence != 1:
        _fail("CHECKPOINT_SEQUENCE", "first checkpoint sequence must be 1")
    previous_digest = previous_value["checkpoint_digest"] if previous_value else None
    value: dict[str, Any] = {
        "schema_version": CHECKPOINT_SCHEMA,
        "checkpoint_id": "",
        "checkpoint_digest": "",
        "previous_checkpoint_digest": previous_digest,
        "mission_id": mission_id,
        "attempt_id": attempt_id,
        "sequence": sequence,
        "worker_id": worker_id,
        "stage": stage,
        "observed_main_head": observed_main_head,
        "observed_branch_head": observed_branch_head,
        "completed_work": list(completed_work),
        "remaining_work": list(remaining_work),
        "stop_reason": stop_reason,
        "lease": {
            "claim_id": claim_id,
            "disposition": lease_disposition,
            "expected_previous_digest": previous_digest,
        },
        "next_action": next_action,
        "created_at": created_at,
    }
    value["checkpoint_id"] = _stable_id("MCP", _checkpoint_seed(value))
    value["checkpoint_digest"] = _digest({**_checkpoint_seed(value), "checkpoint_id": value["checkpoint_id"]})
    return validate_checkpoint(value)


def validate_checkpoint_chain(values: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    if not values:
        return []
    result = [validate_checkpoint(value) for value in values]
    mission_ids = {item["mission_id"] for item in result}
    attempt_ids = {item["attempt_id"] for item in result}
    if len(mission_ids) != 1 or len(attempt_ids) != 1:
        _fail("CHECKPOINT_IDENTITY_DRIFT", "chain crosses Mission or attempt")
    for index, checkpoint in enumerate(result):
        expected_sequence = index + 1
        expected_previous = result[index - 1]["checkpoint_digest"] if index else None
        if checkpoint["sequence"] != expected_sequence or checkpoint["previous_checkpoint_digest"] != expected_previous:
            _fail("CHECKPOINT_CHAIN_BROKEN", f"sequence {checkpoint['sequence']}")
        if checkpoint["lease"]["expected_previous_digest"] != expected_previous:
            _fail("STALE_WORKER", f"sequence {checkpoint['sequence']}")
    return result


def claim_stage(
    worker: Mapping[str, Any],
    *,
    stage: str,
    claim_id: str,
    expected_checkpoint_digest: str | None,
    checkpoints: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    match = match_worker_to_stage(worker, stage)
    chain = validate_checkpoint_chain(checkpoints)
    current_digest = chain[-1]["checkpoint_digest"] if chain else None
    if expected_checkpoint_digest != current_digest:
        _fail("STALE_WORKER", "checkpoint compare-and-swap failed")
    if chain and chain[-1]["lease"]["disposition"] == "CLAIMED":
        _fail("SIMULTANEOUS_CLAIM", chain[-1]["lease"]["claim_id"])
    _identity(claim_id, "claim_id")
    return {**match, "claim_id": claim_id, "expected_checkpoint_digest": current_digest, "result": "CLAIMED"}


def _paths_digest(paths: Sequence[str]) -> str:
    return f"sha256:{hashlib.sha256((('\n'.join(paths) + '\n') if paths else '').encode()).hexdigest()}"


def validate_working_handoff(value: Mapping[str, Any]) -> dict[str, Any]:
    keys = frozenset(
        {
            "schema_version",
            "mission_id",
            "attempt_id",
            "branch",
            "base_sha",
            "expected_head",
            "changed_paths",
            "changed_paths_digest",
            "candidate_state",
            "public_clean_status",
            "force_push",
            "pull_request",
            "previous_handoff_digest",
            "handoff_digest",
        }
    )
    if not isinstance(value, Mapping):
        _fail("INVALID_HANDOFF", "handoff must be an object")
    _exact_keys(value, keys, "handoff")
    if value["schema_version"] != HANDOFF_SCHEMA:
        _fail("SCHEMA_VERSION", "handoff")
    for field in ("mission_id", "attempt_id", "branch"):
        _identity(value[field], field)
    _sha(value["base_sha"], "base_sha")
    _sha(value["expected_head"], "expected_head")
    paths = normalize_changed_paths(value["changed_paths"])
    if paths != value["changed_paths"] or value["changed_paths_digest"] != _paths_digest(paths):
        _fail("HANDOFF_PATH_BINDING", "changed paths or digest mismatch")
    if value["candidate_state"] not in {"WORKING_DRAFT", "SEALED"}:
        _fail("INVALID_HANDOFF_STATE", str(value["candidate_state"]))
    if value["public_clean_status"] != "PASS" or value["force_push"] is not False:
        _fail("UNSAFE_HANDOFF", "public-clean PASS and force_push false are required")
    if value["candidate_state"] == "WORKING_DRAFT" and value["pull_request"] is not None:
        _fail("PREMATURE_PULL_REQUEST", "WORKING_DRAFT cannot bind a pull request")
    if value["pull_request"] is not None and (type(value["pull_request"]) is not int or value["pull_request"] < 1):
        _fail("INVALID_HANDOFF", "pull_request")
    _digest_value(value["previous_handoff_digest"], "previous_handoff_digest", nullable=True)
    _digest_value(value["handoff_digest"], "handoff_digest")
    seed = {key: child for key, child in value.items() if key != "handoff_digest"}
    if value["handoff_digest"] != _digest(seed):
        _fail("HANDOFF_INTEGRITY", "handoff digest mismatch")
    _public_clean(value)
    return deepcopy(dict(value))


def build_working_handoff(
    *,
    mission_id: str,
    attempt_id: str,
    branch: str,
    base_sha: str,
    expected_head: str,
    changed_paths: Sequence[str],
    candidate_payloads: Mapping[str, bytes],
    declared_path_envelope: Sequence[str] | None = None,
    candidate_state: str,
    pull_request: int | None = None,
    previous: Mapping[str, Any] | None = None,
    observed_previous_head: str | None = None,
) -> dict[str, Any]:
    previous_value = validate_working_handoff(previous) if previous is not None else None
    if previous_value is not None:
        if observed_previous_head != previous_value["expected_head"]:
            _fail("STALE_WORKER", "working branch compare-and-swap failed")
        for field, expected in (
            ("mission_id", mission_id),
            ("attempt_id", attempt_id),
            ("branch", branch),
            ("base_sha", base_sha),
        ):
            if previous_value[field] != expected:
                _fail("HANDOFF_IDENTITY_DRIFT", field)
        if previous_value["candidate_state"] == "SEALED":
            _fail("SEALED_CANDIDATE_IMMUTABLE", "create no replacement handoff")
    paths = normalize_changed_paths(changed_paths)
    if not paths:
        _fail("EMPTY_HANDOFF", "working source requires at least one changed path")
    envelope = normalize_changed_paths(declared_path_envelope if declared_path_envelope is not None else paths)
    undeclared = sorted(set(paths) - set(envelope))
    if undeclared:
        _fail("UNDECLARED_PATH", str(undeclared))
    if not isinstance(candidate_payloads, Mapping):
        _fail("INVALID_PAYLOADS", "candidate_payloads must be a path-to-bytes object")
    payload_paths = normalize_changed_paths(candidate_payloads)
    if payload_paths != paths:
        _fail("PAYLOAD_PATH_MISMATCH", "payload paths must equal the complete changed paths")
    for path in paths:
        payload = candidate_payloads[path]
        if not isinstance(payload, bytes):
            _fail("INVALID_PAYLOADS", path)
        try:
            text = payload.decode("utf-8")
        except UnicodeDecodeError:
            _fail("NON_UTF8_PAYLOAD", path)
        _public_clean(text, f"candidate_payloads.{path}")
    value: dict[str, Any] = {
        "schema_version": HANDOFF_SCHEMA,
        "mission_id": mission_id,
        "attempt_id": attempt_id,
        "branch": branch,
        "base_sha": base_sha,
        "expected_head": expected_head,
        "changed_paths": paths,
        "changed_paths_digest": _paths_digest(paths),
        "candidate_state": candidate_state,
        "public_clean_status": "PASS",
        "force_push": False,
        "pull_request": pull_request,
        "previous_handoff_digest": previous_value["handoff_digest"] if previous_value else None,
        "handoff_digest": "",
    }
    value["handoff_digest"] = _digest({key: child for key, child in value.items() if key != "handoff_digest"})
    return validate_working_handoff(value)


def assert_single_carrier(
    *,
    branch: str,
    branch_snapshots: Sequence[Mapping[str, Any]],
    pull_request: int | None,
    pr_snapshots: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    _identity(branch, "branch")
    branches = [
        item
        for item in branch_snapshots
        if isinstance(item, Mapping) and item.get("branch") == branch and item.get("exists") is True
    ]
    if len(branches) == 0:
        _fail("WORKING_BRANCH_UNAVAILABLE", branch)
    if len(branches) > 1:
        _fail("DUPLICATE_BRANCH", branch)
    prs = [
        item
        for item in pr_snapshots
        if isinstance(item, Mapping) and item.get("branch") == branch
    ]
    if len(prs) > 1:
        _fail("DUPLICATE_PULL_REQUEST", branch)
    if pull_request is None:
        if prs:
            _fail("UNEXPECTED_PULL_REQUEST", str(prs[0].get("number")))
        return {"branch": branch, "pull_request": None, "result": "SINGLE_CARRIER"}
    if type(pull_request) is not int or pull_request < 1:
        _fail("INVALID_PULL_REQUEST", str(pull_request))
    if len(prs) != 1 or prs[0].get("number") != pull_request:
        _fail("PULL_REQUEST_UNAVAILABLE", str(pull_request))
    if prs[0].get("state") != "OPEN":
        _fail("PULL_REQUEST_UNAVAILABLE", f"PR #{pull_request} is {prs[0].get('state')}")
    return {"branch": branch, "pull_request": pull_request, "result": "SINGLE_CARRIER"}


def validate_route_attempt(value: Mapping[str, Any]) -> dict[str, Any]:
    keys = frozenset(
        {
            "schema_version",
            "route_id",
            "ordinal",
            "stage",
            "status",
            "failed_capability",
            "evidence_refs",
            "observed_head",
            "next_route_disposition",
            "attempted_at",
        }
    )
    if not isinstance(value, Mapping):
        _fail("INVALID_ROUTE_ATTEMPT", "route attempt must be an object")
    _exact_keys(value, keys, "route_attempt")
    if value["schema_version"] != ROUTE_ATTEMPT_SCHEMA:
        _fail("SCHEMA_VERSION", "route_attempt")
    _identity(value["route_id"], "route_id")
    if type(value["ordinal"]) is not int or value["ordinal"] < 1:
        _fail("INVALID_ROUTE_ORDINAL", str(value["ordinal"]))
    if value["stage"] not in STAGES and value["stage"] not in {"PREVIEW", "APPROVAL"}:
        _fail("UNKNOWN_STAGE", str(value["stage"]))
    if value["status"] not in ROUTE_STATES:
        _fail("INVALID_ROUTE_STATE", str(value["status"]))
    if value["failed_capability"] is not None:
        _text(value["failed_capability"], "failed_capability")
    if value["status"] in {"REJECTED_CAPABILITY", "REJECTED_SAFETY", "REJECTED_AUTHORITY", "REJECTED_DRIFT"} and value["failed_capability"] is None:
        _fail("ROUTE_FAILURE_UNBOUND", "rejected route requires failed_capability")
    _text_list(value["evidence_refs"], "evidence_refs")
    _sha(value["observed_head"], "observed_head", nullable=True)
    _text(value["next_route_disposition"], "next_route_disposition")
    _timestamp(value["attempted_at"], "attempted_at")
    _public_clean(value)
    return deepcopy(dict(value))


def build_route_attempt(
    *,
    route_id: str,
    ordinal: int,
    stage: str,
    status: str,
    failed_capability: str | None,
    evidence_refs: Sequence[str],
    observed_head: str | None,
    next_route_disposition: str,
    attempted_at: str,
) -> dict[str, Any]:
    return validate_route_attempt(
        {
            "schema_version": ROUTE_ATTEMPT_SCHEMA,
            "route_id": route_id,
            "ordinal": ordinal,
            "stage": stage,
            "status": status,
            "failed_capability": failed_capability,
            "evidence_refs": list(evidence_refs),
            "observed_head": observed_head,
            "next_route_disposition": next_route_disposition,
            "attempted_at": attempted_at,
        }
    )


def validate_route_attempts(
    routes: Sequence[str], attempts: Sequence[Mapping[str, Any]], *, stage: str
) -> list[dict[str, Any]]:
    if not routes or len(set(routes)) != len(routes):
        _fail("ROUTE_ORDER", "authorized routes must be nonempty and unique")
    normalized = [validate_route_attempt(item) for item in attempts]
    if len(normalized) > len(routes):
        _fail("ROUTE_LEDGER_OVERFLOW", "more attempts than authorized routes")
    for index, attempt in enumerate(normalized):
        if attempt["ordinal"] != index + 1 or attempt["route_id"] != routes[index]:
            _fail("ROUTE_ORDER", "attempt does not match authorized route order")
        if attempt["stage"] != stage:
            _fail("ROUTE_STAGE_DRIFT", f"{attempt['route_id']} belongs to {attempt['stage']}")
        if index < len(normalized) - 1 and attempt["status"] not in TERMINAL_ROUTE_STATES:
            _fail("ROUTE_NOT_TERMINAL", attempt["route_id"])
        if index < len(normalized) - 1 and attempt["status"] in TRUE_GATE_STATES:
            _fail("ROUTE_AFTER_TRUE_GATE", attempt["route_id"])
        if attempt["status"] == "SUCCEEDED" and index != len(normalized) - 1:
            _fail("ROUTE_AFTER_SUCCESS", attempt["route_id"])
    return normalized


def next_authorized_route(
    routes: Sequence[str], attempts: Sequence[Mapping[str, Any]], *, stage: str
) -> str | None:
    normalized = validate_route_attempts(routes, attempts, stage=stage)
    if normalized and normalized[-1]["status"] in TRUE_GATE_STATES | {"SUCCEEDED"}:
        return None
    if normalized and normalized[-1]["status"] not in TERMINAL_ROUTE_STATES:
        return normalized[-1]["route_id"]
    return routes[len(normalized)] if len(normalized) < len(routes) else None


def resolve_route_disposition(
    routes: Sequence[str],
    attempts: Sequence[Mapping[str, Any]],
    *,
    stage: str,
    transaction_reconciled: bool,
    boundaries_unchanged: bool,
) -> dict[str, Any]:
    if type(transaction_reconciled) is not bool or type(boundaries_unchanged) is not bool:
        _fail("INVALID_ROUTE_DISPOSITION", "reconciliation and boundary flags must be booleans")
    if stage not in STAGES and stage not in {"PREVIEW", "APPROVAL"}:
        _fail("UNKNOWN_STAGE", stage)
    normalized = validate_route_attempts(routes, attempts, stage=stage)

    def disposition(
        value: str,
        *,
        selected_route: str | None,
        mission_state: str,
        user_authorization_required: bool,
        decision_box_allowed: bool,
        basis: str,
        message_code: str,
    ) -> dict[str, Any]:
        result = {
            "disposition": value,
            "selected_route": selected_route,
            "mission_state": mission_state,
            "user_authorization_required": user_authorization_required,
            "decision_box_allowed": decision_box_allowed,
            "basis": basis,
            "message_code": message_code,
        }
        _public_clean(result, "route_disposition")
        return result

    if not transaction_reconciled:
        return disposition(
            "STOP_AT_GATE",
            selected_route=None,
            mission_state="BLOCKED_RESUMABLE",
            user_authorization_required=False,
            decision_box_allowed=False,
            basis="TRANSACTION_UNRECONCILED",
            message_code="ROUTE_RECONCILIATION_REQUIRED",
        )
    if not boundaries_unchanged:
        return disposition(
            "STOP_AT_GATE",
            selected_route=None,
            mission_state="BLOCKED_RESUMABLE",
            user_authorization_required=True,
            decision_box_allowed=True,
            basis="BOUNDARIES_CHANGED",
            message_code="ROUTE_BOUNDARY_CHANGE_REQUIRES_DECISION",
        )
    if not normalized:
        return disposition(
            "CONTINUE_CURRENT_ROUTE",
            selected_route=routes[0],
            mission_state="IN_PROGRESS",
            user_authorization_required=False,
            decision_box_allowed=False,
            basis="ROUTE_NOT_STARTED",
            message_code="ROUTE_CONTINUE_CURRENT",
        )

    latest = normalized[-1]
    status = latest["status"]
    if status in {"PENDING", "IN_PROGRESS"}:
        return disposition(
            "CONTINUE_CURRENT_ROUTE",
            selected_route=latest["route_id"],
            mission_state="IN_PROGRESS",
            user_authorization_required=False,
            decision_box_allowed=False,
            basis=status,
            message_code="ROUTE_CONTINUE_CURRENT",
        )
    if status == "SUCCEEDED":
        return disposition(
            "STAGE_COMPLETE",
            selected_route=latest["route_id"],
            mission_state="IN_PROGRESS",
            user_authorization_required=False,
            decision_box_allowed=False,
            basis="SUCCEEDED",
            message_code="ROUTE_STAGE_COMPLETE",
        )
    if status in TRUE_GATE_STATES:
        return disposition(
            "STOP_AT_GATE",
            selected_route=None,
            mission_state="BLOCKED_RESUMABLE",
            user_authorization_required=True,
            decision_box_allowed=True,
            basis=status,
            message_code="ROUTE_TRUE_GATE",
        )

    selected = next_authorized_route(routes, normalized, stage=stage)
    if status == "REJECTED_CAPABILITY" and selected is not None:
        return disposition(
            "CONTINUE_AUTOMATICALLY",
            selected_route=selected,
            mission_state="IN_PROGRESS",
            user_authorization_required=False,
            decision_box_allowed=False,
            basis="REJECTED_CAPABILITY",
            message_code="ROUTE_AUTOMATIC_FALLBACK",
        )
    if status == "REJECTED_CAPABILITY":
        blocked = assert_mission_may_block(routes, normalized, stage=stage)
        return disposition(
            "BLOCKED_RESUMABLE",
            selected_route=None,
            mission_state="BLOCKED_RESUMABLE",
            user_authorization_required=True,
            decision_box_allowed=True,
            basis=blocked["basis"],
            message_code="AUTHORIZED_ROUTES_EXHAUSTED",
        )
    _fail("INVALID_ROUTE_DISPOSITION", status)


def assert_mission_may_block(
    routes: Sequence[str],
    attempts: Sequence[Mapping[str, Any]],
    *,
    stage: str,
    true_gate: bool = False,
) -> dict[str, Any]:
    normalized = validate_route_attempts(routes, attempts, stage=stage)
    if true_gate:
        if not normalized or normalized[-1]["status"] not in TRUE_GATE_STATES:
            _fail("TRUE_GATE_UNPROVEN", "blocking gate lacks a terminal route receipt")
        return {"result": "BLOCKED_RESUMABLE", "basis": normalized[-1]["status"]}
    if len(normalized) != len(routes):
        pending = routes[len(normalized)]
        _fail("ROUTE_FALLBACK_PENDING", pending)
    if any(item["status"] not in TERMINAL_ROUTE_STATES for item in normalized):
        _fail("ROUTE_FALLBACK_PENDING", "authorized route remains nonterminal")
    if any(item["status"] == "SUCCEEDED" for item in normalized):
        _fail("ROUTE_ALREADY_SUCCEEDED", "Mission cannot block after route success")
    return {"result": "BLOCKED_RESUMABLE", "basis": "AUTHORIZED_ROUTES_EXHAUSTED"}


def assert_publication_compare_and_swap(expected_head: str, observed_head: str) -> None:
    _sha(expected_head, "expected_head")
    _sha(observed_head, "observed_head")
    if expected_head != observed_head:
        _fail("EXPECTED_HEAD_MISMATCH", f"expected {expected_head}, observed {observed_head}")


def reconstruct_attempt(
    mission: Mapping[str, Any],
    *,
    canonical_head: str,
    worker: Mapping[str, Any],
    stage: str,
    checkpoints: Sequence[Mapping[str, Any]],
    working_handoff: Mapping[str, Any] | None = None,
    branch_snapshot: Mapping[str, Any] | None = None,
    pr_snapshot: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    source_status = mission.get("canonical_source_status")
    if pr_snapshot is not None:
        pr_state = pr_snapshot.get("state")
        if source_status == "PR_OPEN" and pr_state != "OPEN":
            _fail("PULL_REQUEST_UNAVAILABLE", f"expected OPEN, observed {pr_state}")
        if source_status == "MERGED_PENDING_READBACK" and pr_state != "MERGED":
            _fail("PULL_REQUEST_UNAVAILABLE", f"expected MERGED, observed {pr_state}")
    try:
        current = validate_mission(mission)
        plan = resume_plan(current, canonical_head, pr_snapshot=pr_snapshot)
    except MissionError as exc:
        _fail("MISSION_RECONCILIATION", str(exc))
    match = match_worker_to_stage(worker, stage)
    chain = validate_checkpoint_chain(checkpoints)
    if chain:
        latest = chain[-1]
        if latest["mission_id"] != current["mission_id"] or latest["attempt_id"] != current["attempt_id"]:
            _fail("CHECKPOINT_IDENTITY_DRIFT", "checkpoint does not bind Mission")
        if latest["observed_main_head"] != canonical_head:
            _fail("CANONICAL_DRIFT", "checkpoint main head is stale")
    handoff = validate_working_handoff(working_handoff) if working_handoff is not None else None
    if handoff is not None:
        if handoff["mission_id"] != current["mission_id"] or handoff["attempt_id"] != current["attempt_id"]:
            _fail("HANDOFF_IDENTITY_DRIFT", "working source does not bind Mission")
        binding_branch = current["source_binding"]["branch"]
        if binding_branch is not None and binding_branch != handoff["branch"]:
            _fail("HANDOFF_IDENTITY_DRIFT", "Mission branch differs from handoff")
        if not isinstance(branch_snapshot, Mapping) or branch_snapshot.get("exists") is not True:
            _fail("WORKING_BRANCH_UNAVAILABLE", "linked branch is deleted or unreadable")
        observed = {
            "branch": branch_snapshot.get("branch"),
            "head_sha": branch_snapshot.get("head_sha"),
        }
        expected = {"branch": handoff["branch"], "head_sha": handoff["expected_head"]}
        if observed != expected:
            _fail("STALE_WORKER", f"expected branch {expected}, observed {observed}")
    return {
        "mission_id": current["mission_id"],
        "attempt_id": current["attempt_id"],
        "canonical_head": canonical_head,
        "worker_match": match,
        "latest_checkpoint_digest": chain[-1]["checkpoint_digest"] if chain else None,
        "working_handoff_digest": handoff["handoff_digest"] if handoff else None,
        "next_safe_action": plan["next_safe_action"],
        "result": "RECONSTRUCTED",
    }
