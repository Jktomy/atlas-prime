from __future__ import annotations

import re
from typing import Any

from .errors import LifecycleError


FORBIDDEN = (
    re.compile(r"(?i)(?:api[_-]?key|access[_-]?token|refresh[_-]?token|password|secret)\s*[:=]\s*[^\s]+"),
    re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~+/-]{16,}={0,2}"),
    re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"(?i)\b(?:seed phrase|mfa code|recovery code)\s*[:=]"),
    re.compile(r"(?<![A-Za-z0-9])(?:\d{1,3}\.){3}\d{1,3}(?![A-Za-z0-9])"),
    re.compile(r"(?i)(?:\b[a-z]:[\\/]|\\\\)"),
    re.compile(r"(?<![:/A-Za-z0-9])/(?:[A-Za-z0-9._-]+/)*[A-Za-z0-9._-]+"),
)


def enforce_clean_values(value: Any) -> None:
    if isinstance(value, str):
        if any(pattern.search(value) for pattern in FORBIDDEN):
            raise LifecycleError(
                "PROTECTED_VALUE_REJECTED",
                "record contains a value forbidden by the protected-source boundary",
            )
    elif isinstance(value, dict):
        for nested in value.values():
            enforce_clean_values(nested)
    elif isinstance(value, list):
        for nested in value:
            enforce_clean_values(nested)


def enforce_pointer_contract(record: dict[str, Any]) -> None:
    protected = record.get("protected_data")
    if not isinstance(protected, dict):
        return
    classification = protected.get("classification")
    pointers = protected.get("protected_pointers", [])
    if classification == "PROTECTED_POINTER_ONLY" and not pointers:
        raise LifecycleError(
            "PROTECTED_POINTER_REQUIRED",
            "protected-pointer-only records require at least one protected pointer",
        )
    if classification != "PROTECTED_POINTER_ONLY" and pointers:
        raise LifecycleError(
            "PROTECTED_POINTER_CLASSIFICATION",
            "protected pointers require protected-pointer-only classification",
        )
