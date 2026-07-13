from __future__ import annotations

import json
import os
import re
import stat
from contextlib import contextmanager
from contextvars import ContextVar
from pathlib import Path
from typing import Any, Iterator

from .core import (
    InvestitureError,
    ROOT,
    ZERO_SHA256,
    build_manifest,
    build_record,
    build_summary,
    event_from_bytes,
    sha256_bytes,
    sha256_object,
    stable_json,
    strict_loads,
    validate_against_schema,
    validate_manifest,
    validate_record,
)


MAX_JSON_BYTES = 1_000_000
RECORD_NAME = re.compile(r"^(?P<sequence>[0-9]{8})-(?P<digest>[a-f0-9]{64})[.]json$")
RECORD_TEMP_NAME = re.compile(r"^[.](?P<request>[a-f0-9]{64})(?:[.]recovery)?[.]tmp$")
EVIDENCE_NAME = re.compile(r"^(?P<identity>[a-f0-9]{64})[.]json$")
EVIDENCE_TEMP_NAME = re.compile(r"^[.](?P<identity>[a-f0-9]{64})[.](?P<kind>intent|receipt|quarantine|recovery)[.]tmp$")
INTENT_FIELDS = {"schema_version", "request_id_sha256", "expected_head", "input_sha256", "input_byte_count", "record", "intent_sha256"}
ALLOWED_ROOT_ENTRIES = {"manifest.json", "records", "receipts", "quarantine", "intents", "recoveries", "append.lock"}
STORE_DIRECTORIES = ("records", "receipts", "quarantine", "intents", "recoveries")
_ACTIVE_VIEW: ContextVar[tuple[str, dict[str, Path], tuple[int, int]] | None] = ContextVar("investiture_active_view", default=None)


def _open_windows_directory(path: Path):
    import ctypes
    from ctypes import wintypes

    create_file = ctypes.windll.kernel32.CreateFileW
    create_file.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, wintypes.LPVOID, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
    create_file.restype = wintypes.HANDLE
    handle = create_file(str(path), 0x00000001, 0x00000001 | 0x00000002, None, 3, 0x02000000 | 0x00200000, None)
    if handle == wintypes.HANDLE(-1).value:
        raise OSError(ctypes.get_last_error(), "directory handle open failed")
    return handle


def _close_windows_handle(handle) -> None:
    import ctypes

    if not ctypes.windll.kernel32.CloseHandle(handle):
        raise OSError(ctypes.get_last_error(), "directory handle close failed")


@contextmanager
def _stable_directory(path: Path, expected_identity: tuple[int, int]) -> Iterator[Path]:
    handle = None
    descriptor: int | None = None
    try:
        before = path.lstat()
        if not stat.S_ISDIR(before.st_mode) or _is_reparse(path) or (before.st_dev, before.st_ino) != expected_identity:
            raise InvestitureError("STORE_ROOT_IDENTITY_CHANGED")
        if os.name == "nt":
            handle = _open_windows_directory(path)
            stable = path
        else:
            descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0))
            stable = Path(f"/proc/self/fd/{descriptor}")
            if not stable.exists():
                raise InvestitureError("STABLE_DIRECTORY_HANDLE_UNAVAILABLE")
        after = path.lstat()
        if (
            _is_reparse(path)
            or (after.st_dev, after.st_ino) != expected_identity
            or _identity(stable) != expected_identity
        ):
            raise InvestitureError("STORE_ROOT_IDENTITY_CHANGED")
        yield stable
    finally:
        if descriptor is not None:
            os.close(descriptor)
        if handle is not None:
            _close_windows_handle(handle)


@contextmanager
def _mutation_view(path: Path, expected_identity: tuple[int, int]) -> Iterator[Path]:
    with _stable_directory(path, expected_identity) as stable_root:
        handles: list[Any] = []
        descriptors: list[int] = []
        children: dict[str, Path] = {}
        try:
            for name in STORE_DIRECTORIES:
                child = stable_root / name
                before = child.lstat()
                if not stat.S_ISDIR(before.st_mode) or _is_reparse(child):
                    raise InvestitureError("STORE_LAYOUT_INVALID")
                if os.name == "nt":
                    handles.append(_open_windows_directory(child))
                    stable_child = child
                else:
                    descriptor = os.open(child, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0))
                    descriptors.append(descriptor)
                    stable_child = Path(f"/proc/self/fd/{descriptor}")
                after = child.lstat()
                if (
                    not stable_child.is_dir()
                    or _is_reparse(child)
                    or (before.st_dev, before.st_ino) != (after.st_dev, after.st_ino)
                    or _identity(stable_child) != (before.st_dev, before.st_ino)
                ):
                    raise InvestitureError("STORE_LAYOUT_INVALID")
                children[name] = stable_child
            token = _ACTIVE_VIEW.set((str(stable_root), children, expected_identity))
            try:
                yield stable_root
            finally:
                _ACTIVE_VIEW.reset(token)
        finally:
            for descriptor in reversed(descriptors):
                os.close(descriptor)
            for handle in reversed(handles):
                _close_windows_handle(handle)


def _child(root: Path, name: str) -> Path:
    active = _ACTIVE_VIEW.get()
    if active is not None and str(root) == active[0]:
        return active[1][name]
    return root / name


def _guarded_identity(root: Path) -> tuple[int, int] | None:
    active = _ACTIVE_VIEW.get()
    if active is not None and str(root) == active[0]:
        return active[2]
    return None


def _is_reparse(path: Path) -> bool:
    try:
        info = path.lstat()
    except OSError:
        return False
    if stat.S_ISLNK(info.st_mode):
        return True
    if getattr(os.path, "isjunction", lambda _: False)(path):
        return True
    attributes = getattr(info, "st_file_attributes", 0)
    return bool(attributes & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0))


def _existing_chain(path: Path) -> list[Path]:
    current = path
    missing: list[Path] = []
    while not current.exists() and not current.is_symlink():
        missing.append(current)
        if current.parent == current:
            break
        current = current.parent
    chain = list(reversed(list(current.parents))) + [current]
    return chain + list(reversed(missing))


def validate_external_root(path: Path, *, must_exist: bool) -> Path:
    if not path.is_absolute():
        raise InvestitureError("STORE_ROOT_ABSOLUTE_REQUIRED")
    raw = Path(os.path.abspath(path))
    for item in _existing_chain(raw):
        if (item.exists() or item.is_symlink()) and _is_reparse(item):
            raise InvestitureError("STORE_ROOT_REPARSE_REJECTED")
    resolved = raw.resolve(strict=False)
    repo = ROOT.resolve()
    if resolved == repo or resolved.is_relative_to(repo) or repo.is_relative_to(resolved):
        raise InvestitureError("STORE_ROOT_REPOSITORY_OVERLAP")
    for parent in (resolved, *resolved.parents):
        marker = parent / ".git"
        if marker.exists() or marker.is_symlink():
            raise InvestitureError("STORE_ROOT_REPOSITORY_CONTAINED")
    if must_exist:
        if not raw.is_dir() or _is_reparse(raw):
            raise InvestitureError("STORE_ROOT_INVALID")
    elif raw.exists() or raw.is_symlink():
        raise InvestitureError("STORE_ROOT_MUST_BE_NEW")
    return raw


def _identity(root: Path) -> tuple[int, int]:
    info = root.stat()
    return info.st_dev, info.st_ino


def _assert_identity(root: Path, expected: tuple[int, int]) -> None:
    if _guarded_identity(root) is None:
        validate_external_root(root, must_exist=True)
    if (_guarded_identity(root) is None and _is_reparse(root)) or _identity(root) != expected:
        raise InvestitureError("STORE_ROOT_IDENTITY_CHANGED")


