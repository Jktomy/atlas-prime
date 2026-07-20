from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PUBLISHER_PATH = ROOT / ".github/workflows/generated-checkpoint-publisher.yml"
TARGETED_VALIDATION_TEST_PATH = ROOT / "tests/prime-program/test_targeted_validation.py"


class GeneratedPublisherCheckoutTests(unittest.TestCase):
    def test_exact_head_validation_has_full_history_for_candidate_identity(self) -> None:
        workflow = PUBLISHER_PATH.read_text(encoding="utf-8")
        job_marker = "\n  validate_exact_head:\n"
        self.assertEqual(workflow.count(job_marker), 1)
        job = workflow.split(job_marker, 1)[1]

        step_marker = "      - name: Check out immutable generated head\n"
        self.assertEqual(job.count(step_marker), 1)
        checkout_step = job.split(step_marker, 1)[1].split("\n      - name:", 1)[0]

        self.assertIn("          fetch-depth: 0\n", checkout_step)
        self.assertNotIn("          fetch-depth: 1\n", checkout_step)

        candidate_identity_test = TARGETED_VALIDATION_TEST_PATH.read_text(encoding="utf-8")
        self.assertIn('["git", "rev-parse", "HEAD^"]', candidate_identity_test)
        self.assertIn("git_candidate_identity(base, head)", candidate_identity_test)


if __name__ == "__main__":
    unittest.main()
