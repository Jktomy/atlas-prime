from __future__ import annotations

import unittest
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

from tools.generated_checkpoint.core import PreparationError
from tools.generated_checkpoint.hosted_prepare import bind_hosted_event


class InChatWorkflowBridgeTests(unittest.TestCase):
    def test_hosted_event_binding_is_closed_and_rehashes_mission(self) -> None:
        original = {
            "mission_id": "RP-C08-GENERATED-AUTO-1-1",
            "mission_sha256": "0" * 64,
            "generated_checkpoint_profile": {"event_name": "workflow_dispatch"},
        }
        for event_name in ("push", "workflow_dispatch"):
            mission = bind_hosted_event(deepcopy(original), event_name)
            self.assertEqual(
                mission["generated_checkpoint_profile"]["event_name"],
                event_name,
            )
            self.assertRegex(mission["mission_sha256"], r"^[0-9a-f]{64}$")
            self.assertNotEqual(mission["mission_sha256"], "0" * 64)

        with self.assertRaises(PreparationError) as raised:
            bind_hosted_event(deepcopy(original), "schedule")
        self.assertEqual(raised.exception.code, "GENERATED_CHECKPOINT_EVENT")

    def test_publisher_is_explicit_manual_only_and_retains_full_safe_route(self) -> None:
        workflow = (
            ROOT / ".github" / "workflows" / "generated-checkpoint-publisher.yml"
        ).read_text(encoding="utf-8")
        for phrase in (
            "workflow_dispatch:",
            "Admit exact publisher invocation",
            'expectedRepository = "Jktomy/atlas-prime"',
            'expectedOwner = "Jktomy"',
            "git/ref/heads/main",
            "github.actor == github.repository_owner",
            "github.triggering_actor == github.repository_owner",
            "tools.generated_checkpoint.hosted_prepare",
            "Bind exact generated draft readback",
            "DRAFT_CREATED; required pull-request validation pending",
            "ubuntu-latest",
            "windows-latest",
        ):
            self.assertIn(phrase, workflow)

        self.assertNotIn("\n  push:", workflow)
        self.assertNotIn("paths-ignore:", workflow)
        self.assertNotIn('"generated/**"', workflow)
        self.assertNotIn("actions: write", workflow)
        self.assertNotIn("automatic merge", workflow.casefold())
        self.assertNotIn("gh workflow run", workflow)
        self.assertNotIn("\n  validate_exact_head:\n", workflow)
        self.assertNotIn("Validate generated exact head", workflow)
        self.assertNotIn("needs.publish.outputs.head_sha", workflow)
        for duplicate_step in (
            "Prime kernel checks",
            "Prime repository policy tests",
            "Prime privacy boundary tests",
            "Prime lifecycle contract tests",
            "Full Prime Thread Engine tests",
            "Prime whole-program tests",
            "Athena execution route tests",
            "Prime source validation",
            "Prove active PowerShell launcher resolution",
        ):
            self.assertNotIn(duplicate_step, workflow)

    def test_publisher_defers_cleanly_while_one_generated_draft_is_open(self) -> None:
        workflow = (
            ROOT / ".github" / "workflows" / "generated-checkpoint-publisher.yml"
        ).read_text(encoding="utf-8")
        queue_block = workflow.split("\n  queue:\n", 1)[1].split("\n  parity:\n", 1)[0]
        parity_block = workflow.split("\n  parity:\n", 1)[1].split("\n  reconcile:\n", 1)[0]
        self.assertIn("Inspect generated checkpoint queue", queue_block)
        self.assertIn("pull-requests: read", queue_block)
        self.assertIn("tools.generated_checkpoint.queue", queue_block)
        self.assertIn("DEFERRED_OPEN_CHECKPOINT", queue_block)
        self.assertIn("No mutation attempted", queue_block)
        self.assertIn("--limit 1001", queue_block)
        self.assertIn("receipt_sha256", queue_block)
        self.assertNotIn("contents: write", queue_block)
        self.assertNotIn("pull-requests: write", queue_block)
        self.assertIn("needs: queue", parity_block)
        self.assertIn("needs.queue.outputs.queue_result == 'CLEAR'", parity_block)

        reconcile_block = workflow.split("\n  reconcile:\n", 1)[1].split("\n  prepare:\n", 1)[0]
        prepare_block = workflow.split("\n  prepare:\n", 1)[1].split("\n  publish:\n", 1)[0]
        publish_block = workflow.split("\n  publish:\n", 1)[1]
        self.assertIn("needs: parity", reconcile_block)
        self.assertIn("needs: reconcile", prepare_block)
        self.assertIn("- prepare", publish_block)
        self.assertIn("Bind exact generated draft readback", publish_block)
        for block in (parity_block, reconcile_block, prepare_block, publish_block):
            job_preamble = block.split("\n    steps:\n", 1)[0]
            self.assertNotIn("always()", job_preamble)
            self.assertNotIn("continue-on-error", block)

    def test_push_identity_is_deterministic_and_public_clean_by_construction(self) -> None:
        workflow = (
            ROOT / ".github" / "workflows" / "generated-checkpoint-publisher.yml"
        ).read_text(encoding="utf-8")
        self.assertIn("RP-C08-GENERATED-AUTO-{0}-{1}", workflow)
        self.assertIn("generated-checkpoint-auto-{0}-{1}", workflow)
        self.assertIn("'PUBLIC_CLEAN_CONFIRMED'", workflow)
        self.assertIn("GENERATED_BASE_SHA", workflow)
        self.assertIn("GENERATED_REPLAY_NONCE", workflow)
        self.assertNotIn("--github-event", workflow)

    def test_generated_profile_accepts_only_push_or_manual_dispatch(self) -> None:
        source = (
            ROOT
            / "tools"
            / "thread-engine"
            / "production_adapter"
            / "generated_checkpoint.py"
        ).read_text(encoding="utf-8")
        self.assertIn(
            'ALLOWED_EVENT_NAMES = frozenset({"push", "workflow_dispatch"})',
            source,
        )
        self.assertIn(
            'profile.get("event_name") not in ALLOWED_EVENT_NAMES',
            source,
        )
        self.assertIn(
            '"GITHUB_EVENT_NAME": profile["event_name"]',
            source,
        )

    def test_generated_queue_governance_defines_coalescing_and_manual_recovery(self) -> None:
        governance = (
            ROOT / "governance" / "athena-execution-route-contract.md"
        ).read_text(encoding="utf-8")
        for phrase in (
            "1,001-entry sentinel",
            "DEFERRED_OPEN_CHECKPOINT",
            "overall GREEN workflow outcome",
            "older serialized event",
            "`CLEAR` decision with event-base drift fails closed before parity",
            "Canonical `main` pushes do not launch",
            "explicit later dispatch",
            "recomputes all five projections",
            "one full five-file mission",
            "Closing a generated draft without merge",
            "explicit owner `workflow_dispatch`",
            "There is no push, pull-request-close, or schedule trigger",
            "singular Thread Engine retains",
            "No generated queue component may become a second repository writer",
        ):
            self.assertIn(phrase, governance)


if __name__ == "__main__":
    unittest.main()
