from __future__ import annotations

import io
import json
import sys
import unittest
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[2]
THREAD_ENGINE = ROOT / "tools" / "thread-engine"
sys.path.insert(0, str(THREAD_ENGINE))

from production_adapter.protected_paths import POLICY_PATH, is_protected_path, is_thread_engine_self_change_path


class RepositoryPolicyTests(unittest.TestCase):
    def test_000_temporary_remaining_prime_modules(self) -> None:
        suite = unittest.TestSuite()
        for filename in (
            "test_context_pack.py",
            "test_chromelight.py",
            "test_resonance.py",
            "test_shardblade_permanence.py",
            "test_oathbringer_foundry.py",
            "test_investiture_accounting.py",
            "test_oathbringer_foundry_lifecycle.py",
            "test_oathbringer_console_v2.py",
            "test_oathbringer_repair_parent_tree.py",
            "test_investiture_construction_acceptance.py",
            "test_consistent_pr_delivery_standard.py",
            "test_investiture_storage.py",
            "test_agentic_warrants.py",
        ):
            suite.addTests(unittest.defaultTestLoader.discover(str(ROOT / "tests" / "prime-program"), pattern=filename))
        result = unittest.TextTestRunner(stream=io.StringIO(), verbosity=0).run(suite)
        self.assertTrue(result.wasSuccessful(), "TEMP_REMAINING_PRIME_MODULES_FAILED")

    def test_repository_and_operator_invariants(self) -> None:
        repository = json.loads((ROOT / "policies" / "repository-policy.json").read_text(encoding="utf-8"))
        operator = json.loads((ROOT / "policies" / "operator-policy.json").read_text(encoding="utf-8"))
        self.assertEqual(repository["repository"], "Jktomy/atlas-prime")
        self.assertEqual(repository["state"], "CANONICAL_ACTIVE")
        self.assertEqual(repository["canonical_repository"], "Jktomy/atlas-prime")
        self.assertEqual(repository["predecessor_repository"], "Jktomy/atlas-codex")
        self.assertEqual(repository["predecessor_role"], "FROZEN_PREDECESSOR_ROLLBACK_EVIDENCE")
        for field in ("direct_main_allowed", "force_push_allowed", "automatic_ready_allowed", "automatic_merge_allowed", "repository_settings_mutation_allowed", "standing_writer_allowed", "generated_output_authoritative"):
            self.assertFalse(repository[field], field)
        self.assertTrue(operator["draft_pr_only"])
        self.assertTrue(operator["human_merge_required"])
        self.assertFalse(operator["standing_authority"])

    def test_live_code_loads_the_reviewed_prime_policy(self) -> None:
        self.assertEqual(POLICY_PATH, ROOT / "policies" / "protected-paths.json")
        required = {"README.md", "bootstrap.md", "atlas-prime.md", "atlas-start-here.md", "quests/prime-reborn.md", "governance/noctua.md", "policies/repository-policy.json", "schemas/thread-engine/mission.json", "migration/codex-inheritance-manifest.md", "lifecycle/events/fixture-event.json", "quest-board/quest-board.md", "generated/atlas-health.md", "tools/thread-engine/production_adapter/adapter.py", ".github/workflows/prime-readonly-validation.yml"}
        for value in required:
            with self.subTest(value=value):
                self.assertTrue(is_protected_path(PurePosixPath(value)))
        self.assertFalse(is_protected_path(PurePosixPath("proof/harmless.md")))
        self.assertTrue(is_thread_engine_self_change_path(PurePosixPath("tools/thread-engine/README.md")))
        self.assertFalse(is_thread_engine_self_change_path(PurePosixPath("governance/noctua.md")))

    def test_codex_workboard_route_is_absent_from_executable_surface(self) -> None:
        files = [THREAD_ENGINE / "production_adapter" / "adapter.py", THREAD_ENGINE / "production_adapter" / "authority.py", THREAD_ENGINE / "production_adapter" / "cli.py", THREAD_ENGINE / "production_adapter" / "production_mission.schema.json"]
        for path in files:
            text = path.read_text(encoding="utf-8").casefold()
            with self.subTest(path=path.name):
                self.assertNotIn("workboard", text)
                self.assertNotIn("codex/atlas-active-workboard.md", text)


if __name__ == "__main__":
    unittest.main()
