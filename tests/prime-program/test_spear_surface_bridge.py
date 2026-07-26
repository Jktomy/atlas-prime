from __future__ import annotations

import json
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]


def test_workflow_is_default_branch_issue_comment_only() -> None:
    value = yaml.safe_load((ROOT / ".github/workflows/athena-spear-issue-ingress.yml").read_text(encoding="utf-8"))
    trigger = value.get(True, value.get("on"))
    assert trigger == {"issue_comment": {"types": ["created"]}}
    assert "pull_request_target" not in value
    assert value["concurrency"]["cancel-in-progress"] is False
    execute = value["jobs"]["execute-or-resume"]
    assert execute["permissions"] == {"contents": "write", "issues": "write", "pull-requests": "write"}
    assert execute["environment"] == "atlas-spear-ingress"
    assert "secrets.ATLAS_SPEAR_INGRESS_PRIVATE_KEY_V1" in json.dumps(execute)


def test_key_policy_contains_no_private_key() -> None:
    policy = json.loads((ROOT / "config/athena-spear-ingress-public-keys.json").read_text(encoding="utf-8"))
    assert policy["source_contains_private_key"] is False
    assert policy["repository_pat_required"] is False
    assert policy["activation_requires_separate_jayson_authority"] is True


def test_schemas_are_closed_at_authority_fields() -> None:
    for path in (
        ROOT / "schemas/athena-spear-issue-envelope-v1.schema.json",
        ROOT / "schemas/athena-spear-issue-receipt-v1.schema.json",
    ):
        schema = json.loads(path.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
    receipt_schema = json.loads((ROOT / "schemas/athena-spear-issue-receipt-v1.schema.json").read_text())
    forbidden = receipt_schema["properties"]["forbidden_actions"]["properties"]
    assert all(spec == {"const": False} for spec in forbidden.values())

def test_issue_ingress_uses_direct_spear_path_scope() -> None:
    source = (ROOT / "tools/athena_routes/spear_issue_ingress.py").read_text(encoding="utf-8")
    assert "from production_adapter.protected_paths import direct_spear_path_scope" in source
    assert "with direct_spear_path_scope():" in source
