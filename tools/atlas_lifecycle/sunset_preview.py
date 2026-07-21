from __future__ import annotations

import base64
import hashlib
import tempfile
from pathlib import Path
from typing import Any

from .candidate import _create_output_directory, _validated_output_path, _write_exact
from .errors import LifecycleError
from .jsonio import canonical_bytes, load_bounded, read_bounded, stable_record_id
from .protection import enforce_clean_values, enforce_pointer_contract
from .repository import (
    _validate_lesson_harvest_bindings,
    _validate_living_emberline,
    _validate_sunset_feather_bindings,
    observed_head,
    validate_repository,
)
from .schema import SchemaValidator
from .sunset import (
    generate_sunset_candidate as generate_legacy_candidate,
    verify_sunset_candidate as verify_legacy_candidate,
)

PREVIEW_ARTIFACT = "sunset-preview.json"
PREVIEW_RECEIPT = "sunset-preview-receipt.json"
APPROVAL_ARTIFACT = "sunset-approval.json"
CARRIER_ARTIFACT = "sunset-carrier.json"
BOUND_REQUEST = "sunset-request-v3.json"
APPROVAL_RECEIPT = "sunset-approval-receipt.json"
ARTIFACT_BUNDLE = "candidate-bundle.json"
ARTIFACT_RECEIPT = "candidate-receipt.json"

APPROVAL_MODES = ("STANDARD", "GODDESS_MODE", "GODDESS_MODE_SHARDBLADE")
SEMANTIC_KEYS = (
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
    "lesson_harvest",
)
SCHEMA_DIRECTORY = {
    "atlas.lifecycle.feather": "feathers",
    "atlas.lifecycle.quest-emberline": "quest-emberlines",
    "atlas.lifecycle.quest-checkpoint": "quest-checkpoints",
    "atlas.lifecycle.sunset": "sunsets",
    "atlas.lifecycle.sunrise": "sunrises",
}


def _fail(code: str, message: str) -> None:
    raise LifecycleError(code, message)


def _digest(data: bytes) -> str:
    return f"sha256:{hashlib.sha256(data).hexdigest()}"


def _stable_id(prefix: str, value: Any) -> str:
    token = base64.b32encode(hashlib.sha256(canonical_bytes(value)).digest()).decode("ascii")
    return f"{prefix}-{token.rstrip('=')[:26]}"


def _read_canonical(path: Path, code: str) -> dict[str, Any]:
    value = load_bounded(path)
    if read_bounded(path) != canonical_bytes(value):
        _fail(code, f"{path.name} must use canonical JSON bytes")
    return value


def _write_boundary() -> dict[str, Any]:
    return {
        "output_scope": "SYSTEM_TEMPORARY_DIRECTORY",
        "canonical_writes": False,
        "direct_main": False,
        "github_actions": [],
        "automatic_ready": False,
        "automatic_merge": False,
    }


def _dynamic_validate(root: Path, value: dict[str, Any], schema_name: str) -> None:
    validator = SchemaValidator(root / "lifecycle" / "schemas")
    schema = load_bounded(root / "lifecycle" / "schemas" / schema_name)
    expected_id = f"https://github.com/Jktomy/atlas-prime/lifecycle/schemas/{schema_name}"
    if (
        schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema"
        or schema.get("$id") != expected_id
        or schema.get("additionalProperties") is not False
    ):
        _fail("SUNSET_SCHEMA_IDENTITY", "Sunset auxiliary schema identity is invalid")
    validator.schemas[schema_name] = schema
    validator._validate(value, schema, schema_name, "$")


def _semantic(value: dict[str, Any]) -> dict[str, Any]:
    return {key: value[key] for key in SEMANTIC_KEYS}


def _expected_records(scope_type: str) -> dict[str, int]:
    admitted = scope_type == "ADMITTED_QUEST"
    return {
        "feathers": 1,
        "sunsets": 1,
        "sunrises": 1,
        "quest_emberlines": 1 if admitted else 0,
        "quest_checkpoints": 1 if admitted else 0,
    }


