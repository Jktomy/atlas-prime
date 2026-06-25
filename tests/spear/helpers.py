from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "schemas/spear/spear-packet-v1.schema.json"
POLICY = ROOT / "policies/operations/spear/spear-policy-v1.yaml"
FIXTURES = ROOT / "tests/fixtures/spear"

DEST_POLICY_TEXT = """policy_id: atlas-prime-destination-policy
policy_version: 0.2.0
status: PREVIEW
mode: V03_CONTRACT_PREVIEW
repository: Jktomy/atlas-prime
authority:
  repository_writes_authorized: false
  compatible_spear_contracts:
  - athenas-spear/0.3
  registered_operations:
  - CREATE_FILE
  - REPLACE_FILE_FULL
  execution_authorized_operations: []
source_control:
  allowed_base_refs:
  - main
  denied_write_refs:
  - main
  future_transaction_branch_regex: ^spear/[0-9]{8}-[0-9]{3}-[a-f0-9]{8}$
path_safety:
  reject_absolute_paths: true
  reject_backslashes: true
  reject_traversal: true
  reject_percent_encoded_traversal: true
  reject_control_characters: true
  reject_trailing_space_or_dot: true
  reject_case_collisions: true
  reject_symlinks: true
  reject_submodules: true
  max_path_bytes: 500
path_classes:
- id: project-and-operation-source
  precedence: 50
  match:
    prefixes:
    - projects/
  write_lane: SOURCE_PR
  current_mutation: DENY
  extensions:
  - .md
  future_operations:
  - CREATE_FILE
  - REPLACE_FILE_FULL
"""
PROT_POLICY_TEXT = """policy_id: atlas-prime-protected-paths
policy_version: 0.2.0
status: PREVIEW
mode: DENY_BY_DEFAULT
repository: Jktomy/atlas-prime
protected_sets:
- id: spear-self-protection
  level: CRITICAL
  match:
    prefixes:
    - tools/spear/
    - policies/operations/spear
  normal_spear_mutation: DENY
  required_route: SEPARATE_SPEAR_ENGINE_UPDATE
  controls: []
content_boundaries:
  prohibited_raw_content:
  - TOKENS
  permitted_forms:
  - PUBLIC_CLEAN
  diagnostics_must_redact_matches: true
globally_denied_operations:
- DIRECT_MAIN_WRITE
- FORCE_PUSH
- AUTOMATIC_MERGE
- HARD_DELETE
- MOVE_OR_RENAME
- PACKET_SELECTED_SHELL_COMMAND
- SPEAR_SELF_MODIFICATION
"""


