"""Deterministic, read-only Oathbringer carrier compiler.

This module intentionally has no GitHub mutation, git mutation, retry, merge,
or credential-storage function.  ``read_live_state`` uses only read-only
``gh api`` requests; all durable work is deterministic local compilation.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
import unicodedata
import zipfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Mapping, Sequence


COMPILER_IDENTITY = "SWORD_FORGE_COMPILER_V1"
FORMAT_VERSION = "1.0"
FORGE_STANDARD = "SWORD_FORGE_STANDARD_V1"
LESSONS_SCHEMA = "prime-sword-lessons-v1"
MAX_MEMBERS = 256
MAX_MEMBER_BYTES = 1_048_576
MAX_TOTAL_BYTES = 8_388_608
ZIP_EPOCH = (1980, 1, 1, 0, 0, 0)
REQUIRED_FORBIDDEN = {"DIRECT_MAIN", "FORCE_PUSH", "SCOPE_WIDENING", "TOKEN_PERSISTENCE"}
SENSITIVE = re.compile(
    r"(?:\bgh[pousr]_[A-Za-z0-9]{20,}\b|\bAKIA[0-9A-Z]{16}\b|"
    r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|"
    r"(?i:(?:api[_-]?key|access[_-]?token|password|secret)\s*[:=]\s*['\"][^'\"\r\n]{8,}['\"]))"
)


class FoundryError(RuntimeError):
    """A carrier cannot be safely compiled or verified."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise FoundryError(message)


def _pairs_no_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise FoundryError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_pairs_no_duplicates)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise FoundryError(f"invalid UTF-8 JSON: {path}") from exc
    _require(isinstance(value, dict), f"JSON root must be an object: {path}")
    return value


def canonical_json(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        .replace("\r\n", "\n")
        .replace("\r", "\n")
        .encode("utf-8")
        + b"\n"
    )


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def safe_path(value: Any, field: str) -> str:
    raw = str(value or "")
    _require(bool(raw), f"{field} must not be empty")
    _require(raw == unicodedata.normalize("NFC", raw), f"{field} must be Unicode NFC")
    _require("\\" not in raw and not raw.startswith("/") and not raw.startswith("//"), f"{field} must be a relative POSIX path")
    _require(not re.match(r"^[A-Za-z]:", raw), f"{field} must not be drive-qualified")
    parts = raw.split("/")
    _require(all(part and part not in {".", ".."} for part in parts), f"{field} contains an unsafe segment")
    normalized = PurePosixPath(raw).as_posix()
    _require(normalized == raw, f"{field} is not canonical")
    return normalized


def _safe_branch(value: Any, field: str) -> str:
    branch = str(value or "")
    _require(branch and not branch.startswith(("-", "/")), f"{field} is invalid")
    _require(".." not in branch and " " not in branch and "@{" not in branch and not branch.endswith((".", "/")), f"{field} is invalid")
    return branch


def _sha1(value: Any, field: str, *, nullable: bool = False) -> str | None:
    if value is None and nullable:
        return None
    text = str(value or "")
    _require(re.fullmatch(r"[0-9a-f]{40}", text) is not None, f"{field} must be a lowercase SHA-1")
    return text


def _sha256(value: Any, field: str) -> str:
    text = str(value or "")
    _require(re.fullmatch(r"[0-9a-f]{64}", text) is not None, f"{field} must be a lowercase SHA-256")
    return text


def _exact_keys(value: Mapping[str, Any], allowed: set[str], field: str) -> None:
    unknown = sorted(set(value) - allowed)
    _require(not unknown, f"{field} contains unknown fields: {unknown}")


def _regular_member(root: Path, relative: str, field: str) -> Path:
    path = (root / relative).resolve()
    _require(path == root.resolve() or root.resolve() in path.parents, f"{field} escapes its root")
    _require(path.is_file() and not path.is_symlink(), f"{field} must name a regular file")
    _require(path.stat().st_size <= MAX_MEMBER_BYTES, f"{field} exceeds the per-member limit")
    return path


def _scan_clean(data: bytes, field: str) -> None:
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise FoundryError(f"{field} is not UTF-8 clean text") from exc
    _require(SENSITIVE.search(text) is None, f"{field} contains protected or token-shaped material")