def _validate_draft_request(root: Path, request_path: Path) -> dict[str, Any]:
    request = _read_canonical(request_path, "SUNSET_REQUEST_CANONICAL")
    if (
        request.get("schema_id") != "atlas.lifecycle.sunset-request"
        or request.get("schema_version") != "2.0.0"
    ):
        _fail("SUNSET_REQUEST_VERSION", "Sunset Preview input must use request v2")
    SchemaValidator(root / "lifecycle" / "schemas").validate_sunset_request(request)
    enforce_clean_values(request)
    enforce_pointer_contract(request)
    if request.get("expected_main_sha") != observed_head(root):
        _fail("STALE_STATE", "Sunset Preview base does not match the exact transaction input")
    scope = request.get("quest_scope", {})
    if scope.get("scope_type") == "ADMITTED_QUEST":
        quest_id = scope.get("quest_id")
        if not isinstance(quest_id, str) or not (root / "quests" / f"{quest_id}.md").is_file():
            _fail("SUNSET_REQUEST_QUEST_SOURCE", "admitted Quest source is unavailable")
        if not any(
            isinstance(item, dict)
            and item.get("authority") == "CANONICAL_SOURCE"
            and item.get("uri") == f"quests/{quest_id}.md"
            for item in request.get("durable_source_references", [])
        ):
            _fail("SUNSET_REQUEST_QUEST_SOURCE", "request does not bind its admitted Quest source")
    elif scope.get("scope_type") != "NON_QUEST":
        _fail("SUNSET_REQUEST_SCOPE", "live Sunset accepts admitted-Quest or non-Quest scope only")
    keys = [item["key"] for item in request["lesson_harvest"]["observations"]]
    if len(keys) != len(set(keys)):
        _fail("LESSON_HARVEST_DUPLICATE_KEY", "lesson observation keys must be unique")
    return request


def _record_path(record: dict[str, Any]) -> str:
    directory = SCHEMA_DIRECTORY.get(record.get("schema_id"))
    if directory is None:
        _fail("SUNSET_RECORD_TYPE", "approved Sunset emitted an unsupported record type")
    return f"lifecycle/{directory}/{record['record_id']}.json"


def generate_sunset_preview(
    repo_root: Path,
    request_path: Path,
    output_dir: Path,
    *,
    selected_route: str,
    fallback_routes: list[str],
) -> dict[str, Any]:
    root = repo_root.resolve()
    request = _validate_draft_request(root, request_path)
    if not selected_route or not fallback_routes or selected_route in fallback_routes:
        _fail("SUNSET_PREVIEW_ROUTE", "selected and fallback routes must be distinct")
    if len(fallback_routes) != len(set(fallback_routes)):
        _fail("SUNSET_PREVIEW_ROUTE", "fallback routes must be unique")

    expected = _expected_records(request["quest_scope"]["scope_type"])
    semantic = {
        **_semantic(request),
        "selected_route": selected_route,
        "fallback_routes": fallback_routes,
        "permitted_approval_modes": list(APPROVAL_MODES),
        "default_approval_mode": "STANDARD",
        "expected_records": expected,
    }
    semantic_digest = _digest(canonical_bytes(semantic))
    preview = {
        "schema_id": "atlas.lifecycle.sunset-preview",
        "schema_version": "1.0.0",
        "preview_id": _stable_id(
            "SPV",
            {
                "semantic_digest": semantic_digest,
                "expected_main_sha": request["expected_main_sha"],
            },
        ),
        "authority": "PREVIEW_ONLY",
        **semantic,
        "semantic_digest": semantic_digest,
    }
    _dynamic_validate(root, preview, "sunset-preview-v1.schema.json")
    enforce_clean_values(preview)
    enforce_pointer_contract(preview)
    preview_bytes = canonical_bytes(preview)
    receipt = {
        "schema_id": "atlas.lifecycle.sunset-preview-receipt",
        "schema_version": "1.0.0",
        "authority": "PREVIEW_ONLY",
        "preview_id": preview["preview_id"],
        "preview_digest": _digest(preview_bytes),
        "semantic_digest": semantic_digest,
        "expected_main_sha": request["expected_main_sha"],
        "record_plan_digest": _digest(canonical_bytes(expected)),
        "verification_result": "PASS",
        "write_boundary": _write_boundary(),
    }
    destination = _validated_output_path(root, output_dir)
    _create_output_directory(destination)
    _write_exact(destination / PREVIEW_ARTIFACT, preview_bytes)
    _write_exact(destination / PREVIEW_RECEIPT, canonical_bytes(receipt))
    verified = verify_sunset_preview(root, destination, require_current_head=True)
    return {
        "authority": "PREVIEW_ONLY",
        "command": "sunset preview",
        "preview_id": preview["preview_id"],
        "preview_digest": verified["preview_digest"],
        "semantic_digest": semantic_digest,
        "expected_records": expected,
        "approval_required": True,
        "status": "PASS",
    }


