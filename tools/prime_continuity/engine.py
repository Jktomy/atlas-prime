from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path, PurePosixPath
from typing import Any

from tools.athena_routes.schema import SchemaValidationError, validate_schema

ROOT = Path(__file__).resolve().parents[2]
FROZEN_BOARD_SCHEMA = ROOT / "schemas" / "quest-board-v1.schema.json"
QUEST_REGISTRY_SCHEMA = ROOT / "schemas" / "mission-board-quest-registry-v1.schema.json"
CONTINUITY_SCHEMA = ROOT / "schemas" / "prime-continuity-register-v1.schema.json"
IDENTITY_SCHEMA = ROOT / "schemas" / "quest-engine-identity-register-v1.schema.json"
ALLOWED_UPDATE_FIELDS = {
    "current_position", "blockers", "next_action", "next_approval",
    "campaign_id", "mission_id", "gate_id",
}
ADMISSION_STATES = {
    "READY_FOR_CAMPAIGN_1_PREVIEW", "READY_FOR_JAYSON_EXECUTION_PACKAGE",
    "IN_PROGRESS", "BLOCKED",
}
ALLOWED_CAMPAIGN_TRANSITIONS = {
    "PENDING->IN_PROGRESS", "IN_PROGRESS->BLOCKED",
    "BLOCKED->IN_PROGRESS", "IN_PROGRESS->COMPLETE",
}
REQUIRED_GATES = {
    "RP-C01": "ATHENA_NATIVE_EXECUTION_ROUTES_PROVEN",
    "RP-C02": "SHARED_AGENTIC_WARRANTS_ACCEPTED",
    "RP-C03": "CHROMELIGHT_EVIDENCE_RECONCILED",
    "RP-C04": "RESONANCE_EVIDENCE_RECONCILED",
    "RP-C05": "QUEST_ENGINE_AND_CONTINUITY_PROVEN",
    "RP-C06": "DETERMINISTIC_CONSERVATION_AND_GENERATED_PARITY_PROVEN",
    "RP-C07": "AJ_01_THROUGH_AJ_12_RECONCILED",
    "RP-C08": "REPAIRING_PRIME_COMPLETE",
}


