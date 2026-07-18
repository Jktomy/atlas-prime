from __future__ import annotations

import hashlib
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .errors import LifecycleError
from .event_paths import bind_event_storage_path
from .jsonio import canonical_bytes, loads_bounded, read_bounded, stable_record_id
from .limits import MAX_RECORDS
from .protection import enforce_clean_values, enforce_pointer_contract
from .schema import SchemaValidator


CANONICAL_DIRS = (
    "feathers",
    "feather-archives",
    "golden-wings",
    "quest-emberlines",
    "quest-checkpoints",
    "sunsets",
    "sunrises",
    "continuity",
    "receipts",
    "events",
)


@dataclass(frozen=True)
class ValidationResult:
    records: int
    fixtures: int
    trust_roots: int
    source_fingerprint: str
    stale_records: tuple[str, ...]
    canonical_records: tuple[dict[str, Any], ...]
    fixture_records: tuple[dict[str, Any], ...]


def observed_head(repo_root: Path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
        timeout=10,
    )
    value = result.stdout.strip()
    if result.returncode != 0 or len(value) != 40:
        raise LifecycleError("GIT_STATE_UNAVAILABLE", "exact repository HEAD is unavailable")
    return value


def _validate_sunset_feather_bindings(
    records: list[dict[str, Any]],
    *,
    record_class: str,
) -> None:
    """Enforce the universal one-Sunset-to-one-Feather invariant."""

    records_by_id = {record["record_id"]: record for record in records}
    claimed_feathers: dict[str, str] = {}

    for sunset in (record for record in records if record.get("schema_id") == "atlas.lifecycle.sunset"):
        feather_id = sunset.get("latest_feather_id")
        if not isinstance(feather_id, str):
            raise LifecycleError(
                "SUNSET_FEATHER_REQUIRED",
                f"{record_class} Sunset must reference exactly one Feather",
            )
        feather = records_by_id.get(feather_id)
        if feather is None or feather.get("schema_id") != "atlas.lifecycle.feather":
            raise LifecycleError(
                "SUNSET_FEATHER_MISSING",
                f"{record_class} Sunset Feather reference does not resolve",
            )
        prior_sunset = claimed_feathers.get(feather_id)
        if prior_sunset is not None:
            raise LifecycleError(
                "SUNSET_FEATHER_REUSED",
                f"{record_class} Feather is claimed by more than one Sunset",
            )
        claimed_feathers[feather_id] = sunset["record_id"]

        for field in ("project_id", "operation_id", "quest_scope"):
            if sunset.get(field) != feather.get(field):
                raise LifecycleError(
                    "SUNSET_FEATHER_SCOPE_MISMATCH",
                    f"{record_class} Sunset and Feather disagree on {field}",
                )
        sunset_concurrency = sunset.get("concurrency")
        feather_concurrency = feather.get("concurrency")
        if not isinstance(sunset_concurrency, dict) or not isinstance(feather_concurrency, dict):
            raise LifecycleError(
                "SUNSET_FEATHER_CONCURRENCY_MISMATCH",
                f"{record_class} Sunset and Feather require concurrency bindings",
            )
        for field in (
            "expected_main_sha",
            "expected_quest_revision",
            "declared_source_fingerprint",
        ):
            if sunset_concurrency.get(field) != feather_concurrency.get(field):
                raise LifecycleError(
                    "SUNSET_FEATHER_CONCURRENCY_MISMATCH",
                    f"{record_class} Sunset and Feather disagree on {field}",
                )

    for sunrise in (record for record in records if record.get("schema_id") == "atlas.lifecycle.sunrise"):
        sunset = records_by_id.get(sunrise.get("sunset_id"))
        if sunset is None or sunset.get("schema_id") != "atlas.lifecycle.sunset":
            raise LifecycleError(
                "SUNRISE_SUNSET_MISSING",
                f"{record_class} Sunrise does not resolve an exact Sunset",
            )
        feather_id = sunset.get("latest_feather_id")
        if sunrise.get("latest_feather_id") != feather_id:
            raise LifecycleError(
                "SUNRISE_FEATHER_MISMATCH",
                f"{record_class} Sunrise does not resolve the Sunset-bound Feather",
            )
        feather = records_by_id.get(feather_id)
        if feather is None or feather.get("schema_id") != "atlas.lifecycle.feather":
            raise LifecycleError(
                "SUNRISE_FEATHER_MISSING",
                f"{record_class} Sunrise Feather reference does not resolve",
            )


