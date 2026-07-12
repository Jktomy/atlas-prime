from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .path_policy import PolicyError, validate_declared_path_set, validate_relative_path, validate_safe_filename
from .protected_paths import is_protected_path, is_thread_engine_self_change_path
from .receipt import sha256_bytes, stable_json

MISSION_SCHEMA_VERSION = "atlas-thread-engine-production-mission-v1"
IMPLEMENTATION_STATE = "THREAD_ENGINE_ACTIVE_MISSION_SCOPED"
ADAPTER_MODE = "DRAFT_PR_ONLY"
REQUIRED_STOP_POINT = "DRAFT_PR_READBACK"
EXPECTED_REPOSITORY = "Jktomy/atlas-prime"
EXPECTED_REMOTE_URL = "https://github.com/Jktomy/atlas-prime.git"
EXPECTED_API = "https://api.github.com/repos/Jktomy/atlas-prime"
AEGIS_BREAK_ROUTE_IDENTITY = "AEGIS_BREAK_PROTECTED_PATH_V1"
AEGIS_BREAK_OPERATOR = "Jayson"
AEGIS_BREAK_GITHUB_OPERATOR_LOGIN = "Jktomy"

TOP_LEVEL_KEYS = {
    "schema_version",
    "implementation_state",
    "adapter_mode",
    "persistent_writer",
    "activation_authority",
    "mission_id",
    "authority_id",
    "build_identity",
    "execute_identity",
    "mission_sha256",
    "repository",
    "remote_url",
    "base_sha",
    "branch",
    "commit_message",
    "pr_title",
    "pr_body",
    "declared_paths",
    "payload_root",
    "candidate_tree_sha256",
    "final_pathset_sha256",
    "source_blobs",
    "operations",
    "lifecycle_profile",
    "delete_authority_id",
    "aegis_break_authority",
    "network_allowlist",
    "receipt_name",
    "stop_point",
}

OPERATION_KEYS = {"thread_id", "operation", "path", "payload", "source_sha256", "payload_sha256", "expected_output_sha256", "delete_authority_id"}
AEGIS_BREAK_KEYS = {
    "route_identity",
    "authority_id",
    "operator",
    "github_operator_login",
    "repository",
    "base_sha",
    "branch",
    "declared_protected_paths",
    "source_blobs",
    "candidate_tree_sha256",
    "final_pathset_sha256",
    "operation_set_sha256",
    "stop_point",
    "persistent_writer",
    "direct_main_write",
    "force_push",
    "automatic_ready",
    "automatic_merge",
    "workflow_dispatch",
    "standing_authority",
}
AEGIS_BREAK_FALSE_FIELDS = {
    "direct_main_write",
    "force_push",
    "automatic_ready",
    "automatic_merge",
    "workflow_dispatch",
}
class MissionError(Exception):
    def __init__(self, message: str, code: str = "MISSION_REJECTED") -> None:
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class ThreadOperation:
    thread_id: str
    operation: str
    path: str
    payload: str | None = None
    source_sha256: str | None = None
    payload_sha256: str | None = None
    expected_output_sha256: str | None = None
    delete_authority_id: str | None = None


@dataclass(frozen=True)
class Mission:
    data: dict[str, Any]
    mission_id: str
    authority_id: str
    build_identity: str
    execute_identity: str
    mission_sha256: str
    repository: str
    remote_url: str
    base_sha: str
    branch: str
    commit_message: str
    pr_title: str
    pr_body: str
    declared_paths: tuple[str, ...]
    payload_root: str
    candidate_tree_sha256: str
    final_pathset_sha256: str
    source_blobs: dict[str, str]
    operations: tuple[ThreadOperation, ...]
    delete_authority_id: str | None
    network_allowlist: tuple[str, ...]
    receipt_name: str
    stop_point: str
    aegis_break_authority: dict[str, Any] | None
    lifecycle_profile: dict[str, Any] | None


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise MissionError(f"duplicate JSON key rejected: {key}", "DUPLICATE_JSON_KEY")
        result[key] = value
    return result


