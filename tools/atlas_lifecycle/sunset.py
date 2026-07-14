from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any

from .candidate import _create_output_directory, _validated_output_path, _write_exact
from .errors import LifecycleError
from .jsonio import canonical_bytes, load_bounded, read_bounded, stable_record_id
from .repository import _validate_sunset_feather_bindings, observed_head, validate_repository
from .schema import SchemaValidator

ARTIFACT_BUNDLE = "candidate-bundle.json"
ARTIFACT_RECEIPT = "candidate-receipt.json"
IDENTITY = re.compile(r"^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$")
GIT_SHA = re.compile(r"^[a-f0-9]{40}$")
FINGERPRINT = re.compile(r"^sha256:[a-f0-9]{64}$")
SCHEMA_DIRECTORY = {
    "atlas.lifecycle.feather": "feathers",
    "atlas.lifecycle.quest-emberline": "quest-emberlines",
    "atlas.lifecycle.quest-checkpoint": "quest-checkpoints",
    "atlas.lifecycle.sunset": "sunsets",
    "atlas.lifecycle.sunrise": "sunrises",
}
REQUEST_KEYS = {
    "schema_id",
    "schema_version",
    "authority",
    "request_id",
    "expected_main_sha",
    "project_id",
    "operation_id",
    "quest_scope",
    "campaign",
    "mission",
    "gate",
    "context_summary",
    "completion_assessment",
    "decisions",
    "open_items",
    "current_position",
    "unresolved_blockers",
    "next_safe_action",
    "next_approval_gate",
    "next_gate",
    "durable_source_references",
    "evidence_pointers",
    "protected_data",
}


def _digest(data: bytes) -> str:
    return f"sha256:{hashlib.sha256(data).hexdigest()}"


def _fail(code: str, message: str) -> None:
    raise LifecycleError(code, message)


def _bounded_text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value or len(value) > 4000:
        _fail("SUNSET_REQUEST_TEXT", f"{label} must be non-empty bounded text")
    return value


def _bounded_text_list(value: Any, label: str) -> list[str]:
    if (
        not isinstance(value, list)
        or len(value) > 64
        or any(not isinstance(item, str) or not item or len(item) > 4000 for item in value)
        or len(value) != len(set(value))
    ):
        _fail("SUNSET_REQUEST_LIST", f"{label} must be a unique bounded text list")
    return list(value)


def _validate_request(root: Path, request_path: Path) -> dict[str, Any]:
    request = load_bounded(request_path)
    if read_bounded(request_path) != canonical_bytes(request):
        _fail("SUNSET_REQUEST_CANONICAL", "Sunset request bytes must be canonical JSON")
    if set(request) != REQUEST_KEYS:
        _fail("SUNSET_REQUEST_CONTRACT", "Sunset request has missing or undeclared fields")
    if (
        request.get("schema_id") != "atlas.lifecycle.sunset-request"
        or request.get("schema_version") != "1.0.0"
        or request.get("authority") != "PUBLIC_CLEAN_REQUEST"
    ):
        _fail("SUNSET_REQUEST_IDENTITY", "Sunset request identity is invalid")
    for field in ("request_id", "project_id", "operation_id"):
        value = request.get(field)
        if not isinstance(value, str) or IDENTITY.fullmatch(value) is None or len(value) > 128:
            _fail("SUNSET_REQUEST_IDENTITY", f"{field} is invalid")
    if not isinstance(request.get("expected_main_sha"), str) or GIT_SHA.fullmatch(
        request["expected_main_sha"]
    ) is None:
        _fail("SUNSET_REQUEST_BASE", "expected_main_sha must be one exact Git commit SHA")
    for field in (
        "context_summary",
        "completion_assessment",
        "current_position",
        "next_safe_action",
        "next_approval_gate",
        "next_gate",
    ):
        _bounded_text(request.get(field), field)
    for field in ("decisions", "open_items", "unresolved_blockers"):
        _bounded_text_list(request.get(field), field)
    for field in ("campaign", "mission", "gate"):
        value = request.get(field)
        if value is not None and (not isinstance(value, str) or not value or len(value) > 256):
            _fail("SUNSET_REQUEST_POSITION", f"{field} is invalid")

    scope = request.get("quest_scope")
    if not isinstance(scope, dict):
        _fail("SUNSET_REQUEST_SCOPE", "quest_scope must be an object")
    scope_type = scope.get("scope_type")
    if scope_type == "ADMITTED_QUEST":
        if set(scope) != {"scope_type", "quest_id"}:
            _fail("SUNSET_REQUEST_SCOPE", "admitted Quest scope is malformed")
        quest_id = scope.get("quest_id")
        if not isinstance(quest_id, str) or IDENTITY.fullmatch(quest_id) is None:
            _fail("SUNSET_REQUEST_SCOPE", "admitted Quest ID is invalid")
        expected_source = root / "quests" / f"{quest_id}.md"
        if not expected_source.is_file() or expected_source.is_symlink():
            _fail("SUNSET_REQUEST_QUEST_SOURCE", "admitted Quest source is unavailable")
        expected_uri = f"quests/{quest_id}.md"
        references = request.get("durable_source_references")
        if not isinstance(references, list) or not any(
            isinstance(item, dict)
            and item.get("authority") == "CANONICAL_SOURCE"
            and item.get("uri") == expected_uri
            for item in references
        ):
            _fail("SUNSET_REQUEST_QUEST_SOURCE", "request does not bind its admitted Quest source")
    elif scope_type == "NON_QUEST":
        if set(scope) != {"scope_type", "work_scope"}:
            _fail("SUNSET_REQUEST_SCOPE", "non-Quest scope is malformed")
        _bounded_text(scope.get("work_scope"), "work_scope")
    else:
        _fail("SUNSET_REQUEST_SCOPE", "live Sunset accepts admitted-Quest or non-Quest scope only")
    return request