def _safe_file(path: Path, *, allowed_links: tuple[int, ...] = (1,)) -> None:
    if not path.is_file() or _is_reparse(path):
        raise InvestitureError("LEDGER_FILE_INVALID")
    info = path.stat()
    if info.st_size > MAX_JSON_BYTES or info.st_nlink not in allowed_links:
        raise InvestitureError("LEDGER_FILE_UNSAFE")


def _read_same_handle(path: Path, *, allowed_links: tuple[int, ...] = (1,)) -> bytes:
    _safe_file(path, allowed_links=allowed_links)
    before = path.lstat()
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags)
    try:
        opened = os.fstat(descriptor)
        if (
            not stat.S_ISREG(opened.st_mode)
            or opened.st_nlink not in allowed_links
            or opened.st_size > MAX_JSON_BYTES
            or (opened.st_dev, opened.st_ino) != (before.st_dev, before.st_ino)
        ):
            raise InvestitureError("LEDGER_FILE_HANDLE_MISMATCH")
        chunks: list[bytes] = []
        while True:
            chunk = os.read(descriptor, 65536)
            if not chunk:
                break
            chunks.append(chunk)
        raw = b"".join(chunks)
        opened_after = os.fstat(descriptor)
    finally:
        os.close(descriptor)
    after = path.lstat()
    identity = (before.st_dev, before.st_ino)
    if (opened_after.st_dev, opened_after.st_ino) != identity or (after.st_dev, after.st_ino) != identity or after.st_size != len(raw):
        raise InvestitureError("LEDGER_FILE_HANDLE_MISMATCH")
    return raw


def _load_canonical(path: Path, code: str) -> dict[str, Any]:
    raw = _read_same_handle(path)
    try:
        value = strict_loads(raw)
    except InvestitureError as exc:
        raise InvestitureError(code) from exc
    if raw != stable_json(value):
        raise InvestitureError(code)
    return value


def _sync_directory(path: Path) -> None:
    if os.name == "nt":
        return
    nofollow = 0 if path.as_posix().startswith("/proc/self/fd/") else getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | nofollow)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _windows_move_no_clobber_write_through(source: Path, target: Path) -> None:
    import ctypes
    from ctypes import wintypes

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    move_file = kernel32.MoveFileExW
    move_file.argtypes = [wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.DWORD]
    move_file.restype = wintypes.BOOL
    if move_file(str(source), str(target), 0x00000008):
        return
    error = ctypes.get_last_error()
    if error in {80, 183}:
        raise FileExistsError(error, "publication target already exists", str(target))
    raise OSError(error, "write-through publication failed", str(target))


def _write_exclusive(path: Path, payload: bytes) -> None:
    parent_before = path.parent.stat()
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    flags |= getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags, 0o600)
    try:
        opened = os.fstat(descriptor)
        if not stat.S_ISREG(opened.st_mode) or opened.st_nlink != 1:
            raise InvestitureError("LEDGER_FILE_HANDLE_MISMATCH")
        with os.fdopen(descriptor, "wb", closefd=False) as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        opened_after = os.fstat(descriptor)
    finally:
        os.close(descriptor)
    parent_after = path.parent.stat()
    published = path.lstat()
    if (
        (parent_before.st_dev, parent_before.st_ino) != (parent_after.st_dev, parent_after.st_ino)
        or (opened_after.st_dev, opened_after.st_ino) != (published.st_dev, published.st_ino)
        or published.st_size != len(payload)
        or published.st_nlink != 1
    ):
        raise InvestitureError("LEDGER_FILE_HANDLE_MISMATCH")
    _sync_directory(path.parent)


def _publish_no_clobber(temporary: Path, target: Path) -> None:
    payload = _read_same_handle(temporary)
    if target.exists() or target.is_symlink():
        raise InvestitureError("LEDGER_PUBLICATION_COLLISION")
    try:
        if os.name == "nt":
            _windows_move_no_clobber_write_through(temporary, target)
        else:
            os.link(temporary, target, follow_symlinks=False)
            temporary.unlink()
    except FileExistsError as exc:
        raise InvestitureError("LEDGER_PUBLICATION_COLLISION") from exc
    _safe_file(target)
    if _read_same_handle(target) != payload:
        raise InvestitureError("LEDGER_FILE_HANDLE_MISMATCH")
    _sync_directory(target.parent)


def _write_atomic_evidence(path: Path, payload: bytes, *, kind: str) -> None:
    if not EVIDENCE_NAME.fullmatch(path.name):
        raise InvestitureError("EVIDENCE_FILENAME_INVALID")
    temporary = path.parent / f".{path.stem}.{kind}.tmp"
    if temporary.exists() or temporary.is_symlink():
        if _read_same_handle(temporary) != payload:
            raise InvestitureError("BLOCKED_STATE_DIVERGENCE")
    else:
        _write_exclusive(temporary, payload)
    _publish_no_clobber(temporary, path)


def _reconcile_atomic_evidence(root: Path, identity: str, kind: str) -> None:
    directory_name = {"intent": "intents", "receipt": "receipts", "quarantine": "quarantine", "recovery": "recoveries"}[kind]
    directory = _child(root, directory_name)
    temporary = directory / f".{identity}.{kind}.tmp"
    target = directory / f"{identity}.json"
    if not temporary.exists() and not temporary.is_symlink():
        return
    links = temporary.lstat().st_nlink
    if target.exists() or target.is_symlink():
        target_info = target.lstat()
        temporary_info = temporary.lstat()
        if links != 2 or (target_info.st_dev, target_info.st_ino) != (temporary_info.st_dev, temporary_info.st_ino):
            raise InvestitureError("BLOCKED_STATE_DIVERGENCE")
        temporary.unlink()
        _sync_directory(directory)
        return
    raw = _read_same_handle(temporary)
    value = _load_canonical(temporary, f"{kind.upper()}_JSON_INVALID")
    if kind == "intent":
        _validate_intent(value)
        if value["request_id_sha256"] != identity:
            raise InvestitureError("BLOCKED_STATE_DIVERGENCE")
    else:
        digest_field = "recovery_sha256" if kind == "recovery" else "receipt_sha256"
        body = {key: child for key, child in value.items() if key != digest_field}
        if value.get(digest_field) != sha256_object(body):
            raise InvestitureError("BLOCKED_STATE_DIVERGENCE")
    _publish_no_clobber(temporary, target)
    if _read_same_handle(target) != raw:
        raise InvestitureError("BLOCKED_STATE_DIVERGENCE")


def _acquire_append_lock(root: Path):
    path = root / "append.lock"
    _safe_file(path)
    if os.name != "nt":
        nofollow = 0 if root.as_posix().startswith("/proc/self/fd/") else getattr(os, "O_NOFOLLOW", 0)
        descriptor = os.open(root, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | nofollow)
        try:
            import fcntl
            fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            os.close(descriptor)
            raise InvestitureError("APPEND_LOCK_BUSY") from exc
        return descriptor
    handle = path.open("r+b", buffering=0)
    opened = os.fstat(handle.fileno())
    current = path.lstat()
    if (opened.st_dev, opened.st_ino) != (current.st_dev, current.st_ino):
        handle.close()
        raise InvestitureError("LEDGER_FILE_HANDLE_MISMATCH")
    try:
        import msvcrt
        handle.seek(0)
        msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
    except OSError as exc:
        handle.close()
        raise InvestitureError("APPEND_LOCK_BUSY") from exc
    return handle


