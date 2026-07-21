from __future__ import annotations

from pathlib import Path, PurePosixPath
from typing import Iterable

from .protected_paths import is_protected_path

RUNTIME_BYPRODUCTS = {"__pycache__", ".pytest_cache"}
RUNTIME_SUFFIXES = {".pyc", ".pyo"}


class PolicyError(Exception):
    def __init__(self, message: str, code: str = "POLICY_REJECTED") -> None:
        super().__init__(message)
        self.code = code


def validate_relative_path(value: str) -> PurePosixPath:
    if not isinstance(value, str) or not value:
        raise PolicyError("path must be a non-empty string", "PATH_REJECTED")
    if "\\" in value:
        raise PolicyError(f"backslash path rejected: {value}", "PATH_REJECTED")
    path = PurePosixPath(value)
    if path.is_absolute() or ":" in value:
        raise PolicyError(f"absolute path rejected: {value}", "PATH_REJECTED")
    if any(part in ("", ".", "..") for part in path.parts):
        raise PolicyError(f"traversal or empty path segment rejected: {value}", "PATH_REJECTED")
    return path


def validate_safe_filename(value: str, *, reserved: set[str] | None = None) -> str:
    reserved = reserved or set()
    if not isinstance(value, str) or value in {"", ".", ".."}:
        raise PolicyError("receipt_name must be a safe filename", "RECEIPT_NAME_REJECTED")
    if "/" in value or "\\" in value or ":" in value:
        raise PolicyError("receipt_name must not contain path separators or drive prefixes", "RECEIPT_NAME_REJECTED")
    if value in reserved:
        raise PolicyError("receipt_name collides with reserved evidence file", "RECEIPT_NAME_REJECTED")
    if not value.endswith(".json"):
        raise PolicyError("receipt_name must end with .json", "RECEIPT_NAME_REJECTED")
    return value


def resolve_under(root: Path, relative: PurePosixPath) -> Path:
    root_resolved = root.resolve()
    target = root.joinpath(*relative.parts).resolve(strict=False)
    try:
        target.relative_to(root_resolved)
    except ValueError as exc:
        raise PolicyError(f"path escapes root: {relative.as_posix()}", "BOUNDARY_REJECTED") from exc
    return target


def reject_runtime_byproducts(root: Path) -> None:
    for path in root.rglob("*"):
        if path.name in RUNTIME_BYPRODUCTS or path.suffix in RUNTIME_SUFFIXES:
            raise PolicyError(f"runtime byproduct rejected: {path.name}", "RUNTIME_BYPRODUCT")


def reject_symlinks(root: Path) -> None:
    for path in root.rglob("*"):
        if path.is_symlink():
            raise PolicyError(f"symlink rejected: {path.relative_to(root).as_posix()}", "SYMLINK_REJECTED")


def validate_declared_path_set(paths: Iterable[str], *, allow_protected: bool = False) -> list[PurePosixPath]:
    seen: dict[str, str] = {}
    result: list[PurePosixPath] = []
    for value in paths:
        rel = validate_relative_path(value)
        if not allow_protected and is_protected_path(rel):
            raise PolicyError(f"protected path requires a separate route: {rel.as_posix()}", "PROTECTED_PATH")
        folded = rel.as_posix().casefold()
        if folded in seen:
            raise PolicyError(f"duplicate or case-fold collision rejected: {rel.as_posix()}", "PATH_COLLISION")
        seen[folded] = rel.as_posix()
        result.append(rel)
    return result
