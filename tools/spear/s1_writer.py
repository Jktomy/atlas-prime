from __future__ import annotations

import base64
import hashlib
import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Protocol

from .compile import compile_packet, prevalidate_operation_paths
from .models import BASE_BRANCH, COMPILER_VERSION, TARGET_REPOSITORY, ContractIdentity, SpearError, StateError
from .policy import (
    effective_limits,
    load_controlling_policies,
    load_source_metadata_schema,
    load_spear_overlay_policy,
    load_spear_packet_schema,
)
from .s1_git_adapter import S1GitAdapter, commit_spec, validate_commit_readback
from .s1_pr_client import (
    DraftPullRequestSpec,
    S1PrClient,
    build_pr_body,
    build_pr_title,
    validate_pr_readback,
)
from .s1_receipts import bounded_receipt, safe_code, state_for_blocker
from .validate import parse_json_bytes, validate_schema

S1_APPLY_HARD_DISABLED = True
ALLOWED_ACTORS = ("Jktomy",)
ALLOWED_EVENT = "workflow_dispatch"
MAX_ENVELOPE_BYTES = 1024 * 1024
MAX_DECODED_PACKET_BYTES = 1024 * 1024


def _canonical_json_bytes(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class TargetStateReader(Protocol):
    def read_target_blob(self, path: str) -> str | None: ...


@dataclass(frozen=True)
class RuntimeContext:
    actor: str
    event: str
    repository: str
    workflow_sha: str
    run_id: str
    run_attempt: str


@dataclass(frozen=True)
class S1CompileContext:
    packet_schema: dict[str, Any]
    overlay_policy: dict[str, Any]
    controlling_policy: dict[str, Any]
    limits: dict[str, int]
    contract_identity: ContractIdentity
    source_metadata_schema: dict[str, Any]
    contract_identities: tuple[dict[str, Any], ...]


@dataclass(frozen=True)
class S1Plan:
    packet: dict[str, Any]
    envelope: dict[str, Any]
    packet_bytes: bytes
    packet_sha256: str
    canonical_packet_sha256: str
    manifest_sha256: str
    preview_sha256: str
    approval_reference: str
    base_commit: str
    branch: str
    changed_paths: tuple[str, ...]
    proposed_files: dict[str, str]
    file_identities: tuple[dict[str, Any], ...]
    contract_identities: tuple[dict[str, Any], ...]
    validation_results: tuple[str, ...]
    warning_codes: tuple[str, ...]
    protected_scan_categories: tuple[str, ...]
    protected_boundary: str
    plan_timestamp: str


def _identity_record(value: Any) -> dict[str, Any]:
    record = asdict(value)
    sha256 = record.get("sha256", record.get("raw_byte_sha256"))
    return {
        "path": record["path"],
        "repository_commit": record["repository_commit"],
        "git_blob_sha": record["git_blob_sha"],
        "sha256": sha256,
    }


def load_compile_context(
    repository: str,
    base_commit: str,
    *,
    additional_contract_identities: list[dict[str, Any]] | None = None,
) -> S1CompileContext:
    packet_schema_identity, packet_schema, _ = load_spear_packet_schema(repository, base_commit)
    overlay_identity, overlay_policy, _ = load_spear_overlay_policy(repository, base_commit)
    controlling = load_controlling_policies(repository, base_commit)
    source_metadata_identity, source_metadata_schema = load_source_metadata_schema(repository, base_commit)
    limits = effective_limits(packet_schema, overlay_policy, controlling)
    contract_identity = ContractIdentity(
        compiler_version=COMPILER_VERSION,
        packet_schema=packet_schema_identity,
        overlay_policy=overlay_identity,
        destination_policy=controlling["destination_identity"],
        protected_policy=controlling["protected_identity"],
        source_metadata_schema=source_metadata_identity,
    )
    identities = [
        _identity_record(packet_schema_identity),
        _identity_record(overlay_identity),
        _identity_record(controlling["destination_identity"]),
        _identity_record(controlling["protected_identity"]),
        _identity_record(source_metadata_identity),
    ]
    for extra in additional_contract_identities or []:
        identities.append({
            "path": extra["path"],
            "repository_commit": extra["repository_commit"],
            "git_blob_sha": extra["git_blob_sha"],
            "sha256": extra["sha256"],
        })
    return S1CompileContext(
        packet_schema=packet_schema,
        overlay_policy=overlay_policy,
        controlling_policy=controlling,
        limits=limits,
        contract_identity=contract_identity,
        source_metadata_schema=source_metadata_schema,
        contract_identities=tuple(sorted(identities, key=lambda item: item["path"])),
    )


def repository_packet_identity(repository: str, packet_id: str) -> str:
    return f"{repository}+{packet_id}"


def derive_s1_branch(repository: str, packet_id: str, branch_regex: str) -> str:
    seed = _sha256_bytes(_canonical_json_bytes({"packet_id": packet_id, "target_repository": repository}))
    branch = f"spear/{int(seed[:12], 16) % 100000000:08d}-{(int(seed[12:16], 16) % 999) + 1:03d}-{seed[:8]}"
    if not re.fullmatch(branch_regex, branch):
        raise StateError("BRANCH_POLICY_MISMATCH")
    return branch


def assert_apply_enabled(*, hard_disabled: bool = S1_APPLY_HARD_DISABLED) -> None:
    if hard_disabled:
        raise StateError("S1_APPLY_DISABLED")


def validate_runtime_context(context: RuntimeContext) -> None:
    if context.actor not in ALLOWED_ACTORS:
        raise StateError("ACTOR_NOT_AUTHORIZED")
    if context.event != ALLOWED_EVENT:
        raise StateError("EVENT_NOT_AUTHORIZED")
    if context.repository != TARGET_REPOSITORY:
        raise StateError("REPOSITORY_MISMATCH")


def decode_packet_from_envelope(envelope: dict) -> tuple[dict[str, Any], bytes]:
    try:
        packet_bytes = base64.b64decode(envelope["packet_b64"], validate=True)
    except Exception as exc:
        raise StateError("PACKET_BASE64_INVALID") from exc
    actual_sha = _sha256_bytes(packet_bytes)
    if actual_sha != envelope["packet_transport_sha256"]:
        raise StateError("PACKET_HASH_MISMATCH")
    try:
        return parse_json_bytes(packet_bytes, max_bytes=MAX_DECODED_PACKET_BYTES), packet_bytes
    except SpearError as exc:
        raise StateError("PACKET_JSON_INVALID") from exc


def validate_dispatch_packet_id(dispatch_packet_id: str, envelope: dict, packet: dict) -> None:
    if dispatch_packet_id != envelope.get("packet_id") or dispatch_packet_id != packet.get("packet_id"):
        raise StateError("PACKET_IDENTITY_MISMATCH")


def verify_remote_main(observed: str, expected: str, *, stage: str) -> None:
    if observed != expected:
        if stage == "before_branch":
            raise StateError("REMOTE_MAIN_ADVANCED_BEFORE_BRANCH")
        if stage == "before_push":
            raise StateError("REMOTE_MAIN_ADVANCED_BEFORE_PUSH")
        if stage == "before_pr":
            raise StateError("REMOTE_MAIN_ADVANCED_BEFORE_PR")
        raise StateError("REMOTE_MAIN_ADVANCED")


def verify_base_in_plan(observed: str, expected: str) -> None:
    if observed != expected:
        raise StateError("BASE_COMMIT_MISMATCH")


def verify_target_blob(observed: str | None, expected: str | None) -> None:
    if observed != expected:
        raise StateError("TARGET_BLOB_MISMATCH")


def check_disallowed_capability(name: str) -> None:
    forbidden = {
        "direct_main",
        "force_push",
        "merge",
        "delete",
        "settings_mutation",
        "pr_repair",
        "workflow_self_modification",
        "packet_selected_command",
    }
    if name in forbidden:
        raise StateError("FORBIDDEN_CAPABILITY")


def _parse_datetime(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError) as exc:
        raise StateError("PLAN_TIMESTAMP_INVALID") from exc
    if parsed.tzinfo is None:
        raise StateError("PLAN_TIMESTAMP_INVALID")
    return parsed.astimezone(timezone.utc)


def validate_plan_timestamps(envelope: dict[str, Any], *, now: datetime) -> None:
    created = _parse_datetime(envelope["plan_created_at"])
    expires = _parse_datetime(envelope["plan_expires_at"])
    observed_now = now.astimezone(timezone.utc)
    if expires <= created or observed_now < created or observed_now >= expires:
        raise StateError("PLAN_EXPIRED")


def validate_preview_binding(envelope: dict[str, Any]) -> None:
    try:
        preview_bytes = base64.b64decode(envelope["preview_b64"], validate=True)
    except Exception as exc:
        raise StateError("PREVIEW_BASE64_INVALID") from exc
    if _sha256_bytes(preview_bytes) != envelope["approved_preview_sha256"]:
        raise StateError("PREVIEW_HASH_MISMATCH")
    approval = envelope["approval"]
    if approval.get("source") != "APPROVED_PREVIEW_EXECUTE" or approval.get("approved_scope") != "CREATE_DRAFT_PR_ONLY":
        raise StateError("APPROVAL_SCOPE_MISMATCH")


def validate_disabled_dual_activation(activation: dict[str, Any], destination: dict[str, Any]) -> None:
    if activation.get("enabled") is not False or activation.get("mode") != "DISABLED":
        raise StateError("DUAL_ACTIVATION_MISMATCH")
    if activation.get("repository_writes_authorized") is not False or activation.get("authorized_operations") != []:
        raise StateError("DUAL_ACTIVATION_MISMATCH")
    authority = activation.get("authority", {})
    if any(authority.get(key) is not False for key in authority):
        raise StateError("DUAL_ACTIVATION_MISMATCH")
    destination_authority = destination.get("authority", {})
    if destination_authority.get("repository_writes_authorized") is not False:
        raise StateError("DUAL_ACTIVATION_MISMATCH")
    if destination_authority.get("execution_authorized_operations") != []:
        raise StateError("DUAL_ACTIVATION_MISMATCH")


def parse_and_validate_envelope(
    envelope_bytes: bytes,
    schema: dict[str, Any],
    *,
    now: datetime,
) -> dict[str, Any]:
    try:
        envelope = parse_json_bytes(envelope_bytes, max_bytes=MAX_ENVELOPE_BYTES)
        validate_schema(envelope, schema)
    except SpearError as exc:
        raise StateError("ENVELOPE_INVALID") from exc
    validate_plan_timestamps(envelope, now=now)
    validate_preview_binding(envelope)
    return envelope


def _compile_error_code(exc: Exception) -> str:
    text = str(exc).lower()
    if "content sha-256 mismatch" in text:
        return "CONTENT_HASH_MISMATCH"
    if "protected" in text or "overlay blocks" in text or "does not allow this path" in text:
        return "PROTECTED_PATH_REJECTED"
    if "create_file target already exists" in text:
        return "CREATE_TARGET_EXISTS"
    if "stale blob" in text or "replace_file_full target is absent" in text:
        return "TARGET_BLOB_MISMATCH"
    return "S0_COMPILE_REJECTED"


def build_plan(
    *,
    dispatch_packet_id: str,
    envelope: dict[str, Any],
    branch_regex: str,
    compile_context: S1CompileContext,
    target_reader: TargetStateReader,
) -> S1Plan:
    packet, packet_bytes = decode_packet_from_envelope(envelope)
    validate_dispatch_packet_id(dispatch_packet_id, envelope, packet)
    try:
        validate_schema(packet, compile_context.packet_schema)
    except SpearError as exc:
        raise StateError("PACKET_SCHEMA_INVALID") from exc
    if packet.get("target_repository") != TARGET_REPOSITORY or packet.get("base_branch") != BASE_BRANCH:
        raise StateError("REPOSITORY_MISMATCH")
    verify_base_in_plan(packet["base_commit"], envelope["expected_base_commit"])
    try:
        operations = prevalidate_operation_paths(
            packet,
            compile_context.overlay_policy,
            compile_context.controlling_policy,
            compile_context.limits,
        )
    except Exception as exc:
        raise StateError("PATH_POLICY_REJECTED") from exc
    base_state: dict[str, str | None] = {}
    for operation in operations:
        base_state[operation["path"]] = target_reader.read_target_blob(operation["path"])
    try:
        result = compile_packet(
            packet,
            compile_context.overlay_policy,
            compile_context.controlling_policy,
            compile_context.limits,
            compile_context.contract_identity,
            base_state=base_state,
            transport_sha256=envelope["packet_transport_sha256"],
            source_metadata_schema=compile_context.source_metadata_schema,
        )
    except Exception as exc:
        raise StateError(_compile_error_code(exc)) from exc
    manifest_sha256 = result.receipt["manifest_sha256"]
    if manifest_sha256 != envelope["approved_manifest_sha256"]:
        raise StateError("MANIFEST_HASH_MISMATCH")
    branch = derive_s1_branch(TARGET_REPOSITORY, packet["packet_id"], branch_regex)
    if result.operation_manifest["derived_future_branch"] != branch:
        raise StateError("BRANCH_POLICY_MISMATCH")
    file_identities = tuple(
        {
            "action": item["action"],
            "path": item["path"],
            "old_blob_sha": item["old_blob_sha"],
            "new_content_sha256": item["new_content_sha256"],
        }
        for item in result.operation_manifest["operations"]
    )
    validation_results = (
        "APPROVAL_BINDING_VALID",
        "CONTRACT_IDENTITIES_PINNED",
        "MANIFEST_HASH_MATCH",
        "PACKET_SCHEMA_VALID",
        "PATHS_VALIDATED_BEFORE_TARGET_LOOKUP",
        "PROTECTED_BOUNDARY_PASS",
        "S0_COMPILER_VALIDATED",
        "TARGET_STATE_VALID",
    )
    return S1Plan(
        packet=result.normalized_packet,
        envelope=envelope,
        packet_bytes=packet_bytes,
        packet_sha256=envelope["packet_transport_sha256"],
        canonical_packet_sha256=result.operation_manifest["canonical_packet_sha256"],
        manifest_sha256=manifest_sha256,
        preview_sha256=envelope["approved_preview_sha256"],
        approval_reference=envelope["approval"]["reference"],
        base_commit=envelope["expected_base_commit"],
        branch=branch,
        changed_paths=tuple(sorted(result.proposed_files)),
        proposed_files=dict(result.proposed_files),
        file_identities=file_identities,
        contract_identities=compile_context.contract_identities,
        validation_results=validation_results,
        warning_codes=(),
        protected_scan_categories=(),
        protected_boundary="PASS",
        plan_timestamp=envelope["plan_created_at"],
    )


def _receipt_for_error(context: RuntimeContext, plan: S1Plan | None, code: str, gate: str) -> dict[str, Any]:
    return bounded_receipt(
        transaction_state=state_for_blocker(code),
        last_completed_gate=gate,
        blocker_codes=[code],
        repository=context.repository,
        base_commit=plan.base_commit if plan else None,
        packet_id=plan.packet["packet_id"] if plan else None,
        packet_transport_sha256=plan.packet_sha256 if plan else None,
        manifest_sha256=plan.manifest_sha256 if plan else None,
        preview_sha256=plan.preview_sha256 if plan else None,
        approval_reference=plan.approval_reference if plan else None,
        actor=context.actor,
        event=context.event,
        workflow_sha=context.workflow_sha,
        run_id=context.run_id,
        run_attempt=context.run_attempt,
        changed_files=list(plan.changed_paths) if plan else [],
        branch=plan.branch if plan else None,
        validation_results=list(plan.validation_results) if plan else [],
        warning_codes=list(plan.warning_codes) if plan else [],
        protected_scan_categories=list(plan.protected_scan_categories) if plan else [],
        contract_identities=list(plan.contract_identities) if plan else [],
        file_identities=list(plan.file_identities) if plan else [],
    )


def _receipt_success(
    *,
    context: RuntimeContext,
    plan: S1Plan,
    state: str,
    commit_sha: str,
    tree_sha: str,
    pr_number: int,
    pr_url: str,
) -> dict[str, Any]:
    return bounded_receipt(
        transaction_state=state,
        last_completed_gate="PR_VERIFIED",
        blocker_codes=[],
        repository=context.repository,
        base_commit=plan.base_commit,
        packet_id=plan.packet["packet_id"],
        packet_transport_sha256=plan.packet_sha256,
        manifest_sha256=plan.manifest_sha256,
        preview_sha256=plan.preview_sha256,
        approval_reference=plan.approval_reference,
        actor=context.actor,
        event=context.event,
        workflow_sha=context.workflow_sha,
        run_id=context.run_id,
        run_attempt=context.run_attempt,
        changed_files=list(plan.changed_paths),
        branch=plan.branch,
        commit_sha=commit_sha,
        tree_sha=tree_sha,
        pull_request_number=pr_number,
        pull_request_url=pr_url,
        validation_results=list(plan.validation_results),
        warning_codes=list(plan.warning_codes),
        protected_scan_categories=list(plan.protected_scan_categories),
        contract_identities=list(plan.contract_identities),
        file_identities=list(plan.file_identities),
    )


def _commit_spec(plan: S1Plan, tree_sha: str):
    return commit_spec(
        title=plan.packet["title"],
        packet_id=plan.packet["packet_id"],
        packet_sha256=plan.packet_sha256,
        manifest_sha256=plan.manifest_sha256,
        preview_sha256=plan.preview_sha256,
        parent=plan.base_commit,
        tree_sha=tree_sha,
        changed_paths=list(plan.changed_paths),
        plan_timestamp=plan.plan_timestamp,
    )


def _pr_spec(context: RuntimeContext, plan: S1Plan, commit_sha: str) -> DraftPullRequestSpec:
    return DraftPullRequestSpec(
        title=build_pr_title(plan.packet),
        body=build_pr_body(
            packet=plan.packet,
            branch=plan.branch,
            commit_sha=commit_sha,
            manifest_sha256=plan.manifest_sha256,
            preview_sha256=plan.preview_sha256,
            transport_sha256=plan.packet_sha256,
            approval_reference=plan.approval_reference,
            changed_paths=list(plan.changed_paths),
            contract_identities=list(plan.contract_identities),
            file_identities=list(plan.file_identities),
            validation_results=list(plan.validation_results),
            warning_codes=list(plan.warning_codes),
            protected_boundary=plan.protected_boundary,
            actor=context.actor,
            event=context.event,
            workflow_sha=context.workflow_sha,
            run_id=context.run_id,
            run_attempt=context.run_attempt,
            repository=context.repository,
        ),
        base=BASE_BRANCH,
        head=plan.branch,
        head_sha=commit_sha,
    )


def _revalidate_target_state(plan: S1Plan, git: S1GitAdapter) -> None:
    expected_by_path = {item["path"]: item["old_blob_sha"] for item in plan.file_identities}
    for path in plan.changed_paths:
        verify_target_blob(git.read_target_blob(path), expected_by_path[path])


def run_disabled_transaction(
    *,
    context: RuntimeContext,
    plan: S1Plan,
    git: S1GitAdapter,
    pr: S1PrClient,
    hard_disabled: bool = True,
    now: datetime,
) -> dict[str, Any]:
    gate = "PLAN_VALIDATED"
    try:
        validate_runtime_context(context)
        gate = "CONTEXT_VALIDATED"
        validate_plan_timestamps(plan.envelope, now=now)
        verify_remote_main(git.read_remote_main(), plan.base_commit, stage="before_branch")
        _revalidate_target_state(plan, git)
        gate = "BASE_REVERIFIED"
        assert_apply_enabled(hard_disabled=hard_disabled)

        blobs = {path: git.create_blob(path, content) for path, content in sorted(plan.proposed_files.items())}
        tree_sha = git.create_complete_tree(plan.base_commit, blobs)
        expected_commit = _commit_spec(plan, tree_sha)
        existing_branch = git.read_branch_ref(plan.branch)

        if existing_branch is not None:
            readback = git.read_commit_and_changed_paths(existing_branch)
            try:
                validate_commit_readback(readback, expected_commit)
            except StateError as exc:
                raise StateError("PACKET_ID_REUSE_COLLISION") from exc
            expected_pr = _pr_spec(context, plan, existing_branch)
            existing_pr = pr.find_open_draft_pr_for_branch(plan.branch)
            if existing_pr is not None:
                validate_pr_readback(existing_pr, expected_pr)
                return _receipt_success(
                    context=context,
                    plan=plan,
                    state="EXISTING_TRANSACTION_RETURNED",
                    commit_sha=existing_branch,
                    tree_sha=tree_sha,
                    pr_number=existing_pr.number,
                    pr_url=existing_pr.url,
                )
            verify_remote_main(git.read_remote_main(), plan.base_commit, stage="before_pr")
            if not pr.establish_definite_absence(plan.branch):
                raise StateError("PR_CREATION_UNCERTAIN")
            created = pr.create_draft_pr(expected_pr)
            gate = "PR_REQUESTED"
            read_pr = pr.read_pull_request(created.number)
            validate_pr_readback(read_pr, expected_pr)
            return _receipt_success(
                context=context,
                plan=plan,
                state="DRAFT_PR_CREATED",
                commit_sha=existing_branch,
                tree_sha=tree_sha,
                pr_number=read_pr.number,
                pr_url=read_pr.url,
            )

        verify_remote_main(git.read_remote_main(), plan.base_commit, stage="before_push")
        commit_sha = git.create_exact_single_parent_commit(expected_commit)
        gate = "COMMIT_CREATED"
        validate_commit_readback(git.read_commit_and_changed_paths(commit_sha), expected_commit)
        git.create_branch_ref_without_force(plan.branch, commit_sha)
        gate = "BRANCH_PUSHED"
        verify_remote_main(git.read_remote_main(), plan.base_commit, stage="before_pr")
        if pr.find_open_draft_pr_for_branch(plan.branch) is not None:
            raise StateError("BRANCH_COLLISION")
        if not pr.establish_definite_absence(plan.branch):
            raise StateError("PR_CREATION_UNCERTAIN")
        expected_pr = _pr_spec(context, plan, commit_sha)
        created = pr.create_draft_pr(expected_pr)
        gate = "PR_REQUESTED"
        read_pr = pr.read_pull_request(created.number)
        validate_pr_readback(read_pr, expected_pr)
        return _receipt_success(
            context=context,
            plan=plan,
            state="DRAFT_PR_CREATED",
            commit_sha=commit_sha,
            tree_sha=tree_sha,
            pr_number=read_pr.number,
            pr_url=read_pr.url,
        )
    except StateError as exc:
        code = safe_code(exc)
        if code == "PR_CREATION_UNCERTAIN":
            pr.post_request_uncertainty_readback(plan.branch)
        return _receipt_for_error(context, plan, code, gate)
    except Exception:
        return _receipt_for_error(context, plan, "UNEXPECTED_EXCEPTION", gate)
