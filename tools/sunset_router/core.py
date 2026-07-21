from __future__ import annotations

import base64
import hashlib
import re
import tempfile
import unicodedata
from pathlib import Path, PurePosixPath
from typing import Any

from tools.atlas_lifecycle.errors import LifecycleError
from tools.atlas_lifecycle.jsonio import canonical_bytes, load_bounded, read_bounded
from tools.atlas_lifecycle.protection import enforce_clean_values, enforce_pointer_contract
from tools.atlas_lifecycle.repository import observed_head
from tools.atlas_lifecycle.schema import SchemaValidator
from tools.atlas_lifecycle.sunset_preview import (
    BOUND_REQUEST,
    generate_approved_sunset_candidate,
    generate_sunset_approval,
    generate_sunset_preview,
    verify_approved_sunset_candidate,
    verify_sunset_approval,
    verify_sunset_preview,
)

ROUTER_PLAN = "sunset-router-plan.json"
ROUTER_RECEIPT = "sunset-router-receipt.json"
PREVIEW_DIR, APPROVAL_DIR, CANDIDATE_DIR = "preview", "approval", "lifecycle-candidate"
ATHENA_ROUTES = (
    "ATHENA_SPEAR_THREAD_ENGINE",
    "ATHENA_PHOENIX_BLADE",
    "ATHENA_AEGIS_BREAK",
)
JAYSON_ROUTES = ("JAYSON_ARROW_BOW_THREAD_ENGINE", "JAYSON_OATHBRINGER_SWORD")
DELEGATED_ROUTES = ("DELEGATED_ARROW_BOW_THREAD_ENGINE",)
TRANSFER_STOP = "OPERATOR_TRANSFER_REQUIRED"
DRIVE_PATH = re.compile(r"^[A-Za-z]:/")
SHA40 = re.compile(r"^[a-f0-9]{40}$")


def _fail(code: str, message: str) -> None:
    raise LifecycleError(code, message)


def _digest(data: bytes) -> str:
    return f"sha256:{hashlib.sha256(data).hexdigest()}"


def _stable_id(prefix: str, value: Any) -> str:
    token = base64.b32encode(hashlib.sha256(canonical_bytes(value)).digest()).decode()
    return f"{prefix}-{token.rstrip('=')[:26]}"


def _read(path: Path, code: str) -> dict[str, Any]:
    value = load_bounded(path)
    if read_bounded(path) != canonical_bytes(value):
        _fail(code, f"{path.name} must use canonical JSON bytes")
    return value


def _write(path: Path, value: dict[str, Any]) -> None:
    if path.exists() or path.is_symlink():
        _fail("SUNSET_ROUTER_OUTPUT_EXISTS", "router artifact already exists")
    path.write_bytes(canonical_bytes(value))


def _output(root: Path, output_dir: Path) -> Path:
    destination, repository = output_dir.resolve(), root.resolve()
    temporary = Path(tempfile.gettempdir()).resolve()
    if destination == repository or repository in destination.parents:
        _fail("SUNSET_ROUTER_OUTPUT_SCOPE", "router output cannot be inside the repository")
    if temporary != destination and temporary not in destination.parents:
        _fail("SUNSET_ROUTER_OUTPUT_SCOPE", "router output must be in system temporary storage")
    if output_dir.exists() or output_dir.is_symlink():
        _fail("SUNSET_ROUTER_OUTPUT_EXISTS", "router output must be a new directory")
    destination.mkdir(parents=True, exist_ok=False)
    return destination


def _slug(prefix: str, value: str) -> str:
    return f"{prefix}-{re.sub(r'[^a-z0-9]+', '-', value.casefold()).strip('-')}"


def _project_ids(root: Path) -> set[str]:
    pattern = re.compile(r"^\d+\.\s+\*\*(.+?)\*\*\s+—")
    values = {
        _slug("project", match.group(1))
        for line in (root / "projects/project-registry.md").read_text(encoding="utf-8").splitlines()
        if (match := pattern.match(line))
    }
    if not values:
        _fail("SUNSET_ROUTER_PROJECT_REGISTRY", "canonical Project registry is unreadable")
    return values


