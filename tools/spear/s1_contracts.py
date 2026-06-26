from __future__ import annotations

from typing import Any

from .git_adapter import blob_sha_at_commit, file_bytes_at_commit
from .models import (
    BASE_BRANCH,
    DESTINATION_POLICY_PATH,
    SPEAR_CONTRACT_ID,
    TARGET_REPOSITORY,
    PolicyError,
)
from .policy import load_controlling_policies
from .validate import load_json_bytes, sha256_bytes

ACTIVATION_POLICY_PATH = "policies/operations/spear/spear-s1-activation-v1.json"
A2_CONTRACT_PATH = "specs/spear/athenas-spear-s1-writer-contract-v1.md"
A2_CONTRACT_BLOB = "dadf1d83841d3cb6a5a0f6848be6787602ac5a51"
S1_EXECUTION_MODE = "CREATE_DRAFT_PR_ONLY"
S1_ALLOWED_EVENT = "workflow_dispatch"
S1_ALLOWED_ACTORS = ("Jktomy",)
S1_ALLOWED_OPERATIONS = frozenset({"CREATE_FILE", "REPLACE_FILE_FULL"})

_REQUIRED_POLICY_KEYS = {
    "policy_id",
    "policy_version",
    "status",
    "repository",
    "base_branch",
    "mode",
    "enabled",
    "allowed_actor_logins",
    "allowed_event",
    "execution_mode",
    "a2_contract",
    "destination_policy_contract",
    "activation_reference",
    "authority",
    "authorized_operations",
    "repository_writes_authorized",
    "note",
}
_REQUIRED_AUTHORITY = {
    "direct_main": False,
    "force_push": False,
    "merge": False,
    "auto_merge": False,
    "deletion": False,
    "migration": False,
    "promotion": False,
    "cutover": False,
}