def _release_append_lock(handle) -> None:
    if isinstance(handle, int):
        try:
            import fcntl
            fcntl.flock(handle, fcntl.LOCK_UN)
        finally:
            os.close(handle)
        return
    try:
        import msvcrt
        handle.seek(0)
        msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
    finally:
        handle.close()


def _acquire_mutation(root: Path, expected_identity: tuple[int, int]):
    original_root = root
    view = _mutation_view(root, expected_identity)
    stable_root = view.__enter__()
    try:
        lock_handle = _acquire_append_lock(stable_root)
    except Exception:
        view.__exit__(None, None, None)
        raise
    child_identities = {name: _identity(_child(stable_root, name)) for name in STORE_DIRECTORIES}
    root_entries = tuple(sorted(item.name for item in stable_root.iterdir()))
    lock_info = (stable_root / "append.lock").lstat()
    lock_identity = (lock_info.st_dev, lock_info.st_ino, lock_info.st_nlink)
    mutation_state = {
        "original_root": original_root,
        "stable_root": stable_root,
        "expected_identity": expected_identity,
        "child_identities": child_identities,
        "root_entries": root_entries,
        "lock_identity": lock_identity,
        "sealed_snapshot": None,
    }
    return stable_root, view, lock_handle, mutation_state


def _seal_mutation_state(mutation_state, lock_handle) -> None:
    mutation_state["sealed_snapshot"] = _store_snapshot(mutation_state["stable_root"], lock_handle=lock_handle)


def _release_mutation(view, lock_handle, mutation_state) -> None:
    original_root = mutation_state["original_root"]
    expected_identity = mutation_state["expected_identity"]
    child_identities = mutation_state["child_identities"]
    root_entries = mutation_state["root_entries"]
    lock_identity = mutation_state["lock_identity"]
    drifted = False
    try:
        drifted = _identity(original_root) != expected_identity or any(
            _identity(original_root / name) != identity for name, identity in child_identities.items()
        )
        current_lock = (original_root / "append.lock").lstat()
        drifted = drifted or tuple(sorted(item.name for item in original_root.iterdir())) != root_entries
        drifted = drifted or (current_lock.st_dev, current_lock.st_ino, current_lock.st_nlink) != lock_identity
        if mutation_state["sealed_snapshot"] is not None:
            drifted = drifted or _store_snapshot(
                mutation_state["stable_root"], lock_handle=lock_handle
            ) != mutation_state["sealed_snapshot"]
    except (OSError, InvestitureError):
        drifted = True
    try:
        _release_append_lock(lock_handle)
    finally:
        view.__exit__(None, None, None)
    if drifted:
        raise InvestitureError("STORE_ROOT_IDENTITY_CHANGED")


def _unresolved_intents(root: Path) -> list[Path]:
    return [
        path for path in _child(root, "intents").iterdir()
        if EVIDENCE_NAME.fullmatch(path.name) and not (_child(root, "receipts") / path.name).is_file()
    ]


def _evidence_temporary_files(root: Path) -> list[Path]:
    return [
        path
        for name in ("intents", "receipts", "quarantine", "recoveries")
        for path in _child(root, name).iterdir()
        if EVIDENCE_TEMP_NAME.fullmatch(path.name)
    ]


def initialize_store(store_root: Path, *, ledger_id: str, generation_id: str, created_at: str) -> dict[str, Any]:
    return _initialize_store(store_root, ledger_id=ledger_id, generation_id=generation_id, created_at=created_at)


def _initialize_store(store_root: Path, *, ledger_id: str, generation_id: str, created_at: str,
                      previous_generation_id: str | None = None,
                      previous_last_record_sha256: str | None = None,
                      inherited_summary: dict[str, Any] | None = None,
                      inherited_identities: dict[str, list[str]] | None = None) -> dict[str, Any]:
    root = validate_external_root(store_root, must_exist=False)
    manifest = build_manifest(
        ledger_id=ledger_id,
        generation_id=generation_id,
        created_at=created_at,
        previous_generation_id=previous_generation_id,
        previous_last_record_sha256=previous_last_record_sha256,
        inherited_summary=inherited_summary,
        inherited_identities=inherited_identities,
    )
    parent = root.parent
    parent_identity = _identity(parent)
    with _stable_directory(parent, parent_identity) as stable_parent:
        stable_root = stable_parent / root.name
        if stable_root.exists() or stable_root.is_symlink():
            raise InvestitureError("STORE_ROOT_MUST_BE_NEW")
        stable_root.mkdir(mode=0o700)
        identity = _identity(stable_root)
        with _stable_directory(stable_root, identity) as held_root:
            for name in STORE_DIRECTORIES:
                (held_root / name).mkdir(mode=0o700)
            _write_exclusive(held_root / "manifest.json", stable_json(manifest))
            _write_exclusive(held_root / "append.lock", b"0")
            _sync_directory(held_root)
        _sync_directory(stable_parent)
    try:
        if _identity(root) != identity or any(not (root / name).is_dir() or _is_reparse(root / name) for name in STORE_DIRECTORIES):
            raise InvestitureError("STORE_ROOT_IDENTITY_CHANGED")
    except OSError as exc:
        raise InvestitureError("STORE_ROOT_IDENTITY_CHANGED") from exc
    return manifest


def load_manifest(store_root: Path, *, allow_publication_pair: bool = False) -> tuple[Path, dict[str, Any], tuple[int, int]]:
    guarded = _guarded_identity(store_root)
    root = store_root if guarded is not None else validate_external_root(store_root, must_exist=True)
    identity = _identity(root)
    if guarded is not None and identity != guarded:
        raise InvestitureError("STORE_ROOT_IDENTITY_CHANGED")
    entries = {item.name for item in root.iterdir()}
    if not entries.issubset(ALLOWED_ROOT_ENTRIES):
        raise InvestitureError("STORE_LAYOUT_INVALID")
    for name in ("records", "receipts", "quarantine", "intents", "recoveries"):
        child = _child(root, name)
        if not child.is_dir() or (_guarded_identity(root) is None and _is_reparse(child)):
            raise InvestitureError("STORE_LAYOUT_INVALID")
        for descendant in child.iterdir():
            if descendant.is_dir() or _is_reparse(descendant):
                raise InvestitureError("STORE_LAYOUT_INVALID")
            allowed_links = (1, 2) if allow_publication_pair else (1,)
            _safe_file(descendant, allowed_links=allowed_links)
    lock = root / "append.lock"
    if not lock.is_file() or lock.is_symlink() or lock.stat().st_size != 1:
        raise InvestitureError("APPEND_LOCK_INVALID")
    manifest = _load_canonical(root / "manifest.json", "MANIFEST_JSON_INVALID")
    validate_manifest(manifest)
    _assert_identity(root, identity)
    return root, manifest, identity


def _record_files(root: Path) -> list[Path]:
    files = sorted(_child(root, "records").iterdir(), key=lambda item: item.name)
    if any(not RECORD_NAME.fullmatch(item.name) and not RECORD_TEMP_NAME.fullmatch(item.name) for item in files):
        raise InvestitureError("RECORD_FILENAME_INVALID")
    return [item for item in files if RECORD_NAME.fullmatch(item.name)]


def _record_temporary_files(root: Path) -> list[Path]:
    return sorted(
        (item for item in _child(root, "records").iterdir() if RECORD_TEMP_NAME.fullmatch(item.name)),
        key=lambda item: item.name,
    )