def _operation_ids(root: Path) -> dict[str, set[str]]:
    values: dict[str, set[str]] = {}
    for line in (root / "operations/operation-registry.md").read_text(encoding="utf-8").splitlines():
        if not line.startswith("|") or line.startswith("|---") or "Durable operations" in line:
            continue
        cells = [item.strip() for item in line.strip().strip("|").split("|")]
        if len(cells) == 2 and all(cells):
            values[_slug("project", cells[0])] = {
                _slug("operation", item.strip()) for item in cells[1].split(";") if item.strip()
            }
    if not values:
        _fail("SUNSET_ROUTER_OPERATION_REGISTRY", "canonical Operation registry is unreadable")
    return values


def _ownership(root: Path, request: dict[str, Any]) -> None:
    project_id, operation_id = request["project_id"], request["operation_id"]
    if project_id not in _project_ids(root):
        _fail("SUNSET_ROUTER_PROJECT_IDENTITY", "request Project does not resolve canonically")
    if operation_id not in _operation_ids(root).get(project_id, set()):
        _fail("SUNSET_ROUTER_OPERATION_IDENTITY", "request Operation does not belong to Project")
    scope = request["quest_scope"]
    if scope["scope_type"] == "NON_QUEST":
        return
    if scope["scope_type"] != "ADMITTED_QUEST":
        _fail("SUNSET_ROUTER_QUEST_IDENTITY", "router accepts admitted-Quest or non-Quest scope")
    source = f"quests/{scope['quest_id']}.md"
    board = load_bounded(root / "quest-board/quest-board-v1.json")
    admitted = any(isinstance(item, dict) and item.get("source") == source for item in board["entries"])
    if not admitted or not (root / source).is_file():
        _fail("SUNSET_ROUTER_QUEST_IDENTITY", "request Quest is not canonically admitted")


def _routes(request: dict[str, Any]) -> tuple[str, list[str]]:
    actor, requested = request["actor"], request["requested_route"]
    if actor == "ATHENA":
        if requested == "AUTO":
            return ATHENA_ROUTES[0], list(ATHENA_ROUTES[1:])
        if requested not in ATHENA_ROUTES:
            _fail("SUNSET_ROUTER_ROUTE_IDENTITY", "Athena may select only an Athena route")
        return requested, [item for item in ATHENA_ROUTES if item != requested]
    allowed = JAYSON_ROUTES if actor == "JAYSON" else DELEGATED_ROUTES
    if requested == "AUTO" or not request["operator_transfer_authorized"]:
        _fail("OPERATOR_TRANSFER_REQUIRED", "non-Athena routes require explicit transfer and route")
    if requested not in allowed:
        _fail("SUNSET_ROUTER_ROUTE_IDENTITY", "route does not match declared actor")
    return requested, [TRANSFER_STOP]


def normalize_record_paths(paths: list[str]) -> list[str]:
    normalized, seen = [], set()
    for raw in paths:
        if not isinstance(raw, str) or not raw:
            _fail("SUNSET_ROUTER_PATH", "candidate paths must be nonempty text")
        text = unicodedata.normalize("NFC", raw.replace("\\", "/"))
        pure = PurePosixPath(text)
        if (
            pure.is_absolute()
            or text.startswith("/")
            or DRIVE_PATH.match(text)
            or ".." in pure.parts
            or text != pure.as_posix()
            or not text.startswith("lifecycle/")
        ):
            _fail("SUNSET_ROUTER_PATH", "candidate path is unsafe or outside lifecycle")
        folded = text.casefold()
        if folded in seen:
            _fail("SUNSET_ROUTER_PATH_COLLISION", "candidate paths collide after case folding")
        seen.add(folded)
        normalized.append(text)
    return sorted(normalized, key=lambda item: (item.casefold(), item))


def _validator(root: Path) -> SchemaValidator:
    return SchemaValidator(root / "lifecycle/schemas")


def _validate_request(root: Path, path: Path) -> tuple[dict[str, Any], bytes]:
    request = _read(path, "SUNSET_ROUTER_REQUEST_CANONICAL")
    validator = _validator(root)
    validator.validate_sunset_router_request(request)
    enforce_clean_values(request)
    enforce_pointer_contract(request)
    lifecycle_request = request["lifecycle_request"]
    validator.validate_sunset_request(lifecycle_request)
    if lifecycle_request["expected_main_sha"] != observed_head(root):
        _fail("STALE_STATE", "router request does not match current canonical main")
    _ownership(root, lifecycle_request)
    return request, canonical_bytes(request)


