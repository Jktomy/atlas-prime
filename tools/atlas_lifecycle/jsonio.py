from __future__ import annotations

import base64
import hashlib
import json
import unicodedata
from pathlib import Path
from typing import Any

from .errors import LifecycleError
from .limits import MAX_JSON_BYTES, MAX_JSON_DEPTH, MAX_JSON_NODES


PREFIX_BY_SCHEMA = {
    "atlas.lifecycle.feather": "FTR",
    "atlas.lifecycle.feather-archive": "FAR",
    "atlas.lifecycle.golden-wing": "GWN",
    "atlas.lifecycle.quest-emberline": "QEM",
    "atlas.lifecycle.quest-checkpoint": "QCP",
    "atlas.lifecycle.sunset": "SUN",
    "atlas.lifecycle.sunrise": "SRI",
    "atlas.lifecycle.continuity": "CON",
    "atlas.lifecycle.receipt": "LCR",
}


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise LifecycleError("DUPLICATE_JSON_KEY", f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _forbid_float(value: str) -> None:
    raise LifecycleError("FLOAT_FORBIDDEN", "floating-point values are forbidden")


def _forbid_constant(value: str) -> None:
    raise LifecycleError("NONFINITE_FORBIDDEN", "non-finite values are forbidden")


def _check_bounds(
    value: Any,
    depth: int = 0,
    count: list[int] | None = None,
    *,
    max_depth: int = MAX_JSON_DEPTH,
    max_nodes: int = MAX_JSON_NODES,
) -> None:
    if count is None:
        count = [0]
    count[0] += 1
    if count[0] > max_nodes:
        raise LifecycleError("JSON_NODE_LIMIT", "JSON node count exceeds the trusted limit")
    if depth > max_depth:
        raise LifecycleError("JSON_DEPTH_LIMIT", "JSON parsing depth exceeds the trusted limit")
    if isinstance(value, str) and unicodedata.normalize("NFC", value) != value:
        raise LifecycleError("NONCANONICAL_UNICODE", "JSON strings must be NFC normalized")
    if isinstance(value, dict):
        for key, nested in value.items():
            if unicodedata.normalize("NFC", key) != key:
                raise LifecycleError("NONCANONICAL_UNICODE", "JSON keys must be NFC normalized")
            _check_bounds(nested, depth + 1, count, max_depth=max_depth, max_nodes=max_nodes)
    elif isinstance(value, list):
        for nested in value:
            _check_bounds(nested, depth + 1, count, max_depth=max_depth, max_nodes=max_nodes)


def loads_bounded(
    data: bytes,
    *,
    label: str = "JSON input",
    max_bytes: int = MAX_JSON_BYTES,
    max_depth: int = MAX_JSON_DEPTH,
    max_nodes: int = MAX_JSON_NODES,
) -> dict[str, Any]:
    if len(data) > max_bytes:
        raise LifecycleError("JSON_SIZE_LIMIT", f"{label} exceeds the trusted byte limit")
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise LifecycleError("INVALID_UTF8", f"{label} is not valid UTF-8") from exc
    try:
        value = json.loads(
            text,
            object_pairs_hook=_pairs,
            parse_float=_forbid_float,
            parse_constant=_forbid_constant,
        )
    except LifecycleError:
        raise
    except json.JSONDecodeError as exc:
        raise LifecycleError("MALFORMED_JSON", f"{label} is malformed JSON") from exc
    if not isinstance(value, dict):
        raise LifecycleError("ROOT_NOT_OBJECT", f"{label} root must be an object")
    _check_bounds(value, max_depth=max_depth, max_nodes=max_nodes)
    return value


def load_bounded(path: Path) -> dict[str, Any]:
    return loads_bounded(read_bounded(path), label=path.name)


def read_bounded(path: Path, *, max_bytes: int = MAX_JSON_BYTES) -> bytes:
    try:
        size = path.stat().st_size
    except OSError as exc:
        raise LifecycleError("INPUT_UNAVAILABLE", "JSON input is unavailable") from exc
    if not path.is_file() or path.is_symlink():
        raise LifecycleError("INPUT_NOT_REGULAR", "JSON input must be a regular file")
    if size > max_bytes:
        raise LifecycleError("JSON_SIZE_LIMIT", "JSON input exceeds the trusted byte limit")
    try:
        with path.open("rb") as handle:
            data = handle.read(max_bytes + 1)
    except OSError as exc:
        raise LifecycleError("INPUT_UNAVAILABLE", "JSON input is unavailable") from exc
    if len(data) > max_bytes:
        raise LifecycleError("JSON_SIZE_LIMIT", "JSON input exceeds the trusted byte limit")
    return data


def canonical_bytes(
    value: dict[str, Any],
    *,
    omit_record_id: bool = False,
    max_depth: int = MAX_JSON_DEPTH,
    max_nodes: int = MAX_JSON_NODES,
) -> bytes:
    payload = dict(value)
    if omit_record_id:
        payload.pop("record_id", None)
    _check_bounds(payload, max_depth=max_depth, max_nodes=max_nodes)
    return (
        json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def stable_record_id(record: dict[str, Any]) -> str:
    schema_id = record.get("schema_id")
    prefix = PREFIX_BY_SCHEMA.get(schema_id)
    if prefix is None:
        raise LifecycleError("UNTRUSTED_SCHEMA_ID", "record declares an untrusted schema identity")
    digest = hashlib.sha256(canonical_bytes(record, omit_record_id=True)).digest()
    token = base64.b32encode(digest).decode("ascii").rstrip("=")[:26]
    return f"{prefix}-{token}"
