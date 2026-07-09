from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path
from typing import Any

from .authority import (
    EXPECTED_API,
    EXPECTED_REMOTE_URL,
    WORKBOARD_ALLOWED_UPDATE_FIELDS,
    WORKBOARD_PATH,
    WORKBOARD_PRIORITY_VALUES,
    WORKBOARD_STATUS_VALUES,
    Mission,
    MissionError,
    ThreadOperation,
    load_mission,
    operation_set_sha256,
)
from .git_runner import GitRunner, GitRunnerError
from .path_policy import PolicyError, reject_runtime_byproducts, reject_symlinks, resolve_under, validate_relative_path
from .readback import REVIEW_THREAD_QUERY, ReadbackError, verify_pr_readback, verify_review_thread_readback
from .receipt import declared_state_hash, forbidden_confirmation, sha256_bytes, sha256_file, stable_json, tree_hash, write_evidence_json, write_json
from .recovery import classify_recovery

CHECKPOINTS = [
    "PACKAGE_AUDIT",
    "MISSION_PARSE",
    "MISSION_SCHEMA",
    "MISSION_INTEGRITY",
    "PROTECTED_ROUTE_INTENT",
    "OPERATOR_VERIFY",
    "REMOTE_LOCK",
    "DUPLICATE_CHECK",
    "FRESH_CLONE",
    "CLEAN_START",
    "SOURCE_BLOB_VERIFY",
    "CANDIDATE_STAGE",
    "PATH_POLICY_VERIFY",
    "TREE_VERIFY",
    "INSTALL",
    "DIFF_CHECK",
    "STAGE_VERIFY",
    "COMMIT",
    "COMMIT_VERIFY",
    "PUSH",
    "DRAFT_PR",
    "READBACK",
    "RECEIPT",
    "STOP",
]


class AdapterError(Exception):
    def __init__(self, message: str, code: str = "ADAPTER_REJECTED", stage: str = "STOP", partial: bool = False) -> None:
        super().__init__(message)
        self.code = code
        self.stage = stage
        self.partial = partial
        self.receipt: dict[str, Any] | None = None


class Journal:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.completed: list[str] = []
        self.entered: str | None = None

    def record(self, checkpoint: str, status: str, detail: str | None = None) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        entry = {"checkpoint": checkpoint, "status": status}
        if detail:
            entry["detail"] = detail
        with self.path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(entry, sort_keys=True) + "\n")

    def enter(self, checkpoint: str) -> None:
        self.entered = checkpoint
        self.record(checkpoint, "entered")

    def complete(self, checkpoint: str) -> None:
        self.completed.append(checkpoint)
        self.record(checkpoint, "completed")

    def reject(self, checkpoint: str, detail: str) -> None:
        self.record(checkpoint, "rejected", detail)