def verify_sunset_preview(
    repo_root: Path,
    preview_dir: Path,
    *,
    require_current_head: bool = False,
) -> dict[str, Any]:
    root = repo_root.resolve()
    if not preview_dir.is_dir() or preview_dir.is_symlink():
        _fail("SUNSET_PREVIEW_DIRECTORY", "Sunset Preview directory is unsafe")
    members = sorted(preview_dir.iterdir(), key=lambda path: path.name)
    expected_members = sorted([PREVIEW_ARTIFACT, PREVIEW_RECEIPT])
    if [path.name for path in members] != expected_members:
        _fail("SUNSET_PREVIEW_MEMBERS", "Sunset Preview has unexpected members")
    preview = _read_canonical(preview_dir / PREVIEW_ARTIFACT, "SUNSET_PREVIEW_CANONICAL")
    receipt = _read_canonical(preview_dir / PREVIEW_RECEIPT, "SUNSET_PREVIEW_CANONICAL")
    _dynamic_validate(root, preview, "sunset-preview-v1.schema.json")
    semantic = {
        **{key: preview[key] for key in SEMANTIC_KEYS},
        "selected_route": preview["selected_route"],
        "fallback_routes": preview["fallback_routes"],
        "permitted_approval_modes": preview["permitted_approval_modes"],
        "default_approval_mode": preview["default_approval_mode"],
        "expected_records": preview["expected_records"],
    }
    semantic_digest = _digest(canonical_bytes(semantic))
    preview_digest = _digest(canonical_bytes(preview))
    expected_id = _stable_id(
        "SPV",
        {
            "semantic_digest": semantic_digest,
            "expected_main_sha": preview["expected_main_sha"],
        },
    )
    expected_receipt = {
        "schema_id": "atlas.lifecycle.sunset-preview-receipt",
        "schema_version": "1.0.0",
        "authority": "PREVIEW_ONLY",
        "preview_id": preview["preview_id"],
        "preview_digest": preview_digest,
        "semantic_digest": semantic_digest,
        "expected_main_sha": preview["expected_main_sha"],
        "record_plan_digest": _digest(canonical_bytes(preview["expected_records"])),
        "verification_result": "PASS",
        "write_boundary": _write_boundary(),
    }
    if preview["preview_id"] != expected_id or preview["semantic_digest"] != semantic_digest:
        _fail("SUNSET_PREVIEW_BINDING", "Sunset Preview identity is invalid")
    if receipt != expected_receipt:
        _fail("SUNSET_PREVIEW_BINDING", "Sunset Preview receipt is invalid")
    if require_current_head and preview["expected_main_sha"] != observed_head(root):
        _fail("STALE_STATE", "Sunset Preview no longer matches the transaction input")
    return {
        "authority": "READ_ONLY",
        "preview": preview,
        "preview_digest": preview_digest,
        "semantic_digest": semantic_digest,
        "status": "PASS",
    }