LESSON_DISPOSITIONS = (
    "LOCAL_ONLY",
    "REINFORCES_EXISTING",
    "NEW_CANDIDATE",
    "SYSTEMIC_EXCEPTION_CANDIDATE",
    "REJECTED",
    "ABSORPTION_REQUIRED",
)


def _validate_lesson_harvest_bindings(
    records: list[dict[str, Any]],
    *,
    record_class: str,
) -> None:
    """Bind every v2 Sunset summary to its exact v2 Feather harvest."""

    records_by_id = {record.get("record_id"): record for record in records}
    golden_wings = {
        record.get("record_id")
        for record in records
        if record.get("schema_id") == "atlas.lifecycle.golden-wing"
    }
    for sunset in (
        record
        for record in records
        if record.get("schema_id") == "atlas.lifecycle.sunset"
        and record.get("schema_version") == "2.0.0"
    ):
        feather = records_by_id.get(sunset.get("latest_feather_id"))
        if feather is None or feather.get("schema_version") != "2.0.0":
            raise LifecycleError(
                "LESSON_HARVEST_FEATHER_VERSION",
                f"{record_class} v2 Sunset must bind one v2 Feather",
            )
        harvest = feather.get("lesson_harvest", {})
        observations = harvest.get("observations", [])
        keys = [item.get("key") for item in observations if isinstance(item, dict)]
        if len(keys) != len(observations) or len(keys) != len(set(keys)):
            raise LifecycleError(
                "LESSON_HARVEST_DUPLICATE_KEY",
                f"{record_class} lesson observation keys must be unique",
            )
        for observation in observations:
            if (
                observation.get("disposition") == "REINFORCES_EXISTING"
                and observation.get("golden_wing_id") not in golden_wings
            ):
                raise LifecycleError(
                    "LESSON_HARVEST_GOLDEN_WING",
                    f"{record_class} reinforcement Golden Wing does not resolve",
                )
        expected = {
            "observation_keys": keys,
            "disposition_counts": {
                disposition: sum(
                    item.get("disposition") == disposition for item in observations
                )
                for disposition in LESSON_DISPOSITIONS
            },
            "no_lesson_reason": harvest.get("no_lesson_reason"),
        }
        if sunset.get("lesson_harvest_summary") != expected:
            raise LifecycleError(
                "LESSON_HARVEST_SUMMARY_MISMATCH",
                f"{record_class} Sunset summary does not match its Feather harvest",
            )



