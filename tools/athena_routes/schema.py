from __future__ import annotations

import re
from typing import Any


class SchemaValidationError(ValueError):
    pass


def validate_schema(schema: dict[str, Any], value: Any, path: str = "$") -> None:
    for part in schema.get("allOf", []):
        validate_schema(part, value, path)
    condition = schema.get("if")
    if condition is not None:
        try:
            validate_schema(condition, value, path)
        except SchemaValidationError:
            pass
        else:
            validate_schema(schema.get("then", {}), value, path)
    if "const" in schema and value != schema["const"]:
        raise SchemaValidationError(f"{path}: const mismatch")
    if "enum" in schema and value not in schema["enum"]:
        raise SchemaValidationError(f"{path}: enum mismatch")
    expected = schema.get("type")
    if expected is not None:
        expected_types = expected if isinstance(expected, list) else [expected]
        matches = {
            "object": isinstance(value, dict),
            "array": isinstance(value, list),
            "string": isinstance(value, str),
            "integer": isinstance(value, int) and not isinstance(value, bool),
            "boolean": isinstance(value, bool),
            "null": value is None,
        }
        if not any(matches.get(item, False) for item in expected_types):
            raise SchemaValidationError(f"{path}: type mismatch")
    if isinstance(value, dict):
        required = set(schema.get("required", []))
        missing = required - set(value)
        if missing:
            raise SchemaValidationError(f"{path}: missing {sorted(missing)}")
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            extras = set(value) - set(properties)
            if extras:
                raise SchemaValidationError(f"{path}: unexpected {sorted(extras)}")
        for key, child in properties.items():
            if key in value:
                validate_schema(child, value[key], f"{path}.{key}")
    if isinstance(value, list) and "items" in schema:
        for index, item in enumerate(value):
            validate_schema(schema["items"], item, f"{path}[{index}]")
    if isinstance(value, str):
        if len(value) < schema.get("minLength", 0):
            raise SchemaValidationError(f"{path}: too short")
        if len(value) > schema.get("maxLength", len(value)):
            raise SchemaValidationError(f"{path}: too long")
        pattern = schema.get("pattern")
        if pattern and re.search(pattern, value) is None:
            raise SchemaValidationError(f"{path}: pattern mismatch")
    if isinstance(value, int) and not isinstance(value, bool):
        if value < schema.get("minimum", value):
            raise SchemaValidationError(f"{path}: below minimum")