def _require_sha(value: Any, field: str, length: int) -> str:
    if not isinstance(value, str) or len(value) != length:
        raise MissionError(f"{field} must be a {length}-character lowercase hex SHA", "MISSION_SCHEMA")
    if any(char not in "0123456789abcdef" for char in value):
        raise MissionError(f"{field} must be lowercase hex", "MISSION_SCHEMA")
    return value


def _require_string(data: dict[str, Any], field: str) -> str:
    value = data.get(field)
    if not isinstance(value, str) or not value:
        raise MissionError(f"{field} must be a non-empty string", "MISSION_SCHEMA")
    return value


def _require_const(data: dict[str, Any], field: str, expected: str) -> None:
    if data.get(field) != expected:
        raise MissionError(f"{field} must be {expected}", "MISSION_SCHEMA")


def _canonical_mission_digest(data: dict[str, Any]) -> str:
    without_digest = dict(data)
    without_digest["mission_sha256"] = "0" * 64
    return sha256_bytes(stable_json(without_digest).encode("utf-8"))


def operation_set_sha256(operations: list[dict[str, Any]]) -> str:
    return sha256_bytes(stable_json({"operations": operations}).encode("utf-8"))


def _protected_path_set(paths: tuple[str, ...]) -> tuple[str, ...]:
    protected: list[str] = []
    for value in paths:
        rel = validate_relative_path(value)
        if is_protected_path(rel):
            protected.append(rel.as_posix())
    return tuple(protected)


def _reject_thread_engine_self_change(paths: tuple[str, ...]) -> None:
    for path in paths:
        if is_thread_engine_self_change_path(validate_relative_path(path)):
            raise MissionError("Thread Engine self-change requires a separate protected route", "THREAD_ENGINE_SELF_CHANGE_REJECTED")