def _reconcile_linked_publication(root: Path, request_digest: str) -> None:
    linked = [item for item in _child(root, "records").iterdir() if item.lstat().st_nlink == 2]
    if not linked:
        return
    record_paths = [item for item in linked if RECORD_NAME.fullmatch(item.name)]
    temporary_paths = [
        item for item in linked
        if (match := RECORD_TEMP_NAME.fullmatch(item.name)) and match.group("request") == request_digest
    ]
    if len(linked) != 2 or len(record_paths) != 1 or len(temporary_paths) != 1:
        raise InvestitureError("BLOCKED_STATE_DIVERGENCE")
    target, temporary = record_paths[0], temporary_paths[0]
    target_info = target.lstat()
    temporary_info = temporary.lstat()
    if (target_info.st_dev, target_info.st_ino) != (temporary_info.st_dev, temporary_info.st_ino):
        raise InvestitureError("BLOCKED_STATE_DIVERGENCE")
    intent_path = _child(root, "intents") / f"{request_digest}.json"
    if not intent_path.exists():
        raise InvestitureError("BLOCKED_STATE_DIVERGENCE")
    intent = _load_canonical(intent_path, "INTENT_JSON_INVALID")
    _validate_intent(intent)
    record = intent.get("record")
    if (
        intent["request_id_sha256"] != request_digest
        or not isinstance(record, dict)
        or not isinstance(record.get("sequence"), int)
        or not isinstance(record.get("record_sha256"), str)
    ):
        raise InvestitureError("BLOCKED_STATE_DIVERGENCE")
    expected = stable_json(record)
    if (
        target.name != f"{record['sequence']:08d}-{record['record_sha256']}.json"
        or _read_same_handle(target, allowed_links=(2,)) != expected
        or _read_same_handle(temporary, allowed_links=(2,)) != expected
    ):
        raise InvestitureError("BLOCKED_STATE_DIVERGENCE")
    temporary.unlink()
    if temporary.exists() or target.lstat().st_nlink != 1:
        raise InvestitureError("BLOCKED_STATE_DIVERGENCE")
    _sync_directory(target.parent)


def _scan(store_root: Path, *, allow_invalid_tail: bool = False) -> tuple[Path, dict[str, Any], tuple[int, int], list[dict[str, Any]], str | None]:
    root, manifest, identity = load_manifest(store_root)
    records: list[dict[str, Any]] = []
    prior = manifest["previous_last_record_sha256"] or ZERO_SHA256
    seen_events = set(manifest["inherited_event_identity_sha256s"])
    seen_replays = set(manifest["inherited_replay_identity_sha256s"])
    seen_scopes = set(manifest["inherited_usage_scope_identity_sha256s"])
    seen_receipts = set(manifest["inherited_source_receipt_identity_sha256s"])
    usage_events = set(manifest["inherited_usage_event_identity_sha256s"])
    error: str | None = None
    for index, path in enumerate(_record_files(root), start=1):
        try:
            match = RECORD_NAME.fullmatch(path.name)
            record = _load_canonical(path, "RECORD_JSON_INVALID")
            validate_record(record, manifest)
            if record["sequence"] != index or int(match.group("sequence")) != index:
                raise InvestitureError("RECORD_SEQUENCE_INVALID")
            if record["record_sha256"] != match.group("digest") or record["prior_record_sha256"] != prior:
                raise InvestitureError("RECORD_CHAIN_INVALID")
            event = record["event"]
            event_digest = sha256_bytes(event["event_id"].encode("utf-8"))
            replay_digest = sha256_bytes(event["replay_identity"].encode("utf-8"))
            if event_digest in seen_events or replay_digest in seen_replays:
                raise InvestitureError("RECORD_REPLAY_DETECTED")
            for bound in event["bound_usage_event_ids"]:
                if sha256_bytes(bound.encode("utf-8")) not in usage_events:
                    raise InvestitureError("LIFECYCLE_USAGE_BINDING_INVALID")
            if event["event_type"] == "USAGE_REPORTED":
                usage_events.add(event_digest)
                measurement = event["measurement"]
                if measurement["state"] in {"MEASURED", "PARTIAL"}:
                    scope = sha256_bytes(measurement["usage_scope_id"].encode("utf-8"))
                    receipt = sha256_bytes(measurement["source_receipt_sha256"].encode("utf-8"))
                    if scope in seen_scopes or receipt in seen_receipts:
                        raise InvestitureError("USAGE_SCOPE_REPLAY_DETECTED")
                    seen_scopes.add(scope)
                    seen_receipts.add(receipt)
            seen_events.add(event_digest)
            seen_replays.add(replay_digest)
            records.append(record)
            prior = record["record_sha256"]
        except InvestitureError as exc:
            error = exc.code
            if not allow_invalid_tail:
                raise
            break
    _assert_identity(root, identity)
    return root, manifest, identity, records, error


def verify_store(store_root: Path) -> dict[str, Any]:
    _, summary = _read_verified_store(store_root)
    return summary


