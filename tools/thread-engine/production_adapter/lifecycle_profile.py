from __future__ import annotations

import base64
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


PRIME_ROOT = Path(__file__).resolve().parents[3]
if str(PRIME_ROOT) not in sys.path:
    sys.path.insert(0, str(PRIME_ROOT))

from tools.atlas_lifecycle.errors import LifecycleError
from tools.atlas_lifecycle.protection import enforce_clean_values, enforce_pointer_contract
from tools.atlas_lifecycle.schema import SchemaValidator


MAX_CANDIDATE_BYTES = 1024 * 1024
MAX_CANONICAL_EVENTS = 1000
MAX_CANONICAL_EVENT_BYTES = 32 * 1024 * 1024
MAX_JSON_DEPTH = 64
MAX_JSON_NODES = 20000
FINGERPRINT = re.compile(r"^sha256:[a-f0-9]{64}$")
EVENT_ID = re.compile(r"^LEV-[A-Z2-7]{26}$")
EVENT_PATH = re.compile(r"^lifecycle/events/[A-Za-z0-9](?:[A-Za-z0-9._-]*[A-Za-z0-9])?[.]json$")
ATLAS_IDENTITY = re.compile(r"^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$")
ENTITY_TYPES = {
    "QUEST", "CAMPAIGN", "MISSION", "GATE", "LANDMARK", "BLOCKER",
    "FEATHER", "GOLDEN_WING", "ACCEPTANCE", "CAPABILITY", "SUNSET", "SUNRISE",
}
PROFILE_KEYS = {
    "schema_id", "schema_version", "profile_id", "event_record_id",
    "event_class", "event_type", "event_schema_id", "event_schema_version",
    "semantic_author", "repository_path", "allowed_paths", "candidate_root",
    "route_authority", "target_entity_type", "target_entity_id",
    "expected_main_sha", "expected_entity_revision",
    "expected_quest_revision", "expected_gate_revision", "expected_parent_event_id",
    "expected_source_fingerprint", "candidate_event_digest",
    "candidate_manifest_digest", "candidate_receipt_digest", "candidate_set_digest",
    "trust_root_digest", "state_snapshot_digest", "trusted_acceptance_receipt_digest",
    "protected_data_classification", "replay_key", "lineage", "rollback_contract",
    "reversal_contract", "stop_boundary", "write_boundary",
}
LINEAGE_KEYS = {
    "parent_event_id", "supersedes_event_id", "invalidates_event_id",
    "reverses_event_id", "revokes_event_id", "reopens_event_id",
}
WRITE_BOUNDARY = {
    "branch_scoped_only": True,
    "canonical_writes": False,
    "direct_main": False,
    "automatic_ready": False,
    "automatic_merge": False,
    "standing_authority": False,
}


class LifecycleProfileError(Exception):
    def __init__(self, message: str, code: str = "LIFECYCLE_PROFILE_REJECTED") -> None:
        super().__init__(message)
        self.code = code


def _digest(data: bytes) -> str:
    return f"sha256:{hashlib.sha256(data).hexdigest()}"


def _canonical(value: dict[str, Any]) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise LifecycleProfileError("candidate JSON contains a duplicate key", "LIFECYCLE_DUPLICATE_JSON_KEY")
        result[key] = value
    return result


def _forbid_float(value: str) -> None:
    raise LifecycleProfileError("candidate JSON floating-point values are forbidden", "LIFECYCLE_FLOAT_REJECTED")


def _check_bounds(value: Any, depth: int = 0, count: list[int] | None = None) -> None:
    if count is None:
        count = [0]
    count[0] += 1
    if count[0] > MAX_JSON_NODES or depth > MAX_JSON_DEPTH:
        raise LifecycleProfileError("candidate JSON exceeds parsing bounds", "LIFECYCLE_JSON_LIMIT")
    if isinstance(value, dict):
        for nested in value.values():
            _check_bounds(nested, depth + 1, count)
    elif isinstance(value, list):
        for nested in value:
            _check_bounds(nested, depth + 1, count)


