from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any

from .errors import LifecycleError
from .jsonio import load_bounded, read_bounded, stable_record_id
from .protection import enforce_clean_values, enforce_pointer_contract
from .schema import SchemaValidator


STATE_KEYS = {
    "schema_id", "schema_version", "authority", "main_sha", "source_fingerprint",
    "entity", "quest", "gate", "blockers", "existing_event_ids", "replay_keys",
    "revision_claim_event_id",
}
ENTITY_KEYS = {
    "entity_type", "entity_id", "revision", "state", "exists",
    "declared_children_complete", "acceptance_criteria", "satisfied_criteria",
}
QUEST_KEYS = {
    "quest_id", "revision", "state", "current_campaign_id", "current_mission_id",
    "current_gate_id",
}
GATE_KEYS = {
    "gate_id", "revision", "state", "latest_checkpoint_id", "declared_gate_ids",
}
BLOCKER_KEYS = {"blocker_id", "state"}
SHA = re.compile(r"^[a-f0-9]{40}$")
FINGERPRINT = re.compile(r"^sha256:[a-f0-9]{64}$")
EVENT_ID = re.compile(r"^LEV-[A-Z2-7]{26}$")


def _fail(code: str, message: str) -> None:
    raise LifecycleError(code, message)


def _closed(value: Any, keys: set[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != keys:
        _fail("STATE_SCHEMA", f"{label} has an invalid closed shape")
    return value


def _identity(value: Any, label: str, *, nullable: bool = False) -> str | None:
    if nullable and value is None:
        return None
    if not isinstance(value, str) or re.fullmatch(r"[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*", value) is None:
        _fail("STATE_SCHEMA", f"{label} has an invalid identity")
    return value


def _text_list(value: Any, label: str) -> list[str]:
    if (
        not isinstance(value, list)
        or len(value) > 64
        or len(value) != len(set(value))
        or any(not isinstance(item, str) or not item or len(item) > 4000 for item in value)
    ):
        _fail("STATE_SCHEMA", f"{label} has an invalid bounded list")
    return value


def validate_state_snapshot(state: dict[str, Any]) -> dict[str, Any]:
    _closed(state, STATE_KEYS, "state snapshot")
    if (
        state["schema_id"] != "atlas.lifecycle.current-state-snapshot"
        or state["schema_version"] != "1.0.0"
        or state["authority"] != "TRUSTED_READ_ONLY_STATE"
    ):
        _fail("STATE_SCHEMA", "state snapshot identity or authority is invalid")
    if not isinstance(state["main_sha"], str) or SHA.fullmatch(state["main_sha"]) is None:
        _fail("STATE_SCHEMA", "state main SHA is invalid")
    if not isinstance(state["source_fingerprint"], str) or FINGERPRINT.fullmatch(state["source_fingerprint"]) is None:
        _fail("STATE_SCHEMA", "state source fingerprint is invalid")

    entity = _closed(state["entity"], ENTITY_KEYS, "entity state")
    if entity["entity_type"] not in {
        "QUEST", "CAMPAIGN", "MISSION", "GATE", "LANDMARK", "BLOCKER",
        "FEATHER", "GOLDEN_WING", "ACCEPTANCE", "CAPABILITY", "SUNSET", "SUNRISE",
    }:
        _fail("STATE_SCHEMA", "entity type is invalid")
    _identity(entity["entity_id"], "entity ID")
    if not isinstance(entity["revision"], int) or isinstance(entity["revision"], bool) or entity["revision"] < 0:
        _fail("STATE_SCHEMA", "entity revision is invalid")
    if not isinstance(entity["state"], str) or not entity["state"] or len(entity["state"]) > 4000:
        _fail("STATE_SCHEMA", "entity state is invalid")
    if not isinstance(entity["exists"], bool) or not isinstance(entity["declared_children_complete"], bool):
        _fail("STATE_SCHEMA", "entity booleans are invalid")
    _text_list(entity["acceptance_criteria"], "entity acceptance criteria")
    _text_list(entity["satisfied_criteria"], "entity satisfied criteria")

    quest = state["quest"]
    if quest is not None:
        quest = _closed(quest, QUEST_KEYS, "Quest state")
        for field in ("quest_id", "current_campaign_id", "current_mission_id", "current_gate_id"):
            _identity(quest[field], field)
        if not isinstance(quest["revision"], int) or isinstance(quest["revision"], bool) or quest["revision"] < 0:
            _fail("STATE_SCHEMA", "Quest revision is invalid")
        if not isinstance(quest["state"], str) or not quest["state"]:
            _fail("STATE_SCHEMA", "Quest state is invalid")

    gate = state["gate"]
    if gate is not None:
        gate = _closed(gate, GATE_KEYS, "Gate state")
        _identity(gate["gate_id"], "Gate ID")
        if not isinstance(gate["revision"], int) or isinstance(gate["revision"], bool) or gate["revision"] < 0:
            _fail("STATE_SCHEMA", "Gate revision is invalid")
        if not isinstance(gate["state"], str) or not gate["state"]:
            _fail("STATE_SCHEMA", "Gate state is invalid")
        latest = gate["latest_checkpoint_id"]
        if latest is not None and (not isinstance(latest, str) or EVENT_ID.fullmatch(latest) is None):
            _fail("STATE_SCHEMA", "latest checkpoint ID is invalid")
        declared = _text_list(gate["declared_gate_ids"], "declared Gate IDs")
        for value in declared:
            _identity(value, "declared Gate ID")

    if not isinstance(state["blockers"], list) or len(state["blockers"]) > 64:
        _fail("STATE_SCHEMA", "blocker state is invalid")
    blocker_ids: set[str] = set()
    for blocker in state["blockers"]:
        _closed(blocker, BLOCKER_KEYS, "blocker")
        blocker_id = _identity(blocker["blocker_id"], "blocker ID")
        if blocker_id in blocker_ids or blocker["state"] not in {"OPEN", "RESOLVED"}:
            _fail("STATE_SCHEMA", "blocker state is invalid or duplicated")
        blocker_ids.add(blocker_id)

    for field, pattern in (("existing_event_ids", EVENT_ID), ("replay_keys", FINGERPRINT)):
        values = _text_list(state[field], field)
        if any(pattern.fullmatch(value) is None for value in values):
            _fail("STATE_SCHEMA", f"{field} contains an invalid value")
    claim = state["revision_claim_event_id"]
    if claim is not None and (not isinstance(claim, str) or EVENT_ID.fullmatch(claim) is None):
        _fail("STATE_SCHEMA", "revision claim event ID is invalid")
    enforce_clean_values(state)
    return state


def _digest(path: Path) -> str:
    return f"sha256:{hashlib.sha256(read_bounded(path)).hexdigest()}"


def _trusted_root_path(root: Path, candidate: Path) -> Path:
    directory = (root / "lifecycle/trust-roots").resolve()
    try:
        resolved = candidate.resolve()
        relative = resolved.relative_to(directory)
    except (OSError, ValueError) as exc:
        raise LifecycleError(
            "TRUST_ROOT_LOCATION",
            "event trust root must come from the repository-controlled trust store",
        ) from exc
    if len(relative.parts) != 1 or candidate.is_symlink():
        _fail("TRUST_ROOT_LOCATION", "event trust root location is not a regular trusted member")
    return resolved


def _bind(event: dict[str, Any], trust: dict[str, Any], state: dict[str, Any], root: Path) -> None:
    expected = event["expectations"]
    route = event["route"]
    evidence = event["evidence"]
    quest_revision = None if state["quest"] is None else state["quest"]["revision"]
    gate_revision = None if state["gate"] is None else state["gate"]["revision"]
    bindings = (
        (expected["expected_main_sha"], trust["expected_main_sha"], "TRUST_MAIN"),
        (expected["expected_main_sha"], state["main_sha"], "STALE_MAIN"),
        (expected["expected_entity_revision"], trust["expected_entity_revision"], "TRUST_ENTITY_REVISION"),
        (expected["expected_entity_revision"], state["entity"]["revision"], "STALE_ENTITY_REVISION"),
        (expected["expected_quest_revision"], trust["expected_quest_revision"], "TRUST_QUEST_REVISION"),
        (expected["expected_quest_revision"], quest_revision, "STALE_QUEST_REVISION"),
        (expected["expected_gate_revision"], gate_revision, "STALE_GATE_REVISION"),
        (expected["expected_source_fingerprint"], state["source_fingerprint"], "STALE_SOURCE_FINGERPRINT"),
        (event["target"]["entity_type"], state["entity"]["entity_type"], "TARGET_TYPE_MISMATCH"),
        (event["target"]["entity_id"], state["entity"]["entity_id"], "TARGET_ID_MISMATCH"),
        (expected["expected_prior_state"], state["entity"]["state"], "PRIOR_STATE_MISMATCH"),
        (evidence["exact_subject_sha"], trust["expected_evidence_sha"], "TRUST_EVIDENCE_SHA"),
        (route["route_authority"], trust["allowed_route_authority"], "TRUST_ROUTE"),
        (route["allowed_paths"], trust["allowed_paths"], "TRUST_ALLOWED_PATHS"),
    )
    for observed, required, code in bindings:
        if observed != required:
            _fail(code, "event, trust root, and current state do not agree")
    if not state["entity"]["exists"]:
        _fail("TARGET_NOT_FOUND", "target entity does not exist")
    if trust["accepted_event_schema_id"] != event["schema_id"]:
        _fail("TRUST_SCHEMA_ID", "event schema identity is not externally trusted")
    schema_path = root / "lifecycle/schemas/lifecycle-event-v1.schema.json"
    contract_path = root / "lifecycle/lifecycle-event-contract.md"
    if trust["accepted_event_schema_digest"] != _digest(schema_path):
        _fail("TRUST_SCHEMA_DIGEST", "event schema digest is not externally trusted")
    if (
        trust["acceptance_contract_ref"].get("uri") != "lifecycle/lifecycle-event-contract.md"
        or trust["acceptance_contract_digest"] != _digest(contract_path)
    ):
        _fail("TRUST_ACCEPTANCE_CONTRACT", "acceptance contract is not externally trusted")
    reference = expected["trusted_expectation_ref"]
    if reference.get("uri") != f"lifecycle/trust-roots/{trust['trust_root_id']}.json":
        _fail("TRUST_ROOT_REFERENCE", "event does not reference the selected external trust root")


def _common_guards(event: dict[str, Any], state: dict[str, Any]) -> None:
    if event["record_id"] in state["existing_event_ids"]:
        _fail("DUPLICATE_EVENT", "event ID already exists")
    if event["replay_key"] in state["replay_keys"]:
        _fail("REPLAYED_EVENT", "event replay identifier already exists")
    if state["revision_claim_event_id"] is not None:
        _fail("CONCURRENT_REVISION", "current revision is already claimed by another event")
    expected_parent = event["expectations"]["expected_parent_checkpoint_id"]
    current_parent = None if state["gate"] is None else state["gate"]["latest_checkpoint_id"]
    if expected_parent != current_parent:
        _fail("STALE_PARENT_CHECKPOINT", "expected parent checkpoint is not current")
    current_quest = None if state["quest"] is None else state["quest"]["quest_id"]
    current_gate = None if state["gate"] is None else state["gate"]["gate_id"]
    if event["position"]["quest_id"] != current_quest:
        _fail("QUEST_POSITION_MISMATCH", "event Quest does not match current state")
    if event["position"]["gate_id"] != current_gate:
        _fail("GATE_POSITION_MISMATCH", "event Gate does not match current state")


def _transition_guards(event: dict[str, Any], state: dict[str, Any]) -> None:
    transition = event["transition"]
    event_type = event["event_type"]
    required = set(transition["acceptance_criteria"])
    if not required.issubset(set(state["entity"]["satisfied_criteria"])):
        _fail("INCOMPLETE_ACCEPTANCE", "declared transition acceptance is not fully satisfied")
    authorized = transition["authorized_blocker_ids"]
    if event_type != "BLOCKER_RESOLVED" and authorized:
        _fail("UNAUTHORIZED_BLOCKER_RESOLUTION", "only a blocker-resolution event may clear blockers")
    if event_type == "BLOCKER_RESOLVED":
        if event["target"]["entity_id"] not in authorized or state["entity"]["state"] != "OPEN":
            _fail("UNAUTHORIZED_BLOCKER_RESOLUTION", "blocker resolution is not explicitly authorized")
    if event_type == "GATE_COMPLETED":
        if state["gate"] is None:
            _fail("TARGET_NOT_FOUND", "Gate state does not exist")
        if state["gate"]["state"] != "IN_PROGRESS":
            _fail("INVALID_STATE_MOVEMENT", "Gate completion requires an in-progress Gate")
        next_gate = transition["declared_next_gate"]
        if next_gate is not None and next_gate not in state["gate"]["declared_gate_ids"]:
            _fail("NEXT_GATE_NOT_FOUND", "declared next Gate does not exist")
        if any(blocker["state"] == "OPEN" for blocker in state["blockers"]):
            _fail("OPEN_BLOCKER", "Gate completion cannot silently clear an open blocker")
    if event_type in {"MISSION_COMPLETED", "CAMPAIGN_COMPLETED"} and not state["entity"]["declared_children_complete"]:
        _fail("INCOMPLETE_CHILDREN", "completion requires every declared child to be complete")
    if event_type == "COMPLETION_REVOKED":
        revoked = event["lineage"]["revokes_event_id"]
        if revoked is None or revoked not in state["existing_event_ids"]:
            _fail("REVOCATION_LINEAGE", "completion revocation must name an existing transition")


def _deltas(event: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
    blank = {
        name: None
        for name in (
            "emberline", "checkpoint", "blocker", "feather", "golden_wing",
            "acceptance", "capability", "target",
        )
    }
    if event["event_class"] == "CHECKPOINT":
        if state["quest"] is None or state["gate"] is None:
            _fail("TARGET_NOT_FOUND", "checkpoint Quest or Gate state does not exist")
        blank["emberline"] = {
            "current_campaign_id": state["quest"]["current_campaign_id"],
            "current_mission_id": state["quest"]["current_mission_id"],
            "current_gate_id": state["quest"]["current_gate_id"],
            "quest_state": state["quest"]["state"],
            "quest_revision": state["quest"]["revision"] + 1,
            "gate_state": state["gate"]["state"],
            "gate_revision": state["gate"]["revision"] + 1,
            "latest_checkpoint_id": event["record_id"],
        }
        blank["checkpoint"] = {
            "event_id": event["record_id"],
            "parent_checkpoint_id": state["gate"]["latest_checkpoint_id"],
            "restart_position": event["checkpoint"]["restart_position"],
        }
        return blank

    event_type = event["event_type"]
    requested = event["transition"]["requested_resulting_state"]
    blank["target"] = {
        "entity_id": event["target"]["entity_id"],
        "prior_state": state["entity"]["state"],
        "resulting_state": requested,
        "entity_revision": state["entity"]["revision"] + 1,
    }
    if event_type == "GATE_COMPLETED":
        blank["emberline"] = {
            "completed_gate_id": state["gate"]["gate_id"],
            "current_gate_id": event["transition"]["declared_next_gate"],
            "quest_revision": state["quest"]["revision"] + 1,
            "gate_revision": state["gate"]["revision"] + 1,
            "accepted_event_id": event["record_id"],
        }
    elif event_type == "COMPLETION_REVOKED":
        blank["emberline"] = {
            "reopened_gate_id": state["gate"]["gate_id"],
            "current_gate_id": event["transition"]["declared_next_gate"],
            "quest_revision": state["quest"]["revision"] + 1,
            "gate_revision": state["gate"]["revision"] + 1,
            "revoked_event_id": event["lineage"]["revokes_event_id"],
        }
    elif event_type in {"BLOCKER_RESOLVED", "BLOCKER_REOPENED"}:
        blank["blocker"] = blank["target"]
    elif event_type.startswith("FEATHER_"):
        blank["feather"] = blank["target"]
    elif event_type.startswith("GOLDEN_WING_"):
        blank["golden_wing"] = blank["target"]
    elif event_type.startswith("ACCEPTANCE_"):
        blank["acceptance"] = blank["target"]
    elif event_type.startswith("CAPABILITY_"):
        blank["capability"] = blank["target"]
    return blank


def plan_event(
    repo_root: Path,
    event_path: Path,
    trust_root_path: Path,
    expected_trust_root_digest: str,
    state_path: Path,
    expected_state_digest: str,
) -> dict[str, Any]:
    root = repo_root.resolve()
    validator = SchemaValidator(root / "lifecycle/schemas")
    event = load_bounded(event_path)
    trusted_path = _trusted_root_path(root, trust_root_path)
    if (
        not isinstance(expected_trust_root_digest, str)
        or FINGERPRINT.fullmatch(expected_trust_root_digest) is None
        or _digest(trusted_path) != expected_trust_root_digest
    ):
        _fail("TRUST_ROOT_DIGEST", "event trust root does not match the independent expected digest")
    trust = load_bounded(trusted_path)
    if (
        not isinstance(expected_state_digest, str)
        or FINGERPRINT.fullmatch(expected_state_digest) is None
        or _digest(state_path) != expected_state_digest
    ):
        _fail("STATE_DIGEST", "current-state snapshot does not match the independent expected digest")
    state = validate_state_snapshot(load_bounded(state_path))
    validator.validate_record(event)
    validator.validate_event_trust_root(trust)
    if trusted_path.name != f"{trust['trust_root_id']}.json":
        _fail("TRUST_ROOT_IDENTITY", "event trust-root filename does not match its trusted identity")
    enforce_clean_values(event)
    enforce_pointer_contract(event)
    if stable_record_id(event) != event["record_id"]:
        _fail("STABLE_ID_MISMATCH", "event ID does not match canonical payload")
    _bind(event, trust, state, root)
    _common_guards(event, state)
    if event["event_class"] == "CHECKPOINT":
        if state["gate"] is None or state["quest"] is None or state["gate"]["state"] != "IN_PROGRESS":
            _fail("INVALID_CHECKPOINT_STATE", "checkpoint requires an in-progress Gate")
    else:
        _transition_guards(event, state)
    return {
        "authority": "READ_ONLY_PLAN",
        "command": "event plan",
        "event_id": event["record_id"],
        "event_class": event["event_class"],
        "event_type": event["event_type"],
        "exact_main_sha": state["main_sha"],
        "exact_entity_revision": state["entity"]["revision"],
        "source_fingerprint": state["source_fingerprint"],
        "trusted_root_digest": expected_trust_root_digest,
        "state_snapshot_digest": expected_state_digest,
        "proposed_deltas": _deltas(event, state),
        "writes_performed": False,
        "candidate_bytes_created": False,
        "github_actions": [],
        "status": "PASS",
    }
