from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path

from .git_environment import controlled_environment, git_safe_prefix
from .readback import REVIEW_THREAD_QUERY


class GitRunnerError(Exception):
    pass


@dataclass(frozen=True)
class Completed:
    args: tuple[str, ...]
    returncode: int
    stdout: str
    stderr: str


class GitRunner:
    """Exact-template wrapper around git and gh for one disabled adapter mission."""

    def __init__(
        self,
        *,
        allowed_remote: str,
        allowed_api_prefix: str,
        mission_branch: str,
        base_sha: str,
        declared_paths: tuple[str, ...],
        commit_message: str,
        pr_title: str,
        disabled_hooks: Path,
    ) -> None:
        self.allowed_remote = allowed_remote
        self.allowed_api_prefix = allowed_api_prefix
        self.mission_branch = mission_branch
        self.base_sha = base_sha
        self.declared_paths = declared_paths
        self.commit_message = commit_message
        self.pr_title = pr_title
        self.disabled_hooks = disabled_hooks

    def run(self, args: list[str], cwd: Path | None = None) -> Completed:
        if not args:
            raise GitRunnerError("empty command rejected")
        self._validate(args)
        actual = self._actual_args(args)
        completed = subprocess.run(
            actual,
            cwd=str(cwd) if cwd else None,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=controlled_environment(self.disabled_hooks),
        )
        if completed.returncode != 0:
            raise GitRunnerError(completed.stderr.strip() or completed.stdout.strip() or "command failed")
        return Completed(tuple(args), completed.returncode, completed.stdout, completed.stderr)

    def _actual_args(self, args: list[str]) -> list[str]:
        if args[0] == "git":
            return git_safe_prefix(self.disabled_hooks) + args[1:]
        return args

    def _validate(self, args: list[str]) -> None:
        if args[0] == "git":
            self._validate_git(args)
            return
        if args[0] == "gh":
            self._validate_gh(args)
            return
        raise GitRunnerError(f"command rejected: {args[0]}")

    def _validate_git(self, args: list[str]) -> None:
        denied_tokens = {"--force", "-f", "--force-with-lease", "--mirror", "--all", "--tags", "--delete", "--prune", "--amend", "--reset-author"}
        if any(token in denied_tokens or token.startswith("+") or token == ":" or token.startswith(":") for token in args):
            raise GitRunnerError("unsafe git token rejected")
        exact_templates = [
            ["git", "ls-remote", self.allowed_remote, "refs/heads/main"],
            ["git", "ls-remote", self.allowed_remote, f"refs/heads/{self.mission_branch}"],
            ["git", "clone", "--no-tags", self.allowed_remote, "<path>"],
            ["git", "rev-parse", "HEAD"],
            ["git", "rev-parse", "HEAD^"],
            ["git", "rev-parse", f"{self.base_sha}:.github/workflows/generated-checkpoint-publisher.yml"],
            ["git", "rev-list", "--parents", "-n", "1", "HEAD"],
            ["git", "log", "-1", "--format=%s"],
            ["git", "show", "--format=%T", "--no-patch", "HEAD"],
            ["git", "status", "--porcelain=v1"],
            ["git", "diff", "--check"],
            ["git", "diff", "--cached", "--check"],
            ["git", "diff", "--cached", "--name-only"],
            ["git", "diff", "--name-only", f"{self.base_sha}..HEAD"],
            ["git", "switch", "-c", self.mission_branch, self.base_sha],
            ["git", "add", "--", *self.declared_paths],
            ["git", "commit", "-m", self.commit_message],
            ["git", "push", "-u", "origin", self.mission_branch],
        ]
        if args[:3] == ["git", "hash-object", "--"] and len(args) == 4 and args[3] in self.declared_paths:
            return
        for template in exact_templates:
            if template == ["git", "clone", "--no-tags", self.allowed_remote, "<path>"]:
                if len(args) == 5 and args[:4] == template[:4] and args[4]:
                    return
            elif args == template:
                return
        raise GitRunnerError(f"git command template rejected: {' '.join(args)}")

    def _validate_gh(self, args: list[str]) -> None:
        if args == ["gh", "api", "user", "--jq", ".login"]:
            return
        review_thread_query = [
            "gh",
            "api",
            "graphql",
            "-f",
            f"query={REVIEW_THREAD_QUERY}",
            "-f",
            "owner=Jktomy",
            "-f",
            "name=atlas-prime",
            "-f",
            f"head={self.mission_branch}",
        ]
        if args == review_thread_query:
            return
        denied = {"merge", "ready", "close", "reopen", "edit", "delete", "enable-auto-merge", "api", "workflow", "run", "release", "repo"}
        if any(token in denied for token in args[1:]):
            raise GitRunnerError("unsafe gh command rejected")
        allowed_view_fields = "number,url,state,isDraft,baseRefName,baseRefOid,headRefName,headRefOid,title,body,files,commits,comments,reviews"
        templates = [
            ["gh", "pr", "list", "--repo", "Jktomy/atlas-prime", "--state", "all", "--head", self.mission_branch, "--json", "number,state,isDraft,headRefOid"],
            ["gh", "pr", "list", "--repo", "Jktomy/atlas-prime", "--state", "all", "--limit", "1000", "--json", "number,state,isDraft,headRefName,headRefOid,title,body"],
            ["gh", "pr", "view", self.mission_branch, "--repo", "Jktomy/atlas-prime", "--json", allowed_view_fields],
            ["gh", "pr", "checks", self.mission_branch, "--repo", "Jktomy/atlas-prime"],
        ]
        for template in templates:
            if args == template:
                return
        if (
            len(args) == 14
            and args[:7] == ["gh", "pr", "create", "--repo", "Jktomy/atlas-prime", "--base", "main"]
            and args[7:9] == ["--head", self.mission_branch]
            and args[9:11] == ["--title", self.pr_title]
            and args[11] == "--body-file"
            and args[12]
            and args[13] == "--draft"
        ):
            return
        raise GitRunnerError(f"gh command template rejected: {' '.join(args)}")
