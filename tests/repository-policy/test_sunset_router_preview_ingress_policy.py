from __future__ import annotations

import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RETIRED_WORKFLOW = ROOT / ".github/workflows/sunset-router-preview-intake.yml"
ADAPTER = ROOT / "tools/sunset_router/issue_preview_ingress.py"


class SunsetRouterPreviewIngressPolicyTests(unittest.TestCase):
    def test_historical_adapter_exposes_no_repository_mutation_surface(self) -> None:
        tree = ast.parse(ADAPTER.read_text(encoding="utf-8"))
        forbidden_calls = {
            "create_branch",
            "create_file",
            "update_file",
            "delete_file",
            "create_pull_request",
            "mark_pull_request_ready_for_review",
            "merge_pull_request",
            "update_ref",
            "subprocess",
            "requests",
        }
        names = {
            node.id
            for node in ast.walk(tree)
            if isinstance(node, ast.Name)
        }
        attributes = {
            node.attr
            for node in ast.walk(tree)
            if isinstance(node, ast.Attribute)
        }
        self.assertTrue(forbidden_calls.isdisjoint(names | attributes))
        text = ADAPTER.read_text(encoding="utf-8")
        self.assertNotIn("api.github.com", text)
        self.assertNotIn("git push", text)
        self.assertNotIn("gh api", text)

    def test_campaign_workflow_is_retired_without_runner_guard(self) -> None:
        self.assertFalse(RETIRED_WORKFLOW.exists())
        workflow_text = "\n".join(
            path.read_text(encoding="utf-8")
            for pattern in ("*.yml", "*.yaml")
            for path in sorted((ROOT / ".github/workflows").glob(pattern))
        )
        for retired_marker in (
            "Mission 257 Sunset Router Preview intake",
            "tools.sunset_router.issue_preview_ingress",
            "atlas-sunset-router-preview-intake-v1",
        ):
            self.assertNotIn(retired_marker, workflow_text)

    def test_historical_adapter_retains_exact_owner_and_non_pr_authority(self) -> None:
        adapter = ADAPTER.read_text(encoding="utf-8")
        for marker in (
            'issue.get("pull_request") is not None',
            'comment["user"].get("login") != EXPECTED_OWNER',
            'comment.get("author_association") != "OWNER"',
            'sender.get("login") != EXPECTED_OWNER',
            'repository.get("full_name") != EXPECTED_REPOSITORY',
        ):
            self.assertIn(marker, adapter)

    def test_retirement_is_canonical_and_does_not_claim_replacement_transport(self) -> None:
        contract = (ROOT / "governance/sunset-router-contract.md").read_text(encoding="utf-8")
        readme = (ROOT / "tools/sunset_router/README.md").read_text(encoding="utf-8")
        commands = (ROOT / "routing/command-surfaces.md").read_text(encoding="utf-8")

        self.assertIn("## Retired Mission-comment Preview ingress", contract)
        self.assertIn("must remain absent", contract)
        self.assertIn("No replacement runner guard is permitted", contract)
        self.assertIn("## Retired Mission #257 Preview ingress", readme)
        self.assertIn("intentionally absent", readme)
        self.assertIn("Historical Mission #257 owner-only Sunset Preview ingress", commands)
        self.assertIn("`RETIRED`", commands)
        for text in (contract, readme, commands):
            self.assertNotIn("workflow_dispatch", text)


if __name__ == "__main__":
    unittest.main()
