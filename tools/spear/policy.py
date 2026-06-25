from __future__ import annotations

import fnmatch
import json
import re
from pathlib import PurePosixPath
from typing import Any

import yaml
from jsonschema import Draft202012Validator, FormatChecker

from .git_adapter import blob_sha_at_commit, file_bytes_at_commit
from .models import (
    BASE_BRANCH,
    DESTINATION_POLICY_PATH,
    PROTECTED_POLICY_PATH,
    SOURCE_METADATA_SCHEMA_PATH,
    SPEAR_OVERLAY_POLICY_PATH,
    SPEAR_PACKET_SCHEMA_PATH,
    SPEAR_CONTRACT_ID,
    TARGET_REPOSITORY,
    ArtifactIdentity,
    GitError,
    PolicyError,
    PolicyIdentity,
    WarningSummary,
)
from .validate import load_json_bytes, normalize_spear_path, sha256_bytes

_PRIVATE_IPV4 = re.compile(r"\b(?:10\.\d{1,3}|192\.168|172\.(?:1[6-9]|2\d|3[0-1]))\.\d{1,3}\.\d{1,3}\b")
_CREDENTIAL_ASSIGN = re.compile(r"(?im)\b(?:api[_-]?key|secret|password|passwd|session[_-]?cookie)\b\s*[:=]\s*['\"]?[^'\"\s]{8,}")
_TOKEN_LIKE = re.compile(r"(?im)\btoken\b\s*[:=]\s*['\"]?[^'\"\s]{8,}")
_ENV_ASSIGN = re.compile(r"(?m)^[A-Z][A-Z0-9_]{2,}=.+$")
_PRIVATE_KEY = re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")
_ACCOUNT = re.compile(r"(?i)\b(?:account|routing|iban|ssn)\b.{0,24}\d{4,}")
_MEDICAL = re.compile(r"(?i)\b(?:mrn|medical record|patient id)\b.{0,24}[a-z0-9-]{4,}")
_LFS = re.compile(r"(?m)^version https://git-lfs.github.com/spec/v1$")

IMPLEMENTED_SCANNER_CATEGORIES = {
    "private_key_marker",
    "credential_assignment",
    "token_like_value",
    "env_assignment",
    "private_network_value",
    "account_evidence",
    "medical_record_identifier",
    "git_lfs_pointer",
    "binary_or_nul_content",
}
SUPPORTED_DESTINATION_MODES = {"V03_CONTRACT_PREVIEW"}
SUPPORTED_PROTECTED_MODES = {"DENY_BY_DEFAULT"}
SUPPORTED_PROTECTED_MUTATIONS = {"DENY", "REGISTERED_HIGH_LEVEL_OPERATION_ONLY", "APPEND_FEATHER_OPERATION_ONLY", "REGISTERED_GENERATOR_ONLY", "MIGRATION_OPERATION_ONLY"}
SUPPORTED_WRITE_LANES = {"SOURCE_PR", "GENERATED_PR", "MIGRATION_PR"}
PLAN_ALLOWED_WRITE_LANES = {"SOURCE_PR"}


class UniqueKeySafeLoader(yaml.SafeLoader):
    """Safe YAML loader that rejects duplicate mapping keys."""


UniqueKeySafeLoader.yaml_implicit_resolvers = {
    key: [
        resolver
        for resolver in resolvers
        if resolver[0] != "tag:yaml.org,2002:timestamp"
    ]
    for key, resolvers in yaml.SafeLoader.yaml_implicit_resolvers.items()
}


def _construct_mapping(loader: UniqueKeySafeLoader, node: yaml.nodes.MappingNode, deep: bool = False) -> dict[Any, Any]:
    mapping: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise PolicyError(f"duplicate YAML key: {key}")
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


UniqueKeySafeLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_mapping)


def parse_policy_yaml(data: bytes) -> dict[str, Any]:
    try:
        parsed = yaml.load(data.decode("utf-8", errors="strict"), Loader=UniqueKeySafeLoader)
    except PolicyError:
        raise
    except Exception as exc:
        raise PolicyError("controlling policy YAML is malformed or unsafe") from exc
    if not isinstance(parsed, dict):
        raise PolicyError("controlling policy YAML root must be a mapping")
    return parsed