def _read_verified_store(store_root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    root, _, initial_identity = load_manifest(store_root)
    root, view, lock_handle, mutation_state = _acquire_mutation(root, initial_identity)
    try:
        root, manifest, _, records, error = _scan(root)
        if error is not None:
            raise InvestitureError(error)
        if _unresolved_intents(root):
            raise InvestitureError("INTERRUPTED_RECOVERY_REQUIRED")
        _validate_persisted_evidence(root, manifest, records)
        summary = build_summary(manifest, records)
        _seal_mutation_state(mutation_state, lock_handle)
        return manifest, summary
    finally:
        _release_mutation(view, lock_handle, mutation_state)


def _validate_receipt_digest(receipt: dict[str, Any]) -> None:
    validate_against_schema("receipt", receipt, "RECEIPT_SCHEMA_INVALID")
    body = {key: value for key, value in receipt.items() if key != "receipt_sha256"}
    if receipt["receipt_sha256"] != sha256_object(body):
        raise InvestitureError("RECEIPT_DIGEST_MISMATCH")


def _validate_intent(intent: dict[str, Any]) -> None:
    if (
        set(intent) != INTENT_FIELDS
        or intent.get("schema_version") != "atlas.investiture-append-intent.v1"
        or not isinstance(intent.get("request_id_sha256"), str)
        or re.fullmatch(r"[a-f0-9]{64}", intent["request_id_sha256"]) is None
        or not isinstance(intent.get("expected_head"), str)
        or re.fullmatch(r"[a-f0-9]{64}", intent["expected_head"]) is None
        or not isinstance(intent.get("input_sha256"), str)
        or re.fullmatch(r"[a-f0-9]{64}", intent["input_sha256"]) is None
        or not isinstance(intent.get("input_byte_count"), int)
        or isinstance(intent["input_byte_count"], bool)
        or intent["input_byte_count"] < 0
        or not isinstance(intent.get("record"), dict)
    ):
        raise InvestitureError("INTENT_SCHEMA_INVALID")
    body = {key: value for key, value in intent.items() if key != "intent_sha256"}
    if intent["intent_sha256"] != sha256_object(body):
        raise InvestitureError("INTENT_DIGEST_MISMATCH")


def _validate_receipt_binding(receipt: dict[str, Any], manifest: dict[str, Any], record: dict[str, Any]) -> None:
    _validate_receipt_digest(receipt)
    event = record["event"]
    if (
        receipt["result"] != "COMMITTED"
        or receipt["error_code"] is not None
        or receipt["ledger_id"] != manifest["ledger_id"]
        or receipt["generation_id"] != manifest["generation_id"]
        or receipt["event_id"] != event["event_id"]
        or receipt["replay_identity_sha256"] != sha256_bytes(event["replay_identity"].encode("utf-8"))
        or receipt["sequence"] != record["sequence"]
        or receipt["record_sha256"] != record["record_sha256"]
        or receipt["head_sha256"] != record["record_sha256"]
        or receipt["ledger_mutation_performed"] is not True
    ):
        raise InvestitureError("RECEIPT_RECORD_BINDING_INVALID")


def _validate_persisted_evidence(root: Path, manifest: dict[str, Any], records: list[dict[str, Any]]) -> None:
    if _record_temporary_files(root) or _evidence_temporary_files(root):
        raise InvestitureError("INTERRUPTED_RECOVERY_REQUIRED")
    expected: dict[str, dict[str, Any]] = {
        sha256_bytes(record["event"]["replay_identity"].encode("utf-8")): record for record in records
    }
    receipt_paths = sorted(_child(root, "receipts").iterdir(), key=lambda item: item.name)
    if {path.name for path in receipt_paths} != {f"{identity}.json" for identity in expected}:
        raise InvestitureError("RECEIPT_COVERAGE_INVALID")
    for path in receipt_paths:
        identity = path.stem
        receipt = _load_canonical(path, "RECEIPT_JSON_INVALID")
        _validate_receipt_binding(receipt, manifest, expected[identity])
        if receipt["replay_identity_sha256"] != identity:
            raise InvestitureError("RECEIPT_FILENAME_INVALID")
    intent_paths = sorted(_child(root, "intents").iterdir(), key=lambda item: item.name)
    if {path.name for path in intent_paths} != {f"{identity}.json" for identity in expected}:
        raise InvestitureError("INTENT_COVERAGE_INVALID")
    receipts_by_identity = {
        path.stem: _load_canonical(path, "RECEIPT_JSON_INVALID") for path in receipt_paths
    }
    for path in intent_paths:
        identity = path.stem
        intent = _load_canonical(path, "INTENT_JSON_INVALID")
        _validate_intent(intent)
        record = expected[identity]
        receipt = receipts_by_identity[identity]
        if (
            intent["request_id_sha256"] != identity
            or intent["expected_head"] != record["prior_record_sha256"]
            or intent["input_sha256"] != receipt["input_sha256"]
            or intent["input_byte_count"] != receipt["input_byte_count"]
            or intent["record"] != record
        ):
            raise InvestitureError("INTENT_RECORD_BINDING_INVALID")
    valid_heads = {manifest["previous_last_record_sha256"] or ZERO_SHA256}
    valid_heads.update(record["record_sha256"] for record in records)
    recovery_conflicts = set(expected)
    recovery_conflicts.update(manifest["inherited_replay_identity_sha256s"])
    for path in sorted(_child(root, "quarantine").iterdir(), key=lambda item: item.name):
        receipt = _load_canonical(path, "QUARANTINE_JSON_INVALID")
        _validate_receipt_digest(receipt)
        if (
            path.name != f"{receipt['input_sha256']}.json"
            or receipt["result"] != "QUARANTINED"
            or receipt["error_code"] is None
            or receipt["ledger_id"] != manifest["ledger_id"]
            or receipt["generation_id"] != manifest["generation_id"]
            or receipt["event_id"] is not None
            or receipt["replay_identity_sha256"] is not None
            or receipt["sequence"] is not None
            or receipt["record_sha256"] is not None
            or receipt["head_sha256"] not in valid_heads
            or receipt["ledger_mutation_performed"] is not False
        ):
            raise InvestitureError("QUARANTINE_RECEIPT_INVALID")
    for path in sorted(_child(root, "recoveries").iterdir(), key=lambda item: item.name):
        recovery = _load_canonical(path, "RECOVERY_JSON_INVALID")
        body = {key: value for key, value in recovery.items() if key != "recovery_sha256"}
        if (
            set(recovery) != {"schema_version", "result", "request_id_sha256", "head_sha256", "ledger_mutation_performed", "retry_performed", "recovery_sha256"}
            or recovery["schema_version"] != "atlas.investiture-interruption-recovery.v1"
            or recovery["result"] != "NO_RECORD_RESERVED"
            or not isinstance(recovery["request_id_sha256"], str)
            or re.fullmatch(r"[a-f0-9]{64}", recovery["request_id_sha256"]) is None
            or path.name != f"{recovery['request_id_sha256']}.json"
            or recovery["request_id_sha256"] in recovery_conflicts
            or recovery["head_sha256"] not in valid_heads
            or recovery["ledger_mutation_performed"] is not False
            or recovery["retry_performed"] is not False
            or recovery["recovery_sha256"] != sha256_object(body)
        ):
            raise InvestitureError("RECOVERY_RECEIPT_INVALID")


def _validated_evidence_prefix(root: Path, manifest: dict[str, Any], records: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], str | None]:
    prefix: list[dict[str, Any]] = []
    for record in records:
        identity = sha256_bytes(record["event"]["replay_identity"].encode("utf-8"))
        receipt_path = _child(root, "receipts") / f"{identity}.json"
        intent_path = _child(root, "intents") / f"{identity}.json"
        try:
            if not receipt_path.exists() or not intent_path.exists():
                raise InvestitureError("INTERRUPTED_RECOVERY_REQUIRED")
            receipt = _load_canonical(receipt_path, "RECEIPT_JSON_INVALID")
            intent = _load_canonical(intent_path, "INTENT_JSON_INVALID")
            _validate_receipt_binding(receipt, manifest, record)
            _validate_intent(intent)
            if (
                receipt["replay_identity_sha256"] != identity
                or intent["request_id_sha256"] != identity
                or intent["expected_head"] != record["prior_record_sha256"]
                or intent["input_sha256"] != receipt["input_sha256"]
                or intent["input_byte_count"] != receipt["input_byte_count"]
                or intent["record"] != record
            ):
                raise InvestitureError("INTENT_RECORD_BINDING_INVALID")
        except InvestitureError as exc:
            return prefix, exc.code
        prefix.append(record)
    expected_names = {
        f"{sha256_bytes(record['event']['replay_identity'].encode('utf-8'))}.json" for record in prefix
    }
    if (
        {path.name for path in _child(root, "receipts").iterdir()} != expected_names
        or {path.name for path in _child(root, "intents").iterdir()} != expected_names
        or _record_temporary_files(root)
    ):
        return prefix, "UNRECONCILED_EVIDENCE_TAIL"
    return prefix, None


def _store_snapshot(root: Path, *, lock_handle=None) -> dict[str, str]:
    snapshot: dict[str, str] = {}
    entries = sorted(item.name for item in root.iterdir())
    snapshot["$root_entries"] = sha256_bytes(stable_json(entries))
    snapshot["manifest.json"] = sha256_bytes(_read_same_handle(root / "manifest.json"))
    lock = root / "append.lock"
    lock_info = lock.lstat()
    if os.name == "nt" and lock_handle is not None and not isinstance(lock_handle, int):
        position = lock_handle.tell()
        try:
            lock_handle.seek(0)
            lock_bytes = lock_handle.read(MAX_JSON_BYTES + 1)
            opened = os.fstat(lock_handle.fileno())
        finally:
            lock_handle.seek(position)
        if (opened.st_dev, opened.st_ino) != (lock_info.st_dev, lock_info.st_ino):
            raise InvestitureError("STORE_ROOT_IDENTITY_CHANGED")
    else:
        lock_bytes = _read_same_handle(lock)
    snapshot["append.lock"] = sha256_bytes(lock_bytes)
    snapshot["$append_lock_identity"] = f"{lock_info.st_dev}:{lock_info.st_ino}:{lock_info.st_nlink}"
    for name in STORE_DIRECTORIES:
        for path in sorted(_child(root, name).iterdir(), key=lambda item: item.name):
            snapshot[f"{name}/{path.name}"] = sha256_bytes(_read_same_handle(path))
    return snapshot