def _load_canonical(path: Path) -> tuple[dict[str, Any], bytes]:
    if not path.is_file() or path.is_symlink() or path.stat().st_size > MAX_CANDIDATE_BYTES:
        raise LifecycleProfileError("candidate member is unsafe or oversized", "LIFECYCLE_CANDIDATE_MEMBER")
    data = path.read_bytes()
    try:
        value = json.loads(
            data.decode("utf-8"),
            object_pairs_hook=_pairs,
            parse_float=_forbid_float,
            parse_constant=_forbid_float,
        )
    except LifecycleProfileError:
        raise
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise LifecycleProfileError("candidate member is malformed", "LIFECYCLE_CANDIDATE_JSON") from exc
    if not isinstance(value, dict):
        raise LifecycleProfileError("candidate member root must be an object", "LIFECYCLE_CANDIDATE_JSON")
    _check_bounds(value)
    if _canonical(value) != data:
        raise LifecycleProfileError("candidate member is not canonically serialized", "LIFECYCLE_NONCANONICAL_JSON")
    return value, data


def _trusted_digest(relative: str) -> str:
    path = PRIME_ROOT.joinpath(*relative.split("/"))
    if not path.is_file() or path.is_symlink() or path.stat().st_size > MAX_CANDIDATE_BYTES:
        raise LifecycleProfileError("trusted lifecycle source is unavailable", "LIFECYCLE_TRUSTED_SOURCE")
    return _digest(path.read_bytes())


def _require_fingerprint(value: Any, field: str) -> str:
    if not isinstance(value, str) or FINGERPRINT.fullmatch(value) is None:
        raise LifecycleProfileError(f"{field} is not a trusted digest", "LIFECYCLE_PROFILE_SCHEMA")
    return value


def _require_event_id(value: Any, field: str, *, nullable: bool = False) -> str | None:
    if nullable and value is None:
        return None
    if not isinstance(value, str) or EVENT_ID.fullmatch(value) is None:
        raise LifecycleProfileError(f"{field} is not a lifecycle event ID", "LIFECYCLE_PROFILE_SCHEMA")
    return value