def generate_sunset_approval(
    repo_root: Path,
    preview_dir: Path,
    output_dir: Path,
    *,
    approval_mode: str,
) -> dict[str, Any]:
    root = repo_root.resolve()
    verified = verify_sunset_preview(root, preview_dir, require_current_head=True)
    preview = verified["preview"]
    if approval_mode not in preview["permitted_approval_modes"]:
        _fail("SUNSET_APPROVAL_MODE", "approval mode was not shown in the Preview")
    permanence_mode = (
        "SHARDBLADE"
        if approval_mode == "GODDESS_MODE_SHARDBLADE"
        else "MANUAL_MERGE"
    )
    approval_seed = {
        "preview_id": preview["preview_id"],
        "preview_digest": verified["preview_digest"],
        "semantic_digest": preview["semantic_digest"],
        "approval_mode": approval_mode,
        "permanence_mode": permanence_mode,
    }
    approval = {
        "schema_id": "atlas.lifecycle.sunset-approval",
        "schema_version": "1.0.0",
        "approval_id": _stable_id("SAP", approval_seed),
        "authority": "JAYSON_EXPLICIT_APPROVAL",
        "preview_id": preview["preview_id"],
        "preview_digest": verified["preview_digest"],
        "semantic_digest": preview["semantic_digest"],
        "approved_by": "JAYSON",
        "approval_mode": approval_mode,
        "permanence_mode": permanence_mode,
        "approval_scope": "EXACT_PREVIEW_ONLY",
        "state": "APPROVED",
    }
    _dynamic_validate(root, approval, "sunset-approval-v1.schema.json")
    approval_digest = _digest(canonical_bytes(approval))
    carrier = {
        "schema_id": "atlas.lifecycle.sunset-carrier",
        "schema_version": "1.0.0",
        "carrier_id": _stable_id(
            "SCR",
            {
                "approval_id": approval["approval_id"],
                "approval_digest": approval_digest,
                "preview_id": preview["preview_id"],
                "semantic_digest": preview["semantic_digest"],
            },
        ),
        "authority": "ROUTE_NEUTRAL_APPROVED_CARRIER",
        "preview_id": preview["preview_id"],
        "preview_digest": verified["preview_digest"],
        "approval_id": approval["approval_id"],
        "approval_digest": approval_digest,
        "semantic_digest": preview["semantic_digest"],
        "state": "APPROVED_PENDING_COMPILATION",
        "selected_route": preview["selected_route"],
        "fallback_routes": preview["fallback_routes"],
        "approval_mode": approval_mode,
        "permanence_mode": permanence_mode,
        "expected_main_sha": preview["expected_main_sha"],
        "quest_scope": preview["quest_scope"],
        "record_plan_digest": _digest(canonical_bytes(preview["expected_records"])),
    }
    _dynamic_validate(root, carrier, "sunset-carrier-v1.schema.json")
    carrier_digest = _digest(canonical_bytes(carrier))
    request = {
        "schema_id": "atlas.lifecycle.sunset-request",
        "schema_version": "3.0.0",
        "authority": "PUBLIC_CLEAN_REQUEST",
        "request_id": f"approved-{preview['preview_id'].lower()}",
        **{key: preview[key] for key in SEMANTIC_KEYS},
        "preview_id": preview["preview_id"],
        "preview_digest": verified["preview_digest"],
        "approval_id": approval["approval_id"],
        "approval_digest": approval_digest,
        "carrier_id": carrier["carrier_id"],
        "carrier_digest": carrier_digest,
        "semantic_digest": preview["semantic_digest"],
        "approval_mode": approval_mode,
        "permanence_mode": permanence_mode,
    }
    _dynamic_validate(root, request, "sunset-request-v3.schema.json")
    request_digest = _digest(canonical_bytes(request))
    receipt = {
        "schema_id": "atlas.lifecycle.sunset-approval-receipt",
        "schema_version": "1.0.0",
        "authority": "ROUTE_NEUTRAL_APPROVED_CARRIER",
        "preview_id": preview["preview_id"],
        "preview_digest": verified["preview_digest"],
        "approval_id": approval["approval_id"],
        "approval_digest": approval_digest,
        "carrier_id": carrier["carrier_id"],
        "carrier_digest": carrier_digest,
        "request_digest": request_digest,
        "semantic_digest": preview["semantic_digest"],
        "approval_mode": approval_mode,
        "permanence_mode": permanence_mode,
        "verification_result": "PASS",
        "write_boundary": _write_boundary(),
    }
    for value in (approval, carrier, request, receipt):
        enforce_clean_values(value)
        enforce_pointer_contract(value)
    destination = _validated_output_path(root, output_dir)
    _create_output_directory(destination)
    _write_exact(destination / APPROVAL_ARTIFACT, canonical_bytes(approval))
    _write_exact(destination / CARRIER_ARTIFACT, canonical_bytes(carrier))
    _write_exact(destination / BOUND_REQUEST, canonical_bytes(request))
    _write_exact(destination / APPROVAL_RECEIPT, canonical_bytes(receipt))
    result = verify_sunset_approval(
        root,
        preview_dir,
        destination,
        require_current_head=True,
    )
    return {
        "authority": "ROUTE_NEUTRAL_APPROVED_CARRIER",
        "command": "sunset approve",
        "preview_id": preview["preview_id"],
        "approval_id": approval["approval_id"],
        "carrier_id": carrier["carrier_id"],
        "request_digest": result["request_digest"],
        "approval_mode": approval_mode,
        "permanence_mode": permanence_mode,
        "state": carrier["state"],
        "status": "PASS",
    }


