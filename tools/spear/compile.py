from __future__ import annotations

import re
from typing import Any

from .models import COMPILER_VERSION, EXECUTION_STATE, ContractIdentity, StateError
from .policy import validate_action, validate_content, validate_contract, validate_markdown_source_metadata, validate_path_policy, validate_scanner_category_coverage
from .validate import (
    assert_blob_sha,
    assert_no_path_collisions,
    assert_sha256_matches,
    canonical_json_bytes,
    sha256_bytes,
)

NO_AUTHORITY_STATEMENT = "This draft pull request grants no merge, deletion, migration, source-promotion, or cutover authority."
NOCTUA_STATEMENT = "Manual Noctua review and explicit Jayson approval are required before merge."


def canonical_packet_hash(packet: dict[str, Any]) -> str:
    return sha256_bytes(canonical_json_bytes(packet))


def validate_authority(packet: dict[str, Any]) -> None:
    authority = packet.get("authority", {})
    if authority.get("draft_pr_only") is not True:
        raise StateError("Spear MVP may only open draft PRs")
    if authority.get("merge_authorized") is not False:
        raise StateError("packet may not authorize merge")
    if authority.get("deletion_authorized") is not False:
        raise StateError("packet may not authorize deletion")
    if authority.get("cutover_authorized") is not False:
        raise StateError("packet may not authorize cutover")


def derive_branch(packet: dict[str, Any], canonical_sha: str, branch_regex: str) -> str:
    seed = sha256_bytes(canonical_json_bytes({"packet_id": packet["packet_id"], "canonical_packet_sha256": canonical_sha}))
    digits = f"{int(seed[:12], 16) % 100000000:08d}"
    sequence = f"{(int(seed[12:16], 16) % 999) + 1:03d}"
    branch = f"spear/{digits}-{sequence}-{seed[:8]}"
    if not re.fullmatch(branch_regex, branch):
        raise StateError("derived branch does not satisfy Prime branch policy")
    return branch


def _identity_dict(identity) -> dict[str, Any]:
    return {
        "path": identity.path,
        "repository_commit": identity.repository_commit,
        "git_blob_sha": identity.git_blob_sha,
        "sha256": identity.sha256,
        "policy_id": identity.policy_id,
        "policy_version": identity.policy_version,
    }


def contract_identity_dict(identity: ContractIdentity) -> dict[str, Any]:
    return {
        "compiler_version": identity.compiler_version,
        "schema_id": identity.schema_id,
        "schema_sha256": identity.schema_sha256,
        "overlay_policy_id": identity.overlay_policy_id,
        "overlay_policy_version": identity.overlay_policy_version,
        "overlay_policy_sha256": identity.overlay_policy_sha256,
        "destination_policy": _identity_dict(identity.destination_policy),
        "protected_policy": _identity_dict(identity.protected_policy),
        "source_metadata_schema": {
            "path": identity.source_metadata_schema.path,
            "repository_commit": identity.source_metadata_schema.repository_commit,
            "git_blob_sha": identity.source_metadata_schema.git_blob_sha,
            "raw_byte_sha256": identity.source_metadata_schema.raw_byte_sha256,
            "raw_byte_size": identity.source_metadata_schema.raw_byte_size,
            "schema_id": identity.source_metadata_schema.schema_id,
        },
    }


