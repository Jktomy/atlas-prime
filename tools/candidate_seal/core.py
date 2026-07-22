from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from pathlib import PurePosixPath
from typing import Any, Iterable, Mapping, Sequence

SHA40 = re.compile(r"^[0-9a-f]{40}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
REPOSITORY = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
BRANCH = re.compile(r"^[A-Za-z0-9._/-]+$")
DRIVE_PATH = re.compile(r"^[A-Za-z]:/")
PROTECTED = (
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    re.compile(
        r"(?i)\b(?:password|secret|api[_-]?key|access[_-]?token)"
        r"\s*[:=]\s*['\"][^'\"\r\n]{8,}['\"]"
    ),
)
GENERATED_STATES = {"CURRENT", "STALE_ALLOWED", "STALE_BLOCKING"}
REPAIR_CLASSIFICATIONS = {
    "ACTIONABLE",
    "INCORRECT",
    "DUPLICATE",
    "ALREADY_RESOLVED",
    "INFORMATIONAL",
    "UNAVAILABLE",
    "DECISION_REQUIRED",
    "UNKNOWN",
}
INVALIDATED_EVIDENCE = [
    "CANDIDATE_SEAL",
    "PREPUBLICATION_VALIDATION",
    "HOSTED_VALIDATION",
    "REVIEW",
    "STRIKEFORCE",
    "READY",
    "MERGE",
]


class CandidateSealError(ValueError):
    def __init__(self, code: str, detail: str) -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code


def _fail(code: str, detail: str) -> None:
    raise CandidateSealError(code, detail)


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _sha256_json(value: Any) -> str:
    return sha256_text(canonical_json(value))


def normalize_paths(paths: Iterable[str]) -> list[str]:
    normalized: list[str] = []
    seen: set[str] = set()
    for raw in paths:
        if not isinstance(raw, str) or not raw or raw != raw.strip():
            _fail("INVALID_PATH", "path must be exact nonempty text")
        if unicodedata.normalize("NFC", raw) != raw:
            _fail("NONCANONICAL_PATH", raw)
        pure = PurePosixPath(raw)
        if (
            "\\" in raw
            or any(ord(character) < 32 for character in raw)
            or pure.is_absolute()
            or raw.startswith("/")
            or DRIVE_PATH.match(raw)
            or any(part in {"", ".", ".."} for part in raw.split("/"))
            or raw != pure.as_posix()
        ):
            _fail("UNSAFE_PATH", raw)
        folded = raw.casefold()
        if folded in seen:
            _fail("DUPLICATE_PATH", raw)
        seen.add(folded)
        normalized.append(raw)
    return sorted(normalized, key=lambda item: (item.casefold(), item))


def _scan_public_clean(value: Any) -> None:
    text = value if isinstance(value, str) else canonical_json(value)
    for pattern in PROTECTED:
        if pattern.search(text):
            _fail("PROTECTED_BOUNDARY_FAILURE", "protected-looking content detected")


def _validate_sha40(value: Any, label: str, *, optional: bool = False) -> str | None:
    if value is None and optional:
        return None
    if not isinstance(value, str) or not SHA40.fullmatch(value):
        _fail("INVALID_GIT_IDENTITY", label)
    return value


def _branch(value: Any) -> str:
    if (
        not isinstance(value, str)
        or not value
        or not BRANCH.fullmatch(value)
        or value.startswith(('/', '.'))
        or value.endswith(('/', '.'))
        or ".." in value
        or "//" in value
    ):
        _fail("INVALID_BRANCH_INTENT", str(value))
    return value


def _mission_fields(mission: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(mission, Mapping):
        _fail("INVALID_MISSION", "mission must be an object")
    repository = mission.get("repository")
    issue_number = mission.get("issue_number")
    mission_id = mission.get("mission_id")
    attempt_id = mission.get("attempt_id")
    objective = mission.get("objective")
    if not isinstance(repository, str) or not REPOSITORY.fullmatch(repository):
        _fail("INVALID_MISSION", "repository")
    if type(issue_number) is not int or issue_number < 1:
        _fail("INVALID_MISSION", "issue_number")
    for label, value in (("mission_id", mission_id), ("attempt_id", attempt_id), ("objective", objective)):
        if not isinstance(value, str) or not value.strip():
            _fail("INVALID_MISSION", label)
    _scan_public_clean(mission)
    return {
        "repository": repository,
        "issue_number": issue_number,
        "mission_id": mission_id,
        "attempt_id": attempt_id,
        "objective_sha256": sha256_text(objective),
    }


def _candidate_entries(candidate_files: Mapping[str, bytes]) -> tuple[list[str], list[dict[str, Any]]]:
    if not isinstance(candidate_files, Mapping) or not candidate_files:
        _fail("EMPTY_CANDIDATE", "candidate files are required")
    paths = normalize_paths(candidate_files.keys())
    entries: list[dict[str, Any]] = []
    for path in paths:
        data = candidate_files[path]
        if not isinstance(data, bytes):
            _fail("INVALID_CANDIDATE_BYTES", path)
        _scan_public_clean(data.decode("utf-8", errors="ignore"))
        git_header = f"blob {len(data)}\0".encode("ascii")
        entries.append(
            {
                "path": path,
                "size": len(data),
                "content_sha256": hashlib.sha256(data).hexdigest(),
                "git_blob_sha1": hashlib.sha1(git_header + data).hexdigest(),
            }
        )
    return paths, entries


def _check_evidence(checks: Mapping[str, str]) -> list[dict[str, str]]:
    if not isinstance(checks, Mapping) or not checks:
        _fail("PREPUBLICATION_CHECKS_REQUIRED", "at least one PASS evidence binding is required")
    if any(not isinstance(name, str) for name in checks):
        _fail("INVALID_CHECK_EVIDENCE", "check names must be strings")
    result: list[dict[str, str]] = []
    for name in sorted(checks, key=lambda item: (item.casefold(), item)):
        digest = checks[name]
        if not isinstance(name, str) or not name.strip() or not isinstance(digest, str) or not SHA256.fullmatch(digest):
            _fail("INVALID_CHECK_EVIDENCE", str(name))
        result.append({"name": name, "status": "PASS", "evidence_sha256": digest})
    return result


def _seal_body(seal: Mapping[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in seal.items() if key not in {"seal_id", "seal_sha256"}}


def _verify_seal_digest(seal: Mapping[str, Any]) -> None:
    if not isinstance(seal, Mapping) or seal.get("schema_version") != "atlas.candidate-seal.v1":
        _fail("INVALID_SEAL", "schema_version")
    observed = seal.get("seal_sha256")
    expected = _sha256_json(_seal_body(seal))
    if not isinstance(observed, str) or observed != expected:
        _fail("SEAL_DIGEST_MISMATCH", "seal body changed")
    expected_id = f"{seal.get('mission_id')}:{seal.get('attempt_id')}:{expected[:16]}"
    if seal.get("seal_id") != expected_id:
        _fail("SEAL_ID_MISMATCH", "seal identity changed")


def build_candidate_seal(
    mission: Mapping[str, Any],
    *,
    canonical_base_sha: str,
    branch_intent: str,
    candidate_files: Mapping[str, bytes],
    expected_candidate_tree_sha: str,
    expected_head_sha: str | None,
    prepublication_checks: Mapping[str, str],
    authorizer: str,
    operator: str,
    route: str,
    generated_state: str,
) -> dict[str, Any]:
    identity = _mission_fields(mission)
    base = _validate_sha40(canonical_base_sha, "canonical_base_sha")
    tree = _validate_sha40(expected_candidate_tree_sha, "expected_candidate_tree_sha")
    head = _validate_sha40(expected_head_sha, "expected_head_sha", optional=True)
    branch = _branch(branch_intent)
    if generated_state not in GENERATED_STATES:
        _fail("INVALID_GENERATED_STATE", generated_state)
    for label, value in (("authorizer", authorizer), ("operator", operator), ("route", route)):
        if not isinstance(value, str) or not value.strip():
            _fail("INVALID_ACTOR_OR_ROUTE", label)
    paths, entries = _candidate_entries(candidate_files)
    checks = _check_evidence(prepublication_checks)
    body: dict[str, Any] = {
        "schema_version": "atlas.candidate-seal.v1",
        "seal_state": "SEALED_PREPUBLICATION",
        **identity,
        "canonical_base_sha": base,
        "branch_intent": branch,
        "authorizer": authorizer,
        "operator": operator,
        "route": route,
        "publisher_role": "READ_ONLY_SEAL_COMPILER",
        "generated_state": generated_state,
        "path_inventory": paths,
        "path_inventory_sha256": _sha256_json(paths),
        "candidate_entries": entries,
        "candidate_content_sha256": _sha256_json(entries),
        "expected_candidate_tree_sha": tree,
        "expected_head_sha": head,
        "prepublication_checks": checks,
        "prepublication_checks_sha256": _sha256_json(checks),
        "evidence_generation": 1,
        "invalidation_triggers": [
            "BASE_DRIFT",
            "BRANCH_DRIFT",
            "PATH_DRIFT",
            "BYTE_DRIFT",
            "TREE_DRIFT",
            "HEAD_DRIFT",
            "CHECK_EVIDENCE_DRIFT",
            "SEAL_REPLAY",
        ],
        "forbidden_actions": {
            "direct_main_write": False,
            "force_push": False,
            "automatic_ready": False,
            "automatic_merge": False,
            "workflow_dispatch": False,
            "repository_setting_mutation": False,
            "standing_authority": "NO",
        },
        "rollback": {
            "before_merge": "CLOSE_EXACT_DRAFT_AND_PRESERVE_EVIDENCE",
            "after_merge": "REVIEWED_REVERT_OR_REPAIR_FORWARD",
            "history_rewrite": False,
        },
    }
    digest = _sha256_json(body)
    seal = {
        **body,
        "seal_id": f"{identity['mission_id']}:{identity['attempt_id']}:{digest[:16]}",
        "seal_sha256": digest,
    }
    _scan_public_clean(seal)
    return seal


def verify_candidate_seal(
    seal: Mapping[str, Any],
    *,
    canonical_base_sha: str,
    branch_intent: str,
    candidate_files: Mapping[str, bytes],
    expected_candidate_tree_sha: str,
    expected_head_sha: str | None,
    prepublication_checks: Mapping[str, str],
    consumed_seal_ids: Iterable[str] = (),
) -> dict[str, Any]:
    _verify_seal_digest(seal)
    if seal["seal_id"] in set(consumed_seal_ids):
        _fail("SEAL_REPLAY", str(seal["seal_id"]))
    if seal.get("canonical_base_sha") != canonical_base_sha:
        _fail("STALE_BASE", canonical_base_sha)
    if seal.get("branch_intent") != branch_intent:
        _fail("BRANCH_DRIFT", branch_intent)
    paths, entries = _candidate_entries(candidate_files)
    if seal.get("path_inventory") != paths or seal.get("path_inventory_sha256") != _sha256_json(paths):
        _fail("PATH_DRIFT", "candidate path inventory changed")
    if seal.get("candidate_entries") != entries or seal.get("candidate_content_sha256") != _sha256_json(entries):
        _fail("BYTE_DRIFT", "candidate bytes changed")
    if seal.get("expected_candidate_tree_sha") != expected_candidate_tree_sha:
        _fail("TREE_DRIFT", expected_candidate_tree_sha)
    if seal.get("expected_head_sha") != expected_head_sha:
        _fail("HEAD_DRIFT", str(expected_head_sha))
    checks = _check_evidence(prepublication_checks)
    if seal.get("prepublication_checks") != checks or seal.get("prepublication_checks_sha256") != _sha256_json(checks):
        _fail("CHECK_EVIDENCE_DRIFT", "prepublication evidence changed")
    return {
        "schema_version": "atlas.candidate-seal-verification.v1",
        "status": "VERIFIED",
        "seal_id": seal["seal_id"],
        "seal_sha256": seal["seal_sha256"],
        "canonical_base_sha": canonical_base_sha,
        "branch_intent": branch_intent,
        "path_inventory_sha256": seal["path_inventory_sha256"],
        "candidate_content_sha256": seal["candidate_content_sha256"],
        "expected_candidate_tree_sha": expected_candidate_tree_sha,
        "expected_head_sha": expected_head_sha,
        "dependent_evidence_generation": seal["evidence_generation"],
    }


def reconcile_publication_state(seal: Mapping[str, Any], remote_state: Mapping[str, Any]) -> dict[str, Any]:
    _verify_seal_digest(seal)
    required = {"canonical_main_sha", "branch_head_sha", "pull_requests", "consumed_seal_ids"}
    if not isinstance(remote_state, Mapping) or set(remote_state) != required:
        _fail("UNKNOWN_REMOTE_STATE", "remote state fields are incomplete or unexpected")
    if remote_state["canonical_main_sha"] != seal["canonical_base_sha"]:
        _fail("STALE_BASE", str(remote_state["canonical_main_sha"]))
    consumed = remote_state["consumed_seal_ids"]
    if not isinstance(consumed, list) or any(not isinstance(item, str) for item in consumed):
        _fail("UNKNOWN_REMOTE_STATE", "consumed seal identities are malformed")
    if seal["seal_id"] in consumed:
        _fail("SEAL_REPLAY", str(seal["seal_id"]))
    expected_head = seal.get("expected_head_sha")
    if not isinstance(expected_head, str):
        _fail("HEAD_IDENTITY_REQUIRED", "remote reconciliation requires an expected head")
    branch_head = remote_state["branch_head_sha"]
    if branch_head is not None and (not isinstance(branch_head, str) or not SHA40.fullmatch(branch_head)):
        _fail("UNKNOWN_REMOTE_STATE", "branch head is malformed")
    pull_requests = remote_state["pull_requests"]
    if not isinstance(pull_requests, list):
        _fail("UNKNOWN_REMOTE_STATE", "pull_requests must be a list")
    if len(pull_requests) > 1:
        _fail("DUPLICATE_PULL_REQUEST", "multiple pull requests match the sealed branch")

    common = {
        "schema_version": "atlas.candidate-publication-reconciliation.v1",
        "seal_id": seal["seal_id"],
        "seal_sha256": seal["seal_sha256"],
        "canonical_main_sha": remote_state["canonical_main_sha"],
        "branch_intent": seal["branch_intent"],
        "expected_head_sha": expected_head,
        "blind_retry": False,
    }
    if branch_head is None and not pull_requests:
        return {
            **common,
            "status": "CLEAR",
            "remote_mutation_allowance": "CREATE_BRANCH_COMMIT_AND_DRAFT_PR_ONCE",
            "next_safe_action": "PUBLISH_EXACT_SEALED_CANDIDATE_ONCE",
        }
    if branch_head == expected_head and not pull_requests:
        return {
            **common,
            "status": "BLOCKED_RESUMABLE",
            "remote_mutation_allowance": "CREATE_DRAFT_PR_ONLY",
            "next_safe_action": "RESUME_EXACT_DRAFT_PR_CREATION_WITHOUT_REPUSH",
        }
    if branch_head == expected_head and len(pull_requests) == 1:
        pr = pull_requests[0]
        expected_pr_fields = {"number", "state", "draft", "base_sha", "head_sha", "branch"}
        if not isinstance(pr, Mapping) or set(pr) != expected_pr_fields:
            _fail("UNKNOWN_REMOTE_STATE", "pull request readback is malformed")
        if (
            type(pr["number"]) is not int
            or pr["number"] < 1
            or pr["state"] != "OPEN"
            or pr["draft"] is not True
            or pr["base_sha"] != seal["canonical_base_sha"]
            or pr["head_sha"] != expected_head
            or pr["branch"] != seal["branch_intent"]
        ):
            _fail("REMOTE_STATE_CONFLICT", "pull request does not match the seal")
        return {
            **common,
            "status": "PR_OPEN_RECONCILED",
            "pull_request": pr["number"],
            "remote_mutation_allowance": "NONE",
            "next_safe_action": "READBACK_VALIDATE_AND_REVIEW_EXACT_HEAD",
        }
    _fail("REMOTE_STATE_CONFLICT", "branch or pull request state does not match the seal")


def build_repair_batch(seal: Mapping[str, Any], findings: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    _verify_seal_digest(seal)
    if not isinstance(findings, Sequence) or isinstance(findings, (str, bytes)) or not findings:
        _fail("EMPTY_REPAIR_EVIDENCE", "readable findings are required")
    normalized: list[dict[str, Any]] = []
    seen: set[str] = set()
    actionable: list[str] = []
    for finding in findings:
        if not isinstance(finding, Mapping):
            _fail("MALFORMED_FINDING", "finding must be an object")
        required = {"finding_id", "source", "classification", "candidate_caused", "readable", "detail"}
        if set(finding) != required:
            _fail("MALFORMED_FINDING", "finding fields are incomplete or unexpected")
        finding_id = finding["finding_id"]
        classification = finding["classification"]
        if not isinstance(finding_id, str) or not finding_id.strip() or finding_id in seen:
            _fail("DUPLICATE_OR_INVALID_FINDING", str(finding_id))
        seen.add(finding_id)
        if classification not in REPAIR_CLASSIFICATIONS:
            _fail("UNKNOWN_FINDING_CLASSIFICATION", str(classification))
        if classification == "DECISION_REQUIRED":
            _fail("REPAIR_DECISION_REQUIRED", finding_id)
        if classification == "UNKNOWN":
            _fail("REPAIR_UNKNOWN_STATE", finding_id)
        if type(finding["candidate_caused"]) is not bool or type(finding["readable"]) is not bool:
            _fail("MALFORMED_FINDING", finding_id)
        if not isinstance(finding["source"], str) or not finding["source"].strip():
            _fail("MALFORMED_FINDING", finding_id)
        if not isinstance(finding["detail"], str) or not finding["detail"].strip():
            _fail("MALFORMED_FINDING", finding_id)
        _scan_public_clean(finding["detail"])
        if not finding["readable"] and classification != "UNAVAILABLE":
            _fail("UNREADABLE_FINDING_MISCLASSIFIED", finding_id)
        if classification == "ACTIONABLE":
            if not finding["readable"] or not finding["candidate_caused"]:
                _fail("ACTIONABLE_FINDING_OUT_OF_SCOPE", finding_id)
            actionable.append(finding_id)
        normalized.append(dict(finding))
    if not actionable:
        _fail("NO_CANDIDATE_REPAIR", "no candidate-caused actionable finding exists")
    normalized.sort(key=lambda item: item["finding_id"])
    actionable.sort()
    body = {
        "schema_version": "atlas.candidate-repair-batch.v1",
        "batch_state": "SEALED_REPAIR_BATCH",
        "repository": seal["repository"],
        "mission_id": seal["mission_id"],
        "attempt_id": seal["attempt_id"],
        "source_seal_id": seal["seal_id"],
        "source_seal_sha256": seal["seal_sha256"],
        "source_candidate_content_sha256": seal["candidate_content_sha256"],
        "findings": normalized,
        "findings_sha256": _sha256_json(normalized),
        "actionable_finding_ids": actionable,
        "publication_limit": "ONE_CONSOLIDATED_REPAIR",
        "replacement_seal_required": True,
        "invalidated_evidence": INVALIDATED_EVIDENCE,
        "preserve_partial_state": True,
        "blind_retry": False,
        "force_push": False,
        "next_safe_action": "APPLY_ALL_ACTIONABLE_FINDINGS_LOCALLY_THEN_CREATE_AND_VERIFY_ONE_REPLACEMENT_SEAL",
    }
    digest = _sha256_json(body)
    return {
        **body,
        "repair_batch_id": f"{seal['mission_id']}:{seal['attempt_id']}:repair:{digest[:16]}",
        "repair_batch_sha256": digest,
    }