SOURCE_METADATA_SCHEMA_TEXT = "{\n  \"$schema\": \"https://json-schema.org/draft/2020-12/schema\",\n  \"$id\": \"https://atlas-prime.local/schemas/source-metadata-v1.schema.json\",\n  \"title\": \"Atlas Prime Markdown Source Metadata v1\",\n  \"description\": \"Schema for YAML front matter extracted from authored Atlas Prime Markdown and represented as JSON.\",\n  \"type\": \"object\",\n  \"additionalProperties\": false,\n  \"required\": [\n    \"title\",\n    \"atlas_id\",\n    \"format_version\",\n    \"status\",\n    \"source_type\",\n    \"authority_class\",\n    \"owner_project\",\n    \"owner_operation\",\n    \"canonical_scope\",\n    \"protected_level\",\n    \"routes_from\",\n    \"routes_to\",\n    \"private_boundary\",\n    \"evidence_boundary\",\n    \"supersedes\",\n    \"cleanup_path\",\n    \"last_verified\"\n  ],\n  \"properties\": {\n    \"title\": {\n      \"type\": \"string\",\n      \"minLength\": 1,\n      \"maxLength\": 200\n    },\n    \"atlas_id\": {\n      \"type\": \"string\",\n      \"pattern\": \"^[a-z0-9]+(?:[.-][a-z0-9]+)*$\",\n      \"minLength\": 3,\n      \"maxLength\": 200\n    },\n    \"format_version\": {\n      \"const\": \"1.0\"\n    },\n    \"status\": {\n      \"enum\": [\n        \"DRAFT\",\n        \"PROPOSED\",\n        \"ACTIVE\",\n        \"SUPERSEDED\",\n        \"RETIRED\",\n        \"HISTORICAL\",\n        \"GENERATED\"\n      ]\n    },\n    \"source_type\": {\n      \"enum\": [\n        \"BOOTSTRAP\",\n        \"CORE_DOCTRINE\",\n        \"PROTOCOL\",\n        \"STANDARD\",\n        \"SPECIFICATION\",\n        \"POLICY\",\n        \"PROJECT\",\n        \"OPERATION\",\n        \"RUNBOOK\",\n        \"TEMPLATE\",\n        \"REFERENCE\",\n        \"REGISTER_VIEW\",\n        \"GENERATED_VIEW\",\n        \"MIGRATION_RECORD\",\n        \"HISTORICAL_RECORD\",\n        \"TOOL_DOCUMENTATION\"\n      ]\n    },\n    \"authority_class\": {\n      \"enum\": [\n        \"CANONICAL_AUTHORED_SOURCE\",\n        \"STRUCTURED_AUTHORITATIVE_REGISTER\",\n        \"GENERATED_OPERATIONAL_PROJECTION\",\n        \"CONTINUITY_PROVENANCE\",\n        \"TOOL_CONTRACT\",\n        \"TOOL_IMPLEMENTATION\",\n        \"MIGRATION_EVIDENCE\",\n        \"HISTORICAL_REFERENCE\",\n        \"PRIVATE_POINTER\"\n      ]\n    },\n    \"owner_project\": {\n      \"type\": \"string\",\n      \"minLength\": 1,\n      \"maxLength\": 100\n    },\n    \"owner_operation\": {\n      \"oneOf\": [\n        {\n          \"type\": \"string\",\n          \"minLength\": 1,\n          \"maxLength\": 120\n        },\n        {\n          \"type\": \"null\"\n        }\n      ]\n    },\n    \"canonical_scope\": {\n      \"type\": \"string\",\n      \"minLength\": 10,\n      \"maxLength\": 2000\n    },\n    \"protected_level\": {\n      \"enum\": [\n        \"LOW\",\n        \"MEDIUM\",\n        \"HIGH\",\n        \"CRITICAL\"\n      ]\n    },\n    \"routes_from\": {\n      \"$ref\": \"#/$defs/path_array\"\n    },\n    \"routes_to\": {\n      \"$ref\": \"#/$defs/path_array\"\n    },\n    \"private_boundary\": {\n      \"type\": \"string\",\n      \"minLength\": 10,\n      \"maxLength\": 2000\n    },\n    \"evidence_boundary\": {\n      \"type\": \"string\",\n      \"minLength\": 10,\n      \"maxLength\": 2000\n    },\n    \"supersedes\": {\n      \"$ref\": \"#/$defs/path_array\"\n    },\n    \"cleanup_path\": {\n      \"type\": \"string\",\n      \"minLength\": 5,\n      \"maxLength\": 2000\n    },\n    \"last_verified\": {\n      \"oneOf\": [\n        {\n          \"type\": \"string\",\n          \"format\": \"date\"\n        },\n        {\n          \"type\": \"null\"\n        }\n      ]\n    },\n    \"superseded_by\": {\n      \"$ref\": \"#/$defs/path_array\"\n    }\n  },\n  \"allOf\": [\n    {\n      \"if\": {\n        \"properties\": {\n          \"status\": {\n            \"const\": \"GENERATED\"\n          }\n        }\n      },\n      \"then\": {\n        \"properties\": {\n          \"authority_class\": {\n            \"const\": \"GENERATED_OPERATIONAL_PROJECTION\"\n          },\n          \"source_type\": {\n            \"enum\": [\n              \"GENERATED_VIEW\",\n              \"REGISTER_VIEW\"\n            ]\n          }\n        }\n      }\n    },\n    {\n      \"if\": {\n        \"properties\": {\n          \"authority_class\": {\n            \"const\": \"GENERATED_OPERATIONAL_PROJECTION\"\n          }\n        }\n      },\n      \"then\": {\n        \"properties\": {\n          \"status\": {\n            \"const\": \"GENERATED\"\n          }\n        }\n      }\n    },\n    {\n      \"if\": {\n        \"properties\": {\n          \"status\": {\n            \"const\": \"SUPERSEDED\"\n          }\n        }\n      },\n      \"then\": {\n        \"required\": [\n          \"superseded_by\"\n        ],\n        \"properties\": {\n          \"superseded_by\": {\n            \"minItems\": 1\n          }\n        }\n      }\n    }\n  ],\n  \"$defs\": {\n    \"repository_path\": {\n      \"type\": \"string\",\n      \"minLength\": 1,\n      \"maxLength\": 500,\n      \"pattern\": \"^(?!/)(?!.*(?:^|/)\\\\.\\\\.(?:/|$))(?!.*\\\\\\\\)(?!.*[\\\\x00-\\\\x1f\\\\x7f]).+$\"\n    },\n    \"path_array\": {\n      \"type\": \"array\",\n      \"items\": {\n        \"$ref\": \"#/$defs/repository_path\"\n      },\n      \"uniqueItems\": true,\n      \"maxItems\": 100\n    }\n  }\n}\n"