def _validate_plan(root: Path, plan: dict[str, Any]) -> None:
    _validator(root).validate_sunset_router_plan(plan)
    enforce_clean_values(plan)
    enforce_pointer_contract(plan)


def _validate_receipt(root: Path, receipt: dict[str, Any]) -> None:
    _validator(root).validate_sunset_router_receipt(receipt)
    enforce_clean_values(receipt)
    enforce_pointer_contract(receipt)


def _receipt(plan: dict[str, Any], *, phase: str, state: str, **bindings: Any) -> dict[str, Any]:
    values = {
        "approval_id": plan["approval_id"],
        "candidate_set_digest": plan["candidate_set_digest"],
        "changed_paths_digest": plan["changed_paths_digest"],
        "expected_head": None,
        "pull_request": None,
        "merged_commit": None,
        "canonical_readback": False,
        "reason_code": None,
    }
    values.update(bindings)
    seed = {"plan_id": plan["plan_id"], "phase": phase, "state": state, **values}
    return {
        "schema_id": "atlas.sunset-router.receipt",
        "schema_version": "1.0.0",
        "receipt_id": _stable_id("SRR", seed),
        "authority": "READ_ONLY_RECEIPT",
        "plan_id": plan["plan_id"],
        "phase": phase,
        "state": state,
        "request_digest": plan["request_digest"],
        "plan_digest": _digest(canonical_bytes(plan)),
        "preview_id": plan["preview_id"],
        "preview_digest": plan["preview_digest"],
        **values,
        "next_safe_action": bindings["next_safe_action"],
    }


def generate_router_preview(repo_root: Path, request_path: Path, output_dir: Path) -> dict[str, Any]:
    root = repo_root.resolve()
    request, request_bytes = _validate_request(root, request_path)
    selected, fallbacks = _routes(request)
    destination = _output(root, output_dir)
    with tempfile.TemporaryDirectory() as temp:
        lifecycle_path = Path(temp) / "sunset-request-v2.json"
        lifecycle_path.write_bytes(canonical_bytes(request["lifecycle_request"]))
        preview = generate_sunset_preview(
            root, lifecycle_path, destination / PREVIEW_DIR,
            selected_route=selected, fallback_routes=fallbacks,
        )
    plan = {
        "schema_id": "atlas.sunset-router.plan",
        "schema_version": "1.0.0",
        "plan_id": _stable_id("SRP", {
            "request_digest": _digest(request_bytes),
            "preview_id": preview["preview_id"],
            "selected_route": selected,
        }),
        "authority": "ROUTE_PLAN_ONLY",
        "phase": "PREVIEW",
        "repository": "Jktomy/atlas-prime",
        "request_digest": _digest(request_bytes),
        "expected_main_sha": request["lifecycle_request"]["expected_main_sha"],
        "project_id": request["lifecycle_request"]["project_id"],
        "operation_id": request["lifecycle_request"]["operation_id"],
        "quest_scope": request["lifecycle_request"]["quest_scope"],
        "actor": request["actor"],
        "selected_route": selected,
        "fallback_routes": fallbacks,
        "preview_id": preview["preview_id"],
        "preview_digest": preview["preview_digest"],
        "approval_id": None,
        "approval_digest": None,
        "candidate_set_digest": None,
        "changed_paths": [],
        "changed_paths_digest": None,
        "operations": [],
        "branch": None,
        "state": "PREVIEW_READY",
        "next_safe_action": "Obtain exact Jayson approval bound to this unchanged Preview.",
    }
    _validate_plan(root, plan)
    receipt = _receipt(
        plan, phase="PREVIEW", state="PREVIEW_READY",
        next_safe_action=plan["next_safe_action"],
    )
    _validate_receipt(root, receipt)
    _write(destination / ROUTER_PLAN, plan)
    _write(destination / ROUTER_RECEIPT, receipt)
    verify_router_preview(root, destination, require_current_head=True)
    return {
        "authority": "PREVIEW_ONLY",
        "command": "sunset-router preview",
        "plan_id": plan["plan_id"],
        "preview_id": plan["preview_id"],
        "selected_route": selected,
        "fallback_routes": fallbacks,
        "status": "PASS",
    }


