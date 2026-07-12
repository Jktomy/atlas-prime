from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Any

from .errors import LifecycleError
from .jsonio import canonical_bytes, load_bounded


TRUSTED_SCHEMAS = {
    "atlas.lifecycle.feather": "feather-v1.schema.json",
    "atlas.lifecycle.feather-archive": "feather-archive-v1.schema.json",
    "atlas.lifecycle.golden-wing": "golden-wing-v1.schema.json",
    "atlas.lifecycle.quest-emberline": "quest-emberline-v1.schema.json",
    "atlas.lifecycle.quest-checkpoint": "quest-checkpoint-v1.schema.json",
    "atlas.lifecycle.sunset": "sunset-v1.schema.json",
    "atlas.lifecycle.sunrise": "sunrise-v1.schema.json",
    "atlas.lifecycle.continuity": "continuity-v1.schema.json",
    "atlas.lifecycle.receipt": "lifecycle-receipt-v1.schema.json",
    "atlas.lifecycle.event": "lifecycle-event-v1.schema.json",
}
TRUSTED_PROJECTIONS = {
    ("atlas.lifecycle.website-index", "2.0.0"): "website-index-v2.schema.json",
}
TRUSTED_AUXILIARY_SCHEMAS = {
    ("atlas.lifecycle.event-trust-root", "1.0.0"): "lifecycle-event-trust-root-v1.schema.json",
    (
        "atlas.lifecycle.event-candidate-manifest",
        "1.0.0",
    ): "lifecycle-event-candidate-manifest-v1.schema.json",
    (
        "atlas.lifecycle.event-candidate-receipt",
        "1.0.0",
    ): "lifecycle-event-candidate-receipt-v1.schema.json",
    (
        "atlas.lifecycle.construction-profile",
        "1.0.0",
    ): "lifecycle-construction-profile-v1.schema.json",
}
SCHEMA_DRAFT = "https://json-schema.org/draft/2020-12/schema"


def _type_matches(value: Any, expected: str) -> bool:
    return {
        "object": isinstance(value, dict),
        "array": isinstance(value, list),
        "string": isinstance(value, str),
        "integer": isinstance(value, int) and not isinstance(value, bool),
        "boolean": isinstance(value, bool),
        "null": value is None,
    }.get(expected, False)


