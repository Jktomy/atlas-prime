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
        forbidden = ["requests", "urllib", "http.client", "socket", "os.environ", "getenv", "GITHUB_TOKEN", "SECRET"]
        for path in self.python_sources():
            text = path.read_text(encoding="utf-8-sig")
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

    def test_no_workflow_files_in_s0(self) -> None:
        self.assertFalse((ROOT / ".github").exists())

    def test_yaml_loading_uses_unique_safe_loader_only(self) -> None:
        text = (TOOLS / "policy.py").read_text(encoding="utf-8-sig")
        self.assertIn("class UniqueKeySafeLoader(yaml.SafeLoader)", text)
        self.assertIn("yaml.load(data.decode", text)
        self.assertIn("Loader=UniqueKeySafeLoader", text)
        self.assertNotIn("yaml.unsafe_load", text)
        self.assertNotIn("yaml.FullLoader", text)
        self.assertNotIn("Loader=yaml.Loader", text)


if __name__ == "__main__": unittest.main()