from __future__ import annotations

import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "tools/spear"


class SecuritySourceTests(unittest.TestCase):
    def python_sources(self) -> list[Path]: return sorted(TOOLS.glob("*.py"))

    def test_no_shell_true_or_unsafe_subprocess_construction(self) -> None:
        for path in self.python_sources():
            tree = ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    for kw in node.keywords:
                        self.assertFalse(kw.arg == "shell" and isinstance(kw.value, ast.Constant) and kw.value.value is True, path)

    def test_no_network_or_secret_environment_access(self) -> None:
        forbidden = ["requests", "http.client", "socket", "os.environ", "getenv", "GITHUB_TOKEN", "SECRET"]
        for path in self.python_sources():
            text = path.read_text(encoding="utf-8-sig")
            if path.name != "s1_pr_client.py":
                self.assertNotIn("urllib", text, f"urllib in {path}")
            for needle in forbidden: self.assertNotIn(needle, text, f"{needle} in {path}")

    def test_git_adapter_allows_read_only_commands_only(self) -> None:
        path = TOOLS / "git_adapter.py"; text = path.read_text(encoding="utf-8-sig"); tree = ast.parse(text, filename=str(path))
        assigned_sets = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "_ALLOWED_READ_COMMANDS":
                        assigned_sets.append({elt.value for elt in node.value.elts if isinstance(elt, ast.Constant)})
        self.assertEqual(assigned_sets, [{"rev-parse", "ls-files", "cat-file", "show", "status"}])

    def test_no_destructive_file_operations_or_timestamps(self) -> None:
        forbidden = ["rmtree", ".unlink(", "Remove-Item", "shutil.move", "os.remove", "os.rmdir", "datetime.now", "utcnow", "time.time", "locale.", "strftime", "random.", "uuid4"]
        for path in self.python_sources():
            text = path.read_text(encoding="utf-8-sig")
            for needle in forbidden: self.assertNotIn(needle, text, f"{needle} in {path}")

    def test_workflow_files_are_s1_only_and_hard_disabled(self) -> None:
        workflow = ROOT / ".github/workflows/spear-s1-draft-pr-writer.yml"
        text = workflow.read_text(encoding="utf-8-sig")
        self.assertIn("workflow_dispatch:", text)
        self.assertIn("if: ${{ false }}", text)
        self.assertIn("S1_APPLY_HARD_DISABLED", text)
        self.assertNotIn("pull_request:", text)
        self.assertNotIn("push:", text)

    def test_yaml_loading_uses_unique_safe_loader_only(self) -> None:
        text = (TOOLS / "policy.py").read_text(encoding="utf-8-sig")
        self.assertIn("class UniqueKeySafeLoader(yaml.SafeLoader)", text)
        self.assertIn("yaml.load(data.decode", text)
        self.assertIn("Loader=UniqueKeySafeLoader", text)
        self.assertNotIn("yaml.unsafe_load", text)
        self.assertNotIn("yaml.FullLoader", text)
        self.assertNotIn("Loader=yaml.Loader", text)

    def test_a3b_writer_surface_exists_but_forbidden_capabilities_are_absent(self) -> None:
        for relative in [
            "s1_writer.py",
            "s1_cli.py",
            "s1_git_adapter.py",
            "s1_pr_client.py",
            "s1_recovery.py",
            "s1_receipts.py",
        ]:
            self.assertTrue((TOOLS / relative).exists(), relative)
        combined = "\n".join(path.read_text(encoding="utf-8-sig") for path in self.python_sources())
        for needle in [
            "git push",
            "force_push(",
            "merge_pull_request",
            "delete_branch",
            "packet_selected_command(",
        ]:
            self.assertNotIn(needle, combined)

    def test_s1_contract_module_has_no_mutating_git_or_github_client(self) -> None:
        text = (TOOLS / "s1_contracts.py").read_text(encoding="utf-8-sig")
        for needle in [
            "git push",
            "update-ref",
            "checkout -b",
            "requests",
            "urllib",
            "GITHUB_TOKEN",
            "pull-requests: write",
            "contents: write",
        ]:
            self.assertNotIn(needle, text)


if __name__ == "__main__": unittest.main()