class ContinuityError(ValueError):
    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def stable_json(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")


def sha256(value: Any) -> str:
    return hashlib.sha256(value if isinstance(value, bytes) else stable_json(value)).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _validate(schema: Path, value: dict[str, Any], code: str) -> None:
    try:
        validate_schema(_load(schema), value)
    except SchemaValidationError as exc:
        raise ContinuityError(code) from exc


def _source(source: str, root: Path) -> Path:
    path = PurePosixPath(source)
    candidate = root.joinpath(*path.parts)
    if path.is_absolute() or ".." in path.parts or not candidate.is_file():
        raise ContinuityError("QUEST_SOURCE_INVALID")
    return candidate


def validate_board(board: dict[str, Any], *, root: Path = ROOT) -> None:
    """Validate the frozen predecessor Board; it is evidence, not admission."""
    _validate(FROZEN_BOARD_SCHEMA, board, "QUEST_BOARD_SCHEMA_INVALID")
    ids = [item["quest_id"] for item in board["entries"]]
    sources = [item["source"] for item in board["entries"]]
    if len(ids) != len(set(ids)) or len(sources) != len(set(sources)):
        raise ContinuityError("QUEST_BOARD_DUPLICATE")
    for source in sources:
        _source(source, root)


def validate_quest_registry(
    registry: dict[str, Any], frozen_board: dict[str, Any], *, root: Path = ROOT
) -> None:
    validate_board(frozen_board, root=root)
    _validate(QUEST_REGISTRY_SCHEMA, registry, "QUEST_REGISTRY_SCHEMA_INVALID")
    entries = registry["entries"]
    for values in (
        [item["quest_id"] for item in entries],
        [item["source"] for item in entries],
        [item["parent_issue_number"] for item in entries],
        [item["parent_mission_id"] for item in entries],
        [item["parent_attempt_id"] for item in entries],
        [item["emberline_id"] for item in entries],
    ):
        if len(values) != len(set(values)):
            raise ContinuityError("QUEST_REGISTRY_DUPLICATE")
    for item in entries:
        _source(item["source"], root)

    cutover = registry["cutover"]
    if cutover["predecessor_sha256"] != sha256(frozen_board):
        raise ContinuityError("QUEST_PREDECESSOR_DIGEST_MISMATCH")
    if frozen_board["registry_role"] != "FROZEN_PREDECESSOR_EVIDENCE":
        raise ContinuityError("QUEST_PREDECESSOR_ROLE_MISMATCH")
    if frozen_board["successor_registry"] != "continuity/mission-board-quest-registry-r01.json":
        raise ContinuityError("QUEST_PREDECESSOR_SUCCESSOR_MISMATCH")

    baseline = set(cutover["baseline_active_quest_ids"])
    observed = {item["quest_id"] for item in entries}
    if not baseline.issubset(observed):
        raise ContinuityError("QUEST_REGISTRY_BASELINE_MISSING")
    if registry["registry_revision"] == 1 and baseline != observed:
        raise ContinuityError("QUEST_REGISTRY_CUTOVER_PARITY_MISMATCH")
    completed = sum(item["state"] == "COMPLETE" for item in frozen_board["entries"])
    if cutover["baseline_completed_quest_count"] != completed:
        raise ContinuityError("QUEST_REGISTRY_HISTORY_COUNT_MISMATCH")

    frozen = {item["quest_id"]: item for item in frozen_board["entries"]}
    current = {item["quest_id"]: item for item in entries}
    for identity in baseline:
        prior = frozen.get(identity)
        if prior is None or prior["state"] == "COMPLETE":
            raise ContinuityError("QUEST_REGISTRY_BASELINE_INVALID")
    if registry["registry_revision"] == 1:
        for identity in baseline:
            for field in ("quest_id", "source", "owner", "state", "next_gate", "readiness_basis"):
                if current[identity][field] != frozen[identity][field]:
                    raise ContinuityError("QUEST_REGISTRY_CUTOVER_PARITY_MISMATCH")


def validate_quest_admission(
    before: dict[str, Any],
    after: dict[str, Any],
    frozen_board: dict[str, Any] | None = None,
    *,
    root: Path = ROOT,
) -> dict[str, Any]:
    if before.get("registry_role") == "FROZEN_PREDECESSOR_EVIDENCE":
        raise ContinuityError("QUEST_BOARD_FROZEN")
    if frozen_board is None:
        raise ContinuityError("QUEST_PREDECESSOR_REQUIRED")
    validate_quest_registry(before, frozen_board, root=root)
    validate_quest_registry(after, frozen_board, root=root)
    old = {item["quest_id"]: item for item in before["entries"]}
    new = {item["quest_id"]: item for item in after["entries"]}
    added = set(new) - set(old)
    if len(added) != 1 or set(old) - set(new):
        raise ContinuityError("QUEST_ADMISSION_SCOPE_INVALID")
    if any(new[identity] != item for identity, item in old.items()):
        raise ContinuityError("QUEST_ADMISSION_EXISTING_ENTRY_CHANGED")
    admitted = new[next(iter(added))]
    if admitted["state"] not in ADMISSION_STATES:
        raise ContinuityError("QUEST_ADMISSION_STATE_INVALID")
    if after["registry_revision"] != before["registry_revision"] + 1:
        raise ContinuityError("QUEST_ADMISSION_REVISION_INVALID")
    if after["cutover"] != before["cutover"]:
        raise ContinuityError("QUEST_ADMISSION_CUTOVER_CHANGED")
    return copy.deepcopy(admitted)


def validate_identity_register(register: dict[str, Any]) -> None:
    _validate(IDENTITY_SCHEMA, register, "IDENTITY_REGISTER_SCHEMA_INVALID")
    campaigns = register["campaigns"]
    campaign_ids = [item["campaign_id"] for item in campaigns]
    gate_ids = [item["gate_id"] for item in campaigns]
    mission_ids = [mission["mission_id"] for item in campaigns for mission in item["missions"]]
    if any(len(values) != len(set(values)) for values in (campaign_ids, gate_ids, mission_ids)):
        raise ContinuityError("IDENTITY_DUPLICATE")
    if {item["campaign_id"]: item["gate_id"] for item in campaigns} != REQUIRED_GATES:
        raise ContinuityError("IDENTITY_GATE_SET_INVALID")
    if set(register["state_rules"]["allowed_campaign_transitions"]) != ALLOWED_CAMPAIGN_TRANSITIONS:
        raise ContinuityError("IDENTITY_TRANSITIONS_INVALID")
    for campaign in campaigns:
        if any(not mission["mission_id"].startswith(campaign["campaign_id"] + "-M") for mission in campaign["missions"]):
            raise ContinuityError("MISSION_CAMPAIGN_MISMATCH")
        if campaign["state"] == "COMPLETE" and any(mission["state"] != "PROVEN" for mission in campaign["missions"]):
            raise ContinuityError("CAMPAIGN_COMPLETION_UNPROVEN")


def validate_register(
    register: dict[str, Any],
    frozen_board: dict[str, Any],
    *,
    registry: dict[str, Any] | None = None,
    root: Path = ROOT,
) -> None:
    active = registry or _load(root / "continuity" / "mission-board-quest-registry-r01.json")
    validate_quest_registry(active, frozen_board, root=root)
    _validate(CONTINUITY_SCHEMA, register, "CONTINUITY_SCHEMA_INVALID")
    if register["quest_board_sha256"] != sha256(frozen_board):
        raise ContinuityError("QUEST_BOARD_DIGEST_MISMATCH")
    if register["quest_registry_source"] != "continuity/mission-board-quest-registry-r01.json":
        raise ContinuityError("QUEST_REGISTRY_SOURCE_MISMATCH")
    if register["quest_registry_sha256"] != sha256(active):
        raise ContinuityError("QUEST_REGISTRY_DIGEST_MISMATCH")
    if len(register["event_ids"]) != len(set(register["event_ids"])):
        raise ContinuityError("CONTINUITY_EVENT_REPLAY")

    entries = register["entries"]
    if not {item["last_event_id"] for item in entries}.issubset(set(register["event_ids"])):
        raise ContinuityError("CONTINUITY_EVENT_LEDGER_INCOMPLETE")
    if len({item["continuity_id"] for item in entries}) != len(entries) or len({item["quest_id"] for item in entries}) != len(entries):
        raise ContinuityError("CONTINUITY_DUPLICATE")
    registry_by_id = {item["quest_id"]: item for item in active["entries"]}
    if set(registry_by_id) != {item["quest_id"] for item in entries}:
        raise ContinuityError("CONTINUITY_REGISTRY_COVERAGE_MISMATCH")
    for item in entries:
        parent = registry_by_id[item["quest_id"]]
        if item["quest_source"] != parent["source"] or item["quest_state"] != parent["state"]:
            raise ContinuityError("CONTINUITY_REGISTRY_BINDING_MISMATCH")
        if hashlib.sha256(_source(item["quest_source"], root).read_bytes()).hexdigest() != item["quest_source_sha256"]:
            raise ContinuityError("CONTINUITY_SOURCE_DIGEST_MISMATCH")


def plan_one_entry_update(
    register: dict[str, Any],
    frozen_board: dict[str, Any],
    identities: dict[str, Any],
    *,
    continuity_id: str,
    expected_register_sha256: str,
    expected_entry_revision: int,
    event_id: str,
    changes: dict[str, Any],
    root: Path = ROOT,
) -> dict[str, Any]:
    validate_identity_register(identities)
    validate_register(register, frozen_board, root=root)
    if sha256(register) != expected_register_sha256:
        raise ContinuityError("REGISTER_STALE")
    if not changes or not set(changes).issubset(ALLOWED_UPDATE_FIELDS):
        raise ContinuityError("UPDATE_SCOPE_INVALID")
    if event_id in register["event_ids"]:
        raise ContinuityError("EVENT_REPLAY")
    candidate = copy.deepcopy(register)
    matches = [item for item in candidate["entries"] if item["continuity_id"] == continuity_id]
    if len(matches) != 1 or matches[0]["revision"] != expected_entry_revision:
        raise ContinuityError("ENTRY_STALE_OR_MISSING")
    matches[0].update(copy.deepcopy(changes))
    matches[0]["revision"] += 1
    matches[0]["last_event_id"] = event_id
    candidate["register_revision"] += 1
    candidate["event_ids"].append(event_id)
    changed = [after["continuity_id"] for before, after in zip(register["entries"], candidate["entries"]) if before != after]
    if changed != [continuity_id]:
        raise ContinuityError("UPDATE_NOT_SINGLE_ENTRY")
    validate_register(candidate, frozen_board, root=root)
    entry = matches[0]
    if entry["quest_id"] == identities["quest_id"]:
        if entry["campaign_id"] is None:
            raise ContinuityError("UPDATE_IDENTITY_BINDING_INVALID")
        campaigns = {item["campaign_id"]: item for item in identities["campaigns"]}
        campaign = campaigns.get(entry["campaign_id"])
        if campaign is None or entry["gate_id"] != campaign["gate_id"]:
            raise ContinuityError("UPDATE_IDENTITY_BINDING_INVALID")
        if entry["mission_id"] is not None and entry["mission_id"] not in {item["mission_id"] for item in campaign["missions"]}:
            raise ContinuityError("UPDATE_IDENTITY_BINDING_INVALID")
    return candidate


def render_emberline(register: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "atlas.prime-emberline.v1",
        "authority": "NONAUTHORITATIVE_PROJECTION",
        "source_register_id": register["register_id"],
        "source_register_revision": register["register_revision"],
        "source_register_sha256": sha256(register),
        "entries": [
            {key: item[key] for key in (
                "continuity_id", "quest_id", "campaign_id", "mission_id", "gate_id",
                "current_position", "blockers", "next_action", "next_approval", "revision",
            )}
            for item in sorted(register["entries"], key=lambda value: value["continuity_id"])
        ],
    }


def render_mission_quest_emberline(
    register: dict[str, Any], registry: dict[str, Any], quest_id: str
) -> dict[str, Any]:
    emberline_ids = [item.get("emberline_id") for item in registry.get("entries", [])]
    if len(emberline_ids) != len(set(emberline_ids)):
        raise ContinuityError("QUEST_REGISTRY_DUPLICATE")
    if register.get("quest_registry_sha256") != sha256(registry):
        raise ContinuityError("QUEST_REGISTRY_DIGEST_MISMATCH")
    parents = [item for item in registry["entries"] if item["quest_id"] == quest_id]
    entries = [item for item in register["entries"] if item["quest_id"] == quest_id]
    if len(parents) != 1 or len(entries) != 1:
        raise ContinuityError("MISSION_QUEST_EMBERLINE_BINDING_INVALID")
    parent = parents[0]
    entry = entries[0]
    if entry["quest_source"] != parent["source"] or entry["quest_state"] != parent["state"]:
        raise ContinuityError("CONTINUITY_REGISTRY_BINDING_MISMATCH")
    if parent["parent_issue_label"] != "mission/quest":
        raise ContinuityError("MISSION_QUEST_LABEL_INVALID")
    journey: list[dict[str, Any]] = [
        {
            "entry_id": "Main-Emberline-001",
            "entry_type": "MAIN",
            "scope": "EMBERLINE",
            "summary": f"Admitted Quest parent #{parent['parent_issue_number']} with stable Emberline {parent['emberline_id']}.",
        }
    ]
    sequence = 2
    for scope, value in (
        ("CAMPAIGN", entry["campaign_id"]),
        ("MISSION", entry["mission_id"]),
        ("GATE", entry["gate_id"]),
    ):
        if value is None:
            continue
        journey.append(
            {
                "entry_id": f"Main-{scope.title()}-{sequence:03d}",
                "entry_type": "MAIN",
                "scope": scope,
                "summary": value,
            }
        )
        sequence += 1
    lines = [
        f"## Living Emberline — {quest_id}",
        "",
        f"- **Emberline:** `{parent['emberline_id']}`",
        f"- **Revision:** `{entry['revision']}`",
        f"- **Mission Quest:** `#{parent['parent_issue_number']}`",
        f"- **Required label:** `{parent['parent_issue_label']}`",
        f"- **Quest state:** `{entry['quest_state']}`",
        f"- **Current Campaign:** `{entry['campaign_id'] or 'NONE'}`",
        f"- **Current Mission:** `{entry['mission_id'] or 'NONE'}`",
        f"- **Current Gate:** `{entry['gate_id'] or 'NONE'}`",
        "",
        "### Current position",
        entry["current_position"],
        "",
        "### Emberline path",
    ]
    lines.extend(f"- `{item['entry_id']}` — {item['summary']}" for item in journey)
    lines.extend(["", "### Blockers"])
    lines.extend(f"- {blocker}" for blocker in entry["blockers"] or ["None."])
    lines.extend([
        "",
        "### Next safe action",
        entry["next_action"],
        "",
        "### Next approval",
        entry["next_approval"],
        "",
        "> Human-readable operational presentation only. Merged registry and continuity remain authoritative.",
    ])
    return {
        "schema_version": "atlas.mission-quest-emberline.v1",
        "authority": "NONAUTHORITATIVE_HUMAN_PRESENTATION",
        "emberline_id": parent["emberline_id"],
        "emberline_revision": entry["revision"],
        "quest_id": quest_id,
        "parent_issue_number": parent["parent_issue_number"],
        "required_label": parent["parent_issue_label"],
        "registry_revision": registry["registry_revision"],
        "registry_sha256": sha256(registry),
        "continuity_register_revision": register["register_revision"],
        "continuity_register_sha256": sha256(register),
        "journey_entries": journey,
        "current_position": entry["current_position"],
        "blockers": copy.deepcopy(entry["blockers"]),
        "next_action": entry["next_action"],
        "next_approval": entry["next_approval"],
        "markdown": "\n".join(lines) + "\n",
    }


def sunset(register: dict[str, Any], continuity_id: str) -> dict[str, Any]:
    matches = [item for item in register["entries"] if item["continuity_id"] == continuity_id]
    if len(matches) != 1:
        raise ContinuityError("CONTINUITY_ENTRY_NOT_FOUND")
    body = {"schema_version": "atlas.prime-sunset.v1", "register_sha256": sha256(register), "entry": copy.deepcopy(matches[0])}
    return {**body, "sunset_sha256": sha256(body)}


def sunrise(snapshot: dict[str, Any], register: dict[str, Any]) -> dict[str, Any]:
    body = {key: snapshot[key] for key in ("schema_version", "register_sha256", "entry")}
    if snapshot.get("sunset_sha256") != sha256(body):
        raise ContinuityError("SUNSET_DIGEST_MISMATCH")
    if snapshot["register_sha256"] != sha256(register):
        raise ContinuityError("SUNSET_REGISTER_MISMATCH")
    entry = copy.deepcopy(snapshot["entry"])
    canonical = [item for item in register["entries"] if item["continuity_id"] == entry.get("continuity_id")]
    if len(canonical) != 1 or canonical[0] != entry:
        raise ContinuityError("SUNSET_ENTRY_MISMATCH")
    return {
        "schema_version": "atlas.prime-sunrise.v1",
        "sunset_sha256": snapshot["sunset_sha256"],
        "current_position": entry["current_position"],
        "blockers": entry["blockers"],
        "next_gate": entry["gate_id"],
        "next_action": entry["next_action"],
        "next_approval": entry["next_approval"],
        "source": entry["quest_source"],
    }


def argus(register: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "continuity_id": item["continuity_id"],
            "quest_id": item["quest_id"],
            "gate_id": item["gate_id"],
            "blocker_count": len(item["blockers"]),
            "next_action": item["next_action"],
        }
        for item in sorted(register["entries"], key=lambda value: (-len(value["blockers"]), value["continuity_id"]))
    ]
