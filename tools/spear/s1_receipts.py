from __future__ import annotations

import json
import re
from typing import Any

AUTHORITY = {
    "draft_pr_only": True,
    "merge_authorized": False,
    "deletion_authorized": False,
    "migration_authorized": False,
    "promotion_authorized": False,
    "cutover_authorized": False,
}

_SAFE_CODE = re.compile(r"^[A-Z0-9_]+$")
_VALID_STATES = {
    "BLOCKED_BEFORE_PLAN",
    "BLOCKED_IN_PLAN",
    "BLOCKED_BEFORE_BRANCH",
    "BLOCKED_BEFORE_PUSH",
    "BRANCH_PUSHED_PR_MISSING",
    "PR_STATE_UNCERTAIN",
    "DRAFT_PR_CREATED",
    "EXISTING_TRANSACTION_RETURNED",
    "FAILED_WITH_RECEIPT",
}
_VALID_GATES = {
    "NONE",
    "CONTEXT_VALIDATED",
    "ENVELOPE_VALIDATED",
    "PLAN_VALIDATED",
    "BASE_REVERIFIED",
    "BRANCH_CREATED",
    "COMMIT_CREATED",
    "BRANCH_PUSHED",
    "PR_REQUESTED",
    "PR_VERIFIED",
}


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def receipt_artifact_identity(run_id: str, run_attempt: str) -> tuple[str, str]:
    return f"spear-s1-receipt-{run_id}-{run_attempt}", "spear-s1-receipt.json"


def safe_code(value: object) -> str:
    text = str(value)
    if _SAFE_CODE.fullmatch(text):
        return text
    return "UNEXPECTED_EXCEPTION"


def state_for_blocker(code: str, default: str = "FAILED_WITH_RECEIPT") -> str:
    mapping = {
        "ACTOR_NOT_AUTHORIZED": "BLOCKED_BEFORE_PLAN",
        "EVENT_NOT_AUTHORIZED": "BLOCKED_BEFORE_PLAN",
        "REPOSITORY_MISMATCH": "BLOCKED_BEFORE_PLAN",
        "PACKET_IDENTITY_MISMATCH": "BLOCKED_BEFORE_PLAN",
        "PACKET_HASH_MISMATCH": "BLOCKED_BEFORE_PLAN",
        "PREVIEW_HASH_MISMATCH": "BLOCKED_IN_PLAN",
        "MANIFEST_HASH_MISMATCH": "BLOCKED_IN_PLAN",
        "APPROVAL_SCOPE_MISMATCH": "BLOCKED_IN_PLAN",
        "PLAN_EXPIRED": "BLOCKED_BEFORE_PUSH",
        "BASE_COMMIT_MISMATCH": "BLOCKED_IN_PLAN",
        "REMOTE_MAIN_ADVANCED_BEFORE_BRANCH": "BLOCKED_BEFORE_BRANCH",
        "REMOTE_MAIN_ADVANCED_BEFORE_PUSH": "BLOCKED_BEFORE_PUSH",
        "REMOTE_MAIN_ADVANCED_BEFORE_PR": "BRANCH_PUSHED_PR_MISSING",
        "PR_CREATION_UNCERTAIN": "PR_STATE_UNCERTAIN",
    }
    return mapping.get(code, default)


def bounded_receipt(
    *,
    transaction_state: str,
    last_completed_gate: str,
    blocker_codes: list[str],
    repository: str = "Jktomy/atlas-prime",
    base_branch: str = "main",
    base_commit: str | None = None,
    packet_id: str | None = None,
    packet_transport_sha256: str | None = None,
    manifest_sha256: str | None = None,
    preview_sha256: str | None = None,
    approval_reference: str | None = None,
    actor: str | None = None,
    event: str | None = None,
    workflow_sha: str | None = None,
    run_id: str = "0",
    run_attempt: str = "1",
    changed_files: list[str] | None = None,
    branch: str | None = None,
    commit_sha: str | None = None,
    tree_sha: str | None = None,
    pull_request_number: int | None = None,
    pull_request_url: str | None = None,
    validation_results: list[str] | None = None,
    warning_codes: list[str] | None = None,
    protected_scan_categories: list[str] | None = None,
    contract_identities: list[dict[str, str]] | None = None,
    file_identities: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    if transaction_state not in _VALID_STATES:
        transaction_state = "FAILED_WITH_RECEIPT"
    if last_completed_gate not in _VALID_GATES:
        last_completed_gate = "NONE"
    return {
        "receipt_version": "1.0",
        "transaction_state": transaction_state,
        "last_completed_gate": last_completed_gate,
        "repository": repository,
        "base_branch": base_branch,
        "base_commit": base_commit,
        "packet_id": packet_id,
        "packet_transport_sha256": packet_transport_sha256,
        "manifest_sha256": manifest_sha256,
        "preview_sha256": preview_sha256,
        "approval_reference": approval_reference,
        "actor": actor,
        "event": event,
        "workflow_sha": workflow_sha,
        "run_id": str(run_id),
        "run_attempt": str(run_attempt),
        "changed_files": sorted(changed_files or []),
        "branch": branch,
        "commit_sha": commit_sha,
        "tree_sha": tree_sha,
        "pull_request_number": pull_request_number,
        "pull_request_url": pull_request_url,
        "contract_identities": contract_identities or [],
        "file_identities": file_identities or [],
        "validation_results": sorted(validation_results or []),
        "warning_codes": sorted(safe_code(item) for item in (warning_codes or [])),
        "blocker_codes": sorted(set(safe_code(item) for item in blocker_codes)),
        "protected_scan_categories": sorted(set(protected_scan_categories or [])),
        "redaction_state": "PROTECTED_VALUES_REDACTED",
        "authority": dict(AUTHORITY),
    }