def _receipt(
    mission: Mission | None,
    result: str,
    journal: Journal,
    stage: str,
    code: str | None = None,
    message: str | None = None,
    extra: dict[str, Any] | None = None,
    observed_operator_login: str | None = None,
) -> dict[str, Any]:
    body: dict[str, Any] = {
        "schema_version": "atlas-thread-engine-production-adapter-receipt-v2",
        "implementation_state": "THREAD_ENGINE_ACTIVE_MISSION_SCOPED",
        "adapter_mode": "DRAFT_PR_ONLY",
        "mission_id": mission.mission_id if mission else "UNKNOWN",
        "authority_id": mission.authority_id if mission else "UNKNOWN",
        "build_identity": mission.build_identity if mission else "UNKNOWN",
        "execute_identity": mission.execute_identity if mission else "UNKNOWN",
        "mission_sha256": mission.mission_sha256 if mission else None,
        "repository": mission.repository if mission else "UNKNOWN",
        "base_sha": mission.base_sha if mission else None,
        "branch": mission.branch if mission else None,
        "result": result,
        "error_code": code,
        "error_stage": stage if result in {"REJECTED", "PARTIAL"} else None,
        "stop_point": stage,
        "checkpoint_results": [{"checkpoint": item, "status": "completed"} for item in journal.completed]
        + ([{"checkpoint": stage, "status": result.lower()}] if result in {"REJECTED", "PARTIAL"} and stage not in journal.completed else []),
        "last_completed_checkpoint": journal.completed[-1] if journal.completed else None,
        "forbidden_action_confirmation": forbidden_confirmation(),
        "draft_pr_only": True,
        "thread_engine_active": True,
        "authority_scope": "MISSION_SCOPED",
        "production_authority_activated": False,
        "standing_authority": "NO",
        "human_merge_required": True,
    }
    if message:
        body["message"] = message
    if mission and mission.aegis_break_authority:
        protected_paths = tuple(mission.aegis_break_authority["declared_protected_paths"])
        protected_source_blobs = {path: mission.source_blobs[path] for path in protected_paths if path in mission.source_blobs}
        route_forbidden_confirmation = {
            "direct_main_write": mission.aegis_break_authority["direct_main_write"],
            "force_push": mission.aegis_break_authority["force_push"],
            "automatic_ready": mission.aegis_break_authority["automatic_ready"],
            "automatic_merge": mission.aegis_break_authority["automatic_merge"],
            "workflow_dispatch": mission.aegis_break_authority["workflow_dispatch"],
            "standing_authority": mission.aegis_break_authority["standing_authority"],
        }
        body["aegis_break_protected_route"] = {
            "route_identity": mission.aegis_break_authority["route_identity"],
            "authority_id": mission.aegis_break_authority["authority_id"],
            "operator": mission.aegis_break_authority["operator"],
            "expected_operator_login": mission.aegis_break_authority["github_operator_login"],
            "observed_operator_login": observed_operator_login,
            "declared_protected_paths": list(protected_paths),
            "exact_protected_paths": list(protected_paths),
            "protected_source_blobs": protected_source_blobs,
            "protected_source_blobs_sha256": sha256_bytes(stable_json(protected_source_blobs).encode("utf-8")),
            "operation_set_sha256": operation_set_sha256(mission.data["operations"]),
            "candidate_tree_sha256": mission.candidate_tree_sha256,
            "final_pathset_sha256": mission.final_pathset_sha256,
            "standing_authority": mission.aegis_break_authority["standing_authority"],
            "direct_main_write": mission.aegis_break_authority["direct_main_write"],
            "force_push": mission.aegis_break_authority["force_push"],
            "automatic_ready": mission.aegis_break_authority["automatic_ready"],
            "automatic_merge": mission.aegis_break_authority["automatic_merge"],
            "workflow_dispatch": mission.aegis_break_authority["workflow_dispatch"],
            "forbidden_action_confirmation": route_forbidden_confirmation,
        }
    if mission and mission.workboard_row_update_authority:
        authority = mission.workboard_row_update_authority
        route_forbidden_confirmation = {
            "direct_main_write": authority["direct_main_write"],
            "force_push": authority["force_push"],
            "automatic_ready": authority["automatic_ready"],
            "automatic_merge": authority["automatic_merge"],
            "workflow_dispatch": authority["workflow_dispatch"],
            "standing_authority": authority["standing_authority"],
        }
        body["workboard_row_update_route"] = {
            "route_identity": authority["route_identity"],
            "authority_id": authority["authority_id"],
            "operator": authority["operator"],
            "expected_operator_login": authority["github_operator_login"],
            "observed_operator_login": observed_operator_login,
            "workboard_path": authority["workboard_path"],
            "workboard_source_blob": authority["workboard_source_blob"],
            "row_identity": authority["row_identity"],
            "allowed_fields": authority["allowed_fields"],
            "before_row_sha256": authority["before_row_sha256"],
            "after_row_sha256": authority["after_row_sha256"],
            "operation_set_sha256": operation_set_sha256(mission.data["operations"]),
            "candidate_tree_sha256": mission.candidate_tree_sha256,
            "final_pathset_sha256": mission.final_pathset_sha256,
            "standing_authority": authority["standing_authority"],
            "direct_main_write": authority["direct_main_write"],
            "force_push": authority["force_push"],
            "automatic_ready": authority["automatic_ready"],
            "automatic_merge": authority["automatic_merge"],
            "workflow_dispatch": authority["workflow_dispatch"],
            "forbidden_action_confirmation": route_forbidden_confirmation,
        }
    if extra:
        body.update(extra)
    return body