def _receipt(body: dict[str, Any]) -> dict[str, Any]:
    receipt = dict(body)
    receipt["receipt_sha256"] = sha256_object(body)
    validate_against_schema("receipt", receipt, "RECEIPT_SCHEMA_INVALID")
    return receipt


def _committed_receipt(manifest: dict[str, Any], record: dict[str, Any], raw: bytes, *, mutation: bool,
                       result: str = "COMMITTED", head_sha256: str | None = None) -> dict[str, Any]:
    event = record["event"]
    return _receipt({
        "schema_version": "atlas.investiture-operation-receipt.v1",
        "result": result,
        "error_code": None,
        "ledger_id": manifest["ledger_id"],
        "generation_id": manifest["generation_id"],
        "event_id": event["event_id"],
        "replay_identity_sha256": sha256_bytes(event["replay_identity"].encode("utf-8")),
        "input_sha256": sha256_bytes(raw),
        "input_byte_count": len(raw),
        "sequence": record["sequence"],
        "record_sha256": record["record_sha256"],
        "head_sha256": head_sha256 or record["record_sha256"],
        "ledger_mutation_performed": mutation,
    })


def quarantine(store_root: Path, raw: bytes, error_code: str) -> dict[str, Any]:
    root, _, initial_identity = load_manifest(store_root, allow_publication_pair=True)
    root, view, lock_handle, mutation_state = _acquire_mutation(root, initial_identity)
    try:
        digest = sha256_bytes(raw)
        _reconcile_atomic_evidence(root, digest, "quarantine")
        root, manifest, _, records, _ = _scan(root)
        if _unresolved_intents(root):
            raise InvestitureError("INTERRUPTED_RECOVERY_REQUIRED")
        _validate_persisted_evidence(root, manifest, records)
        receipt = _receipt({
            "schema_version": "atlas.investiture-operation-receipt.v1",
            "result": "QUARANTINED",
            "error_code": error_code,
            "ledger_id": manifest["ledger_id"],
            "generation_id": manifest["generation_id"],
            "event_id": None,
            "replay_identity_sha256": None,
            "input_sha256": digest,
            "input_byte_count": len(raw),
            "sequence": None,
            "record_sha256": None,
            "head_sha256": records[-1]["record_sha256"] if records else (manifest["previous_last_record_sha256"] or ZERO_SHA256),
            "ledger_mutation_performed": False,
        })
        target = _child(root, "quarantine") / f"{digest}.json"
        payload = stable_json(receipt)
        if target.exists():
            if _read_same_handle(target) != payload:
                raise InvestitureError("QUARANTINE_COLLISION")
        else:
            _write_atomic_evidence(target, payload, kind="quarantine")
        root, manifest, _, records, error = _scan(root)
        if error is not None:
            raise InvestitureError(error)
        _validate_persisted_evidence(root, manifest, records)
        _seal_mutation_state(mutation_state, lock_handle)
        return receipt
    finally:
        _release_mutation(view, lock_handle, mutation_state)


def append_event(store_root: Path, raw: bytes, *, expected_head: str, request_id: str,
                 interrupt_after: str | None = None) -> dict[str, Any]:
    if len(raw) > MAX_JSON_BYTES:
        return quarantine(store_root, raw, "EVENT_SIZE_INVALID")
    try:
        event = event_from_bytes(raw)
    except InvestitureError as exc:
        return quarantine(store_root, raw, exc.code)
    if event["replay_identity"] != request_id:
        raise InvestitureError("REQUEST_REPLAY_IDENTITY_MISMATCH")
    root, _, initial_identity = load_manifest(store_root)
    root, view, lock_handle, mutation_state = _acquire_mutation(root, initial_identity)
    try:
        if interrupt_after == "lock":
            raise InvestitureError("INJECTED_INTERRUPTION_AFTER_LOCK")
        root, manifest, identity, records, _ = _scan(root)
        if _unresolved_intents(root):
            raise InvestitureError("INTERRUPTED_RECOVERY_REQUIRED")
        _validate_persisted_evidence(root, manifest, records)
        current_head = records[-1]["record_sha256"] if records else (manifest["previous_last_record_sha256"] or ZERO_SHA256)
        existing = next((record for record in records if record["event"]["replay_identity"] == request_id), None)
        if existing is not None:
            request_digest = sha256_bytes(request_id.encode("utf-8"))
            intent = _load_canonical(_child(root, "intents") / f"{request_digest}.json", "INTENT_JSON_INVALID")
            persisted_receipt = _load_canonical(_child(root, "receipts") / f"{request_digest}.json", "RECEIPT_JSON_INVALID")
            if expected_head != intent["expected_head"]:
                raise InvestitureError("STALE_EXPECTED_HEAD")
            if current_head != existing["record_sha256"]:
                raise InvestitureError("REPLAY_SUPERSEDED_BY_LATER_HEAD")
            if existing["event_sha256"] != sha256_object(event):
                raise InvestitureError("REPLAY_PAYLOAD_MISMATCH")
            if persisted_receipt["input_sha256"] != sha256_bytes(raw) or persisted_receipt["input_byte_count"] != len(raw):
                raise InvestitureError("REPLAY_INPUT_BYTES_MISMATCH")
            replay_receipt = _committed_receipt(
                manifest,
                existing,
                raw,
                mutation=False,
                result="ALREADY_COMMITTED",
                head_sha256=current_head,
            )
            _seal_mutation_state(mutation_state, lock_handle)
            return replay_receipt
        if expected_head != current_head:
            raise InvestitureError("STALE_EXPECTED_HEAD")
        request_digest = sha256_bytes(request_id.encode("utf-8"))
        if (_child(root, "recoveries") / f"{request_digest}.json").exists():
            raise InvestitureError("REQUEST_ID_RECOVERY_CLOSED")
        if request_digest in set(manifest["inherited_replay_identity_sha256s"]):
            raise InvestitureError("REPLAY_FROM_PRIOR_GENERATION")
        if sha256_bytes(event["event_id"].encode("utf-8")) in set(manifest["inherited_event_identity_sha256s"]) or any(record["event"]["event_id"] == event["event_id"] for record in records):
            raise InvestitureError("EVENT_ID_REPLAY_DETECTED")
        bound_usage = set(manifest["inherited_usage_event_identity_sha256s"])
        bound_usage.update(sha256_bytes(record["event"]["event_id"].encode("utf-8")) for record in records if record["event"]["event_type"] == "USAGE_REPORTED")
        if any(sha256_bytes(value.encode("utf-8")) not in bound_usage for value in event["bound_usage_event_ids"]):
            raise InvestitureError("LIFECYCLE_USAGE_BINDING_INVALID")
        measurement = event.get("measurement")
        if event["event_type"] == "USAGE_REPORTED" and measurement["state"] in {"MEASURED", "PARTIAL"}:
            scopes = set(manifest["inherited_usage_scope_identity_sha256s"])
            receipts = set(manifest["inherited_source_receipt_identity_sha256s"])
            scopes.update(sha256_bytes(record["event"]["measurement"]["usage_scope_id"].encode("utf-8")) for record in records if record["event"]["event_type"] == "USAGE_REPORTED" and record["event"]["measurement"]["state"] in {"MEASURED", "PARTIAL"})
            receipts.update(sha256_bytes(record["event"]["measurement"]["source_receipt_sha256"].encode("utf-8")) for record in records if record["event"]["event_type"] == "USAGE_REPORTED" and record["event"]["measurement"]["state"] in {"MEASURED", "PARTIAL"})
            if sha256_bytes(measurement["usage_scope_id"].encode("utf-8")) in scopes or sha256_bytes(measurement["source_receipt_sha256"].encode("utf-8")) in receipts:
                raise InvestitureError("USAGE_SCOPE_REPLAY_DETECTED")
        record = build_record(manifest, event, sequence=len(records) + 1, prior_sha256=current_head)
        intent_body = {
            "schema_version": "atlas.investiture-append-intent.v1",
            "request_id_sha256": request_digest,
            "expected_head": current_head,
            "input_sha256": sha256_bytes(raw),
            "input_byte_count": len(raw),
            "record": record,
        }
        intent = dict(intent_body)
        intent["intent_sha256"] = sha256_object(intent_body)
        intent_path = _child(root, "intents") / f"{request_digest}.json"
        _write_atomic_evidence(intent_path, stable_json(intent), kind="intent")
        _assert_identity(root, identity)
        if interrupt_after == "intent":
            raise InvestitureError("INJECTED_INTERRUPTION_AFTER_INTENT")
        target = _child(root, "records") / f"{record['sequence']:08d}-{record['record_sha256']}.json"
        temporary = _child(root, "records") / f".{request_digest}.tmp"
        _write_exclusive(temporary, stable_json(record))
        if interrupt_after == "temporary":
            raise InvestitureError("INJECTED_INTERRUPTION_AFTER_TEMPORARY")
        _publish_no_clobber(temporary, target)
        _assert_identity(root, identity)
        if interrupt_after == "record":
            raise InvestitureError("INJECTED_INTERRUPTION_AFTER_RECORD")
        receipt = _committed_receipt(manifest, record, raw, mutation=True)
        _write_atomic_evidence(_child(root, "receipts") / f"{request_digest}.json", stable_json(receipt), kind="receipt")
        _assert_identity(root, identity)
        if interrupt_after == "receipt":
            raise InvestitureError("INJECTED_INTERRUPTION_AFTER_RECEIPT")
        root, manifest, _, records, error = _scan(root)
        if error is not None:
            raise InvestitureError(error)
        _validate_persisted_evidence(root, manifest, records)
        _seal_mutation_state(mutation_state, lock_handle)
        return receipt
    finally:
        _release_mutation(view, lock_handle, mutation_state)


