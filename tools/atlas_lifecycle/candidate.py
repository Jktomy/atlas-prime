from __future__ import annotations

import hashlib
import tempfile
from pathlib import Path
from typing import Any

from .errors import LifecycleError
from .event_paths import declared_event_path
from .jsonio import canonical_bytes, load_bounded, read_bounded, stable_record_id
from .planner import plan_event
from .schema import SchemaValidator


ARTIFACT_EVENT = "event.json"
ARTIFACT_MANIFEST = "candidate-manifest.json"
ARTIFACT_RECEIPT = "candidate-receipt.json"


def _digest(data: bytes) -> str:
    return f"sha256:{hashlib.sha256(data).hexdigest()}"


def _write_boundary() -> dict[str, Any]:
    return {
        "output_scope": "SYSTEM_TEMPORARY_DIRECTORY",
        "canonical_writes": False,
        "direct_main": False,
        "github_actions": [],
        "automatic_merge": False,
    }


def _validated_output_path(repo_root: Path, output_dir: Path) -> Path:
    if not output_dir.is_absolute():
        raise LifecycleError("CANDIDATE_OUTPUT_PATH", "candidate output directory must be absolute")
    if output_dir.exists() or output_dir.is_symlink():
        raise LifecycleError("CANDIDATE_OUTPUT_EXISTS", "candidate output directory must not already exist")
    parent = output_dir.parent
    if not parent.is_dir() or parent.is_symlink():
        raise LifecycleError("CANDIDATE_OUTPUT_PARENT", "candidate output parent must be a regular directory")
    temporary_root = Path(tempfile.gettempdir()).resolve()
    try:
        lexical_parent = parent.absolute().relative_to(temporary_root)
    except ValueError as exc:
        raise LifecycleError(
            "CANDIDATE_OUTPUT_BOUNDARY",
            "candidate output must remain beneath the system temporary directory",
        ) from exc
    if any(part in {"", ".", ".."} for part in lexical_parent.parts):
        raise LifecycleError("CANDIDATE_OUTPUT_PATH", "candidate output path is not normalized")
    lexical_cursor = temporary_root
    for part in lexical_parent.parts:
        lexical_cursor = lexical_cursor / part
        if lexical_cursor.is_symlink():
            raise LifecycleError("CANDIDATE_OUTPUT_SYMLINK", "candidate output ancestry contains a symlink")
    resolved_parent = parent.resolve()
    try:
        relative_parent = resolved_parent.relative_to(temporary_root)
    except ValueError as exc:
        raise LifecycleError(
            "CANDIDATE_OUTPUT_BOUNDARY",
            "candidate output must remain beneath the system temporary directory",
        ) from exc
    resolved_output = resolved_parent / output_dir.name
    folded_name = output_dir.name.casefold()
    if any(member.name.casefold() == folded_name for member in resolved_parent.iterdir()):
        raise LifecycleError("CANDIDATE_OUTPUT_COLLISION", "candidate output name case-fold collides")
    try:
        resolved_output.relative_to(repo_root.resolve())
    except ValueError:
        pass
    else:
        raise LifecycleError("CANDIDATE_REPOSITORY_WRITE", "candidate output cannot be inside the repository")
    return resolved_output


def _reject_existing_event_path(repo_root: Path, repository_path: str) -> None:
    target = repo_root.resolve() / Path(*repository_path.split("/"))
    if target.exists() or target.is_symlink():
        raise LifecycleError("EVENT_PATH_ALREADY_EXISTS", "declared event path is already occupied")
    parent = target.parent
    if parent.exists():
        if not parent.is_dir() or parent.is_symlink():
            raise LifecycleError("EVENT_PATH_PARENT", "canonical event directory is unsafe")
        folded = target.name.casefold()
        if any(member.name.casefold() == folded for member in parent.iterdir()):
            raise LifecycleError("EVENT_PATH_COLLISION", "declared event path case-fold collides")


def _write_exact(path: Path, data: bytes) -> None:
    try:
        with path.open("xb") as handle:
            handle.write(data)
    except OSError as exc:
        raise LifecycleError("CANDIDATE_WRITE_FAILED", "temporary candidate output could not be written") from exc
    if read_bounded(path) != data:
        raise LifecycleError("CANDIDATE_READBACK", "temporary candidate readback does not match")