def verify_sunset_approval(
    repo_root: Path,
    preview_dir: Path,
    approval_dir: Path,
    *,
    require_current_head: bool = False,
) -> dict[str, Any]:
    root = repo_root.resolve()
    preview_result = verify_sunset_preview(
        root,
        preview_dir,
        require_current_head=require_current_head,
    )
    preview = preview_result["preview"]
    if not approval_dir.is_dir() or approval_dir.is_symlink():
        _fail("SUNSET_APPROVAL_DIRECTORY", "Sunset approval directory is unsafe")
    names = sorted(path.name for path in approval_dir.iterdir())
    expected_names = sorted(
        [APPROVAL_ARTIFACT, CARRIER_ARTIFACT, BOUND_REQUEST, APPROVAL_RECEIPT]
    )
    if names != expected_names:
        _fail("SUNSET_APPROVAL_MEMBERS", "Sunset approval has unexpected members")
    approval = _read_canonical(
        approval_dir / APPROVAL_ARTIFACT,
        "SUNSET_APPROVAL_CANONICAL",
    )
    carrier = _read_canonical(
        approval_dir / CARRIER_ARTIFACT,
        "SUNSET_APPROVAL_CANONICAL",
    )
    request = _read_canonical(
        approval_dir / BOUND_REQUEST,
        "SUNSET_APPROVAL_CANONICAL",
    )
    receipt = _read_canonical(
        approval_dir / APPROVAL_RECEIPT,
        "SUNSET_APPROVAL_CANONICAL",
    )
    _dynamic_validate(root, approval, "sunset-approval-v1.schema.json")
    _dynamic_validate(root, carrier, "sunset-carrier-v1.schema.json")
    _dynamic_validate(root, request, "sunset-request-v3.schema.json")
    approval_digest = _digest(canonical_bytes(approval))
    carrier_digest = _digest(canonical_bytes(carrier))
    request_digest = _digest(canonical_bytes(request))
    expected_approval_id = _stable_id(
        "SAP",
        {
            "preview_id": preview["preview_id"],
            "preview_digest": preview_result["preview_digest"],
            "semantic_digest": preview["semantic_digest"],
            "approval_mode": approval["approval_mode"],
            "permanence_mode": approval["permanence_mode"],
        },
    )
    expected_carrier_id = _stable_id(
        "SCR",
        {
            "approval_id": approval["approval_id"],
            "approval_digest": approval_digest,
            "preview_id": preview["preview_id"],
            "semantic_digest": preview["semantic_digest"],
        },
    )
    if (
        approval["approval_id"] != expected_approval_id
        or carrier["carrier_id"] != expected_carrier_id
    ):
        _fail("SUNSET_APPROVAL_IDENTITY", "Sunset approval or carrier identity is invalid")
    if (
        approval["preview_id"] != preview["preview_id"]
        or approval["preview_digest"] != preview_result["preview_digest"]
        or approval["semantic_digest"] != preview["semantic_digest"]
        or carrier["preview_id"] != preview["preview_id"]
        or carrier["preview_digest"] != preview_result["preview_digest"]
        or carrier["approval_id"] != approval["approval_id"]
        or carrier["approval_digest"] != approval_digest
        or carrier["semantic_digest"] != preview["semantic_digest"]
        or carrier["expected_main_sha"] != preview["expected_main_sha"]
        or carrier["quest_scope"] != preview["quest_scope"]
        or request["preview_id"] != preview["preview_id"]
        or request["preview_digest"] != preview_result["preview_digest"]
        or request["approval_id"] != approval["approval_id"]
        or request["approval_digest"] != approval_digest
        or request["carrier_id"] != carrier["carrier_id"]
        or request["carrier_digest"] != carrier_digest
        or request["semantic_digest"] != preview["semantic_digest"]
        or request["approval_mode"] != approval["approval_mode"]
        or request["permanence_mode"] != approval["permanence_mode"]
        or _semantic(request) != {key: preview[key] for key in SEMANTIC_KEYS}
    ):
        _fail("SUNSET_APPROVAL_BINDING", "Sunset approval is not bound to one exact Preview")
    expected_receipt = {
        "schema_id": "atlas.lifecycle.sunset-approval-receipt",
        "schema_version": "1.0.0",
        "authority": "ROUTE_NEUTRAL_APPROVED_CARRIER",
        "preview_id": preview["preview_id"],
        "preview_digest": preview_result["preview_digest"],
        "approval_id": approval["approval_id"],
        "approval_digest": approval_digest,
        "carrier_id": carrier["carrier_id"],
        "carrier_digest": carrier_digest,
        "request_digest": request_digest,
        "semantic_digest": preview["semantic_digest"],
        "approval_mode": approval["approval_mode"],
        "permanence_mode": approval["permanence_mode"],
        "verification_result": "PASS",
        "write_boundary": _write_boundary(),
    }
    if receipt != expected_receipt:
        _fail("SUNSET_APPROVAL_BINDING", "Sunset approval receipt is invalid")
    return {
        "authority": "READ_ONLY",
        "preview": preview,
        "approval": approval,
        "carrier": carrier,
        "request": request,
        "preview_digest": preview_result["preview_digest"],
        "approval_digest": approval_digest,
        "carrier_digest": carrier_digest,
        "request_digest": request_digest,
        "status": "PASS",
    }


