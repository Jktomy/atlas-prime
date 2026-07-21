from __future__ import annotations

import hashlib
import json
import re
from copy import deepcopy
from datetime import datetime
from pathlib import PurePosixPath
from typing import Any, Iterable, Mapping, Sequence


SCHEMA_VERSION = "atlas.mission.v1"
MISSION_TYPES = frozenset(
    {
        "mission/sunset",
        "mission/quest",
        "mission/campaign",
        "mission/gate",
        "mission/controlled-burn",
        "mission/phoenix-burn",
        "mission/repair",
        "mission/research",
        "mission/migration",
        "mission/generated-refresh",
    }
)
MISSION_STATES = (
    "CAPTURED",
    "TRIAGED",
    "READY",
    "IN_PROGRESS",
    "BLOCKED_RESUMABLE",
    "PR_OPEN",
    "VALIDATING",
    "READY_FOR_PERMANENCE",
    "CANONICAL",
    "COPPERMIND_ARCHIVED",
    "CLOSED",
)
MISSION_STATE_SET = frozenset(MISSION_STATES)
CANONICAL_SOURCE_STATES = frozenset(
    {"PHOENIX_PENDING", "NO_SOURCE_CHANGE_REQUIRED", "PR_OPEN", "MERGED_PENDING_READBACK", "CANONICAL"}
)
DEPENDENCY_RELATIONS = frozenset(
    {"BLOCKS", "BLOCKED_BY", "PARALLEL_WITH", "NONBLOCKING_RELATED", "PARENT_OF", "CHILD_OF"}
)
EFFORT_CLASSES = frozenset({"BEU_0", "BEU_1", "BEU_2", "BEU_3", "BEU_5", "BEU_8", "UNKNOWN"})
QUEUE_BEHAVIORS = frozenset({"TERMINAL_ON_BLOCK", "CONTINUE_IF_BLOCKED_RESUMABLE"})
ARCHIVE_STATES = frozenset({"PENDING", "PACKAGE_READY", "ARCHIVED", "NOT_APPLICABLE"})
SUNSET_TRUTH_STATES = frozenset(
    {"SUNSET_CAPTURED", "PHOENIX_PENDING", "PR_OPEN", "MERGED_PENDING_READBACK", "CANONICAL_READBACK_COMPLETE", "SUNSET COMPLETE"}
)
VALIDATION_STATES = frozenset({"NOT_STARTED", "PENDING", "PASS", "FAIL", "UNREADABLE"})
REVIEW_STATES = frozenset({"NOT_STARTED", "PENDING", "RESOLVED", "BLOCKING"})
STRIKEFORCE_STATES = frozenset({"NOT_RUN", "GREEN", "YELLOW", "RED"})
TOP_LEVEL_KEYS = frozenset(
    {
        "schema_version",
        "repository",
        "issue_number",
        "mission_id",
        "mission_type",
        "mission_state",
        "created_at",
        "updated_at",
        "objective",
        "rationale_and_decisions",
        "owner",
        "relationships",
        "assigned_worker",
        "execution_identity",
        "dependencies",
        "public_clean_boundary",
        "acceptance_criteria",
        "next_safe_action",
        "effort_class",
        "queue_behavior",
        "canonical_source_status",
        "source_binding",
        "validation_review",
        "coppermind",
        "completion_proof",
        "rollback",
        "attempt_id",
        "sunset",
    }
)
BASE_REQUIRED_KEYS = TOP_LEVEL_KEYS - {"sunset"}
SHA40 = re.compile(r"^[0-9a-f]{40}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
REPOSITORY = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
IDENTITY = re.compile(r"^[A-Z0-9][A-Z0-9-]{2,127}$")
MANIFEST_BLOCK = re.compile(r"```atlas-mission-v1\s*\n(.*?)\n```", re.DOTALL)
PROTECTED_PATTERNS = (
    ("private key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")),
    ("GitHub token", re.compile(r"\bgh(?:p|o|u|s|r)_[A-Za-z0-9]{20,}\b")),
    ("AWS access key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("assigned secret", re.compile(r"(?i)\b(?:api[_-]?key|access[_-]?token|password|secret)\s*[:=]\s*['\"][^'\"\r\n]{8,}['\"]")),
    ("IP address", re.compile(r"(?<![0-9])(?:25[0-5]|2[0-4][0-9]|1?[0-9]{1,2})(?:\.(?:25[0-5]|2[0-4][0-9]|1?[0-9]{1,2})){3}(?![0-9])")),
)
TRANSITIONS = {
    "CAPTURED": frozenset({"TRIAGED", "BLOCKED_RESUMABLE"}),
    "TRIAGED": frozenset({"READY", "BLOCKED_RESUMABLE"}),
    "READY": frozenset({"IN_PROGRESS", "BLOCKED_RESUMABLE"}),
    "IN_PROGRESS": frozenset({"BLOCKED_RESUMABLE", "PR_OPEN", "VALIDATING", "CANONICAL"}),
    "BLOCKED_RESUMABLE": frozenset({"TRIAGED", "READY", "IN_PROGRESS"}),
    "PR_OPEN": frozenset({"VALIDATING", "BLOCKED_RESUMABLE"}),
    "VALIDATING": frozenset({"PR_OPEN", "BLOCKED_RESUMABLE", "READY_FOR_PERMANENCE"}),
    "READY_FOR_PERMANENCE": frozenset({"VALIDATING", "BLOCKED_RESUMABLE", "CANONICAL"}),
    "CANONICAL": frozenset({"COPPERMIND_ARCHIVED", "CLOSED"}),
    "COPPERMIND_ARCHIVED": frozenset({"CLOSED"}),
    "CLOSED": frozenset(),
}
SOURCE_TRANSITIONS = {
    "PHOENIX_PENDING": frozenset({"NO_SOURCE_CHANGE_REQUIRED", "PR_OPEN"}),
    "NO_SOURCE_CHANGE_REQUIRED": frozenset(),
    "PR_OPEN": frozenset({"MERGED_PENDING_READBACK"}),
    "MERGED_PENDING_READBACK": frozenset({"CANONICAL"}),
    "CANONICAL": frozenset(),
}


