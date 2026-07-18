from __future__ import annotations

import unittest
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

from tools.generated_checkpoint.core import PreparationError
from tools.generated_checkpoint.hosted_prepare import bind_hosted_event


class InChatWorkflowBridgeTests(unittest.TestCase):
    def test_preserved_generated_profile_event_binding_remains_closed(self) -> None:
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

    def test_active_workflow_is_manual_read_only_and_has_no_push_trigger(self) -> None:
        workflow = (
            ROOT / ".github" / "workflows" / "generated-checkpoint-publisher.yml"
        ).read_text(encoding="utf-8")
        for phrase in (
            "name: Generated projection status",
            "workflow_dispatch:",
            "Check generated projection status",
            "Admit exact owner read-only request",
            "Build and compare deterministic projections",
            "tools/build_index.py",
            "--compare-dir generated",
            "Generated projections: CURRENT",
            "Generated projections: STALE",
            "contents: read",
            "ubuntu-latest",
        ):
            self.assertIn(phrase, workflow)

        for forbidden in (
            "\n  push:",
            "contents: write",
            "pull-requests: write",
            "production_adapter.cli",
            "--execute-draft-pr",
            "gh pr create",
            "automatic merge",
        ):
            self.assertNotIn(forbidden, workflow.casefold() if forbidden == "automatic merge" else workflow)

    def test_manual_status_workflow_requires_exact_main_and_owner(self) -> None:
        workflow = (
            ROOT / ".github" / "workflows" / "generated-checkpoint-publisher.yml"
        ).read_text(encoding="utf-8")
        for phrase in (
            'GITHUB_REPOSITORY -cne "Jktomy/atlas-prime"',
            "GITHUB_ACTOR -cne $env:GITHUB_REPOSITORY_OWNER",
            "GITHUB_TRIGGERING_ACTOR -cne $env:GITHUB_REPOSITORY_OWNER",
            'GITHUB_REF -cne "refs/heads/main"',
            "PUBLIC_CLEAN_CONFIRMED",
            "git/ref/heads/main",
            "Generated status base is stale",
            "persist-credentials: false",
        ):
            self.assertIn(phrase, workflow)

    def test_disabled_hosted_publisher_code_remains_fail_closed(self) -> None:
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

    def test_governance_records_disabled_first_hosted_publisher(self) -> None:
        governance = (
            ROOT / "governance" / "athena-execution-route-contract.md"
        ).read_text(encoding="utf-8")
        for phrase in (
            "Hosted generated publication is `DISABLED_FIRST`",
            "no `push` trigger",
            "ordinary bounded local source transaction",
            "reviewed draft PR",
            "does not erase the historical AJ-09",
            "must not be interpreted as current automatic operation",
        ):
            self.assertIn(phrase, governance)


if __name__ == "__main__":
    unittest.main()
