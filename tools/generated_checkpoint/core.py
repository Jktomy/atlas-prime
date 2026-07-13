from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

from tools.build_index import APPROVED_OUTPUTS, GENERATOR_FORMAT, build_outputs, output_bytes
THREAD_ENGINE_ROOT = Path(__file__).resolve().parents[1] / "thread-engine"
if str(THREAD_ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(THREAD_ENGINE_ROOT))

from production_adapter.authority import operation_set_sha256
from production_adapter.generated_checkpoint import (
    APPROVED_PATHS,
    RECONCILIATION_SCHEMA,
    REGISTER_SCHEMA,
    deterministic_branch,
)
from production_adapter.receipt import (
    declared_state_hash,
    sha256_bytes,
    stable_json,
    tree_hash,
)


class PreparationError(Exception):
    def __init__(self, message: str, code: str = "GENERATED_CHECKPOINT_PREPARATION_REJECTED") -> None:
        super().__init__(message)
        self.code = code


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def replay_nonce_sha256(replay_nonce: str) -> str:
    if not isinstance(replay_nonce, str) or len(replay_nonce) < 24 or len(replay_nonce) > 200:
        raise PreparationError("replay nonce length is outside the accepted public-clean range", "GENERATED_CHECKPOINT_REPLAY_NONCE")
    return sha256_bytes(replay_nonce.encode("utf-8"))


def build_hash_register(
    repo_root: Path,
    *,
    mission_id: str,
    base_sha: str,
    replay_nonce: str,
    workflow_ref: str,
    workflow_source_sha: str,
    workflow_run_id: str,
    workflow_run_attempt: str,
) -> tuple[dict[str, Any], dict[str, bytes]]:
    outputs, source_fingerprint = build_outputs(repo_root.resolve())
    output_map = {f"generated/{name}": output_bytes(outputs[name]) for name in APPROVED_OUTPUTS}
    if tuple(output_map) != APPROVED_PATHS:
        raise PreparationError("generator output set is not the approved ordered set", "GENERATED_CHECKPOINT_PATH_SET")
    nonce_digest = replay_nonce_sha256(replay_nonce)
    register = {
        "schema_id": REGISTER_SCHEMA,
        "schema_version": "1.0.0",
        "mission_id": mission_id,
        "repository": "Jktomy/atlas-prime",
        "base_sha": base_sha,
        "workflow_ref": workflow_ref,
        "workflow_source_sha": workflow_source_sha,
        "workflow_run_id": workflow_run_id,
        "workflow_run_attempt": workflow_run_attempt,
        "replay_nonce_sha256": nonce_digest,
        "generator_format": GENERATOR_FORMAT,
        "source_fingerprint": f"sha256:{source_fingerprint}",
        "files": [
            {"path": path, "sha256": sha256_bytes(output_map[path])}
            for path in APPROVED_PATHS
        ],
    }
    return register, output_map


