from __future__ import annotations

import importlib.util
import subprocess
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
            ["kernel", "repository_policy", "privacy", "prime_program", "source_validation", "generated_diagnostics"],
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
        self.assertEqual(plan["profile"], "full")
        self.assertEqual(plan["checks"], list(MODULE.FULL_CHECK_IDS))
        self.assertTrue(plan["windows_required"])

    def test_athena_and_oathbringer_tooling_require_windows(self) -> None:
        for changed_path in (
            "tools/athena_routes/adapter.py",
            "tools/oathbringer-foundry/foundry.py",
        ):
            with self.subTest(changed_path=changed_path):
                plan = MODULE.classify_paths([changed_path])
                self.assertTrue(plan["windows_required"])

    def test_generated_path_retirement_keeps_windows_conditional(self) -> None:
        plan = MODULE.classify_paths(["generated/atlas-file-inventory.md"])
        self.assertEqual(plan["profile"], "targeted")
        self.assertIn("generators", plan["checks"])
        self.assertIn("generated_diagnostics", plan["checks"])
        self.assertFalse(plan["windows_required"])

    def test_generator_and_schema_changes_require_windows(self) -> None:
        for changed_path in (
            "tools/build_index.py",
            "tools/generated_checkpoint/core.py",
            "tests/generators/test_build_index.py",
            "schemas/lifecycle/sunset-v2.schema.json",
        ):
            with self.subTest(changed_path=changed_path):
                plan = MODULE.classify_paths([changed_path])
                self.assertTrue(plan["windows_required"])

    def test_mixed_paths_require_windows_when_any_member_requires_it(self) -> None:
        plan = MODULE.classify_paths(
            ["quests/prime-ascendant.md", "schemas/lifecycle/sunset-v2.schema.json"]
        )
        self.assertTrue(plan["windows_required"])
        self.assertEqual(plan["unclassified_paths"], [])

    def test_rename_classifies_both_source_and_destination(self) -> None:
        paths = MODULE._parse_git_name_status_z(
            b"R100\x00tools/build_index.py\x00operations/build-index.md\x00"
        )
        self.assertEqual(paths, ["tools/build_index.py", "operations/build-index.md"])
        plan = MODULE.classify_paths(paths)
        self.assertTrue(plan["windows_required"])

    def test_case_only_rename_requires_windows(self) -> None:
        paths = MODULE._parse_git_name_status_z(
            b"R100\x00quests/prime-ascendant.md\x00quests/Prime-Ascendant.md\x00"
        )
        plan = MODULE.classify_paths(paths)
        self.assertEqual(
            plan["case_collisions"],
            ["quests/Prime-Ascendant.md", "quests/prime-ascendant.md"],
        )
        self.assertTrue(plan["windows_required"])

    def test_malformed_git_name_status_fails_closed(self) -> None:
        for payload in (
            b"R100\x00tools/build_index.py\x00",
            b"Q\x00quests/prime-ascendant.md\x00",
            b"M\x00quests/prime-ascendant.md",
            b"M\x00\xff\x00",
        ):
            with self.subTest(payload=payload):
                with self.assertRaises(ValueError):
                    MODULE._parse_git_name_status_z(payload)

    def test_malformed_and_case_mismatched_paths_fail_closed(self) -> None:
        for changed_path in (
            "",
            "../quests/prime-ascendant.md",
            "quests\\prime-ascendant.md",
            "/quests/prime-ascendant.md",
            "quests/prime-ascendant.md ",
            "quests/prime-ascendant\t.md",
            "Schemas/lifecycle/sunset-v2.schema.json",
        ):
            with self.subTest(changed_path=changed_path):
                plan = MODULE.classify_paths([changed_path])
                self.assertEqual(plan["profile"], "full-fail-closed")
                self.assertEqual(plan["checks"], list(MODULE.FULL_CHECK_IDS))
                self.assertTrue(plan["windows_required"])

    def test_exact_candidate_identity_binds_base_head_and_merge_base(self) -> None:
        head = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, check=True, capture_output=True, text=True
        ).stdout.strip()
        base = subprocess.run(
            ["git", "rev-parse", "HEAD^"], cwd=ROOT, check=True, capture_output=True, text=True
        ).stdout.strip()
        identity = MODULE.git_candidate_identity(base, head)
        self.assertEqual(identity["base_sha"], base)
        self.assertEqual(identity["head_sha"], head)
        self.assertEqual(identity["merge_base_sha"], base)
        self.assertEqual(identity["checkout_sha"], head)

    def test_validation_workflow_exposes_only_required_logical_contexts(self) -> None:
        workflow = (ROOT / ".github/workflows/prime-readonly-validation.yml").read_text(encoding="utf-8")
        for marker in (
            "name: prime/integrity",
            "name: prime/windows-compatibility",
        ):
            self.assertIn(marker, workflow)
        for retired_marker in (
            "name: validate (ubuntu-latest)",
            "name: validate (windows-latest)",
            "legacy_validate_ubuntu:",
            "legacy_validate_windows:",
            "Migration bridge:",
        ):
            self.assertNotIn(retired_marker, workflow)

    def test_validation_workflow_uses_byte_changing_pr_triggers_only(self) -> None:
        workflow = (ROOT / ".github/workflows/prime-readonly-validation.yml").read_text(encoding="utf-8")
        trigger_block = workflow.split("workflow_dispatch:", 1)[0]
        for event in ("opened", "synchronize", "reopened"):
            self.assertIn(f"- {event}", trigger_block)
        self.assertNotIn("ready_for_review", trigger_block)

    def test_privacy_and_repository_policy_are_mandatory_for_every_targeted_plan(self) -> None:
        for changed_path in (
            "README.md",
            "quests/prime-ascendant.md",
            "tools/athena_routes/adapter.py",
            "tests/privacy/test_boundary.py",
        ):
            with self.subTest(changed_path=changed_path):
                plan = MODULE.classify_paths([changed_path])
                self.assertIn("privacy", plan["checks"])
                self.assertIn("repository_policy", plan["checks"])

    def test_unknown_path_fails_closed_to_full_validation(self) -> None:
        plan = MODULE.classify_paths(["unclassified/new-surface.bin"])
        self.assertEqual(plan["profile"], "full-fail-closed")
        self.assertEqual(plan["checks"], list(MODULE.FULL_CHECK_IDS))
        self.assertEqual(plan["unclassified_paths"], ["unclassified/new-surface.bin"])
        self.assertEqual(plan["malformed_paths"], [])
        self.assertTrue(plan["windows_required"])

    def test_full_profile_is_explicit_and_cross_platform(self) -> None:
        plan = MODULE.classify_paths([], full=True)
        self.assertEqual(plan["profile"], "full")
        self.assertEqual(plan["checks"], list(MODULE.FULL_CHECK_IDS))
        self.assertTrue(plan["windows_required"])


if __name__ == "__main__":
    unittest.main()
