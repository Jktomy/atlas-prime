from __future__ import annotations

import base64
import hashlib
import json
import re
import unicodedata
from pathlib import PurePosixPath
from typing import Any, Iterable

from jsonschema import Draft202012Validator, FormatChecker

from .models import DuplicateKeyError, SpearError

_HEX40 = re.compile(r"^[0-9a-f]{40}$")
_DRIVE = re.compile(r"^[A-Za-z]:")
_CONTROL = re.compile(r"[\x00-\x1f\x7f]")


def reject_duplicate_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    seen: set[str] = set()
    out: dict[str, Any] = {}
    for key, value in pairs:
        if key in seen:
            raise DuplicateKeyError(f"duplicate JSON key: {key}")
        seen.add(key)
        out[key] = value
    return out


def parse_json_bytes(data: bytes, *, max_bytes: int) -> dict[str, Any]:
    if len(data) > max_bytes:
        raise SpearError("decoded packet exceeds maximum size")
    try:
        text = data.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise SpearError("packet is not strict UTF-8") from exc
    try:
        packet = json.loads(text, object_pairs_hook=reject_duplicate_pairs)
    except json.JSONDecodeError as exc:
        raise SpearError(f"malformed JSON: {exc.msg}") from exc
    if not isinstance(packet, dict):
        raise SpearError("packet root must be a JSON object")
    return packet


def parse_packet_file(path: str, expected_transport_sha256: str, *, max_bytes: int) -> tuple[dict[str, Any], str, bytes]:
    with open(path, "rb") as fh:
        data = fh.read()
    actual = hashlib.sha256(data).hexdigest()
    if actual != expected_transport_sha256:
        raise SpearError("transport SHA-256 confirmation mismatch")
    return parse_json_bytes(data, max_bytes=max_bytes), actual, data


def parse_base64_packet(packet_b64: str, expected_transport_sha256: str, *, max_bytes: int) -> tuple[dict[str, Any], str, bytes]:
    try:
        data = base64.b64decode(packet_b64.encode("ascii"), validate=True)
    except Exception as exc:
        raise SpearError("packet_b64 is not valid base64") from exc
    actual = hashlib.sha256(data).hexdigest()
    if actual != expected_transport_sha256:
        raise SpearError("transport SHA-256 confirmation mismatch")
    return parse_json_bytes(data, max_bytes=max_bytes), actual, data


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_json_bytes(data: bytes) -> dict[str, Any]:
    return parse_json_bytes(data, max_bytes=1024 * 1024)


def load_json_file(path: str) -> dict[str, Any]:
    with open(path, "rb") as fh:
        return load_json_bytes(fh.read())


def load_json_policy(path: str) -> dict[str, Any]:
    return load_json_file(path)


def validate_schema(packet: dict[str, Any], schema: dict[str, Any]) -> None:
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(packet), key=lambda e: list(e.path))
    if errors:
        first = errors[0]
        location = "/".join(str(p) for p in first.path) or "<root>"
        raise SpearError(f"schema validation failed at {location}: {first.message}")


def normalize_spear_path(path: str, *, max_path_bytes: int) -> str:
    if len(path.encode("utf-8")) > max_path_bytes:
        raise SpearError("path exceeds maximum UTF-8 byte length")
    if _CONTROL.search(path):
        raise SpearError("path contains a control character")
    if "\\" in path:
        raise SpearError("path must use forward slashes only")
    if path.startswith("/") or _DRIVE.match(path):
        raise SpearError("path must be relative")
    low = path.lower()
    if "%2e" in low or "%2f" in low or "%5c" in low:
        raise SpearError("encoded traversal or separator is not allowed")
    normalized = unicodedata.normalize("NFC", path)
    if normalized != path:
        raise SpearError("path must already be Unicode NFC normalized")
    parts = PurePosixPath(path).parts
    if not parts or any(part in ("", ".", "..") for part in parts):
        raise SpearError("path contains an empty, dot, or dot-dot component")
    if any(part.endswith(" ") or part.endswith(".") for part in parts):
        raise SpearError("path component may not end with a space or dot")
    if str(PurePosixPath(*parts)) != path:
        raise SpearError("path is not normalized")
    return path


def assert_no_path_collisions(paths: Iterable[str], *, max_path_bytes: int) -> None:
    exact: set[str] = set()
    folded: dict[str, str] = {}
    for path in paths:
        normalized = normalize_spear_path(path, max_path_bytes=max_path_bytes)
        if normalized in exact:
            raise SpearError(f"duplicate path: {normalized}")
        exact.add(normalized)
        key = unicodedata.normalize("NFC", normalized).casefold()
        prior = folded.get(key)
        if prior is not None and prior != normalized:
            raise SpearError(f"case or Unicode-normalized path collision: {prior} / {normalized}")
        folded[key] = normalized


def assert_sha256_matches(content: str, expected: str) -> None:
    actual = sha256_text(content)
    if actual != expected:
        raise SpearError("content SHA-256 mismatch")


def assert_blob_sha(value: str) -> None:
    if not _HEX40.match(value):
        raise SpearError("expected Git blob SHA must be lowercase 40-character hex")