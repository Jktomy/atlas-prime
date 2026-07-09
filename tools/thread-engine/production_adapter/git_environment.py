from __future__ import annotations

import os
from pathlib import Path


def controlled_environment(disabled_hooks: Path) -> dict[str, str]:
    env: dict[str, str] = {}
    for key in ("PATH", "SystemRoot", "WINDIR", "HOME", "USERPROFILE", "APPDATA", "LOCALAPPDATA", "GH_TOKEN", "GITHUB_TOKEN"):
        value = os.environ.get(key)
        if value:
            env[key] = value
    env.update(
        {
            "GIT_TERMINAL_PROMPT": "0",
            "GIT_ASKPASS": "",
            "GIT_EDITOR": ":",
            "GIT_SEQUENCE_EDITOR": ":",
            "GIT_MERGE_AUTOEDIT": "no",
            "GIT_EXTERNAL_DIFF": "",
            "GIT_PAGER": "cat",
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_ATTR_NOSYSTEM": "1",
            "ATLAS_GIT_HOOKS_DISABLED_DIR": str(disabled_hooks),
        }
    )
    return env


def git_safe_prefix(disabled_hooks: Path) -> list[str]:
    return [
        "git",
        "-c",
        f"core.hooksPath={disabled_hooks.as_posix()}",
        "-c",
        "commit.gpgsign=false",
        "-c",
        "tag.gpgSign=false",
        "-c",
        "core.pager=cat",
        "-c",
        "credential.interactive=false",
        "-c",
        "core.longpaths=true",
        "-c",
        "core.autocrlf=false",
        "-c",
        "core.eol=lf",
        "-c",
        "protocol.file.allow=never",
        "-c",
        "protocol.ext.allow=never",
    ]
