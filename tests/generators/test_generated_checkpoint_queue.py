from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tools.generated_checkpoint.queue import QueueError, classify_open_pull_requests, main


class GeneratedCheckpointQueueTests(unittest.TestCase):
    def entry(
        self,
        *,
        number: int = 192,
        draft: bool = True,
        head: str = "generated/checkpoint-rp-c08-test-0123456789ab",
        head_sha: str = "a" * 40,
        base: str = "main",
        title: str = "generated: deterministic checkpoint RP-C08-TEST",
    ) -> dict[str, object]:
        return {
            "number": number,
            "isDraft": draft,
            "headRefName": head,
            "headRefOid": head_sha,
            "baseRefName": base,
            "title": title,
        }

    def test_clear_queue_ignores_unrelated_open_prs(self) -> None:
        unrelated = self.entry(
            number=189,
            head="source/ordinary-repair",
            title="proof: ordinary repair",
        )
        result = classify_open_pull_requests([unrelated])
        self.assertEqual(result["result"], "CLEAR")
        self.assertEqual(result["open_checkpoint_count"], 0)
        self.assertIsNone(result["checkpoint"])
        self.assertFalse(result["mutation_authorized"])

    def test_one_open_generated_draft_defers_without_mutation(self) -> None:
        result = classify_open_pull_requests([self.entry()])
        self.assertEqual(result["result"], "DEFERRED_OPEN_CHECKPOINT")
        self.assertEqual(result["open_checkpoint_count"], 1)
        self.assertEqual(result["checkpoint"]["number"], 192)
        self.assertFalse(result["mutation_authorized"])

    def test_multiple_open_generated_drafts_fail_closed(self) -> None:
        with self.assertRaises(QueueError) as raised:
            classify_open_pull_requests(
                [
                    self.entry(),
                    self.entry(
                        number=193,
                        head_sha="b" * 40,
                        head="generated/checkpoint-rp-c08-other-abcdef012345",
                        title="generated: deterministic checkpoint RP-C08-OTHER",
                    ),
                ]
            )
        self.assertEqual(
            raised.exception.code,
            "GENERATED_CHECKPOINT_QUEUE_MULTIPLE_OPEN",
        )

    def test_inconsistent_or_unsafe_generated_identity_fails_closed(self) -> None:
        cases = [
            self.entry(title="ordinary title"),
            self.entry(head="source/not-generated"),
            self.entry(draft=False),
            self.entry(base="release"),
            self.entry(head_sha="not-a-sha"),
        ]
        for item in cases:
            with self.subTest(item=item):
                with self.assertRaises(QueueError):
                    classify_open_pull_requests([item])

    def test_cli_emits_canonical_deferred_receipt(self) -> None:
        with tempfile.TemporaryDirectory(prefix="generated-queue-") as raw:
            path = Path(raw) / "open-prs.json"
            path.write_text(json.dumps([self.entry()]), encoding="utf-8")
            self.assertEqual(main(["--pull-requests", str(path)]), 0)

    def test_workflow_defers_before_parity_and_rechecks_generated_only_pushes(self) -> None:
        workflow = (
            Path(__file__).resolve().parents[2]
            / ".github"
            / "workflows"
            / "generated-checkpoint-publisher.yml"
        ).read_text(encoding="utf-8")
        queue_block = workflow.split("\n  queue:\n", 1)[1].split("\n  parity:\n", 1)[0]
        parity_block = workflow.split("\n  parity:\n", 1)[1].split("\n  reconcile:\n", 1)[0]
        self.assertIn("pull-requests: read", queue_block)
        self.assertIn("tools.generated_checkpoint.queue", queue_block)
        self.assertIn('"queue_result=DEFERRED_OPEN_CHECKPOINT"', queue_block)
        self.assertNotIn("contents: write", queue_block)
        self.assertNotIn("pull-requests: write", queue_block)
        self.assertIn("needs: queue", parity_block)
        self.assertIn("needs.queue.outputs.queue_result == 'CLEAR'", parity_block)
        self.assertNotIn("paths-ignore:", workflow)
        self.assertNotIn('"generated/**"', workflow)
        self.assertNotIn("gh pr close", workflow)
        self.assertNotIn("gh pr merge", workflow)


if __name__ == "__main__":
    unittest.main()
