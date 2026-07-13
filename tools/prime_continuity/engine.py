from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path, PurePosixPath
from typing import Any

from tools.athena_routes.schema import SchemaValidationError, validate_schema


ROOT = Path(__file__).resolve().parents[2]
BOARD_SCHEMA = ROOT / "schemas" / "quest-board-v1.schema.json"
CONTINUITY_SCHEMA = ROOT / "schemas" / "prime-continuity-register-v1.schema.json"
IDENTITY_SCHEMA = ROOT / "schemas" / "quest-engine-identity-register-v1.schema.json"
ALLOWED_UPDATE_FIELDS = {"current_position", "blockers", "next_action", "next_approval", "campaign_id", "mission_id", "gate_id", "quest_state"}


class ContinuityError(ValueError):
    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def stable_json(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")


def sha256(value: Any) -> str:
    payload = value if isinstance(value, bytes) else stable_json(value)
    return hashlib.sha256(payload).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _validate(schema_path: Path, value: dict[str, Any], code: str) -> None:
    try:
        validate_schema(_load(schema_path), value)
    except SchemaValidationError as exc:
        raise ContinuityError(code) from exc


def validate_board(board: dict[str, Any], *, root: Path = ROOT) -> None:
    _validate(BOARD_SCHEMA, board, "QUEST_BOARD_SCHEMA_INVALID")
    ids = [entry["quest_id"] for entry in board["entries"]]
    sources = [entry["source"] for entry in board["entries"]]
    if len(ids) != len(set(ids)) or len(sources) != len(set(sources)):
        raise ContinuityError("QUEST_BOARD_DUPLICATE")
    for source in sources:
        path = PurePosixPath(source)
        if path.is_absolute() or ".." in path.parts or not root.joinpath(*path.parts).is_file():
            raise ContinuityError("QUEST_SOURCE_INVALID")


def validate_identity_register(register: dict[str, Any]) -> None:
    _validate(IDENTITY_SCHEMA, register, "IDENTITY_REGISTER_SCHEMA_INVALID")
    campaign_ids = [item["campaign_id"] for item in register["campaigns"]]
    gate_ids = [item["gate_id"] for item in register["campaigns"]]
    mission_ids = [mission["mission_id"] for item in register["campaigns"] for mission in item["missions"]]
    if len(campaign_ids) != len(set(campaign_ids)) or len(gate_ids) != len(set(gate_ids)) or len(mission_ids) != len(set(mission_ids)):
        raise ContinuityError("IDENTITY_DUPLICATE")


def validate_register(register: dict[str, Any], board: dict[str, Any], *, root: Path = ROOT) -> None:
    validate_board(board, root=root)
    _validate(CONTINUITY_SCHEMA, register, "CONTINUITY_SCHEMA_INVALID")
    if register["quest_board_sha256"] != sha256(board):
        raise ContinuityError("QUEST_BOARD_DIGEST_MISMATCH")
    board_by_id = {entry["quest_id"]: entry for entry in board["entries"] if entry["state"] != "COMPLETE"}
    entries = register["entries"]
    if len({entry["continuity_id"] for entry in entries}) != len(entries) or len({entry["quest_id"] for entry in entries}) != len(entries):
        raise ContinuityError("CONTINUITY_DUPLICATE")
    if set(board_by_id) != {entry["quest_id"] for entry in entries}:
        raise ContinuityError("CONTINUITY_BOARD_COVERAGE_MISMATCH")
    for entry in entries:
        board_entry = board_by_id[entry["quest_id"]]
        if entry["quest_source"] != board_entry["source"] or entry["quest_state"] != board_entry["state"]:
            raise ContinuityError("CONTINUITY_BOARD_BINDING_MISMATCH")
        source = root / entry["quest_source"]
        if hashlib.sha256(source.read_bytes()).hexdigest() != entry["quest_source_sha256"]:
            raise ContinuityError("CONTINUITY_SOURCE_DIGEST_MISMATCH")


def plan_one_entry_update(register: dict[str, Any], *, continuity_id: str, expected_register_sha256: str,
                          expected_entry_revision: int, event_id: str, changes: dict[str, Any]) -> dict[str, Any]:
    if sha256(register) != expected_register_sha256:
        raise ContinuityError("REGISTER_STALE")
    if not changes or not set(changes).issubset(ALLOWED_UPDATE_FIELDS):
        raise ContinuityError("UPDATE_SCOPE_INVALID")
    candidate = copy.deepcopy(register)
    matches = [entry for entry in candidate["entries"] if entry["continuity_id"] == continuity_id]
    if len(matches) != 1 or matches[0]["revision"] != expected_entry_revision:
        raise ContinuityError("ENTRY_STALE_OR_MISSING")
    matches[0].update(copy.deepcopy(changes))
    matches[0]["revision"] += 1
    matches[0]["last_event_id"] = event_id
    candidate["register_revision"] += 1
    changed = [entry["continuity_id"] for before, entry in zip(register["entries"], candidate["entries"]) if before != entry]
    if changed != [continuity_id]:
        raise ContinuityError("UPDATE_NOT_SINGLE_ENTRY")
    return candidate


def render_emberline(register: dict[str, Any]) -> dict[str, Any]:
    entries = sorted(register["entries"], key=lambda item: item["continuity_id"])
    return {
        "schema_version": "atlas.prime-emberline.v1", "authority": "NONAUTHORITATIVE_PROJECTION",
        "source_register_id": register["register_id"], "source_register_revision": register["register_revision"],
        "source_register_sha256": sha256(register), "entries": [{key: entry[key] for key in ("continuity_id", "quest_id", "campaign_id", "mission_id", "gate_id", "current_position", "blockers", "next_action", "next_approval", "revision")} for entry in entries],
    }


def sunset(register: dict[str, Any], continuity_id: str) -> dict[str, Any]:
    matches = [entry for entry in register["entries"] if entry["continuity_id"] == continuity_id]
    if len(matches) != 1:
        raise ContinuityError("CONTINUITY_ENTRY_NOT_FOUND")
    entry = copy.deepcopy(matches[0])
    body = {"schema_version": "atlas.prime-sunset.v1", "register_sha256": sha256(register), "entry": entry}
    return {**body, "sunset_sha256": sha256(body)}


def sunrise(snapshot: dict[str, Any]) -> dict[str, Any]:
    body = {key: snapshot[key] for key in ("schema_version", "register_sha256", "entry")}
    if snapshot.get("sunset_sha256") != sha256(body):
        raise ContinuityError("SUNSET_DIGEST_MISMATCH")
    entry = copy.deepcopy(snapshot["entry"])
    return {"schema_version": "atlas.prime-sunrise.v1", "sunset_sha256": snapshot["sunset_sha256"], "current_position": entry["current_position"], "blockers": entry["blockers"], "next_gate": entry["gate_id"], "next_action": entry["next_action"], "next_approval": entry["next_approval"], "source": entry["quest_source"]}


def argus(register: dict[str, Any]) -> list[dict[str, Any]]:
    return [{"continuity_id": entry["continuity_id"], "quest_id": entry["quest_id"], "gate_id": entry["gate_id"], "blocker_count": len(entry["blockers"]), "next_action": entry["next_action"]} for entry in sorted(register["entries"], key=lambda item: (-len(item["blockers"]), item["continuity_id"]))]
