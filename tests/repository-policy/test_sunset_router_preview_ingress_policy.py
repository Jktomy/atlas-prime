from __future__ import annotations

import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github/workflows/sunset-router-preview-intake.yml"
ADAPTER = ROOT / "tools/sunset_router/issue_preview_ingress.py"


class SunsetRouterPreviewIngressPolicyTests(unittest.TestCase):
    def test_adapter_exposes_no_repository_mutation_surface(self) -> None:
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

    def test_workflow_has_only_read_contents_and_issue_comment_write(self) -> None:
        workflow = WORKFLOW.read_text(encoding="utf-8")
        permission_block = workflow.split("concurrency:", 1)[0]
        self.assertIn("contents: read", permission_block)
        self.assertIn("issues: write", permission_block)
        for forbidden in (
            "contents: write",
            "pull-requests: write",
            "actions: write",
            "checks: write",
            "statuses: write",
            "id-token: write",
        ):
            self.assertNotIn(forbidden, workflow)
        self.assertIn("persist-credentials: false", workflow)
        self.assertNotIn("workflow_dispatch:", workflow)

    def test_workflow_is_exact_mission_owner_comment_surface(self) -> None:
        workflow = WORKFLOW.read_text(encoding="utf-8")
        for marker in (
            "issue_comment:",
            "- created",
            "github.event.issue.number == 257",
            "!github.event.issue.pull_request",
            "github.event.comment.user.login == github.repository_owner",
            "github.event.comment.author_association == 'OWNER'",
            "expected_repository='Jktomy/atlas-prime'",
            "expected_owner='Jktomy'",
            "refs/heads/main",
        ):
            self.assertIn(marker, workflow)

    def test_workflow_invokes_only_preview_lifecycle_command(self) -> None:
        workflow = WORKFLOW.read_text(encoding="utf-8")
        self.assertEqual(workflow.count("python -B -m tools.sunset_router \\\n"), 1)
        self.assertIn("preview \\\n", workflow)
        for forbidden in (
            " approve ",
            " candidate ",
            " receipt ",
            "git commit",
            "git push",
            "gh pr create",
            "gh pr ready",
            "gh pr merge",
        ):
            self.assertNotIn(forbidden, workflow)


if __name__ == "__main__":
    unittest.main()
