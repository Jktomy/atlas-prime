from __future__ import annotations

import ctypes
import inspect
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from production_adapter.git_environment import git_safe_prefix


def run(
    args: list[str],
    *,
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
    input_text: str | None = None,
) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        args,
        cwd=str(cwd) if cwd else None,
        env=env,
        input=input_text,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        raise AssertionError(
            f"command failed with {completed.returncode}: {' '.join(args)}\n"
            f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}"
        )
    return completed


def run_binary(
    args: list[str],
    *,
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
    input_bytes: bytes | None = None,
) -> subprocess.CompletedProcess[bytes]:
    completed = subprocess.run(
        args,
        cwd=str(cwd) if cwd else None,
        env=env,
        input=input_bytes,
        text=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        stdout = completed.stdout.decode("utf-8", errors="replace")
        stderr = completed.stderr.decode("utf-8", errors="replace")
        raise AssertionError(
            f"command failed with {completed.returncode}: {' '.join(args)}\n"
            f"stdout:\n{stdout}\nstderr:\n{stderr}"
        )
    return completed


def fixture_clone_prefix(disabled_hooks: Path) -> list[str]:
    prefix = git_safe_prefix(disabled_hooks)
    return [
        "protocol.file.allow=always" if value == "protocol.file.allow=never" else value
        for value in prefix
    ]


def config_values(prefix: list[str]) -> set[str]:
    return {
        prefix[index + 1]
        for index, value in enumerate(prefix[:-1])
        if value == "-c"
    }


def create_bare_long_path_repository(root: Path) -> tuple[Path, str, str]:
    source = root / "source.git"
    run(["git", "init", "--bare", "-q", str(source)])

    git_dir = ["git", f"--git-dir={source}"]
    blob = run_binary(
        [*git_dir, "hash-object", "-w", "--stdin"],
        input_bytes=b"long path fixture\n",
    ).stdout.decode("ascii").strip()
    tree = run_binary(
        [*git_dir, "mktree", "-z"],
        input_bytes=f"100644 blob {blob}\tfile.txt\0".encode("utf-8"),
    ).stdout.decode("ascii").strip()

    segments = tuple(f"segment-{index:02d}-" + ("x" * 36) for index in range(7))
    for segment in reversed(segments[1:]):
        tree = run_binary(
            [*git_dir, "mktree", "-z"],
            input_bytes=f"040000 tree {tree}\t{segment}\0".encode("utf-8"),
        ).stdout.decode("ascii").strip()
    root_tree = run_binary(
        [*git_dir, "mktree", "-z"],
        input_bytes=f"040000 tree {tree}\t{segments[0]}\0".encode("utf-8"),
    ).stdout.decode("ascii").strip()

    identity = dict(os.environ)
    identity.update(
        {
            "GIT_AUTHOR_NAME": "Atlas Fixture",
            "GIT_AUTHOR_EMAIL": "atlas-fixture@example.invalid",
            "GIT_COMMITTER_NAME": "Atlas Fixture",
            "GIT_COMMITTER_EMAIL": "atlas-fixture@example.invalid",
        }
    )
    commit = run_binary(
        [*git_dir, "commit-tree", root_tree],
        env=identity,
        input_bytes=b"long path fixture\n",
    ).stdout.decode("ascii").strip()
    run([*git_dir, "update-ref", "refs/heads/main", commit])
    run([*git_dir, "symbolic-ref", "HEAD", "refs/heads/main"])
    return source, "/".join((*segments, "file.txt")), blob


def normalize_windows_attributes(path: Path) -> None:
    os.chmod(path, stat.S_IWRITE | stat.S_IREAD)
    if os.name == "nt":
        result = ctypes.windll.kernel32.SetFileAttributesW(str(path), 0x80)
        if result == 0:
            raise ctypes.WinError()


def remove_readonly(function: Any, name: str, exc: BaseException) -> None:
    del exc
    normalize_windows_attributes(Path(name))
    function(name)


def rmtree_with_readonly_handler(path: Path) -> None:
    parameters = inspect.signature(shutil.rmtree).parameters
    if "onexc" in parameters:
        shutil.rmtree(path, onexc=remove_readonly)
        return

    def legacy_handler(function: Any, name: str, exc_info: Any) -> None:
        remove_readonly(function, name, exc_info[1])

    shutil.rmtree(path, onerror=legacy_handler)


def remove_long_path_fixture(root: Path, clone: Path, hooks: Path) -> None:
    if clone.is_dir() and (clone / ".git").is_dir():
        # Git has the same command-scoped long-path support used for checkout.
        # Remove tracked deep files through Git before Python removes the short shell.
        run(
            [
                *fixture_clone_prefix(hooks),
                "rm",
                "-r",
                "-f",
                "--ignore-unmatch",
                "--",
                ".",
            ],
            cwd=clone,
        )
        run(
            [
                *fixture_clone_prefix(hooks),
                "clean",
                "-fdx",
            ],
            cwd=clone,
        )
    rmtree_with_readonly_handler(root)


class GitEnvironmentContractTests(unittest.TestCase):
    def test_safe_prefix_binds_windows_and_line_ending_controls(self) -> None:
        prefix = git_safe_prefix(Path("disabled-hooks"))
        values = config_values(prefix)
        self.assertIn("core.longpaths=true", values)
        self.assertIn("core.autocrlf=false", values)
        self.assertIn("core.eol=lf", values)
        self.assertIn("protocol.file.allow=never", values)
        self.assertIn("protocol.ext.allow=never", values)

    def test_readonly_cleanup_handler_removes_file(self) -> None:
        with tempfile.TemporaryDirectory(prefix="atlas-thread-engine-readonly-") as tmp:
            root = Path(tmp) / "fixture"
            root.mkdir()
            target = root / "readonly.txt"
            target.write_text("fixture\n", encoding="utf-8", newline="\n")
            os.chmod(target, stat.S_IREAD)
            rmtree_with_readonly_handler(root)
            self.assertFalse(root.exists())

    def test_hostile_autocrlf_does_not_rewrite_checkout_bytes(self) -> None:
        with tempfile.TemporaryDirectory(prefix="atlas-thread-engine-eol-") as tmp:
            root = Path(tmp)
            source = root / "source"
            clone = root / "clone"
            hooks = root / "hooks"
            hooks.mkdir()

            run(["git", "init", "-q", "-b", "main", str(source)])
            run(["git", "config", "user.name", "Atlas Fixture"], cwd=source)
            run(["git", "config", "user.email", "atlas-fixture@example.invalid"], cwd=source)
            data = b"line one\nline two\n"
            (source / "line.txt").write_bytes(data)
            run(["git", "-c", "core.autocrlf=false", "add", "line.txt"], cwd=source)
            run(["git", "-c", "core.autocrlf=false", "commit", "-qm", "fixture"], cwd=source)

            hostile = dict(os.environ)
            hostile.update(
                {
                    "GIT_CONFIG_COUNT": "1",
                    "GIT_CONFIG_KEY_0": "core.autocrlf",
                    "GIT_CONFIG_VALUE_0": "true",
                }
            )
            run(
                [
                    *fixture_clone_prefix(hooks),
                    "clone",
                    "--no-tags",
                    source.resolve().as_uri(),
                    str(clone),
                ],
                env=hostile,
            )
            self.assertEqual((clone / "line.txt").read_bytes(), data)

    def test_long_path_checkout_succeeds_with_command_scoped_control(self) -> None:
        root = Path(tempfile.mkdtemp(prefix="atlas-thread-engine-longpath-"))
        clone = root / "clone"
        hooks = root / "hooks"
        hooks.mkdir()
        try:
            source, relative, expected_blob = create_bare_long_path_repository(root)
            run(
                [
                    *fixture_clone_prefix(hooks),
                    "clone",
                    "--no-tags",
                    source.resolve().as_uri(),
                    str(clone),
                ]
            )

            target_text = str(clone.joinpath(*relative.split("/")))
            self.assertGreater(len(target_text), 260)

            # Do not ask ordinary Python Win32 path APIs to open a >260 path.
            # Git performs checkout and byte readback with core.longpaths=true.
            observed_blob = run(
                [
                    *fixture_clone_prefix(hooks),
                    "hash-object",
                    "--no-filters",
                    "--",
                    relative,
                ],
                cwd=clone,
            ).stdout.strip()
            self.assertEqual(observed_blob, expected_blob)

            run(
                [
                    *fixture_clone_prefix(hooks),
                    "diff-files",
                    "--quiet",
                    "--",
                    relative,
                ],
                cwd=clone,
            )
        finally:
            remove_long_path_fixture(root, clone, hooks)


if __name__ == "__main__":
    unittest.main()