def validate_lifecycle_profile(profile: Any, mission: dict[str, Any]) -> dict[str, Any] | None:
    if profile is None:
        return None
    if not isinstance(profile, dict) or set(profile) != PROFILE_KEYS:
        raise LifecycleProfileError("lifecycle profile has an invalid closed shape", "LIFECYCLE_PROFILE_SCHEMA")
    if profile["schema_id"] != "atlas.lifecycle.construction-profile" or profile["schema_version"] != "1.0.0":
        raise LifecycleProfileError("lifecycle profile identity is invalid", "LIFECYCLE_PROFILE_SCHEMA")
    expected_profile = {
        "CHECKPOINT": "LIFECYCLE_CHECKPOINT_V1",
        "TRANSITION": "LIFECYCLE_TRANSITION_V1",
    }.get(profile["event_class"])
    if expected_profile is None or profile["profile_id"] != expected_profile:
        raise LifecycleProfileError("lifecycle event class and profile disagree", "LIFECYCLE_PROFILE_CLASS")
    _require_event_id(profile["event_record_id"], "event_record_id")
    if profile["event_schema_id"] != "atlas.lifecycle.event" or profile["event_schema_version"] != "1.0.0":
        raise LifecycleProfileError("lifecycle event schema identity is invalid", "LIFECYCLE_PROFILE_SCHEMA")
    if not isinstance(profile["event_type"], str) or not profile["event_type"]:
        raise LifecycleProfileError("lifecycle event type is missing", "LIFECYCLE_PROFILE_SCHEMA")
    if not isinstance(profile["semantic_author"], str) or not profile["semantic_author"]:
        raise LifecycleProfileError("lifecycle semantic author is missing", "LIFECYCLE_PROFILE_SCHEMA")
    repository_path = profile["repository_path"]
    if not isinstance(repository_path, str) or EVENT_PATH.fullmatch(repository_path) is None:
        raise LifecycleProfileError("lifecycle repository path is invalid", "LIFECYCLE_PROFILE_PATH")
    if profile["allowed_paths"] != [repository_path]:
        raise LifecycleProfileError("lifecycle allowed path is not exact", "LIFECYCLE_PROFILE_PATH")
    if profile["candidate_root"] != "payload/lifecycle-candidate" or mission.get("payload_root") != profile["candidate_root"]:
        raise LifecycleProfileError("lifecycle candidate root is invalid", "LIFECYCLE_PROFILE_PATH")
    if profile["route_authority"] != "AEGIS_BREAK_THREAD_ENGINE_PROTECTED":
        raise LifecycleProfileError("lifecycle route is not the approved protected route", "LIFECYCLE_PROFILE_ROUTE")
    if profile["target_entity_type"] not in ENTITY_TYPES:
        raise LifecycleProfileError("target_entity_type is invalid", "LIFECYCLE_PROFILE_SCHEMA")
    if not isinstance(profile["target_entity_id"], str) or ATLAS_IDENTITY.fullmatch(profile["target_entity_id"]) is None:
        raise LifecycleProfileError("target_entity_id is invalid", "LIFECYCLE_PROFILE_SCHEMA")
    if profile["expected_main_sha"] != mission.get("base_sha"):
        raise LifecycleProfileError("lifecycle expected base does not match mission base", "LIFECYCLE_PROFILE_BASE")
    for field in ("expected_entity_revision",):
        if not isinstance(profile[field], int) or isinstance(profile[field], bool) or profile[field] < 0:
            raise LifecycleProfileError(f"{field} is invalid", "LIFECYCLE_PROFILE_REVISION")
    for field in ("expected_quest_revision", "expected_gate_revision"):
        if profile[field] is not None and (
            not isinstance(profile[field], int) or isinstance(profile[field], bool) or profile[field] < 0
        ):
            raise LifecycleProfileError(f"{field} is invalid", "LIFECYCLE_PROFILE_REVISION")
    _require_event_id(profile["expected_parent_event_id"], "expected_parent_event_id", nullable=True)
    for field in (
        "expected_source_fingerprint", "candidate_event_digest", "candidate_manifest_digest",
        "candidate_receipt_digest", "candidate_set_digest", "trust_root_digest",
        "state_snapshot_digest", "replay_key",
    ):
        _require_fingerprint(profile[field], field)
    acceptance_digest = profile["trusted_acceptance_receipt_digest"]
    if profile["event_class"] == "CHECKPOINT":
        if acceptance_digest is not None:
            raise LifecycleProfileError("checkpoint cannot claim a transition receipt", "LIFECYCLE_PROFILE_RECEIPT")
    else:
        if not isinstance(acceptance_digest, str) or FINGERPRINT.fullmatch(acceptance_digest) is None:
            raise LifecycleProfileError(
                "transition requires an independently bound acceptance receipt",
                "LIFECYCLE_PROFILE_RECEIPT",
            )
    if profile["protected_data_classification"] not in {"PUBLIC", "INTERNAL_CLEAN", "PROTECTED_POINTER_ONLY"}:
        raise LifecycleProfileError("protected-data classification is invalid", "LIFECYCLE_PROFILE_PROTECTION")
    if not isinstance(profile["lineage"], dict) or set(profile["lineage"]) != LINEAGE_KEYS:
        raise LifecycleProfileError("lifecycle lineage has an invalid closed shape", "LIFECYCLE_PROFILE_LINEAGE")
    for field, value in profile["lineage"].items():
        _require_event_id(value, field, nullable=True)
    for field in ("rollback_contract", "reversal_contract"):
        if not isinstance(profile[field], str) or not profile[field] or len(profile[field]) > 4000:
            raise LifecycleProfileError(f"{field} is invalid", "LIFECYCLE_PROFILE_SCHEMA")
    if profile["stop_boundary"] != "DRAFT_PR_READBACK" or profile["write_boundary"] != WRITE_BOUNDARY:
        raise LifecycleProfileError("lifecycle construction boundary is invalid", "LIFECYCLE_PROFILE_AUTHORITY")
    try:
        SchemaValidator(PRIME_ROOT / "lifecycle/schemas").validate_lifecycle_construction_profile(profile)
    except LifecycleError as exc:
        raise LifecycleProfileError("lifecycle profile violates the trusted schema", "LIFECYCLE_TRUSTED_SCHEMA") from exc

    operations = mission.get("operations")
    if not isinstance(operations, list) or len(operations) != 1 or not isinstance(operations[0], dict):
        raise LifecycleProfileError("lifecycle mission requires one operation", "LIFECYCLE_PROFILE_OPERATION")
    operation = operations[0]
    event_hex = profile["candidate_event_digest"].removeprefix("sha256:")
    if (
        operation.get("operation") != "ADD"
        or operation.get("path") != repository_path
        or operation.get("payload") != "event.json"
        or operation.get("payload_sha256") != event_hex
        or operation.get("expected_output_sha256") != event_hex
        or mission.get("declared_paths") != [repository_path]
        or mission.get("source_blobs") != {}
    ):
        raise LifecycleProfileError("lifecycle mission operation binding is invalid", "LIFECYCLE_PROFILE_OPERATION")
    authority = mission.get("aegis_break_authority")
    if not isinstance(authority, dict) or authority.get("declared_protected_paths") != [repository_path]:
        raise LifecycleProfileError("lifecycle protected route binding is missing", "LIFECYCLE_PROFILE_ROUTE")
    return dict(profile)