def verify_router_preview(repo_root: Path, router_dir: Path, *, require_current_head: bool = False) -> dict[str, Any]:
    root = repo_root.resolve()
    if not router_dir.is_dir() or router_dir.is_symlink():
        _fail("SUNSET_ROUTER_DIRECTORY", "router Preview directory is unsafe")
    if sorted(item.name for item in router_dir.iterdir()) != sorted([PREVIEW_DIR, ROUTER_PLAN, ROUTER_RECEIPT]):
        _fail("SUNSET_ROUTER_MEMBERS", "router Preview has unexpected members")
    preview = verify_sunset_preview(root, router_dir / PREVIEW_DIR, require_current_head=require_current_head)
    plan = _read(router_dir / ROUTER_PLAN, "SUNSET_ROUTER_PLAN_CANONICAL")
    receipt = _read(router_dir / ROUTER_RECEIPT, "SUNSET_ROUTER_RECEIPT_CANONICAL")
    _validate_plan(root, plan)
    _validate_receipt(root, receipt)
    if (
        plan["phase"] != "PREVIEW"
        or plan["preview_id"] != preview["preview"]["preview_id"]
        or plan["preview_digest"] != preview["preview_digest"]
        or receipt["plan_id"] != plan["plan_id"]
        or receipt["plan_digest"] != _digest(canonical_bytes(plan))
        or receipt["preview_digest"] != plan["preview_digest"]
    ):
        _fail("SUNSET_ROUTER_BINDING", "router Preview bindings do not reconcile")
    if require_current_head and plan["expected_main_sha"] != observed_head(root):
        _fail("STALE_STATE", "router Preview no longer matches current canonical main")
    return {"plan": plan, "receipt": receipt, "preview": preview, "status": "PASS"}


def generate_router_approval(
    repo_root: Path, router_dir: Path, output_dir: Path, *, approval_mode: str
) -> dict[str, Any]:
    root = repo_root.resolve()
    router = verify_router_preview(root, router_dir, require_current_head=True)
    destination = _output(root, output_dir)
    approval = generate_sunset_approval(
        root, router_dir / PREVIEW_DIR, destination / APPROVAL_DIR,
        approval_mode=approval_mode,
    )
    receipt = _receipt(
        router["plan"], phase="APPROVAL", state="APPROVED_PENDING_COMPILATION",
        approval_id=approval["approval_id"],
        next_safe_action="Compile the exact approved lifecycle candidate without changing scope.",
    )
    _validate_receipt(root, receipt)
    _write(destination / ROUTER_RECEIPT, receipt)
    return {
        "authority": "APPROVAL_CARRIER_ONLY",
        "command": "sunset-router approve",
        "plan_id": router["plan"]["plan_id"],
        "approval_id": approval["approval_id"],
        "state": receipt["state"],
        "status": "PASS",
    }


def _verify_approval(root: Path, router_dir: Path, approval_dir: Path) -> tuple[dict, dict, dict]:
    router = verify_router_preview(root, router_dir)
    if not approval_dir.is_dir() or approval_dir.is_symlink():
        _fail("SUNSET_ROUTER_DIRECTORY", "router approval directory is unsafe")
    if sorted(item.name for item in approval_dir.iterdir()) != sorted([APPROVAL_DIR, ROUTER_RECEIPT]):
        _fail("SUNSET_ROUTER_MEMBERS", "router approval has unexpected members")
    approval = verify_sunset_approval(root, router_dir / PREVIEW_DIR, approval_dir / APPROVAL_DIR)
    receipt = _read(approval_dir / ROUTER_RECEIPT, "SUNSET_ROUTER_RECEIPT_CANONICAL")
    _validate_receipt(root, receipt)
    if (
        receipt["plan_id"] != router["plan"]["plan_id"]
        or receipt["approval_id"] != approval["approval"]["approval_id"]
        or receipt["preview_digest"] != router["plan"]["preview_digest"]
    ):
        _fail("SUNSET_ROUTER_BINDING", "router approval bindings do not reconcile")
    return router, approval, receipt


