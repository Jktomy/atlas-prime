from __future__ import annotations

import ast
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class SpearBridgeStaticTests(unittest.TestCase):
    def runtime_text(self) -> str:
        paths = [
            ROOT / "spear_bridge" / "__init__.py",
            ROOT / "spear_bridge" / "compiler.py",
            ROOT / "spear_bridge" / "git_reader.py",
            ROOT / "spear_bridge" / "cli.py",
            ROOT / "Invoke-AtlasThreadEngineSpearBridge.ps1",
        ]
        return "\n".join(path.read_text(encoding="utf-8") for path in paths)

    def test_python_sources_parse(self) -> None:
        for path in (ROOT / "spear_bridge").glob("*.py"):
            with self.subTest(path=path.name):
                ast.parse(path.read_text(encoding="utf-8"))

    def test_no_adapter_or_github_mutation_route(self) -> None:
        text = self.runtime_text()
        forbidden = [
            r"\bgh\b",
            r"execute_mission",
            r"workflow_dispatch",
            r"pull_request_target",
            r"git\s+commit",
            r"git\s+push",
            r"git\s+branch",
            r"Invoke-Expression",
            r"shell=True",
            r"requests",
            r"urllib\.request",
            r"httpx",
        ]
        for pattern in forbidden:
            with self.subTest(pattern=pattern):
                self.assertIsNone(re.search(pattern, text))

    def test_source_absence_is_fail_closed(self) -> None:
        compiler = (ROOT / "spear_bridge" / "compiler.py").read_text(encoding="utf-8")
        reader = (ROOT / "spear_bridge" / "git_reader.py").read_text(encoding="utf-8")
        self.assertIn("except SourceAbsentError", compiler)
        self.assertNotIn("except Exception", compiler)
        self.assertIn("class SourceAbsentError", reader)
        self.assertIn("self.observed_base", reader)

    def test_disabled_compile_only_constants_are_present(self) -> None:
        text = self.runtime_text()
        for value in ["SPEAR_BRIDGE_DISABLED", "COMPILE_ONLY", "SPEAR_DIRECT", "MISSION_COMPILED"]:
            with self.subTest(value=value):
                self.assertIn(value, text)

    def test_launcher_uses_native_argument_array_and_application_commands(self) -> None:
        launcher = (ROOT / "Invoke-AtlasThreadEngineSpearBridge.ps1").read_text(encoding="utf-8")
        self.assertIn("& $python.Executable @argumentList", launcher)
        self.assertIn("Get-Command $candidate.Name -CommandType Application", launcher)
        self.assertNotIn("Invoke-Expression", launcher)
        self.assertNotIn("Resolve-Path $name", launcher)
        self.assertIn("--read-only-remote-url", launcher)

    def test_git_reader_enforces_noninteractive_authentication_and_redaction(self) -> None:
        reader = (ROOT / "spear_bridge" / "git_reader.py").read_text(encoding="utf-8")
        self.assertIn('"GCM_INTERACTIVE"] = "Never"', reader)
        self.assertIn("GIT_TERMINAL_PROMPT", (ROOT / "production_adapter" / "git_environment.py").read_text(encoding="utf-8"))
        self.assertIn("TOKEN_REMOTE_PATTERN", reader)
        self.assertIn("_sanitize_git_message", reader)
        self.assertNotIn("credential.helper=store", reader)
        self.assertNotIn("GIT_ASKPASS=require", reader)

    def test_clone_disposal_restores_owned_write_bits_before_delete(self) -> None:
        reader = (ROOT / "spear_bridge" / "git_reader.py").read_text(encoding="utf-8")
        self.assertIn("_make_owned_tree_writable", reader)
        self.assertIn("self._assert_owned_descendant(target)", reader)
        self.assertIn("stat.S_IWUSR", reader)


if __name__ == "__main__":
    unittest.main()