def recover_interrupted(store_root: Path, *, request_id: str, expected_head: str) -> dict[str, Any]:
    request_digest = sha256_bytes(request_id.encode("utf-8"))
    root, _, initial_identity = load_manifest(store_root, allow_publication_pair=True)
    root, view, lock_handle, mutation_state = _acquire_mutation(root, initial_identity)
    try:
        for kind in ("intent", "receipt", "recovery"):
            _reconcile_atomic_evidence(root, request_digest, kind)
        _reconcile_linked_publication(root, request_digest)
        root, manifest, identity, records, error = _scan(root)
        if error is not None:
            raise InvestitureError("BLOCKED_STATE_DIVERGENCE")
        receipt_path = _child(root, "receipts") / f"{request_digest}.json"
        recovery_path = _child(root, "recoveries") / f"{request_digest}.json"
        intent_path = _child(root, "intents") / f"{request_digest}.json"
        temporary_paths = _record_temporary_files(root)
        if any(RECORD_TEMP_NAME.fullmatch(path.name).group("request") != request_digest for path in temporary_paths):
            raise InvestitureError("BLOCKED_STATE_DIVERGENCE")
        if recovery_path.exists():
            if temporary_paths:
                raise InvestitureError("BLOCKED_STATE_DIVERGENCE")
            recovery = _load_canonical(recovery_path, "RECOVERY_JSON_INVALID")
            body = {key: value for key, value in recovery.items() if key != "recovery_sha256"}
            if recovery.get("recovery_sha256") != sha256_object(body) or recovery.get("head_sha256") != expected_head:
                raise InvestitureError("BLOCKED_STATE_DIVERGENCE")
            _validate_persisted_evidence(root, manifest, records)
            _seal_mutation_state(mutation_state, lock_handle)
            return recovery
        if receipt_path.exists():
            if temporary_paths:
                raise InvestitureError("BLOCKED_STATE_DIVERGENCE")
            if not intent_path.exists():
                raise InvestitureError("BLOCKED_STATE_DIVERGENCE")
            receipt = _load_canonical(receipt_path, "RECEIPT_JSON_INVALID")
            record = next((item for item in records if item["record_sha256"] == receipt.get("record_sha256")), None)
            intent = _load_canonical(intent_path, "INTENT_JSON_INVALID")
            if record is None or intent.get("expected_head") != expected_head or intent.get("record") != record:
                raise InvestitureError("BLOCKED_STATE_DIVERGENCE")
            _validate_receipt_binding(receipt, manifest, record)
            _validate_persisted_evidence(root, manifest, records)
            _seal_mutation_state(mutation_state, lock_handle)
            return receipt
        current_head = records[-1]["record_sha256"] if records else (manifest["previous_last_record_sha256"] or ZERO_SHA256)
        if not intent_path.exists():
            if current_head != expected_head:
                raise InvestitureError("BLOCKED_STATE_DIVERGENCE")
            if request_digest in set(manifest["inherited_replay_identity_sha256s"]):
                raise InvestitureError("REPLAY_FROM_PRIOR_GENERATION")
            recovery_body = {
                "schema_version": "atlas.investiture-interruption-recovery.v1",
                "result": "NO_RECORD_RESERVED",
                "request_id_sha256": request_digest,
                "head_sha256": current_head,
                "ledger_mutation_performed": False,
                "retry_performed": False,
            }
            recovery = dict(recovery_body)
            recovery["recovery_sha256"] = sha256_object(recovery_body)
            _write_atomic_evidence(recovery_path, stable_json(recovery), kind="recovery")
            _validate_persisted_evidence(root, manifest, records)
            _seal_mutation_state(mutation_state, lock_handle)
            return recovery
        intent = _load_canonical(intent_path, "INTENT_JSON_INVALID")
        _validate_intent(intent)
        if intent["request_id_sha256"] != request_digest or intent["expected_head"] != expected_head:
            raise InvestitureError("BLOCKED_STATE_DIVERGENCE")
        record = intent.get("record")
        validate_record(record, manifest)
        if (
            sha256_bytes(record["event"]["replay_identity"].encode("utf-8")) != request_digest
            or record["prior_record_sha256"] != expected_head
        ):
            raise InvestitureError("BLOCKED_STATE_DIVERGENCE")
        target = _child(root, "records") / f"{record['sequence']:08d}-{record['record_sha256']}.json"
        if target.exists():
            if temporary_paths:
                raise InvestitureError("BLOCKED_STATE_DIVERGENCE")
            if (
                current_head != record["record_sha256"]
                or record["sequence"] != len(records)
                or _read_same_handle(target) != stable_json(record)
            ):
                raise InvestitureError("BLOCKED_STATE_DIVERGENCE")
        elif current_head == expected_head and record["sequence"] == len(records) + 1:
            if len(temporary_paths) > 1:
                raise InvestitureError("BLOCKED_STATE_DIVERGENCE")
            if temporary_paths:
                temporary = temporary_paths[0]
                if _read_same_handle(temporary) != stable_json(record):
                    raise InvestitureError("BLOCKED_STATE_DIVERGENCE")
            else:
                temporary = _child(root, "records") / f".{request_digest}.recovery.tmp"
                _write_exclusive(temporary, stable_json(record))
            _publish_no_clobber(temporary, target)
        else:
            raise InvestitureError("BLOCKED_STATE_DIVERGENCE")
        receipt = _receipt({
            "schema_version": "atlas.investiture-operation-receipt.v1",
            "result": "COMMITTED",
            "error_code": None,
            "ledger_id": manifest["ledger_id"],
            "generation_id": manifest["generation_id"],
            "event_id": record["event"]["event_id"],
            "replay_identity_sha256": request_digest,
            "input_sha256": intent["input_sha256"],
            "input_byte_count": intent["input_byte_count"],
            "sequence": record["sequence"],
            "record_sha256": record["record_sha256"],
            "head_sha256": record["record_sha256"],
            "ledger_mutation_performed": True,
        })
        _write_atomic_evidence(receipt_path, stable_json(receipt), kind="receipt")
        _assert_identity(root, identity)
        root, manifest, _, records, error = _scan(root)
        if error is not None:
            raise InvestitureError("BLOCKED_STATE_DIVERGENCE")
        _validate_persisted_evidence(root, manifest, records)
        _seal_mutation_state(mutation_state, lock_handle)
        return receipt
    finally:
        _release_mutation(view, lock_handle, mutation_state)


