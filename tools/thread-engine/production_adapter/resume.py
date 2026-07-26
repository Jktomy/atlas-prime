from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any
import tempfile
import shutil
import sys

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from tools.candidate_seal.core import CandidateSealError, sha256_text, verify_candidate_seal

from .adapter import AdapterError, execute_mission
from .authority import load_mission
from .receipt import sha256_bytes, stable_json

SHA40 = re.compile(r"^[0-9a-f]{40}$")
POST_PUSH_STAGES = {"PUSH", "DRAFT_PR", "READBACK", "RECEIPT", "STOP"}


class SealedAdapterError(AdapterError):
    pass


def _run(command: list[str], *, cwd: Path | None = None) -> str:
    completed = subprocess.run(command, cwd=cwd, check=False, capture_output=True, text=True)
    if completed.returncode != 0:
        raise SealedAdapterError("remote state readback failed", "REMOTE_STATE_READBACK_FAILED", "READBACK", partial=True)
    return completed.stdout.strip()


def _candidate_files(mission_path: Path, package_root: Path) -> dict[str, bytes]:
    mission = load_mission(mission_path)
    result: dict[str, bytes] = {}
    for operation in mission.operations:
        if operation.operation == "DELETE":
            raise SealedAdapterError("DELETE is not supported by Spear Issue R01", "SPEAR_ISSUE_DELETE_UNSUPPORTED_R01", "PACKAGE_AUDIT")
        assert operation.payload is not None
        path = package_root / mission.payload_root / operation.payload
        if not path.is_file() or path.is_symlink():
            raise SealedAdapterError("candidate payload is unavailable", "PAYLOAD_REJECTED", "PACKAGE_AUDIT")
        result[operation.path] = path.read_bytes()
    return result



def _candidate_git_tree(mission_path: Path, candidate_files: dict[str, bytes]) -> str:
    mission = load_mission(mission_path)
    root = Path(tempfile.mkdtemp(prefix="atlas-sealed-tree-"))
    try:
        checkout = root / "checkout"
        _run(["git", "clone", "--no-tags", mission.remote_url, str(checkout)])
        _run(["git", "checkout", "--detach", mission.base_sha], cwd=checkout)
        if _run(["git", "status", "--porcelain=v1"], cwd=checkout):
            raise SealedAdapterError("candidate tree checkout is dirty", "DIRTY_CHECKOUT", "PACKAGE_AUDIT")
        for path, data in candidate_files.items():
            target = checkout / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        _run(["git", "add", "--", *sorted(candidate_files)], cwd=checkout)
        changed = sorted(_run(["git", "diff", "--cached", "--name-only"], cwd=checkout).splitlines())
        if changed != sorted(candidate_files):
            raise SealedAdapterError("candidate tree path set mismatch", "PATH_SET_MISMATCH", "PACKAGE_AUDIT")
        tree = _run(["git", "write-tree"], cwd=checkout)
        if not SHA40.fullmatch(tree):
            raise SealedAdapterError("candidate tree identity malformed", "TREE_REJECTED", "PACKAGE_AUDIT")
        return tree
    finally:
        shutil.rmtree(root, ignore_errors=True)