def _require_string_list(value: Any, field: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not value or not all(isinstance(item, str) for item in value):
        raise MissionError(f"{field} must be a non-empty string array", "MISSION_SCHEMA")
    return tuple(value)


def _validate_aegis_break_authority(
    data: dict[str, Any],
    protected_paths: tuple[str, ...],
    source_blobs: dict[str, str],
    operations_value: list[dict[str, Any]],
) -> dict[str, Any] | None:
    raw = data.get("aegis_break_authority")
    if not protected_paths:
        if raw is not None:
            raise MissionError("Aegis Break authority is forbidden when no protected paths are declared", "AEGIS_BREAK_UNUSED")
        return None
    if raw is None:
        raise MissionError("protected path requires explicit Aegis Break authority", "PROTECTED_PATH")
    if not isinstance(raw, dict):
        raise MissionError("aegis_break_authority must be an object", "MISSION_SCHEMA")
    unknown = set(raw) - AEGIS_BREAK_KEYS
    if unknown:
        raise MissionError(f"unknown Aegis Break properties rejected: {', '.join(sorted(unknown))}", "UNKNOWN_PROPERTY")
    missing = AEGIS_BREAK_KEYS - set(raw)
    if missing:
        raise MissionError(f"missing Aegis Break properties: {', '.join(sorted(missing))}", "MISSION_SCHEMA")
    if raw["route_identity"] != AEGIS_BREAK_ROUTE_IDENTITY:
        raise MissionError("Aegis Break route identity mismatch", "AEGIS_BREAK_ROUTE_REJECTED")
    if raw["authority_id"] != data["authority_id"]:
        raise MissionError("Aegis Break authority_id mismatch", "AEGIS_BREAK_AUTHORITY_MISMATCH")
    if raw["operator"] != AEGIS_BREAK_OPERATOR:
        raise MissionError("Aegis Break operator mismatch", "AEGIS_BREAK_OPERATOR_MISMATCH")
    if raw["github_operator_login"] != AEGIS_BREAK_GITHUB_OPERATOR_LOGIN:
        raise MissionError("Aegis Break GitHub operator login mismatch", "AEGIS_BREAK_OPERATOR_MISMATCH")
    for field in ("repository", "base_sha", "branch", "candidate_tree_sha256", "final_pathset_sha256", "stop_point", "persistent_writer"):
        if raw[field] != data[field]:
            raise MissionError(f"Aegis Break {field} mismatch", "AEGIS_BREAK_BINDING_MISMATCH")
    for field in AEGIS_BREAK_FALSE_FIELDS:
        if raw[field] is not False:
            raise MissionError(f"Aegis Break forbidden action must remain false: {field}", "AEGIS_BREAK_FORBIDDEN_ACTION")
    if raw["standing_authority"] != "NO":
        raise MissionError("Aegis Break standing_authority must be NO", "AEGIS_BREAK_FORBIDDEN_ACTION")
    declared_protected = _require_string_list(raw["declared_protected_paths"], "declared_protected_paths")
    try:
        validate_declared_path_set(declared_protected, allow_protected=True)
    except PolicyError as exc:
        raise MissionError(str(exc), exc.code) from exc
    if set(declared_protected) != set(protected_paths):
        raise MissionError("Aegis Break protected path set mismatch", "AEGIS_BREAK_PATH_MISMATCH")
    _reject_thread_engine_self_change(declared_protected)
    authority_blobs = raw["source_blobs"]
    if not isinstance(authority_blobs, dict):
        raise MissionError("Aegis Break source_blobs must be an object", "MISSION_SCHEMA")
    if authority_blobs != source_blobs:
        raise MissionError("Aegis Break source_blobs mismatch", "AEGIS_BREAK_SOURCE_BLOB_MISMATCH")
    for raw_operation in operations_value:
        operation_path = validate_relative_path(raw_operation["path"])
        if raw_operation["operation"] in {"REPLACE", "DELETE"} and is_protected_path(operation_path) and operation_path.as_posix() not in source_blobs:
            raise MissionError("Aegis Break protected REPLACE/DELETE requires a source blob entry", "AEGIS_BREAK_SOURCE_BLOB_REQUIRED")
    if raw["operation_set_sha256"] != operation_set_sha256(operations_value):
        raise MissionError("Aegis Break operation set hash mismatch", "AEGIS_BREAK_OPERATION_SET_MISMATCH")
    return dict(raw)


def load_mission(path: Path) -> Mission:
    try:
        data = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_reject_duplicate_keys)
    except json.JSONDecodeError as exc:
        raise MissionError(f"invalid mission JSON: {exc}", "INVALID_JSON") from exc
    return validate_mission(data)


