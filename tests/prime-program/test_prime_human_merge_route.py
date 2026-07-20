from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def source(relative: str) -> str:
    return " ".join((ROOT / relative).read_text(encoding="utf-8").split())


class PrimeHumanMergeRouteTests(unittest.TestCase):
    def test_direct_request_builds_through_ready_but_never_merges(self) -> None:
        bootstrap = source("bootstrap.md")
        self.assertIn("one bounded transaction through an unchanged merge-ready PR", bootstrap)
        self.assertIn("Preview-only, draft-only, or narrower", bootstrap)
        self.assertIn("candidate-caused repair", bootstrap)
        self.assertIn("actionable review repair", bootstrap)
        self.assertIn("exact-head Strikeforce", bootstrap)
        self.assertIn("ready-for-review transition", bootstrap)
        self.assertIn("Prime PR #___ is ready to merge.", bootstrap)
        self.assertIn("Jayson alone makes the candidate permanent", bootstrap)

    def test_manual_github_merge_is_the_only_normal_permanence_action(self) -> None:
        for relative in (
            "routing/command-surfaces.md",
            "safety/atlas-safety-doctrine.md",
            "governance/change-routes.md",
            "governance/shard-doctrine.md",
            "governance/source-lifecycle.md",
        ):
            with self.subTest(relative=relative):
                text = source(relative)
                self.assertIn("manually click", text)
                self.assertIn("GitHub", text)

        safety = source("safety/atlas-safety-doctrine.md")
        self.assertIn("No assistant, model, tool, workflow, or automated route merges", safety)

    def test_changed_bytes_after_ready_restart_the_exact_head_gate(self) -> None:
        for relative in (
            "safety/atlas-safety-doctrine.md",
            "governance/change-routes.md",
            "governance/shard-doctrine.md",
            "governance/source-lifecycle.md",
        ):
            with self.subTest(relative=relative):
                text = source(relative).lower()
                self.assertIn("after ready", text)
                self.assertIn("draft", text)
                self.assertIn("replacement exact head", text)

    def test_machine_shardblade_remains_separate_and_inactive(self) -> None:
        change_routes = source("governance/change-routes.md")
        shard = source("governance/shard-doctrine.md")
        self.assertIn("Machine permanence boundary", change_routes)
        self.assertIn("does not activate or invoke it", change_routes)
        self.assertIn("The normal Prime route does not invoke Shardblade", shard)
        self.assertIn("does not change `CONTRACT_ONLY_NOT_ACTIVATED`", shard)


if __name__ == "__main__":
    unittest.main()