def run(args: list[str], cwd: Path) -> str:
    return subprocess.check_output(args, cwd=str(cwd), text=True, encoding="utf-8")


def init_repo(repo: Path) -> str:
    repo.mkdir(parents=True)
    run(["git", "init", "-b", "main"], repo)
    run(["git", "config", "user.email", "spear@example.test"], repo)
    run(["git", "config", "user.name", "Spear Test"], repo)
    (repo / "policies/destination").mkdir(parents=True)
    (repo / "policies/protected-paths").mkdir(parents=True)
    (repo / "schemas/source-metadata").mkdir(parents=True)
    (repo / "projects/spear").mkdir(parents=True)
    (repo / "policies/destination/atlas-prime-destination-policy-v0.2.yaml").write_text(DEST_POLICY_TEXT, encoding="utf-8")
    (repo / "policies/protected-paths/protected-paths-v0.2.yaml").write_text(PROT_POLICY_TEXT, encoding="utf-8")
    (repo / "schemas/source-metadata/source-metadata-v1.schema.json").write_text(SOURCE_METADATA_SCHEMA_TEXT, encoding="utf-8")
    (repo / "projects/spear/existing.md").write_text('---\ntitle: Spear Existing Test Document\natlas_id: spear.fixture.existing-base\nformat_version: "1.0"\nstatus: PROPOSED\nsource_type: TOOL_DOCUMENTATION\nauthority_class: TOOL_CONTRACT\nowner_project: Codex\nowner_operation: Athena\'s Spear\ncanonical_scope: Provides harmless existing Markdown content for Athena\'s Spear S0 replacement tests.\nprotected_level: LOW\nroutes_from:\n  - athenas-spear.md\nroutes_to:\n  - tools/spear/cli.py\nprivate_boundary: This fixture contains public clean test text only and no private or protected evidence.\nevidence_boundary: This fixture is generated test evidence and not canonical Atlas doctrine or runtime evidence.\nsupersedes: []\ncleanup_path: Remove or update only through a reviewed Spear test fixture PR.\nlast_verified: 2026-06-24\n---\n\n# Spear existing target\n\nOriginal harmless text.\n', encoding="utf-8")
    run(["git", "add", "."], repo)
    run(["git", "commit", "-m", "initial"], repo)
    return run(["git", "rev-parse", "HEAD"], repo).strip()


def fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def write_packet(path: Path, packet: dict) -> str:
    data = json.dumps(packet, ensure_ascii=False, sort_keys=True, indent=2).encode("utf-8") + b"\n"
    path.write_bytes(data)
    return hashlib.sha256(data).hexdigest()


def blob(repo: Path, commit: str, path: str) -> str:
    return run(["git", "rev-parse", f"{commit}:{path}"], repo).strip()


def cli_args(repo: Path, packet_path: Path, packet_sha: str, out: Path) -> list[str]:
    return [
        "--packet", str(packet_path),
        "--packet-sha256", packet_sha,
        "--schema", str(SCHEMA),
        "--policy", str(POLICY),
        "--repository", str(repo),
        "--base-ref", "main",
        "--output-root", str(out),
    ]
