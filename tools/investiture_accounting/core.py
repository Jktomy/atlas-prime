from __future__ import annotations

import hashlib
import ipaddress
import json
import re
from pathlib import Path
from typing import Any

from tools.athena_routes.schema import SchemaValidationError, validate_schema


ROOT = Path(__file__).resolve().parents[2]
SCHEMAS = {
    "event": ROOT / "schemas/investiture-event-v1.schema.json",
    "manifest": ROOT / "schemas/investiture-ledger-manifest-v1.schema.json",
    "record": ROOT / "schemas/investiture-ledger-record-v1.schema.json",
    "receipt": ROOT / "schemas/investiture-operation-receipt-v1.schema.json",
    "summary": ROOT / "schemas/investiture-summary-v1.schema.json",
}
ZERO_SHA256 = "0" * 64
LIGHTS = {"OPENAI": "Spirallight", "GOOGLE": "Chromelight", "ATLAS_LOCAL": "Emberlight"}
MEASUREMENT_STATES = ("MEASURED", "PARTIAL", "UNAVAILABLE", "ZERO_MODEL")
SENSITIVE_VALUE_PATTERNS = (
    re.compile(r"(?i)^(?:sk|rk|pk)-[a-z0-9_-]{8,}$"),
    re.compile(r"(?i)^(?:gh[pousr]_|github_pat_|AIza)[a-z0-9_-]{8,}$"),
    re.compile(r"^eyJ[A-Za-z0-9_-]+[.]eyJ[A-Za-z0-9_-]+[.][A-Za-z0-9_-]+$"),
    re.compile(r"^(?:[0-9]{1,3}[.]){3}[0-9]{1,3}$"),
)


