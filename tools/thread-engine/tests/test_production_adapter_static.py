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
        self.assertIn("name: Generated projection status", workflow)
        self.assertIn("workflow_dispatch:", workflow)
        self.assertIsNone(re.search(r"(?m)^  push:\s*$", workflow))
        self.assertIsNone(re.search(r"(?m)^  pull_request(?:_target)?:", workflow))
        self.assertIn("group: generated-projection-status-jktomy-atlas-prime", workflow)
        self.assertIn("name: Check generated projection status", workflow)
        self.assertIn("Admit exact owner read-only request", workflow)
        self.assertIn("Build and compare deterministic projections", workflow)
        self.assertIn("tools/build_index.py", workflow)
        self.assertIn("--compare-dir generated", workflow)
        self.assertIn("Generated projections: CURRENT", workflow)
        self.assertIn("Generated projections: STALE", workflow)
        self.assertIn('GITHUB_REPOSITORY -cne "Jktomy/atlas-prime"', workflow)
        self.assertIn("GITHUB_ACTOR -cne $env:GITHUB_REPOSITORY_OWNER", workflow)
        self.assertIn("GITHUB_TRIGGERING_ACTOR -cne $env:GITHUB_REPOSITORY_OWNER", workflow)
        self.assertIn('GITHUB_REF -cne "refs/heads/main"', workflow)
        self.assertIn("PUBLIC_CLEAN_CONFIRMED", workflow)
        self.assertIn("git/ref/heads/main", workflow)
        self.assertIn("contents: read", workflow)
        self.assertNotIn("contents: write", workflow)
        self.assertNotIn("pull-requests: write", workflow)
        self.assertNotIn("production_adapter.cli", workflow)
        self.assertNotIn("tools.generated_checkpoint.hosted_prepare", workflow)
        self.assertNotIn("--generated-checkpoint-route", workflow)
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
        for forbidden in (
            "INPUT_REPLAY_NONCE",
            "actions: write",
            "gh workflow run",
            "gh pr create",
            "gh pr close",
            "gh pr ready",
            "gh pr merge",
            "force-push",
            "git push",
            "--force",
            "persist-credentials: true",
            "automatic merge",
        ):
            self.assertNotIn(forbidden, workflow.casefold() if forbidden == "automatic merge" else workflow)

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