def _validate_records(
    root: Path,
    records: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, int], str]:
    validator = SchemaValidator(root / "lifecycle" / "schemas")
    bindings = []
    seen_ids: set[str] = set()
    seen_paths: set[str] = set()
    for record in records:
        validator.validate_record(record)
        enforce_clean_values(record)
        enforce_pointer_contract(record)
        _validate_living_emberline(record)
        if (
            record.get("authority") != "CANONICAL_RECORD"
            or stable_record_id(record) != record.get("record_id")
        ):
            _fail("SUNSET_CANDIDATE_RECORD_ID", "Sunset candidate record identity is invalid")
        path = _record_path(record)
        if path in seen_paths or record["record_id"] in seen_ids:
            _fail("SUNSET_CANDIDATE_RECORD_PATH", "Sunset candidate record path is duplicated")
        seen_paths.add(path)
        seen_ids.add(record["record_id"])
        bindings.append(
            {
                "path": path,
                "record_id": record["record_id"],
                "schema_id": record["schema_id"],
                "payload_digest": _digest(canonical_bytes(record)),
            }
        )
    bindings.sort(key=lambda item: item["path"])
    _validate_sunset_feather_bindings(records, record_class="candidate")
    snapshot = validate_repository(root)
    _validate_lesson_harvest_bindings(
        [*snapshot.canonical_records, *records],
        record_class="candidate",
    )
    counts = {
        "feathers": sum(r["schema_id"] == "atlas.lifecycle.feather" for r in records),
        "sunsets": sum(r["schema_id"] == "atlas.lifecycle.sunset" for r in records),
        "sunrises": sum(r["schema_id"] == "atlas.lifecycle.sunrise" for r in records),
        "quest_emberlines": sum(
            r["schema_id"] == "atlas.lifecycle.quest-emberline" for r in records
        ),
        "quest_checkpoints": sum(
            r["schema_id"] == "atlas.lifecycle.quest-checkpoint" for r in records
        ),
        "quest_identity_fabricated": False,
    }
    return bindings, counts, snapshot.source_fingerprint