def _contains_key(value: Any, key: str) -> bool:
    if isinstance(value, dict):
        return key in value or any(_contains_key(item, key) for item in value.values())
    if isinstance(value, list):
        return any(_contains_key(item, key) for item in value)
    return False


def _source_references(request: dict[str, Any]) -> list[dict[str, Any]]:
    values = [*request["durable_source_references"], *request["evidence_pointers"]]
    unique = {canonical_bytes({"value": value}): value for value in values}
    return [unique[key] for key in sorted(unique)]


def _record_path(record: dict[str, Any]) -> str:
    directory = SCHEMA_DIRECTORY.get(record.get("schema_id"))
    if directory is None:
        _fail("SUNSET_RECORD_TYPE", "Sunset candidate emitted an unsupported record type")
    return f"lifecycle/{directory}/{record['record_id']}.json"


def _canonical_record(record: dict[str, Any]) -> dict[str, Any]:
    value = dict(record)
    value["record_id"] = stable_record_id(value)
    return value


def _build_records(root: Path, request: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    snapshot = validate_repository(root)
    exact_head = observed_head(root)
    if request["expected_main_sha"] != exact_head:
        _fail(
            "STALE_STATE",
            "Sunset request expected_main_sha does not match the exact transaction input",
        )
    scope = request["quest_scope"]
    scope_type = scope["scope_type"]
    current_emberline = None
    parent_feather = None
    prior_emberline = None
    quest_revision = None
    if scope_type == "ADMITTED_QUEST":
        matches = [
            record
            for record in snapshot.canonical_records
            if record.get("schema_id") == "atlas.lifecycle.quest-emberline"
            and record.get("quest_id") == scope["quest_id"]
        ]
        if len(matches) > 1:
            _fail("SUNSET_QUEST_STATE", "admitted Quest has more than one current Emberline")
        current_emberline = matches[0] if matches else None
        if current_emberline is None:
            quest_revision = 1
        else:
            quest_revision = current_emberline["quest_revision"] + 1
            prior_emberline = current_emberline["record_id"]
            parent_feather = current_emberline.get("latest_feather_id")
            if parent_feather is not None and not any(
                record.get("schema_id") == "atlas.lifecycle.feather"
                and record.get("record_id") == parent_feather
                for record in snapshot.canonical_records
            ):
                _fail("SUNSET_PARENT_FEATHER", "current Quest parent Feather does not resolve")

    concurrency = {
        "expected_main_sha": exact_head,
        "expected_parent_feather": parent_feather,
        "expected_quest_revision": quest_revision,
        "declared_source_fingerprint": snapshot.source_fingerprint,
    }
    feather = _canonical_record(
        {
            "schema_id": "atlas.lifecycle.feather",
            "schema_version": "1.0.0",
            "record_id": "FTR-AAAAAAAAAAAAAAAAAAAAAAAAAA",
            "authority": "CANONICAL_RECORD",
            "project_id": request["project_id"],
            "operation_id": request["operation_id"],
            "quest_scope": scope,
            "campaign": request["campaign"],
            "mission": request["mission"],
            "gate": request["gate"],
            "lifecycle_status": "SEALED",
            "context_summary": request["context_summary"],
            "concurrency": concurrency,
            "durable_source_references": request["durable_source_references"],
            "evidence_pointers": request["evidence_pointers"],
            "protected_data": request["protected_data"],
            "next_safe_action": request["next_safe_action"],
            "next_approval_gate": request["next_approval_gate"],
            "supersession_lineage": {
                "supersedes": [parent_feather] if parent_feather else [],
                "superseded_by": None,
            },
        }
    )

    records: list[dict[str, Any]] = [feather]
    emberline = None
    checkpoint = None
    if scope_type == "ADMITTED_QUEST":
        emberline = _canonical_record(
            {
                "schema_id": "atlas.lifecycle.quest-emberline",
                "schema_version": "1.0.0",
                "record_id": "QEM-AAAAAAAAAAAAAAAAAAAAAAAAAA",
                "authority": "CANONICAL_RECORD",
                "quest_id": scope["quest_id"],
                "project_id": request["project_id"],
                "operation_ids": [request["operation_id"]],
                "quest_revision": quest_revision,
                "prior_emberline_id": prior_emberline,
                "current_position": request["current_position"],
                "unresolved_blockers": request["unresolved_blockers"],
                "next_gate": request["next_gate"],
                "latest_feather_id": feather["record_id"],
                "concurrency": concurrency,
                "durable_source_references": request["durable_source_references"],
                "protected_data": request["protected_data"],
            }
        )
        checkpoint = _canonical_record(
            {
                "schema_id": "atlas.lifecycle.quest-checkpoint",
                "schema_version": "1.0.0",
                "record_id": "QCP-AAAAAAAAAAAAAAAAAAAAAAAAAA",
                "authority": "CANONICAL_RECORD",
                "quest_id": scope["quest_id"],
                "quest_revision": quest_revision,
                "emberline_id": emberline["record_id"],
                "feather_id": feather["record_id"],
                "checkpoint_summary": request["context_summary"],
                "gate": request["next_gate"],
                "evidence_pointers": request["evidence_pointers"],
                "protected_data": request["protected_data"],
                "concurrency": concurrency,
            }
        )
        records.extend([emberline, checkpoint])

    sunset = _canonical_record(
        {
            "schema_id": "atlas.lifecycle.sunset",
            "schema_version": "1.0.0",
            "record_id": "SUN-AAAAAAAAAAAAAAAAAAAAAAAAAA",
            "authority": "CANONICAL_RECORD",
            "project_id": request["project_id"],
            "operation_id": request["operation_id"],
            "quest_scope": scope,
            "completion_assessment": request["completion_assessment"],
            "decisions": request["decisions"],
            "open_items": request["open_items"],
            "next_safe_action": request["next_safe_action"],
            "next_approval_gate": request["next_approval_gate"],
            "latest_feather_id": feather["record_id"],
            "concurrency": concurrency,
            "durable_source_references": request["durable_source_references"],
            "evidence_pointers": request["evidence_pointers"],
            "protected_data": request["protected_data"],
        }
    )
    sunrise = _canonical_record(
        {
            "schema_id": "atlas.lifecycle.sunrise",
            "schema_version": "1.0.0",
            "record_id": "SRI-AAAAAAAAAAAAAAAAAAAAAAAAAA",
            "authority": "CANONICAL_RECORD",
            "sunset_id": sunset["record_id"],
            "resolved_source_fingerprint": snapshot.source_fingerprint,
            "current_position": request["current_position"],
            "latest_feather_id": feather["record_id"],
            "unresolved_blockers": request["unresolved_blockers"],
            "next_gate": request["next_gate"],
            "related_golden_wing_ids": [],
            "exact_source_references": _source_references(request),
            "stale_projection_warnings": [
                "Generated lifecycle projection must be refreshed after the source transaction merges."
            ],
            "protected_data": request["protected_data"],
        }
    )
    records.extend([sunset, sunrise])

    validator = SchemaValidator(root / "lifecycle" / "schemas")
    for record in records:
        validator.validate_record(record)
        if stable_record_id(record) != record["record_id"]:
            _fail("SUNSET_RECORD_ID", "Sunset candidate record ID is unstable")
    _validate_sunset_feather_bindings(records, record_class="candidate")

    assertions = {
        "feathers": sum(record["schema_id"] == "atlas.lifecycle.feather" for record in records),
        "sunsets": sum(record["schema_id"] == "atlas.lifecycle.sunset" for record in records),
        "sunrises": sum(record["schema_id"] == "atlas.lifecycle.sunrise" for record in records),
        "quest_emberlines": sum(
            record["schema_id"] == "atlas.lifecycle.quest-emberline" for record in records
        ),
        "quest_checkpoints": sum(
            record["schema_id"] == "atlas.lifecycle.quest-checkpoint" for record in records
        ),
        "quest_identity_fabricated": False,
    }
    if assertions["feathers"] != 1 or assertions["sunsets"] != 1 or assertions["sunrises"] != 1:
        _fail("SUNSET_CARDINALITY", "one invocation must create exactly one Feather, Sunset, and Sunrise")
    if scope_type == "ADMITTED_QUEST":
        if assertions["quest_emberlines"] != 1 or assertions["quest_checkpoints"] != 1:
            _fail("SUNSET_QUEST_CARDINALITY", "admitted Quest invocation requires one Emberline and checkpoint")
    else:
        if assertions["quest_emberlines"] or assertions["quest_checkpoints"]:
            _fail("SUNSET_NONQUEST_FABRICATION", "non-Quest invocation fabricated Quest state")
        if _contains_key(records, "quest_id"):
            _fail("SUNSET_NONQUEST_FABRICATION", "non-Quest record contains an invented Quest ID")
    return records, assertions


def _write_boundary() -> dict[str, Any]:
    return {
        "output_scope": "SYSTEM_TEMPORARY_DIRECTORY",
        "canonical_writes": False,
        "direct_main": False,
        "github_actions": [],
        "automatic_ready": False,
        "automatic_merge": False,
    }


def generate_sunset_candidate(
    repo_root: Path,
    request_path: Path,
    output_dir: Path,
) -> dict[str, Any]:
    root = repo_root.resolve()
    request = _validate_request(root, request_path)
    records, assertions = _build_records(root, request)
    destination = _validated_output_path(root, output_dir)

    entries = []
    bindings = []
    for record in sorted(records, key=_record_path):
        path = _record_path(record)
        data = canonical_bytes(record)
        entries.append({"path": path, "record": record})
        bindings.append(
            {
                "path": path,
                "record_id": record["record_id"],
                "schema_id": record["schema_id"],
                "payload_digest": _digest(data),
            }
        )
    request_digest = _digest(canonical_bytes(request))
    bundle = {
        "schema_id": "atlas.lifecycle.sunset-candidate-bundle",
        "schema_version": "1.0.0",
        "authority": "TEMPORARY_CANDIDATE_ONLY",
        "engine_class": "SCRIPT_ASSIST_LEVEL_1B",
        "request_id": request["request_id"],
        "request_digest": request_digest,
        "expected_main_sha": observed_head(root),
        "source_fingerprint": validate_repository(root).source_fingerprint,
        "scope_type": request["quest_scope"]["scope_type"],
        "record_bindings": bindings,
        "records": entries,
        "assertions": assertions,
        "write_boundary": _write_boundary(),
    }
    bundle_bytes = canonical_bytes(bundle)
    bundle_digest = _digest(bundle_bytes)
    candidate_set_digest = _digest(
        canonical_bytes(
            {
                "bundle_digest": bundle_digest,
                "request_digest": request_digest,
                "request_id": request["request_id"],
            }
        )
    )
    receipt = {
        "schema_id": "atlas.lifecycle.sunset-candidate-receipt",
        "schema_version": "1.0.0",
        "authority": "TEMPORARY_CANDIDATE_ONLY",
        "engine_class": "SCRIPT_ASSIST_LEVEL_1B",
        "command": "sunset candidate",
        "request_id": request["request_id"],
        "request_digest": request_digest,
        "bundle_digest": bundle_digest,
        "candidate_set_digest": candidate_set_digest,
        "expected_main_sha": bundle["expected_main_sha"],
        "source_fingerprint": bundle["source_fingerprint"],
        "record_count": len(entries),
        "verification_result": "PASS",
        "write_boundary": _write_boundary(),
    }
    receipt_bytes = canonical_bytes(receipt)
    _create_output_directory(destination)
    _write_exact(destination / ARTIFACT_BUNDLE, bundle_bytes)
    _write_exact(destination / ARTIFACT_RECEIPT, receipt_bytes)
    verified = verify_sunset_candidate(root, destination)
    if verified["candidate_set_digest"] != candidate_set_digest:
        _fail("SUNSET_CANDIDATE_DIGEST", "Sunset candidate set digest changed during readback")
    return {
        "authority": "TEMPORARY_CANDIDATE_ONLY",
        "command": "sunset candidate",
        "engine_class": "SCRIPT_ASSIST_LEVEL_1B",
        "request_id": request["request_id"],
        "scope_type": bundle["scope_type"],
        "candidate_set_digest": candidate_set_digest,
        "record_count": len(entries),
        "record_bindings": bindings,
        "assertions": assertions,
        "writes_performed": ["SYSTEM_TEMPORARY_DIRECTORY"],
        "canonical_writes": False,
        "github_actions": [],
        "status": "PASS",
    }


def verify_sunset_candidate(repo_root: Path, candidate_dir: Path) -> dict[str, Any]:
    root = repo_root.resolve()
    if not candidate_dir.is_dir() or candidate_dir.is_symlink():
        _fail("SUNSET_CANDIDATE_DIRECTORY", "Sunset candidate directory is unsafe")
    members = sorted(candidate_dir.iterdir(), key=lambda path: path.name)
    if [path.name for path in members] != [ARTIFACT_BUNDLE, ARTIFACT_RECEIPT] or any(
        not path.is_file() or path.is_symlink() for path in members
    ):
        _fail("SUNSET_CANDIDATE_MEMBERS", "Sunset candidate set has unexpected members")
    bundle_bytes = read_bounded(candidate_dir / ARTIFACT_BUNDLE)
    receipt_bytes = read_bounded(candidate_dir / ARTIFACT_RECEIPT)
    bundle = load_bounded(candidate_dir / ARTIFACT_BUNDLE)
    receipt = load_bounded(candidate_dir / ARTIFACT_RECEIPT)
    if bundle_bytes != canonical_bytes(bundle) or receipt_bytes != canonical_bytes(receipt):
        _fail("SUNSET_CANDIDATE_CANONICAL", "Sunset candidate artifacts are not canonical JSON")
    expected_bundle_keys = {
        "schema_id",
        "schema_version",
        "authority",
        "engine_class",
        "request_id",
        "request_digest",
        "expected_main_sha",
        "source_fingerprint",
        "scope_type",
        "record_bindings",
        "records",
        "assertions",
        "write_boundary",
    }
    expected_receipt_keys = {
        "schema_id",
        "schema_version",
        "authority",
        "engine_class",
        "command",
        "request_id",
        "request_digest",
        "bundle_digest",
        "candidate_set_digest",
        "expected_main_sha",
        "source_fingerprint",
        "record_count",
        "verification_result",
        "write_boundary",
    }
    if set(bundle) != expected_bundle_keys or set(receipt) != expected_receipt_keys:
        _fail("SUNSET_CANDIDATE_CONTRACT", "Sunset candidate artifact contract is invalid")
    if (
        bundle.get("schema_id") != "atlas.lifecycle.sunset-candidate-bundle"
        or receipt.get("schema_id") != "atlas.lifecycle.sunset-candidate-receipt"
        or bundle.get("schema_version") != "1.0.0"
        or receipt.get("schema_version") != "1.0.0"
        or bundle.get("authority") != "TEMPORARY_CANDIDATE_ONLY"
        or receipt.get("authority") != "TEMPORARY_CANDIDATE_ONLY"
    ):
        _fail("SUNSET_CANDIDATE_IDENTITY", "Sunset candidate artifact identity is invalid")
    bundle_digest = _digest(bundle_bytes)
    expected_set_digest = _digest(
        canonical_bytes(
            {
                "bundle_digest": bundle_digest,
                "request_digest": bundle["request_digest"],
                "request_id": bundle["request_id"],
            }
        )
    )
    if (
        receipt["request_id"] != bundle["request_id"]
        or receipt["request_digest"] != bundle["request_digest"]
        or receipt["bundle_digest"] != bundle_digest
        or receipt["candidate_set_digest"] != expected_set_digest
        or receipt["expected_main_sha"] != bundle["expected_main_sha"]
        or receipt["source_fingerprint"] != bundle["source_fingerprint"]
        or receipt["record_count"] != len(bundle["records"])
        or receipt["verification_result"] != "PASS"
        or receipt["command"] != "sunset candidate"
        or bundle["write_boundary"] != _write_boundary()
        or receipt["write_boundary"] != _write_boundary()
    ):
        _fail("SUNSET_CANDIDATE_BINDING", "Sunset candidate artifacts are not cross-bound")
    if GIT_SHA.fullmatch(bundle["expected_main_sha"]) is None or FINGERPRINT.fullmatch(
        bundle["source_fingerprint"]
    ) is None:
        _fail("SUNSET_CANDIDATE_LOCK", "Sunset candidate source lock is invalid")

    validator = SchemaValidator(root / "lifecycle" / "schemas")
    bindings = bundle["record_bindings"]
    entries = bundle["records"]
    if not isinstance(bindings, list) or not isinstance(entries, list) or len(bindings) != len(entries):
        _fail("SUNSET_CANDIDATE_RECORDS", "Sunset candidate records are malformed")
    records: list[dict[str, Any]] = []
    observed_bindings = []
    seen_paths: set[str] = set()
    seen_ids: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != {"path", "record"}:
            _fail("SUNSET_CANDIDATE_RECORDS", "Sunset candidate record entry is malformed")
        path = entry["path"]
        record = entry["record"]
        if not isinstance(path, str) or path in seen_paths or not isinstance(record, dict):
            _fail("SUNSET_CANDIDATE_RECORDS", "Sunset candidate record entry is invalid")
        seen_paths.add(path)
        validator.validate_record(record)
        if record.get("authority") != "CANONICAL_RECORD" or stable_record_id(record) != record.get(
            "record_id"
        ):
            _fail("SUNSET_CANDIDATE_RECORD_ID", "Sunset candidate record identity is invalid")
        if path != _record_path(record) or record["record_id"] in seen_ids:
            _fail("SUNSET_CANDIDATE_RECORD_PATH", "Sunset candidate record path is invalid")
        seen_ids.add(record["record_id"])
        data = canonical_bytes(record)
        observed_bindings.append(
            {
                "path": path,
                "record_id": record["record_id"],
                "schema_id": record["schema_id"],
                "payload_digest": _digest(data),
            }
        )
        records.append(record)
    if observed_bindings != bindings:
        _fail("SUNSET_CANDIDATE_BINDING", "Sunset candidate record bindings do not match")
    _validate_sunset_feather_bindings(records, record_class="candidate")

    counts = {
        "feathers": sum(record["schema_id"] == "atlas.lifecycle.feather" for record in records),
        "sunsets": sum(record["schema_id"] == "atlas.lifecycle.sunset" for record in records),
        "sunrises": sum(record["schema_id"] == "atlas.lifecycle.sunrise" for record in records),
        "quest_emberlines": sum(
            record["schema_id"] == "atlas.lifecycle.quest-emberline" for record in records
        ),
        "quest_checkpoints": sum(
            record["schema_id"] == "atlas.lifecycle.quest-checkpoint" for record in records
        ),
        "quest_identity_fabricated": False,
    }
    if counts != bundle["assertions"] or counts["feathers"] != 1 or counts["sunsets"] != 1 or counts[
        "sunrises"
    ] != 1:
        _fail("SUNSET_CANDIDATE_CARDINALITY", "Sunset candidate cardinality is invalid")
    scope_type = bundle["scope_type"]
    if scope_type == "ADMITTED_QUEST":
        if counts["quest_emberlines"] != 1 or counts["quest_checkpoints"] != 1:
            _fail("SUNSET_CANDIDATE_QUEST", "admitted Quest candidate is incomplete")
    elif scope_type == "NON_QUEST":
        if counts["quest_emberlines"] or counts["quest_checkpoints"] or _contains_key(
            records, "quest_id"
        ):
            _fail("SUNSET_CANDIDATE_NONQUEST", "non-Quest candidate fabricated Quest identity")
    else:
        _fail("SUNSET_CANDIDATE_SCOPE", "Sunset candidate scope type is unsupported")

    snapshot = validate_repository(root)
    known_ids = {record["record_id"] for record in snapshot.canonical_records} | seen_ids
    for record in records:
        concurrency = record.get("concurrency")
        if isinstance(concurrency, dict):
            parent = concurrency.get("expected_parent_feather")
            if parent is not None and parent not in known_ids:
                _fail("SUNSET_CANDIDATE_PARENT", "Sunset candidate parent Feather does not resolve")
    return {
        "authority": "READ_ONLY",
        "command": "sunset verify",
        "engine_class": "SCRIPT_ASSIST_LEVEL_1A",
        "request_id": bundle["request_id"],
        "scope_type": scope_type,
        "candidate_set_digest": expected_set_digest,
        "record_count": len(records),
        "record_bindings": bindings,
        "assertions": counts,
        "status": "PASS",
    }