def _operations(root: Path, bundle: dict[str, Any]) -> tuple[list[dict[str, str]], list[str], str]:
    operations = sorted(
        [
            {
                "path": item["path"],
                "action": "REPLACE" if (root / item["path"]).is_file() else "ADD",
                "payload_digest": _digest(canonical_bytes(item["record"])),
            }
            for item in bundle["records"]
        ],
        key=lambda item: (item["path"].casefold(), item["path"]),
    )
    paths = normalize_record_paths([item["path"] for item in operations])
    if paths != [item["path"] for item in operations]:
        _fail("SUNSET_ROUTER_OPERATION_ORDER", "operations must use canonical path order")
    return operations, paths, _digest(("\n".join(paths) + "\n").encode())


def generate_router_candidate(
    repo_root: Path, router_dir: Path, approval_dir: Path, output_dir: Path
) -> dict[str, Any]:
    root = repo_root.resolve()
    router, approval, _ = _verify_approval(root, router_dir, approval_dir)
    if router["plan"]["expected_main_sha"] != observed_head(root):
        _fail("STALE_STATE", "router candidate base no longer matches canonical main")
    destination = _output(root, output_dir)
    generated = generate_approved_sunset_candidate(
        root,
        approval_dir / APPROVAL_DIR / BOUND_REQUEST,
        router_dir / PREVIEW_DIR,
        approval_dir / APPROVAL_DIR,
        destination / CANDIDATE_DIR,
    )
    candidate = verify_approved_sunset_candidate(root, destination / CANDIDATE_DIR)
    bundle = _read(destination / CANDIDATE_DIR / "candidate-bundle.json", "SUNSET_ROUTER_CANDIDATE_CANONICAL")
    operations, paths, paths_digest = _operations(root, bundle)
    plan = {
        **router["plan"],
        "phase": "PUBLICATION",
        "approval_id": approval["approval"]["approval_id"],
        "approval_digest": approval["approval_digest"],
        "candidate_set_digest": candidate["candidate_set_digest"],
        "changed_paths": paths,
        "changed_paths_digest": paths_digest,
        "operations": operations,
        "branch": f"sunset/{router['plan']['preview_id'].casefold()}",
        "state": "APPROVED_PENDING_PUBLICATION",
        "next_safe_action": "Publish these exact record bytes to one draft PR through the selected route.",
    }
    _validate_plan(root, plan)
    receipt = _receipt(
        plan, phase="PUBLICATION", state=plan["state"],
        next_safe_action=plan["next_safe_action"],
    )
    _validate_receipt(root, receipt)
    _write(destination / ROUTER_PLAN, plan)
    _write(destination / ROUTER_RECEIPT, receipt)
    verify_router_candidate(root, router_dir, approval_dir, destination)
    return {
        "authority": "PUBLICATION_PLAN_ONLY",
        "command": "sunset-router candidate",
        "plan_id": plan["plan_id"],
        "candidate_set_digest": generated["candidate_set_digest"],
        "changed_paths": paths,
        "changed_paths_digest": paths_digest,
        "operations": operations,
        "state": plan["state"],
        "status": "PASS",
    }