class SchemaValidator:
    def __init__(self, schema_dir: Path) -> None:
        self.schema_dir = schema_dir.resolve()
        self.schemas: dict[str, dict[str, Any]] = {}
        for name in {
            "common-v1.schema.json",
            *TRUSTED_SCHEMAS.values(),
            *TRUSTED_PROJECTIONS.values(),
            *TRUSTED_AUXILIARY_SCHEMAS.values(),
        }:
            path = self.schema_dir / name
            schema = load_bounded(path)
            if schema.get("$schema") != SCHEMA_DRAFT:
                raise LifecycleError("UNTRUSTED_SCHEMA_DRAFT", "trusted schema draft identity mismatch")
            expected_id = f"https://github.com/Jktomy/atlas-prime/lifecycle/schemas/{name}"
            if schema.get("$id") != expected_id:
                raise LifecycleError("UNTRUSTED_SCHEMA_ID", "trusted schema URI identity mismatch")
            self.schemas[name] = schema

        for schema_id, name in TRUSTED_SCHEMAS.items():
            declared = self.schemas[name].get("properties", {}).get("schema_id", {}).get("const")
            if declared != schema_id:
                raise LifecycleError("SCHEMA_CATALOG_MISMATCH", "schema catalog identity mismatch")

    def validate_record(self, record: dict[str, Any]) -> None:
        schema_id = record.get("schema_id")
        name = TRUSTED_SCHEMAS.get(schema_id)
        if name is None:
            raise LifecycleError("UNTRUSTED_SCHEMA_ID", "record declares an untrusted schema identity")
        self._validate(record, self.schemas[name], name, "$")

    def validate_projection(self, projection: dict[str, Any]) -> None:
        key = (projection.get("schema_id"), projection.get("schema_version"))
        name = TRUSTED_PROJECTIONS.get(key)
        if name is None:
            raise LifecycleError(
                "UNTRUSTED_PROJECTION_SCHEMA",
                "projection declares an untrusted schema identity or version",
            )
        self._validate(projection, self.schemas[name], name, "$")

    def validate_event_trust_root(self, trust_root: dict[str, Any]) -> None:
        key = (trust_root.get("schema_id"), trust_root.get("schema_version"))
        name = TRUSTED_AUXILIARY_SCHEMAS.get(key)
        if name is None:
            raise LifecycleError(
                "UNTRUSTED_EVENT_TRUST_ROOT",
                "event trust root declares an untrusted schema identity or version",
            )
        self._validate(trust_root, self.schemas[name], name, "$")

    def validate_event_candidate_manifest(self, manifest: dict[str, Any]) -> None:
        self._validate_auxiliary(manifest, "atlas.lifecycle.event-candidate-manifest")

    def validate_event_candidate_receipt(self, receipt: dict[str, Any]) -> None:
        self._validate_auxiliary(receipt, "atlas.lifecycle.event-candidate-receipt")

    def validate_lifecycle_construction_profile(self, profile: dict[str, Any]) -> None:
        self._validate_auxiliary(profile, "atlas.lifecycle.construction-profile")

    def _validate_auxiliary(self, value: dict[str, Any], expected_schema_id: str) -> None:
        key = (value.get("schema_id"), value.get("schema_version"))
        name = TRUSTED_AUXILIARY_SCHEMAS.get(key)
        if name is None or key[0] != expected_schema_id:
            raise LifecycleError(
                "UNTRUSTED_AUXILIARY_SCHEMA",
                "auxiliary lifecycle object declares an untrusted schema identity or version",
            )
        self._validate(value, self.schemas[name], name, "$")

    def _resolve(self, reference: str, current_name: str) -> tuple[dict[str, Any], str]:
        if "#" in reference:
            file_name, fragment = reference.split("#", 1)
        else:
            file_name, fragment = reference, ""
        target_name = file_name or current_name
        if target_name not in self.schemas:
            raise LifecycleError("UNTRUSTED_SCHEMA_REFERENCE", "schema reference leaves the trusted catalog")
        target: Any = self.schemas[target_name]
        if fragment:
            if not fragment.startswith("/"):
                raise LifecycleError("INVALID_SCHEMA_REFERENCE", "schema reference fragment is invalid")
            for token in fragment[1:].split("/"):
                token = token.replace("~1", "/").replace("~0", "~")
                if not isinstance(target, dict) or token not in target:
                    raise LifecycleError("INVALID_SCHEMA_REFERENCE", "schema reference target is missing")
                target = target[token]
        if not isinstance(target, dict):
            raise LifecycleError("INVALID_SCHEMA_REFERENCE", "schema reference target is not an object")
        return target, target_name

    def _matches(self, value: Any, schema: dict[str, Any], current_name: str, path: str) -> bool:
        try:
            self._validate(value, schema, current_name, path)
            return True
        except LifecycleError:
            return False

    def _validate(self, value: Any, schema: dict[str, Any], current_name: str, path: str) -> None:
        if "$ref" in schema:
            target, target_name = self._resolve(schema["$ref"], current_name)
            self._validate(value, target, target_name, path)
            return

        if "allOf" in schema:
            for child in schema["allOf"]:
                self._validate(value, child, current_name, path)
        if "oneOf" in schema:
            matches = sum(self._matches(value, child, current_name, path) for child in schema["oneOf"])
            if matches != 1:
                raise LifecycleError("SCHEMA_ONE_OF", f"{path} must match exactly one permitted shape")
        if "if" in schema:
            branch = "then" if self._matches(value, schema["if"], current_name, path) else "else"
            if branch in schema:
                self._validate(value, schema[branch], current_name, path)

        expected = schema.get("type")
        if expected is not None:
            choices = [expected] if isinstance(expected, str) else expected
            if not any(_type_matches(value, choice) for choice in choices):
                raise LifecycleError("SCHEMA_TYPE", f"{path} has an invalid type")
        if "const" in schema and value != schema["const"]:
            raise LifecycleError("SCHEMA_CONST", f"{path} does not match its trusted constant")
        if "enum" in schema and value not in schema["enum"]:
            raise LifecycleError("SCHEMA_ENUM", f"{path} is outside the permitted vocabulary")

        if isinstance(value, dict):
            required = schema.get("required", [])
            missing = [key for key in required if key not in value]
            if missing:
                raise LifecycleError("SCHEMA_REQUIRED", f"{path} is missing required fields: {', '.join(missing)}")
            properties = schema.get("properties", {})
            if schema.get("additionalProperties") is False:
                extra = sorted(set(value) - set(properties))
                if extra:
                    raise LifecycleError("SCHEMA_EXTRA_FIELD", f"{path} has undeclared fields: {', '.join(extra)}")
            for key, nested in value.items():
                if key in properties:
                    self._validate(nested, properties[key], current_name, f"{path}.{key}")

        if isinstance(value, list):
            if len(value) < schema.get("minItems", 0) or len(value) > schema.get("maxItems", len(value)):
                raise LifecycleError("SCHEMA_ITEM_COUNT", f"{path} has an invalid item count")
            if schema.get("uniqueItems"):
                tokens = [canonical_bytes({"value": item}) for item in value]
                if len(tokens) != len(set(tokens)):
                    raise LifecycleError("SCHEMA_DUPLICATE_ITEM", f"{path} contains duplicate items")
            if "items" in schema:
                for index, item in enumerate(value):
                    self._validate(item, schema["items"], current_name, f"{path}[{index}]")

        if isinstance(value, str):
            if len(value) < schema.get("minLength", 0) or len(value) > schema.get("maxLength", len(value)):
                raise LifecycleError("SCHEMA_STRING_LENGTH", f"{path} has an invalid length")
            if "pattern" in schema and re.fullmatch(schema["pattern"], value) is None:
                raise LifecycleError("SCHEMA_PATTERN", f"{path} has an invalid format")
            if schema.get("format") == "date-time":
                try:
                    datetime.fromisoformat(value.replace("Z", "+00:00"))
                except ValueError as exc:
                    raise LifecycleError("SCHEMA_DATETIME", f"{path} is not an ISO date-time") from exc

        if isinstance(value, int) and not isinstance(value, bool):
            if value < schema.get("minimum", value) or value > schema.get("maximum", value):
                raise LifecycleError("SCHEMA_INTEGER_RANGE", f"{path} is outside the permitted range")
