from __future__ import annotations

import json
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]


def _yaml_block(source: str, key: str, indent: int) -> list[str]:
    lines = source.splitlines()
    header = f"{' ' * indent}{key}:"
    matches = [index for index, line in enumerate(lines) if line == header]
    if len(matches) != 1:
        raise AssertionError(f"expected one {key!r} block at indent {indent}, found {len(matches)}")
    block: list[str] = []
    for line in lines[matches[0] + 1 :]:
        if line.strip() and len(line) - len(line.lstrip()) <= indent:
            break
        block.append(line)
    while block and not block[-1].strip():
        block.pop()
    return block


class SpearSurfaceBridgeTests(unittest.TestCase):
    def test_workflow_is_default_branch_issue_comment_only(self) -> None:
        source = (ROOT / ".github/workflows/athena-spear-issue-ingress.yml").read_text(encoding="utf-8")
        self.assertEqual(
            _yaml_block(source, "on", 0),
            [
                "  issue_comment:",
                "    types: [created]",
            ],
        )
        self.assertNotIn("pull_request_target:", source)
        self.assertIn("  cancel-in-progress: false", _yaml_block(source, "concurrency", 0))
        execute = _yaml_block(source, "execute-or-resume", 2)
        self.assertEqual(
            _yaml_block("\n".join(execute), "permissions", 4),
            [
                "      contents: write",
                "      issues: write",
                "      pull-requests: write",
            ],
        )
        self.assertIn("    environment: atlas-spear-ingress", execute)
        self.assertIn("secrets.ATLAS_SPEAR_INGRESS_PRIVATE_KEY_V1", "\n".join(execute))

    def test_key_policy_contains_no_private_key(self) -> None:
        policy = json.loads((ROOT / "config/athena-spear-ingress-public-keys.json").read_text(encoding="utf-8"))
        self.assertIs(policy["source_contains_private_key"], False)
        self.assertIs(policy["repository_pat_required"], False)
        self.assertIs(policy["activation_requires_separate_jayson_authority"], True)

    def test_schemas_are_closed_at_authority_fields(self) -> None:
        for path in (
            ROOT / "schemas/athena-spear-issue-envelope-v1.schema.json",
            ROOT / "schemas/athena-spear-issue-receipt-v1.schema.json",
        ):
            schema = json.loads(path.read_text(encoding="utf-8"))
            Draft202012Validator.check_schema(schema)
        receipt_schema = json.loads((ROOT / "schemas/athena-spear-issue-receipt-v1.schema.json").read_text())
        forbidden = receipt_schema["properties"]["forbidden_actions"]["properties"]
        self.assertTrue(all(spec == {"const": False} for spec in forbidden.values()))

    def test_issue_ingress_uses_direct_spear_path_scope(self) -> None:
        source = (ROOT / "tools/athena_routes/spear_issue_ingress.py").read_text(encoding="utf-8")
        self.assertIn("from production_adapter.protected_paths import direct_spear_path_scope", source)
        self.assertIn("with direct_spear_path_scope():", source)


if __name__ == "__main__":
    unittest.main()