def _write_receipt(
    evidence_root: Path,
    mission: Mission | None,
    journal: Journal,
    result: str,
    stage: str,
    code: str | None = None,
    message: str | None = None,
    extra: dict[str, Any] | None = None,
    observed_operator_login: str | None = None,
) -> dict[str, Any]:
    receipt = _receipt(mission, result, journal, stage, code, message, extra, observed_operator_login)
    name = mission.receipt_name if mission else "production-adapter-rejection-receipt.json"
    write_evidence_json(evidence_root, name, receipt)
    return receipt


def _copy_payload(operation: ThreadOperation, payload_root: Path, target: Path) -> None:
    if not operation.payload:
        raise AdapterError(f"{operation.operation} requires a payload: {operation.thread_id}", "PAYLOAD_REQUIRED", "CANDIDATE_STAGE")
    payload = resolve_under(payload_root, validate_relative_path(operation.payload))
    if not payload.exists() or not payload.is_file() or payload.is_symlink():
        raise AdapterError(f"payload is not a regular file: {operation.thread_id}", "PAYLOAD_REJECTED", "CANDIDATE_STAGE")
    payload_hash = sha256_file(payload)
    if payload_hash != operation.payload_sha256:
        raise AdapterError(f"payload hash mismatch: {operation.thread_id}", "PAYLOAD_HASH_MISMATCH", "CANDIDATE_STAGE")
    if payload_hash != operation.expected_output_sha256:
        raise AdapterError(f"expected output hash mismatch: {operation.thread_id}", "OUTPUT_HASH_MISMATCH", "CANDIDATE_STAGE")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(payload, target)


def _row_hash(row: str) -> str:
    return sha256_bytes((row + "\n").encode("utf-8"))


def _split_markdown_row(row: str) -> list[str]:
    text = row.strip()
    if not text.startswith("|") or not text.endswith("|"):
        raise AdapterError("Workboard row must be a Markdown table row", "WORKBOARD_ROW_REJECTED", "CANDIDATE_STAGE")
    return [cell.strip() for cell in text.strip("|").split("|")]


def _is_separator_row(row: str) -> bool:
    cells = _split_markdown_row(row)
    return bool(cells) and all(cell and set(cell) <= {"-", ":"} for cell in cells)


def _find_workboard_row(lines: list[str], identity: dict[str, str]) -> tuple[int, list[str], list[str]]:
    matches: list[tuple[int, list[str], list[str]]] = []
    for index in range(len(lines) - 2):
        header = lines[index]
        separator = lines[index + 1]
        if not header.lstrip().startswith("|") or not separator.lstrip().startswith("|"):
            continue
        try:
            header_cells = _split_markdown_row(header)
            if not _is_separator_row(separator):
                continue
        except AdapterError:
            continue
        if not set(identity).issubset(header_cells):
            continue
        for row_index in range(index + 2, len(lines)):
            row = lines[row_index]
            if not row.lstrip().startswith("|"):
                break
            if _is_separator_row(row):
                continue
            cells = _split_markdown_row(row)
            if len(cells) != len(header_cells):
                raise AdapterError("Workboard row column count mismatch", "WORKBOARD_ROW_REJECTED", "CANDIDATE_STAGE")
            row_map = dict(zip(header_cells, cells, strict=True))
            if all(row_map.get(key) == value for key, value in identity.items()):
                matches.append((row_index, header_cells, cells))
    if len(matches) != 1:
        raise AdapterError("Workboard row identity must match exactly one row", "WORKBOARD_ROW_IDENTITY_REJECTED", "CANDIDATE_STAGE")
    return matches[0]