def verify_router_candidate(
    repo_root: Path, router_dir: Path, approval_dir: Path, candidate_dir: Path
) -> dict[str, Any]:
    root = repo_root.resolve()
    router, approval, _ = _verify_approval(root, router_dir, approval_dir)
    if not candidate_dir.is_dir() or candidate_dir.is_symlink():
        _fail("SUNSET_ROUTER_DIRECTORY", "router candidate directory is unsafe")
    if sorted(item.name for item in candidate_dir.iterdir()) != sorted([CANDIDATE_DIR, ROUTER_PLAN, ROUTER_RECEIPT]):
        _fail("SUNSET_ROUTER_MEMBERS", "router candidate has unexpected members")
    candidate = verify_approved_sunset_candidate(root, candidate_dir / CANDIDATE_DIR)
    bundle = _read(candidate_dir / CANDIDATE_DIR / "candidate-bundle.json", "SUNSET_ROUTER_CANDIDATE_CANONICAL")
    plan = _read(candidate_dir / ROUTER_PLAN, "SUNSET_ROUTER_PLAN_CANONICAL")
    receipt = _read(candidate_dir / ROUTER_RECEIPT, "SUNSET_ROUTER_RECEIPT_CANONICAL")
    _validate_plan(root, plan)
    _validate_receipt(root, receipt)
    operations, paths, paths_digest = _operations(root, bundle)
    valid = (
        plan["phase"] == "PUBLICATION"
        and plan["approval_id"] == approval["approval"]["approval_id"]
        and plan["candidate_set_digest"] == candidate["candidate_set_digest"]
        and plan["changed_paths"] == paths
        and plan["changed_paths_digest"] == paths_digest
        and plan["operations"] == operations
        and receipt["plan_id"] == plan["plan_id"]
        and receipt["plan_digest"] == _digest(canonical_bytes(plan))
        and receipt["candidate_set_digest"] == plan["candidate_set_digest"]
        and receipt["changed_paths_digest"] == paths_digest
        and router["plan"]["plan_id"] == plan["plan_id"]
    )
    if not valid:
        _fail("SUNSET_ROUTER_BINDING", "router candidate bindings do not reconcile")
    return {"plan": plan, "receipt": receipt, "candidate": candidate, "status": "PASS"}


def build_resumable_receipt(
    repo_root: Path, plan: dict[str, Any], *, reason_code: str, next_safe_action: str
) -> dict[str, Any]:
    root = repo_root.resolve()
    _validate_plan(root, plan)
    if not reason_code or not next_safe_action:
        _fail("SUNSET_ROUTER_RESUME", "blocked receipts require a reason and next action")
    receipt = _receipt(
        plan, phase=plan["phase"], state="BLOCKED_RESUMABLE",
        reason_code=reason_code, next_safe_action=next_safe_action,
    )
    _validate_receipt(root, receipt)
    return receipt


def build_publication_receipt(
    repo_root: Path,
    plan: dict[str, Any],
    *,
    state: str,
    expected_head: str,
    pull_request: int,
    merged_commit: str | None = None,
) -> dict[str, Any]:
    root = repo_root.resolve()
    _validate_plan(root, plan)
    if plan["phase"] != "PUBLICATION":
        _fail("SUNSET_ROUTER_RECEIPT_STATE", "publication receipt requires publication plan")
    if not SHA40.fullmatch(expected_head):
        _fail("SUNSET_ROUTER_RECEIPT_HEAD", "publication receipt requires exact head")
    if type(pull_request) is not int or pull_request < 1:
        _fail("SUNSET_ROUTER_RECEIPT_PR", "publication receipt requires pull request")
    allowed = {"APPROVED_PENDING_VALIDATION", "APPROVED_PENDING_PERMANENCE", "READBACK_COMPLETE"}
    if state not in allowed:
        _fail("SUNSET_ROUTER_RECEIPT_STATE", "publication receipt state is unsupported")
    bindings: dict[str, Any] = {"expected_head": expected_head, "pull_request": pull_request}
    if state == "READBACK_COMPLETE":
        if not merged_commit or not SHA40.fullmatch(merged_commit) or observed_head(root) != merged_commit:
            _fail("SUNSET_ROUTER_READBACK", "canonical main does not match exact merged commit")
        for operation in plan["operations"]:
            path = root / operation["path"]
            if not path.is_file() or _digest(path.read_bytes()) != operation["payload_digest"]:
                _fail("SUNSET_ROUTER_READBACK", "canonical lifecycle bytes do not match plan")
        bindings.update({"merged_commit": merged_commit, "canonical_readback": True})
        phase, action = "READBACK", "Report SUNSET COMPLETE from this exact canonical readback."
    else:
        if merged_commit is not None:
            _fail("SUNSET_ROUTER_READBACK", "pre-readback receipt cannot bind merge commit")
        phase = "PUBLICATION"
        action = "Continue exact-head validation, review, and separately authorized permanence."
    receipt = _receipt(plan, phase=phase, state=state, next_safe_action=action, **bindings)
    _validate_receipt(root, receipt)
    return receipt