def _stable_event_id(event: dict[str, Any]) -> str:
    payload = dict(event)
    payload.pop("record_id", None)
    token = base64.b32encode(hashlib.sha256(_canonical(payload)).digest()).decode("ascii").rstrip("=")[:26]
    return f"LEV-{token}"


def verify_lifecycle_candidate_package(profile: dict[str, Any], package_root: Path) -> dict[str, Any]:
    package_root = package_root.resolve()
    candidate_root = package_root
    for part in profile["candidate_root"].split("/"):
        candidate_root = candidate_root / part
        if candidate_root.is_symlink():
            raise LifecycleProfileError("lifecycle candidate path contains a symlink", "LIFECYCLE_CANDIDATE_ROOT")
        try:
            candidate_root.resolve(strict=False).relative_to(package_root)
        except ValueError as exc:
            raise LifecycleProfileError("lifecycle candidate root escapes its package", "LIFECYCLE_CANDIDATE_ROOT") from exc
    if not candidate_root.is_dir() or candidate_root.is_symlink():
        raise LifecycleProfileError("lifecycle candidate root is unsafe", "LIFECYCLE_CANDIDATE_ROOT")
    members = sorted(candidate_root.iterdir(), key=lambda path: path.name)
    if [path.name for path in members] != ["candidate-manifest.json", "candidate-receipt.json", "event.json"]:
        raise LifecycleProfileError("lifecycle candidate member set is not exact", "LIFECYCLE_CANDIDATE_MEMBERS")
    event, event_bytes = _load_canonical(candidate_root / "event.json")
    manifest, manifest_bytes = _load_canonical(candidate_root / "candidate-manifest.json")
    receipt, receipt_bytes = _load_canonical(candidate_root / "candidate-receipt.json")
    try:
        validator = SchemaValidator(PRIME_ROOT / "lifecycle/schemas")
        validator.validate_record(event)
        validator.validate_event_candidate_manifest(manifest)
        validator.validate_event_candidate_receipt(receipt)
        enforce_clean_values(event)
        enforce_pointer_contract(event)
        enforce_clean_values(profile)
    except LifecycleError as exc:
        raise LifecycleProfileError("lifecycle candidate violates a trusted schema", "LIFECYCLE_TRUSTED_SCHEMA") from exc
    event_digest = _digest(event_bytes)
    manifest_digest = _digest(manifest_bytes)
    receipt_digest = _digest(receipt_bytes)
    output_members = [
        {"artifact_path": "event.json", "digest": event_digest},
        {"artifact_path": "candidate-manifest.json", "digest": manifest_digest},
        {"artifact_path": "candidate-receipt.json", "digest": receipt_digest},
    ]
    set_digest = _digest(_canonical({"members": output_members}))
    expected = event.get("expectations")
    route = event.get("route")
    protected = event.get("protected_data")
    evidence = event.get("evidence")
    target = event.get("target")
    if not all(isinstance(item, dict) for item in (expected, route, protected, evidence, target)):
        raise LifecycleProfileError("lifecycle event binding objects are missing", "LIFECYCLE_CANDIDATE_BINDING")
    acceptance_ref = evidence.get("trusted_acceptance_receipt_ref")
    acceptance_digest = acceptance_ref.get("digest") if isinstance(acceptance_ref, dict) else None
    binding = manifest.get("event_binding")
    locks = manifest.get("locks")
    trusted = manifest.get("trusted_bindings")
    if not all(isinstance(item, dict) for item in (binding, locks, trusted)):
        raise LifecycleProfileError("candidate manifest binding is malformed", "LIFECYCLE_CANDIDATE_BINDING")
    if (
        event.get("schema_id") != profile["event_schema_id"]
        or event.get("schema_version") != profile["event_schema_version"]
        or event.get("authority") != "CANONICAL_RECORD"
        or event.get("record_id") != profile["event_record_id"]
        or _stable_event_id(event) != profile["event_record_id"]
        or event.get("event_class") != profile["event_class"]
        or event.get("event_type") != profile["event_type"]
        or event.get("semantic_author") != profile["semantic_author"]
        or target.get("entity_type") != profile["target_entity_type"]
        or target.get("entity_id") != profile["target_entity_id"]
        or route.get("route_authority") != profile["route_authority"]
        or route.get("allowed_paths") != profile["allowed_paths"]
        or expected.get("expected_main_sha") != profile["expected_main_sha"]
        or expected.get("expected_entity_revision") != profile["expected_entity_revision"]
        or expected.get("expected_quest_revision") != profile["expected_quest_revision"]
        or expected.get("expected_gate_revision") != profile["expected_gate_revision"]
        or expected.get("expected_parent_checkpoint_id") != profile["expected_parent_event_id"]
        or expected.get("expected_source_fingerprint") != profile["expected_source_fingerprint"]
        or protected.get("classification") != profile["protected_data_classification"]
        or event.get("replay_key") != profile["replay_key"]
        or event.get("lineage") != profile["lineage"]
        or acceptance_digest != profile["trusted_acceptance_receipt_digest"]
        or event_digest != profile["candidate_event_digest"]
        or manifest_digest != profile["candidate_manifest_digest"]
        or receipt_digest != profile["candidate_receipt_digest"]
        or set_digest != profile["candidate_set_digest"]
        or binding.get("record_id") != profile["event_record_id"]
        or binding.get("repository_path") != profile["repository_path"]
        or binding.get("payload_digest") != event_digest
        or manifest.get("allowed_paths") != profile["allowed_paths"]
        or locks.get("expected_main_sha") != profile["expected_main_sha"]
        or locks.get("expected_entity_revision") != profile["expected_entity_revision"]
        or trusted.get("trust_root_digest") != profile["trust_root_digest"]
        or trusted.get("state_snapshot_digest") != profile["state_snapshot_digest"]
        or trusted.get("accepted_event_schema_digest") != _trusted_digest(
            "lifecycle/schemas/lifecycle-event-v1.schema.json"
        )
        or trusted.get("acceptance_contract_digest") != _trusted_digest(
            "lifecycle/lifecycle-event-contract.md"
        )
        or receipt.get("event_record_id") != profile["event_record_id"]
        or receipt.get("repository_path") != profile["repository_path"]
        or receipt.get("candidate_payload_digest") != event_digest
        or receipt.get("manifest_digest") != manifest_digest
        or receipt.get("trust_root_digest") != profile["trust_root_digest"]
        or receipt.get("state_snapshot_digest") != profile["state_snapshot_digest"]
        or receipt.get("output_members") != output_members[:2]
    ):
        raise LifecycleProfileError("lifecycle candidate cross-binding is invalid", "LIFECYCLE_CANDIDATE_BINDING")
    return {
        "profile_id": profile["profile_id"],
        "event_record_id": profile["event_record_id"],
        "event_class": profile["event_class"],
        "event_type": profile["event_type"],
        "repository_path": profile["repository_path"],
        "target_entity_type": profile["target_entity_type"],
        "target_entity_id": profile["target_entity_id"],
        "expected_main_sha": profile["expected_main_sha"],
        "expected_entity_revision": profile["expected_entity_revision"],
        "candidate_set_digest": set_digest,
        "candidate_receipt_digest": receipt_digest,
        "replay_key": profile["replay_key"],
        "semantic_validation_performed": False,
        "canonical_writes": False,
        "automatic_ready": False,
        "automatic_merge": False,
    }