def _operation_paths(operations: Sequence[Mapping[str, Any]]) -> tuple[set[str], set[str]]:
    targets: set[str] = set()
    sources: set[str] = set()
    casefold: set[str] = set()
    for index, item in enumerate(operations):
        _require(isinstance(item, dict), f"operations[{index}] must be an object")
        _exact_keys(item, {"path", "operation", "payload_path", "payload_sha256", "source_path", "source_blob", "mode"}, f"operations[{index}]")
        path = safe_path(item.get("path"), f"operations[{index}].path")
        folded = path.casefold()
        _require(path not in targets and folded not in casefold, f"duplicate or case-fold target path: {path}")
        targets.add(path)
        casefold.add(folded)
        operation = str(item.get("operation") or "")
        _require(operation in {"ADD", "REPLACE", "DELETE", "RENAME", "MOVE"}, f"invalid operation for {path}")
        if operation in {"ADD", "REPLACE"} or item.get("payload_path") is not None:
            safe_path(item.get("payload_path"), f"operations[{index}].payload_path")
            _sha256(item.get("payload_sha256"), f"operations[{index}].payload_sha256")
        if operation in {"REPLACE", "DELETE", "RENAME", "MOVE"}:
            _sha1(item.get("source_blob"), f"operations[{index}].source_blob")
        if operation in {"RENAME", "MOVE"}:
            source = safe_path(item.get("source_path"), f"operations[{index}].source_path")
            _require(source != path and source not in sources and source.casefold() not in casefold, f"invalid move source: {source}")
            sources.add(source)
    return targets, sources


def _load_lessons(source_root: Path) -> list[str]:
    lessons = load_json(source_root / "methods" / "sword-lessons.json")
    _require(lessons.get("schema_version") == LESSONS_SCHEMA, "unexpected lessons register schema")
    result = [str(item.get("lesson_id") or "") for item in lessons.get("lessons", []) if isinstance(item, dict)]
    _require(result and len(result) == len(set(result)), "lessons register is malformed")
    return result