def _remote_state(repository: str, branch: str) -> dict[str, Any]:
    ref = subprocess.run(
        ["gh", "api", f"repos/{repository}/git/ref/heads/{branch}"],
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
            raise SealedAdapterError("remote branch state malformed", "REMOTE_STATE_READBACK_FAILED", "READBACK", partial=True) from exc
        if not isinstance(head_sha, str) or not SHA40.fullmatch(head_sha):
            raise SealedAdapterError("remote branch head malformed", "REMOTE_STATE_READBACK_FAILED", "READBACK", partial=True)
    elif "404" not in ref.stderr and "Not Found" not in ref.stderr:
        raise SealedAdapterError("remote branch readback ambiguous", "REMOTE_STATE_READBACK_FAILED", "READBACK", partial=True)
    prs_text = _run([
        "gh", "pr", "list", "--repo", repository, "--state", "all", "--head", branch,
        "--json", "number,state,isDraft,headRefName,headRefOid,baseRefName",
    ])
    try:
        prs = json.loads(prs_text or "[]")
    except json.JSONDecodeError as exc:
        raise SealedAdapterError("remote PR state malformed", "REMOTE_STATE_READBACK_FAILED", "READBACK", partial=True) from exc
    if not isinstance(prs, list) or len(prs) > 1:
        raise SealedAdapterError("remote PR state ambiguous", "REMOTE_STATE_READBACK_FAILED", "READBACK", partial=True)
    return {"branch_exists": branch_exists, "head_sha": head_sha, "pull_request": prs[0] if prs else None}



def _verify_remote_candidate(mission_path: Path, package_root: Path, head_sha: str) -> bool:
    mission = load_mission(mission_path)
    root = Path(tempfile.mkdtemp(prefix="atlas-sealed-partial-readback-"))
    try:
        checkout = root / "checkout"
        _run(["git", "clone", "--no-tags", mission.remote_url, str(checkout)])
        _run(["git", "checkout", "--detach", head_sha], cwd=checkout)
        topology = _run(["git", "rev-list", "--parents", "-n", "1", "HEAD"], cwd=checkout).split()
        if topology != [head_sha, mission.base_sha]:
            return False
        if _run(["git", "log", "-1", "--format=%s"], cwd=checkout) != mission.commit_message:
            return False
        changed = sorted(_run(["git", "diff", "--name-only", f"{mission.base_sha}..HEAD"], cwd=checkout).splitlines())
        if changed != sorted(mission.declared_paths):
            return False
        for operation in mission.operations:
            target = checkout / operation.path
            if operation.operation == "DELETE":
                if target.exists():
                    return False
                continue
            if not target.is_file() or target.is_symlink():
                return False
            assert operation.expected_output_sha256 is not None
            if sha256_bytes(target.read_bytes()) != operation.expected_output_sha256:
                return False
        return True
    except AdapterError:
        return False
    finally:
        shutil.rmtree(root, ignore_errors=True)

def _partial_receipt(exc: AdapterError, mission_path: Path, package_root: Path, seal: dict[str, Any] | None) -> dict[str, Any]:
    mission = load_mission(mission_path)
    try:
        remote = _remote_state(mission.repository, mission.branch)
        state = "YES_EXACT" if remote["branch_exists"] else "NO"
    except AdapterError:
        remote = {"branch_exists": None, "head_sha": None, "pull_request": None}
        state = "UNKNOWN"
    expected_head = None
    if exc.receipt and isinstance(exc.receipt.get("head_sha"), str):
        expected_head = exc.receipt["head_sha"]
    observed = remote.get("head_sha")
    if state == "YES_EXACT":
        if expected_head is None and isinstance(observed, str) and _verify_remote_candidate(mission_path, package_root, observed):
            expected_head = observed
        if expected_head is None or observed != expected_head:
            state = "UNKNOWN"
    return {
        "schema_version": "atlas.thread-engine.sealed-partial.v1",
        "result": "PARTIAL",
        "mission_id": mission.mission_id,
        "mission_sha256": mission.mission_sha256,
        "base_sha": mission.base_sha,
        "branch": mission.branch,
        "seal_id": None if seal is None else seal["seal_id"],
        "seal_sha256": None if seal is None else seal["seal_sha256"],
        "error_code": exc.code,
        "error_stage": exc.stage,
        "last_completed_checkpoint": None if not exc.receipt else exc.receipt.get("last_completed_checkpoint"),
        "expected_head_sha": expected_head,
        "remote_mutation": state,
        "remote_state": remote,
        "automatic_retry": False,
        "allowed_next_action": "EXACT_RESUME_REQUIRED" if state == "YES_EXACT" else "BLOCKED_RESUMABLE",
    }



def reconcile_adapter_error(
    mission_path: Path,
    *,
    package_root: Path,
    error: AdapterError,
) -> dict[str, Any] | None:
    if error.stage not in POST_PUSH_STAGES and not error.partial:
        return error.receipt
    return _partial_receipt(error, mission_path, package_root, None)

def execute_sealed_mission(
    mission_path: Path,
    *,
    package_root: Path,
    seal_path: Path,
    context_path: Path,
    mission_sha256: str | None = None,
    work_root: Path | None = None,
) -> dict[str, Any]:
    mission = load_mission(mission_path)
    context = json.loads(context_path.read_text(encoding="utf-8"))
    seal = json.loads(seal_path.read_text(encoding="utf-8"))
    candidate_files = _candidate_files(mission_path, package_root)
    observed_tree = _candidate_git_tree(mission_path, candidate_files)
    if observed_tree != context.get("expected_candidate_tree_sha"):
        raise SealedAdapterError("candidate Git tree drifted", "TREE_DRIFT", "PACKAGE_AUDIT")
    mission_identity = {
        "repository": mission.repository,
        "issue_number": context["issue_number"],
        "mission_id": mission.mission_id,
        "attempt_id": context["attempt_id"],
        "objective": context["objective"],
    }
    try:
        verification = verify_candidate_seal(
            seal,
            canonical_base_sha=mission.base_sha,
            branch_intent=mission.branch,
            candidate_files=candidate_files,
            expected_candidate_tree_sha=observed_tree,
            expected_head_sha=context.get("expected_head_sha"),
            prepublication_checks=context["prepublication_checks"],
            consumed_seal_ids=context.get("consumed_seal_ids", []),
        )
    except (CandidateSealError, KeyError, TypeError, ValueError) as exc:
        raise SealedAdapterError(str(exc), getattr(exc, "code", "CANDIDATE_SEAL_REJECTED"), "PACKAGE_AUDIT") from exc
    identity_expectations = {
        "repository": mission_identity["repository"],
        "issue_number": mission_identity["issue_number"],
        "mission_id": mission_identity["mission_id"],
        "attempt_id": mission_identity["attempt_id"],
        "objective_sha256": sha256_text(mission_identity["objective"]),
    }
    if any(seal.get(key) != value for key, value in identity_expectations.items()):
        raise SealedAdapterError("candidate seal Mission identity mismatch", "CANDIDATE_SEAL_REJECTED", "PACKAGE_AUDIT")
    if seal.get("route") != "SPEAR_DIRECT_ISSUE" or seal.get("authorizer") != "JAYSON" or seal.get("operator") != "ATHENA":
        raise SealedAdapterError("candidate seal route identity mismatch", "CANDIDATE_SEAL_REJECTED", "PACKAGE_AUDIT")
    try:
        receipt = execute_mission(
            mission_path,
            mission_scoped=True,
            execute_draft_pr=True,
            mission_sha256=mission_sha256 or mission.mission_sha256,
            work_root=work_root,
            package_root=package_root,
        )
    except AdapterError as exc:
        if exc.stage in POST_PUSH_STAGES or exc.partial:
            partial = _partial_receipt(exc, mission_path, package_root, seal)
            wrapped = SealedAdapterError("Thread Engine stopped after possible remote mutation", exc.code, exc.stage, partial=True)
            wrapped.receipt = partial
            raise wrapped from exc
        raise
    receipt["candidate_seal"] = {
        "seal_id": seal["seal_id"],
        "seal_sha256": seal["seal_sha256"],
        "verification_sha256": sha256_bytes(stable_json(verification).encode("utf-8")),
    }
    return receipt



def _exact_pr_readback(mission: Any, expected_head: str) -> dict[str, Any]:
    raw = _run([
        "gh", "pr", "view", mission.branch, "--repo", mission.repository,
        "--json", "number,state,isDraft,baseRefName,baseRefOid,headRefName,headRefOid,title,body",
    ])
    try:
        pr = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SealedAdapterError("exact PR readback malformed", "REMOTE_STATE_READBACK_FAILED", "READBACK", partial=True) from exc
    expected = {
        "state": "OPEN",
        "isDraft": True,
        "baseRefName": "main",
        "baseRefOid": mission.base_sha,
        "headRefName": mission.branch,
        "headRefOid": expected_head,
        "title": mission.pr_title,
        "body": mission.pr_body,
    }
    if not isinstance(pr, dict) or any(pr.get(key) != value for key, value in expected.items()) or type(pr.get("number")) is not int:
        raise SealedAdapterError("exact PR readback mismatch", "PARTIAL_STATE_AMBIGUOUS", "READBACK", partial=True)
    return pr

def resume_exact_partial(
    mission_path: Path,
    *,
    partial_receipt_path: Path,
    seal_path: Path,
) -> dict[str, Any]:
    mission = load_mission(mission_path)
    partial = json.loads(partial_receipt_path.read_text(encoding="utf-8"))
    seal = json.loads(seal_path.read_text(encoding="utf-8"))
    required = {
        "schema_version": "atlas.thread-engine.sealed-partial.v1",
        "result": "PARTIAL",
        "mission_id": mission.mission_id,
        "mission_sha256": mission.mission_sha256,
        "base_sha": mission.base_sha,
        "branch": mission.branch,
        "seal_id": seal["seal_id"],
        "seal_sha256": seal["seal_sha256"],
    }
    for key, value in required.items():
        if partial.get(key) != value:
            raise SealedAdapterError(f"partial receipt mismatch: {key}", "PARTIAL_RECEIPT_MISMATCH", "READBACK", partial=True)
    if partial.get("automatic_retry") is not False:
        raise SealedAdapterError("partial receipt permits unsafe retry", "PARTIAL_RECEIPT_MISMATCH", "READBACK", partial=True)
    remote = _remote_state(mission.repository, mission.branch)
    expected_head = partial.get("expected_head_sha")
    if not remote["branch_exists"] or not expected_head or remote["head_sha"] != expected_head:
        raise SealedAdapterError("exact partial branch is unavailable", "PARTIAL_STATE_AMBIGUOUS", "READBACK", partial=True)
    pr = remote["pull_request"]
    if pr is None:
        body_file = partial_receipt_path.parent / "resume-pr-body.md"
        body_file.write_text(mission.pr_body, encoding="utf-8", newline="\n")
        _run([
            "gh", "pr", "create", "--repo", mission.repository, "--base", "main", "--head", mission.branch,
            "--title", mission.pr_title, "--body-file", str(body_file), "--draft",
        ])
        remote = _remote_state(mission.repository, mission.branch)
        pr = remote["pull_request"]
    pr = _exact_pr_readback(mission, expected_head)
    return {
        "schema_version": "atlas.thread-engine.sealed-resume.v1",
        "result": "RECOVERED_SUCCESS",
        "mission_id": mission.mission_id,
        "mission_sha256": mission.mission_sha256,
        "base_sha": mission.base_sha,
        "branch": mission.branch,
        "head_sha": expected_head,
        "pull_request": pr,
        "seal_id": seal["seal_id"],
        "seal_sha256": seal["seal_sha256"],
        "automatic_retry": False,
        "stop_point": "DRAFT_PR_READBACK",
    }
