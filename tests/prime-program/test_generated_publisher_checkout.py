from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PUBLISHER_PATH = ROOT / ".github/workflows/generated-checkpoint-publisher.yml"
PR_VALIDATION_PATH = ROOT / ".github/workflows/prime-readonly-validation.yml"
TARGETED_VALIDATION_TEST_PATH = ROOT / "tests/prime-program/test_targeted_validation.py"
CONSERVATION_PATH = ROOT / "governance/deterministic-conservation-contract.md"


class GeneratedPublisherCheckoutTests(unittest.TestCase):
    def test_publisher_is_retired_and_pr_validation_owns_diagnostics(self) -> None:
        self.assertFalse(PUBLISHER_PATH.exists())

        validation = PR_VALIDATION_PATH.read_text(encoding="utf-8")
        self.assertIn("pull_request:", validation)
        self.assertIn("name: prime/integrity", validation)
        self.assertIn("name: prime/windows-compatibility", validation)
        self.assertIn(
            "ref: ${{ github.event_name == 'pull_request' && github.event.pull_request.head.sha || github.sha }}",
            validation,
        )
        self.assertIn("          fetch-depth: 0\n", validation)

        candidate_identity_test = TARGETED_VALIDATION_TEST_PATH.read_text(encoding="utf-8")
        self.assertIn('["git", "rev-parse", "HEAD^"]', candidate_identity_test)
        self.assertIn("git_candidate_identity(base, head)", candidate_identity_test)

        conservation = CONSERVATION_PATH.read_text(encoding="utf-8")
        self.assertIn("temporary", conservation)
        self.assertIn("machine-readable", conservation)
        self.assertIn("historical", conservation.casefold())


if __name__ == "__main__":
    unittest.main()
