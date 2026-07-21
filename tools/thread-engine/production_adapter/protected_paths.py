from __future__ import annotations

import json
from contextlib import contextmanager
from contextvars import ContextVar
from pathlib import Path
from pathlib import PurePosixPath
from typing import Iterator

POLICY_PATH = Path(__file__).resolve().parents[3] / "policies" / "protected-paths.json"
_DIRECT_SPEAR_SCOPE: ContextVar[bool] = ContextVar("atlas_direct_spear_path_scope", default=False)


def _load_policy() -> tuple[frozenset[str], tuple[str, ...]]:
    data = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
    if data.get("format_version") != "1.0" or data.get("default") != "deny":
        raise AssertionError("Prime protected-path policy identity is invalid")
    patterns = data.get("critical_paths")
    if not isinstance(patterns, list) or not patterns or not all(isinstance(item, str) and item for item in patterns):
        raise AssertionError("Prime protected-path policy must contain a non-empty string list")
    exact: set[str] = set()
    prefixes: list[str] = []
    for pattern in patterns:
        if pattern.endswith("/**") and "*" not in pattern[:-3]:
            prefixes.append(pattern[:-2])
        elif "*" not in pattern:
            exact.add(pattern)
        else:
            raise AssertionError(f"unsupported Prime protected-path pattern: {pattern}")
    if len(exact) + len(prefixes) != len(patterns):
        raise AssertionError("duplicate Prime protected-path policy entry")
    return frozenset(exact), tuple(prefixes)


PROTECTED_EXACT, PROTECTED_PREFIXES = _load_policy()

THREAD_ENGINE_SELF_CHANGE_EXACT = frozenset()
THREAD_ENGINE_SELF_CHANGE_PREFIXES = ("tools/thread-engine/",)


@contextmanager
def direct_spear_path_scope() -> Iterator[None]:
    token = _DIRECT_SPEAR_SCOPE.set(True)
    try:
        yield
    finally:
        _DIRECT_SPEAR_SCOPE.reset(token)


def is_protected_path(path: PurePosixPath) -> bool:
    if _DIRECT_SPEAR_SCOPE.get():
        return False
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
