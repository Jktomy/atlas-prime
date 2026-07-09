from __future__ import annotations

import os
import re
import stat
import subprocess
import tempfile
import shutil
import time
from dataclasses import dataclass
from pathlib import Path

from production_adapter.git_environment import controlled_environment, git_safe_prefix


EXPECTED_REMOTE = "https://github.com/Jktomy/atlas-prime.git"
TOKEN_REMOTE_PATTERN = re.compile(r"^https://x-access-token:[^/@]+@github\.com/Jktomy/atlas-prime\.git$")
DISPOSAL_PREFIX = "atlas-spear-bridge-git-"
MAX_DISPOSAL_ATTEMPTS = 5
DISPOSAL_BACKOFF_SECONDS = (0.05, 0.1, 0.2, 0.4)


class GitReaderError(Exception):
    pass


class SourceAbsentError(GitReaderError):
    pass


@dataclass(frozen=True)
class SourceFile:
    data: bytes
    sha256: str
    blob: str


class GitReader:
    """Read-only Git substrate for Spear bridge compilation."""

    def __init__(self, *, remote_url: str = EXPECTED_REMOTE, base_sha: str, work_root: Path | None = None) -> None:
        self.remote_url = remote_url
        self.base_sha = base_sha
        self.observed_base: str | None = None
        self.root = Path(tempfile.mkdtemp(prefix=DISPOSAL_PREFIX, dir=str(work_root) if work_root else None))
        self._owned_root = self.root.resolve(strict=False)
        self._closed = False
        self.hooks = self.root / "disabled-hooks"
        self.hooks.mkdir()
        self.checkout = self.root / "checkout"

    def _run(self, args: list[str], cwd: Path | None = None) -> str:
        self._validate(args)
        actual = git_safe_prefix(self.hooks) + args[1:]
        env = controlled_environment(self.hooks)
        env["GCM_INTERACTIVE"] = "Never"
        completed = subprocess.run(
            actual,
            cwd=str(cwd) if cwd else None,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=env,
        )
        if completed.returncode != 0:
            message = completed.stderr.strip() or completed.stdout.strip() or "git command failed"
            raise GitReaderError(self._sanitize_git_message(message))
        return completed.stdout

    def _validate(self, args: list[str]) -> None:
        if not args or args[0] != "git":
            raise GitReaderError("only git read commands are allowed")
        denied = {"add", "commit", "branch", "push", "tag", "reset", "clean", "update-ref"}
        if len(args) > 1 and args[1] in denied:
            raise GitReaderError("mutating git command rejected")
        if any(token.startswith("+") or token in {"--force", "-f", "--force-with-lease", "--mirror", "--all"} for token in args):
            raise GitReaderError("unsafe git option rejected")
        if self.remote_url != EXPECTED_REMOTE and not TOKEN_REMOTE_PATTERN.match(self.remote_url):
            raise GitReaderError("remote URL is not an approved read-only repository route")
        allowed = [
            ["git", "ls-remote", self.remote_url, "refs/heads/main"],
            ["git", "clone", "--no-tags", self.remote_url, "<path>"],
            ["git", "checkout", "--detach", self.base_sha],
            ["git", "rev-parse", "HEAD"],
            ["git", "status", "--porcelain=v1"],
            ["git", "hash-object", "--", "<path>"],
        ]
        if args[:3] == ["git", "hash-object", "--"] and len(args) == 4:
            return
        for template in allowed:
            if template[-1] == "<path>":
                if len(args) == len(template) and args[:-1] == template[:-1] and args[-1]:
                    return
            elif args == template:
                return
        raise GitReaderError(f"git command rejected: {' '.join(args)}")

    def _sanitize_git_message(self, message: str) -> str:
        if self.remote_url != EXPECTED_REMOTE:
            message = message.replace(self.remote_url, EXPECTED_REMOTE)
        return re.sub(r"https://x-access-token:[^/@]+@github\.com/", "https://github.com/", message)

    def prepare(self) -> None:
        remote = self._run(["git", "ls-remote", self.remote_url, "refs/heads/main"]).strip().split()
        if not remote or remote[0] != self.base_sha:
            raise GitReaderError("canonical main does not match expected base")
        self._run(["git", "clone", "--no-tags", self.remote_url, str(self.checkout)])
        self._run(["git", "checkout", "--detach", self.base_sha], cwd=self.checkout)
        observed = self._run(["git", "rev-parse", "HEAD"], cwd=self.checkout).strip()
        self.observed_base = observed
        if observed != self.base_sha:
            raise GitReaderError("checkout head mismatch")
        if self._run(["git", "status", "--porcelain=v1"], cwd=self.checkout).strip():
            raise GitReaderError("read-only checkout is dirty")

    def read_source(self, path: str) -> SourceFile:
        target = self.checkout.joinpath(*path.split("/"))
        if not target.exists():
            raise SourceAbsentError(f"source file is absent: {path}")
        if target.is_symlink() or not target.is_file():
            raise GitReaderError(f"source file is not a regular file: {path}")
        import hashlib

        data = target.read_bytes()
        blob = self._run(["git", "hash-object", "--", path], cwd=self.checkout).strip()
        if not blob:
            raise GitReaderError(f"source blob hash failed: {path}")
        return SourceFile(data=data, sha256=hashlib.sha256(data).hexdigest(), blob=blob)

    def close(self) -> None:
        if self._closed and not self.root.exists():
            return
        self._validate_owned_root()
        if not self.root.exists():
            self._closed = True
            return
        last_error: Exception | None = None
        for attempt in range(MAX_DISPOSAL_ATTEMPTS):
            try:
                self._make_owned_tree_writable()
                self._remove_owned_root_once()
            except Exception as exc:  # noqa: BLE001 - preserve fail-closed disposal semantics.
                last_error = exc
            if not self.root.exists():
                self._closed = True
                return
            if attempt < MAX_DISPOSAL_ATTEMPTS - 1:
                time.sleep(DISPOSAL_BACKOFF_SECONDS[min(attempt, len(DISPOSAL_BACKOFF_SECONDS) - 1)])
        raise GitReaderError("failed to dispose read-only clone") from last_error

    def _validate_owned_root(self) -> None:
        if self.root.resolve(strict=False) != self._owned_root:
            raise GitReaderError("refusing to dispose unexpected GitReader root")
        if not self.root.name.startswith(DISPOSAL_PREFIX):
            raise GitReaderError("refusing to dispose unexpected GitReader root")
        if self.root.is_symlink():
            raise GitReaderError("refusing to dispose symlink GitReader root")

    def _remove_owned_root_once(self) -> None:
        if hasattr(shutil.rmtree, "__call__"):
            try:
                shutil.rmtree(self.root, onexc=self._clear_readonly_and_retry)
                return
            except TypeError:
                shutil.rmtree(self.root, onerror=self._clear_readonly_and_retry_legacy)
                return

    def _clear_readonly_and_retry(self, function, path: str, excinfo) -> None:
        self._retry_after_write_bit_restore(function, Path(path), excinfo)

    def _clear_readonly_and_retry_legacy(self, function, path: str, excinfo) -> None:
        self._retry_after_write_bit_restore(function, Path(path), excinfo)

    def _retry_after_write_bit_restore(self, function, path: Path, excinfo) -> None:
        self._assert_owned_descendant(path)
        if path.is_symlink():
            raise GitReaderError("refusing to remediate symlink during clone disposal")
        try:
            current_mode = path.stat().st_mode
        except OSError:
            current_mode = stat.S_IRUSR | stat.S_IXUSR
        os.chmod(path, current_mode | stat.S_IWUSR)
        function(path)

    def _make_owned_tree_writable(self) -> None:
        if not self.root.exists():
            return
        targets = sorted(self.root.rglob("*"), key=lambda item: len(item.parts), reverse=True)
        targets.append(self.root)
        for target in targets:
            self._assert_owned_descendant(target)
            if target.is_symlink() or not target.exists():
                continue
            try:
                mode = target.stat().st_mode
                write_mode = mode | stat.S_IWUSR
                if target.is_dir():
                    write_mode |= stat.S_IXUSR
                os.chmod(target, write_mode)
            except OSError:
                continue

    def _assert_owned_descendant(self, path: Path) -> None:
        target = path.resolve(strict=False)
        try:
            target.relative_to(self._owned_root)
        except ValueError as exc:
            raise GitReaderError("refusing to dispose path outside owned GitReader root") from exc