def reconcile_registers(ubuntu_path: Path, windows_path: Path) -> dict[str, Any]:
    ubuntu = ubuntu_path.read_bytes()
    windows = windows_path.read_bytes()
    if ubuntu != windows:
        raise PreparationError("Ubuntu and Windows registers are not byte-identical", "GENERATED_CHECKPOINT_PARITY")
    try:
        register = json.loads(ubuntu.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PreparationError("parity register is invalid JSON", "GENERATED_CHECKPOINT_REGISTER") from exc
    if not isinstance(register, dict) or ubuntu != stable_json(register).encode("utf-8") or register.get("schema_id") != REGISTER_SCHEMA:
        raise PreparationError("parity register is not canonical", "GENERATED_CHECKPOINT_REGISTER")
    digest = sha256_bytes(ubuntu)
    return {
        "schema_id": RECONCILIATION_SCHEMA,
        "schema_version": "1.0.0",
        "mission_id": register["mission_id"],
        "repository": register["repository"],
        "base_sha": register["base_sha"],
        "workflow_ref": register["workflow_ref"],
        "workflow_source_sha": register["workflow_source_sha"],
        "workflow_run_id": register["workflow_run_id"],
        "workflow_run_attempt": register["workflow_run_attempt"],
        "replay_nonce_sha256": register["replay_nonce_sha256"],
        "register_sha256": digest,
        "ubuntu_register_sha256": digest,
        "windows_register_sha256": digest,
        "byte_identical": True,
    }


def _load_canonical(path: Path) -> tuple[dict[str, Any], bytes]:
    raw = path.read_bytes()
    try:
        data = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PreparationError("checkpoint evidence is invalid JSON", "GENERATED_CHECKPOINT_JSON") from exc
    if not isinstance(data, dict) or raw != stable_json(data).encode("utf-8"):
        raise PreparationError("checkpoint evidence is not canonical", "GENERATED_CHECKPOINT_JSON")
    return data, raw


def prepare_package(
    repo_root: Path,
    register_path: Path,
    reconciliation_path: Path,
    package_root: Path,
    *,
    replay_nonce: str,
    public_clean_confirmation: str,
) -> dict[str, Any]:
    if public_clean_confirmation != "PUBLIC_CLEAN_CONFIRMED":
        raise PreparationError("public-clean confirmation is absent", "GENERATED_CHECKPOINT_PRIVACY")
    repo_root = repo_root.resolve()
    package_root = package_root.resolve()
    if package_root.exists() and any(package_root.iterdir()):
        raise PreparationError("package root must be absent or empty", "GENERATED_CHECKPOINT_PACKAGE_ROOT")
    register, register_bytes = _load_canonical(register_path)
    reconciliation, reconciliation_bytes = _load_canonical(reconciliation_path)
    rebuilt, outputs = build_hash_register(
        repo_root,
        mission_id=register.get("mission_id", ""),
        base_sha=register.get("base_sha", ""),
        replay_nonce=replay_nonce,
        workflow_ref=register.get("workflow_ref", ""),
        workflow_source_sha=register.get("workflow_source_sha", ""),
        workflow_run_id=register.get("workflow_run_id", ""),
        workflow_run_attempt=register.get("workflow_run_attempt", ""),
    )
    if stable_json(rebuilt).encode("utf-8") != register_bytes:
        raise PreparationError("publisher reproduction differs from reconciled register", "GENERATED_CHECKPOINT_REPRODUCTION")
    register_digest = sha256_bytes(register_bytes)
    identity_fields = (
        "mission_id", "repository", "base_sha", "workflow_ref", "workflow_source_sha",
        "workflow_run_id", "workflow_run_attempt", "replay_nonce_sha256",
    )
    if (
        reconciliation.get("schema_id") != RECONCILIATION_SCHEMA
        or reconciliation.get("byte_identical") is not True
        or any(reconciliation.get(field) != register.get(field) for field in identity_fields)
        or reconciliation.get("register_sha256") != register_digest
        or reconciliation.get("ubuntu_register_sha256") != register_digest
        or reconciliation.get("windows_register_sha256") != register_digest
    ):
        raise PreparationError("reconciliation does not bind the exact register", "GENERATED_CHECKPOINT_RECONCILIATION")
    if register["base_sha"] != register["workflow_source_sha"]:
        raise PreparationError("workflow source must equal the requested base", "GENERATED_CHECKPOINT_WORKFLOW_SOURCE")

    payload_root = package_root / "payloads"
    evidence_root = package_root / "evidence"
    final_root = package_root / "final"
    payload_root.mkdir(parents=True)
    evidence_root.mkdir(parents=True)
    final_root.mkdir(parents=True)
    (evidence_root / "hash-register.json").write_bytes(register_bytes)
    (evidence_root / "reconciliation.json").write_bytes(reconciliation_bytes)

    operations: list[dict[str, Any]] = []
    source_blobs: dict[str, str] = {}
    for index, path in enumerate(APPROVED_PATHS, start=1):
        current_path = repo_root.joinpath(*path.split("/"))
        if not current_path.is_file() or current_path.is_symlink():
            raise PreparationError(f"committed generated source is missing: {path}", "GENERATED_CHECKPOINT_SOURCE")
        current = current_path.read_bytes()
        candidate = outputs[path]
        if current == candidate:
            raise PreparationError(f"generated output has no delta: {path}", "NO_GENERATED_DELTA")
        payload_path = payload_root.joinpath(*path.split("/"))
        final_path = final_root.joinpath(*path.split("/"))
        payload_path.parent.mkdir(parents=True, exist_ok=True)
        final_path.parent.mkdir(parents=True, exist_ok=True)
        payload_path.write_bytes(candidate)
        final_path.write_bytes(candidate)
        source_sha = sha256_bytes(current)
        output_sha = sha256_bytes(candidate)
        source_blobs[path] = git_blob_sha(current)
        operations.append(
            {
                "thread_id": f"generated-checkpoint-{index:02d}",
                "operation": "REPLACE",
                "path": path,
                "payload": path,
                "source_sha256": source_sha,
                "payload_sha256": output_sha,
                "expected_output_sha256": output_sha,
            }
        )

    mission_id = register["mission_id"]
    replay_digest = register["replay_nonce_sha256"]
    branch = deterministic_branch(mission_id, replay_digest)
    workflow_path = repo_root / ".github" / "workflows" / "generated-checkpoint-publisher.yml"
    if not workflow_path.is_file() or workflow_path.is_symlink():
        raise PreparationError("generated checkpoint workflow source is absent", "GENERATED_CHECKPOINT_WORKFLOW_SOURCE")
    profile = {
        "schema_id": "atlas.generated-checkpoint.profile",
        "schema_version": "1.0.0",
        "profile_id": "GENERATED_CHECKPOINT_V1",
        "mission_id": mission_id,
        "repository": "Jktomy/atlas-prime",
        "base_sha": register["base_sha"],
        "branch": branch,
        "declared_paths": list(APPROVED_PATHS),
        "source_blobs": source_blobs,
        "candidate_tree_sha256": tree_hash(payload_root),
        "final_pathset_sha256": declared_state_hash(final_root, APPROVED_PATHS),
        "operation_set_sha256": operation_set_sha256(operations),
        "source_fingerprint": register["source_fingerprint"],
        "hash_register_path": "evidence/hash-register.json",
        "hash_register_sha256": register_digest,
        "reconciliation_path": "evidence/reconciliation.json",
        "reconciliation_sha256": sha256_bytes(reconciliation_bytes),
        "workflow_ref": register["workflow_ref"],
        "workflow_source_sha": register["workflow_source_sha"],
        "workflow_blob_sha": git_blob_sha(workflow_path.read_bytes()),
        "workflow_run_id": register["workflow_run_id"],
        "workflow_run_attempt": register["workflow_run_attempt"],
        "event_name": "workflow_dispatch",
        "actor": "Jktomy",
        "triggering_actor": "Jktomy",
        "repository_owner": "Jktomy",
        "credential_principal": "github-actions[bot]",
        "credential_mode": "GITHUB_TOKEN",
        "replay_nonce_sha256": replay_digest,
        "public_clean_confirmation": "PUBLIC_CLEAN_CONFIRMED",
        "stop_point": "DRAFT_PR_READBACK",
        "persistent_writer": "ABSENT",
        "direct_main_write": False,
        "force_push": False,
        "automatic_ready": False,
        "automatic_merge": False,
        "workflow_dispatch": False,
        "repository_setting_mutation": False,
        "quest_promotion": False,
        "capability_promotion": False,
        "automatic_retry": False,
        "standing_authority": "NO",
    }
    mission = {
        "schema_version": "atlas-thread-engine-production-mission-v1",
        "implementation_state": "THREAD_ENGINE_ACTIVE_MISSION_SCOPED",
        "adapter_mode": "DRAFT_PR_ONLY",
        "persistent_writer": "ABSENT",
        "activation_authority": "MISSION_SCOPED",
        "mission_id": mission_id,
        "authority_id": f"{mission_id}-GENERATED-CHECKPOINT",
        "build_identity": f"{mission_id}-HOSTED-PARITY-BUILD",
        "execute_identity": f"{mission_id}-THREAD-ENGINE-EXECUTE",
        "mission_sha256": "0" * 64,
        "repository": "Jktomy/atlas-prime",
        "remote_url": "https://github.com/Jktomy/atlas-prime.git",
        "base_sha": register["base_sha"],
        "branch": branch,
        "commit_message": f"generated: deterministic checkpoint {mission_id}",
        "pr_title": f"generated: deterministic checkpoint {mission_id}",
        "pr_body": (
            f"Hosted RP-C06 generated checkpoint `{mission_id}`.\n\n"
            f"- Exact base: `{register['base_sha']}`\n"
            f"- Source fingerprint: `{register['source_fingerprint']}`\n"
            f"- Workflow run: `{register['workflow_run_id']}` attempt `{register['workflow_run_attempt']}`\n"
            f"- Replay identity: `sha256:{replay_digest}`\n"
            "- Ubuntu/Windows register parity: exact\n"
            "- Route: singular Thread Engine; draft PR readback stop\n"
            "- Quest/capability promotion: none\n"
        ),
        "declared_paths": list(APPROVED_PATHS),
        "payload_root": "payloads",
        "candidate_tree_sha256": profile["candidate_tree_sha256"],
        "final_pathset_sha256": profile["final_pathset_sha256"],
        "source_blobs": source_blobs,
        "operations": operations,
        "generated_checkpoint_profile": profile,
        "network_allowlist": [
            "https://github.com/Jktomy/atlas-prime.git",
            "https://api.github.com/repos/Jktomy/atlas-prime",
        ],
        "receipt_name": f"{mission_id.lower()}-thread-engine-receipt.json",
        "stop_point": "DRAFT_PR_READBACK",
    }
    mission["mission_sha256"] = sha256_bytes(stable_json(mission).encode("utf-8"))
    (package_root / "mission.json").write_text(stable_json(mission), encoding="utf-8", newline="\n")
    return mission
