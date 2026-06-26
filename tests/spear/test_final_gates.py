from __future__ import annotations

import json
import unittest
from pathlib import Path

from tools.spear.models import EXECUTION_STATE
from tools.spear.policy import IMPLEMENTED_SCANNER_CATEGORIES, load_controlling_policies
from tools.spear.validate import load_json_file, load_json_policy
from .helpers import POLICY, SCHEMA, fixture, init_repo

ROOT = Path(__file__).resolve().parents[2]


class FinalGateTests(unittest.TestCase):
    def test_registered_operation_names_only_in_schema(self) -> None:
        schema = load_json_file(str(SCHEMA))
        self.assertEqual(schema["$defs"]["operation"]["properties"]["action"]["enum"], ["CREATE_FILE", "REPLACE_FILE_FULL"])

    def test_no_legacy_create_update_actions_in_fixtures(self) -> None:
        for name in ["valid-create.json", "valid-update.json", "valid-multi.json"]:
            actions = {op["action"] for op in fixture(name)["operations"]}
            self.assertNotIn("CREATE", actions); self.assertNotIn("UPDATE", actions)

    def test_approval_basis_is_required_by_schema(self) -> None:
        schema = load_json_file(str(SCHEMA))
        self.assertIn("approval_basis", schema["required"])

    def test_overlay_declares_prime_compatible_contract(self) -> None:
        overlay = load_json_policy(str(POLICY))
        self.assertEqual(overlay["contract_id"], "athenas-spear/0.3")
        self.assertEqual(overlay["policy_version"], "4.0.0")

    def test_overlay_declares_no_more_than_five_operations(self) -> None:
        overlay = load_json_policy(str(POLICY))
        self.assertLessEqual(overlay["limits"]["max_operations"], 5)

    def test_overlay_declares_sixteen_kib_content_limit(self) -> None:
        overlay = load_json_policy(str(POLICY))
        self.assertLessEqual(overlay["limits"]["max_content_bytes"], 16 * 1024)

    def test_declared_scanner_categories_are_implemented(self) -> None:
        overlay = load_json_policy(str(POLICY))
        self.assertTrue(set(overlay["protected_warning_categories"]).issubset(IMPLEMENTED_SCANNER_CATEGORIES))

    def test_dependency_toml_pins_complete_closure(self) -> None:
        text = (ROOT / "tools/spear/dependencies-v1.toml").read_text(encoding="utf-8")
        self.assertIn('contract_version = "1.0"', text)
        for line in [
            'jsonschema = "4.26.0"',
            'attrs = "26.1.0"',
            'jsonschema-specifications = "2025.9.1"',
            'PyYAML = "6.0.2"',
            'referencing = "0.37.0"',
            'rpds-py = "2026.5.1"',
        ]:
            self.assertIn(line, text)
        self.assertFalse((ROOT / "requirements-spear.txt").exists())
        self.assertFalse((ROOT / "requirements-spear-lock.txt").exists())

    def test_s1_workflow_exists_but_apply_is_hard_disabled(self) -> None:
        workflow = ROOT / ".github/workflows/spear-s1-draft-pr-writer.yml"
        text = workflow.read_text(encoding="utf-8")
        self.assertIn("workflow_dispatch:", text)
        self.assertIn("if: ${{ false }}", text)
        self.assertIn("contents: write", text)
        self.assertIn("pull-requests: write", text)
        self.assertIn("S1_APPLY_HARD_DISABLED", text)
        self.assertNotIn("pull_request:", text)
        self.assertNotIn("push:", text)
        self.assertNotIn("force", text.lower())

    def test_cli_requires_repository_argument(self) -> None:
        text = (ROOT / "tools/spear/cli.py").read_text(encoding="utf-8")
        self.assertIn('parser.add_argument("--repository", required=True', text)

    def test_cli_requires_packet_transport_hash(self) -> None:
        text = (ROOT / "tools/spear/cli.py").read_text(encoding="utf-8")
        self.assertIn('parser.add_argument("--packet-sha256", required=True', text)

    def test_cli_does_not_accept_external_schema_or_policy_paths(self) -> None:
        text = (ROOT / "tools/spear/cli.py").read_text(encoding="utf-8")
        self.assertNotIn('parser.add_argument("--schema"', text)
        self.assertNotIn('parser.add_argument("--policy"', text)

    def test_no_legacy_branch_template_in_compile_source(self) -> None:
        text = (ROOT / "tools/spear/compile.py").read_text(encoding="utf-8")
        self.assertNotIn('spear/{packet', text)

    def test_execution_state_constant_is_not_authorized(self) -> None:
        self.assertEqual(EXECUTION_STATE, "EXECUTION_NOT_AUTHORIZED")

    def test_policy_loader_records_protected_policy_identity(self) -> None:
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d) / "repo"; commit = init_repo(repo); policies = load_controlling_policies(str(repo), commit)
            self.assertEqual(policies["protected_identity"].policy_id, "atlas-prime-protected-paths")
            self.assertEqual(len(policies["protected_identity"].sha256), 64)

    def test_a3a_contract_assets_exist_with_disabled_writer_only(self) -> None:
        required = [
            ROOT / "specs/spear/athenas-spear-a3-g0-golden-transaction-suite-v1.md",
            ROOT / "tools/spear/s1_contracts.py",
            ROOT / "tools/spear/s1_writer.py",
            ROOT / "tools/spear/s1_cli.py",
            ROOT / "tools/spear/s1_git_adapter.py",
            ROOT / "tools/spear/s1_pr_client.py",
            ROOT / "tools/spear/s1_recovery.py",
            ROOT / "tools/spear/s1_receipts.py",
            ROOT / "policies/operations/spear/spear-s1-activation-v1.json",
            ROOT / "schemas/spear/spear-execution-envelope-v1.schema.json",
            ROOT / "schemas/spear/spear-execution-preview-v1.schema.json",
            ROOT / "schemas/spear/spear-execution-receipt-v1.schema.json",
            ROOT / "schemas/spear/spear-golden-transaction-suite-v1.schema.json",
            ROOT / "tests/fixtures/spear/golden-transactions-v1.json",
            ROOT / ".github/workflows/spear-s1-draft-pr-writer.yml",
        ]
        for path in required:
            self.assertTrue(path.is_file(), path)

    def test_s1_activation_policy_is_exactly_disabled(self) -> None:
        policy = load_json_file(str(ROOT / "policies/operations/spear/spear-s1-activation-v1.json"))
        self.assertIs(policy["enabled"], False)
        self.assertEqual(policy["mode"], "DISABLED")
        self.assertIs(policy["repository_writes_authorized"], False)
        self.assertEqual(policy["authorized_operations"], [])
        self.assertIsNone(policy["activation_reference"])
        self.assertTrue(all(value is False for value in policy["authority"].values()))

    def test_runbook_metadata_covers_s0_and_disabled_a3b_s1(self) -> None:
        operator = (ROOT / "tools/spear/operator-runbook.md").read_text(encoding="utf-8")
        recovery = (ROOT / "tools/spear/recovery-runbook.md").read_text(encoding="utf-8")
        for text in (operator, recovery):
            self.assertIn("S0/S1", text)
            self.assertIn("last_verified: 2026-06-26", text)
            self.assertIn("tools/spear/s1_writer.py", text)
            self.assertIn(".github/workflows/spear-s1-draft-pr-writer.yml", text)
        self.assertIn("S1_APPLY_HARD_DISABLED", operator)
        self.assertIn("packet-ID replay collision", recovery)


if __name__ == "__main__": unittest.main()