class InvestitureError(ValueError):
    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def stable_json(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_object(value: Any) -> str:
    return sha256_bytes(stable_json(value))


def _pairs_no_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, child in pairs:
        if key in value:
            raise InvestitureError("DUPLICATE_JSON_KEY")
        value[key] = child
    return value


def strict_loads(raw: bytes) -> dict[str, Any]:
    try:
        text = raw.decode("utf-8", errors="strict")
        value = json.loads(text, object_pairs_hook=_pairs_no_duplicates)
    except InvestitureError:
        raise
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise InvestitureError("EVENT_JSON_INVALID") from exc
    if not isinstance(value, dict):
        raise InvestitureError("EVENT_JSON_INVALID")
    return value


def _schema(name: str) -> dict[str, Any]:
    return json.loads(SCHEMAS[name].read_text(encoding="utf-8"))


def validate_against_schema(name: str, value: dict[str, Any], code: str) -> None:
    try:
        validate_schema(_schema(name), value)
    except SchemaValidationError as exc:
        raise InvestitureError(code) from exc


def _validate_categories(measurement: dict[str, Any]) -> int:
    categories = measurement["categories"]
    by_id = {item["category_id"]: item for item in categories}
    if len(by_id) != len(categories):
        raise InvestitureError("CATEGORY_DUPLICATE")
    for item in categories:
        parent = item["parent_category_id"]
        if parent is not None and (parent not in by_id or parent == item["category_id"]):
            raise InvestitureError("CATEGORY_PARENT_INVALID")
        visited: set[str] = set()
        cursor = parent
        while cursor is not None:
            if cursor in visited:
                raise InvestitureError("CATEGORY_CYCLE")
            visited.add(cursor)
            cursor = by_id[cursor]["parent_category_id"]
    counted = [item for item in categories if item["role"] == "COUNTED"]
    if not counted:
        raise InvestitureError("COUNTED_CATEGORY_REQUIRED")
    basis = measurement["counting_basis"]
    if basis == "AUTHORITATIVE_TOTAL":
        if len(counted) != 1 or counted[0]["explicitly_disjoint"]:
            raise InvestitureError("AUTHORITATIVE_TOTAL_INVALID")
    elif basis == "DISJOINT_LEAVES":
        if any(not item["explicitly_disjoint"] for item in counted):
            raise InvestitureError("DISJOINT_DECLARATION_REQUIRED")
        counted_ids = {item["category_id"] for item in counted}
        for item in counted:
            cursor = item["parent_category_id"]
            while cursor is not None:
                if cursor in counted_ids:
                    raise InvestitureError("COUNTED_CATEGORY_OVERLAP")
                cursor = by_id[cursor]["parent_category_id"]
    else:
        raise InvestitureError("COUNTING_BASIS_INVALID")
    return sum(item["token_count"] for item in counted)


def _reject_sensitive_values(value: Any) -> None:
    if isinstance(value, dict):
        for child in value.values():
            _reject_sensitive_values(child)
    elif isinstance(value, list):
        for child in value:
            _reject_sensitive_values(child)
    elif isinstance(value, str):
        if any(pattern.fullmatch(value) for pattern in SENSITIVE_VALUE_PATTERNS):
            raise InvestitureError("SENSITIVE_VALUE_REJECTED")
        try:
            ipaddress.ip_address(value)
        except ValueError:
            pass
        else:
            raise InvestitureError("SENSITIVE_VALUE_REJECTED")


def validate_event(event: dict[str, Any]) -> dict[str, Any]:
    validate_against_schema("event", event, "EVENT_SCHEMA_INVALID")
    _reject_sensitive_values(event)
    bound = event["bound_usage_event_ids"]
    if len(bound) != len(set(bound)):
        raise InvestitureError("BOUND_USAGE_DUPLICATE")
    if event["event_type"] != "USAGE_REPORTED":
        if event["measurement"] is not None:
            raise InvestitureError("LIFECYCLE_MEASUREMENT_FORBIDDEN")
        return event
    if bound:
        raise InvestitureError("USAGE_EVENT_BINDING_FORBIDDEN")
    measurement = event["measurement"]
    if not isinstance(measurement, dict):
        raise InvestitureError("USAGE_MEASUREMENT_REQUIRED")
    state = measurement["state"]
    if state in {"MEASURED", "PARTIAL"}:
        required = (
            "provider_origin", "model_id", "runtime_id", "atlas_runtime_control", "light",
            "usage_scope_id", "source_receipt_sha256", "category_semantics_sha256", "counting_basis",
        )
        if any(measurement[key] is None for key in required):
            raise InvestitureError("COUNTABLE_IDENTITY_INCOMPLETE")
        if measurement["light"] != LIGHTS[measurement["provider_origin"]]:
            raise InvestitureError("LIGHT_IDENTITY_MISMATCH")
        if measurement["provider_origin"] == "ATLAS_LOCAL" and measurement["atlas_runtime_control"] is not True:
            raise InvestitureError("LOCAL_RUNTIME_CONTROL_REQUIRED")
        computed = _validate_categories(measurement)
        if state == "MEASURED":
            if measurement["known_beu_subtotal"] is not None or measurement["total_investiture_beu"] != computed:
                raise InvestitureError("MEASURED_TOTAL_INVALID")
        elif measurement["known_beu_subtotal"] != computed or measurement["total_investiture_beu"] is not None:
            raise InvestitureError("PARTIAL_SUBTOTAL_INVALID")
    elif state == "UNAVAILABLE":
        if measurement["light"] is not None or measurement["counting_basis"] is not None or measurement["categories"]:
            raise InvestitureError("UNAVAILABLE_COUNTING_FORBIDDEN")
        if measurement["known_beu_subtotal"] is not None or measurement["total_investiture_beu"] is not None:
            raise InvestitureError("UNAVAILABLE_VALUE_FORBIDDEN")
    elif state == "ZERO_MODEL":
        identity_fields = (
            "provider_origin", "model_id", "runtime_id", "atlas_runtime_control", "light", "usage_scope_id",
            "source_receipt_sha256", "category_semantics_sha256", "counting_basis",
        )
        if any(measurement[key] is not None for key in identity_fields) or measurement["categories"]:
            raise InvestitureError("ZERO_MODEL_IDENTITY_FORBIDDEN")
        if measurement["known_beu_subtotal"] is not None or measurement["total_investiture_beu"] != 0:
            raise InvestitureError("ZERO_MODEL_VALUE_INVALID")
    else:
        raise InvestitureError("MEASUREMENT_STATE_INVALID")
    return event


def event_from_bytes(raw: bytes) -> dict[str, Any]:
    return validate_event(strict_loads(raw))


def _with_digest(value: dict[str, Any], field: str) -> dict[str, Any]:
    candidate = dict(value)
    candidate[field] = sha256_object(value)
    return candidate


def build_manifest(*, ledger_id: str, generation_id: str, created_at: str,
                   previous_generation_id: str | None = None,
                   previous_last_record_sha256: str | None = None,
                   inherited_summary: dict[str, Any] | None = None,
                   inherited_identities: dict[str, list[str]] | None = None) -> dict[str, Any]:
    previous_bound = previous_generation_id is not None or previous_last_record_sha256 is not None
    if previous_bound and (inherited_summary is None or inherited_identities is None):
        raise InvestitureError("MANIFEST_INHERITANCE_REQUIRED")
    if not previous_bound and (inherited_summary is not None or inherited_identities is not None):
        raise InvestitureError("MANIFEST_GENESIS_INHERITANCE_FORBIDDEN")
    inherited = inherited_summary or {
        "record_count": 0,
        "measurement_counts": {state: 0 for state in MEASUREMENT_STATES},
        "light_known_beu": {light: 0 for light in LIGHTS.values()},
        "known_beu_subtotal": 0,
        "total_investiture_beu": 0,
        "complete_total_available": True,
    }
    identities = inherited_identities or {
        "event": [], "replay": [], "usage_event": [], "usage_scope": [], "source_receipt": [],
    }
    manifest = {
        "schema_version": "atlas.investiture-ledger-manifest.v1",
        "ledger_id": ledger_id,
        "generation_id": generation_id,
        "created_at": created_at,
        "previous_generation_id": previous_generation_id,
        "previous_last_record_sha256": previous_last_record_sha256,
        "inherited_record_count": inherited["record_count"],
        "inherited_measurement_counts": inherited["measurement_counts"],
        "inherited_light_known_beu": inherited["light_known_beu"],
        "inherited_known_beu_subtotal": inherited["known_beu_subtotal"],
        "inherited_total_investiture_beu": inherited["total_investiture_beu"],
        "inherited_complete_total_available": inherited["complete_total_available"],
        "inherited_event_identity_sha256s": identities["event"],
        "inherited_replay_identity_sha256s": identities["replay"],
        "inherited_usage_event_identity_sha256s": identities["usage_event"],
        "inherited_usage_scope_identity_sha256s": identities["usage_scope"],
        "inherited_source_receipt_identity_sha256s": identities["source_receipt"],
    }
    manifest = _with_digest(manifest, "manifest_sha256")
    validate_manifest(manifest)
    return manifest


def validate_manifest(manifest: dict[str, Any]) -> None:
    validate_against_schema("manifest", manifest, "MANIFEST_SCHEMA_INVALID")
    body = {key: value for key, value in manifest.items() if key != "manifest_sha256"}
    if manifest["manifest_sha256"] != sha256_object(body):
        raise InvestitureError("MANIFEST_DIGEST_MISMATCH")
    paired = (manifest["previous_generation_id"], manifest["previous_last_record_sha256"])
    if (paired[0] is None) != (paired[1] is None):
        raise InvestitureError("MANIFEST_PREVIOUS_BINDING_INVALID")
    expected_count_keys = set(MEASUREMENT_STATES)
    expected_light_keys = set(LIGHTS.values())
    if set(manifest["inherited_measurement_counts"]) != expected_count_keys or set(manifest["inherited_light_known_beu"]) != expected_light_keys:
        raise InvestitureError("MANIFEST_INHERITED_SUMMARY_INVALID")
    if any(not isinstance(value, int) or isinstance(value, bool) or value < 0 for value in manifest["inherited_measurement_counts"].values()):
        raise InvestitureError("MANIFEST_INHERITED_SUMMARY_INVALID")
    if any(not isinstance(value, int) or isinstance(value, bool) or value < 0 for value in manifest["inherited_light_known_beu"].values()):
        raise InvestitureError("MANIFEST_INHERITED_SUMMARY_INVALID")
    if paired[0] is None and (
        manifest["inherited_record_count"] != 0
        or any(manifest["inherited_measurement_counts"].values())
        or any(manifest["inherited_light_known_beu"].values())
        or manifest["inherited_known_beu_subtotal"] != 0
        or manifest["inherited_total_investiture_beu"] != 0
        or manifest["inherited_complete_total_available"] is not True
        or any(manifest[key] for key in (
            "inherited_event_identity_sha256s", "inherited_replay_identity_sha256s",
            "inherited_usage_event_identity_sha256s", "inherited_usage_scope_identity_sha256s",
            "inherited_source_receipt_identity_sha256s",
        ))
    ):
        raise InvestitureError("MANIFEST_INHERITED_SUMMARY_INVALID")
    for key in (
        "inherited_event_identity_sha256s", "inherited_replay_identity_sha256s",
        "inherited_usage_event_identity_sha256s", "inherited_usage_scope_identity_sha256s",
        "inherited_source_receipt_identity_sha256s",
    ):
        values = manifest[key]
        if values != sorted(set(values)):
            raise InvestitureError("MANIFEST_INHERITED_IDENTITIES_INVALID")
    counts = manifest["inherited_measurement_counts"]
    lights = manifest["inherited_light_known_beu"]
    known = manifest["inherited_known_beu_subtotal"]
    total = manifest["inherited_total_investiture_beu"]
    complete = manifest["inherited_complete_total_available"]
    if known != sum(lights.values()) or (complete and total != known) or (not complete and total is not None):
        raise InvestitureError("MANIFEST_INHERITED_TOTAL_INVALID")
    usage_count = sum(counts.values())
    countable_count = counts["MEASURED"] + counts["PARTIAL"]
    event_ids = manifest["inherited_event_identity_sha256s"]
    replay_ids = manifest["inherited_replay_identity_sha256s"]
    usage_ids = manifest["inherited_usage_event_identity_sha256s"]
    scope_ids = manifest["inherited_usage_scope_identity_sha256s"]
    receipt_ids = manifest["inherited_source_receipt_identity_sha256s"]
    if (
        len(event_ids) != manifest["inherited_record_count"]
        or len(replay_ids) != manifest["inherited_record_count"]
        or len(usage_ids) != usage_count
        or len(scope_ids) != countable_count
        or len(receipt_ids) != countable_count
        or not set(usage_ids).issubset(set(event_ids))
    ):
        raise InvestitureError("MANIFEST_INHERITED_CARDINALITY_INVALID")


def build_record(manifest: dict[str, Any], event: dict[str, Any], *, sequence: int, prior_sha256: str) -> dict[str, Any]:
    validate_manifest(manifest)
    validate_event(event)
    body = {
        "schema_version": "atlas.investiture-ledger-record.v1",
        "ledger_id": manifest["ledger_id"],
        "generation_id": manifest["generation_id"],
        "sequence": sequence,
        "prior_record_sha256": prior_sha256,
        "event_sha256": sha256_object(event),
        "event": event,
    }
    record = _with_digest(body, "record_sha256")
    validate_record(record, manifest)
    return record


def validate_record(record: dict[str, Any], manifest: dict[str, Any]) -> None:
    validate_against_schema("record", record, "RECORD_SCHEMA_INVALID")
    if record["ledger_id"] != manifest["ledger_id"] or record["generation_id"] != manifest["generation_id"]:
        raise InvestitureError("RECORD_MANIFEST_BINDING_INVALID")
    validate_event(record["event"])
    if record["event_sha256"] != sha256_object(record["event"]):
        raise InvestitureError("EVENT_DIGEST_MISMATCH")
    body = {key: value for key, value in record.items() if key != "record_sha256"}
    if record["record_sha256"] != sha256_object(body):
        raise InvestitureError("RECORD_DIGEST_MISMATCH")


def build_summary(manifest: dict[str, Any], records: list[dict[str, Any]]) -> dict[str, Any]:
    validate_manifest(manifest)
    prior = manifest["previous_last_record_sha256"] or ZERO_SHA256
    for index, record in enumerate(records, start=1):
        validate_record(record, manifest)
        if record["sequence"] != index or record["prior_record_sha256"] != prior:
            raise InvestitureError("SUMMARY_RECORD_CHAIN_INVALID")
        prior = record["record_sha256"]
    counts = dict(manifest["inherited_measurement_counts"])
    lights = dict(manifest["inherited_light_known_beu"])
    known = manifest["inherited_known_beu_subtotal"]
    complete = manifest["inherited_complete_total_available"]
    for record in records:
        event = record["event"]
        if event["event_type"] != "USAGE_REPORTED":
            continue
        measurement = event["measurement"]
        state = measurement["state"]
        counts[state] += 1
        if state == "MEASURED":
            value = measurement["total_investiture_beu"]
            lights[measurement["light"]] += value
            known += value
        elif state == "PARTIAL":
            value = measurement["known_beu_subtotal"]
            lights[measurement["light"]] += value
            known += value
            complete = False
        elif state == "UNAVAILABLE":
            complete = False
    body = {
        "schema_version": "atlas.investiture-summary.v1",
        "ledger_id": manifest["ledger_id"],
        "generation_id": manifest["generation_id"],
        "record_count": manifest["inherited_record_count"] + len(records),
        "head_sha256": records[-1]["record_sha256"] if records else (manifest["previous_last_record_sha256"] or ZERO_SHA256),
        "measurement_counts": counts,
        "light_known_beu": lights,
        "known_beu_subtotal": known,
        "total_investiture_beu": known if complete else None,
        "complete_total_available": complete,
    }
    summary = _with_digest(body, "summary_sha256")
    validate_against_schema("summary", summary, "SUMMARY_SCHEMA_INVALID")
    return summary
