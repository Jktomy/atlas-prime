from __future__ import annotations

import ast
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ADAPTER = ROOT / "production_adapter"
sys.path.insert(0, str(ROOT))


class ProductionAdapterStaticTests(unittest.TestCase):
    def test_python_sources_parse(self) -> None:
        for path in ADAPTER.rglob("*.py"):
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))

    def test_schema_and_examples_are_json(self) -> None:
        for path in ADAPTER.rglob("*.json"):
            json.loads(path.read_text(encoding="utf-8"))

    def test_mission_examples_pass_prime_runtime_validation(self) -> None:
        from production_adapter.authority import load_mission

        for path in sorted((ADAPTER / "examples").glob("*.mission.example.json")):
            mission = load_mission(path)
            self.assertEqual(mission.repository, "Jktomy/atlas-prime")

    def test_no_dynamic_execution_or_shell_eval(self) -> None:
        forbidden_calls = {"eval", "exec", "compile", "__import__"}
        for path in ADAPTER.rglob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                    self.assertNotIn(node.func.id, forbidden_calls, str(path))
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "run":
                    for keyword in node.keywords:
                        self.assertFalse(keyword.arg == "shell" and getattr(keyword.value, "value", None) is True)

    def test_network_libraries_absent_and_launcher_safe(self) -> None:
        forbidden = [r"\brequests\b", r"\burllib\b", r"\bhttp\.client\b", r"\bsocket\b", "Invoke-Expression", "Read-Host", "Start-Process"]
        runtime_files = list(ADAPTER.rglob("*.py")) + [ROOT / "Invoke-AtlasThreadEngineProductionAdapter.ps1"]
        for path in runtime_files:
            text = path.read_text(encoding="utf-8")
            for pattern in forbidden:
                self.assertIsNone(re.search(pattern, text), f"{pattern} in {path}")

    def test_aegis_break_self_change_policy_is_protected(self) -> None:
        from production_adapter.protected_paths import PROTECTED_EXACT, PROTECTED_PREFIXES, THREAD_ENGINE_SELF_CHANGE_EXACT, THREAD_ENGINE_SELF_CHANGE_PREFIXES, is_thread_engine_self_change_path
        from pathlib import PurePosixPath

        self.assertTrue(THREAD_ENGINE_SELF_CHANGE_EXACT <= PROTECTED_EXACT)
        for prefix in THREAD_ENGINE_SELF_CHANGE_PREFIXES:
            self.assertIn(prefix, PROTECTED_PREFIXES)
        self.assertFalse(is_thread_engine_self_change_path(PurePosixPath("governance/noctua.md")))
        self.assertTrue(is_thread_engine_self_change_path(PurePosixPath("tools/thread-engine/production_adapter/adapter.py")))

    def test_cli_and_launcher_retain_only_prime_protected_route(self) -> None:
        cli = (ADAPTER / "cli.py").read_text(encoding="utf-8")
        launcher = (ROOT / "Invoke-AtlasThreadEngineProductionAdapter.ps1").read_text(encoding="utf-8")
        self.assertIn("--aegis-break-protected-route", cli)
        self.assertIn("--aegis-break-authority-id", cli)
        self.assertIn("aegis_break_protected_route=args.aegis_break_protected_route", cli)
        self.assertIn("aegis_break_authority_id=args.aegis_break_authority_id", cli)
        self.assertIn("--generated-checkpoint-route", cli)
        self.assertIn("generated_checkpoint_route=args.generated_checkpoint_route", cli)
        self.assertNotIn("workboard", cli.casefold())
        self.assertIn("[switch] $AegisBreakProtectedRoute", launcher)
        self.assertIn("[string] $AegisBreakAuthorityId", launcher)
        self.assertIn("--aegis-break-protected-route", launcher)
        self.assertIn("--aegis-break-authority-id", launcher)
        self.assertIn("[switch] $GeneratedCheckpointRoute", launcher)
        self.assertIn("--generated-checkpoint-route", launcher)
        self.assertIn("production_adapter.cli", launcher)
        self.assertIn("ResolverSelfTest", launcher)
        self.assertNotIn("workboard", launcher.casefold())

    def test_codex_workboard_authority_schema_is_absent(self) -> None:
        schema = json.loads((ADAPTER / "production_mission.schema.json").read_text(encoding="utf-8"))
        self.assertNotIn("workboard_row_update_authority", schema["properties"])
        self.assertFalse(schema.get("additionalProperties", True))

    def test_generated_checkpoint_profile_and_workflow_are_closed(self) -> None:
        schema = json.loads((ADAPTER / "production_mission.schema.json").read_text(encoding="utf-8"))
        profile = schema["properties"]["generated_checkpoint_profile"]
        self.assertFalse(profile["additionalProperties"])
        self.assertEqual(profile["properties"]["profile_id"]["const"], "GENERATED_CHECKPOINT_V1")
        source = (ADAPTER / "generated_checkpoint.py").read_text(encoding="utf-8")
        adapter = (ADAPTER / "adapter.py").read_text(encoding="utf-8")
        preparer = (ROOT.parent / "generated_checkpoint" / "core.py").read_text(encoding="utf-8")
        workflow = (ROOT.parents[1] / ".github" / "workflows" / "generated-checkpoint-publisher.yml").read_text(encoding="utf-8")
        self.assertNotIn("subprocess", preparer)
        self.assertIn("workflow_dispatch:", workflow)
        self.assertIn("push:", workflow)
        self.assertIsNone(re.search(r"(?m)^  pull_request(?:_target)?:", workflow))
        self.assertNotIn("paths-ignore:", workflow)
        self.assertNotIn('- "generated/**"', workflow)
        self.assertIn("group: generated-checkpoint-publisher-jktomy-atlas-prime", workflow)

        queue_block = workflow.split("\n  queue:\n", 1)[1].split("\n  parity:\n", 1)[0]
        parity_block = workflow.split("\n  parity:\n", 1)[1].split("\n  reconcile:\n", 1)[0]
        reconcile_block = workflow.split("\n  reconcile:\n", 1)[1].split("\n  prepare:\n", 1)[0]
        prepare_block = workflow.split("\n  prepare:\n", 1)[1].split("\n  publish:\n", 1)[0]
        publish_block = workflow.split("\n  publish:\n", 1)[1].split("\n  validate_exact_head:\n", 1)[0]
        validate_block = workflow.split("\n  validate_exact_head:\n", 1)[1]
        first_queue_step = queue_block.split("\n    steps:\n", 1)[1].lstrip()
        self.assertTrue(first_queue_step.startswith("- name: Admit exact publisher invocation"))
        self.assertLess(queue_block.index("Admit exact publisher invocation"), queue_block.index("uses:"))
        for phrase in (
            'expectedRepository = "Jktomy/atlas-prime"',
            'expectedOwner = "Jktomy"',
            "$env:GITHUB_ACTOR",
            "$env:GITHUB_TRIGGERING_ACTOR",
            "$env:GITHUB_EVENT_NAME -ceq \"push\"",
            "$env:GITHUB_EVENT_NAME -ceq \"workflow_dispatch\"",
            "$env:GITHUB_REF -cne \"refs/heads/main\"",
            "$env:GITHUB_SHA",
            "$env:GITHUB_WORKFLOW_SHA",
            "$env:GENERATED_BASE_SHA",
            "git/ref/heads/main",
        ):
            self.assertIn(phrase, queue_block)
        self.assertIn("contents: read", queue_block)
        self.assertIn("pull-requests: read", queue_block)
        self.assertNotIn("contents: write", queue_block)
        self.assertNotIn("pull-requests: write", queue_block)
        self.assertIn("--limit 1001", queue_block)
        self.assertIn("tools.generated_checkpoint.queue", queue_block)
        self.assertIn("DEFERRED_OPEN_CHECKPOINT", queue_block)
        self.assertIn("receipt_sha256", queue_block)

        self.assertIn("needs: queue", parity_block)
        self.assertIn("needs.queue.result == 'success'", parity_block)
        self.assertIn("needs.queue.outputs.queue_result == 'CLEAR'", parity_block)
        self.assertIn("ubuntu-latest", parity_block)
        self.assertIn("windows-latest", parity_block)
        self.assertIn("needs: parity", reconcile_block)
        self.assertIn("needs: reconcile", prepare_block)
        self.assertIn("tools.generated_checkpoint.hosted_prepare", prepare_block)
        self.assertIn("route_result=NOOP", prepare_block)
        self.assertIn("- prepare", publish_block)
        self.assertIn("--generated-checkpoint-route", publish_block)
        self.assertEqual(publish_block.count("production_adapter.cli"), 1)
        self.assertIn("Bind exact generated draft readback", publish_block)
        self.assertIn("needs: publish", validate_block)
        self.assertIn("needs.publish.outputs.head_sha", validate_block)
        for block in (parity_block, reconcile_block, prepare_block, publish_block, validate_block):
            job_preamble = block.split("\n    steps:\n", 1)[0]
            self.assertNotIn("always()", job_preamble)
            self.assertNotIn("!cancelled()", job_preamble)
            self.assertNotIn("continue-on-error", block)

        self.assertEqual(workflow.count("contents: write"), 1)
        self.assertEqual(workflow.count("pull-requests: write"), 1)
        self.assertEqual(workflow.count("production_adapter.cli"), 1)
        self.assertEqual(
            workflow.count("persist-credentials: false"),
            workflow.count("uses: actions/checkout@"),
        )
        action_uses = re.findall(r"(?m)^\s*uses:\s+(\S+)\s*$", workflow)
        self.assertTrue(action_uses)
        for action in action_uses:
            self.assertRegex(
                action,
                r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+@[0-9a-f]{40}$",
            )
        self.assertNotIn("INPUT_REPLAY_NONCE", workflow)
        self.assertNotIn("actions: write", workflow)
        self.assertNotIn("gh workflow run", workflow)
        self.assertNotIn("gh pr close", workflow)
        self.assertNotIn("gh pr ready", workflow)
        self.assertNotIn("gh pr merge", workflow)
        self.assertNotIn("force-push", workflow)
        self.assertNotIn("git push", workflow)
        self.assertNotIn("--force", workflow)
        self.assertNotIn("persist-credentials: true", workflow)
        self.assertNotIn("automatic merge", workflow.casefold())
        self.assertIn("PRE_PUSH_REMOTE_LOCK", adapter)
        self.assertIn("GENERATED_CHECKPOINT_PR_COLLISION", source)
        self.assertIn('"--limit", "1001", "--json"', adapter)
        self.assertIn("fresh_clone_reproduction", source)

    def test_lifecycle_profile_is_closed_and_uses_the_protected_draft_route(self) -> None:
        schema = json.loads((ADAPTER / "production_mission.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(
            schema["properties"]["lifecycle_profile"]["$ref"],
            "../../../lifecycle/schemas/lifecycle-construction-profile-v1.schema.json",
        )
        source = (ADAPTER / "lifecycle_profile.py").read_text(encoding="utf-8")
        self.assertIn('"AEGIS_BREAK_THREAD_ENGINE_PROTECTED"', source)
        self.assertIn('"DRAFT_PR_READBACK"', source)
        self.assertNotIn("importlib", source)
        self.assertNotIn("subprocess", source)
        self.assertNotIn("automatic_ready\": True", source)
        self.assertNotIn("automatic_merge\": True", source)

    def test_git_runner_exact_templates_deny_unsafe_routes(self) -> None:
        from production_adapter.git_runner import GitRunner, GitRunnerError
        from production_adapter.readback import REVIEW_THREAD_QUERY

        with tempfile.TemporaryDirectory(prefix="atlas-gate7f-static-") as tmp_text:
            runner = GitRunner(
                allowed_remote="https://github.com/Jktomy/atlas-prime.git",
                allowed_api_prefix="https://api.github.com/repos/Jktomy/atlas-prime",
                mission_branch="source/gate-7f-unit",
                base_sha="d81fda533e7a15dcb4cc4ae08163dcc1c23f2b05",
                declared_paths=("docs/new.txt",),
                commit_message="prime: unit production adapter mission",
                pr_title="prime: unit production adapter mission",
                disabled_hooks=Path(tmp_text) / "hooks",
            )
            allowed = [
                ["git", "push", "-u", "origin", "source/gate-7f-unit"],
                ["git", "add", "--", "docs/new.txt"],
                ["gh", "api", "user", "--jq", ".login"],
                ["gh", "pr", "list", "--repo", "Jktomy/atlas-prime", "--state", "all", "--head", "source/gate-7f-unit", "--json", "number,state,isDraft,headRefOid"],
                ["gh", "pr", "list", "--repo", "Jktomy/atlas-prime", "--state", "all", "--limit", "1001", "--json", "number,state,isDraft,headRefName,headRefOid,title,body"],
                ["gh", "api", "graphql", "-f", f"query={REVIEW_THREAD_QUERY}", "-f", "owner=Jktomy", "-f", "name=atlas-prime", "-f", "head=source/gate-7f-unit"],
            ]
            for args in allowed:
                runner._validate(args)
            denied = [
                ["git", "push", "--force", "origin", "source/gate-7f-unit"],
                ["git", "push", "-u", "upstream", "source/gate-7f-unit"],
                ["git", "push", "-u", "origin", "main"],
                ["git", "push", "-u", "origin", "+source/gate-7f-unit"],
                ["git", "push", "-u", "origin", ":source/gate-7f-unit"],
                ["git", "reset", "--hard"],
                ["git", "rebase", "main"],
                ["git", "tag", "x"],
                ["gh", "api", "repos/Jktomy/atlas-prime"],
                ["gh", "api", "graphql", "-f", "query=query { viewer { login } }", "-f", "owner=Jktomy", "-f", "name=atlas-prime", "-f", "head=source/gate-7f-unit"],
                ["gh", "api", "graphql", "-f", f"query={REVIEW_THREAD_QUERY} mutation {{ __typename }}", "-f", "owner=Jktomy", "-f", "name=atlas-prime", "-f", "head=source/gate-7f-unit"],
                ["gh", "api", "graphql", "-f", f"query={REVIEW_THREAD_QUERY}", "-f", "owner=Other", "-f", "name=atlas-prime", "-f", "head=source/gate-7f-unit"],
                ["gh", "api", "graphql", "-f", f"query={REVIEW_THREAD_QUERY}", "-f", "owner=Jktomy", "-f", "name=other", "-f", "head=source/gate-7f-unit"],
                ["gh", "api", "graphql", "-f", f"query={REVIEW_THREAD_QUERY}", "-f", "owner=Jktomy", "-f", "name=atlas-prime", "-f", "head=other"],
                ["gh", "api", "graphql", "-f", f"query={REVIEW_THREAD_QUERY}", "-f", "owner=Jktomy", "-f", "name=atlas-prime", "-f", "head=source/gate-7f-unit", "--paginate"],
                ["gh", "api", "graphql", "-X", "POST", "-f", f"query={REVIEW_THREAD_QUERY}", "-f", "owner=Jktomy", "-f", "name=atlas-prime", "-f", "head=source/gate-7f-unit"],
                ["gh", "api", "graphql", "-f", f"query={REVIEW_THREAD_QUERY}", "-f", "owner=Jktomy", "-f", "name=atlas-prime", "-f", "head=source/gate-7f-unit", "-f", "extra=x"],
                ["gh", "pr", "list", "--repo", "Jktomy/atlas-prime", "--state", "all", "--limit", "1000", "--json", "number,state,isDraft,headRefName,headRefOid,title,body"],
                ["gh", "pr", "merge", "1"],
                ["gh", "pr", "ready", "1"],
                ["gh", "pr", "edit", "1"],
                ["gh", "workflow", "run", "x"],
                ["gh", "pr", "create", "--repo", "Jktomy/atlas-prime", "--base", "main", "--head", "source/gate-7f-unit", "--title", "prime: unit production adapter mission", "--body-file", "body.md"],
            ]
            for args in denied:
                with self.subTest(args=args), self.assertRaises(GitRunnerError):
                    runner._validate(args)


if __name__ == "__main__":
    unittest.main()