def validate_mission(mission: Mapping[str, Any], source_root: Path) -> None:
    _exact_keys(mission, {"format_version", "compiler_identity", "mode", "mission_id", "revision", "authority", "source_lock", "target_lock", "operations", "lesson_applicability", "privacy_classification", "stop_boundary", "rollback", "oathbringer_mission"}, "foundry mission")
    required = {"format_version", "compiler_identity", "mode", "mission_id", "revision", "authority", "source_lock", "target_lock", "operations", "lesson_applicability", "privacy_classification", "stop_boundary", "rollback", "oathbringer_mission"}
    _require(required <= set(mission), f"foundry mission is missing: {sorted(required - set(mission))}")
    _require(mission["format_version"] == FORMAT_VERSION, f"format_version must be {FORMAT_VERSION}")
    _require(mission["compiler_identity"] == COMPILER_IDENTITY, f"compiler_identity must be {COMPILER_IDENTITY}")
    mode = str(mission["mode"])
    _require(mode in {"BUILD", "REPAIR", "RECOVERY", "EXECUTE"}, "mode is invalid")
    _require(re.fullmatch(r"[A-Za-z0-9._-]+", str(mission["mission_id"])) is not None, "mission_id is unsafe")
    _require(re.fullmatch(r"R[0-9]{2,}", str(mission["revision"])) is not None, "revision is invalid")
    _require(mission["privacy_classification"] == "PUBLIC_CLEAN", "carrier inputs must be PUBLIC_CLEAN")
    _require(bool(str(mission["stop_boundary"]).strip()) and bool(str(mission["rollback"]).strip()), "stop boundary and rollback are required")

    authority = mission["authority"]
    _require(isinstance(authority, dict), "authority must be an object")
    _exact_keys(authority, {"authorizer", "operator", "repository", "execution_authorized", "merge_authorized"}, "authority")
    _require(str(authority.get("authorizer") or "").upper() == "JAYSON", "authorizer must be JAYSON")
    _require(str(authority.get("operator") or "").upper() == "JAYSON", "operator must be JAYSON")
    _require(re.fullmatch(r"[^/\s]+/[^/\s]+", str(authority.get("repository") or "")) is not None, "authority.repository is invalid")
    _require(authority.get("execution_authorized") is True, "execution authorization is required to forge a sealed carrier")
    _require(authority.get("merge_authorized") is False, "Foundry cannot carry standing merge authority")

    source_lock = mission["source_lock"]
    _require(isinstance(source_lock, dict), "source_lock must be an object")
    _exact_keys(source_lock, {"base_branch", "expected_base", "expected_head", "workflow_sources", "source_paths"}, "source_lock")
    _safe_branch(source_lock.get("base_branch"), "source_lock.base_branch")
    _sha1(source_lock.get("expected_base"), "source_lock.expected_base")
    expected_head = _sha1(source_lock.get("expected_head"), "source_lock.expected_head", nullable=True)
    _require(isinstance(source_lock.get("workflow_sources"), list), "workflow_sources must be an array")
    workflow_paths: set[str] = set()
    for index, item in enumerate(source_lock["workflow_sources"]):
        _require(isinstance(item, dict), f"workflow_sources[{index}] must be an object")
        _exact_keys(item, {"path", "blob"}, f"workflow_sources[{index}]")
        path = safe_path(item.get("path"), f"workflow_sources[{index}].path")
        _require(path.startswith(".github/workflows/"), "workflow source must be under .github/workflows")
        _require(path not in workflow_paths, f"duplicate workflow source: {path}")
        workflow_paths.add(path)
        _sha1(item.get("blob"), f"workflow_sources[{index}].blob")
    _require(isinstance(source_lock.get("source_paths"), list) and source_lock["source_paths"], "source_paths must be non-empty")
    source_paths: set[str] = set()
    for index, item in enumerate(source_lock["source_paths"]):
        _require(isinstance(item, dict), f"source_paths[{index}] must be an object")
        _exact_keys(item, {"path", "sha256"}, f"source_paths[{index}]")
        path = safe_path(item.get("path"), f"source_paths[{index}].path")
        _require(path not in source_paths, f"duplicate source path: {path}")
        source_paths.add(path)
        _sha256(item.get("sha256"), f"source_paths[{index}].sha256")
    _require("methods/sword-lessons.json" in source_paths, "source lock must bind the lessons register")

    target_lock = mission["target_lock"]
    _require(isinstance(target_lock, dict), "target_lock must be an object")
    _exact_keys(target_lock, {"branch", "pull_request"}, "target_lock")
    _safe_branch(target_lock.get("branch"), "target_lock.branch")
    pull_request = target_lock.get("pull_request")
    if mode == "BUILD":
        _require(expected_head is None and pull_request is None, "BUILD must not bind an existing PR head")
    else:
        _require(expected_head is not None and isinstance(pull_request, int) and pull_request >= 1, f"{mode} requires an exact head and pull request")

    operations = mission["operations"]
    _require(isinstance(operations, list), "operations must be an array")
    if mode in {"BUILD", "REPAIR"}:
        _require(bool(operations), f"{mode} requires operations")
    _operation_paths(operations)

    lessons = mission["lesson_applicability"]
    _require(isinstance(lessons, list), "lesson_applicability must be an array")
    expected_lessons = _load_lessons(source_root)
    seen_lessons: set[str] = set()
    for index, item in enumerate(lessons):
        _require(isinstance(item, dict), f"lesson_applicability[{index}] must be an object")
        _exact_keys(item, {"lesson_id", "status", "reason"}, f"lesson_applicability[{index}]")
        lesson_id = str(item.get("lesson_id") or "")
        _require(lesson_id in expected_lessons and lesson_id not in seen_lessons, f"unknown or duplicate lesson: {lesson_id}")
        seen_lessons.add(lesson_id)
        status = item.get("status")
        _require(status in {"APPLIED", "NOT_APPLICABLE"}, f"invalid lesson status: {lesson_id}")
        if status == "NOT_APPLICABLE":
            _require(bool(str(item.get("reason") or "").strip()), f"not-applicable lesson requires a reason: {lesson_id}")
    _require(seen_lessons == set(expected_lessons), "every controlling lesson must be classified")

    oathbringer = mission["oathbringer_mission"]
    if mode == "RECOVERY":
        _require(oathbringer is None, "RECOVERY must not pretend to have a current Oathbringer executor lane")
    else:
        _require(isinstance(oathbringer, dict), f"{mode} requires an Oathbringer mission")
        _validate_oathbringer_binding(mission, oathbringer)