def verify_candidate_set(
    output_dir: Path,
    schema_dir: Path,
    *,
    expected_event_id: str,
    expected_repository_path: str,
    expected_trust_root_digest: str,
    expected_state_digest: str,
) -> str:
    """Verify exact members, schemas, digests, and ID/path cross-bindings."""
    if not output_dir.is_dir() or output_dir.is_symlink():
        raise LifecycleError("CANDIDATE_SET_DIRECTORY", "candidate set directory is unsafe")
    members = sorted(output_dir.iterdir(), key=lambda path: path.name)
    expected_names = [ARTIFACT_MANIFEST, ARTIFACT_RECEIPT, ARTIFACT_EVENT]
    if [path.name for path in members] != expected_names or any(
        not path.is_file() or path.is_symlink() for path in members
    ):
        raise LifecycleError("CANDIDATE_SET_MEMBERS", "candidate set has an unexpected or unsafe member")
    event = load_bounded(output_dir / ARTIFACT_EVENT)
    manifest = load_bounded(output_dir / ARTIFACT_MANIFEST)
    receipt = load_bounded(output_dir / ARTIFACT_RECEIPT)
    validator = SchemaValidator(schema_dir)
    validator.validate_record(event)
    validator.validate_event_candidate_manifest(manifest)
    validator.validate_event_candidate_receipt(receipt)
    if event.get("authority") != "CANONICAL_RECORD" or stable_record_id(event) != event.get("record_id"):
        raise LifecycleError("CANDIDATE_EVENT_IDENTITY", "candidate event identity is invalid")
    repository_path = declared_event_path(event)
    event_digest = _digest(read_bounded(output_dir / ARTIFACT_EVENT))
    manifest_digest = _digest(read_bounded(output_dir / ARTIFACT_MANIFEST))
    receipt_digest = _digest(read_bounded(output_dir / ARTIFACT_RECEIPT))
    binding = manifest["event_binding"]
    if (
        event["record_id"] != expected_event_id
        or repository_path != expected_repository_path
        or binding["record_id"] != event["record_id"]
        or binding["repository_path"] != repository_path
        or binding["payload_digest"] != event_digest
        or manifest["allowed_paths"] != [repository_path]
        or receipt["event_record_id"] != event["record_id"]
        or receipt["repository_path"] != repository_path
        or receipt["candidate_payload_digest"] != event_digest
        or receipt["manifest_digest"] != manifest_digest
        or receipt["expected_main_sha"] != manifest["locks"]["expected_main_sha"]
        or receipt["expected_entity_revision"] != manifest["locks"]["expected_entity_revision"]
        or receipt["trust_root_digest"] != manifest["trusted_bindings"]["trust_root_digest"]
        or receipt["state_snapshot_digest"] != manifest["trusted_bindings"]["state_snapshot_digest"]
        or receipt["replay_key"] != event["replay_key"]
        or receipt["output_members"] != [
            {"artifact_path": ARTIFACT_EVENT, "digest": event_digest},
            {"artifact_path": ARTIFACT_MANIFEST, "digest": manifest_digest},
        ]
    ):
        raise LifecycleError("CANDIDATE_BINDING_MISMATCH", "candidate set cross-binding is invalid")
    if (
        manifest["trusted_bindings"]["trust_root_digest"] != expected_trust_root_digest
        or manifest["trusted_bindings"]["state_snapshot_digest"] != expected_state_digest
    ):
        raise LifecycleError(
            "CANDIDATE_TRUST_BINDING",
            "candidate set does not match independently supplied trusted expectations",
        )
    output_members = [
        {"artifact_path": ARTIFACT_EVENT, "digest": event_digest},
        {"artifact_path": ARTIFACT_MANIFEST, "digest": manifest_digest},
        {"artifact_path": ARTIFACT_RECEIPT, "digest": receipt_digest},
    ]
    return _digest(canonical_bytes({"members": output_members}))


