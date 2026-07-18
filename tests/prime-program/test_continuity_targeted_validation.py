from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "tools" / "prime_checks" / "targeted_validation.py"
SPEC = importlib.util.spec_from_file_location("targeted_validation_continuity", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class ContinuityTargetedValidationTests(unittest.TestCase):
    def test_continuity_change_uses_canonical_validator_without_windows(self) -> None:
        plan = MODULE.classify_paths(["continuity/prime-continuity-register-r01.json"])
        self.assertEqual(plan["profile"], "targeted")
        self.assertEqual(
            plan["checks"],
            ["kernel", "repository_policy", "privacy", "source_validation", "continuity"],
        )
        self.assertFalse(plan["windows_required"])
        self.assertEqual(plan["unclassified_paths"], [])
        self.assertEqual(
            MODULE.CHECKS["continuity"].command,
            (MODULE.PYTHON, "-B", "-m", "tools.prime_continuity.cli", "validate"),
        )

    def test_full_surface_drops_duplicate_continuity_check(self) -> None:
        plan = MODULE.classify_paths(
            [
                ".github/workflows/prime-readonly-validation.yml",
                "continuity/prime-continuity-register-r01.json",
            ]
        )
        self.assertEqual(plan["profile"], "full")
        self.assertEqual(plan["checks"], list(MODULE.FULL_CHECK_IDS))
        self.assertNotIn("continuity", plan["checks"])
        self.assertTrue(plan["windows_required"])


if __name__ == "__main__":
    unittest.main()