def _validate_oathbringer_binding(mission: Mapping[str, Any], oathbringer: Mapping[str, Any]) -> None:
    mode = str(mission["mode"])
    source_lock = mission["source_lock"]
    target_lock = mission["target_lock"]
    _require(oathbringer.get("format_version") == "2.0", "embedded Oathbringer mission must be production format 2.0")
    _require(oathbringer.get("forge_standard") == FORGE_STANDARD, "embedded Oathbringer mission has the wrong Forge Standard")
    _require(oathbringer.get("lane") == mode, "embedded Oathbringer lane disagrees with Foundry mode")
    _require(oathbringer.get("repository") == mission["authority"]["repository"], "embedded Oathbringer repository disagrees with authority")
    _require(oathbringer.get("base_branch") == source_lock["base_branch"], "embedded Oathbringer base branch disagrees")
    _require(oathbringer.get("expected_base") == source_lock["expected_base"], "embedded Oathbringer base disagrees")
    _require(oathbringer.get("expected_head") == source_lock["expected_head"], "embedded Oathbringer head disagrees")
    _require(oathbringer.get("branch") == target_lock["branch"], "embedded Oathbringer branch disagrees")
    _require(oathbringer.get("pull_request") == target_lock["pull_request"], "embedded Oathbringer PR disagrees")
    _require(oathbringer.get("package_manifest_required") is True, "embedded Oathbringer mission must require a manifest")
    _require(set(oathbringer.get("forbidden_actions") or []) >= REQUIRED_FORBIDDEN, "embedded Oathbringer forbidden actions are incomplete")
    embedded = oathbringer.get("declared_paths")
    _require(isinstance(embedded, list), "embedded Oathbringer declared_paths must be an array")
    _require(canonical_json(embedded) == canonical_json(mission["operations"]), "embedded Oathbringer operations disagree with Foundry inventory")
    lessons = oathbringer.get("lessons_register")
    _require(isinstance(lessons, dict) and lessons.get("path") == "source/methods/sword-lessons.json", "embedded Oathbringer lessons path is unbound")


def bind_live_state(mission: Mapping[str, Any], live_state: Mapping[str, Any], source_root: Path) -> dict[str, Any]:
    """Validate a read-only snapshot against every carrier lock."""

    validate_mission(mission, source_root)
    _require(isinstance(live_state, dict), "live state must be an object")
    _exact_keys(live_state, {"repository", "base_branch", "base_sha", "head_sha", "pull_request", "github_login", "workflow_blobs"}, "live state")
    authority = mission["authority"]
    source_lock = mission["source_lock"]
    target_lock = mission["target_lock"]
    _require(live_state.get("repository") == authority["repository"], "live repository drift")
    _require(live_state.get("base_branch") == source_lock["base_branch"], "live base branch drift")
    _require(live_state.get("base_sha") == source_lock["expected_base"], "live base SHA drift")
    _require(re.fullmatch(r"[A-Za-z0-9-]+", str(live_state.get("github_login") or "")) is not None, "live GitHub identity is invalid")
    if mission["mode"] != "BUILD":
        _require(live_state.get("head_sha") == source_lock["expected_head"], "live pull-request head drift")
        _require(live_state.get("pull_request") == target_lock["pull_request"], "live pull-request identity drift")
    workflow_blobs = live_state.get("workflow_blobs")
    _require(isinstance(workflow_blobs, dict), "live workflow blobs must be an object")
    for item in source_lock["workflow_sources"]:
        _require(workflow_blobs.get(item["path"]) == item["blob"], f"workflow source drift: {item['path']}")
    for item in source_lock["source_paths"]:
        path = _regular_member(source_root, item["path"], f"source path {item['path']}")
        _require(sha256(path.read_bytes()) == item["sha256"], f"source hash drift: {item['path']}")
    return json.loads(canonical_json(dict(live_state)).decode("utf-8"))


