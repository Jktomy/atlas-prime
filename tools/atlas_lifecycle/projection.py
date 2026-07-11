from __future__ import annotations

import hashlib
import json
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .errors import LifecycleError
from .jsonio import canonical_bytes, loads_bounded, read_bounded
from .limits import MAX_INDEX_BYTES, MAX_INDEX_NODES
from .repository import ValidationResult, validate_repository
from .schema import SchemaValidator


INDEX_RELATIVE_PATH = Path("generated/lifecycle/website-index-v2.json")
GENERATOR_VERSION = "0.2.0"
STABLE_ID = re.compile(r"^(?:FTR|FAR|GWN|QEM|QCP|SUN|SRI|CON|LCR)-[A-Z2-7]{26}$")
TYPE_BY_SCHEMA = {
    "atlas.lifecycle.feather": "FEATHER",
    "atlas.lifecycle.feather-archive": "FEATHER_ARCHIVE",
    "atlas.lifecycle.golden-wing": "GOLDEN_WING",
    "atlas.lifecycle.quest-emberline": "QUEST_EMBERLINE",
    "atlas.lifecycle.quest-checkpoint": "QUEST_CHECKPOINT",
    "atlas.lifecycle.sunset": "SUNSET",
    "atlas.lifecycle.sunrise": "SUNRISE",
    "atlas.lifecycle.continuity": "CONTINUITY",
    "atlas.lifecycle.receipt": "LIFECYCLE_RECEIPT",
}


@dataclass(frozen=True)
class IndexCheck:
    status: str
    expected_digest: str
    expected_bytes: bytes
    source_revision: str
    source_timestamp: str
    source_fingerprint: str
    warning: str | None