class MissionError(ValueError):
    """Fail-closed Mission validation or reconciliation error."""


def _fail(code: str, detail: str) -> None:
    raise MissionError(f"{code}: {detail}")


def _require_exact_keys(value: Mapping[str, Any], required: set[str] | frozenset[str], allowed: set[str] | frozenset[str], label: str) -> None:
    missing = sorted(required - set(value))
    unknown = sorted(set(value) - allowed)
    if missing:
        _fail("MISSING_FIELDS", f"{label}: {missing}")
    if unknown:
        _fail("UNKNOWN_FIELDS", f"{label}: {unknown}")


def _require_nonempty_text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        _fail("INVALID_FIELD", f"{label} must be nonempty text")
    return value


def _require_text_list(value: Any, label: str, *, nonempty: bool = False) -> list[str]:
    if not isinstance(value, list) or (nonempty and not value):
        _fail("INVALID_FIELD", f"{label} must be {'a nonempty ' if nonempty else 'a '}list")
    for index, item in enumerate(value):
        _require_nonempty_text(item, f"{label}[{index}]")
    return value


def _require_timestamp(value: Any, label: str) -> datetime:
    text = _require_nonempty_text(value, label)
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as exc:
        _fail("INVALID_TIMESTAMP", f"{label}: {exc}")
    if parsed.tzinfo is None:
        _fail("INVALID_TIMESTAMP", f"{label} must include a timezone")
    return parsed


def _require_nullable_sha(value: Any, label: str, pattern: re.Pattern[str]) -> None:
    if value is not None and (not isinstance(value, str) or not pattern.fullmatch(value)):
        _fail("INVALID_DIGEST", f"{label}")