def validate_mission(data: dict[str, Any]) -> Mission:
    if not isinstance(data, dict):
        raise MissionError("mission must be a JSON object", "MISSION_SCHEMA")
    unknown = set(data) - TOP_LEVEL_KEYS
    if unknown:
        raise MissionError(f"unknown mission properties rejected: {', '.join(sorted(unknown))}", "UNKNOWN_PROPERTY")
    missing = TOP_LEVEL_KEYS - set(data) - {"delete_authority_id", "aegis_break_authority", "lifecycle_profile"}
    if missing:
        raise MissionError(f"missing mission properties: {', '.join(sorted(missing))}", "MISSION_SCHEMA")

    _require_const(data, "schema_version", MISSION_SCHEMA_VERSION)
    _require_const(data, "implementation_state", IMPLEMENTATION_STATE)
    _require_const(data, "adapter_mode", ADAPTER_MODE)
    _require_const(data, "persistent_writer", "ABSENT")
    _require_const(data, "activation_authority", "MISSION_SCOPED")

    mission_sha256 = _require_sha(data.get("mission_sha256"), "mission_sha256", 64)
    if _canonical_mission_digest(data) != mission_sha256:
        raise MissionError("mission_sha256 does not match canonical mission bytes", "MISSION_SHA_MISMATCH")

    build_identity = _require_string(data, "build_identity")
    execute_identity = _require_string(data, "execute_identity")
    if build_identity == execute_identity:
        raise MissionError("build_identity and execute_identity must remain separate", "IDENTITY_COLLISION")

    repository = _require_string(data, "repository")
    remote_url = _require_string(data, "remote_url")
    if repository != EXPECTED_REPOSITORY or remote_url != EXPECTED_REMOTE_URL:
        raise MissionError("mission repository or remote is not approved", "REMOTE_REJECTED")

    base_sha = _require_sha(data.get("base_sha"), "base_sha", 40)
    branch = _require_string(data, "branch")
    if not branch.startswith("source/"):
        raise MissionError("mission branch must be a source branch", "BRANCH_REJECTED")
    validate_relative_path(branch)

    declared_paths_value = data.get("declared_paths")
    if not isinstance(declared_paths_value, list) or not declared_paths_value or not all(isinstance(item, str) for item in declared_paths_value):
        raise MissionError("declared_paths must be a non-empty string array", "MISSION_SCHEMA")
    aegis_break_requested = data.get("aegis_break_authority") is not None
    protected_route_requested = aegis_break_requested
    try:
        declared_paths = tuple(item for item in declared_paths_value)
        validate_declared_path_set(declared_paths, allow_protected=protected_route_requested)
    except PolicyError as exc:
        raise MissionError(str(exc), exc.code) from exc
    protected_paths = _protected_path_set(declared_paths)

    payload_root = _require_string(data, "payload_root")
    validate_relative_path(payload_root)
    candidate_tree_sha256 = _require_sha(data.get("candidate_tree_sha256"), "candidate_tree_sha256", 64)
    final_pathset_sha256 = _require_sha(data.get("final_pathset_sha256"), "final_pathset_sha256", 64)

    source_blobs = data.get("source_blobs")
    if not isinstance(source_blobs, dict):
        raise MissionError("source_blobs must be an object", "MISSION_SCHEMA")
    for path, sha in source_blobs.items():
        if not isinstance(path, str):
            raise MissionError("source_blobs keys must be strings", "MISSION_SCHEMA")
        validate_relative_path(path)
        _require_sha(sha, f"source_blobs[{path}]", 40)

    operations_value = data.get("operations")
    if not isinstance(operations_value, list) or not operations_value:
        raise MissionError("operations must be a non-empty array", "MISSION_SCHEMA")
    seen_threads: set[str] = set()
    operation_paths: list[str] = []
    operations: list[ThreadOperation] = []
    has_delete = False
    for raw in operations_value:
        if not isinstance(raw, dict):
            raise MissionError("operation must be an object", "MISSION_SCHEMA")
        unknown_op = set(raw) - OPERATION_KEYS
        if unknown_op:
            raise MissionError(f"unknown operation properties rejected: {', '.join(sorted(unknown_op))}", "UNKNOWN_PROPERTY")
        thread_id = _require_string(raw, "thread_id")
        if thread_id in seen_threads:
            raise MissionError(f"duplicate thread_id: {thread_id}", "THREAD_COLLISION")
        seen_threads.add(thread_id)
        operation = _require_string(raw, "operation")
        path = _require_string(raw, "path")
        validate_relative_path(path)
        operation_paths.append(path)

        if operation == "ADD":
            required = {"payload", "payload_sha256", "expected_output_sha256"}
            forbidden = {"source_sha256", "delete_authority_id"}
        elif operation == "REPLACE":
            required = {"payload", "payload_sha256", "expected_output_sha256", "source_sha256"}
            forbidden = {"delete_authority_id"}
        elif operation == "DELETE":
            required = {"source_sha256", "delete_authority_id"}
            forbidden = {"payload", "payload_sha256", "expected_output_sha256"}
            has_delete = True
        else:
            raise MissionError(f"unsupported operation: {operation}", "MISSION_SCHEMA")

        missing_required = [field for field in sorted(required) if field not in raw]
        present_forbidden = [field for field in sorted(forbidden) if field in raw]
        if missing_required:
            raise MissionError(f"{operation} missing fields: {', '.join(missing_required)}", "MISSION_SCHEMA")
        if present_forbidden:
            raise MissionError(f"{operation} forbidden fields present: {', '.join(present_forbidden)}", "MISSION_SCHEMA")
        for sha_field in ("source_sha256", "payload_sha256", "expected_output_sha256"):
            if sha_field in raw:
                _require_sha(raw[sha_field], sha_field, 64)

        operations.append(
            ThreadOperation(
                thread_id=thread_id,
                operation=operation,
                path=path,
                payload=raw.get("payload"),
                source_sha256=raw.get("source_sha256"),
                payload_sha256=raw.get("payload_sha256"),
                expected_output_sha256=raw.get("expected_output_sha256"),
                delete_authority_id=raw.get("delete_authority_id"),
            )
        )

    try:
        validate_declared_path_set(operation_paths, allow_protected=protected_route_requested)
    except PolicyError as exc:
        raise MissionError(str(exc), exc.code) from exc
    if set(operation_paths) != set(declared_paths):
        raise MissionError("operation paths must match declared_paths exactly", "PATH_SET_MISMATCH")
    aegis_break_authority = _validate_aegis_break_authority(data, protected_paths, source_blobs, operations_value) if aegis_break_requested else None
    if protected_paths and aegis_break_authority is None:
        raise MissionError("protected path requires explicit protected route authority", "PROTECTED_PATH")
    delete_authority_id = data.get("delete_authority_id")
    if has_delete and not isinstance(delete_authority_id, str):
        raise MissionError("DELETE missions require top-level delete_authority_id", "DELETE_AUTHORITY_REQUIRED")
    if not has_delete and "delete_authority_id" in data and data["delete_authority_id"] is not None:
        raise MissionError("delete_authority_id is forbidden when no DELETE operation exists", "MISSION_SCHEMA")

    network_allowlist = data.get("network_allowlist")
    if network_allowlist != [EXPECTED_REMOTE_URL, EXPECTED_API]:
        raise MissionError("network_allowlist is not exact", "NETWORK_REJECTED")

    try:
        receipt_name = validate_safe_filename(_require_string(data, "receipt_name"), reserved={"state-journal.jsonl", "pr-body.md"})
    except PolicyError as exc:
        raise MissionError(str(exc), exc.code) from exc
    stop_point = _require_string(data, "stop_point")
    if stop_point != REQUIRED_STOP_POINT:
        raise MissionError("stop_point must be DRAFT_PR_READBACK", "STOP_POINT_REJECTED")

    lifecycle_profile = None
    if data.get("lifecycle_profile") is not None:
        from .lifecycle_profile import LifecycleProfileError, validate_lifecycle_profile

        try:
            lifecycle_profile = validate_lifecycle_profile(data["lifecycle_profile"], data)
        except LifecycleProfileError as exc:
            raise MissionError(str(exc), exc.code) from exc

    return Mission(
        data=data,
        mission_id=_require_string(data, "mission_id"),
        authority_id=_require_string(data, "authority_id"),
        build_identity=build_identity,
        execute_identity=execute_identity,
        mission_sha256=mission_sha256,
        repository=repository,
        remote_url=remote_url,
        base_sha=base_sha,
        branch=branch,
        commit_message=_require_string(data, "commit_message"),
        pr_title=_require_string(data, "pr_title"),
        pr_body=_require_string(data, "pr_body"),
        declared_paths=declared_paths,
        payload_root=payload_root,
        candidate_tree_sha256=candidate_tree_sha256,
        final_pathset_sha256=final_pathset_sha256,
        source_blobs=source_blobs,
        operations=tuple(operations),
        delete_authority_id=delete_authority_id,
        network_allowlist=tuple(network_allowlist),
        receipt_name=receipt_name,
        stop_point=stop_point,
        aegis_break_authority=aegis_break_authority,
        lifecycle_profile=lifecycle_profile,
    )
