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
                if emberline is None or emberline.get("quest_revision") != expected_revision:
                    raise LifecycleError("STALE_QUEST_REVISION", "expected Quest revision is not current")

    return ValidationResult(
        records=canonical_count,
        fixtures=fixture_count,
        trust_roots=trust_root_count,
        source_fingerprint=f"sha256:{fingerprint.hexdigest()}",
        stale_records=tuple(stale),
        canonical_records=tuple(canonical),
        fixture_records=tuple(record for record, fixture in loaded if fixture),
    )