def generate_approved_sunset_candidate(
    repo_root: Path,
    request_path: Path,
    preview_dir: Path,
    approval_dir: Path,
    output_dir: Path,
) -> dict[str, Any]:
    root = repo_root.resolve()
    approved = verify_sunset_approval(
        root,
        preview_dir,
        approval_dir,
        require_current_head=True,
    )
    request = _read_canonical(request_path, "SUNSET_REQUEST_CANONICAL")
    if canonical_bytes(request) != canonical_bytes(approved["request"]):
        _fail("SUNSET_APPROVAL_BINDING", "candidate request differs from approved request")
    _dynamic_validate(root, request, "sunset-request-v3.schema.json")

    legacy_request = {
        "schema_id": "atlas.lifecycle.sunset-request",
        "schema_version": "2.0.0",
        "authority": "PUBLIC_CLEAN_REQUEST",
        "request_id": request["request_id"],
        **_semantic(request),
    }
    with tempfile.TemporaryDirectory() as temp:
        temp_root = Path(temp)
        legacy_request_path = temp_root / "request-v2.json"
        _write_exact(legacy_request_path, canonical_bytes(legacy_request))
        legacy_dir = temp_root / "legacy-candidate"
        generate_legacy_candidate(root, legacy_request_path, legacy_dir)
        verify_legacy_candidate(root, legacy_dir)
        legacy_bundle = _read_canonical(
            legacy_dir / ARTIFACT_BUNDLE,
            "SUNSET_CANDIDATE_CANONICAL",
        )
        records = [dict(item["record"]) for item in legacy_bundle["records"]]

    related = sorted(
        {
            item["golden_wing_id"]
            for item in request["lesson_harvest"]["observations"]
            if item.get("golden_wing_id") is not None
        }
    )
    for record in records:
        if record["schema_id"] == "atlas.lifecycle.sunrise":
            record["related_golden_wing_ids"] = related
            record["record_id"] = stable_record_id(record)

    bindings, assertions, source_fingerprint = _validate_records(root, records)
    expected = {
        **approved["preview"]["expected_records"],
        "quest_identity_fabricated": False,
    }
    if assertions != expected:
        _fail("SUNSET_RECORD_PLAN", "candidate records differ from approved Preview")
    entries = [
        {"path": _record_path(record), "record": record}
        for record in sorted(records, key=_record_path)
    ]
    bundle = {
        "schema_id": "atlas.lifecycle.approved-sunset-candidate-bundle",
        "schema_version": "1.0.0",
        "authority": "TEMPORARY_CANDIDATE_ONLY",
        "engine_class": "SCRIPT_ASSIST_LEVEL_1B",
        "request_id": request["request_id"],
        "request_digest": approved["request_digest"],
        "preview_id": request["preview_id"],
        "preview_digest": request["preview_digest"],
        "approval_id": request["approval_id"],
        "approval_digest": request["approval_digest"],
        "carrier_id": request["carrier_id"],
        "carrier_digest": request["carrier_digest"],
        "semantic_digest": request["semantic_digest"],
        "approval_mode": request["approval_mode"],
        "permanence_mode": request["permanence_mode"],
        "expected_main_sha": observed_head(root),
        "source_fingerprint": source_fingerprint,
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
                "request_digest": approved["request_digest"],
                "preview_digest": request["preview_digest"],
                "approval_digest": request["approval_digest"],
                "carrier_digest": request["carrier_digest"],
            }
        )
    )
    receipt = {
        "schema_id": "atlas.lifecycle.approved-sunset-candidate-receipt",
        "schema_version": "1.0.0",
        "authority": "TEMPORARY_CANDIDATE_ONLY",
        "engine_class": "SCRIPT_ASSIST_LEVEL_1B",
        "command": "sunset candidate",
        "request_id": request["request_id"],
        "request_digest": approved["request_digest"],
        "preview_id": request["preview_id"],
        "preview_digest": request["preview_digest"],
        "approval_id": request["approval_id"],
        "approval_digest": request["approval_digest"],
        "carrier_id": request["carrier_id"],
        "carrier_digest": request["carrier_digest"],
        "semantic_digest": request["semantic_digest"],
        "approval_mode": request["approval_mode"],
        "permanence_mode": request["permanence_mode"],
        "bundle_digest": bundle_digest,
        "candidate_set_digest": candidate_set_digest,
        "expected_main_sha": bundle["expected_main_sha"],
        "source_fingerprint": bundle["source_fingerprint"],
        "record_count": len(entries),
        "verification_result": "PASS",
        "write_boundary": _write_boundary(),
    }
    destination = _validated_output_path(root, output_dir)
    _create_output_directory(destination)
    _write_exact(destination / ARTIFACT_BUNDLE, bundle_bytes)
    _write_exact(destination / ARTIFACT_RECEIPT, canonical_bytes(receipt))
    verified = verify_approved_sunset_candidate(root, destination)
    return {
        "authority": "TEMPORARY_CANDIDATE_ONLY",
        "command": "sunset candidate",
        "preview_id": request["preview_id"],
        "approval_id": request["approval_id"],
        "carrier_id": request["carrier_id"],
        "approval_mode": request["approval_mode"],
        "permanence_mode": request["permanence_mode"],
        "scope_type": bundle["scope_type"],
        "candidate_set_digest": verified["candidate_set_digest"],
        "record_count": len(entries),
        "record_bindings": bindings,
        "assertions": assertions,
        "writes_performed": ["SYSTEM_TEMPORARY_DIRECTORY"],
        "canonical_writes": False,
        "github_actions": [],
        "status": "PASS",
    }


APPROVED_BUNDLE_KEYS = {
    "schema_id", "schema_version", "authority", "engine_class", "request_id",
    "request_digest", "preview_id", "preview_digest", "approval_id",
    "approval_digest", "carrier_id", "carrier_digest", "semantic_digest",
    "approval_mode", "permanence_mode", "expected_main_sha",
    "source_fingerprint", "scope_type", "record_bindings", "records",
    "assertions", "write_boundary",
}
APPROVED_RECEIPT_KEYS = {
    "schema_id", "schema_version", "authority", "engine_class", "command",
    "request_id", "request_digest", "preview_id", "preview_digest",
    "approval_id", "approval_digest", "carrier_id", "carrier_digest",
    "semantic_digest", "approval_mode", "permanence_mode", "bundle_digest",
    "candidate_set_digest", "expected_main_sha", "source_fingerprint",
    "record_count", "verification_result", "write_boundary",
}