def _gh_json(path: str) -> Any:
    result = subprocess.run(["gh", "api", path], check=False, capture_output=True, text=True, encoding="utf-8")
    if result.returncode != 0:
        detail = " ".join((result.stderr or result.stdout or "gh read failed").split())[:500]
        raise FoundryError(f"read-only GitHub binding failed: {detail}")
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise FoundryError("read-only GitHub binding returned invalid JSON") from exc


def read_live_state(mission: Mapping[str, Any]) -> dict[str, Any]:
    """Obtain a fresh snapshot through read-only GitHub CLI API calls only."""

    source_lock = mission["source_lock"]
    target_lock = mission["target_lock"]
    repository = str(mission["authority"]["repository"])
    base_ref = _gh_json(f"repos/{repository}/git/ref/heads/{source_lock['base_branch']}")
    user = _gh_json("user")
    workflows: dict[str, str] = {}
    for item in source_lock["workflow_sources"]:
        content = _gh_json(f"repos/{repository}/contents/{item['path']}?ref={source_lock['expected_base']}")
        workflows[item["path"]] = str(content.get("sha") or "")
    snapshot: dict[str, Any] = {
        "repository": repository,
        "base_branch": source_lock["base_branch"],
        "base_sha": str(base_ref.get("object", {}).get("sha") or ""),
        "head_sha": None,
        "pull_request": None,
        "github_login": str(user.get("login") or ""),
        "workflow_blobs": workflows,
    }
    if mission["mode"] != "BUILD":
        pull = _gh_json(f"repos/{repository}/pulls/{target_lock['pull_request']}")
        snapshot["head_sha"] = str(pull.get("head", {}).get("sha") or "")
        snapshot["pull_request"] = int(pull.get("number") or 0)
    return snapshot


def _material_entry(path: str, data: bytes) -> dict[str, Any]:
    return {"path": path, "sha256": sha256(data), "size": len(data)}


def _carrier_launcher() -> bytes:
    return b'''[CmdletBinding()]\nparam(\n    [string]$ReceiptPath = (Join-Path $PSScriptRoot '..\\oathbringer.receipt.json'),\n    [switch]$Json\n)\n$ErrorActionPreference = 'Stop'\n$root = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path\n$runner = Join-Path $root 'engine\\Invoke-AtlasSword.ps1'\n$args = @('-MissionPath', (Join-Path $root 'oathbringer-mission.json'), '-ReceiptPath', $ReceiptPath)\nif ($Json) { $args += '-Json' }\n& $runner @args\nexit $LASTEXITCODE\n'''


def _read_input_payloads(mission: Mapping[str, Any], input_root: Path) -> dict[str, bytes]:
    materials: dict[str, bytes] = {}
    total = 0
    for index, item in enumerate(mission["operations"]):
        payload_path = item.get("payload_path")
        if payload_path is None:
            continue
        relative = safe_path(payload_path, f"operations[{index}].payload_path")
        source = _regular_member(input_root, relative, f"payload {relative}")
        data = source.read_bytes()
        total += len(data)
        _require(total <= MAX_TOTAL_BYTES, "payload total exceeds the carrier limit")
        _scan_clean(data, f"payload {relative}")
        _require(sha256(data) == item["payload_sha256"], f"payload hash mismatch: {relative}")
        _require(relative not in materials, f"duplicate payload path: {relative}")
        materials[relative] = data
    return materials


def _engine_materials(source_root: Path) -> dict[str, bytes]:
    engine_root = source_root / "tools" / "atlas-sword" / "engine"
    _require(engine_root.is_dir(), "current Oathbringer engine is missing")
    result: dict[str, bytes] = {}
    for path in sorted(engine_root.iterdir(), key=lambda item: item.name):
        if not path.is_file() or path.is_symlink() or path.suffix not in {".py", ".ps1", ".psm1"}:
            continue
        relative = f"engine/{path.name}"
        data = path.read_bytes()
        _scan_clean(data, f"transport {relative}")
        result[relative] = data
    _require("engine/Invoke-AtlasSword.ps1" in result and "engine/oathbringer_github.py" in result, "current Oathbringer transport is incomplete")
    return result


