from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

TARGET_REPOSITORY = "Jktomy/atlas-prime"
BASE_BRANCH = "main"
SPEAR_CONTRACT_ID = "athenas-spear/0.3"
COMPILER_VERSION = "4.0.0-s0"
DESTINATION_POLICY_PATH = "policies/destination/atlas-prime-destination-policy-v0.2.yaml"
PROTECTED_POLICY_PATH = "policies/protected-paths/protected-paths-v0.2.yaml"
SOURCE_METADATA_SCHEMA_PATH = "schemas/source-metadata/source-metadata-v1.schema.json"
SPEAR_PACKET_SCHEMA_PATH = "schemas/spear/spear-packet-v1.schema.json"
SPEAR_OVERLAY_POLICY_PATH = "policies/operations/spear/spear-policy-v1.yaml"
EXECUTION_STATE = "EXECUTION_NOT_AUTHORIZED"


class SpearError(ValueError):
    """Base class for closed-fail Spear validation errors."""


class DuplicateKeyError(SpearError):
    """Raised when JSON contains duplicate object keys."""


class PolicyError(SpearError):
    """Raised when policy validation fails."""


class StateError(SpearError):
    """Raised when expected repository state does not match."""


class GitError(SpearError):
    """Raised for explicit Git-state failures."""

    def __init__(self, kind: str, message: str):
        super().__init__(message)
        self.kind = kind


@dataclass(frozen=True)
class WarningSummary:
    path: str
    category: str
    count: int


@dataclass(frozen=True)
class PolicyIdentity:
    path: str
    repository_commit: str
    git_blob_sha: str
    sha256: str
    raw_byte_size: int
    policy_id: str
    policy_version: str


@dataclass(frozen=True)
class ArtifactIdentity:
    path: str
    repository_commit: str
    git_blob_sha: str
    raw_byte_sha256: str
    raw_byte_size: int
    schema_id: str


@dataclass(frozen=True)
class ContractIdentity:
    compiler_version: str
    packet_schema: ArtifactIdentity
    overlay_policy: PolicyIdentity
    destination_policy: PolicyIdentity
    protected_policy: PolicyIdentity
    source_metadata_schema: ArtifactIdentity


@dataclass
class CompileResult:
    normalized_packet: dict[str, Any]
    operation_manifest: dict[str, Any]
    receipt: dict[str, Any]
    proposed_files: dict[str, str] = field(default_factory=dict)