def _validate_living_emberline(record: dict[str, Any]) -> None:
    if record.get("schema_id") != "atlas.lifecycle.quest-emberline" or record.get("schema_version") != "2.0.0":
        return
    if record.get("record_id") != record.get("lineage_root_id"):
        raise LifecycleError("LIVING_EMBERLINE_ID", "living Emberline record ID must equal its lineage root")
    revision = record.get("quest_revision")
    parent_digest = record.get("revision_parent_digest")
    if revision == 1 and parent_digest is not None:
        raise LifecycleError("LIVING_EMBERLINE_PARENT", "first living Emberline revision cannot bind a parent digest")
    if revision > 1 and not isinstance(parent_digest, str):
        raise LifecycleError("LIVING_EMBERLINE_PARENT", "later living Emberline revisions require a parent digest")
    entries = record.get("journey_entries")
    if not isinstance(entries, list) or not entries:
        raise LifecycleError("LIVING_EMBERLINE_ENTRIES", "living Emberline requires journey entries")
    ids = [entry.get("entry_id") for entry in entries if isinstance(entry, dict)]
    if len(ids) != len(entries) or len(ids) != len(set(ids)):
        raise LifecycleError("LIVING_EMBERLINE_ENTRIES", "journey entry IDs must be unique")
    by_id = {entry["entry_id"]: entry for entry in entries}
    type_label = {"MAIN": "Main", "SIDE": "Side", "BRANCHED": "Branched", "FINAL": "Final"}
    scope_label = {"EMBERLINE": "Emberline", "CAMPAIGN": "Campaign", "MISSION": "Mission", "GATE": "Gate"}
    for expected_sequence, entry in enumerate(entries, start=1):
        if entry.get("sequence") != expected_sequence:
            raise LifecycleError("LIVING_EMBERLINE_SEQUENCE", "journey entries must use contiguous sequence numbers")
        expected_id = f"{type_label[entry['entry_type']]}-{scope_label[entry['scope']]}-{expected_sequence:03d}"
        if entry["entry_id"] != expected_id:
            raise LifecycleError("LIVING_EMBERLINE_ENTRY_ID", "journey entry ID disagrees with type, scope, or sequence")
        branched_from = entry.get("branched_from")
        returns_to = entry.get("returns_to")
        if branched_from is not None and (branched_from not in by_id or by_id[branched_from]["sequence"] >= expected_sequence):
            raise LifecycleError("LIVING_EMBERLINE_BRANCH", "journey branch source must resolve to an earlier entry")
        if returns_to is not None and (returns_to not in by_id or by_id[returns_to]["sequence"] <= expected_sequence):
            raise LifecycleError("LIVING_EMBERLINE_RETURN", "Side journey return must resolve to a later entry")
        entry_type = entry["entry_type"]
        if entry_type == "MAIN":
            if any(entry.get(field) is not None for field in ("reason", "branched_from", "returns_to", "superseded_direction", "active_direction", "outcome")):
                raise LifecycleError("LIVING_EMBERLINE_MAIN", "Main journey entries cannot declare branch-only fields")
        elif entry_type == "SIDE":
            if not all(isinstance(entry.get(field), str) for field in ("reason", "branched_from", "returns_to", "outcome")) or any(entry.get(field) is not None for field in ("superseded_direction", "active_direction")):
                raise LifecycleError("LIVING_EMBERLINE_SIDE", "Side entry must bind departure, reason, outcome, and return")
        elif entry_type == "BRANCHED":
            if not all(isinstance(entry.get(field), str) for field in ("reason", "branched_from", "superseded_direction", "active_direction")) or entry.get("returns_to") is not None or entry.get("outcome") is not None:
                raise LifecycleError("LIVING_EMBERLINE_BRANCHED", "Branched entry must bind the superseded and active direction")
        elif entry_type == "FINAL":
            if not isinstance(entry.get("outcome"), str) or any(entry.get(field) is not None for field in ("reason", "branched_from", "returns_to", "superseded_direction", "active_direction")):
                raise LifecycleError("LIVING_EMBERLINE_FINAL", "Final entry must record only its accepted outcome")
    if record.get("current_entry_id") != entries[-1]["entry_id"]:
        raise LifecycleError("LIVING_EMBERLINE_CURRENT_ENTRY", "current journey entry must be the final ordered entry")
    complete = record.get("quest_state") == "COMPLETE"
    if complete:
        if entries[-1]["entry_type"] != "FINAL" or record.get("next_gate") != "CLOSED" or record.get("unresolved_blockers"):
            raise LifecycleError("LIVING_EMBERLINE_COMPLETION", "completed Quest requires Final entry, CLOSED gate, and no blockers")
    elif entries[-1]["entry_type"] == "FINAL" or record.get("next_gate") == "CLOSED":
        raise LifecycleError("LIVING_EMBERLINE_COMPLETION", "in-progress Quest cannot claim a Final entry or CLOSED gate")

