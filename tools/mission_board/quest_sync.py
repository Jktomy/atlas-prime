from __future__ import annotations

import base64
import hashlib
import json
import re
from copy import deepcopy
from typing import Any, Mapping, Sequence

from .core import MissionError, validate_mission


RECEIPT_SCHEMA_ID = "atlas.mission.quest-sync-receipt"
RECEIPT_SCHEMA_VERSION = "1.0.0"
RECEIPT_BLOCK = re.compile(r"```atlas-quest-sync-receipt-v1\s*\n(.*?)\n```", re.DOTALL)
SHA40 = re.compile(r"^[0-9a-f]{40}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
RECEIPT_ID = re.compile(r"^QSR-[A-Z2-7]{26}$")

GLOBAL_QUEST_DOCTRINE_PATHS = frozenset(
    {
        "continuity/mission-board-quest-registry-r01.json",
        "continuity/prime-continuity-register-r01.json",
        "governance/atlas-quest-portfolio-contract.md",
        "governance/mission-board-contract.md",
        "governance/mission-quest-emberline-contract.md",
        "governance/quest-engine-continuity-contract.md",
        "recovery/elantris-recovery.md",
    }
)
GLOBAL_QUEST_DOCTRINE_PREFIXES = ("tools/mission_board/",)
RECEIPT_KEYS = frozenset(
    {
        "schema_id",
        "schema_version",
        "receipt_id",
        "repository",
        "child_mission_id",
        "child_issue_number",
        "merged_commit",
        "changed_paths_digest",
        "parent_quest_id",
        "parent_issue_number",
        "parent_mission_id",
        "impact_summary",
        "readback_status",
    }
)


def _fail(code: str, detail: str) -> None:
    raise MissionError(f"{code}: {detail}")


def _canonical_bytes(value: Mapping[str, Any], *, omit_receipt_id: bool = False) -> bytes:
    payload = dict(value)
    if omit_receipt_id:
        payload.pop("receipt_id", None)
    return (json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def _stable_receipt_id(receipt: Mapping[str, Any]) -> str:
    digest = hashlib.sha256(_canonical_bytes(receipt, omit_receipt_id=True)).digest()
    token = base64.b32encode(digest).decode("ascii").rstrip("=")[:26]
    return f"QSR-{token}"


def _registry_entries(registry: Mapping[str, Any]) -> list[dict[str, Any]]:
    if not isinstance(registry, Mapping):
        _fail("QUEST_REGISTRY_INVALID", "registry must be an object")
    if registry.get("schema_version") != "atlas.mission-board-quest-registry.v1":
        _fail("QUEST_REGISTRY_INVALID", "unexpected schema version")
    if registry.get("authority") != "CANONICAL_ADMITTED_QUEST_REGISTRY":
        _fail("QUEST_REGISTRY_INVALID", "registry is not canonical authority")
    entries = registry.get("entries")
    if not isinstance(entries, list):
        _fail("QUEST_REGISTRY_INVALID", "entries must be a list")
    normalized: list[dict[str, Any]] = []
    seen_quests: set[str] = set()
    seen_issues: set[int] = set()
    for index, entry in enumerate(entries):
        if not isinstance(entry, Mapping):
            _fail("QUEST_REGISTRY_INVALID", f"entry {index} is not an object")
        required = {"quest_id", "source", "parent_issue_number", "parent_mission_id", "state"}
        if not required.issubset(entry):
            _fail("QUEST_REGISTRY_INVALID", f"entry {index} is incomplete")
        quest_id = entry["quest_id"]
        source = entry["source"]
        issue_number = entry["parent_issue_number"]
        parent_mission_id = entry["parent_mission_id"]
        if not all(isinstance(value, str) and value for value in (quest_id, source, parent_mission_id)):
            _fail("QUEST_REGISTRY_INVALID", f"entry {index} identity is invalid")
        if type(issue_number) is not int or issue_number < 1:
            _fail("QUEST_REGISTRY_INVALID", f"entry {index} parent issue is invalid")
        if quest_id in seen_quests or issue_number in seen_issues:
            _fail("QUEST_REGISTRY_INVALID", "duplicate Quest or parent Issue identity")
        seen_quests.add(quest_id)
        seen_issues.add(issue_number)
        normalized.append(dict(entry))
    return normalized


def affected_parent_quests(
    mission: Mapping[str, Any],
    quest_registry: Mapping[str, Any],
    *,
    changed_paths: Sequence[str] | None = None,
) -> list[dict[str, Any]]:
    """Return active parent Quests whose live Issues require a synchronization receipt."""

    current = validate_mission(mission)
    if current["mission_type"] == "mission/quest":
        return []
    entries = _registry_entries(quest_registry)
    paths = list(changed_paths if changed_paths is not None else current["source_binding"]["changed_paths"])
    if any(not isinstance(path, str) or not path for path in paths):
        _fail("QUEST_SYNC_PATHS", "changed paths must be nonempty repository-relative strings")

    global_impact = any(path in GLOBAL_QUEST_DOCTRINE_PATHS for path in paths) or any(
        path.startswith(prefix) for path in paths for prefix in GLOBAL_QUEST_DOCTRINE_PREFIXES
    )
    relationship = current["relationships"].get("quest")
    dependency_refs = {
        dependency["mission_ref"].strip().casefold()
        for dependency in current["dependencies"]
        if dependency["repository"] == current["repository"] and dependency["relation"] == "CHILD_OF"
    }

    affected: list[dict[str, Any]] = []
    for entry in entries:
        issue_number = entry["parent_issue_number"]
        parent_refs = {
            entry["parent_mission_id"].casefold(),
            f"mission #{issue_number}",
            f"mission {issue_number}",
            f"#{issue_number}",
            str(issue_number),
        }
        direct_relationship = relationship in {entry["quest_id"], entry["source"]}
        source_change = entry["source"] in paths
        dependency_change = bool(dependency_refs & parent_refs)
        if global_impact or direct_relationship or source_change or dependency_change:
            affected.append(entry)
    return sorted(affected, key=lambda item: item["parent_issue_number"])


def validate_quest_sync_receipt(receipt: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(receipt, Mapping):
        _fail("QUEST_SYNC_RECEIPT_INVALID", "receipt must be an object")
    if set(receipt) != RECEIPT_KEYS:
        missing = sorted(RECEIPT_KEYS - set(receipt))
        extra = sorted(set(receipt) - RECEIPT_KEYS)
        _fail("QUEST_SYNC_RECEIPT_INVALID", f"missing={missing}, extra={extra}")
    if receipt["schema_id"] != RECEIPT_SCHEMA_ID or receipt["schema_version"] != RECEIPT_SCHEMA_VERSION:
        _fail("QUEST_SYNC_RECEIPT_INVALID", "schema identity mismatch")
    if receipt["repository"] != "Jktomy/atlas-prime":
        _fail("QUEST_SYNC_RECEIPT_INVALID", "repository mismatch")
    if not isinstance(receipt["receipt_id"], str) or RECEIPT_ID.fullmatch(receipt["receipt_id"]) is None:
        _fail("QUEST_SYNC_RECEIPT_INVALID", "receipt_id")
    if _stable_receipt_id(receipt) != receipt["receipt_id"]:
        _fail("QUEST_SYNC_RECEIPT_INVALID", "receipt_id does not bind the canonical payload")
    for field in ("child_mission_id", "parent_quest_id", "parent_mission_id", "impact_summary"):
        if not isinstance(receipt[field], str) or not receipt[field].strip():
            _fail("QUEST_SYNC_RECEIPT_INVALID", field)
    for field in ("child_issue_number", "parent_issue_number"):
        if type(receipt[field]) is not int or receipt[field] < 1:
            _fail("QUEST_SYNC_RECEIPT_INVALID", field)
    if not isinstance(receipt["merged_commit"], str) or SHA40.fullmatch(receipt["merged_commit"]) is None:
        _fail("QUEST_SYNC_RECEIPT_INVALID", "merged_commit")
    if not isinstance(receipt["changed_paths_digest"], str) or SHA256.fullmatch(receipt["changed_paths_digest"]) is None:
        _fail("QUEST_SYNC_RECEIPT_INVALID", "changed_paths_digest")
    if receipt["readback_status"] != "EXACT_MERGED_MAIN":
        _fail("QUEST_SYNC_RECEIPT_INVALID", "readback_status")
    return deepcopy(dict(receipt))


def build_quest_sync_receipt(
    mission: Mapping[str, Any],
    parent_entry: Mapping[str, Any],
    *,
    canonical_head: str,
    impact_summary: str,
) -> dict[str, Any]:
    current = validate_mission(mission)
    binding = current["source_binding"]
    if current["canonical_source_status"] != "CANONICAL" or binding["merged_commit"] != canonical_head:
        _fail("QUEST_SYNC_READBACK_REQUIRED", "child Mission must bind exact merged-main readback")
    if not isinstance(canonical_head, str) or SHA40.fullmatch(canonical_head) is None:
        _fail("QUEST_SYNC_READBACK_REQUIRED", "canonical head is invalid")
    if not isinstance(impact_summary, str) or not impact_summary.strip() or len(impact_summary) > 1000:
        _fail("QUEST_SYNC_RECEIPT_INVALID", "impact_summary")
    if binding["changed_paths_digest"] is None:
        _fail("QUEST_SYNC_RECEIPT_INVALID", "source-changing child Mission requires changed-path digest")
    receipt: dict[str, Any] = {
        "schema_id": RECEIPT_SCHEMA_ID,
        "schema_version": RECEIPT_SCHEMA_VERSION,
        "receipt_id": "QSR-AAAAAAAAAAAAAAAAAAAAAAAAAA",
        "repository": current["repository"],
        "child_mission_id": current["mission_id"],
        "child_issue_number": current["issue_number"],
        "merged_commit": canonical_head,
        "changed_paths_digest": binding["changed_paths_digest"],
        "parent_quest_id": parent_entry["quest_id"],
        "parent_issue_number": parent_entry["parent_issue_number"],
        "parent_mission_id": parent_entry["parent_mission_id"],
        "impact_summary": impact_summary.strip(),
        "readback_status": "EXACT_MERGED_MAIN",
    }
    receipt["receipt_id"] = _stable_receipt_id(receipt)
    return validate_quest_sync_receipt(receipt)


def receipt_markdown(receipt: Mapping[str, Any]) -> str:
    current = validate_quest_sync_receipt(receipt)
    return "```atlas-quest-sync-receipt-v1\n" + json.dumps(current, ensure_ascii=False, indent=2, sort_keys=True) + "\n```"


def _snapshot_receipts(snapshot: Mapping[str, Any], expected_issue_number: int) -> list[dict[str, Any]]:
    if not isinstance(snapshot, Mapping):
        _fail("QUEST_SYNC_PARENT_READBACK", f"parent Issue #{expected_issue_number} snapshot is unavailable")
    number = snapshot.get("number", snapshot.get("issue_number"))
    if number != expected_issue_number or snapshot.get("is_pull_request") is True:
        _fail("QUEST_SYNC_PARENT_READBACK", f"parent Issue #{expected_issue_number} identity mismatch")
    bodies = [snapshot.get("body") or ""]
    comments = snapshot.get("comments", [])
    if not isinstance(comments, list):
        _fail("QUEST_SYNC_PARENT_READBACK", f"parent Issue #{expected_issue_number} comments are unreadable")
    bodies.extend(str(item.get("body") or "") for item in comments if isinstance(item, Mapping))
    receipts: list[dict[str, Any]] = []
    for body in bodies:
        for raw in RECEIPT_BLOCK.findall(str(body)):
            try:
                value = json.loads(raw)
            except json.JSONDecodeError as exc:
                _fail("QUEST_SYNC_RECEIPT_INVALID", f"parent Issue #{expected_issue_number}: {exc}")
            receipts.append(validate_quest_sync_receipt(value))
    return receipts


def enforce_quest_sync_closure(
    mission: Mapping[str, Any],
    quest_registry: Mapping[str, Any],
    parent_issue_snapshots: Mapping[int, Mapping[str, Any]],
    *,
    canonical_head: str,
    changed_paths: Sequence[str] | None = None,
) -> dict[str, Any]:
    """Fail closed with QUEST_SYNC_PENDING until every affected parent receipt is proven."""

    current = validate_mission(mission)
    entries = affected_parent_quests(current, quest_registry, changed_paths=changed_paths)
    if not entries:
        return {
            "status": "NOT_REQUIRED",
            "mission_id": current["mission_id"],
            "required_parent_issues": [],
            "confirmed_receipts": [],
        }

    binding = current["source_binding"]
    if current["canonical_source_status"] != "CANONICAL" or binding["merged_commit"] != canonical_head:
        _fail("QUEST_SYNC_PENDING", "exact merged-main readback is not proven")
    if not isinstance(canonical_head, str) or SHA40.fullmatch(canonical_head) is None:
        _fail("QUEST_SYNC_PENDING", "canonical head is invalid")

    confirmed: list[str] = []
    for entry in entries:
        issue_number = entry["parent_issue_number"]
        snapshot = parent_issue_snapshots.get(issue_number)
        receipts = _snapshot_receipts(snapshot, issue_number)
        matches = [
            receipt
            for receipt in receipts
            if receipt["repository"] == current["repository"]
            and receipt["child_mission_id"] == current["mission_id"]
            and receipt["child_issue_number"] == current["issue_number"]
            and receipt["merged_commit"] == canonical_head
            and receipt["changed_paths_digest"] == binding["changed_paths_digest"]
            and receipt["parent_quest_id"] == entry["quest_id"]
            and receipt["parent_issue_number"] == issue_number
            and receipt["parent_mission_id"] == entry["parent_mission_id"]
        ]
        if not matches:
            _fail("QUEST_SYNC_PENDING", f"parent Issue #{issue_number} lacks the exact synchronization receipt")
        if len(matches) != 1:
            _fail("QUEST_SYNC_DUPLICATE", f"parent Issue #{issue_number} contains duplicate synchronization receipts")
        confirmed.append(matches[0]["receipt_id"])

    return {
        "status": "PASS",
        "mission_id": current["mission_id"],
        "merged_commit": canonical_head,
        "required_parent_issues": [entry["parent_issue_number"] for entry in entries],
        "confirmed_receipts": confirmed,
    }