def verify_approved_sunset_candidate(
    repo_root: Path,
    candidate_dir: Path,
) -> dict[str, Any]:
    root = repo_root.resolve()
    if not candidate_dir.is_dir() or candidate_dir.is_symlink():
        _fail("SUNSET_CANDIDATE_DIRECTORY", "Sunset candidate directory is unsafe")
    members = sorted(candidate_dir.iterdir(), key=lambda path: path.name)
    if [path.name for path in members] != [ARTIFACT_BUNDLE, ARTIFACT_RECEIPT]:
        _fail("SUNSET_CANDIDATE_MEMBERS", "Sunset candidate has unexpected members")
    bundle = _read_canonical(
        candidate_dir / ARTIFACT_BUNDLE,
        "SUNSET_CANDIDATE_CANONICAL",
    )
    receipt = _read_canonical(
        candidate_dir / ARTIFACT_RECEIPT,
        "SUNSET_CANDIDATE_CANONICAL",
    )
    if (
        set(bundle) != APPROVED_BUNDLE_KEYS
        or set(receipt) != APPROVED_RECEIPT_KEYS
        or bundle.get("schema_id")
        != "atlas.lifecycle.approved-sunset-candidate-bundle"
        or receipt.get("schema_id")
        != "atlas.lifecycle.approved-sunset-candidate-receipt"
        or bundle.get("schema_version") != "1.0.0"
        or receipt.get("schema_version") != "1.0.0"
        or bundle.get("authority") != "TEMPORARY_CANDIDATE_ONLY"
        or receipt.get("authority") != "TEMPORARY_CANDIDATE_ONLY"
        or bundle.get("engine_class") != "SCRIPT_ASSIST_LEVEL_1B"
        or receipt.get("engine_class") != "SCRIPT_ASSIST_LEVEL_1B"
        or receipt.get("command") != "sunset candidate"
    ):
        _fail("SUNSET_CANDIDATE_IDENTITY", "approved Sunset candidate identity is invalid")
    bundle_digest = _digest(canonical_bytes(bundle))
    candidate_set_digest = _digest(
        canonical_bytes(
            {
                "bundle_digest": bundle_digest,
                "request_digest": bundle["request_digest"],
                "preview_digest": bundle["preview_digest"],
                "approval_digest": bundle["approval_digest"],
                "carrier_digest": bundle["carrier_digest"],
            }
        )
    )
    if (
        receipt["bundle_digest"] != bundle_digest
        or receipt["candidate_set_digest"] != candidate_set_digest
        or receipt["request_digest"] != bundle["request_digest"]
        or receipt["preview_digest"] != bundle["preview_digest"]
        or receipt["approval_digest"] != bundle["approval_digest"]
        or receipt["carrier_digest"] != bundle["carrier_digest"]
        or receipt["record_count"] != len(bundle["records"])
        or receipt["verification_result"] != "PASS"
        or receipt["write_boundary"] != _write_boundary()
        or bundle["write_boundary"] != _write_boundary()
    ):
        _fail("SUNSET_CANDIDATE_BINDING", "approved Sunset candidate is not cross-bound")
    records = [entry["record"] for entry in bundle["records"]]
    bindings, assertions, source_fingerprint = _validate_records(root, records)
    if (
        bindings != bundle["record_bindings"]
        or assertions != bundle["assertions"]
        or source_fingerprint != bundle["source_fingerprint"]
    ):
        _fail("SUNSET_CANDIDATE_BINDING", "approved Sunset record bindings changed")
    if [entry["path"] for entry in bundle["records"]] != [
        item["path"] for item in bindings
    ]:
        _fail("SUNSET_CANDIDATE_RECORD_PATH", "approved Sunset record paths changed")
    return {
        "authority": "READ_ONLY",
        "command": "sunset verify",
        "request_id": bundle["request_id"],
        "preview_id": bundle["preview_id"],
        "approval_id": bundle["approval_id"],
        "carrier_id": bundle["carrier_id"],
        "scope_type": bundle["scope_type"],
        "candidate_set_digest": candidate_set_digest,
        "record_count": len(records),
        "record_bindings": bindings,
        "assertions": assertions,
        "status": "PASS",
    }
