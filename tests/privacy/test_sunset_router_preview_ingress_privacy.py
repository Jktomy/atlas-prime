from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tests.lifecycle.test_sunset_candidate import request
from tools.atlas_lifecycle.errors import LifecycleError
from tools.atlas_lifecycle.jsonio import canonical_bytes
from tools.atlas_lifecycle.repository import observed_head
from tools.sunset_router.issue_preview_ingress import (
    INTAKE_LANGUAGE,
    MAX_COMMENT_BYTES,
    admit_issue_comment,
)

ROOT = Path(__file__).resolve().parents[2]


def envelope(context_summary: str) -> dict:
    lifecycle = request("NON_QUEST")
    lifecycle["context_summary"] = context_summary
    return {
        "schema_id": "atlas.sunset-router.preview-intake",
        "schema_version": "1.0.0",
        "authority": "PREVIEW_ONLY",
        "command": "SUNSET_ROUTER_PREVIEW",
        "repository": "Jktomy/atlas-prime",
        "issue_number": 257,
        "expected_main_sha": observed_head(ROOT),
        "replay_nonce": "mission-257-stage3-privacy-test-r01",
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


def event(body: str) -> dict:
    return {
        "action": "created",
        "repository": {
            "full_name": "Jktomy/atlas-prime",
            "default_branch": "main",
            "owner": {"login": "Jktomy"},
        },
        "issue": {"number": 257},
        "comment": {
            "id": 257004,
            "body": body,
            "author_association": "OWNER",
            "user": {"login": "Jktomy"},
        },
        "sender": {"login": "Jktomy"},
    }


class SunsetRouterPreviewIngressPrivacyTests(unittest.TestCase):
    def write_json(self, path: Path, value: object) -> Path:
        path.write_bytes(canonical_bytes(value))
        return path

    def test_protected_looking_value_rejects_before_output(self) -> None:
        protected_value = "github" + "_pat_" + ("z" * 24)
        value = envelope(protected_value)
        payload = canonical_bytes(value).decode("utf-8").rstrip("\n")
        body = f"```{INTAKE_LANGUAGE}\n{payload}\n```\n"
        with tempfile.TemporaryDirectory() as temp:
            parent = Path(temp)
            with self.assertRaises(LifecycleError) as raised:
                admit_issue_comment(
                    ROOT,
                    self.write_json(parent / "event.json", event(body)),
                    self.write_json(parent / "comments.json", []),
                    parent / "request.json",
                    parent / "admission.json",
                )
            self.assertEqual(raised.exception.code, "PROTECTED_VALUE_REJECTED")
            self.assertFalse((parent / "request.json").exists())
            self.assertFalse((parent / "admission.json").exists())

    def test_oversized_comment_rejects_before_json_parse(self) -> None:
        body = "x" * (MAX_COMMENT_BYTES + 1)
        with tempfile.TemporaryDirectory() as temp:
            parent = Path(temp)
            with self.assertRaises(LifecycleError) as raised:
                admit_issue_comment(
                    ROOT,
                    self.write_json(parent / "event.json", event(body)),
                    self.write_json(parent / "comments.json", []),
                    parent / "request.json",
                    parent / "admission.json",
                )
            self.assertEqual(raised.exception.code, "SUNSET_PREVIEW_INTAKE_SIZE")
            self.assertFalse((parent / "request.json").exists())


if __name__ == "__main__":
    unittest.main()
