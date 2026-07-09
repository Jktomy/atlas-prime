from __future__ import annotations

from pathlib import PurePosixPath

PROTECTED_EXACT = {
    "codex/atlas-active-workboard.md",
    "codex/atlas-change-paths.md",
    "codex/atlas-strikeforce.md",
    "codex/codex-source-update-standard.md",
    "codex/gate-7-dual-path-proof.md",
    "codex/thread-engine-spear-weave-contract.md",
    "atlas-aegis.md",
    "atlas-sword.md",
    "noctua.md",
    "thread-engine.md",
}

PROTECTED_PREFIXES = (
    ".git/",
    ".github/workflows/",
    "generated/",
    "tools/atlas-sword/",
    "tools/thread-engine/",
)

THREAD_ENGINE_SELF_CHANGE_EXACT = frozenset(
    {
        "codex/thread-engine-spear-weave-contract.md",
        "thread-engine.md",
    }
)

THREAD_ENGINE_SELF_CHANGE_PREFIXES = (
    "tools/thread-engine/",
)


def is_protected_path(path: PurePosixPath) -> bool:
    value = path.as_posix()
    if value in PROTECTED_EXACT:
        return True
    return any(value == prefix.rstrip("/") or value.startswith(prefix) for prefix in PROTECTED_PREFIXES)


def is_thread_engine_self_change_path(path: PurePosixPath) -> bool:
    value = path.as_posix()
    if value in THREAD_ENGINE_SELF_CHANGE_EXACT:
        return True
    return any(value == prefix.rstrip("/") or value.startswith(prefix) for prefix in THREAD_ENGINE_SELF_CHANGE_PREFIXES)


def assert_thread_engine_self_change_policy_is_protected() -> None:
    for value in THREAD_ENGINE_SELF_CHANGE_EXACT:
        if value not in PROTECTED_EXACT:
            raise AssertionError(f"Thread Engine self-change path is not protected: {value}")
    for prefix in THREAD_ENGINE_SELF_CHANGE_PREFIXES:
        if prefix not in PROTECTED_PREFIXES:
            raise AssertionError(f"Thread Engine self-change prefix is not protected: {prefix}")


assert_thread_engine_self_change_policy_is_protected()
