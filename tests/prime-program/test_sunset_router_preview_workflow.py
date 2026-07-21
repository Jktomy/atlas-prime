from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tests.lifecycle.test_sunset_candidate import request
from tools.atlas_lifecycle.jsonio import canonical_bytes
from tools.atlas_lifecycle.repository import observed_head
from tools.atlas_lifecycle.schema import SchemaValidator
from tools.sunset_router.core import generate_router_preview
from tools.sunset_router.issue_preview_ingress import (
    INTAKE_LANGUAGE,
    admit_issue_comment,
    render_preview_comment,
)

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github/workflows/sunset-router-preview-intake.yml"


def intake() -> dict:
    lifecycle = request("NON_QUEST")
    lifecycle["campaign"] = "CAMPAIGN-CODEX-OPEN-PATHWAYS-SUNSET-R01"
    lifecycle["mission"] = "Mission #257 Stage 3 live Preview acceptance"
    lifecycle["gate"] = "STAGE_3_EXACT_PREVIEW_APPROVAL"
    return {
        "schema_id": "atlas.sunset-router.preview-intake",
        "schema_version": "1.0.0",
        "authority": "PREVIEW_ONLY",
        "command": "SUNSET_ROUTER_PREVIEW",
        "repository": "Jktomy/atlas-prime",
        "issue_number": 257,
        "expected_main_sha": observed_head(ROOT),
        "replay_nonce": "mission-257-stage3-prime-program-r01",
        "public_clean_confirmation": "PUBLIC_CLEAN_CONFIRMED",
        "router_request": {
            "schema_id": "atlas.sunset-router.request",
            "schema_version": "1.0.0",
            "authority": "PUBLIC_CLEAN_REQUEST",
            "actor": "ATHENA",
            "requested_route": "ATHENA_SPEAR_THREAD_ENGINE",
            "operator_transfer_authorized": False,
            "lifecycle_request": lifecycle,
        },
    }


def event(value: dict) -> dict:
    payload = canonical_bytes(value).decode("utf-8").rstrip("\n")
    return {
        "action": "created",
        "repository": {
            "full_name": "Jktomy/atlas-prime",
            "default_branch": "main",
            "owner": {"login": "Jktomy"},
        },
        "issue": {"number": 257},
        "comment": {
            "id": 257005,
            "body": f"```{INTAKE_LANGUAGE}\n{payload}\n```\n",
            "author_association": "OWNER",
            "user": {"login": "Jktomy"},
        },
        "sender": {"login": "Jktomy"},
    }


class SunsetRouterPreviewWorkflowTests(unittest.TestCase):
    def write(self, path: Path, value: object) -> Path:
        path.write_bytes(canonical_bytes(value))
        return path

    def test_intake_schema_is_trusted_and_closed(self) -> None:
        value = intake()
        SchemaValidator(ROOT / "lifecycle/schemas").validate_sunset_router_preview_intake(value)
        schema = json.loads(
            (ROOT / "lifecycle/schemas/sunset-router-preview-intake-v1.schema.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertFalse(schema["additionalProperties"])
        self.assertEqual(set(value), set(schema["required"]))

    def test_exact_workflow_route_produces_approval_bound_preview(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            parent = Path(temp)
            request_path = parent / "request.json"
            admission_path = parent / "admission.json"
            admission = admit_issue_comment(
                ROOT,
                self.write(parent / "event.json", event(intake())),
                self.write(parent / "comments.json", []),
                request_path,
                admission_path,
            )
            router_dir = parent / "router"
            result = generate_router_preview(ROOT, request_path, router_dir)
            output = parent / "comment.md"
            rendered = render_preview_comment(ROOT, router_dir, admission_path, output)
            body = output.read_text(encoding="utf-8")

            self.assertEqual(result["authority"], "PREVIEW_ONLY")
            self.assertEqual(result["selected_route"], "ATHENA_SPEAR_THREAD_ENGINE")
            self.assertEqual(
                result["fallback_routes"],
                ["ATHENA_PHOENIX_BLADE", "ATHENA_AEGIS_BREAK"],
            )
            self.assertEqual(rendered["replay_id"], admission["replay_id"])
            self.assertIn(rendered["preview_digest"], body)
            self.assertIn(rendered["semantic_digest"], body)
            self.assertIn(rendered["router_receipt_digest"], body)
            self.assertIn("APPROVE SUNSET PREVIEW", body)
            self.assertIn("WITH GODDESS MODE AND SHARDBLADE", body)

    def test_workflow_has_no_source_or_permanence_step(self) -> None:
        workflow = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("Generate exact Sunset Router Preview", workflow)
        self.assertIn("Return exact Preview to Mission 257", workflow)
        for forbidden in (
            "contents: write",
            "pull-requests: write",
            "create_pull_request",
            "mark_pull_request_ready_for_review",
            "merge_pull_request",
            "SUNSET COMPLETE",
        ):
            self.assertNotIn(forbidden, workflow)


if __name__ == "__main__":
    unittest.main()