class S1ContractError(PolicyError):
    """Raised when the disabled S1 contract or dual-activation gate is invalid."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


def _fail(code: str, message: str) -> None:
    raise S1ContractError(code, message)


def _exact_string_list(value: Any, expected: tuple[str, ...], code: str) -> None:
    if not isinstance(value, list) or tuple(value) != expected:
        _fail(code, "S1 contract list does not match its exact allowed values")


def _load_activation_policy(repository: str, base_commit: str) -> tuple[dict[str, Any], dict[str, Any]]:
    raw = file_bytes_at_commit(repository, base_commit, ACTIVATION_POLICY_PATH)
    policy = load_json_bytes(raw)
    if set(policy) != _REQUIRED_POLICY_KEYS:
        _fail("activation_policy_shape", "activation policy keys do not match the contract")
    if policy["policy_id"] != "atlas-prime-spear-s1-activation":
        _fail("activation_policy_id", "activation policy id mismatch")
    if policy["policy_version"] != "1.0.0":
        _fail("activation_policy_version", "activation policy version mismatch")
    if policy["status"] not in {"PROPOSED", "ACTIVE"}:
        _fail("activation_policy_status", "activation policy status mismatch")
    if policy["repository"] != TARGET_REPOSITORY or policy["base_branch"] != BASE_BRANCH:
        _fail("activation_repository", "activation repository or base branch mismatch")
    _exact_string_list(policy["allowed_actor_logins"], S1_ALLOWED_ACTORS, "activation_actor_allowlist")
    if policy["allowed_event"] != S1_ALLOWED_EVENT:
        _fail("activation_event", "activation event mismatch")
    if policy["execution_mode"] != S1_EXECUTION_MODE:
        _fail("activation_execution_mode", "activation execution mode mismatch")
    if policy["authority"] != _REQUIRED_AUTHORITY:
        _fail("activation_authority", "activation policy contains unexpected authority")

    a2 = policy["a2_contract"]
    if not isinstance(a2, dict) or set(a2) != {"path", "git_blob_sha"}:
        _fail("activation_a2_shape", "activation A2 contract identity is malformed")
    if a2["path"] != A2_CONTRACT_PATH or a2["git_blob_sha"] != A2_CONTRACT_BLOB:
        _fail("activation_a2_identity", "activation A2 contract identity mismatch")
    actual_a2 = blob_sha_at_commit(repository, base_commit, A2_CONTRACT_PATH)
    if actual_a2 != A2_CONTRACT_BLOB:
        _fail("activation_a2_drift", "A2 writer contract blob differs at the pinned base")

    destination = policy["destination_policy_contract"]
    if not isinstance(destination, dict) or set(destination) != {"path", "policy_id"}:
        _fail("activation_destination_shape", "destination policy identity is malformed")
    if destination["path"] != DESTINATION_POLICY_PATH:
        _fail("activation_destination_path", "destination policy path mismatch")
    if destination["policy_id"] != "atlas-prime-destination-policy":
        _fail("activation_destination_id", "destination policy id mismatch")

    blob = blob_sha_at_commit(repository, base_commit, ACTIVATION_POLICY_PATH)
    if blob is None:
        _fail("activation_policy_missing", "activation policy is missing at the pinned base")
    identity = {
        "path": ACTIVATION_POLICY_PATH,
        "repository_commit": base_commit,
        "git_blob_sha": blob,
        "sha256": sha256_bytes(raw),
        "raw_byte_size": len(raw),
        "policy_id": policy["policy_id"],
        "policy_version": policy["policy_version"],
    }
    return policy, identity


def validate_dual_activation(
    activation: dict[str, Any],
    controlling: dict[str, Any],
    *,
    require_enabled: bool,
) -> str:
    destination_authority = controlling["destination"]["authority"]
    destination_write = destination_authority.get("repository_writes_authorized")
    destination_operations = destination_authority.get("execution_authorized_operations")
    activation_operations = activation["authorized_operations"]

    if require_enabled:
        if activation["enabled"] is not True or activation["mode"] != "ACTIVATED":
            _fail("s1_disabled", "S1 activation policy is disabled")
        if activation["status"] != "ACTIVE":
            _fail("activation_status", "enabled S1 activation policy is not active")
        if controlling["destination"].get("status") != "ACTIVE":
            _fail("destination_status", "destination policy is not active for S1 execution")
        if not isinstance(activation["activation_reference"], str) or not activation["activation_reference"].strip():
            _fail("activation_reference_missing", "enabled S1 lacks an exact activation reference")
        if activation["repository_writes_authorized"] is not True:
            _fail("activation_write_authority", "activation policy does not authorize repository writes")
        if destination_write is not True:
            _fail("destination_write_authority", "destination policy does not authorize repository writes")
        if set(activation_operations) != S1_ALLOWED_OPERATIONS:
            _fail("activation_operation_authority", "activation operations do not match the S1 pilot")
        if set(destination_operations or []) != S1_ALLOWED_OPERATIONS:
            _fail("destination_operation_authority", "destination operations do not match the S1 pilot")
        if set(activation_operations) != set(destination_operations):
            _fail("dual_activation_mismatch", "activation and destination operation authority differ")
        if not S1_ALLOWED_OPERATIONS.issubset(set(controlling["registered_operations"])):
            _fail("unregistered_operation", "S1 operation is not registered by destination policy")
        if SPEAR_CONTRACT_ID not in controlling["compatible_spear_contracts"]:
            _fail("incompatible_contract", "destination policy does not accept the current Spear contract")
        return "S1_DUAL_ACTIVATION_VALIDATED"

    if activation["enabled"] is not False or activation["mode"] != "DISABLED":
        _fail("unexpected_activation", "A3a requires S1 to remain disabled")
    if activation["status"] != "PROPOSED":
        _fail("unexpected_activation_status", "disabled S1 activation policy must remain proposed")
    if controlling["destination"].get("status") != "PREVIEW":
        _fail("unexpected_destination_status", "A3a requires the destination policy to remain preview-only")
    if activation["activation_reference"] is not None:
        _fail("unexpected_activation_reference", "disabled S1 must not contain an activation reference")
    if activation["repository_writes_authorized"] is not False or activation_operations != []:
        _fail("unexpected_activation_authority", "disabled S1 must not authorize writes or operations")
    if destination_write is not False or destination_operations != []:
        _fail("unexpected_destination_authority", "A3a requires destination execution authority to remain empty")
    return "S1_DISABLED_DUAL_GATE_VALIDATED"


def load_s1_contracts(
    repository: str,
    base_commit: str,
    *,
    require_enabled: bool = False,
) -> dict[str, Any]:
    controlling = load_controlling_policies(repository, base_commit)
    activation, activation_identity = _load_activation_policy(repository, base_commit)
    state = validate_dual_activation(activation, controlling, require_enabled=require_enabled)
    return {
        "state": state,
        "activation": activation,
        "activation_identity": activation_identity,
        "destination_identity": controlling["destination_identity"],
        "protected_identity": controlling["protected_identity"],
        "controlling": controlling,
    }


def validate_execution_context(
    activation: dict[str, Any],
    *,
    actor: str,
    event: str,
    repository: str,
) -> None:
    if actor not in activation["allowed_actor_logins"]:
        _fail("actor_not_authorized", "authenticated actor is not allowed")
    if event != activation["allowed_event"]:
        _fail("event_not_authorized", "workflow event is not allowed")
    if repository != activation["repository"]:
        _fail("repository_mismatch", "workflow repository is not allowed")


def validate_packet_envelope_binding(envelope: dict[str, Any], packet: dict[str, Any]) -> None:
    if envelope.get("packet_id") != packet.get("packet_id"):
        _fail("packet_id_mismatch", "envelope packet_id differs from the packet")
    if envelope.get("expected_base_commit") != packet.get("base_commit"):
        _fail("base_commit_mismatch", "envelope base differs from the packet")
    if packet.get("target_repository") != TARGET_REPOSITORY:
        _fail("packet_repository_mismatch", "packet repository differs from Prime")
    if packet.get("base_branch") != BASE_BRANCH:
        _fail("packet_base_branch_mismatch", "packet base branch differs from main")