def source_revision(repo_root: Path) -> tuple[str, str]:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD:lifecycle"],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
        timeout=10,
    )
    tree_sha = result.stdout.strip()
    if result.returncode != 0 or re.fullmatch(r"[a-f0-9]{40}", tree_sha) is None:
        raise LifecycleError("SOURCE_REVISION_UNAVAILABLE", "lifecycle source revision is unavailable")
    epoch_2000 = 946_684_800
    hundred_year_seconds = 3_155_760_000
    derived_epoch = epoch_2000 + (int(tree_sha[:16], 16) % hundred_year_seconds)
    timestamp = datetime.fromtimestamp(derived_epoch, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return tree_sha, timestamp


def _values(record: dict[str, Any], singular: str, plural: str) -> list[str]:
    values: list[str] = []
    if isinstance(record.get(singular), str):
        values.append(record[singular])
    if isinstance(record.get(plural), list):
        values.extend(value for value in record[plural] if isinstance(value, str))
    return sorted(set(values))


def _related_ids(record: dict[str, Any]) -> list[str]:
    found: set[str] = set()

    def walk(value: Any, *, root: bool = False) -> None:
        if isinstance(value, str) and STABLE_ID.fullmatch(value):
            if value != record["record_id"]:
                found.add(value)
        elif isinstance(value, dict):
            for nested in value.values():
                walk(nested)
        elif isinstance(value, list):
            for nested in value:
                walk(nested)

    walk(record, root=True)
    return sorted(found)


def _references(record: dict[str, Any]) -> list[dict[str, Any]]:
    values: list[dict[str, Any]] = []
    for key in (
        "durable_source_references",
        "evidence_pointers",
        "recurrence_evidence",
        "exact_source_references",
    ):
        candidate = record.get(key)
        if isinstance(candidate, list):
            values.extend(item for item in candidate if isinstance(item, dict))
    unique = {canonical_bytes({"value": item}): item for item in values}
    return [unique[key] for key in sorted(unique)]


def _summary(record: dict[str, Any]) -> str | None:
    for key in (
        "context_summary",
        "checkpoint_summary",
        "completion_assessment",
        "current_position",
        "recovery_reason",
        "diagnostic_summary",
        "lesson",
        "archive_reason",
    ):
        value = record.get(key)
        if isinstance(value, str):
            return value
    return None


def project_record(record: dict[str, Any]) -> dict[str, Any]:
    schema_id = record["schema_id"]
    record_type = TYPE_BY_SCHEMA.get(schema_id)
    if record_type is None:
        raise LifecycleError("UNSUPPORTED_PROJECTION_RECORD", "record type has no website projection")
    quest_ids = _values(record, "quest_id", "originating_quest_ids")
    candidate_refs: list[str] = []
    scope = record.get("quest_scope")
    if isinstance(scope, dict):
        if isinstance(scope.get("quest_id"), str):
            quest_ids.append(scope["quest_id"])
        if isinstance(scope.get("candidate_quest_ref"), str):
            candidate_refs.append(scope["candidate_quest_ref"])
    protection = record.get("protected_data")
    promotion = record.get("promotion_readiness")
    revision = record.get("quest_revision")
    return {
        "record_id": record["record_id"],
        "record_type": record_type,
        "schema_version": record["schema_version"],
        "lifecycle_status": str(
            record.get("lifecycle_status")
            or record.get("verification_result")
            or record.get("reconstruction_accuracy")
            or "RECORDED"
        ),
        "record_revision": revision if isinstance(revision, int) else None,
        "project_ids": _values(record, "project_id", "originating_project_ids"),
        "operation_ids": _values(record, "operation_id", "operation_ids"),
        "quest_ids": sorted(set(quest_ids)),
        "candidate_quest_refs": sorted(set(candidate_refs)),
        "campaign": record.get("campaign") if isinstance(record.get("campaign"), str) else None,
        "mission": record.get("mission") if isinstance(record.get("mission"), str) else None,
        "gate": record.get("gate") if isinstance(record.get("gate"), str) else None,
        "related_record_ids": _related_ids(record),
        "summary": _summary(record),
        "current_position": record.get("current_position") if isinstance(record.get("current_position"), str) else None,
        "unresolved_blockers": list(record.get("unresolved_blockers", [])),
        "next_safe_action": record.get("next_safe_action") if isinstance(record.get("next_safe_action"), str) else None,
        "next_gate": record.get("next_gate") if isinstance(record.get("next_gate"), str) else None,
        "latest_feather_id": record.get("latest_feather_id") if isinstance(record.get("latest_feather_id"), str) else None,
        "evidence_references": _references(record),
        "protected_warning": isinstance(protection, dict)
        and protection.get("classification") == "PROTECTED_POINTER_ONLY",
        "promotion_readiness": promotion.get("state") if isinstance(promotion, dict) else None,
        "source_record_digest": f"sha256:{hashlib.sha256(canonical_bytes(record)).hexdigest()}",
    }


def build_website_index(
    snapshot: ValidationResult,
    *,
    source_revision_sha: str,
    source_timestamp: str,
    schema_dir: Path,
) -> dict[str, Any]:
    records = [project_record(record) for record in snapshot.canonical_records]
    records.sort(key=lambda item: (item["record_type"], item["record_id"]))
    known_ids = {item["record_id"] for item in records}
    for item in records:
        if any(related not in known_ids for related in item["related_record_ids"]):
            raise LifecycleError(
                "DANGLING_PROJECTION_RELATIONSHIP",
                "lifecycle projection contains a relationship to a nonexistent record",
            )
    value = {
        "schema_id": "atlas.lifecycle.website-index",
        "schema_version": "2.0.0",
        "authority": "GENERATED_NONCANONICAL_PROJECTION",
        "generator_version": GENERATOR_VERSION,
        "generated_timestamp": source_timestamp,
        "source_revision": source_revision_sha,
        "source_fingerprint": snapshot.source_fingerprint,
        "records": records,
    }
    SchemaValidator(schema_dir).validate_projection(value)
    return value


def check_website_index(repo_root: Path) -> tuple[IndexCheck, ValidationResult]:
    root = repo_root.resolve()
    snapshot = validate_repository(root, check_stale=True)
    revision, timestamp = source_revision(root)
    value = build_website_index(
        snapshot,
        source_revision_sha=revision,
        source_timestamp=timestamp,
        schema_dir=root / "lifecycle/schemas",
    )
    expected = canonical_bytes(value, max_nodes=MAX_INDEX_NODES)
    expected_digest = f"sha256:{hashlib.sha256(expected).hexdigest()}"
    path = root / INDEX_RELATIVE_PATH
    cursor = root
    path_has_link = False
    for part in INDEX_RELATIVE_PATH.parts:
        cursor = cursor / part
        if cursor.is_symlink():
            path_has_link = True
            break
    if path_has_link:
        status, warning = "INVALID", "website lifecycle index path traverses a link"
    elif not path.exists():
        status, warning = "MISSING", "website lifecycle index is missing"
    elif not path.is_file() or path.is_symlink():
        status, warning = "INVALID", "website lifecycle index is not a regular file"
    else:
        try:
            observed = read_bounded(path, max_bytes=MAX_INDEX_BYTES)
            parsed = loads_bounded(
                observed,
                label=path.name,
                max_bytes=MAX_INDEX_BYTES,
                max_nodes=MAX_INDEX_NODES,
            )
            SchemaValidator(root / "lifecycle/schemas").validate_projection(parsed)
        except LifecycleError:
            status, warning = "INVALID", "website lifecycle index is malformed or untrusted"
        else:
            if observed == expected:
                status, warning = "CURRENT", None
            else:
                status, warning = "STALE", "website lifecycle index source binding is stale"
    return (
        IndexCheck(
            status=status,
            expected_digest=expected_digest,
            expected_bytes=expected,
            source_revision=revision,
            source_timestamp=timestamp,
            source_fingerprint=snapshot.source_fingerprint,
            warning=warning,
        ),
        snapshot,
    )


def compact_context(
    snapshot: ValidationResult,
    *,
    quest_id: str | None,
    projection_warning: str | None,
) -> dict[str, Any]:
    records = snapshot.canonical_records
    emberlines = [
        record for record in records if record.get("schema_id") == "atlas.lifecycle.quest-emberline"
    ]
    if quest_id is None:
        if len(emberlines) > 1:
            raise LifecycleError("QUEST_SELECTION_REQUIRED", "multiple admitted Quests require an exact quest ID")
        emberline = emberlines[0] if emberlines else None
    else:
        emberline = next((record for record in emberlines if record.get("quest_id") == quest_id), None)
        if emberline is None:
            raise LifecycleError("QUEST_NOT_FOUND", "requested admitted Quest has no current Emberline")
    if emberline is None:
        return {
            "current_quest_position": None,
            "latest_valid_feather": None,
            "unresolved_blockers": [],
            "next_gate": None,
            "related_golden_wings": [],
            "exact_source_references": [],
            "source_fingerprint": snapshot.source_fingerprint,
            "stale_projection_warnings": [projection_warning] if projection_warning else [],
        }

    latest_id = emberline.get("latest_feather_id")
    feather = next((record for record in records if record.get("record_id") == latest_id), None)
    if latest_id is not None and (
        feather is None
        or feather.get("schema_id") != "atlas.lifecycle.feather"
        or feather.get("lifecycle_status") not in {"SEALED", "ARCHIVED", "SUPERSEDED"}
    ):
        raise LifecycleError("LATEST_FEATHER_INVALID", "current Quest references no valid latest Feather")
    quest = emberline["quest_id"]
    related = sorted(
        record["record_id"]
        for record in records
        if record.get("schema_id") == "atlas.lifecycle.golden-wing"
        and (
            quest in record.get("originating_quest_ids", [])
            or (latest_id is not None and latest_id in record.get("supporting_feather_ids", []))
        )
    )
    references = _references(emberline) + (_references(feather) if feather else [])
    unique = {json.dumps(item, sort_keys=True, separators=(",", ":")): item for item in references}
    return {
        "current_quest_position": emberline["current_position"],
        "latest_valid_feather": latest_id,
        "unresolved_blockers": list(emberline["unresolved_blockers"]),
        "next_gate": emberline["next_gate"],
        "related_golden_wings": related,
        "exact_source_references": [unique[key] for key in sorted(unique)],
        "source_fingerprint": snapshot.source_fingerprint,
        "stale_projection_warnings": [projection_warning] if projection_warning else [],
    }
