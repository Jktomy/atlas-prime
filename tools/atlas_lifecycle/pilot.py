from __future__ import annotations

import hashlib
import json
import statistics
import time
from dataclasses import replace
from pathlib import Path
from typing import Any, Callable

from .errors import LifecycleError
from .jsonio import canonical_bytes, loads_bounded, read_bounded
from .projection import compact_context
from .protection import enforce_clean_values
from .repository import ValidationResult, validate_repository


PILOT_ID = "G3-D-COMPACT-CONTEXT-R01"
PILOT_FIXTURES = (
    "lifecycle/fixtures/quest-emberline-context.json",
    "lifecycle/fixtures/feather-quest-bound.json",
    "lifecycle/fixtures/golden-wing-multi-context.json",
)


def _reference_key(value: dict[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _references(record: dict[str, Any]) -> list[dict[str, Any]]:
    values: list[dict[str, Any]] = []
    for key in ("durable_source_references", "evidence_pointers"):
        candidate = record.get(key)
        if isinstance(candidate, list):
            values.extend(item for item in candidate if isinstance(item, dict))
    return values


def _manual_context(records: tuple[dict[str, Any], ...]) -> dict[str, Any]:
    emberline = next(record for record in records if record["schema_id"] == "atlas.lifecycle.quest-emberline")
    feather = next(record for record in records if record["record_id"] == emberline["latest_feather_id"])
    wing = next(record for record in records if record["schema_id"] == "atlas.lifecycle.golden-wing")
    references = _references(emberline) + _references(feather)
    unique = {_reference_key(item): item for item in references}
    related = []
    if (
        emberline["quest_id"] in wing["originating_quest_ids"]
        or feather["record_id"] in wing["supporting_feather_ids"]
    ):
        related.append(wing["record_id"])
    return {
        "current_quest_position": emberline["current_position"],
        "latest_valid_feather": feather["record_id"],
        "unresolved_blockers": list(emberline["unresolved_blockers"]),
        "next_gate": emberline["next_gate"],
        "related_golden_wings": sorted(related),
        "exact_source_references": [unique[key] for key in sorted(unique)],
        "source_fingerprint": "",
        "stale_projection_warnings": ["website lifecycle index is missing"],
    }


def _median_ns(operation: Callable[[], dict[str, Any]], repetitions: int) -> int:
    values: list[int] = []
    for _ in range(repetitions):
        started = time.perf_counter_ns()
        operation()
        values.append(time.perf_counter_ns() - started)
    return int(statistics.median(values))


def run_context_pilot(repo_root: Path, *, repetitions: int = 500) -> dict[str, Any]:
    if repetitions < 10 or repetitions > 10_000:
        raise LifecycleError("PILOT_REPETITIONS", "pilot repetitions must be between 10 and 10000")
    root = repo_root.resolve()
    snapshot = validate_repository(root)
    fixture_bytes = {path: read_bounded(root / path) for path in PILOT_FIXTURES}
    fixture_inputs = {
        path: loads_bounded(data, label=Path(path).name)
        for path, data in fixture_bytes.items()
    }
    fixture_by_id = {record["record_id"]: record for record in snapshot.fixture_records}
    selected_by_path: dict[str, dict[str, Any]] = {}
    for path in PILOT_FIXTURES:
        record = fixture_by_id.get(fixture_inputs[path]["record_id"])
        if record is None:
            raise LifecycleError("PILOT_FIXTURE_MISMATCH", "pilot fixture was not validated")
        selected_by_path[path] = record
    selected = tuple(selected_by_path[path] for path in PILOT_FIXTURES)
    pilot_snapshot: ValidationResult = replace(
        snapshot,
        records=len(selected),
        canonical_records=selected,
    )

    def manual_operation() -> dict[str, Any]:
        value = _manual_context(selected)
        value["source_fingerprint"] = snapshot.source_fingerprint
        return value

    def script_operation() -> dict[str, Any]:
        return compact_context(
            pilot_snapshot,
            quest_id="found-silverlight",
            projection_warning="website lifecycle index is missing",
        )

    manual_context = manual_operation()
    script_context = script_operation()
    if manual_context != script_context:
        raise LifecycleError("PILOT_RECONSTRUCTION_MISMATCH", "manual and compact reconstruction differ")
    context_bytes = canonical_bytes(script_context)
    manual_visible_bytes = sum(len(data) for data in fixture_bytes.values())
    script_visible_bytes = len(context_bytes)
    if script_visible_bytes >= manual_visible_bytes:
        raise LifecycleError("PILOT_NO_REDUCTION", "compact context did not reduce model-visible bytes")

    protected_trials = 1
    protected_rejections = 0
    try:
        enforce_clean_values({"value": "pass" + "word=fixture-private-value"})
    except LifecycleError as exc:
        if exc.code == "PROTECTED_VALUE_REJECTED":
            protected_rejections += 1
        else:
            raise

    manual_steps = [
        "read-current-quest-emberline",
        "read-latest-feather",
        "read-related-golden-wing",
        "resolve-stable-id-links",
        "assemble-eight-context-fields",
        "verify-reconstruction",
    ]
    script_steps = ["run-compact-context-command"]
    reduction = round((1 - script_visible_bytes / manual_visible_bytes) * 100, 2)
    return {
        "schema_id": "atlas.lifecycle.beu-reduction-pilot",
        "schema_version": "1.0.0",
        "authority": "NONCANONICAL_MEASUREMENT_EVIDENCE",
        "pilot_id": PILOT_ID,
        "operation": "CLEAN_CONTEXT_RECONSTRUCTION",
        "source_fingerprint": snapshot.source_fingerprint,
        "fixture_paths": list(PILOT_FIXTURES),
        "fixture_record_ids": [record["record_id"] for record in selected],
        "manual_baseline": {
            "model_visible_files": len(PILOT_FIXTURES),
            "model_visible_bytes": manual_visible_bytes,
            "process_steps": manual_steps,
            "retries": 0,
            "errors": 0,
            "machine_execution_median_ns": _median_ns(manual_operation, repetitions),
        },
        "script_assisted": {
            "model_visible_files": 1,
            "model_visible_bytes": script_visible_bytes,
            "process_steps": script_steps,
            "retries": 0,
            "errors": 0,
            "machine_execution_median_ns": _median_ns(script_operation, repetitions),
            "context_sha256": f"sha256:{hashlib.sha256(context_bytes).hexdigest()}",
            "protected_boundary_trials": protected_trials,
            "protected_boundary_rejections": protected_rejections,
        },
        "comparison": {
            "model_visible_file_reduction_percent": round(
                (1 - 1 / len(PILOT_FIXTURES)) * 100, 2
            ),
            "model_visible_byte_reduction_percent": reduction,
            "manual_steps": len(manual_steps),
            "script_steps": len(script_steps),
            "reconstruction_fields_total": len(script_context),
            "reconstruction_fields_exact": len(script_context),
            "reconstruction_accuracy_percent": 100.0,
            "usage_saving_supported": True,
        },
        "measurement_boundaries": {
            "beu": "NOT_MEASURED",
            "model_usage": "NOT_MEASURED",
            "elapsed_agent_work": "NOT_MEASURED",
            "real_workflow_human_interventions": "NOT_MEASURED",
            "pilot_human_interventions": 0,
            "manual_semantic_privacy_review": "NOT_MEASURED",
            "machine_execution_is_not_agent_elapsed_work": True,
            "hidden_model_calls": False,
        },
    }