def _validate_workboard_row_update(mission: Mission, checkout: Path, candidate_root: Path) -> dict[str, Any] | None:
    authority = mission.workboard_row_update_authority
    if not authority:
        return None
    if mission.declared_paths != (WORKBOARD_PATH,) or len(mission.operations) != 1:
        raise AdapterError("Workboard row update route requires exactly one Workboard path", "WORKBOARD_PATH_MISMATCH", "CANDIDATE_STAGE")
    operation = mission.operations[0]
    if operation.operation != "REPLACE" or operation.path != WORKBOARD_PATH:
        raise AdapterError("Workboard row update route requires one Workboard REPLACE", "WORKBOARD_OPERATION_REJECTED", "CANDIDATE_STAGE")
    source_path = checkout / WORKBOARD_PATH
    candidate_path = candidate_root / WORKBOARD_PATH
    before_lines = source_path.read_text(encoding="utf-8").splitlines()
    after_lines = candidate_path.read_text(encoding="utf-8").splitlines()
    if len(before_lines) != len(after_lines):
        raise AdapterError("Workboard row update must not add or remove lines", "WORKBOARD_STRUCTURE_REJECTED", "CANDIDATE_STAGE")
    row_index, before_header, before_cells = _find_workboard_row(before_lines, authority["row_identity"])
    after_index, after_header, after_cells = _find_workboard_row(after_lines, authority["row_identity"])
    if row_index != after_index or before_header != after_header:
        raise AdapterError("Workboard row update must not move rows or alter headers", "WORKBOARD_STRUCTURE_REJECTED", "CANDIDATE_STAGE")
    changed_lines = [index for index, pair in enumerate(zip(before_lines, after_lines, strict=True)) if pair[0] != pair[1]]
    if changed_lines != [row_index]:
        raise AdapterError("Workboard row update must change exactly one declared row", "WORKBOARD_ROW_SCOPE_REJECTED", "CANDIDATE_STAGE")
    before_row = before_lines[row_index]
    after_row = after_lines[row_index]
    if _row_hash(before_row) != authority["before_row_sha256"] or _row_hash(after_row) != authority["after_row_sha256"]:
        raise AdapterError("Workboard row hash mismatch", "WORKBOARD_ROW_HASH_MISMATCH", "CANDIDATE_STAGE")
    before_map = dict(zip(before_header, before_cells, strict=True))
    after_map = dict(zip(after_header, after_cells, strict=True))
    changed_fields = [field for field in before_header if before_map[field] != after_map[field]]
    if not changed_fields:
        raise AdapterError("Workboard row update must change at least one field", "WORKBOARD_ROW_SCOPE_REJECTED", "CANDIDATE_STAGE")
    allowed_fields = set(authority["allowed_fields"])
    if not set(changed_fields).issubset(allowed_fields):
        raise AdapterError("Workboard row update changed an undeclared field", "WORKBOARD_FIELD_REJECTED", "CANDIDATE_STAGE")
    if not set(changed_fields).issubset(WORKBOARD_ALLOWED_UPDATE_FIELDS):
        raise AdapterError("Workboard row update changed a protected field", "WORKBOARD_FIELD_REJECTED", "CANDIDATE_STAGE")
    if after_map.get("Status") not in WORKBOARD_STATUS_VALUES:
        raise AdapterError("Workboard row update produced an invalid status", "WORKBOARD_STATUS_REJECTED", "CANDIDATE_STAGE")
    if after_map.get("Priority") not in WORKBOARD_PRIORITY_VALUES:
        raise AdapterError("Workboard row update produced an invalid priority", "WORKBOARD_PRIORITY_REJECTED", "CANDIDATE_STAGE")
    return {
        "workboard_row_update_evidence": {
            "row_index": row_index,
            "changed_fields": changed_fields,
            "before_status": before_map.get("Status"),
            "after_status": after_map.get("Status"),
            "before_priority": before_map.get("Priority"),
            "after_priority": after_map.get("Priority"),
        }
    }


def _install_candidate(mission: Mission, package_root: Path, checkout: Path, candidate_root: Path) -> None:
    payload_root = resolve_under(package_root, validate_relative_path(mission.payload_root))
    if not payload_root.exists() or not payload_root.is_dir():
        raise AdapterError("payload_root is absent", "PAYLOAD_REJECTED", "CANDIDATE_STAGE")
    reject_symlinks(payload_root)
    for operation in mission.operations:
        rel = validate_relative_path(operation.path)
        target = resolve_under(candidate_root, rel)
        checkout_target = resolve_under(checkout, rel)
        if operation.operation == "ADD":
            if checkout_target.exists():
                raise AdapterError(f"ADD target already exists: {operation.path}", "THREAD_REJECTED", "CANDIDATE_STAGE")
            _copy_payload(operation, payload_root, target)
        elif operation.operation == "REPLACE":
            if not checkout_target.exists() or not checkout_target.is_file() or checkout_target.is_symlink():
                raise AdapterError(f"REPLACE source missing: {operation.path}", "SOURCE_REJECTED", "CANDIDATE_STAGE")
            if sha256_file(checkout_target) != operation.source_sha256:
                raise AdapterError(f"source hash mismatch: {operation.path}", "SOURCE_HASH_MISMATCH", "CANDIDATE_STAGE")
            _copy_payload(operation, payload_root, target)
        elif operation.operation == "DELETE":
            if mission.delete_authority_id is None or operation.delete_authority_id != mission.delete_authority_id:
                raise AdapterError(f"DELETE lacks matching authority: {operation.path}", "DELETE_AUTHORITY_REQUIRED", "CANDIDATE_STAGE")
            if not checkout_target.exists() or not checkout_target.is_file() or checkout_target.is_symlink():
                raise AdapterError(f"DELETE source missing: {operation.path}", "SOURCE_REJECTED", "CANDIDATE_STAGE")
            if sha256_file(checkout_target) != operation.source_sha256:
                raise AdapterError(f"delete source hash mismatch: {operation.path}", "SOURCE_HASH_MISMATCH", "CANDIDATE_STAGE")


