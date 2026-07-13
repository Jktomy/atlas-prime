from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any, Callable, Sequence

from tools import build_index


SHA_RE = re.compile(r"^[0-9a-f]{40}$")
NONCE_RE = re.compile(r"^[A-Za-z0-9._-]{12,128}$")
APPROVED_PATHS = tuple(f"generated/{name}" for name in build_index.APPROVED_OUTPUTS)


class CheckpointError(ValueError):
    pass


def stable_json(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def deterministic_branch(base_sha: str, replay_nonce: str) -> str:
    if not SHA_RE.fullmatch(base_sha) or not NONCE_RE.fullmatch(replay_nonce):
        raise CheckpointError("IDENTITY_INVALID")
    nonce_digest = sha256(replay_nonce.encode("utf-8"))[:16]
    return f"generated/checkpoint-{base_sha[:12]}-{nonce_digest}"


def validate_changed_paths(paths: Sequence[str]) -> list[str]:
    normalized = sorted(set(paths))
    if not normalized or any(path not in APPROVED_PATHS for path in normalized):
        raise CheckpointError("GENERATED_PATHSET_INVALID")
    return normalized


def build_hash_register(repo_root: Path, output_dir: Path) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    output_dir = output_dir.resolve()
    if output_dir.is_relative_to(repo_root):
        raise CheckpointError("PARITY_OUTPUT_INSIDE_REPOSITORY")
    outputs, fingerprint = build_index.build_outputs(repo_root)
    hashes = build_index.write_outputs(outputs, output_dir)
    record = {
        "schema_version": "atlas.generated-checkpoint-hashes.v1",
        "generator_format": build_index.GENERATOR_FORMAT,
        "source_fingerprint": f"sha256:{fingerprint}",
        "files": [{"path": name, "sha256": hashes[name]} for name in build_index.APPROVED_OUTPUTS],
    }
    (output_dir / "hash-register.json").write_bytes(stable_json(record))
    return record


def compare_hash_registers(left: dict[str, Any], right: dict[str, Any]) -> None:
    if stable_json(left) != stable_json(right):
        raise CheckpointError("CROSS_PLATFORM_PARITY_MISMATCH")


def validate_pr_readback(readback: dict[str, Any], *, branch: str, head_sha: str, base_sha: str,
                         expected_paths: Sequence[str]) -> None:
    expected = {
        "baseRefName": "main",
        "baseRefOid": base_sha,
        "headRefName": branch,
        "headRefOid": head_sha,
        "isDraft": True,
        "state": "OPEN",
    }
    if any(readback.get(key) != value for key, value in expected.items()):
        raise CheckpointError("PR_READBACK_MISMATCH")
    files = sorted(item.get("path") for item in readback.get("files", []))
    if validate_changed_paths(files) != sorted(expected_paths):
        raise CheckpointError("PR_PATHSET_MISMATCH")


def _run(arguments: Sequence[str], *, cwd: Path) -> str:
    completed = subprocess.run(arguments, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if completed.returncode != 0:
        raise CheckpointError(f"COMMAND_FAILED:{arguments[0]}:{completed.stderr.strip()[:300]}")
    return completed.stdout.strip()


def publish(repo_root: Path, *, repository: str, base_sha: str, replay_nonce: str, run_id: str,
            receipt_path: Path, runner: Callable[[Sequence[str]], str] | None = None) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    if repository != "Jktomy/atlas-prime" or not run_id.isdigit():
        raise CheckpointError("PUBLISH_IDENTITY_INVALID")
    branch = deterministic_branch(base_sha, replay_nonce)
    receipt_path = receipt_path.resolve()
    if receipt_path.is_relative_to(repo_root) or receipt_path.exists():
        raise CheckpointError("RECEIPT_PATH_INVALID")
    invoke = runner or (lambda args: _run(args, cwd=repo_root))
    if invoke(["git", "rev-parse", "HEAD"]) != base_sha:
        raise CheckpointError("LOCAL_BASE_MISMATCH")
    if invoke(["git", "status", "--porcelain"]):
        raise CheckpointError("WORKTREE_NOT_CLEAN")
    remote = invoke(["git", "ls-remote", "origin", "refs/heads/main"]).split()
    if len(remote) != 2 or remote[0] != base_sha or remote[1] != "refs/heads/main":
        raise CheckpointError("REMOTE_BASE_STALE")
    if invoke(["git", "ls-remote", "origin", f"refs/heads/{branch}"]):
        raise CheckpointError("REPLAY_BRANCH_EXISTS")
    existing = json.loads(invoke(["gh", "pr", "list", "--repo", repository, "--head", branch, "--state", "all", "--json", "number"]) or "[]")
    if existing:
        raise CheckpointError("REPLAY_PR_EXISTS")

    outputs, _fingerprint = build_index.build_outputs(repo_root)
    build_index.write_outputs(outputs, repo_root / "generated")
    paths = validate_changed_paths(invoke(["git", "diff", "--name-only"]).splitlines())
    invoke(["git", "diff", "--check"])
    invoke(["git", "switch", "-c", branch])
    invoke(["git", "add", "--", *paths])
    staged = validate_changed_paths(invoke(["git", "diff", "--cached", "--name-only"]).splitlines())
    if staged != paths:
        raise CheckpointError("STAGED_PATHSET_MISMATCH")
    invoke(["git", "-c", "user.name=github-actions[bot]", "-c", "user.email=41898282+github-actions[bot]@users.noreply.github.com", "commit", "-m", "generated: publish immutable checkpoint"])
    head_sha = invoke(["git", "rev-parse", "HEAD"])
    remote_before_push = invoke(["git", "ls-remote", "origin", "refs/heads/main"]).split()
    if len(remote_before_push) != 2 or remote_before_push[0] != base_sha:
        raise CheckpointError("REMOTE_BASE_DRIFT_BEFORE_PUSH")
    invoke(["git", "push", "origin", f"HEAD:refs/heads/{branch}"])
    url = invoke(["gh", "pr", "create", "--repo", repository, "--base", "main", "--head", branch, "--draft", "--title", "Generated: immutable checkpoint", "--body", f"Owner-triggered exact-base generated-only checkpoint from `{base_sha}`. Workflow run `{run_id}`. Generated projections report and do not govern."])
    readback = json.loads(invoke(["gh", "pr", "view", url, "--repo", repository, "--json", "number,url,state,isDraft,baseRefName,baseRefOid,headRefName,headRefOid,files"]))
    validate_pr_readback(readback, branch=branch, head_sha=head_sha, base_sha=base_sha, expected_paths=paths)
    receipt = {
        "schema_version": "atlas.generated-checkpoint-publisher-receipt.v1",
        "result": "SUCCESS",
        "repository": repository,
        "base_sha": base_sha,
        "branch": branch,
        "replay_nonce_sha256": sha256(replay_nonce.encode("utf-8")),
        "workflow_run": run_id,
        "changed_paths": paths,
        "head_sha": head_sha,
        "pull_request": readback["number"],
        "pull_request_url": readback["url"],
        "draft": True,
        "stop_point": "DRAFT_PR_READBACK",
        "forbidden_actions": {"direct_main": False, "force_push": False, "ready": False, "merge": False, "second_writer": False},
    }
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    with receipt_path.open("xb") as handle:
        handle.write(stable_json(receipt))
    return receipt
