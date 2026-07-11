from __future__ import annotations

import hashlib
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .errors import LifecycleError
from .jsonio import canonical_bytes, load_bounded, stable_record_id
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
)


@dataclass(frozen=True)
class ValidationResult:
    records: int
    fixtures: int
    source_fingerprint: str
    stale_records: tuple[str, ...]


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


def validate_repository(
    repo_root: Path,
    *,
    check_stale: bool = False,
    expected_head: str | None = None,
) -> ValidationResult:
    root = repo_root.resolve()
    lifecycle = root / "lifecycle"
    validator = SchemaValidator(lifecycle / "schemas")
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
    loaded: list[tuple[dict[str, Any], bool]] = []
    fingerprint = hashlib.sha256()
    stale: list[str] = []
    canonical_count = 0
    fixture_count = 0
    current_head = expected_head or (observed_head(root) if check_stale else None)

    for path, fixture in sources:
        if path.suffix != ".json" or not path.is_file() or path.is_symlink():
            raise LifecycleError("UNSAFE_RECORD_MEMBER", "record trees may contain only regular JSON files")
        record = load_bounded(path)
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
            if path.name != f"{identifier}.json":
                raise LifecycleError("CANONICAL_FILENAME_MISMATCH", "canonical filename must equal the stable record ID")
            if path.read_bytes() != canonical_bytes(record):
                raise LifecycleError("NONCANONICAL_SERIALIZATION", "canonical record bytes are not deterministic")
            concurrency = record.get("concurrency")
            if check_stale and isinstance(concurrency, dict):
                if concurrency.get("expected_main_sha") != current_head:
                    stale.append(identifier)
        fingerprint.update(identifier.encode("ascii"))
        fingerprint.update(b"\0")
        fingerprint.update(hashlib.sha256(canonical_bytes(record)).digest())
        loaded.append((record, fixture))

    canonical = [record for record, fixture in loaded if not fixture]
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

    if check_stale and stale:
        raise LifecycleError("STALE_STATE", f"{len(stale)} lifecycle record(s) are stale")
    return ValidationResult(
        records=canonical_count,
        fixtures=fixture_count,
        source_fingerprint=f"sha256:{fingerprint.hexdigest()}",
        stale_records=tuple(stale),
    )