def validate_repository(
    repo_root: Path,
    *,
    check_stale: bool = False,
    expected_head: str | None = None,
) -> ValidationResult:
    root = repo_root.resolve()
    lifecycle = root / "lifecycle"
    validator = SchemaValidator(lifecycle / "schemas")
    fingerprint = hashlib.sha256()

    def add_source(path: Path, data: bytes) -> None:
        try:
            relative = path.resolve().relative_to(root).as_posix()
        except ValueError as exc:
            raise LifecycleError("SOURCE_PATH_ESCAPE", "lifecycle source path leaves the repository") from exc
        fingerprint.update(relative.encode("utf-8"))
        fingerprint.update(b"\0")
        fingerprint.update(hashlib.sha256(data).digest())

    for contract_name in (
        "lifecycle-contract.md",
        "lifecycle-event-contract.md",
        "lifecycle-construction-contract.md",
    ):
        contract_path = lifecycle / contract_name
        contract_data = read_bounded(contract_path)
        try:
            contract_data.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise LifecycleError("INVALID_UTF8", "lifecycle contract is not valid UTF-8") from exc
        add_source(contract_path, contract_data)
    for schema_path in sorted((lifecycle / "schemas").glob("*.json")):
        schema_data = read_bounded(schema_path)
        loads_bounded(schema_data, label=schema_path.name)
        add_source(schema_path, schema_data)

    trust_root_count = 0
    trust_dir = lifecycle / "trust-roots"
    if not trust_dir.is_dir() or trust_dir.is_symlink():
        raise LifecycleError("TRUST_ROOT_LOCATION", "repository-controlled trust-root directory is invalid")
    trust_keys = {
        "schema_id",
        "expected_subject_digest",
        "trusted_contract_digest",
        "trusted_schema_digest",
    }
    digest_pattern = re.compile(r"sha256:[a-f0-9]{64}")
    for trust_path in sorted(trust_dir.iterdir()):
        if not trust_path.is_file() or trust_path.is_symlink():
            raise LifecycleError("TRUST_ROOT_MEMBER", "trust-root directory contains an unsafe member")
        trust_data = read_bounded(trust_path)
        if trust_path.name == "README.md":
            try:
                trust_data.decode("utf-8")
            except UnicodeDecodeError as exc:
                raise LifecycleError("INVALID_UTF8", "trust-root doctrine is not valid UTF-8") from exc
        else:
            if (
                trust_path.suffix != ".json"
                or re.fullmatch(r"[a-z0-9][a-z0-9._-]{0,127}[.]json", trust_path.name) is None
            ):
                raise LifecycleError("TRUST_ROOT_MEMBER", "trust-root filename is invalid")
            trust = loads_bounded(trust_data, label=trust_path.name)
            if trust.get("schema_id") == "atlas.lifecycle.trust-root.v1":
                if set(trust) != trust_keys:
                    raise LifecycleError("TRUST_ROOT_CONTRACT", "trusted expectation has an invalid contract")
                if any(
                    digest_pattern.fullmatch(trust[field]) is None
                    for field in trust_keys - {"schema_id"}
                ):
                    raise LifecycleError("TRUST_ROOT_DIGEST", "trusted expectation contains an invalid digest")
            elif trust.get("schema_id") == "atlas.lifecycle.event-trust-root":
                validator.validate_event_trust_root(trust)
            else:
                raise LifecycleError("TRUST_ROOT_CONTRACT", "trusted expectation has an invalid contract")
            trust_root_count += 1
        add_source(trust_path, trust_data)
    sources: list[tuple[Path, bool]] = []
    for name in CANONICAL_DIRS:
        directory = lifecycle / name
        if directory.exists():
            if not directory.is_dir() or directory.is_symlink():
                raise LifecycleError("UNSAFE_RECORD_DIRECTORY", "record directory is not a regular directory")
            sources.extend((path, False) for path in sorted(directory.iterdir()))
    fixture_dir = lifecycle / "fixtures"
    sources.extend((path, True) for path in sorted(fixture_dir.iterdir()))
    if len(sources) > MAX_RECORDS:
        raise LifecycleError("RECORD_COUNT_LIMIT", "record count exceeds the trusted limit")

    seen_ids: set[str] = set()
    seen_payloads: set[str] = set()
    seen_replays: set[str] = set()
    seen_event_paths: set[str] = set()
    loaded: list[tuple[dict[str, Any], bool]] = []
    stale: list[str] = []
    canonical_count = 0
    fixture_count = 0
    if check_stale and expected_head is None:
        observed_head(root)

    for path, fixture in sources:
        if path.suffix != ".json" or not path.is_file() or path.is_symlink():
            raise LifecycleError("UNSAFE_RECORD_MEMBER", "record trees may contain only regular JSON files")
        record_data = read_bounded(path)
        record = loads_bounded(record_data, label=path.name)
        validator.validate_record(record)
        enforce_clean_values(record)
        enforce_pointer_contract(record)
        identifier = record.get("record_id", "")
        if stable_record_id(record) != identifier:
            raise LifecycleError("STABLE_ID_MISMATCH", "record ID does not match its canonical payload")
        _validate_living_emberline(record)
        folded = identifier.casefold()
        if folded in seen_ids:
            raise LifecycleError("DUPLICATE_RECORD_ID", "duplicate or case-fold-colliding record ID")
        seen_ids.add(folded)
        payload_digest = hashlib.sha256(canonical_bytes(record, omit_record_id=True)).hexdigest()
        if payload_digest in seen_payloads:
            raise LifecycleError("REPLAYED_RECORD_PAYLOAD", "duplicate or replayed record payload")
        seen_payloads.add(payload_digest)
        replay_key = record.get("replay_key")
        if isinstance(replay_key, str):
            if replay_key in seen_replays:
                raise LifecycleError("REPLAY_IDENTIFIER", "receipt replay identifier was already used")
            seen_replays.add(replay_key)

        expected_authority = "NONCANONICAL_FIXTURE" if fixture else "CANONICAL_RECORD"
        if record.get("authority") != expected_authority:
            raise LifecycleError("AUTHORITY_PATH_MISMATCH", "record authority does not match its storage path")
        if fixture:
            fixture_count += 1
        else:
            canonical_count += 1
            relative_path = path.resolve().relative_to(root).as_posix()
            if record.get("schema_id") == "atlas.lifecycle.event":
                bind_event_storage_path(record, relative_path, seen_event_paths)
            elif path.name != f"{identifier}.json":
                raise LifecycleError("CANONICAL_FILENAME_MISMATCH", "canonical filename must equal the stable record ID")
            if record_data != canonical_bytes(record):
                raise LifecycleError("NONCANONICAL_SERIALIZATION", "canonical record bytes are not deterministic")
            # expected_main_sha is immutable transaction-input evidence.
            # Stale transaction bases are rejected by candidate construction before output;
            # accepted historical records do not expire when canonical main advances.
        add_source(path, canonical_bytes(record))
        loaded.append((record, fixture))

    canonical = [record for record, fixture in loaded if not fixture]
    fixtures = [record for record, fixture in loaded if fixture]
    _validate_sunset_feather_bindings(canonical, record_class="canonical")
    _validate_sunset_feather_bindings(fixtures, record_class="fixture")
    _validate_lesson_harvest_bindings(canonical, record_class="canonical")
    _validate_lesson_harvest_bindings(fixtures, record_class="fixture")
    records_by_id = {record["record_id"]: record for record in canonical}
    emberlines: dict[str, dict[str, Any]] = {}
    for record in canonical:
        if record.get("schema_id") == "atlas.lifecycle.quest-emberline":
            quest_id = record["quest_id"]
            if quest_id in emberlines:
                raise LifecycleError("DUPLICATE_QUEST_STATE", "Quest has multiple current Emberlines")
            emberlines[quest_id] = record

    if check_stale:
        for record in canonical:
            concurrency = record.get("concurrency")
            if not isinstance(concurrency, dict):
                continue
            parent = concurrency.get("expected_parent_feather")
            if parent is not None and parent not in records_by_id:
                raise LifecycleError("STALE_PARENT", "expected parent Feather does not exist")
            quest_id = record.get("quest_id")
            scope = record.get("quest_scope")
            if quest_id is None and isinstance(scope, dict):
                quest_id = scope.get("quest_id")
            expected_revision = concurrency.get("expected_quest_revision")
            if quest_id is not None and record.get("schema_id") != "atlas.lifecycle.quest-emberline":
                emberline = emberlines.get(quest_id)
                current_revision = emberline.get("quest_revision") if emberline is not None else None
                if (
                    emberline is None
                    or not isinstance(expected_revision, int)
                    or not isinstance(current_revision, int)
                    or expected_revision > current_revision
                ):
                    raise LifecycleError(
                        "STALE_QUEST_REVISION",
                        "expected Quest revision exceeds the current living Emberline revision",
                    )

    return ValidationResult(
        records=canonical_count,
        fixtures=fixture_count,
        trust_roots=trust_root_count,
        source_fingerprint=f"sha256:{fingerprint.hexdigest()}",
        stale_records=tuple(stale),
        canonical_records=tuple(canonical),
        fixture_records=tuple(record for record, fixture in loaded if fixture),
    )
