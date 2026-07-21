from __future__ import annotations

import base64
import binascii
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Callable
from urllib.parse import quote

from .schema import validate_schema


ROOT = Path(__file__).resolve().parents[2]
THREAD_ENGINE_ROOT = ROOT / "tools" / "thread-engine"
REQUEST_SCHEMA = ROOT / "schemas" / "athena-hosted-route-request-v1.schema.json"
RECEIPT_SCHEMA = ROOT / "schemas" / "athena-hosted-route-receipt-v1.schema.json"
ADAPTER_EVIDENCE_SCHEMA = ROOT / "schemas" / "athena-thread-engine-evidence-v2.schema.json"
REPOSITORY = "Jktomy/atlas-prime"
OWNER = "Jktomy"
MAX_ENCODED_BYTES = 60_000
MAX_CARRIER_BYTES = 45_000
SHA40 = re.compile(r"^[0-9a-f]{40}$")
SHA64 = re.compile(r"^[0-9a-f]{64}$")
SENSITIVE = (
    re.compile(rb"(?i)(api[_-]?key|access[_-]?token|refresh[_-]?token|password|secret)\s*[:=]\s*[^\s`'\"<>{}]+"),
    re.compile(rb"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(rb"(?i)(mfa|recovery code)\s*[:=]\s*[^\s`'\"<>{}]+"),
)


class HostedRouteError(RuntimeError):
    def __init__(self, message: str, code: str, *, result: str = "REJECTED", route: str = "ARROW_BOW_HOSTED") -> None:
        super().__init__(message)
        self.code = code
        self.result = result
        self.route = route


def stable_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def safe_error_code(error: BaseException, fallback: str) -> str:
    code = str(getattr(error, "code", fallback))
    return code if re.fullmatch(r"[A-Z][A-Z0-9_]{0,79}", code) else fallback


def safe_evidence_code(value: Any, fallback: str) -> str:
    code = str(value or fallback)
    return code if re.fullmatch(r"[A-Z][A-Z0-9_]{0,79}", code) else fallback


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(stable_json(value), encoding="utf-8", newline="\n")


def adapter_source_receipt_bytes(value: dict[str, Any]) -> bytes:
    """Reproduce the production adapter's exact receipt serialization."""
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")


def load_schema(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise HostedRouteError("route schema root is not an object", "ROUTE_SCHEMA_INVALID")
    return value


def required_environment(env: dict[str, str]) -> dict[str, str]:
    keys = (
        "GITHUB_REPOSITORY",
        "GITHUB_REPOSITORY_OWNER",
        "GITHUB_EVENT_NAME",
        "GITHUB_EVENT_PATH",
        "GITHUB_ACTOR",
        "GITHUB_TRIGGERING_ACTOR",
        "GITHUB_WORKFLOW_REF",
        "GITHUB_WORKFLOW_SHA",
        "GITHUB_RUN_ID",
        "GITHUB_RUN_ATTEMPT",
        "ATHENA_ARROW_SHA256",
        "ATHENA_MISSION_LOCK_SHA256",
        "ATHENA_PUBLIC_CLEAN_CONFIRMATION",
    )
    missing = [key for key in keys if not env.get(key)]
    if missing:
        raise HostedRouteError(f"missing trusted environment: {', '.join(missing)}", "TRUSTED_ENVIRONMENT_MISSING")
    values = {key: env[key] for key in keys}
    if values["GITHUB_REPOSITORY"] != REPOSITORY or values["GITHUB_REPOSITORY_OWNER"] != OWNER:
        raise HostedRouteError("repository identity mismatch", "REPOSITORY_IDENTITY_MISMATCH")
    if values["GITHUB_EVENT_NAME"] != "workflow_dispatch":
        raise HostedRouteError("hosted Bow requires workflow_dispatch", "EVENT_ROUTE_REJECTED")
    if values["GITHUB_ACTOR"] != OWNER or values["GITHUB_TRIGGERING_ACTOR"] != OWNER:
        raise HostedRouteError("owner actor and triggering actor are required", "OWNER_IDENTITY_REJECTED")
    if values["ATHENA_PUBLIC_CLEAN_CONFIRMATION"] != "PUBLIC_CLEAN_CONFIRMED":
        raise HostedRouteError("public-clean pre-ingress confirmation required", "PRE_INGRESS_PRIVACY_REQUIRED")
    if not SHA40.fullmatch(values["GITHUB_WORKFLOW_SHA"]):
        raise HostedRouteError("workflow source SHA is invalid", "WORKFLOW_IDENTITY_REJECTED")
    if not SHA64.fullmatch(values["ATHENA_ARROW_SHA256"]):
        raise HostedRouteError("carrier SHA-256 is invalid", "CARRIER_SHA_REJECTED")
    if not SHA64.fullmatch(values["ATHENA_MISSION_LOCK_SHA256"]):
        raise HostedRouteError("mission lock SHA-256 is invalid", "MISSION_LOCK_REJECTED")
    if not values["GITHUB_RUN_ID"].isdigit() or not values["GITHUB_RUN_ATTEMPT"].isdigit() or int(values["GITHUB_RUN_ATTEMPT"]) < 1:
        raise HostedRouteError("run identity is invalid", "RUN_IDENTITY_REJECTED")
    return values


def fetch_run_metadata(repository: str, run_id: str) -> dict[str, Any]:
    completed = subprocess.run(
        ["gh", "api", f"repos/{repository}/actions/runs/{run_id}"],
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise HostedRouteError("GitHub run identity readback failed", "RUN_IDENTITY_READBACK_FAILED")
    try:
        value = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise HostedRouteError("GitHub run identity was not JSON", "RUN_IDENTITY_READBACK_FAILED") from exc
    if not isinstance(value, dict):
        raise HostedRouteError("GitHub run identity was malformed", "RUN_IDENTITY_READBACK_FAILED")
    return value


def decode_carrier(encoded: str, expected_sha256: str) -> bytes:
    encoded_bytes = encoded.encode("ascii", errors="strict")
    if not encoded_bytes or len(encoded_bytes) > MAX_ENCODED_BYTES:
        raise HostedRouteError("carrier input size rejected", "CARRIER_SIZE_REJECTED")
    try:
        data = base64.b64decode(encoded_bytes, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise HostedRouteError("carrier is not strict Base64", "CARRIER_BASE64_REJECTED") from exc
    if not data or len(data) > MAX_CARRIER_BYTES:
        raise HostedRouteError("decoded carrier size rejected", "CARRIER_SIZE_REJECTED")
    if sha256_bytes(data) != expected_sha256:
        raise HostedRouteError("carrier SHA-256 mismatch", "CARRIER_SHA_REJECTED")
    return data


def observed_rejection_digest(encoded: str, fallback: str) -> str:
    try:
        encoded_bytes = encoded.encode("ascii", errors="strict")
        if not encoded_bytes or len(encoded_bytes) > MAX_ENCODED_BYTES:
            return fallback
        data = base64.b64decode(encoded_bytes, validate=True)
    except (UnicodeEncodeError, binascii.Error, ValueError):
        return fallback
    return sha256_bytes(data) if data else fallback


def privacy_scan(package: Any) -> None:
    values = [stable_json(package.weave).encode("utf-8"), *package.payloads.values()]
    for value in values:
        try:
            value.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise HostedRouteError("carrier content is not public-clean UTF-8", "CARRIER_PRIVACY_REJECTED") from exc
        if any(pattern.search(value) for pattern in SENSITIVE):
            raise HostedRouteError("carrier failed public-clean privacy scan", "CARRIER_PRIVACY_REJECTED")


def classify_paths(paths: list[str]) -> tuple[str, str]:
    if any(path.startswith("generated/") for path in paths):
        return "GENERATED_SOURCE_MIXING", "ARROW_BOW_HOSTED"
    return "SAFE_DECLARED", "ARROW_BOW_HOSTED"


def identity_from(values: dict[str, str], mission_id: str) -> dict[str, Any]:
    return {
        "authorizer": "Jayson",
        "semantic_operator": "Codex SOL Goal",
        "requesting_surface": "Codex",
        "event_actor": values["GITHUB_ACTOR"],
        "triggering_actor": values["GITHUB_TRIGGERING_ACTOR"],
        "workflow_ref": values["GITHUB_WORKFLOW_REF"],
        "workflow_source_sha": values["GITHUB_WORKFLOW_SHA"],
        "credential_principal": f"GITHUB_ACTIONS_REPOSITORY_TOKEN:{REPOSITORY}",
        "token_mode": "GITHUB_TOKEN",
        "mission_id": mission_id,
        "run_id": values["GITHUB_RUN_ID"],
        "run_attempt": int(values["GITHUB_RUN_ATTEMPT"]),
    }


def expected_mission_branch(mission_id: str, base_sha: str) -> str:
    material = {"repository": REPOSITORY, "mission_id": mission_id, "base_sha": base_sha}
    return "source/athena-bow-" + sha256_bytes(stable_json(material).encode("utf-8"))[:20]


def mission_lock_sha256(mission_id: str, base_sha: str) -> str:
    material = {"repository": REPOSITORY, "mission_id": mission_id, "base_sha": base_sha}
    return sha256_bytes(stable_json(material).encode("utf-8"))


def assert_no_replay(branch: str) -> None:
    ref = subprocess.run(
        ["gh", "api", f"repos/{REPOSITORY}/git/ref/heads/{quote(branch, safe='')}"],
        check=False,
        capture_output=True,
        text=True,
    )
    if ref.returncode == 0:
        raise HostedRouteError("mission branch already exists", "REPLAY_BRANCH_EXISTS")
    if "404" not in ref.stderr and "Not Found" not in ref.stderr:
        raise HostedRouteError("branch replay readback failed", "REPLAY_READBACK_FAILED")
    prs = subprocess.run(
        ["gh", "pr", "list", "--repo", REPOSITORY, "--state", "all", "--head", branch, "--json", "number,state"],
        check=False,
        capture_output=True,
        text=True,
    )
    if prs.returncode != 0:
        raise HostedRouteError("pull-request replay readback failed", "REPLAY_READBACK_FAILED")
    try:
        observed = json.loads(prs.stdout)
    except json.JSONDecodeError as exc:
        raise HostedRouteError("pull-request replay readback was malformed", "REPLAY_READBACK_FAILED") from exc
    if observed:
        raise HostedRouteError("historical mission pull request already exists", "REPLAY_PULL_REQUEST_EXISTS")


def read_remote_state(branch: str) -> dict[str, Any]:
    ref = subprocess.run(
        ["gh", "api", f"repos/{REPOSITORY}/git/ref/heads/{quote(branch, safe='')}"],
        check=False,
        capture_output=True,
        text=True,
    )
    branch_exists = ref.returncode == 0
    head_sha: str | None = None
    if branch_exists:
        try:
            head_sha = json.loads(ref.stdout)["object"]["sha"]
        except (KeyError, TypeError, json.JSONDecodeError) as exc:
            raise HostedRouteError("remote branch readback was malformed", "REMOTE_STATE_READBACK_FAILED") from exc
        if not isinstance(head_sha, str) or not SHA40.fullmatch(head_sha):
            raise HostedRouteError("remote branch head was malformed", "REMOTE_STATE_READBACK_FAILED")
    elif "404" not in ref.stderr and "Not Found" not in ref.stderr:
        raise HostedRouteError("remote branch readback failed", "REMOTE_STATE_READBACK_FAILED")
    prs = subprocess.run(
        [
            "gh", "pr", "list", "--repo", REPOSITORY, "--state", "all", "--head", branch,
            "--json", "number,state,isDraft,headRefName,headRefOid",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    if prs.returncode != 0:
        raise HostedRouteError("remote pull-request readback failed", "REMOTE_STATE_READBACK_FAILED")
    try:
        pull_requests = json.loads(prs.stdout)
    except json.JSONDecodeError as exc:
        raise HostedRouteError("remote pull-request readback was malformed", "REMOTE_STATE_READBACK_FAILED") from exc
    if not isinstance(pull_requests, list) or len(pull_requests) > 1:
        raise HostedRouteError("remote pull-request state was ambiguous", "REMOTE_STATE_READBACK_FAILED")
    pull_request = pull_requests[0] if pull_requests else None
    if pull_request is not None and not isinstance(pull_request, dict):
        raise HostedRouteError("remote pull-request state was malformed", "REMOTE_STATE_READBACK_FAILED")
    return {
        "readback": "VERIFIED",
        "branch_exists": branch_exists,
        "head_sha": head_sha,
        "pull_request": pull_request,
    }


def sanitized_adapter_evidence(raw: dict[str, Any], branch: str, remote: dict[str, Any]) -> dict[str, Any]:
    checkpoints = []
    for item in raw.get("checkpoint_results", []):
        if not isinstance(item, dict):
            continue
        checkpoint = safe_evidence_code(item.get("checkpoint"), "UNKNOWN_CHECKPOINT")
        status = safe_evidence_code(str(item.get("status", "")).upper(), "UNKNOWN_STATUS")
        checkpoints.append({"checkpoint": checkpoint, "status": status})
    pr = remote.get("pull_request") if isinstance(remote.get("pull_request"), dict) else None
    confirmation = raw.get("forbidden_action_confirmation")
    confirmation = confirmation if isinstance(confirmation, dict) else {}
    evidence = {
        "schema_version": "atlas.athena.thread-engine-evidence.v2",
        "source_receipt_schema_version": (
            raw.get("schema_version")
            if raw.get("schema_version") == "atlas-thread-engine-production-adapter-receipt-v2"
            else None
        ),
        "source_receipt_sha256": sha256_bytes(adapter_source_receipt_bytes(raw)),
        "mission_id": raw.get("mission_id") if isinstance(raw.get("mission_id"), str) else None,
        "mission_sha256": raw.get("mission_sha256") if isinstance(raw.get("mission_sha256"), str) and SHA64.fullmatch(raw["mission_sha256"]) else None,
        "candidate_tree_sha256": raw.get("candidate_tree_sha256") if isinstance(raw.get("candidate_tree_sha256"), str) and SHA64.fullmatch(raw["candidate_tree_sha256"]) else None,
        "commit_tree": raw.get("commit_tree") if isinstance(raw.get("commit_tree"), str) and SHA40.fullmatch(raw["commit_tree"]) else None,
        "result": safe_evidence_code(raw.get("result"), "UNKNOWN_RESULT"),
        "error_code": None if raw.get("error_code") is None else safe_evidence_code(raw.get("error_code"), "THREAD_ENGINE_REJECTED"),
        "error_stage": None if raw.get("error_stage") is None else safe_evidence_code(raw.get("error_stage"), "THREAD_ENGINE_REJECTED"),
        "stop_point": safe_evidence_code(raw.get("stop_point"), "UNKNOWN_STOP_POINT"),
        "forbidden_action_confirmation": {
            "direct_main_write": confirmation.get("direct_main_write"),
            "force_push": confirmation.get("force_push"),
            "auto_merge": confirmation.get("auto_merge"),
            "ready_transition": confirmation.get("ready_transition"),
            "workflow_dispatch": confirmation.get("workflow_dispatch"),
            "repository_setting_mutation": confirmation.get("repository_setting_mutation"),
            "unprofiled_generated_output_mutation": confirmation.get("unprofiled_generated_output_mutation"),
            "protected_board_mutation": confirmation.get("protected_board_mutation"),
            "production_authority_activated": confirmation.get("production_authority_activated"),
            "standing_authority": confirmation.get("standing_authority"),
        },
        "branch": branch,
        "checkpoint_results": checkpoints,
        "remote_state": {
            "readback": remote.get("readback", "UNAVAILABLE"),
            "branch_exists": remote.get("branch_exists"),
            "head_sha": remote.get("head_sha"),
            "pull_request": None if pr is None else {
                "number": pr.get("number") if isinstance(pr.get("number"), int) else None,
                "state": pr.get("state") if pr.get("state") in {"OPEN", "CLOSED", "MERGED"} else None,
                "is_draft": pr.get("isDraft") if isinstance(pr.get("isDraft"), bool) else None,
                "head_ref_name": pr.get("headRefName") if pr.get("headRefName") == branch else None,
                "head_ref_oid": pr.get("headRefOid") if isinstance(pr.get("headRefOid"), str) and SHA40.fullmatch(pr["headRefOid"]) else None,
            },
        },
    }
    validate_schema(load_schema(ADAPTER_EVIDENCE_SCHEMA), evidence)
    return evidence


def completed_remote_checkpoint(raw: dict[str, Any]) -> bool:
    mutation_checkpoints = {"PUSH", "DRAFT_PR", "READBACK", "RECEIPT", "STOP"}
    return any(
        isinstance(item, dict)
        and item.get("checkpoint") in mutation_checkpoints
        and item.get("status") == "completed"
        for item in raw.get("checkpoint_results", [])
    )


def build_request(values: dict[str, str], package: Any, event_bytes: bytes, run: dict[str, Any], classification: str) -> dict[str, Any]:
    actor = ((run.get("actor") or {}).get("login"))
    triggering_actor = ((run.get("triggering_actor") or {}).get("login"))
    if actor != OWNER or triggering_actor != OWNER:
        raise HostedRouteError("run actor readback mismatch", "OWNER_IDENTITY_REJECTED")
    if str(run.get("id")) != values["GITHUB_RUN_ID"] or int(run.get("run_attempt", 0)) != int(values["GITHUB_RUN_ATTEMPT"]):
        raise HostedRouteError("run identity readback mismatch", "RUN_IDENTITY_REJECTED")
    weave = package.weave
    run_head = run.get("head_sha")
    if run.get("head_branch") != "main" or not isinstance(run_head, str) or not SHA40.fullmatch(run_head):
        raise HostedRouteError("workflow run base readback mismatch", "RUN_IDENTITY_REJECTED")
    if run_head != values["GITHUB_WORKFLOW_SHA"]:
        raise HostedRouteError("workflow source does not match run head", "WORKFLOW_IDENTITY_REJECTED")
    if weave["base_sha"] != run_head:
        raise HostedRouteError("carrier base is stale", "BASE_STALE")
    expected_branch = expected_mission_branch(weave["weave_id"], weave["base_sha"])
    if weave["branch"] != expected_branch:
        raise HostedRouteError("mission branch is not deterministic", "REPLAY_BRANCH_MISMATCH")
    expected_lock = mission_lock_sha256(weave["weave_id"], weave["base_sha"])
    if values["ATHENA_MISSION_LOCK_SHA256"] != expected_lock:
        raise HostedRouteError("mission concurrency lock does not match decoded carrier", "MISSION_LOCK_REJECTED")
    event_id = f"workflow_dispatch:{values['GITHUB_RUN_ID']}"
    replay_material = {
        "repository": REPOSITORY,
        "event_identity": event_id,
        "carrier_sha256": package.carrier_sha256,
        "mission_lock_sha256": expected_lock,
        "mission_id": weave["weave_id"],
        "base_sha": weave["base_sha"],
    }
    request = {
        "schema_version": "atlas.athena.hosted-route-request.v1",
        "authorizer": "Jayson",
        "semantic_operator": "Codex SOL Goal",
        "requesting_surface": "Codex",
        "repository": REPOSITORY,
        "base_sha": weave["base_sha"],
        "route": "ARROW_BOW_HOSTED",
        "mission_id": weave["weave_id"],
        "carrier_sha256": package.carrier_sha256,
        "mission_lock_sha256": expected_lock,
        "event_identity": {
            "event_name": "workflow_dispatch",
            "event_action": "requested",
            "event_node_or_delivery_id": event_id,
            "created_at": run["created_at"],
            "updated_at": run["updated_at"],
            "event_payload_sha256": sha256_bytes(event_bytes),
            "event_actor": actor,
            "triggering_actor": triggering_actor,
            "workflow_ref": values["GITHUB_WORKFLOW_REF"],
            "workflow_source_sha": values["GITHUB_WORKFLOW_SHA"],
            "run_id": values["GITHUB_RUN_ID"],
            "run_attempt": int(values["GITHUB_RUN_ATTEMPT"]),
        },
        "credential_identity": {
            "credential_principal": f"GITHUB_ACTIONS_REPOSITORY_TOKEN:{REPOSITORY}",
            "token_mode": "GITHUB_TOKEN",
        },
        "replay_key": "sha256:" + sha256_bytes(stable_json(replay_material).encode("utf-8")),
        "protected_path_classification": classification,
        "stop_boundary": "DRAFT_PR_READBACK",
        "forbidden_actions": {
            "direct_main": False,
            "force_push": False,
            "ready": False,
            "merge": False,
            "settings": False,
            "standing_authority": False,
            "second_writer": False,
        },
    }
    validate_schema(load_schema(REQUEST_SCHEMA), request)
    return request


def no_mutation_receipt(values: dict[str, str], *, code: str, route: str, result: str, carrier_sha256: str, mission_id: str = "UNKNOWN") -> dict[str, Any]:
    blocked = result == "BLOCKED"
    basis = {
        "repository": REPOSITORY,
        "run_id": values["GITHUB_RUN_ID"],
        "run_attempt": values["GITHUB_RUN_ATTEMPT"],
        "carrier_sha256": carrier_sha256,
        "error_code": code,
    }
    receipt = {
        "schema_version": "atlas.athena.hosted-route-receipt.v1",
        "result": result,
        "route": route,
        "identity": identity_from(values, mission_id),
        "request_sha256": sha256_bytes(stable_json(basis).encode("utf-8")),
        "carrier_sha256": carrier_sha256,
        "compile_receipt_sha256": None,
        "adapter_receipt_sha256": None,
        "replay_key": "sha256:" + sha256_bytes(stable_json(basis).encode("utf-8")),
        "stage": "ROUTE_HANDOFF" if blocked else "PRE_MUTATION_REJECTION",
        "error_code": code,
        "stop_point": "ROUTE_HANDOFF_REQUIRED" if blocked else "PRE_MUTATION_REJECTION",
        "mutation": {"occurred": False, "branch": None, "pull_request": None, "head_sha": None, "draft": None},
        "rollback": {"pre_merge": "NO_MUTATION_REQUIRED", "post_merge": "NO_MUTATION_REQUIRED", "force_or_history_rewrite": False},
        "forbidden_action_confirmation": {
            "direct_main": False,
            "force_push": False,
            "ready": False,
            "merge": False,
            "settings": False,
            "standing_authority": False,
            "second_writer": False,
        },
    }
    validate_schema(load_schema(RECEIPT_SCHEMA), receipt)
    return receipt


def preserve_engine_failure(
    *,
    values: dict[str, str],
    package: Any,
    request: dict[str, Any],
    expected_sha: str,
    compile_receipt_sha256: str,
    receipt_path: Path,
    raw: dict[str, Any],
    fallback_code: str,
    known_mutation: bool,
    remote_probe: Callable[[str], dict[str, Any]],
) -> dict[str, Any]:
    branch = package.weave["branch"]
    try:
        remote = remote_probe(branch)
    except Exception:
        remote = {"readback": "UNAVAILABLE", "branch_exists": None, "head_sha": None, "pull_request": None}
    adapter_path = receipt_path.with_name("thread-engine-evidence.json")
    evidence = sanitized_adapter_evidence(raw, branch, remote)
    write_json(adapter_path, evidence)
    pr = remote.get("pull_request") if isinstance(remote.get("pull_request"), dict) else None
    remote_mutation = bool(remote.get("branch_exists") or pr)
    absence_proven = remote.get("readback") == "VERIFIED" and not remote.get("branch_exists") and pr is None
    mutation_possible = known_mutation or completed_remote_checkpoint(raw) or remote_mutation or not absence_proven
    code_fallback = "THREAD_ENGINE_PARTIAL" if raw.get("result") == "PARTIAL" else fallback_code
    code = safe_evidence_code(raw.get("error_code"), code_fallback)
    if not mutation_possible:
        receipt = no_mutation_receipt(
            values,
            code=code,
            route="ARROW_BOW_HOSTED",
            result="REJECTED",
            carrier_sha256=expected_sha,
            mission_id=package.weave["weave_id"],
        )
        write_json(receipt_path, receipt)
        return receipt
    partial = {
        "schema_version": "atlas.athena.hosted-route-receipt.v1",
        "result": "PARTIAL",
        "route": "ARROW_BOW_HOSTED",
        "identity": identity_from(values, package.weave["weave_id"]),
        "request_sha256": sha256_bytes(stable_json(request).encode("utf-8")),
        "carrier_sha256": expected_sha,
        "compile_receipt_sha256": compile_receipt_sha256,
        "adapter_receipt_sha256": sha256_bytes(adapter_path.read_bytes()),
        "replay_key": request["replay_key"],
        "stage": safe_evidence_code(raw.get("error_stage"), "THREAD_ENGINE_PARTIAL"),
        "error_code": code,
        "stop_point": "PARTIAL_STATE_PRESERVED",
        "mutation": {
            "occurred": True,
            "branch": branch,
            "pull_request": pr.get("number") if pr and isinstance(pr.get("number"), int) else None,
            "head_sha": remote.get("head_sha") if isinstance(remote.get("head_sha"), str) and SHA40.fullmatch(remote["head_sha"]) else None,
            "draft": pr.get("isDraft") if pr and isinstance(pr.get("isDraft"), bool) else None,
        },
        "rollback": {"pre_merge": "PRESERVE_PARTIAL_STATE_AND_REVIEW", "post_merge": "NO_MERGE_OCCURRED", "force_or_history_rewrite": False},
        "forbidden_action_confirmation": {"direct_main": False, "force_push": False, "ready": False, "merge": False, "settings": False, "standing_authority": False, "second_writer": False},
    }
    validate_schema(load_schema(RECEIPT_SCHEMA), partial)
    write_json(receipt_path, partial)
    return partial


def _engine_imports() -> tuple[Any, Any, Any, Any]:
    if str(THREAD_ENGINE_ROOT) not in sys.path:
        sys.path.insert(0, str(THREAD_ENGINE_ROOT))
    from production_adapter.adapter import AdapterError, execute_mission
    from spear_bridge.compiler import compile_package, read_spear_package

    return AdapterError, execute_mission, compile_package, read_spear_package


def preflight_hosted(
    encoded_carrier: str,
    *,
    env: dict[str, str],
    evidence_dir: Path,
    work_root: Path,
    run_metadata: dict[str, Any] | None = None,
    package_reader: Callable[[Path, str], Any] | None = None,
    replay_probe: Callable[[str], None] = assert_no_replay,
) -> dict[str, Any]:
    try:
        values = required_environment(env)
    except HostedRouteError as exc:
        if exc.code != "OWNER_IDENTITY_REJECTED":
            raise
        keys = (
            "GITHUB_REPOSITORY",
            "GITHUB_REPOSITORY_OWNER",
            "GITHUB_EVENT_NAME",
            "GITHUB_EVENT_PATH",
            "GITHUB_ACTOR",
            "GITHUB_TRIGGERING_ACTOR",
            "GITHUB_WORKFLOW_REF",
            "GITHUB_WORKFLOW_SHA",
            "GITHUB_RUN_ID",
            "GITHUB_RUN_ATTEMPT",
            "ATHENA_ARROW_SHA256",
            "ATHENA_PUBLIC_CLEAN_CONFIRMATION",
        )
        values = {key: env[key] for key in keys}
        receipt = no_mutation_receipt(
            values,
            code=exc.code,
            route="ARROW_BOW_HOSTED",
            result="REJECTED",
            carrier_sha256=values["ATHENA_ARROW_SHA256"],
        )
        write_json(evidence_dir / "athena-hosted-route-receipt.json", receipt)
        return receipt
    expected_sha = values["ATHENA_ARROW_SHA256"]
    try:
        carrier_data = decode_carrier(encoded_carrier, expected_sha)
    except HostedRouteError as exc:
        observed_sha = observed_rejection_digest(encoded_carrier, expected_sha)
        receipt = no_mutation_receipt(values, code=exc.code, route=exc.route, result=exc.result, carrier_sha256=observed_sha)
        write_json(evidence_dir / "athena-hosted-route-receipt.json", receipt)
        return receipt
    event_bytes = Path(values["GITHUB_EVENT_PATH"]).read_bytes()
    if package_reader is None:
        package_reader = _engine_imports()[3]
    work_root.mkdir(parents=True, exist_ok=True)
    try:
        with tempfile.TemporaryDirectory(prefix="atlas-athena-bow-preflight-", dir=work_root) as temporary:
            carrier_path = Path(temporary) / "arrow.zip"
            carrier_path.write_bytes(carrier_data)
            package = package_reader(carrier_path, expected_sha)
            privacy_scan(package)
            paths = [item["path"] for item in package.weave["threads"]]
            classification, route = classify_paths(paths)
            if classification != "SAFE_DECLARED":
                receipt = no_mutation_receipt(
                    values,
                    code=classification,
                    route=route,
                    result="BLOCKED" if route != "ARROW_BOW_HOSTED" else "REJECTED",
                    carrier_sha256=expected_sha,
                    mission_id=package.weave["weave_id"],
                )
                write_json(evidence_dir / "athena-hosted-route-receipt.json", receipt)
                return receipt
            run = run_metadata or fetch_run_metadata(REPOSITORY, values["GITHUB_RUN_ID"])
            request = build_request(values, package, event_bytes, run, classification)
            replay_probe(package.weave["branch"])
            write_json(evidence_dir / "athena-hosted-route-request.json", request)
            result = {
                "result": "ACCEPTED",
                "route": "ARROW_BOW_HOSTED",
                "request_sha256": sha256_bytes(stable_json(request).encode("utf-8")),
                "carrier_sha256": expected_sha,
                "replay_key": request["replay_key"],
                "stop_point": "READ_ONLY_PREFLIGHT_COMPLETE",
            }
            write_json(evidence_dir / "athena-hosted-preflight-result.json", result)
            return result
    except HostedRouteError as exc:
        observed_sha = observed_rejection_digest(encoded_carrier, expected_sha)
        receipt = no_mutation_receipt(values, code=exc.code, route=exc.route, result=exc.result, carrier_sha256=observed_sha)
        write_json(evidence_dir / "athena-hosted-route-receipt.json", receipt)
        return receipt
    except Exception as exc:
        code = safe_error_code(exc, "HOSTED_PREFLIGHT_REJECTED")
        receipt = no_mutation_receipt(values, code=code, route="ARROW_BOW_HOSTED", result="REJECTED", carrier_sha256=expected_sha)
        write_json(evidence_dir / "athena-hosted-route-receipt.json", receipt)
        return receipt


def run_hosted(
    encoded_carrier: str,
    *,
    env: dict[str, str],
    receipt_path: Path,
    work_root: Path,
    run_metadata: dict[str, Any] | None = None,
    engine: tuple[Any, Any, Any, Any] | None = None,
    replay_probe: Callable[[str], None] = assert_no_replay,
    remote_probe: Callable[[str], dict[str, Any]] = read_remote_state,
) -> dict[str, Any]:
    values = required_environment(env)
    expected_sha = values["ATHENA_ARROW_SHA256"]
    try:
        carrier_data = decode_carrier(encoded_carrier, expected_sha)
    except HostedRouteError as exc:
        receipt = no_mutation_receipt(values, code=exc.code, route=exc.route, result=exc.result, carrier_sha256=expected_sha)
        write_json(receipt_path, receipt)
        return receipt
    event_path = Path(values["GITHUB_EVENT_PATH"])
    event_bytes = event_path.read_bytes()
    AdapterError, execute_mission, compile_package, read_spear_package = engine or _engine_imports()
    work_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="atlas-athena-bow-", dir=work_root) as temporary:
        temp = Path(temporary)
        carrier_path = temp / "arrow.zip"
        carrier_path.write_bytes(carrier_data)
        package: Any | None = None
        request: dict[str, Any] | None = None
        compile_receipt_sha256: str | None = None
        adapter_started = False
        try:
            package = read_spear_package(carrier_path, expected_sha)
            privacy_scan(package)
            paths = [item["path"] for item in package.weave["threads"]]
            classification, route = classify_paths(paths)
            if classification != "SAFE_DECLARED":
                receipt = no_mutation_receipt(
                    values,
                    code=classification,
                    route=route,
                    result="BLOCKED" if route != "ARROW_BOW_HOSTED" else "REJECTED",
                    carrier_sha256=expected_sha,
                    mission_id=package.weave["weave_id"],
                )
                write_json(receipt_path, receipt)
                return receipt
            run = run_metadata or fetch_run_metadata(REPOSITORY, values["GITHUB_RUN_ID"])
            request = build_request(values, package, event_bytes, run, classification)
            replay_probe(package.weave["branch"])
            write_json(receipt_path.with_name("athena-hosted-route-request.json"), request)
            compiled = temp / "compiled"
            compile_receipt = compile_package(
                carrier_path,
                package_sha256=expected_sha,
                output_dir=compiled,
                disabled_proof=True,
                compile_only=True,
            )
            mission_path = compiled / compile_receipt["output_mission_filename"]
            compile_receipt_path = compiled / compile_receipt["compile_receipt_filename"]
            compile_receipt_sha256 = sha256_bytes(compile_receipt_path.read_bytes())
            try:
                adapter_started = True
                adapter_receipt = execute_mission(
                    mission_path,
                    mission_scoped=True,
                    execute_draft_pr=True,
                    mission_sha256=compile_receipt["mission_sha256"],
                    work_root=temp,
                    package_root=compiled,
                )
            except Exception as exc:
                raw = getattr(exc, "receipt", None)
                if not isinstance(raw, dict):
                    raw = {
                        "result": "UNKNOWN_RESULT",
                        "error_code": safe_error_code(exc, "THREAD_ENGINE_STATE_UNKNOWN"),
                        "error_stage": "THREAD_ENGINE_INVOCATION",
                        "checkpoint_results": [],
                    }
                return preserve_engine_failure(
                    values=values,
                    package=package,
                    request=request,
                    expected_sha=expected_sha,
                    compile_receipt_sha256=compile_receipt_sha256,
                    receipt_path=receipt_path,
                    raw=raw,
                    fallback_code="THREAD_ENGINE_REJECTED",
                    known_mutation=False,
                    remote_probe=remote_probe,
                )
            try:
                pr = adapter_receipt["pr_readback"]
                success_remote = {
                    "readback": "VERIFIED",
                    "branch_exists": True,
                    "head_sha": adapter_receipt["head_sha"],
                    "pull_request": pr,
                }
                adapter_path = receipt_path.with_name("thread-engine-evidence.json")
                write_json(adapter_path, sanitized_adapter_evidence(adapter_receipt, package.weave["branch"], success_remote))
                receipt = {
                    "schema_version": "atlas.athena.hosted-route-receipt.v1",
                    "result": "SUCCESS",
                    "route": "ARROW_BOW_HOSTED",
                    "identity": identity_from(values, package.weave["weave_id"]),
                    "request_sha256": sha256_bytes(stable_json(request).encode("utf-8")),
                    "carrier_sha256": expected_sha,
                    "compile_receipt_sha256": compile_receipt_sha256,
                    "adapter_receipt_sha256": sha256_bytes(adapter_path.read_bytes()),
                    "replay_key": request["replay_key"],
                    "stage": "DRAFT_PR_READBACK",
                    "error_code": None,
                    "stop_point": "DRAFT_PR_READBACK",
                    "mutation": {
                        "occurred": True,
                        "branch": package.weave["branch"],
                        "pull_request": pr["number"],
                        "head_sha": adapter_receipt["head_sha"],
                        "draft": pr["isDraft"],
                    },
                    "rollback": {"pre_merge": "CLOSE_DRAFT_PR", "post_merge": "REVIEWED_REVERT_PR", "force_or_history_rewrite": False},
                    "forbidden_action_confirmation": {"direct_main": False, "force_push": False, "ready": False, "merge": False, "settings": False, "standing_authority": False, "second_writer": False},
                }
                validate_schema(load_schema(RECEIPT_SCHEMA), receipt)
                write_json(receipt_path, receipt)
                return receipt
            except Exception as exc:
                raw = adapter_receipt if isinstance(adapter_receipt, dict) else {}
                raw = {**raw, "result": "PARTIAL", "error_code": safe_error_code(exc, "POST_RETURN_PROCESSING_FAILED"), "error_stage": "POST_RETURN_PROCESSING"}
                return preserve_engine_failure(
                    values=values,
                    package=package,
                    request=request,
                    expected_sha=expected_sha,
                    compile_receipt_sha256=compile_receipt_sha256,
                    receipt_path=receipt_path,
                    raw=raw,
                    fallback_code="POST_RETURN_PROCESSING_FAILED",
                    known_mutation=True,
                    remote_probe=remote_probe,
                )
        except HostedRouteError as exc:
            receipt = no_mutation_receipt(values, code=exc.code, route=exc.route, result=exc.result, carrier_sha256=expected_sha)
            write_json(receipt_path, receipt)
            return receipt
        except Exception as exc:
            if adapter_started and package is not None and request is not None and compile_receipt_sha256 is not None:
                return preserve_engine_failure(
                    values=values,
                    package=package,
                    request=request,
                    expected_sha=expected_sha,
                    compile_receipt_sha256=compile_receipt_sha256,
                    receipt_path=receipt_path,
                    raw={
                        "result": "PARTIAL",
                        "error_code": safe_error_code(exc, "THREAD_ENGINE_STATE_UNKNOWN"),
                        "error_stage": "THREAD_ENGINE_STATE_RECONCILIATION",
                        "checkpoint_results": [],
                    },
                    fallback_code="THREAD_ENGINE_STATE_UNKNOWN",
                    known_mutation=True,
                    remote_probe=remote_probe,
                )
            code = safe_error_code(exc, "HOSTED_ROUTE_REJECTED")
            receipt = no_mutation_receipt(values, code=code, route="ARROW_BOW_HOSTED", result="REJECTED", carrier_sha256=expected_sha)
            write_json(receipt_path, receipt)
            return receipt