def compile_packet(
    packet: dict[str, Any],
    overlay_policy: dict[str, Any],
    controlling_policy: dict[str, Any],
    limits: dict[str, int],
    contract_identity: ContractIdentity,
    *,
    base_state: dict[str, str | None],
    transport_sha256: str,
    source_metadata_schema: dict[str, Any],
) -> Any:
    """Compile a validated packet into deterministic S0 artifacts without Git writes."""
    validate_contract(packet, overlay_policy, controlling_policy)
    validate_scanner_category_coverage(overlay_policy)
    validate_authority(packet)
    operations = packet["operations"]
    assert_no_path_collisions((op["path"] for op in operations), max_path_bytes=limits["max_path_bytes"])

    proposed_files: dict[str, str] = {}
    manifest_ops: list[dict[str, Any]] = []
    for index, op in enumerate(operations, start=1):
        action = op["action"]
        path = op["path"]
        content = op["content_utf8"]
        validate_action(action, overlay_policy, controlling_policy)
        validate_path_policy(path, overlay_policy, controlling_policy, limits, action=action)
        validate_content(path, content, limits)
        if path.endswith(".md"):
            validate_markdown_source_metadata(path, content, source_metadata_schema, action=action)
        assert_sha256_matches(content, op["content_sha256"])
        existing_blob = base_state.get(path)
        if action == "CREATE_FILE":
            if op.get("expected_state") != "ABSENT":
                raise StateError("CREATE_FILE requires expected_state ABSENT")
            if existing_blob is not None:
                raise StateError(f"CREATE_FILE target already exists: {path}")
            old_blob = None
        elif action == "REPLACE_FILE_FULL":
            assert_blob_sha(op["expected_blob_sha"])
            if existing_blob is None:
                raise StateError(f"REPLACE_FILE_FULL target is absent: {path}")
            if existing_blob != op["expected_blob_sha"]:
                raise StateError(f"stale blob for REPLACE_FILE_FULL target: {path}")
            old_blob = existing_blob
        else:
            raise StateError(f"unsupported action: {action}")
        proposed_files[path] = content
        manifest_ops.append(
            {
                "index": index,
                "action": action,
                "path": path,
                "old_blob_sha": old_blob,
                "expected_state": op.get("expected_state"),
                "new_content_sha256": op["content_sha256"],
                "source_type": op["source_type"],
            }
        )

    canonical_sha = canonical_packet_hash(packet)
    branch = derive_branch(packet, canonical_sha, controlling_policy["future_branch_regex"])
    identity = contract_identity_dict(contract_identity)
    common = {
        "compiler_version": COMPILER_VERSION,
        "contract_identity": identity,
        "atlas_prime_base_commit": packet["base_commit"],
        "canonical_packet_sha256": canonical_sha,
        "transport_sha256": transport_sha256,
        "execution_authorization_state": EXECUTION_STATE,
    }
    operation_manifest = {
        "manifest_version": "spear-operation-manifest-v1",
        **common,
        "packet_id": packet["packet_id"],
        "target_repository": packet["target_repository"],
        "base_branch": packet["base_branch"],
        "derived_future_branch": branch,
        "commit_message": f"Spear packet {packet['packet_id']}",
        "draft_pr_title": f"Spear: {packet['title']}",
        "operations": manifest_ops,
        "approval_basis_claim": packet["approval_basis"],
        "authenticated_execution_actor": None,
        "authentication_state": "UNVERIFIED_PACKET_CLAIM_ONLY",
        "safety_statements": [NO_AUTHORITY_STATEMENT, NOCTUA_STATEMENT],
    }
    receipt = {
        "receipt_version": "spear-validation-receipt-v1",
        **common,
        "status": "DRY_RUN_VALIDATED",
        "probationary": True,
        "packet_id": packet["packet_id"],
        "operation_count": len(manifest_ops),
        "changed_paths": [item["path"] for item in manifest_ops],
        "manifest_sha256": sha256_bytes(canonical_json_bytes(operation_manifest)),
        "proposed_tree_sha256": sha256_bytes(canonical_json_bytes(proposed_files)),
        "packet_authority_claim": packet["authority"],
        "approval_basis_claim": packet["approval_basis"],
        "authenticated_execution_actor": None,
        "authentication_state": "UNVERIFIED_PACKET_CLAIM_ONLY",
        "merge_authorized": False,
        "deletion_authorized": False,
        "cutover_authorized": False,
    }
    from .models import CompileResult
    return CompileResult(
        normalized_packet=dict(packet),
        operation_manifest=operation_manifest,
        receipt=receipt,
        proposed_files=proposed_files,
    )