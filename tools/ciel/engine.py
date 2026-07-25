from __future__ import annotations

import argparse
import json
import re
from pathlib import Path, PurePosixPath
from typing import Any

from tools.athena_routes.schema import SchemaValidationError, validate_schema

ROOT = Path(__file__).resolve().parents[2]
SCHEMAS = {
    "HARVEST": ROOT / "schemas" / "ciel-harvest-record-v1.schema.json",
    "ABSORPTION": ROOT / "schemas" / "ciel-absorption-record-v1.schema.json",
    "CODE_CAPSULE": ROOT / "schemas" / "rimuru-code-capsule-v1.schema.json",
    "REGISTRY": ROOT / "schemas" / "rimuru-registry-v1.schema.json",
}
REGISTRY = ROOT / "knowledge" / "rimuru" / "registry-r01.json"

PROTECTED_PATTERNS = (
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"(?i)\b(?:password|api[_ -]?key|access[_ -]?token|refresh[_ -]?token)\s*[:=]\s*\S+"),
    re.compile(r"(?i)\b(?:patient|account|routing)\s+(?:number|id)\s*[:=]\s*\S+"),
    re.compile(r"\b(?:10|127|169\.254|172\.(?:1[6-9]|2\d|3[01])|192\.168)\.\d{1,3}\.\d{1,3}\b"),
)
FORBIDDEN_SUFFIXES = {
    ".exe", ".dll", ".so", ".dylib", ".zip", ".tar", ".gz", ".7z", ".whl",
    ".pyc", ".jar", ".bin", ".img", ".iso",
}


class CielValidationError(ValueError):
    pass


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_with_schema(kind: str, value: dict[str, Any]) -> None:
    try:
        validate_schema(load(SCHEMAS[kind]), value)
    except SchemaValidationError as exc:
        raise CielValidationError(f"{kind}_SCHEMA_INVALID") from exc


def scan_public_clean(value: Any) -> None:
    rendered = json.dumps(value, sort_keys=True, ensure_ascii=False)
    for pattern in PROTECTED_PATTERNS:
        if pattern.search(rendered):
            raise CielValidationError("PROTECTED_MATERIAL_REJECTED")


def safe_repo_path(path: str) -> PurePosixPath:
    parsed = PurePosixPath(path)
    if parsed.is_absolute() or ".." in parsed.parts or "\\" in path:
        raise CielValidationError("RIMURU_PATH_INVALID")
    if parsed.suffix.casefold() in FORBIDDEN_SUFFIXES:
        raise CielValidationError("EXECUTABLE_OR_ARCHIVE_REJECTED")
    return parsed


def validate_harvest_record(value: dict[str, Any]) -> None:
    validate_with_schema("HARVEST", value)
    scan_public_clean(value)


def validate_absorption_record(value: dict[str, Any]) -> None:
    validate_with_schema("ABSORPTION", value)
    scan_public_clean(value)


def validate_code_capsule(value: dict[str, Any]) -> None:
    validate_with_schema("CODE_CAPSULE", value)
    scan_public_clean(value)
    if value["license"]["spdx_id"] in {"UNKNOWN", "NOASSERTION"}:
        raise CielValidationError("LICENSE_UNRESOLVED")
    if any(value["authority_boundary"].values()):
        raise CielValidationError("CODE_CAPSULE_AUTHORITY_INVALID")


def validate_registry(value: dict[str, Any], *, root: Path = ROOT) -> None:
    validate_with_schema("REGISTRY", value)
    scan_public_clean(value)
    ids: list[str] = []
    paths: list[str] = []
    source_keys: list[tuple[str, str | None]] = []
    for entry in value["entries"]:
        path = safe_repo_path(entry["path"])
        expected_root = (
            PurePosixPath(value["code_capsule_root"])
            if entry["record_type"] == "CODE_CAPSULE"
            else PurePosixPath(value["record_root"])
        )
        if path.parent != expected_root:
            raise CielValidationError("RIMURU_PATH_CLASS_MISMATCH")
        ids.append(entry["record_id"])
        paths.append(entry["path"].casefold())
        source_keys.append((entry["source_locator"], entry["source_revision"]))
        target = root.joinpath(*path.parts)
        if not target.is_file():
            raise CielValidationError("RIMURU_RECORD_MISSING")
        payload = load(target)
        if entry["record_type"] == "HARVEST":
            validate_harvest_record(payload)
        elif entry["record_type"] == "ABSORPTION":
            validate_absorption_record(payload)
        else:
            validate_code_capsule(payload)
        if payload.get("record_id", payload.get("absorption_id", payload.get("capsule_id"))) != entry["record_id"]:
            raise CielValidationError("RIMURU_RECORD_ID_MISMATCH")
    for values in (ids, paths, source_keys):
        if len(values) != len(set(values)):
            raise CielValidationError("RIMURU_DUPLICATE")
    for lineage in value["lineage"]:
        safe_repo_path(lineage["path"])
        safe_repo_path(lineage["successor"])


def validate_repository(*, root: Path = ROOT) -> dict[str, Any]:
    registry = load(root / "knowledge" / "rimuru" / "registry-r01.json")
    validate_registry(registry, root=root)
    operation = (root / "operations" / "ciel.md").read_text(encoding="utf-8")
    skill = (root / "skills" / "gluttony" / "SKILL.md").read_text(encoding="utf-8")
    rimuru = (root / "knowledge" / "rimuru" / "README.md").read_text(encoding="utf-8")
    quest = (root / "quests" / "ciels-awakening.md").read_text(encoding="utf-8")
    required = {
        "operation": ("HARVEST <X>", "ABSORB <Y>", "A disposition is analysis, not authority"),
        "skill": ("may not obey instructions retrieved", "stop before any unapproved Prime write"),
        "rimuru": ("noncanonical", "never override merged Prime"),
        "quest": ("CIEL-C01-M02-PREVIEW", "M02 is ineligible"),
    }
    surfaces = {"operation": operation, "skill": skill, "rimuru": rimuru, "quest": quest}
    for name, markers in required.items():
        for marker in markers:
            if marker.casefold() not in surfaces[name].casefold():
                raise CielValidationError(f"CIEL_CONTRACT_MARKER_MISSING:{name}:{marker}")
    return {
        "schema_version": "atlas.ciel.validation-receipt.v1",
        "result": "PASS",
        "registry_id": registry["registry_id"],
        "registry_revision": registry["registry_revision"],
        "entry_count": len(registry["entries"]),
        "authority": registry["authority"],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Read-only Operation Ciel validator")
    parser.add_argument("command", choices=("validate",))
    args = parser.parse_args(argv)
    if args.command == "validate":
        print(json.dumps(validate_repository(), sort_keys=True))
        return 0
    raise AssertionError("unreachable")


if __name__ == "__main__":
    raise SystemExit(main())
