from __future__ import annotations

import json
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github/workflows/athena-spear-issue-ingress.yml"


class SpearSurfaceRetirementTests(unittest.TestCase):
    def test_github_issue_ingress_workflow_is_retired(self) -> None:
        self.assertFalse(WORKFLOW.exists())
        contract = (ROOT / "governance/aegis-break-primary-route-contract.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("CURRENT_GITHUB_SPEAR_RETIRED", contract)
        self.assertIn("future Gitea", contract)

    def test_dormant_bridge_source_and_schemas_remain_readable(self) -> None:
        for path in (
            ROOT / "tools/athena_routes/spear_issue_client.py",
            ROOT / "tools/athena_routes/spear_issue_crypto.py",
            ROOT / "tools/athena_routes/spear_issue_ingress.py",
            ROOT / "schemas/athena-spear-issue-envelope-v1.schema.json",
            ROOT / "schemas/athena-spear-issue-receipt-v1.schema.json",
        ):
            self.assertTrue(path.is_file(), path)

    def test_key_policy_contains_no_private_key(self) -> None:
        policy = json.loads(
            (ROOT / "config/athena-spear-ingress-public-keys.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertIs(policy["source_contains_private_key"], False)
        self.assertIs(policy["repository_pat_required"], False)
        self.assertIs(policy["activation_requires_separate_jayson_authority"], True)

    def test_schemas_remain_closed_at_authority_fields(self) -> None:
        for path in (
            ROOT / "schemas/athena-spear-issue-envelope-v1.schema.json",
            ROOT / "schemas/athena-spear-issue-receipt-v1.schema.json",
        ):
            schema = json.loads(path.read_text(encoding="utf-8"))
            Draft202012Validator.check_schema(schema)
        receipt_schema = json.loads(
            (ROOT / "schemas/athena-spear-issue-receipt-v1.schema.json").read_text()
        )
        forbidden = receipt_schema["properties"]["forbidden_actions"]["properties"]
        self.assertTrue(all(spec == {"const": False} for spec in forbidden.values()))

    def test_dormant_ingress_preserves_direct_spear_path_scope(self) -> None:
        source = (ROOT / "tools/athena_routes/spear_issue_ingress.py").read_text(
            encoding="utf-8"
        )
        self.assertIn(
            "from production_adapter.protected_paths import direct_spear_path_scope",
            source,
        )
        self.assertIn("with direct_spear_path_scope():", source)


if __name__ == "__main__":
    unittest.main()
