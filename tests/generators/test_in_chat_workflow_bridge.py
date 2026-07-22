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

    def test_hosted_publisher_entrypoint_is_retired(self) -> None:
        self.assertFalse(
            (ROOT / ".github" / "workflows" / "generated-checkpoint-publisher.yml").exists()
        )

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

    def test_governance_refracts_routine_publication_into_diagnostics(self) -> None:
        governance = (
            ROOT / "governance" / "athena-execution-route-contract.md"
        ).read_text(encoding="utf-8")
        for phrase in (
            "temporary storage",
            "machine-readable",
            "no generated-only follow-up",
            "historical proof",
        ):
            self.assertIn(phrase, governance)


if __name__ == "__main__":
    unittest.main()
