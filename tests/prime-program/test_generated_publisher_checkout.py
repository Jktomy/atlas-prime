from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PUBLISHER_PATH = ROOT / ".github/workflows/generated-checkpoint-publisher.yml"
PR_VALIDATION_PATH = ROOT / ".github/workflows/prime-readonly-validation.yml"
TARGETED_VALIDATION_TEST_PATH = ROOT / "tests/prime-program/test_targeted_validation.py"
CONSERVATION_PATH = ROOT / "governance/deterministic-conservation-contract.md"


class GeneratedPublisherCheckoutTests(unittest.TestCase):
    def test_publisher_stops_at_draft_readback_and_pr_validation_owns_exact_head(self) -> None:
        publisher = PUBLISHER_PATH.read_text(encoding="utf-8")
        self.assertNotIn("\n  validate_exact_head:\n", publisher)
        self.assertNotIn("Validate generated exact head", publisher)
        self.assertNotIn("needs.publish.outputs.head_sha", publisher)
        self.assertIn("Bind exact generated draft readback", publisher)
        self.assertIn("if ($headSha -notmatch '^[0-9a-f]{40}$')", publisher)
        self.assertIn(
            "DRAFT_CREATED; required pull-request validation pending",
            publisher,
        )

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
        self.assertIn("single authoritative", conservation)
        self.assertIn("candidate-validation layer", conservation)
        self.assertIn("does not run a second exact-head Ubuntu/Windows validation matrix", conservation)


if __name__ == "__main__":
    unittest.main()