def _scan_public_clean(value: Any, path: str = "mission") -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            _scan_public_clean(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _scan_public_clean(child, f"{path}[{index}]")
    elif isinstance(value, str):
        for label, pattern in PROTECTED_PATTERNS:
            if pattern.search(value):
                _fail("PROTECTED_BOUNDARY_FAILURE", f"{label} detected at {path}")


def normalize_changed_paths(paths: Iterable[str]) -> list[str]:
    normalized: list[str] = []
    seen_folded: set[str] = set()
    for raw in paths:
        text = _require_nonempty_text(raw, "changed path").replace("\\", "/")
        pure = PurePosixPath(text)
        if pure.is_absolute() or text.startswith("/") or re.match(r"^[A-Za-z]:/", text) or ".." in pure.parts or text != pure.as_posix():
            _fail("UNSAFE_PATH", text)
        folded = text.casefold()
        if folded in seen_folded:
            _fail("DUPLICATE_PATH", text)
        seen_folded.add(folded)
        normalized.append(text)
    return sorted(normalized, key=lambda item: (item.casefold(), item))


def changed_paths_digest(paths: Iterable[str]) -> str:
    normalized = normalize_changed_paths(paths)
    return hashlib.sha256((("\n".join(normalized) + "\n") if normalized else "").encode("utf-8")).hexdigest()


def _validate_source_binding(binding: Any, source_status: str) -> None:
    if not isinstance(binding, Mapping):
        _fail("INVALID_FIELD", "source_binding must be an object")
    keys = frozenset({"base_sha", "branch", "pull_request", "expected_head", "changed_paths", "changed_paths_digest", "merged_commit"})
    _require_exact_keys(binding, keys, keys, "source_binding")
    _require_nullable_sha(binding["base_sha"], "source_binding.base_sha", SHA40)
    _require_nullable_sha(binding["expected_head"], "source_binding.expected_head", SHA40)
    _require_nullable_sha(binding["changed_paths_digest"], "source_binding.changed_paths_digest", SHA256)
    _require_nullable_sha(binding["merged_commit"], "source_binding.merged_commit", SHA40)
    if binding["branch"] is not None:
        _require_nonempty_text(binding["branch"], "source_binding.branch")
    if binding["pull_request"] is not None and (not isinstance(binding["pull_request"], int) or binding["pull_request"] < 1):
        _fail("INVALID_FIELD", "source_binding.pull_request")
    paths = binding["changed_paths"]
    if not isinstance(paths, list):
        _fail("INVALID_FIELD", "source_binding.changed_paths must be a list")
    normalized = normalize_changed_paths(paths)
    if paths != normalized:
        _fail("PATH_ORDER", "changed_paths must be sorted and case-fold unique")
    if paths:
        expected_digest = changed_paths_digest(paths)
        if binding["changed_paths_digest"] != expected_digest:
            _fail("PATH_DIGEST_MISMATCH", f"expected {expected_digest}")
    elif binding["changed_paths_digest"] is not None:
        _fail("PATH_DIGEST_MISMATCH", "empty paths require a null digest")
    if source_status in {"PR_OPEN", "MERGED_PENDING_READBACK", "CANONICAL"}:
        required = ("base_sha", "branch", "pull_request", "expected_head", "changed_paths_digest")
        if any(binding[field] is None for field in required) or not paths:
            _fail("SOURCE_BINDING_INCOMPLETE", source_status)
    if source_status in {"MERGED_PENDING_READBACK", "CANONICAL"} and binding["merged_commit"] is None:
        _fail("MERGE_BINDING_INCOMPLETE", source_status)


def _validate_coppermind(value: Any) -> None:
    if not isinstance(value, Mapping):
        _fail("INVALID_FIELD", "coppermind must be an object")
    keys = frozenset({"status", "reference", "archive_timestamp", "archive_package"})
    _require_exact_keys(value, keys, keys, "coppermind")
    if value["status"] not in ARCHIVE_STATES:
        _fail("INVALID_ENUM", "coppermind.status")
    if value["reference"] is not None:
        _require_nonempty_text(value["reference"], "coppermind.reference")
    if value["archive_timestamp"] is not None:
        _require_timestamp(value["archive_timestamp"], "coppermind.archive_timestamp")
    package = value["archive_package"]
    if package is not None:
        if not isinstance(package, Mapping):
            _fail("INVALID_FIELD", "coppermind.archive_package")
        required = frozenset({"mission_identity", "objective", "final_status", "decisions", "relationships", "worker_identity", "branch", "pull_request", "merged_commit", "changed_paths", "validation_summary", "receipts", "lesson_harvest", "unresolved_follow_up", "rollback", "canonical_readback", "archive_timestamp"})
        _require_exact_keys(package, required, required, "coppermind.archive_package")
        for field in ("mission_identity", "objective", "final_status", "worker_identity", "validation_summary", "rollback", "canonical_readback"):
            _require_nonempty_text(package[field], f"coppermind.archive_package.{field}")
        for field in ("decisions", "relationships", "changed_paths", "receipts", "lesson_harvest", "unresolved_follow_up"):
            _require_text_list(package[field], f"coppermind.archive_package.{field}")
        if package["archive_timestamp"] is not None:
            _require_timestamp(package["archive_timestamp"], "coppermind.archive_package.archive_timestamp")
    if value["status"] == "PENDING" and (value["reference"] is not None or package is not None):
        _fail("ARCHIVE_STATE_MISMATCH", "PENDING cannot claim a reference or package")
    if value["status"] == "PACKAGE_READY" and package is None:
        _fail("ARCHIVE_STATE_MISMATCH", "PACKAGE_READY requires archive_package")
    if value["status"] == "ARCHIVED" and (package is None or value["reference"] is None or value["archive_timestamp"] is None or package["archive_timestamp"] is None):
        _fail("ARCHIVE_STATE_MISMATCH", "ARCHIVED requires package, reference, and timestamp")
    if value["status"] == "NOT_APPLICABLE" and (value["reference"] is not None or value["archive_timestamp"] is not None or package is not None):
        _fail("ARCHIVE_STATE_MISMATCH", "NOT_APPLICABLE cannot claim an archive")


def _validate_sunset(value: Any, source_status: str, mission_state: str) -> None:
    if not isinstance(value, Mapping):
        _fail("INVALID_FIELD", "sunset must be an object")
    keys = frozenset({"conversation_summary", "exact_unfinished_work", "blockers", "lesson_harvest_dispositions", "golden_wing_candidate_disposition", "record_plan", "phoenix_processing_pending", "archival_status", "truth_state"})
    _require_exact_keys(value, keys, keys, "sunset")
    for field in ("conversation_summary", "golden_wing_candidate_disposition", "record_plan"):
        _require_nonempty_text(value[field], f"sunset.{field}")
    _require_text_list(value["exact_unfinished_work"], "sunset.exact_unfinished_work")
    _require_text_list(value["blockers"], "sunset.blockers")
    _require_text_list(value["lesson_harvest_dispositions"], "sunset.lesson_harvest_dispositions")
    if not isinstance(value["phoenix_processing_pending"], bool):
        _fail("INVALID_FIELD", "sunset.phoenix_processing_pending")
    if value["archival_status"] not in ARCHIVE_STATES:
        _fail("INVALID_ENUM", "sunset.archival_status")
    if value["truth_state"] not in SUNSET_TRUTH_STATES:
        _fail("INVALID_ENUM", "sunset.truth_state")
    if value["truth_state"] in {"CANONICAL_READBACK_COMPLETE", "SUNSET COMPLETE"} and source_status != "CANONICAL":
        _fail("FALSE_COMPLETION", "Sunset canonical completion requires canonical source readback")
    if value["truth_state"] == "SUNSET COMPLETE" and mission_state not in {"CANONICAL", "COPPERMIND_ARCHIVED", "CLOSED"}:
        _fail("FALSE_COMPLETION", "SUNSET COMPLETE requires a canonical Mission state")


def validate_mission(mission: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(mission, Mapping):
        _fail("INVALID_MISSION", "Mission must be an object")
    _require_exact_keys(mission, BASE_REQUIRED_KEYS, TOP_LEVEL_KEYS, "mission")
    if mission["schema_version"] != SCHEMA_VERSION:
        _fail("SCHEMA_VERSION", str(mission["schema_version"]))
    if not isinstance(mission["repository"], str) or not REPOSITORY.fullmatch(mission["repository"]):
        _fail("REPOSITORY_IDENTITY", str(mission["repository"]))
    if not isinstance(mission["issue_number"], int) or mission["issue_number"] < 1:
        _fail("ISSUE_IDENTITY", str(mission["issue_number"]))
    for field in ("mission_id", "attempt_id"):
        if not isinstance(mission[field], str) or not IDENTITY.fullmatch(mission[field]):
            _fail("MISSION_IDENTITY", field)
    if mission["mission_type"] not in MISSION_TYPES:
        _fail("INVALID_ENUM", "mission_type")
    if mission["mission_state"] not in MISSION_STATE_SET:
        _fail("INVALID_ENUM", "mission_state")
    created = _require_timestamp(mission["created_at"], "created_at")
    updated = _require_timestamp(mission["updated_at"], "updated_at")
    if updated < created:
        _fail("TIMESTAMP_ORDER", "updated_at precedes created_at")
    _require_nonempty_text(mission["objective"], "objective")
    _require_text_list(mission["rationale_and_decisions"], "rationale_and_decisions")
    owner = mission["owner"]
    if not isinstance(owner, Mapping):
        _fail("INVALID_FIELD", "owner")
    _require_exact_keys(owner, frozenset({"project", "operation"}), frozenset({"project", "operation"}), "owner")
    _require_nonempty_text(owner["project"], "owner.project")
    _require_nonempty_text(owner["operation"], "owner.operation")
    relationships = mission["relationships"]
    if not isinstance(relationships, Mapping):
        _fail("INVALID_FIELD", "relationships")
    rel_keys = frozenset({"quest", "campaign", "gate"})
    _require_exact_keys(relationships, rel_keys, rel_keys, "relationships")
    for field in rel_keys:
        if relationships[field] is not None:
            _require_nonempty_text(relationships[field], f"relationships.{field}")
    _require_nonempty_text(mission["assigned_worker"], "assigned_worker")
    identity = mission["execution_identity"]
    if not isinstance(identity, Mapping):
        _fail("INVALID_FIELD", "execution_identity")
    identity_keys = frozenset({"declared_worker", "credential_principal", "surface", "publisher"})
    _require_exact_keys(identity, identity_keys, identity_keys, "execution_identity")
    for field in identity_keys:
        _require_nonempty_text(identity[field], f"execution_identity.{field}")
    dependencies = mission["dependencies"]
    if not isinstance(dependencies, list):
        _fail("INVALID_FIELD", "dependencies")
    dependency_keys = frozenset({"relation", "repository", "mission_ref"})
    for index, dependency in enumerate(dependencies):
        if not isinstance(dependency, Mapping):
            _fail("INVALID_FIELD", f"dependencies[{index}]")
        _require_exact_keys(dependency, dependency_keys, dependency_keys, f"dependencies[{index}]")
        if dependency["relation"] not in DEPENDENCY_RELATIONS:
            _fail("INVALID_ENUM", f"dependencies[{index}].relation")
        if not isinstance(dependency["repository"], str) or not REPOSITORY.fullmatch(dependency["repository"]):
            _fail("REPOSITORY_IDENTITY", f"dependencies[{index}]")
        _require_nonempty_text(dependency["mission_ref"], f"dependencies[{index}].mission_ref")
    boundary = mission["public_clean_boundary"]
    if not isinstance(boundary, Mapping):
        _fail("INVALID_FIELD", "public_clean_boundary")
    boundary_keys = frozenset({"classification", "sanitized_summary", "protected_pointer"})
    _require_exact_keys(boundary, boundary_keys, boundary_keys, "public_clean_boundary")
    if boundary["classification"] != "PUBLIC_CLEAN":
        _fail("PROTECTED_BOUNDARY_FAILURE", "classification must be PUBLIC_CLEAN")
    _require_nonempty_text(boundary["sanitized_summary"], "public_clean_boundary.sanitized_summary")
    if boundary["protected_pointer"] is not None and not str(boundary["protected_pointer"]).startswith("protected://"):
        _fail("PROTECTED_POINTER", "only protected:// pointers are accepted")
    _require_text_list(mission["acceptance_criteria"], "acceptance_criteria", nonempty=True)
    _require_nonempty_text(mission["next_safe_action"], "next_safe_action")
    _require_nonempty_text(mission["rollback"], "rollback")
    _require_text_list(mission["completion_proof"], "completion_proof")
    if mission["effort_class"] not in EFFORT_CLASSES:
        _fail("INVALID_ENUM", "effort_class")
    if mission["queue_behavior"] not in QUEUE_BEHAVIORS:
        _fail("INVALID_ENUM", "queue_behavior")
    if mission["canonical_source_status"] not in CANONICAL_SOURCE_STATES:
        _fail("INVALID_ENUM", "canonical_source_status")
    _validate_source_binding(mission["source_binding"], mission["canonical_source_status"])
    review = mission["validation_review"]
    if not isinstance(review, Mapping):
        _fail("INVALID_FIELD", "validation_review")
    review_keys = frozenset({"validation_status", "review_status", "strikeforce_status", "receipt_refs"})
    _require_exact_keys(review, review_keys, review_keys, "validation_review")
    if review["validation_status"] not in VALIDATION_STATES or review["review_status"] not in REVIEW_STATES or review["strikeforce_status"] not in STRIKEFORCE_STATES:
        _fail("INVALID_ENUM", "validation_review")
    _require_text_list(review["receipt_refs"], "validation_review.receipt_refs")
    _validate_coppermind(mission["coppermind"])
    if mission["mission_type"] == "mission/sunset":
        if "sunset" not in mission:
            _fail("MISSING_FIELDS", "mission/sunset requires sunset")
        _validate_sunset(mission["sunset"], mission["canonical_source_status"], mission["mission_state"])
    elif "sunset" in mission:
        _fail("UNEXPECTED_SUNSET", "only mission/sunset may contain sunset")
    if mission["mission_state"] == "COPPERMIND_ARCHIVED" and mission["coppermind"]["status"] != "ARCHIVED":
        _fail("ARCHIVE_STATE_MISMATCH", "COPPERMIND_ARCHIVED requires a real archive receipt")
    if mission["mission_state"] in {"CANONICAL", "COPPERMIND_ARCHIVED", "CLOSED"} and mission["canonical_source_status"] not in {"CANONICAL", "NO_SOURCE_CHANGE_REQUIRED"}:
        _fail("FALSE_COMPLETION", f"{mission['mission_state']} requires canonical readback or no source change")
    if mission["mission_state"] == "CLOSED":
        if mission["canonical_source_status"] not in {"CANONICAL", "NO_SOURCE_CHANGE_REQUIRED"}:
            _fail("FALSE_COMPLETION", "CLOSED requires canonical readback or no source change")
        if not mission["completion_proof"]:
            _fail("FALSE_COMPLETION", "CLOSED requires completion_proof")
        if mission["coppermind"]["status"] not in {"PACKAGE_READY", "ARCHIVED", "NOT_APPLICABLE"}:
            _fail("FALSE_COMPLETION", "CLOSED requires archival disposition")
    _scan_public_clean(mission)
    return deepcopy(dict(mission))


def validate_transition(previous: str, current: str) -> None:
    if previous not in TRANSITIONS or current not in MISSION_STATE_SET:
        _fail("INVALID_ENUM", f"transition {previous}->{current}")
    if current != previous and current not in TRANSITIONS[previous]:
        _fail("INVALID_TRANSITION", f"{previous}->{current}")


def validate_source_transition(previous: str, current: str) -> None:
    if previous not in SOURCE_TRANSITIONS or current not in CANONICAL_SOURCE_STATES:
        _fail("INVALID_ENUM", f"source transition {previous}->{current}")
    if current != previous and current not in SOURCE_TRANSITIONS[previous]:
        _fail("INVALID_SOURCE_TRANSITION", f"{previous}->{current}")


def extract_manifest(text: str) -> dict[str, Any]:
    matches = MANIFEST_BLOCK.findall(text or "")
    if len(matches) != 1:
        _fail("MANIFEST_CARDINALITY", f"expected 1 atlas-mission-v1 block, found {len(matches)}")
    value = parse_json_document(matches[0])
    return validate_mission(value)


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, child in pairs:
        if key in value:
            _fail("DUPLICATE_JSON_KEY", key)
        value[key] = child
    return value


def parse_json_document(text: str) -> dict[str, Any]:
    try:
        value = json.loads(text, object_pairs_hook=_unique_object)
    except json.JSONDecodeError as exc:
        _fail("MANIFEST_JSON", str(exc))
    if not isinstance(value, dict):
        _fail("INVALID_MISSION", "JSON document must be an object")
    return value


def reconcile_issue_snapshot(snapshot: Mapping[str, Any], expected_repository: str, expected_issue_number: int) -> dict[str, Any]:
    if snapshot.get("repository") != expected_repository or snapshot.get("number") != expected_issue_number:
        _fail("IDENTITY_MISMATCH", "repository or issue number")
    if snapshot.get("is_pull_request") is True:
        _fail("IDENTITY_MISMATCH", f"repository object #{expected_issue_number} is a pull request, not a Mission Issue")
    bodies = [snapshot.get("body") or ""] + [str(item.get("body") or "") for item in snapshot.get("comments", []) if isinstance(item, Mapping)]
    manifests: list[dict[str, Any]] = []
    for body in bodies:
        if MANIFEST_BLOCK.search(body):
            manifests.append(extract_manifest(body))
    if not manifests:
        _fail("MISSION_MANIFEST_MISSING", f"Issue #{expected_issue_number}")
    mission_ids = {item["mission_id"] for item in manifests}
    attempt_ids = {item["attempt_id"] for item in manifests}
    if len(mission_ids) != 1 or len(attempt_ids) != 1:
        _fail("CONTRADICTORY_MISSION_CLAIM", "Mission or attempt identity changed")
    for previous, current in zip(manifests, manifests[1:]):
        previous_updated = _require_timestamp(previous["updated_at"], "updated_at")
        current_updated = _require_timestamp(current["updated_at"], "updated_at")
        if current_updated < previous_updated:
            _fail("STALE_MISSION_CLAIM", "a later Issue comment carries an older updated_at")
        validate_transition(previous["mission_state"], current["mission_state"])
        validate_source_transition(previous["canonical_source_status"], current["canonical_source_status"])
    latest = manifests[-1]
    if latest["repository"] != expected_repository or latest["issue_number"] != expected_issue_number:
        _fail("IDENTITY_MISMATCH", "manifest does not bind the enclosing issue")
    return latest


def resume_plan(mission: Mapping[str, Any], canonical_head: str, *, pr_snapshot: Mapping[str, Any] | None = None) -> dict[str, Any]:
    current = validate_mission(mission)
    if not SHA40.fullmatch(canonical_head):
        _fail("CANONICAL_HEAD", canonical_head)
    binding = current["source_binding"]
    source_status = current["canonical_source_status"]
    if source_status == "PHOENIX_PENDING" and binding["base_sha"] not in {None, canonical_head}:
        _fail("STALE_MISSION_CLAIM", f"base {binding['base_sha']} is not current {canonical_head}")
    if source_status in {"PR_OPEN", "MERGED_PENDING_READBACK"}:
        if pr_snapshot is None:
            _fail("PR_READBACK_REQUIRED", source_status)
        if not isinstance(pr_snapshot, Mapping):
            _fail("INVALID_FIELD", "pr_snapshot must be an object")
        expected = {"number": binding["pull_request"], "head_sha": binding["expected_head"], "branch": binding["branch"]}
        observed = {key: pr_snapshot.get(key) for key in expected}
        if observed != expected:
            _fail("STALE_OR_CONTRADICTORY_PR", f"expected {expected}, observed {observed}")
    if source_status == "MERGED_PENDING_READBACK" and canonical_head == binding["merged_commit"]:
        action = "Verify exact tree and changed paths, then transition canonical-source status to CANONICAL."
    elif current["mission_state"] == "BLOCKED_RESUMABLE":
        action = current["next_safe_action"]
    elif current["mission_state"] in {"CANONICAL", "COPPERMIND_ARCHIVED", "CLOSED"}:
        action = "No implementation retry. Reconcile archival and closeout evidence only."
    else:
        action = current["next_safe_action"]
    return {
        "mission_id": current["mission_id"],
        "repository": current["repository"],
        "issue_number": current["issue_number"],
        "last_proven_state": current["mission_state"],
        "canonical_source_status": source_status,
        "canonical_head": canonical_head,
        "next_safe_action": action,
    }


def duplicate_key(mission: Mapping[str, Any]) -> str:
    current = validate_mission(mission)
    binding = current["source_binding"]
    components = (
        current["mission_id"],
        current["repository"],
        str(current["issue_number"]),
        binding["base_sha"] or "NONE",
        binding["branch"] or "NONE",
        str(binding["pull_request"] or "NONE"),
        binding["expected_head"] or "NONE",
        binding["changed_paths_digest"] or "NONE",
        current["attempt_id"],
    )
    return hashlib.sha256("\0".join(components).encode("utf-8")).hexdigest()


def assert_no_duplicate(candidate: Mapping[str, Any], existing: Sequence[Mapping[str, Any]]) -> None:
    current = validate_mission(candidate)
    key = duplicate_key(current)
    for item in existing:
        observed = validate_mission(item)
        if observed["repository"] != current["repository"]:
            continue
        if duplicate_key(observed) == key:
            _fail("REPLAY", key)
        same_mission = observed["mission_id"] == current["mission_id"] or observed["issue_number"] == current["issue_number"]
        same_attempt = observed["attempt_id"] == current["attempt_id"]
        if same_mission or same_attempt:
            _fail("CONFLICTING_BINDING", f"Mission or attempt already exists with different transaction bindings: {observed['mission_id']}")
        current_binding = current["source_binding"]
        observed_binding = observed["source_binding"]
        for field in ("branch", "pull_request", "expected_head"):
            if current_binding[field] is not None and current_binding[field] == observed_binding[field]:
                _fail("CONFLICTING_BINDING", f"source_binding.{field} is already bound to {observed['mission_id']}")
        if (
            current_binding["base_sha"] is not None
            and current_binding["changed_paths_digest"] is not None
            and current_binding["base_sha"] == observed_binding["base_sha"]
            and current_binding["changed_paths_digest"] == observed_binding["changed_paths_digest"]
        ):
            _fail("CONFLICTING_BINDING", f"base and changed-path digest are already bound to {observed['mission_id']}")


def _dependency_names(mission: Mapping[str, Any]) -> frozenset[str]:
    number = mission["issue_number"]
    return frozenset({mission["mission_id"], f"Mission #{number}", f"Mission {number}", f"#{number}"})


def _blocked_mission_stops_remaining(blocked: Mapping[str, Any], remaining: Sequence[Mapping[str, Any]]) -> bool:
    blocked_names = _dependency_names(blocked)
    remaining_names = set().union(*(_dependency_names(item) for item in remaining)) if remaining else set()
    for dependency in blocked["dependencies"]:
        if dependency["repository"] == blocked["repository"] and dependency["relation"] == "BLOCKS" and dependency["mission_ref"] in remaining_names:
            return True
    for item in remaining:
        for dependency in item["dependencies"]:
            if dependency["repository"] == blocked["repository"] and dependency["relation"] == "BLOCKED_BY" and dependency["mission_ref"] in blocked_names:
                return True
    return False


def sequence_missions(missions: Mapping[int, Mapping[str, Any]], order: Sequence[int]) -> dict[str, Any]:
    results: list[dict[str, Any]] = []
    stopped = False
    validated: dict[int, dict[str, Any]] = {}
    for issue_number, mission in missions.items():
        validated[issue_number] = validate_mission(mission)
    for position, issue_number in enumerate(order):
        if stopped:
            results.append({"issue_number": issue_number, "result": "NOT_STARTED_AFTER_STOP"})
            continue
        if issue_number not in missions:
            results.append({"issue_number": issue_number, "result": "IDENTITY_MISMATCH", "detail": "Mission Issue not found"})
            stopped = True
            continue
        mission = validated[issue_number]
        if mission["issue_number"] != issue_number:
            _fail("IDENTITY_MISMATCH", f"requested {issue_number}, manifest {mission['issue_number']}")
        state = mission["mission_state"]
        if state in {"CANONICAL", "COPPERMIND_ARCHIVED", "CLOSED"}:
            result = "COMPLETE"
        elif state == "BLOCKED_RESUMABLE":
            result = "BLOCKED_RESUMABLE"
            remaining = [validated[number] for number in order[position + 1 :] if number in validated]
            if mission["queue_behavior"] != "CONTINUE_IF_BLOCKED_RESUMABLE" or _blocked_mission_stops_remaining(mission, remaining):
                stopped = True
        else:
            result = "ACTION_REQUIRED"
            stopped = True
        results.append({"issue_number": issue_number, "mission_id": mission["mission_id"], "result": result, "next_safe_action": mission["next_safe_action"]})
    return {"requested_order": list(order), "results": results, "stopped": stopped}