def _deterministic_zip(destination: Path, members: Mapping[str, bytes]) -> None:
    _require(len(members) <= MAX_MEMBERS, "carrier member limit exceeded")
    total = sum(len(value) for value in members.values())
    _require(total <= MAX_TOTAL_BYTES, "carrier total limit exceeded")
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_STORED, strict_timestamps=True) as archive:
        for name in sorted(members):
            safe_path(name, "carrier member")
            data = members[name]
            _require(len(data) <= MAX_MEMBER_BYTES, f"carrier member exceeds limit: {name}")
            info = zipfile.ZipInfo(name, date_time=ZIP_EPOCH)
            info.compress_type = zipfile.ZIP_STORED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data)


@dataclass(frozen=True)
class CarrierResult:
    carrier_path: Path
    carrier_sha256: str
    manifest_sha256: str
    forge_receipt_sha256: str
    member_count: int
    bound_live_state_sha256: str


def compile_carrier(
    mission: Mapping[str, Any],
    *,
    input_root: Path,
    source_root: Path,
    output_dir: Path,
    live_state: Mapping[str, Any],
    seen_mission_ids: Iterable[str] = (),
) -> CarrierResult:
    """Compile exactly one deterministic carrier without external mutation."""

    mission_id = str(mission.get("mission_id") or "")
    _require(mission_id not in set(seen_mission_ids), f"replayed mission identity: {mission_id}")
    bound = bind_live_state(mission, live_state, source_root)
    input_root = input_root.resolve()
    source_root = source_root.resolve()
    output_dir = output_dir.resolve()
    _require(input_root.is_dir() and source_root.is_dir(), "input and source roots must exist")

    members: dict[str, bytes] = {}
    members["foundry-mission.json"] = canonical_json(mission)
    members["AUTHORITY.json"] = canonical_json(mission["authority"])
    members["SOURCE-LOCK.json"] = canonical_json(mission["source_lock"])
    members["TARGET-LOCK.json"] = canonical_json(mission["target_lock"])
    members["OPERATIONS.json"] = canonical_json(mission["operations"])
    members["LIVE-STATE.json"] = canonical_json(bound)
    members["launcher/Invoke-OathbringerCarrier.ps1"] = _carrier_launcher()
    members["RECOVERY.md"] = (
        "# Oathbringer Foundry Recovery\n\n"
        "This carrier is immutable evidence. Read the exact receipt, remote state, and stop boundary before any new mission. "
        "Do not retry, roll back, delete, ready, or merge automatically.\n"
    ).encode("utf-8")
    members["TEST-CONTRACT.md"] = (
        "# Carrier Test Contract\n\n"
        "Verify the ZIP manifest, SHA256SUMS, source/target locks, payload bytes, current-directory-independent launcher, and applicable Oathbringer tests before operator delivery.\n"
    ).encode("utf-8")
    members["DEFLECTED-SWORD-CONFIG.json"] = canonical_json(
        {"automatic_retry": False, "automatic_rollback": False, "automatic_ready": False, "automatic_merge": False, "sanitized_evidence_only": True}
    )
    members["source/methods/sword-lessons.json"] = _regular_member(source_root, "methods/sword-lessons.json", "lessons register").read_bytes()
    members.update(_engine_materials(source_root))
    members.update(_read_input_payloads(mission, input_root))

    oathbringer = mission["oathbringer_mission"]
    if isinstance(oathbringer, dict):
        members["oathbringer-mission.json"] = canonical_json(oathbringer)
        audit = oathbringer.get("independent_audit")
        if isinstance(audit, dict):
            audit_path = safe_path(audit.get("receipt_path"), "independent audit receipt")
            audit_file = _regular_member(input_root, audit_path, "independent audit receipt")
            audit_bytes = audit_file.read_bytes()
            _scan_clean(audit_bytes, "independent audit receipt")
            _require(sha256(audit_bytes) == audit.get("receipt_sha256"), "independent audit hash mismatch")
            members[audit_path] = audit_bytes

    receipt = {
        "receipt_version": "1.0",
        "compiler_identity": COMPILER_IDENTITY,
        "forge_standard": FORGE_STANDARD,
        "mission_id": mission["mission_id"],
        "revision": mission["revision"],
        "mode": mission["mode"],
        "repository": mission["authority"]["repository"],
        "source_lock": mission["source_lock"],
        "target_lock": mission["target_lock"],
        "lesson_applicability": mission["lesson_applicability"],
        "live_state_sha256": sha256(canonical_json(bound)),
        "compiler_is_writer": False,
        "automatic_retry": False,
        "automatic_rollback": False,
        "automatic_ready": False,
        "automatic_merge": False,
    }
    members["FORGE-RECEIPT.json"] = canonical_json(receipt)
    members["README-FIRST.md"] = (
        "# Oathbringer Foundry Carrier\n\n"
        f"Mission: `{mission['mission_id']}`  \nMode: `{mission['mode']}`  \n"
        "This is a deterministic, sealed carrier. Verify MANIFEST.json and SHA256SUMS.txt before operator use. "
        "The carrier grants no new authority and never auto-retries, rolls back, readies, or merges.\n"
    ).encode("utf-8")

    manifest = {"format_version": "1.0", "files": [_material_entry(path, members[path]) for path in sorted(members)]}
    members["MANIFEST.json"] = canonical_json(manifest)
    checksums = "".join(f"{sha256(members[path])}  {path}\n" for path in sorted(members))
    members["SHA256SUMS.txt"] = checksums.encode("ascii")

    safe_mission = re.sub(r"[^A-Za-z0-9._-]+", "-", str(mission["mission_id"])).strip("-.")
    filename = f"Oathbringer-Foundry-{safe_mission}-{mission['revision']}.zip"
    carrier = output_dir / filename
    _deterministic_zip(carrier, members)
    verification = verify_carrier(carrier)
    sidecar = carrier.with_suffix(carrier.suffix + ".sha256")
    sidecar.write_text(f"{verification['carrier_sha256']}  {carrier.name}\n", encoding="ascii", newline="\n")
    return CarrierResult(
        carrier_path=carrier,
        carrier_sha256=verification["carrier_sha256"],
        manifest_sha256=sha256(members["MANIFEST.json"]),
        forge_receipt_sha256=sha256(members["FORGE-RECEIPT.json"]),
        member_count=verification["member_count"],
        bound_live_state_sha256=sha256(canonical_json(bound)),
    )


