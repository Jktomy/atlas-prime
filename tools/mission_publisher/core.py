from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from pathlib import PurePosixPath
from typing import Any, Iterable, Mapping

SHA40 = re.compile(r"^[0-9a-f]{40}$")
REPOSITORY = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
PROTECTED = (
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    re.compile(r"(?i)\b(?:password|secret|api[_-]?key|access[_-]?token)\s*[:=]\s*['\"][^'\"\r\n]{8,}['\"]"),
)

class PublicationError(ValueError):
    pass

def _fail(code: str, detail: str) -> None:
    raise PublicationError(f"{code}: {detail}")

def canonical_json(value: Mapping[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def digest_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()

def normalize_paths(paths: Iterable[str]) -> list[str]:
    normalized: list[str] = []
    seen: set[str] = set()
    for raw in paths:
        if not isinstance(raw, str) or not raw.strip():
            _fail("INVALID_PATH", "path must be nonempty text")
        text = unicodedata.normalize("NFC", raw.replace("\\", "/"))
        pure = PurePosixPath(text)
        if pure.is_absolute() or text.startswith("/") or ".." in pure.parts or text != pure.as_posix():
            _fail("UNSAFE_PATH", text)
        folded = text.casefold()
        if folded in seen:
            _fail("DUPLICATE_PATH", text)
        seen.add(folded)
        normalized.append(text)
    return sorted(normalized, key=lambda item: (item.casefold(), item))

def _scan(value: Any) -> None:
    text = json.dumps(value, sort_keys=True, ensure_ascii=False)
    for pattern in PROTECTED:
        if pattern.search(text):
            _fail("PROTECTED_BOUNDARY_FAILURE", "protected-looking content detected")

def build_plan(mission: Mapping[str, Any], canonical_base: str, changed_paths: Iterable[str], sealed_paths: Iterable[str], *, publisher: str = "MISSION_BOARD_ADAPTER") -> dict[str, Any]:
    if not isinstance(mission, Mapping):
        _fail("INVALID_MISSION", "mission must be an object")
    _scan(mission)
    if not SHA40.fullmatch(canonical_base):
        _fail("INVALID_BASE", canonical_base)
    repository = mission.get("repository")
    issue_number = mission.get("issue_number")
    mission_id = mission.get("mission_id")
    attempt_id = mission.get("attempt_id")
    objective = mission.get("objective")
    if not isinstance(repository, str) or not REPOSITORY.fullmatch(repository):
        _fail("IDENTITY_MISMATCH", "repository")
    if type(issue_number) is not int or issue_number < 1:
        _fail("IDENTITY_MISMATCH", "issue_number")
    for label, value in (("mission_id", mission_id), ("attempt_id", attempt_id), ("objective", objective)):
        if not isinstance(value, str) or not value.strip():
            _fail("INVALID_MISSION", label)
    paths = normalize_paths(changed_paths)
    envelope = set(normalize_paths(sealed_paths))
    outside = [path for path in paths if path not in envelope]
    if outside:
        _fail("PATH_OUTSIDE_ENVELOPE", ", ".join(outside))
    if not paths:
        _fail("EMPTY_CANDIDATE", "at least one changed path is required")
    slug = re.sub(r"[^a-z0-9]+", "-", mission_id.lower()).strip("-")[:60]
    branch = f"mission/{issue_number}-{slug}"
    plan = {
        "schema_version": "atlas.mission-publication-plan.v1",
        "repository": repository,
        "issue_number": issue_number,
        "mission_id": mission_id,
        "attempt_id": attempt_id,
        "canonical_base": canonical_base,
        "branch": branch,
        "commit_message": f"Build Mission #{issue_number} publication foundation",
        "pull_request_title": f"Mission #{issue_number}: publication foundation",
        "changed_paths": paths,
        "changed_paths_digest": digest_text("\n".join(paths) + "\n"),
        "objective_digest": digest_text(objective),
        "publisher": publisher,
        "public_clean": True,
        "next_safe_action": "Authenticated adapter performs fresh readback, replay search, one branch, one commit, and one draft PR.",
    }
    _scan(plan)
    return plan

def build_receipt(plan: Mapping[str, Any], *, status: str, candidate_tree: str | None = None, expected_head: str | None = None, pull_request: int | None = None, reconciled: bool = False, next_safe_action: str) -> dict[str, Any]:
    if status not in {"PLANNED", "PR_OPEN", "BLOCKED_RESUMABLE"}:
        _fail("INVALID_STATUS", status)
    if status == "PR_OPEN":
        if not (candidate_tree and SHA40.fullmatch(candidate_tree) and expected_head and SHA40.fullmatch(expected_head) and type(pull_request) is int and pull_request > 0):
            _fail("INCOMPLETE_RECEIPT", "PR_OPEN requires tree, head, and pull request")
    receipt = {
        "schema_version": "atlas.mission-publication-receipt.v1",
        "status": status,
        "repository": plan["repository"],
        "issue_number": plan["issue_number"],
        "mission_id": plan["mission_id"],
        "attempt_id": plan["attempt_id"],
        "canonical_base": plan["canonical_base"],
        "branch": plan["branch"],
        "changed_paths_digest": plan["changed_paths_digest"],
        "candidate_tree": candidate_tree,
        "expected_head": expected_head,
        "pull_request": pull_request,
        "draft": status == "PR_OPEN",
        "reconciled": reconciled,
        "next_safe_action": next_safe_action,
    }
    _scan(receipt)
    return receipt
