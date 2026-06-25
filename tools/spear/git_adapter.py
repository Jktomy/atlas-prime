from __future__ import annotations

import subprocess
from pathlib import Path

from .models import GitError

_ALLOWED_READ_COMMANDS = {"rev-parse", "ls-files", "cat-file", "show", "status"}


def _run_git(repo: str | Path, args: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    if not args or args[0] not in _ALLOWED_READ_COMMANDS:
        raise GitError("unsafe_git_command", "git adapter permits read-only Git commands only in S0")
    completed = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=False,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if check and completed.returncode != 0:
        stderr = completed.stderr.strip()
        if "dubious ownership" in stderr.lower():
            raise GitError("unsafe_repository_ownership", "Git refused repository ownership")
        raise GitError("git_failure", "git read failed")
    return completed


def assert_git_repository(repo: str | Path) -> Path:
    root = Path(repo).resolve()
    if not root.exists() or not root.is_dir():
        raise GitError("missing_repository", "repository path does not exist")
    completed = _run_git(root, ["rev-parse", "--show-toplevel"], check=False)
    if completed.returncode != 0:
        stderr = completed.stderr.strip()
        if "dubious ownership" in stderr.lower():
            raise GitError("unsafe_repository_ownership", "Git refused repository ownership")
        raise GitError("invalid_repository", "path is not a valid Git repository")
    actual = Path(completed.stdout.strip()).resolve()
    if actual != root:
        raise GitError("repository_root_mismatch", "supplied repository is not the Git root")
    return actual


def current_head(repo: str | Path) -> str:
    return _run_git(repo, ["rev-parse", "HEAD"]).stdout.strip()


def current_branch(repo: str | Path) -> str:
    return _run_git(repo, ["rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()


def resolve_ref(repo: str | Path, ref: str) -> str:
    completed = _run_git(repo, ["rev-parse", "--verify", ref], check=False)
    if completed.returncode != 0:
        raise GitError("missing_ref", "base ref cannot be resolved")
    value = completed.stdout.strip()
    if len(value) != 40:
        raise GitError("invalid_ref", "resolved ref is not a 40-character Git object")
    return value


def object_type(repo: str | Path, object_name: str) -> str:
    completed = _run_git(repo, ["cat-file", "-t", object_name], check=False)
    if completed.returncode != 0:
        raise GitError("missing_git_object", "Git object is missing or invalid")
    return completed.stdout.strip()


def assert_commit(repo: str | Path, commit: str) -> None:
    if object_type(repo, commit) != "commit":
        raise GitError("invalid_base_commit", "base object is not a commit")


def tracked_paths(repo: str | Path) -> list[str]:
    return [line for line in _run_git(repo, ["ls-files"]).stdout.splitlines() if line]


def blob_sha_at_commit(repo: str | Path, commit: str, path: str) -> str | None:
    assert_commit(repo, commit)
    spec = f"{commit}:{path}"
    completed = _run_git(repo, ["cat-file", "-t", spec], check=False)
    if completed.returncode != 0:
        stderr = completed.stderr.lower()
        if "path" in stderr or "exists on disk" in stderr or "not exist" in stderr or "not a valid object name" in stderr:
            return None
        raise GitError("git_failure", "Git failed while reading target object")
    kind = completed.stdout.strip()
    if kind != "blob":
        raise GitError("invalid_git_object", "operation target is not a regular blob")
    sha = _run_git(repo, ["rev-parse", spec]).stdout.strip()
    if len(sha) != 40:
        raise GitError("invalid_git_object", "target blob SHA is invalid")
    return sha


def file_bytes_at_commit(repo: str | Path, commit: str, path: str) -> bytes:
    assert_commit(repo, commit)
    completed = subprocess.run(
        ["git", "-C", str(repo), "show", f"{commit}:{path}"],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if completed.returncode != 0:
        raise GitError("missing_path", "file is missing at commit")
    return completed.stdout