def generate_event_candidate(
    repo_root: Path,
    event_path: Path,
    trust_root_path: Path,
    expected_trust_root_digest: str,
    state_path: Path,
    expected_state_digest: str,
    output_dir: Path,
) -> dict[str, Any]:
    """Generate a deterministic Level 1B candidate set in fresh temporary output."""
    root = repo_root.resolve()
    plan = plan_event(
        root,
        event_path,
        trust_root_path,
        expected_trust_root_digest,
        state_path,
        expected_state_digest,
    )
    event = load_bounded(event_path)
    if event.get("authority") != "CANONICAL_RECORD":
        raise LifecycleError(
            "CANDIDATE_EVENT_AUTHORITY",
            "candidate generation requires final canonical-record authority bytes",
        )
    repository_path = declared_event_path(event)
    _reject_existing_event_path(root, repository_path)
    destination = _validated_output_path(root, output_dir)
    trust = load_bounded(root / "lifecycle/trust-roots" / trust_root_path)

    event_bytes = canonical_bytes(event)
    event_digest = _digest(event_bytes)
    expected = event["expectations"]
    manifest = {
        "schema_id": "atlas.lifecycle.event-candidate-manifest",
        "schema_version": "1.0.0",
        "authority": "TEMPORARY_CANDIDATE_ONLY",
        "engine_class": "SCRIPT_ASSIST_LEVEL_1B",
        "event_binding": {
            "record_id": event["record_id"],
            "repository_path": repository_path,
            "artifact_path": ARTIFACT_EVENT,
            "schema_id": event["schema_id"],
            "schema_version": event["schema_version"],
            "event_class": event["event_class"],
            "event_type": event["event_type"],
            "payload_digest": event_digest,
        },
        "locks": {
            "expected_main_sha": expected["expected_main_sha"],
            "expected_entity_revision": expected["expected_entity_revision"],
            "expected_quest_revision": expected["expected_quest_revision"],
            "expected_gate_revision": expected["expected_gate_revision"],
            "expected_parent_checkpoint_id": expected["expected_parent_checkpoint_id"],
            "expected_source_fingerprint": expected["expected_source_fingerprint"],
            "route_authority": event["route"]["route_authority"],
        },
        "trusted_bindings": {
            "trust_root_digest": expected_trust_root_digest,
            "state_snapshot_digest": expected_state_digest,
            "accepted_event_schema_digest": trust["accepted_event_schema_digest"],
            "acceptance_contract_digest": trust["acceptance_contract_digest"],
        },
        "allowed_paths": [repository_path],
        "write_boundary": _write_boundary(),
    }
    validator = SchemaValidator(root / "lifecycle/schemas")
    validator.validate_event_candidate_manifest(manifest)
    manifest_bytes = canonical_bytes(manifest)
    manifest_digest = _digest(manifest_bytes)
    receipt = {
        "schema_id": "atlas.lifecycle.event-candidate-receipt",
        "schema_version": "1.0.0",
        "authority": "TEMPORARY_CANDIDATE_ONLY",
        "engine_class": "SCRIPT_ASSIST_LEVEL_1B",
        "event_record_id": event["record_id"],
        "repository_path": repository_path,
        "candidate_payload_digest": event_digest,
        "manifest_digest": manifest_digest,
        "expected_main_sha": plan["exact_main_sha"],
        "expected_entity_revision": plan["exact_entity_revision"],
        "trust_root_digest": expected_trust_root_digest,
        "state_snapshot_digest": expected_state_digest,
        "replay_key": event["replay_key"],
        "output_members": [
            {"artifact_path": ARTIFACT_EVENT, "digest": event_digest},
            {"artifact_path": ARTIFACT_MANIFEST, "digest": manifest_digest},
        ],
        "write_boundary": _write_boundary(),
        "verification_result": "PASS",
    }
    validator.validate_event_candidate_receipt(receipt)
    receipt_bytes = canonical_bytes(receipt)
    receipt_digest = _digest(receipt_bytes)
    members = [
        {"artifact_path": ARTIFACT_EVENT, "digest": event_digest},
        {"artifact_path": ARTIFACT_MANIFEST, "digest": manifest_digest},
        {"artifact_path": ARTIFACT_RECEIPT, "digest": receipt_digest},
    ]
    candidate_set_digest = _digest(canonical_bytes({"members": members}))

    try:
        destination.mkdir(mode=0o700)
    except OSError as exc:
        raise LifecycleError("CANDIDATE_OUTPUT_CREATE", "temporary candidate directory could not be created") from exc
    _write_exact(destination / ARTIFACT_EVENT, event_bytes)
    _write_exact(destination / ARTIFACT_MANIFEST, manifest_bytes)
    _write_exact(destination / ARTIFACT_RECEIPT, receipt_bytes)
    verified_set_digest = verify_candidate_set(
        destination,
        root / "lifecycle/schemas",
        expected_event_id=event["record_id"],
        expected_repository_path=repository_path,
        expected_trust_root_digest=expected_trust_root_digest,
        expected_state_digest=expected_state_digest,
    )
    if verified_set_digest != candidate_set_digest:
        raise LifecycleError("CANDIDATE_SET_DIGEST", "candidate set digest does not match readback")
    return {
        "authority": "TEMPORARY_CANDIDATE_ONLY",
        "command": "event candidate",
        "engine_class": "SCRIPT_ASSIST_LEVEL_1B",
        "event_id": event["record_id"],
        "repository_path": repository_path,
        "expected_main_sha": plan["exact_main_sha"],
        "expected_entity_revision": plan["exact_entity_revision"],
        "output_members": members,
        "candidate_set_digest": candidate_set_digest,
        "writes_performed": ["SYSTEM_TEMPORARY_DIRECTORY"],
        "canonical_writes": False,
        "github_actions": [],
        "status": "PASS",
    }