def _apply_candidate_set(mission: Mission, checkout: Path, candidate_root: Path) -> None:
    for operation in mission.operations:
        rel = validate_relative_path(operation.path)
        checkout_target = resolve_under(checkout, rel)
        if operation.operation == "DELETE":
            if checkout_target.exists():
                checkout_target.unlink()
        else:
            candidate = resolve_under(candidate_root, rel)
            checkout_target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(candidate, checkout_target)


def _verify_final_bytes(mission: Mission, checkout: Path) -> None:
    for operation in mission.operations:
        target = resolve_under(checkout, validate_relative_path(operation.path))
        if operation.operation == "DELETE":
            if target.exists():
                raise AdapterError(f"DELETE target remains present: {operation.path}", "DELETE_VERIFY_FAILED", "INSTALL")
        elif sha256_file(target) != operation.expected_output_sha256:
            raise AdapterError(f"final output hash mismatch: {operation.path}", "OUTPUT_HASH_MISMATCH", "INSTALL")
    observed = declared_state_hash(checkout, mission.declared_paths)
    if observed != mission.final_pathset_sha256:
        raise AdapterError("final declared path-set hash mismatch", "FINAL_PATHSET_MISMATCH", "INSTALL")


def execute_mission(
    mission_path: Path,
    *,
    mission_scoped: bool,
    execute_draft_pr: bool,
    mission_sha256: str | None = None,
    aegis_break_protected_route: bool = False,
    aegis_break_authority_id: str | None = None,
    workboard_row_update: bool = False,
    workboard_row_update_authority_id: str | None = None,
    work_root: Path | None = None,
    package_root: Path | None = None,
    runner: GitRunner | None = None,
) -> dict[str, Any]:
    if not mission_scoped or not execute_draft_pr:
        raise AdapterError("explicit mission-scoped and draft-PR-only execution intent required", "INTENT_REQUIRED", "PACKAGE_AUDIT")
    root = Path(tempfile.mkdtemp(prefix="atlas-gate7f-adapter-", dir=str(work_root) if work_root else None))
    evidence_root = root / "evidence"
    journal = Journal(evidence_root / "state-journal.jsonl")
    mission: Mission | None = None
    checkout: Path | None = None
    observed_operator_login: str | None = None
    workboard_evidence: dict[str, Any] | None = None
    head = ""
    candidate_hash = ""
    commit_tree = ""
    package_root = (package_root or mission_path.resolve().parent).resolve()
    try:
        journal.enter("PACKAGE_AUDIT")
        reject_runtime_byproducts(package_root)
        journal.complete("PACKAGE_AUDIT")

        journal.enter("MISSION_PARSE")
        mission = load_mission(mission_path)
        if mission_sha256 and mission.mission_sha256 != mission_sha256:
            raise AdapterError("mission SHA argument mismatch", "MISSION_SHA_MISMATCH", "MISSION_PARSE")
        journal.complete("MISSION_PARSE")
        journal.enter("MISSION_SCHEMA")
        journal.complete("MISSION_SCHEMA")
        journal.enter("MISSION_INTEGRITY")
        journal.complete("MISSION_INTEGRITY")

        journal.enter("PROTECTED_ROUTE_INTENT")
        if aegis_break_protected_route and workboard_row_update:
            raise AdapterError("only one protected route launch intent may be supplied", "PROTECTED_ROUTE_COLLISION", "PROTECTED_ROUTE_INTENT")
        if mission.aegis_break_authority:
            if not aegis_break_protected_route:
                raise AdapterError("Aegis Break protected-route execution requires explicit launch intent", "AEGIS_BREAK_INTENT_REQUIRED", "PROTECTED_ROUTE_INTENT")
            if not aegis_break_authority_id:
                raise AdapterError("Aegis Break protected-route execution requires launch authority id", "AEGIS_BREAK_AUTHORITY_REQUIRED", "PROTECTED_ROUTE_INTENT")
            if aegis_break_authority_id != mission.aegis_break_authority["authority_id"]:
                raise AdapterError("Aegis Break launch authority id mismatch", "AEGIS_BREAK_AUTHORITY_MISMATCH", "PROTECTED_ROUTE_INTENT")
        elif mission.workboard_row_update_authority:
            if not workboard_row_update:
                raise AdapterError("Workboard row update route requires explicit launch intent", "WORKBOARD_INTENT_REQUIRED", "PROTECTED_ROUTE_INTENT")
            if not workboard_row_update_authority_id:
                raise AdapterError("Workboard row update route requires launch authority id", "WORKBOARD_AUTHORITY_REQUIRED", "PROTECTED_ROUTE_INTENT")
            if workboard_row_update_authority_id != mission.workboard_row_update_authority["authority_id"]:
                raise AdapterError("Workboard row update launch authority id mismatch", "WORKBOARD_AUTHORITY_MISMATCH", "PROTECTED_ROUTE_INTENT")
        elif aegis_break_protected_route or aegis_break_authority_id:
            raise AdapterError("Aegis Break launch intent supplied without mission authority", "AEGIS_BREAK_UNUSED", "PROTECTED_ROUTE_INTENT")
        elif workboard_row_update or workboard_row_update_authority_id:
            raise AdapterError("Workboard row update launch intent supplied without mission authority", "WORKBOARD_UNUSED", "PROTECTED_ROUTE_INTENT")
        journal.complete("PROTECTED_ROUTE_INTENT")

        disabled_hooks = root / "disabled-hooks"
        disabled_hooks.mkdir()
        runner = runner or GitRunner(
            allowed_remote=EXPECTED_REMOTE_URL,
            allowed_api_prefix=EXPECTED_API,
            mission_branch=mission.branch,
            base_sha=mission.base_sha,
            declared_paths=mission.declared_paths,
            commit_message=mission.commit_message,
            pr_title=mission.pr_title,
            disabled_hooks=disabled_hooks,
        )

        journal.enter("OPERATOR_VERIFY")
        if mission.aegis_break_authority:
            observed_operator_login = runner.run(["gh", "api", "user", "--jq", ".login"]).stdout.strip()
            if observed_operator_login != mission.aegis_break_authority["github_operator_login"]:
                raise AdapterError("Aegis Break authenticated GitHub operator mismatch", "AEGIS_BREAK_OPERATOR_MISMATCH", "OPERATOR_VERIFY")
        elif mission.workboard_row_update_authority:
            observed_operator_login = runner.run(["gh", "api", "user", "--jq", ".login"]).stdout.strip()
            if observed_operator_login != mission.workboard_row_update_authority["github_operator_login"]:
                raise AdapterError("Workboard row update authenticated GitHub operator mismatch", "WORKBOARD_OPERATOR_MISMATCH", "OPERATOR_VERIFY")
        journal.complete("OPERATOR_VERIFY")

        journal.enter("REMOTE_LOCK")
        remote = runner.run(["git", "ls-remote", mission.remote_url, "refs/heads/main"]).stdout.strip().split()
        if not remote or remote[0] != mission.base_sha:
            raise AdapterError("canonical main does not match mission base", "STALE_BASE", "REMOTE_LOCK")
        journal.complete("REMOTE_LOCK")

        journal.enter("DUPLICATE_CHECK")
        branch_remote = runner.run(["git", "ls-remote", mission.remote_url, f"refs/heads/{mission.branch}"]).stdout.strip()
        if branch_remote:
            decision = classify_recovery("PUSH", branch_exists=True, head_matches=False)
            raise AdapterError("mission branch already exists", "BRANCH_EXISTS", "DUPLICATE_CHECK", partial=not decision.safe_to_continue)
        prs = runner.run(["gh", "pr", "list", "--repo", mission.repository, "--state", "all", "--head", mission.branch, "--json", "number,state,isDraft,headRefOid"]).stdout.strip()
        if prs and prs != "[]":
            raise AdapterError("matching mission PR already exists", "PR_EXISTS", "DUPLICATE_CHECK", partial=True)
        journal.complete("DUPLICATE_CHECK")

        journal.enter("FRESH_CLONE")
        checkout = root / "checkout"
        runner.run(["git", "clone", "--no-tags", mission.remote_url, str(checkout)])
        observed = runner.run(["git", "rev-parse", "HEAD"], cwd=checkout).stdout.strip()
        if observed != mission.base_sha:
            raise AdapterError("fresh clone head mismatch", "STALE_BASE", "FRESH_CLONE")
        runner.run(["git", "switch", "-c", mission.branch, mission.base_sha], cwd=checkout)
        journal.complete("FRESH_CLONE")

        journal.enter("CLEAN_START")
        if runner.run(["git", "status", "--porcelain=v1"], cwd=checkout).stdout.strip():
            raise AdapterError("fresh checkout is dirty", "DIRTY_CHECKOUT", "CLEAN_START")
        journal.complete("CLEAN_START")

        journal.enter("SOURCE_BLOB_VERIFY")
        for path, expected_blob in mission.source_blobs.items():
            observed_blob = runner.run(["git", "hash-object", "--", path], cwd=checkout).stdout.strip()
            if observed_blob != expected_blob:
                raise AdapterError(f"source blob mismatch: {path}", "SOURCE_BLOB_MISMATCH", "SOURCE_BLOB_VERIFY")
        journal.complete("SOURCE_BLOB_VERIFY")

        journal.enter("CANDIDATE_STAGE")
        candidate_root = root / "candidate"
        candidate_root.mkdir()
        _install_candidate(mission, package_root, checkout, candidate_root)
        workboard_evidence = _validate_workboard_row_update(mission, checkout, candidate_root)
        journal.complete("CANDIDATE_STAGE")

        journal.enter("PATH_POLICY_VERIFY")
        reject_symlinks(candidate_root)
        candidate_paths = sorted(path.relative_to(candidate_root).as_posix() for path in candidate_root.rglob("*") if path.is_file())
        expected_candidate_files = sorted(operation.path for operation in mission.operations if operation.operation != "DELETE")
        if candidate_paths != expected_candidate_files:
            raise AdapterError("candidate file set does not match declared non-delete paths", "PATH_SET_MISMATCH", "PATH_POLICY_VERIFY")
        journal.complete("PATH_POLICY_VERIFY")

        journal.enter("TREE_VERIFY")
        candidate_hash = tree_hash(candidate_root)
        if candidate_hash != mission.candidate_tree_sha256:
            raise AdapterError("candidate tree hash mismatch", "CANDIDATE_TREE_MISMATCH", "TREE_VERIFY")
        journal.complete("TREE_VERIFY")

        journal.enter("INSTALL")
        _apply_candidate_set(mission, checkout, candidate_root)
        _verify_final_bytes(mission, checkout)
        journal.complete("INSTALL")

        journal.enter("DIFF_CHECK")
        runner.run(["git", "diff", "--check"], cwd=checkout)
        journal.complete("DIFF_CHECK")

        journal.enter("STAGE_VERIFY")
        runner.run(["git", "add", "--", *mission.declared_paths], cwd=checkout)
        runner.run(["git", "diff", "--cached", "--check"], cwd=checkout)
        staged = sorted(runner.run(["git", "diff", "--cached", "--name-only"], cwd=checkout).stdout.splitlines())
        if staged != sorted(mission.declared_paths):
            raise AdapterError("staged path set mismatch", "STAGED_PATH_MISMATCH", "STAGE_VERIFY")
        journal.complete("STAGE_VERIFY")

        journal.enter("COMMIT")
        runner.run(["git", "commit", "-m", mission.commit_message], cwd=checkout)
        journal.complete("COMMIT")

        journal.enter("COMMIT_VERIFY")
        head = runner.run(["git", "rev-parse", "HEAD"], cwd=checkout).stdout.strip()
        topology = runner.run(["git", "rev-list", "--parents", "-n", "1", "HEAD"], cwd=checkout).stdout.strip().split()
        if topology != [head, mission.base_sha]:
            raise AdapterError("commit topology mismatch", "TOPOLOGY_REJECTED", "COMMIT_VERIFY")
        if runner.run(["git", "log", "-1", "--format=%s"], cwd=checkout).stdout.strip() != mission.commit_message:
            raise AdapterError("commit message mismatch", "COMMIT_MESSAGE_MISMATCH", "COMMIT_VERIFY")
        changed = sorted(runner.run(["git", "diff", "--name-only", f"{mission.base_sha}..HEAD"], cwd=checkout).stdout.splitlines())
        if changed != sorted(mission.declared_paths):
            raise AdapterError("commit changed-file set mismatch", "COMMIT_FILE_SET_MISMATCH", "COMMIT_VERIFY")
        commit_tree = runner.run(["git", "show", "--format=%T", "--no-patch", "HEAD"], cwd=checkout).stdout.strip()
        journal.complete("COMMIT_VERIFY")

        journal.enter("PUSH")
        runner.run(["git", "push", "-u", "origin", mission.branch], cwd=checkout)
        journal.complete("PUSH")

        journal.enter("DRAFT_PR")
        body_file = evidence_root / "pr-body.md"
        body_file.parent.mkdir(parents=True, exist_ok=True)
        body_file.write_text(mission.pr_body, encoding="utf-8", newline="\n")
        runner.run(
            [
                "gh",
                "pr",
                "create",
                "--repo",
                mission.repository,
                "--base",
                "main",
                "--head",
                mission.branch,
                "--title",
                mission.pr_title,
                "--body-file",
                str(body_file),
                "--draft",
            ],
            cwd=checkout,
        )
        journal.complete("DRAFT_PR")

        journal.enter("READBACK")
        pr_readback = json.loads(
            runner.run(
                [
                    "gh",
                    "pr",
                    "view",
                    mission.branch,
                    "--repo",
                    mission.repository,
                    "--json",
                    "number,url,state,isDraft,baseRefName,baseRefOid,headRefName,headRefOid,title,body,files,commits,comments,reviews",
                ],
                cwd=checkout,
            ).stdout
        )
        pr_number = verify_pr_readback(
            pr_readback,
            mission_branch=mission.branch,
            base_sha=mission.base_sha,
            head_sha=head,
            title=mission.pr_title,
            body=mission.pr_body,
            declared_paths=mission.declared_paths,
        )
        review_thread_readback = json.loads(
            runner.run(
                [
                    "gh",
                    "api",
                    "graphql",
                    "-f",
                    f"query={REVIEW_THREAD_QUERY}",
                    "-f",
                    "owner=Jktomy",
                    "-f",
                    "name=atlas-prime",
                    "-f",
                    f"head={mission.branch}",
                ],
                cwd=checkout,
            ).stdout
        )
        review_thread_count = verify_review_thread_readback(review_thread_readback, expected_pr_number=pr_number, mission_branch=mission.branch)
        journal.complete("READBACK")

        journal.enter("RECEIPT")
        receipt = _write_receipt(
            evidence_root,
            mission,
            journal,
            "SUCCESS",
            "DRAFT_PR_READBACK",
            extra={
                "head_sha": head,
                "commit_tree": commit_tree,
                "candidate_tree_sha256": candidate_hash,
                "pr_readback": pr_readback,
                "review_thread_count": review_thread_count,
                **(workboard_evidence or {}),
            },
            observed_operator_login=observed_operator_login,
        )
        journal.complete("RECEIPT")
        journal.enter("STOP")
        journal.complete("STOP")
        return receipt
    except (AdapterError, MissionError, PolicyError, GitRunnerError, ReadbackError, OSError, ValueError, json.JSONDecodeError) as exc:
        stage = exc.stage if isinstance(exc, AdapterError) else (journal.entered or "PACKAGE_AUDIT")
        code = exc.code if hasattr(exc, "code") else "ADAPTER_REJECTED"
        journal.reject(stage, str(exc))
        result = "PARTIAL" if isinstance(exc, AdapterError) and exc.partial else "REJECTED"
        receipt = _write_receipt(evidence_root, mission, journal, result, stage, str(code), str(exc), observed_operator_login=observed_operator_login)
        wrapped = exc if isinstance(exc, AdapterError) else AdapterError(str(exc), str(code), stage, partial=result == "PARTIAL")
        wrapped.receipt = receipt
        raise wrapped from exc