def _require_mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise PolicyError(f"{label} must be a mapping")
    return value


def _require_list(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise PolicyError(f"{label} must be a list")
    return value


def _require_str(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise PolicyError(f"{label} must be a nonempty string")
    return value


def _identity_from_parsed(path: str, commit: str, blob: str, data: bytes, parsed: dict[str, Any]) -> PolicyIdentity:
    return PolicyIdentity(
        path=path,
        repository_commit=commit,
        git_blob_sha=blob,
        sha256=sha256_bytes(data),
        raw_byte_size=len(data),
        policy_id=_require_str(parsed.get("policy_id"), "policy_id"),
        policy_version=_require_str(parsed.get("policy_version"), "policy_version"),
    )


def _policy_object_from_git(repo: str, commit: str, path: str) -> tuple[PolicyIdentity, dict[str, Any], bytes]:
    data = file_bytes_at_commit(repo, commit, path)
    blob = blob_sha_at_commit(repo, commit, path)
    if blob is None:
        raise PolicyError("controlling policy path missing at pinned commit")
    parsed = parse_policy_yaml(data)
    return _identity_from_parsed(path, commit, blob, data, parsed), parsed, data


def _validate_destination_policy(parsed: dict[str, Any]) -> None:
    if parsed.get("repository") != TARGET_REPOSITORY:
        raise PolicyError("destination policy repository mismatch")
    if parsed.get("mode") not in SUPPORTED_DESTINATION_MODES:
        raise PolicyError("unsupported destination policy mode")
    authority = _require_mapping(parsed.get("authority"), "authority")
    _require_list(authority.get("compatible_spear_contracts"), "compatible_spear_contracts")
    _require_list(authority.get("registered_operations"), "registered_operations")
    _require_list(authority.get("execution_authorized_operations"), "execution_authorized_operations")
    source_control = _require_mapping(parsed.get("source_control"), "source_control")
    _require_list(source_control.get("allowed_base_refs"), "allowed_base_refs")
    _require_list(source_control.get("denied_write_refs"), "denied_write_refs")
    _require_str(source_control.get("future_transaction_branch_regex"), "future_transaction_branch_regex")
    path_safety = _require_mapping(parsed.get("path_safety"), "path_safety")
    for key in ["reject_absolute_paths", "reject_backslashes", "reject_traversal", "reject_percent_encoded_traversal", "reject_control_characters", "reject_trailing_space_or_dot", "reject_case_collisions", "reject_symlinks", "reject_submodules"]:
        if path_safety.get(key) is not True:
            raise PolicyError(f"destination path_safety.{key} must be true")
    if not isinstance(path_safety.get("max_path_bytes"), int):
        raise PolicyError("destination path_safety.max_path_bytes must be integer")
    for path_class in _require_list(parsed.get("path_classes"), "path_classes"):
        cls = _require_mapping(path_class, "path_class")
        _require_str(cls.get("id"), "path_class.id")
        _require_mapping(cls.get("match"), "path_class.match")
        if cls.get("write_lane") not in SUPPORTED_WRITE_LANES:
            raise PolicyError("unsupported destination write_lane")
        _require_list(cls.get("future_operations", []), "path_class.future_operations")
        authority_classes = _require_list(cls.get("authority_classes"), "path_class.authority_classes")
        source_types = _require_list(cls.get("source_types"), "path_class.source_types")
        if not authority_classes or not all(isinstance(item, str) and item for item in authority_classes):
            raise PolicyError("path_class.authority_classes must contain nonempty strings")
        if not source_types or not all(isinstance(item, str) and item for item in source_types):
            raise PolicyError("path_class.source_types must contain nonempty strings")


def _validate_protected_policy(parsed: dict[str, Any]) -> None:
    if parsed.get("repository") != TARGET_REPOSITORY:
        raise PolicyError("protected policy repository mismatch")
    if parsed.get("mode") not in SUPPORTED_PROTECTED_MODES:
        raise PolicyError("unsupported protected policy mode")
    for protected in _require_list(parsed.get("protected_sets"), "protected_sets"):
        item = _require_mapping(protected, "protected_set")
        _require_str(item.get("id"), "protected_set.id")
        _require_mapping(item.get("match"), "protected_set.match")
        mutation = _require_str(item.get("normal_spear_mutation"), "normal_spear_mutation")
        if mutation not in SUPPORTED_PROTECTED_MUTATIONS:
            raise PolicyError("unknown protection mode")
        _require_str(item.get("required_route"), "required_route")
    _require_list(parsed.get("globally_denied_operations"), "globally_denied_operations")
    _require_mapping(parsed.get("content_boundaries"), "content_boundaries")


def load_controlling_policies(prime_repo: str, base_commit: str) -> dict[str, Any]:
    destination_identity, destination, destination_bytes = _policy_object_from_git(prime_repo, base_commit, DESTINATION_POLICY_PATH)
    protected_identity, protected, protected_bytes = _policy_object_from_git(prime_repo, base_commit, PROTECTED_POLICY_PATH)
    _validate_destination_policy(destination)
    _validate_protected_policy(protected)
    authority = destination["authority"]
    source_control = destination["source_control"]
    return {
        "destination_identity": destination_identity,
        "protected_identity": protected_identity,
        "destination": destination,
        "protected": protected,
        "destination_bytes_sha256": sha256_bytes(destination_bytes),
        "protected_bytes_sha256": sha256_bytes(protected_bytes),
        "repository": destination["repository"],
        "future_branch_regex": source_control["future_transaction_branch_regex"],
        "registered_operations": authority["registered_operations"],
        "execution_authorized_operations": authority["execution_authorized_operations"],
        "compatible_spear_contracts": authority["compatible_spear_contracts"],
        "allowed_base_refs": source_control["allowed_base_refs"],
        "denied_write_refs": source_control["denied_write_refs"],
        "path_safety": destination["path_safety"],
        "path_classes": destination["path_classes"],
        "protected_sets": protected["protected_sets"],
        "globally_denied_operations": protected["globally_denied_operations"],
        "content_boundaries": protected["content_boundaries"],
    }


def load_spear_packet_schema(prime_repo: str, base_commit: str) -> tuple[ArtifactIdentity, dict[str, Any], bytes]:
    try:
        data = file_bytes_at_commit(prime_repo, base_commit, SPEAR_PACKET_SCHEMA_PATH)
    except GitError as exc:
        raise PolicyError("Spear packet schema missing at pinned commit") from exc
    blob = blob_sha_at_commit(prime_repo, base_commit, SPEAR_PACKET_SCHEMA_PATH)
    if blob is None:
        raise PolicyError("Spear packet schema missing at pinned commit")
    try:
        schema = load_json_bytes(data)
    except Exception as exc:
        raise PolicyError("Spear packet schema is not valid strict JSON") from exc
    schema_id = schema.get("$id")
    if not isinstance(schema_id, str) or not schema_id:
        raise PolicyError("Spear packet schema is missing $id")
    Draft202012Validator.check_schema(schema)
    identity = ArtifactIdentity(
        path=SPEAR_PACKET_SCHEMA_PATH,
        repository_commit=base_commit,
        git_blob_sha=blob,
        raw_byte_sha256=sha256_bytes(data),
        raw_byte_size=len(data),
        schema_id=schema_id,
    )
    return identity, schema, data


def load_spear_overlay_policy(prime_repo: str, base_commit: str) -> tuple[PolicyIdentity, dict[str, Any], bytes]:
    try:
        data = file_bytes_at_commit(prime_repo, base_commit, SPEAR_OVERLAY_POLICY_PATH)
    except GitError as exc:
        raise PolicyError("Spear overlay policy missing at pinned commit") from exc
    blob = blob_sha_at_commit(prime_repo, base_commit, SPEAR_OVERLAY_POLICY_PATH)
    if blob is None:
        raise PolicyError("Spear overlay policy missing at pinned commit")
    parsed = parse_policy_yaml(data)
    identity = _identity_from_parsed(SPEAR_OVERLAY_POLICY_PATH, base_commit, blob, data, parsed)
    if parsed.get("target_repository") != TARGET_REPOSITORY:
        raise PolicyError("Spear overlay target repository mismatch")
    if parsed.get("contract_id") != SPEAR_CONTRACT_ID:
        raise PolicyError("Spear overlay contract id mismatch")
    for key in ["limits", "allowed_actions", "allowed_extensions", "ordinary_packet_allowed_prefixes", "ordinary_packet_denied_path_globs"]:
        if key not in parsed:
            raise PolicyError(f"Spear overlay policy missing {key}")
    return identity, parsed, data


def effective_limits(schema: dict[str, Any], overlay: dict[str, Any], controlling: dict[str, Any]) -> dict[str, int]:
    policy_limits = overlay["limits"]
    schema_max_ops = schema["properties"]["operations"]["maxItems"]
    schema_max_content = schema["$defs"]["operation"]["properties"]["content_utf8"]["maxLength"]
    schema_max_path = schema["$defs"]["operation"]["properties"]["path"]["maxLength"]
    destination_path_max = int(controlling["path_safety"]["max_path_bytes"])
    if policy_limits["max_operations"] != schema_max_ops:
        raise PolicyError("policy/schema operation limit drift")
    if policy_limits["max_content_bytes"] != schema_max_content:
        raise PolicyError("policy/schema content limit drift")
    if policy_limits["max_path_bytes"] != schema_max_path:
        raise PolicyError("policy/schema path limit drift")
    return {
        "max_operations": min(int(policy_limits["max_operations"]), schema_max_ops),
        "max_decoded_packet_bytes": int(policy_limits["max_decoded_packet_bytes"]),
        "max_content_bytes": min(int(policy_limits["max_content_bytes"]), schema_max_content),
        "max_path_bytes": min(int(policy_limits["max_path_bytes"]), schema_max_path, destination_path_max),
    }


def validate_contract(packet: dict[str, Any], overlay: dict[str, Any], controlling: dict[str, Any]) -> None:
    if packet.get("target_repository") != TARGET_REPOSITORY or packet.get("target_repository") != controlling["repository"]:
        raise PolicyError("repository does not match Prime policy")
    if packet.get("base_branch") != BASE_BRANCH or overlay.get("base_branch") != BASE_BRANCH:
        raise PolicyError("base branch does not match Prime policy")
    if BASE_BRANCH not in controlling["allowed_base_refs"]:
        raise PolicyError("base branch is not allowed by Prime policy")
    if BASE_BRANCH in controlling["denied_write_refs"]:
        pass
    if overlay.get("contract_id") != SPEAR_CONTRACT_ID:
        raise PolicyError("overlay contract id mismatch")
    if SPEAR_CONTRACT_ID not in controlling["compatible_spear_contracts"]:
        raise PolicyError("Spear contract is not compatible with destination policy")
    if controlling["execution_authorized_operations"]:
        raise PolicyError("S0 expected no execution-authorized operations in controlling policy")


def validate_scanner_category_coverage(overlay: dict[str, Any]) -> None:
    declared = set(overlay.get("protected_warning_categories", []))
    future = set(overlay.get("scanner_future_categories", []))
    missing = declared - IMPLEMENTED_SCANNER_CATEGORIES - future
    if missing:
        raise PolicyError("scanner category declared but not implemented: " + ", ".join(sorted(missing)))
    if future:
        raise PolicyError("future scanner categories fail closed in S0: " + ", ".join(sorted(future)))


def validate_action(action: str, overlay: dict[str, Any], controlling: dict[str, Any]) -> None:
    if action not in overlay.get("allowed_actions", []):
        raise PolicyError(f"unsupported action: {action}")
    if action not in controlling["registered_operations"]:
        raise PolicyError(f"operation is not registered by Prime policy: {action}")
    if action in controlling["globally_denied_operations"]:
        raise PolicyError(f"operation is globally denied: {action}")


def _glob_match(path: str, pattern: str) -> bool:
    return fnmatch.fnmatchcase(path, pattern) or fnmatch.fnmatchcase(path + "/", pattern)


def _matches(match: dict[str, Any], path: str) -> bool:
    for exact in match.get("exact", []) or []:
        if path == exact:
            return True
    for prefix in match.get("prefixes", []) or []:
        if path.startswith(prefix):
            return True
    return False


def _destination_class_for(path: str, controlling: dict[str, Any]) -> dict[str, Any] | None:
    matches = [cls for cls in controlling["path_classes"] if _matches(cls.get("match", {}), path)]
    if not matches:
        return None
    return sorted(matches, key=lambda item: int(item.get("precedence", 10_000)))[0]


def destination_class_for(path: str, controlling: dict[str, Any], limits: dict[str, int]) -> dict[str, Any]:
    normalized = normalize_spear_path(path, max_path_bytes=limits["max_path_bytes"])
    cls = _destination_class_for(normalized, controlling)
    if cls is None:
        raise PolicyError("unknown or unauthorized Prime path class blocks ordinary packet")
    return cls


def _protected_matches(path: str, controlling: dict[str, Any]) -> list[dict[str, Any]]:
    return [item for item in controlling["protected_sets"] if _matches(item.get("match", {}), path)]


def validate_path_policy(path: str, overlay: dict[str, Any], controlling: dict[str, Any], limits: dict[str, int], action: str | None = None) -> dict[str, Any]:
    normalized = normalize_spear_path(path, max_path_bytes=limits["max_path_bytes"])
    suffix = PurePosixPath(normalized).suffix.lower()
    if suffix not in overlay.get("allowed_extensions", []):
        raise PolicyError("unsupported file extension")
    for protected in _protected_matches(normalized, controlling):
        raise PolicyError(f"Prime protected policy blocks ordinary packet path: {protected['id']}")
    cls = _destination_class_for(normalized, controlling)
    if cls is None:
        raise PolicyError("unknown or unauthorized Prime path class blocks ordinary packet")
    class_extensions = cls.get("extensions") or []
    if class_extensions and suffix not in class_extensions:
        raise PolicyError("extension is not allowed by destination path class")
    if cls.get("write_lane") not in PLAN_ALLOWED_WRITE_LANES:
        raise PolicyError("destination path class is not an authored-source plan lane")
    if action is not None and action not in (cls.get("future_operations") or []):
        raise PolicyError("operation is not allowed by destination path class")
    for pattern in overlay.get("ordinary_packet_denied_path_globs", []):
        if _glob_match(normalized, pattern):
            raise PolicyError(f"Spear overlay blocks path category: {pattern}")
    overlay_prefixes = overlay.get("ordinary_packet_allowed_prefixes", [])
    if overlay_prefixes and not any(normalized.startswith(prefix) for prefix in overlay_prefixes):
        raise PolicyError("Spear overlay does not allow this path")
    return cls


def scan_content(path: str, content: str) -> list[WarningSummary]:
    checks: list[tuple[str, re.Pattern[str] | bool]] = [
        ("binary_or_nul_content", "\x00" in content),
        ("private_key_marker", _PRIVATE_KEY),
        ("credential_assignment", _CREDENTIAL_ASSIGN),
        ("token_like_value", _TOKEN_LIKE),
        ("env_assignment", _ENV_ASSIGN),
        ("private_network_value", _PRIVATE_IPV4),
        ("account_evidence", _ACCOUNT),
        ("medical_record_identifier", _MEDICAL),
        ("git_lfs_pointer", _LFS),
    ]
    warnings: list[WarningSummary] = []
    for category, checker in checks:
        if isinstance(checker, bool):
            if checker:
                warnings.append(WarningSummary(path=path, category=category, count=1))
        else:
            count = len(list(checker.finditer(content)))
            if count:
                warnings.append(WarningSummary(path=path, category=category, count=count))
    return warnings


def validate_content(path: str, content: str, limits: dict[str, int]) -> list[WarningSummary]:
    if len(content.encode("utf-8")) > limits["max_content_bytes"]:
        raise PolicyError("content exceeds Spear MVP file limit")
    warnings = scan_content(path, content)
    if warnings:
        categories = ", ".join(sorted({w.category for w in warnings}))
        raise PolicyError(f"protected-content scan failed for {path}: {categories}")
    return warnings


def load_source_metadata_schema(prime_repo: str, base_commit: str) -> tuple[ArtifactIdentity, dict[str, Any]]:
    data = file_bytes_at_commit(prime_repo, base_commit, SOURCE_METADATA_SCHEMA_PATH)
    blob = blob_sha_at_commit(prime_repo, base_commit, SOURCE_METADATA_SCHEMA_PATH)
    if blob is None:
        raise PolicyError("source metadata schema missing at pinned commit")
    try:
        schema = json.loads(data.decode("utf-8", errors="strict"))
    except Exception as exc:
        raise PolicyError("source metadata schema is not valid UTF-8 JSON") from exc
    schema_id = schema.get("$id")
    if not isinstance(schema_id, str) or not schema_id:
        raise PolicyError("source metadata schema is missing $id")
    Draft202012Validator.check_schema(schema)
    identity = ArtifactIdentity(
        path=SOURCE_METADATA_SCHEMA_PATH,
        repository_commit=base_commit,
        git_blob_sha=blob,
        raw_byte_sha256=sha256_bytes(data),
        raw_byte_size=len(data),
        schema_id=schema_id,
    )
    return identity, schema


def extract_markdown_front_matter(path: str, content: str) -> dict[str, Any]:
    if not content.startswith("---\n"):
        raise PolicyError(f"Markdown source metadata missing at first byte for {path}")
    closing = content.find("\n---\n", 4)
    if closing == -1:
        raise PolicyError(f"Markdown source metadata closing delimiter missing for {path}")
    raw = content[4:closing]
    try:
        parsed = yaml.load(raw, Loader=UniqueKeySafeLoader)
    except PolicyError:
        raise
    except Exception as exc:
        raise PolicyError(f"Markdown source metadata is malformed for {path}") from exc
    if not isinstance(parsed, dict):
        raise PolicyError(f"Markdown source metadata must be a mapping for {path}")
    return parsed


def validate_markdown_source_metadata(
    path: str,
    content: str,
    schema: dict[str, Any],
    *,
    action: str,
) -> dict[str, Any]:
    metadata = extract_markdown_front_matter(path, content)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(metadata), key=lambda e: list(e.path))
    if errors:
        first = errors[0]
        location = "/".join(str(part) for part in first.path) or "<root>"
        raise PolicyError(f"Markdown source metadata schema validation failed at {location} for {path}")
    if action == "CREATE_FILE" and metadata.get("status") not in {"DRAFT", "PROPOSED"}:
        raise PolicyError(f"CREATE_FILE Markdown status is not pre-merge safe for {path}")
    return metadata


def validate_metadata_destination_class(
    path: str,
    metadata: dict[str, Any],
    destination_class: dict[str, Any],
    packet_source_type: str,
) -> None:
    authority_classes = destination_class.get("authority_classes")
    source_types = destination_class.get("source_types")
    if not isinstance(authority_classes, list) or not authority_classes or not all(isinstance(item, str) and item for item in authority_classes):
        raise PolicyError("destination path class authority_classes are missing or malformed")
    if not isinstance(source_types, list) or not source_types or not all(isinstance(item, str) and item for item in source_types):
        raise PolicyError("destination path class source_types are missing or malformed")
    authority_class = metadata.get("authority_class")
    source_type = metadata.get("source_type")
    if authority_class not in authority_classes:
        raise PolicyError(f"Markdown authority_class is not allowed by destination path class for {path}")
    if source_type not in source_types:
        raise PolicyError(f"Markdown source_type is not allowed by destination path class for {path}")
    class_id = destination_class.get("id")
    if packet_source_type == "POINTER_ONLY":
        if authority_class != "PRIVATE_POINTER":
            raise PolicyError("POINTER_ONLY packet source_type requires PRIVATE_POINTER metadata authority")
    elif packet_source_type == "CLEAN_SUMMARY":
        if authority_class not in {"CONTINUITY_PROVENANCE", "HISTORICAL_REFERENCE"}:
            raise PolicyError("CLEAN_SUMMARY packet source_type requires continuity metadata authority")
    elif packet_source_type == "AUTHORED_SOURCE":
        if authority_class in {"PRIVATE_POINTER", "CONTINUITY_PROVENANCE", "HISTORICAL_REFERENCE", "GENERATED_OPERATIONAL_PROJECTION", "MIGRATION_EVIDENCE"}:
            raise PolicyError("AUTHORED_SOURCE packet source_type is incompatible with metadata authority")
    elif packet_source_type == "GENERATED_FIXTURE":
        if class_id == "project-and-operation-source":
            raise PolicyError("GENERATED_FIXTURE may not enter authored project source paths")
    else:
        raise PolicyError(f"unsupported packet source_type: {packet_source_type}")
