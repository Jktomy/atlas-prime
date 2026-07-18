from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "tools" / "prime_checks" / "targeted_validation.py"
SPEC = importlib.util.spec_from_file_location("targeted_validation", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class TargetedValidationTests(unittest.TestCase):
    def test_docs_only_change_uses_one_targeted_linux_profile(self) -> None:
        plan = MODULE.classify_paths(["quests/prime-ascendant.md"])
        self.assertEqual(plan["profile"], "targeted")
        self.assertEqual(
            plan["checks"],
            ["kernel", "privacy", "prime_program", "source_validation"],
        )
        self.assertFalse(plan["windows_required"])
        self.assertEqual(plan["unclassified_paths"], [])

    def test_thread_engine_change_requires_bounded_cross_platform_checks(self) -> None:
        plan = MODULE.classify_paths(["tools/thread-engine/production_adapter/adapter.py"])
        self.assertEqual(plan["profile"], "targeted")
        for check_id in (
            "repository_policy",
            "thread_engine",
            "thread_engine_static",
            "prime_program",
            "source_validation",
            "powershell_resolver",
        ):
            self.assertIn(check_id, plan["checks"])
        self.assertTrue(plan["windows_required"])

    def test_workflow_change_runs_full_cross_platform_validation(self) -> None:
        plan = MODULE.classify_paths([".github/workflows/prime-readonly-validation.yml"])
        self.assertEqual(plan["profile"], "targeted")
        self.assertEqual(plan["checks"], list(MODULE.FULL_CHECK_IDS))
        self.assertTrue(plan["windows_required"])

    def test_unknown_path_fails_closed_to_full_validation(self) -> None:
        plan = MODULE.classify_paths(["unclassified/new-surface.bin"])
        self.assertEqual(plan["profile"], "full-fail-closed")
        self.assertEqual(plan["checks"], list(MODULE.FULL_CHECK_IDS))
        self.assertEqual(plan["unclassified_paths"], ["unclassified/new-surface.bin"])
        self.assertTrue(plan["windows_required"])

    def test_full_profile_is_explicit_and_cross_platform(self) -> None:
        plan = MODULE.classify_paths([], full=True)
        self.assertEqual(plan["profile"], "full")
        self.assertEqual(plan["checks"], list(MODULE.FULL_CHECK_IDS))
        self.assertTrue(plan["windows_required"])


if __name__ == "__main__":
    unittest.main()