def verify_carrier(carrier: Path) -> dict[str, Any]:
    carrier = carrier.resolve()
    _require(carrier.is_file(), "carrier is missing")
    with zipfile.ZipFile(carrier, "r") as archive:
        infos = archive.infolist()
        _require(0 < len(infos) <= MAX_MEMBERS, "carrier member count is unsafe")
        names: set[str] = set()
        total = 0
        for info in infos:
            name = safe_path(info.filename, "carrier archive path")
            _require(name not in names, f"duplicate carrier member: {name}")
            names.add(name)
            _require(not info.is_dir(), "carrier must not contain directory entries")
            _require(info.file_size <= MAX_MEMBER_BYTES, f"carrier member exceeds limit: {name}")
            _require(info.compress_size == info.file_size, f"carrier compression policy drift: {name}")
            total += info.file_size
        _require(total <= MAX_TOTAL_BYTES, "carrier total exceeds limit")
        _require("MANIFEST.json" in names and "SHA256SUMS.txt" in names and "FORGE-RECEIPT.json" in names, "carrier control members are missing")
        manifest = json.loads(archive.read("MANIFEST.json").decode("utf-8"), object_pairs_hook=_pairs_no_duplicates)
        entries = manifest.get("files")
        _require(isinstance(entries, list) and entries, "carrier manifest is malformed")
        declared = {str(item.get("path")): item for item in entries if isinstance(item, dict)}
        _require(len(declared) == len(entries), "carrier manifest has duplicate or malformed entries")
        for path, entry in declared.items():
            safe_path(path, "carrier manifest path")
            _require(path in names, f"manifest member missing from carrier: {path}")
            data = archive.read(path)
            _require(len(data) == int(entry.get("size")), f"manifest size mismatch: {path}")
            _require(sha256(data) == entry.get("sha256"), f"manifest hash mismatch: {path}")
        sums = archive.read("SHA256SUMS.txt").decode("ascii")
        for line in sums.splitlines():
            digest, path = line.split("  ", 1)
            _require(path in names and sha256(archive.read(path)) == digest, f"checksum mismatch: {path}")
    return {"carrier_sha256": sha256(carrier.read_bytes()), "member_count": len(infos), "status": "PASS"}