def _invalidate_recovery_destination(destination_root: Path) -> None:
    destination = Path(os.path.abspath(destination_root))
    identity = _identity(destination)
    with _stable_directory(destination, identity) as held:
        marker = held / "recovery.invalid"
        payload = stable_json({"schema_version": "atlas.investiture-recovery-invalid.v1", "error_code": "RECOVERY_SOURCE_MUTATED"})
        if marker.exists() or marker.is_symlink():
            if _read_same_handle(marker) != payload:
                raise InvestitureError("BLOCKED_STATE_DIVERGENCE")
        else:
            _write_exclusive(marker, payload)


def recover_generation(source_root: Path, destination_root: Path, *, expected_valid_head: str,
                       new_generation_id: str, created_at: str) -> dict[str, Any]:
    source, _, initial_identity = load_manifest(source_root)
    destination = Path(os.path.abspath(destination_root)).resolve(strict=False)
    source_resolved = source.resolve()
    if destination == source_resolved or destination.is_relative_to(source_resolved) or source_resolved.is_relative_to(destination):
        raise InvestitureError("RECOVERY_STORE_OVERLAP")
    source, view, lock_handle, mutation_state = _acquire_mutation(source, initial_identity)
    destination_created = False
    body_error: Exception | None = None
    try:
        source_snapshot = _store_snapshot(source, lock_handle=lock_handle)
        mutation_state["sealed_snapshot"] = source_snapshot
        source, manifest, _, scanned_records, chain_error = _scan(source, allow_invalid_tail=True)
        records, evidence_error = _validated_evidence_prefix(source, manifest, scanned_records)
        if _store_snapshot(source, lock_handle=lock_handle) != source_snapshot:
            raise InvestitureError("RECOVERY_SOURCE_MUTATED")
        valid_head = records[-1]["record_sha256"] if records else (manifest["previous_last_record_sha256"] or ZERO_SHA256)
        if valid_head != expected_valid_head:
            raise InvestitureError("RECOVERY_VALID_HEAD_MISMATCH")
        inherited_summary = build_summary(manifest, records)
        inherited_identities = {
            "event": list(manifest["inherited_event_identity_sha256s"]),
            "replay": list(manifest["inherited_replay_identity_sha256s"]),
            "usage_event": list(manifest["inherited_usage_event_identity_sha256s"]),
            "usage_scope": list(manifest["inherited_usage_scope_identity_sha256s"]),
            "source_receipt": list(manifest["inherited_source_receipt_identity_sha256s"]),
        }
        for record in records:
            event = record["event"]
            inherited_identities["event"].append(sha256_bytes(event["event_id"].encode("utf-8")))
            inherited_identities["replay"].append(sha256_bytes(event["replay_identity"].encode("utf-8")))
            if event["event_type"] == "USAGE_REPORTED":
                inherited_identities["usage_event"].append(sha256_bytes(event["event_id"].encode("utf-8")))
                measurement = event["measurement"]
                if measurement["state"] in {"MEASURED", "PARTIAL"}:
                    inherited_identities["usage_scope"].append(sha256_bytes(measurement["usage_scope_id"].encode("utf-8")))
                    inherited_identities["source_receipt"].append(sha256_bytes(measurement["source_receipt_sha256"].encode("utf-8")))
        inherited_identities = {key: sorted(set(values)) for key, values in inherited_identities.items()}
        if _store_snapshot(source, lock_handle=lock_handle) != source_snapshot:
            raise InvestitureError("RECOVERY_SOURCE_MUTATED")
        new_manifest = _initialize_store(
            destination_root,
            ledger_id=manifest["ledger_id"],
            generation_id=new_generation_id,
            created_at=created_at,
            previous_generation_id=manifest["generation_id"],
            previous_last_record_sha256=valid_head,
            inherited_summary=inherited_summary,
            inherited_identities=inherited_identities,
        )
        destination_created = True
        if _store_snapshot(source, lock_handle=lock_handle) != source_snapshot:
            raise InvestitureError("RECOVERY_SOURCE_MUTATED")
        source_error = evidence_error or chain_error
    except Exception as exc:
        if destination_created:
            _invalidate_recovery_destination(destination_root)
        body_error = exc
    try:
        _release_mutation(view, lock_handle, mutation_state)
    except Exception:
        if destination_created:
            _invalidate_recovery_destination(destination_root)
        if body_error is None:
            raise
    if body_error is not None:
        raise body_error
    return {
        "schema_version": "atlas.investiture-generation-recovery.v1",
        "ledger_id": manifest["ledger_id"],
        "source_generation_id": manifest["generation_id"],
        "new_generation_id": new_manifest["generation_id"],
        "verified_prefix_records": len(records),
        "previous_last_record_sha256": valid_head,
        "source_error_code": source_error,
        "source_mutated": False,
    }


def rollback_plan(current_root: Path, target_root: Path, *, expected_current_head: str,
                  expected_target_head: str) -> dict[str, Any]:
    current_manifest, current = _read_verified_store(current_root)
    target_manifest, target = _read_verified_store(target_root)
    if current["head_sha256"] != expected_current_head or target["head_sha256"] != expected_target_head:
        raise InvestitureError("ROLLBACK_HEAD_MISMATCH")
    if current["ledger_id"] != target["ledger_id"]:
        raise InvestitureError("ROLLBACK_LEDGER_MISMATCH")
    if current["generation_id"] == target["generation_id"]:
        raise InvestitureError("ROLLBACK_TARGET_NOT_DISTINCT")
    if (
        current_manifest["previous_generation_id"] != target_manifest["generation_id"]
        or current_manifest["previous_last_record_sha256"] != target["head_sha256"]
    ):
        raise InvestitureError("ROLLBACK_TARGET_NOT_DIRECT_PREDECESSOR")
    return {
        "schema_version": "atlas.investiture-rollback-plan.v1",
        "ledger_id": current["ledger_id"],
        "current_generation_id": current["generation_id"],
        "target_generation_id": target["generation_id"],
        "current_head_sha256": current["head_sha256"],
        "target_head_sha256": target["head_sha256"],
        "mutation_performed": False,
        "owner_managed_selection_required": True,
    }
