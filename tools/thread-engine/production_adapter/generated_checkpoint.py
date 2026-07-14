from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Mapping

from .authority import operation_set_sha256
from .receipt import sha256_bytes, sha256_file, stable_json

PRIME_ROOT = Path(__file__).resolve().parents[3]
if str(PRIME_ROOT) not in sys.path:
    sys.path.insert(0, str(PRIME_ROOT))


PROFILE_ID = "GENERATED_CHECKPOINT_V1"
PROFILE_SCHEMA = "atlas.generated-checkpoint.profile"
PROFILE_VERSION = "1.0.0"
REGISTER_SCHEMA = "atlas.generated-checkpoint.hash-register"
RECONCILIATION_SCHEMA = "atlas.generated-checkpoint.reconciliation"
APPROVED_PATHS = (
    "generated/atlas-duplicate-scope-report.md",
    "generated/atlas-file-inventory.md",
    "generated/atlas-metadata-inventory.md",
    "generated/atlas-orphan-report.md",
    "generated/atlas-routing-inventory.md",
)
PROFILE_KEYS = {
    "schema_id", "schema_version", "profile_id", "mission_id", "repository",
    "base_sha", "branch", "declared_paths", "source_blobs",
    "candidate_tree_sha256", "final_pathset_sha256", "operation_set_sha256",
    "source_fingerprint", "hash_register_path", "hash_register_sha256",
    "reconciliation_path", "reconciliation_sha256", "workflow_ref",
    "workflow_source_sha", "workflow_blob_sha", "workflow_run_id",
    "workflow_run_attempt", "event_name", "actor", "triggering_actor",
    "repository_owner", "credential_principal", "credential_mode",
    "replay_nonce_sha256", "public_clean_confirmation", "stop_point", "persistent_writer",
    "direct_main_write", "force_push", "automatic_ready", "automatic_merge",
    "workflow_dispatch", "repository_setting_mutation", "quest_promotion",
    "capability_promotion", "automatic_retry", "standing_authority",
}
FALSE_FIELDS = {
    "direct_main_write", "force_push", "automatic_ready", "automatic_merge",
    "workflow_dispatch", "repository_setting_mutation", "quest_promotion",
    "capability_promotion",
    "automatic_retry",
}
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
MISSION_ID = re.compile(r"^[A-Z0-9]+(?:-[A-Z0-9]+)*$")
ALLOWED_EVENT_NAMES = frozenset({"push", "workflow_dispatch"})


class GeneratedCheckpointError(Exception):
    def __init__(self, message: str, code: str = "GENERATED_CHECKPOINT_REJECTED") -> None:
        super().__init__(message)
        self.code = code


def deterministic_branch(mission_id: str, replay_nonce_sha256: str) -> str:
    if MISSION_ID.fullmatch(mission_id) is None or HEX64.fullmatch(replay_nonce_sha256) is None:
        raise GeneratedCheckpointError("generated checkpoint replay identity is invalid", "GENERATED_CHECKPOINT_IDENTITY")
    return f"generated/checkpoint-{mission_id.lower()}-{replay_nonce_sha256[:12]}"


def _safe_package_file(package_root: Path, relative: str) -> Path:
    if not isinstance(relative, str) or not relative or "\\" in relative or relative.startswith("/"):
        raise GeneratedCheckpointError("generated checkpoint artifact path is invalid", "GENERATED_CHECKPOINT_PATH")
    target = package_root.joinpath(*relative.split("/")).resolve(strict=False)
    try:
        target.relative_to(package_root)
    except ValueError as exc:
        raise GeneratedCheckpointError("generated checkpoint artifact escapes package", "GENERATED_CHECKPOINT_PATH") from exc
    if not target.is_file() or target.is_symlink():
        raise GeneratedCheckpointError("generated checkpoint artifact is missing or unsafe", "GENERATED_CHECKPOINT_PATH")
    return target


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise GeneratedCheckpointError("generated checkpoint JSON contains duplicate keys", "GENERATED_CHECKPOINT_JSON")
        result[key] = value
    return result


def _load_canonical(path: Path) -> tuple[dict[str, Any], bytes]:
    raw = path.read_bytes()
    try:
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=_pairs)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise GeneratedCheckpointError("generated checkpoint JSON is invalid", "GENERATED_CHECKPOINT_JSON") from exc
    if not isinstance(value, dict) or raw != stable_json(value).encode("utf-8"):
        raise GeneratedCheckpointError("generated checkpoint JSON is not canonical", "GENERATED_CHECKPOINT_JSON")
    return value, raw