def reject_lifecycle_replay(checkout: Path, profile: dict[str, Any]) -> None:
    checkout = checkout.resolve()
    directory = checkout
    for part in ("lifecycle", "events"):
        directory = directory / part
        if directory.is_symlink():
            raise LifecycleProfileError("canonical lifecycle path contains a symlink", "LIFECYCLE_REPLAY_SOURCE")
    if not directory.exists():
        return
    if not directory.is_dir() or directory.is_symlink():
        raise LifecycleProfileError("canonical lifecycle event directory is unsafe", "LIFECYCLE_REPLAY_SOURCE")
    members = sorted(directory.iterdir(), key=lambda path: path.name)
    if len(members) > MAX_CANONICAL_EVENTS:
        raise LifecycleProfileError("canonical lifecycle event count exceeds limit", "LIFECYCLE_REPLAY_LIMIT")
    total_bytes = sum(path.stat().st_size for path in members if path.is_file() and not path.is_symlink())
    if total_bytes > MAX_CANONICAL_EVENT_BYTES:
        raise LifecycleProfileError("canonical lifecycle event bytes exceed limit", "LIFECYCLE_REPLAY_LIMIT")
    found_ids: set[str] = set()
    found_names: set[str] = set()
    found_replay_keys: set[str] = set()
    validator = SchemaValidator(PRIME_ROOT / "lifecycle/schemas")
    for path in members:
        folded_name = path.name.casefold()
        if folded_name in found_names:
            raise LifecycleProfileError("canonical lifecycle path case-fold collision", "LIFECYCLE_REPLAY_SOURCE")
        found_names.add(folded_name)
        event, _ = _load_canonical(path)
        try:
            validator.validate_record(event)
            enforce_clean_values(event)
            enforce_pointer_contract(event)
        except LifecycleError as exc:
            raise LifecycleProfileError("canonical lifecycle event violates its trusted schema", "LIFECYCLE_REPLAY_SOURCE") from exc
        event_id = event.get("record_id")
        replay_key = event.get("replay_key")
        if (
            EVENT_PATH.fullmatch(f"lifecycle/events/{path.name}") is None
            or event.get("schema_id") != "atlas.lifecycle.event"
            or event.get("schema_version") != "1.0.0"
            or event.get("authority") != "CANONICAL_RECORD"
            or not isinstance(event_id, str)
            or EVENT_ID.fullmatch(event_id) is None
            or _stable_event_id(event) != event_id
            or not isinstance(replay_key, str)
            or FINGERPRINT.fullmatch(replay_key) is None
        ):
            raise LifecycleProfileError("canonical lifecycle event violates its trusted identity", "LIFECYCLE_REPLAY_SOURCE")
        if event_id in found_ids or replay_key in found_replay_keys:
            raise LifecycleProfileError("canonical lifecycle identity is duplicated", "LIFECYCLE_REPLAY_SOURCE")
        found_ids.add(event_id)
        found_replay_keys.add(replay_key)
        if event_id == profile["event_record_id"] or replay_key == profile["replay_key"]:
            raise LifecycleProfileError("lifecycle event or replay key already exists", "LIFECYCLE_REPLAY")
        expected = event.get("expectations")
        target = event.get("target")
        if (
            isinstance(expected, dict)
            and isinstance(target, dict)
            and target.get("entity_id") is not None
            and target.get("entity_id") == profile["target_entity_id"]
            and expected.get("expected_entity_revision") == profile["expected_entity_revision"]
        ):
            raise LifecycleProfileError("lifecycle entity revision is already claimed", "LIFECYCLE_CONCURRENT_REVISION")
    parent = profile["expected_parent_event_id"]
    if parent is not None and parent not in found_ids:
        raise LifecycleProfileError("expected lifecycle parent is absent", "LIFECYCLE_PARENT_ABSENT")
