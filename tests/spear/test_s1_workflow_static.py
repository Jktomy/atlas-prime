from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github/workflows/spear-s1-draft-pr-writer.yml"


class S1WorkflowStaticTests(unittest.TestCase):
    def setUp(self) -> None:
        self.text = WORKFLOW.read_text(encoding="utf-8")

    def test_workflow_is_manual_only_and_concurrency_is_repository_plus_packet_id(self) -> None:
        self.assertIn("workflow_dispatch:", self.text)
        self.assertIn("group: spear-s1-${{ github.repository }}-${{ inputs.packet_id }}", self.text)
        self.assertIn("cancel-in-progress: false", self.text)
        self.assertNotIn("pull_request:", self.text)
        self.assertNotIn("push:", self.text)
        self.assertNotIn("schedule:", self.text)

    def test_defaults_are_read_only_and_apply_is_source_hard_disabled(self) -> None:
        self.assertIn("permissions:\n  contents: read\n  pull-requests: read", self.text)
        self.assertIn("if: ${{ false }}", self.text)
        self.assertIn("contents: write", self.text)
        self.assertIn("pull-requests: write", self.text)
        self.assertIn("S1_APPLY_HARD_DISABLED", self.text)

    def test_no_dependency_install_and_all_actions_are_sha_pinned(self) -> None:
        lowered = self.text.lower()
        self.assertNotIn("pip install", lowered)
        self.assertNotIn("npm install", lowered)
        uses = re.findall(r"(?m)^\s*uses:\s*([^\s]+)\s*$", self.text)
        self.assertEqual(uses, ["actions/upload-artifact@65462800fd760344b1a7b4382951275a0abb4808"])

    def test_blocked_receipt_records_known_authenticated_context(self) -> None:
        for variable in [
            "SPEAR_ACTOR: ${{ github.actor }}",
            "SPEAR_EVENT: ${{ github.event_name }}",
            "SPEAR_WORKFLOW_SHA: ${{ github.workflow_sha }}",
            "SPEAR_REPOSITORY: ${{ github.repository }}",
            "SPEAR_PACKET_ID: ${{ inputs.packet_id }}",
        ]:
            self.assertIn(variable, self.text)
        self.assertIn('"actor": os.environ["SPEAR_ACTOR"]', self.text)
        self.assertIn('"packet_id": os.environ["SPEAR_PACKET_ID"]', self.text)
        self.assertNotIn('"actor":null', self.text)
        self.assertNotIn('"workflow_sha":null', self.text)

    def test_failure_artifact_upload_is_unconditional(self) -> None:
        self.assertIn("if: always()", self.text)
        self.assertIn("DEPENDENCY_ROUTE_BLOCKED", self.text)
        self.assertIn("if-no-files-found: error", self.text)


if __name__ == "__main__":
    unittest.main()