def validate_generated_checkpoint_profile(profile: Any, mission: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(profile, dict) or set(profile) != PROFILE_KEYS:
        raise GeneratedCheckpointError("generated checkpoint profile has an invalid closed shape", "GENERATED_CHECKPOINT_PROFILE_SCHEMA")
    constants = {
        "schema_id": PROFILE_SCHEMA,
        "schema_version": PROFILE_VERSION,
        "profile_id": PROFILE_ID,
        "repository": "Jktomy/atlas-prime",
        "actor": "Jktomy",
        "triggering_actor": "Jktomy",
        "repository_owner": "Jktomy",
        "credential_principal": "github-actions[bot]",
        "credential_mode": "GITHUB_TOKEN",
        "public_clean_confirmation": "PUBLIC_CLEAN_CONFIRMED",
        "stop_point": "DRAFT_PR_READBACK",
        "persistent_writer": "ABSENT",
        "standing_authority": "NO",
    }
    for field, expected in constants.items():
        if profile.get(field) != expected:
            raise GeneratedCheckpointError(f"generated checkpoint {field} is invalid", "GENERATED_CHECKPOINT_PROFILE_SCHEMA")
    if profile.get("event_name") not in ALLOWED_EVENT_NAMES:
        raise GeneratedCheckpointError("generated checkpoint event_name is invalid", "GENERATED_CHECKPOINT_PROFILE_SCHEMA")
    for field in FALSE_FIELDS:
        if profile.get(field) is not False:
            raise GeneratedCheckpointError(f"generated checkpoint forbidden field must remain false: {field}", "GENERATED_CHECKPOINT_FORBIDDEN_ACTION")
    for field in (
        "candidate_tree_sha256", "final_pathset_sha256", "operation_set_sha256",
        "hash_register_sha256", "reconciliation_sha256", "replay_nonce_sha256",
    ):
        if not isinstance(profile.get(field), str) or HEX64.fullmatch(profile[field]) is None:
            raise GeneratedCheckpointError(f"generated checkpoint {field} is invalid", "GENERATED_CHECKPOINT_PROFILE_SCHEMA")
    if not isinstance(profile.get("source_fingerprint"), str) or re.fullmatch(r"sha256:[0-9a-f]{64}", profile["source_fingerprint"]) is None:
        raise GeneratedCheckpointError("generated checkpoint source fingerprint is invalid", "GENERATED_CHECKPOINT_PROFILE_SCHEMA")
    for field in ("base_sha", "workflow_source_sha", "workflow_blob_sha"):
        if not isinstance(profile.get(field), str) or HEX40.fullmatch(profile[field]) is None:
            raise GeneratedCheckpointError(f"generated checkpoint {field} is invalid", "GENERATED_CHECKPOINT_PROFILE_SCHEMA")
    if not isinstance(profile.get("workflow_run_id"), str) or not profile["workflow_run_id"].isdigit():
        raise GeneratedCheckpointError("generated checkpoint workflow_run_id is invalid", "GENERATED_CHECKPOINT_PROFILE_SCHEMA")
    if not isinstance(profile.get("workflow_run_attempt"), str) or not profile["workflow_run_attempt"].isdigit():
        raise GeneratedCheckpointError("generated checkpoint workflow_run_attempt is invalid", "GENERATED_CHECKPOINT_PROFILE_SCHEMA")
    expected_ref = "Jktomy/atlas-prime/.github/workflows/generated-checkpoint-publisher.yml@refs/heads/main"
    if profile.get("workflow_ref") != expected_ref:
        raise GeneratedCheckpointError("generated checkpoint workflow ref is invalid", "GENERATED_CHECKPOINT_WORKFLOW_REF")
    if profile.get("hash_register_path") != "evidence/hash-register.json" or profile.get("reconciliation_path") != "evidence/reconciliation.json":
        raise GeneratedCheckpointError("generated checkpoint evidence paths are invalid", "GENERATED_CHECKPOINT_PATH")
    if tuple(profile.get("declared_paths", ())) != APPROVED_PATHS:
        raise GeneratedCheckpointError("generated checkpoint path set is not exact", "GENERATED_CHECKPOINT_PATH_SET")
    if not isinstance(profile.get("source_blobs"), dict) or tuple(profile["source_blobs"]) != APPROVED_PATHS:
        raise GeneratedCheckpointError("generated checkpoint source blob set is not exact", "GENERATED_CHECKPOINT_PATH_SET")
    bindings = {
        "mission_id": mission.get("mission_id"),
        "repository": mission.get("repository"),
        "base_sha": mission.get("base_sha"),
        "branch": mission.get("branch"),
        "declared_paths": mission.get("declared_paths"),
        "source_blobs": mission.get("source_blobs"),
        "candidate_tree_sha256": mission.get("candidate_tree_sha256"),
        "final_pathset_sha256": mission.get("final_pathset_sha256"),
    }
    for field, expected in bindings.items():
        if profile.get(field) != expected:
            raise GeneratedCheckpointError(f"generated checkpoint mission binding mismatch: {field}", "GENERATED_CHECKPOINT_BINDING")
    if profile["workflow_source_sha"] != mission.get("base_sha"):
        raise GeneratedCheckpointError("generated checkpoint workflow source is not the mission base", "GENERATED_CHECKPOINT_BINDING")
    if profile["operation_set_sha256"] != operation_set_sha256(mission.get("operations", [])):
        raise GeneratedCheckpointError("generated checkpoint operation set mismatch", "GENERATED_CHECKPOINT_BINDING")
    if profile["branch"] != deterministic_branch(profile["mission_id"], profile["replay_nonce_sha256"]):
        raise GeneratedCheckpointError("generated checkpoint branch does not match replay identity", "GENERATED_CHECKPOINT_IDENTITY")
    operations = mission.get("operations")
    if not isinstance(operations, list) or len(operations) != len(APPROVED_PATHS):
        raise GeneratedCheckpointError("generated checkpoint operations are not exact", "GENERATED_CHECKPOINT_OPERATION_SET")
    for index, (operation, path) in enumerate(zip(operations, APPROVED_PATHS, strict=True), start=1):
        if not isinstance(operation, dict) or operation.get("operation") != "REPLACE" or operation.get("path") != path:
            raise GeneratedCheckpointError("generated checkpoint permits only ordered REPLACE operations", "GENERATED_CHECKPOINT_OPERATION_SET")
        if operation.get("thread_id") != f"generated-checkpoint-{index:02d}":
            raise GeneratedCheckpointError("generated checkpoint thread identity mismatch", "GENERATED_CHECKPOINT_OPERATION_SET")
        if operation.get("payload_sha256") != operation.get("expected_output_sha256") or operation.get("source_sha256") == operation.get("expected_output_sha256"):
            raise GeneratedCheckpointError("generated checkpoint operation does not change bytes", "GENERATED_CHECKPOINT_NO_CHANGE")
    return dict(profile)


def verify_generated_checkpoint_package(profile: dict[str, Any], package_root: Path) -> dict[str, Any]:
    root = package_root.resolve()
    register_path = _safe_package_file(root, profile["hash_register_path"])
    reconciliation_path = _safe_package_file(root, profile["reconciliation_path"])
    register, register_bytes = _load_canonical(register_path)
    reconciliation, reconciliation_bytes = _load_canonical(reconciliation_path)
    register_sha = sha256_bytes(register_bytes)
    reconciliation_sha = sha256_bytes(reconciliation_bytes)
    if register_sha != profile["hash_register_sha256"] or reconciliation_sha != profile["reconciliation_sha256"]:
        raise GeneratedCheckpointError("generated checkpoint evidence digest mismatch", "GENERATED_CHECKPOINT_EVIDENCE_DIGEST")
    identity = {
        "mission_id": profile["mission_id"],
        "repository": profile["repository"],
        "base_sha": profile["base_sha"],
        "workflow_ref": profile["workflow_ref"],
        "workflow_source_sha": profile["workflow_source_sha"],
        "workflow_run_id": profile["workflow_run_id"],
        "workflow_run_attempt": profile["workflow_run_attempt"],
        "replay_nonce_sha256": profile["replay_nonce_sha256"],
    }
    if (
        register.get("schema_id") != REGISTER_SCHEMA
        or register.get("schema_version") != "1.0.0"
        or register.get("generator_format") != "2"
        or any(register.get(key) != value for key, value in identity.items())
    ):
        raise GeneratedCheckpointError("generated checkpoint register identity mismatch", "GENERATED_CHECKPOINT_REGISTER")
    if register.get("source_fingerprint") != profile["source_fingerprint"]:
        raise GeneratedCheckpointError("generated checkpoint source fingerprint mismatch", "GENERATED_CHECKPOINT_REGISTER")
    if (
        reconciliation.get("schema_id") != RECONCILIATION_SCHEMA
        or reconciliation.get("schema_version") != "1.0.0"
        or reconciliation.get("byte_identical") is not True
        or any(reconciliation.get(key) != value for key, value in identity.items())
    ):
        raise GeneratedCheckpointError("generated checkpoint reconciliation identity mismatch", "GENERATED_CHECKPOINT_RECONCILIATION")
    if reconciliation.get("register_sha256") != register_sha or reconciliation.get("ubuntu_register_sha256") != register_sha or reconciliation.get("windows_register_sha256") != register_sha:
        raise GeneratedCheckpointError("generated checkpoint parity was not exact", "GENERATED_CHECKPOINT_PARITY")
    files = register.get("files")
    if not isinstance(files, list) or [item.get("path") for item in files if isinstance(item, dict)] != list(APPROVED_PATHS):
        raise GeneratedCheckpointError("generated checkpoint register file set is not exact", "GENERATED_CHECKPOINT_PATH_SET")
    for item in files:
        expected = item.get("sha256")
        path = item.get("path")
        if not isinstance(path, str) or not isinstance(expected, str) or HEX64.fullmatch(expected) is None:
            raise GeneratedCheckpointError("generated checkpoint register member is invalid", "GENERATED_CHECKPOINT_REGISTER")
        payload = _safe_package_file(root, f"payloads/{path}")
        if sha256_file(payload) != expected:
            raise GeneratedCheckpointError("generated checkpoint payload differs from parity register", "GENERATED_CHECKPOINT_PAYLOAD")
    return {
        "profile_id": PROFILE_ID,
        "mission_id": profile["mission_id"],
        "base_sha": profile["base_sha"],
        "branch": profile["branch"],
        "source_fingerprint": profile["source_fingerprint"],
        "hash_register_sha256": register_sha,
        "reconciliation_sha256": reconciliation_sha,
        "ubuntu_windows_byte_parity": True,
        "declared_paths": list(APPROVED_PATHS),
        "workflow_source_sha": profile["workflow_source_sha"],
        "workflow_blob_sha": profile["workflow_blob_sha"],
        "workflow_run_id": profile["workflow_run_id"],
        "workflow_run_attempt": profile["workflow_run_attempt"],
        "replay_nonce_sha256": profile["replay_nonce_sha256"],
        "preparer_git_or_github_invocation": False,
        "quest_promotion": False,
        "capability_promotion": False,
    }


def verify_generated_checkpoint_checkout(profile: dict[str, Any], checkout: Path, package_root: Path) -> dict[str, Any]:
    from tools.build_index import APPROVED_OUTPUTS as GENERATOR_OUTPUTS, build_outputs, output_bytes

    outputs, fingerprint = build_outputs(checkout.resolve())
    if tuple(f"generated/{name}" for name in GENERATOR_OUTPUTS) != APPROVED_PATHS:
        raise GeneratedCheckpointError("fresh-clone generator path set is not exact", "GENERATED_CHECKPOINT_REPRODUCTION")
    if f"sha256:{fingerprint}" != profile["source_fingerprint"]:
        raise GeneratedCheckpointError("fresh-clone source fingerprint differs", "GENERATED_CHECKPOINT_REPRODUCTION")
    observed: list[dict[str, str]] = []
    for path, name in zip(APPROVED_PATHS, GENERATOR_OUTPUTS, strict=True):
        candidate = output_bytes(outputs[name])
        payload = _safe_package_file(package_root.resolve(), f"payloads/{path}")
        if payload.read_bytes() != candidate:
            raise GeneratedCheckpointError("fresh-clone output differs from prepared payload", "GENERATED_CHECKPOINT_REPRODUCTION")
        observed.append({"path": path, "sha256": sha256_bytes(candidate)})
    return {
        "source_fingerprint": profile["source_fingerprint"],
        "declared_paths": list(APPROVED_PATHS),
        "files": observed,
        "fresh_clone_reproduction": True,
    }


def verify_generated_checkpoint_history(profile: dict[str, Any], pull_requests: Any) -> dict[str, Any]:
    if not isinstance(pull_requests, list) or len(pull_requests) > 1000:
        raise GeneratedCheckpointError("generated checkpoint PR history is malformed or unbounded", "GENERATED_CHECKPOINT_HISTORY")
    expected_title = f"generated: deterministic checkpoint {profile['mission_id']}"
    replay_marker = f"Replay identity: `sha256:{profile['replay_nonce_sha256']}`"
    checkpoint_count = 0
    for item in pull_requests:
        if not isinstance(item, dict) or set(item) != {
            "number", "state", "isDraft", "headRefName", "headRefOid", "title", "body"
        }:
            raise GeneratedCheckpointError("generated checkpoint PR history entry is malformed", "GENERATED_CHECKPOINT_HISTORY")
        head = item["headRefName"]
        title = item["title"]
        body = item["body"]
        if not isinstance(head, str) or not isinstance(title, str) or not isinstance(body, str):
            raise GeneratedCheckpointError("generated checkpoint PR history text is malformed", "GENERATED_CHECKPOINT_HISTORY")
        is_checkpoint = head.startswith("generated/checkpoint-") or title.startswith("generated: deterministic checkpoint ")
        if not is_checkpoint:
            continue
        checkpoint_count += 1
        if item["state"] == "OPEN":
            raise GeneratedCheckpointError("another generated checkpoint PR is already open", "GENERATED_CHECKPOINT_PR_COLLISION")
        if title == expected_title:
            raise GeneratedCheckpointError("generated checkpoint mission identity was already used", "GENERATED_CHECKPOINT_MISSION_REPLAY")
        if replay_marker in body:
            raise GeneratedCheckpointError("generated checkpoint nonce identity was already used", "GENERATED_CHECKPOINT_NONCE_REPLAY")
    return {
        "history_entries_checked": len(pull_requests),
        "checkpoint_entries_checked": checkpoint_count,
        "open_checkpoint_prs": 0,
        "mission_identity_reused": False,
        "nonce_identity_reused": False,
    }


def verify_generated_checkpoint_environment(profile: dict[str, Any], environment: Mapping[str, str] | None = None) -> dict[str, Any]:
    env = environment or os.environ
    expected = {
        "GITHUB_ACTIONS": "true",
        "GITHUB_REPOSITORY": profile["repository"],
        "GITHUB_REPOSITORY_OWNER": profile["repository_owner"],
        "GITHUB_ACTOR": profile["actor"],
        "GITHUB_TRIGGERING_ACTOR": profile["triggering_actor"],
        "GITHUB_EVENT_NAME": profile["event_name"],
        "GITHUB_REF": "refs/heads/main",
        "GITHUB_WORKFLOW_REF": profile["workflow_ref"],
        "GITHUB_WORKFLOW_SHA": profile["workflow_source_sha"],
        "GITHUB_SHA": profile["base_sha"],
        "GITHUB_RUN_ID": profile["workflow_run_id"],
        "GITHUB_RUN_ATTEMPT": profile["workflow_run_attempt"],
    }
    mismatches = [field for field, value in expected.items() if env.get(field) != value]
    if mismatches:
        raise GeneratedCheckpointError(
            f"generated checkpoint hosted environment mismatch: {', '.join(mismatches)}",
            "GENERATED_CHECKPOINT_ENVIRONMENT",
        )
    if not env.get("GH_TOKEN"):
        raise GeneratedCheckpointError("generated checkpoint credential is absent", "GENERATED_CHECKPOINT_CREDENTIAL")
    return {
        "github_actions": True,
        "repository": profile["repository"],
        "repository_owner": profile["repository_owner"],
        "actor": profile["actor"],
        "triggering_actor": profile["triggering_actor"],
        "event_name": profile["event_name"],
        "workflow_ref": profile["workflow_ref"],
        "workflow_source_sha": profile["workflow_source_sha"],
        "run_id": profile["workflow_run_id"],
        "run_attempt": profile["workflow_run_attempt"],
        "credential_principal": profile["credential_principal"],
        "credential_mode": profile["credential_mode"],
        "token_present": True,
    }
