from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tests.lifecycle.test_sunset_candidate import request
from tools.atlas_lifecycle.errors import LifecycleError
from tools.atlas_lifecycle.jsonio import canonical_bytes
from tools.atlas_lifecycle.repository import observed_head
from tools.sunset_router.core import generate_router_preview
from tools.sunset_router.issue_preview_ingress import (
    BINDING_LANGUAGE,
    INTAKE_LANGUAGE,
    RESULT_MARKER,
    admit_issue_comment,
    render_preview_comment,
)

ROOT = Path(__file__).resolve().parents[2]


def router_request() -> dict:
    return {
        "schema_id": "atlas.sunset-router.request",
        "schema_version": "1.0.0",
        "authority": "PUBLIC_CLEAN_REQUEST",
        "actor": "ATHENA",
        "requested_route": "ATHENA_SPEAR_THREAD_ENGINE",
        "operator_transfer_authorized": False,
        "lifecycle_request": request("NON_QUEST"),
    }


def envelope() -> dict:
    return {
        "schema_id": "atlas.sunset-router.preview-intake",
        "schema_version": "1.0.0",
        "authority": "PREVIEW_ONLY",
        "command": "SUNSET_ROUTER_PREVIEW",
        "repository": "Jktomy/atlas-prime",
        "issue_number": 257,
        "expected_main_sha": observed_head(ROOT),
        "replay_nonce": "mission-257-stage3-preview-test-r01",
        "public_clean_confirmation": "PUBLIC_CLEAN_CONFIRMED",
        "router_request": router_request(),
    }


def comment_body(value: dict) -> str:
    payload = canonical_bytes(value).decode("utf-8").rstrip("\n")
    return f"```{INTAKE_LANGUAGE}\n{payload}\n```\n"


def event(value: dict, *, login: str = "Jktomy", association: str = "OWNER") -> dict:
    return {
        "action": "created",
        "repository": {
            "full_name": "Jktomy/atlas-prime",
            "default_branch": "main",
            "owner": {"login": "Jktomy"},
        },
        "issue": {"number": 257},
        "comment": {
            "id": 257003,
            "body": comment_body(value),
            "author_association": association,
            "user": {"login": login},
        },
        "sender": {"login": login},
    }


class SunsetRouterPreviewIngressTests(unittest.TestCase):
    def write_json(self, path: Path, value: object) -> Path:
        path.write_bytes(canonical_bytes(value))
        return path

    def admit(
        self,
        parent: Path,
        value: dict | None = None,
        *,
        comments: list[dict] | None = None,
        login: str = "Jktomy",
        association: str = "OWNER",
        prefix: str = "first",
    ) -> tuple[dict, Path, Path]:
        request_output = parent / f"{prefix}-request.json"
        admission_output = parent / f"{prefix}-admission.json"
        result = admit_issue_comment(
            ROOT,
            self.write_json(
                parent / f"{prefix}-event.json",
                event(value or envelope(), login=login, association=association),
            ),
            self.write_json(parent / f"{prefix}-comments.json", comments or []),
            request_output,
            admission_output,
        )
        return result, request_output, admission_output

    def test_owner_event_generates_exact_temporary_preview_comment(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            parent = Path(temp)
            admission, request_path, admission_path = self.admit(parent)
            router_dir = parent / "router-preview"
            generate_router_preview(ROOT, request_path, router_dir)
            output = parent / "result.md"
            result = render_preview_comment(ROOT, router_dir, admission_path, output)

            body = output.read_text(encoding="utf-8")
            self.assertEqual(result["status"], "PASS")
            self.assertEqual(admission["authority"], "PREVIEW_ONLY_ADMISSION")
            self.assertFalse(admission["mutation_authorized"])
            self.assertIn(RESULT_MARKER, body)
            self.assertIn("```atlas-sunset-preview-v1", body)
            self.assertIn("```atlas-sunset-router-receipt-v1", body)
            self.assertIn(f"```{BINDING_LANGUAGE}", body)
            self.assertIn("WITH GODDESS MODE AND SHARDBLADE", body)
            self.assertIn("creates no branch or PR", body)
            self.assertFalse((ROOT / "sunset-router-preview").exists())

    def test_non_owner_event_rejects_before_output(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            parent = Path(temp)
            with self.assertRaises(LifecycleError) as raised:
                self.admit(parent, login="not-owner", association="NONE")
            self.assertEqual(raised.exception.code, "SUNSET_PREVIEW_OWNER_IDENTITY")
            self.assertFalse((parent / "first-request.json").exists())

    def test_stale_base_rejects_before_output(self) -> None:
        value = envelope()
        stale = "0" * 40
        if stale == observed_head(ROOT):
            stale = "f" * 40
        value["expected_main_sha"] = stale
        value["router_request"]["lifecycle_request"]["expected_main_sha"] = stale
        with tempfile.TemporaryDirectory() as temp:
            parent = Path(temp)
            with self.assertRaises(LifecycleError) as raised:
                self.admit(parent, value)
            self.assertEqual(raised.exception.code, "STALE_STATE")
            self.assertFalse((parent / "first-request.json").exists())

    def test_non_spear_route_rejects_before_output(self) -> None:
        value = envelope()
        value["router_request"]["requested_route"] = "AUTO"
        with tempfile.TemporaryDirectory() as temp:
            parent = Path(temp)
            with self.assertRaises(LifecycleError) as raised:
                self.admit(parent, value)
            self.assertEqual(raised.exception.code, "SUNSET_PREVIEW_ROUTE_IDENTITY")
            self.assertFalse((parent / "first-request.json").exists())

    def test_exact_replay_receipt_rejects(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            parent = Path(temp)
            first, _, _ = self.admit(parent)
            binding = {
                "replay_id": first["replay_id"],
            }
            binding_json = canonical_bytes(binding).decode("utf-8").rstrip("\n")
            prior = {
                "id": 9001,
                "user": {"login": "github-actions[bot]"},
                "body": (
                    f"{RESULT_MARKER}\n"
                    f"```{BINDING_LANGUAGE}\n{binding_json}\n```\n"
                ),
            }
            with self.assertRaises(LifecycleError) as raised:
                self.admit(parent, comments=[prior], prefix="replay")
            self.assertEqual(raised.exception.code, "REPLAY")
            self.assertFalse((parent / "replay-request.json").exists())

    def test_comment_must_be_one_canonical_block(self) -> None:
        value = envelope()
        payload = canonical_bytes(value).decode("utf-8").rstrip("\n")
        bad_event = event(value)
        bad_event["comment"]["body"] = f"extra\n```{INTAKE_LANGUAGE}\n{payload}\n```\n"
        with tempfile.TemporaryDirectory() as temp:
            parent = Path(temp)
            with self.assertRaises(LifecycleError) as raised:
                admit_issue_comment(
                    ROOT,
                    self.write_json(parent / "event.json", bad_event),
                    self.write_json(parent / "comments.json", []),
                    parent / "request.json",
                    parent / "admission.json",
                )
            self.assertEqual(raised.exception.code, "SUNSET_PREVIEW_INTAKE_FORMAT")


if __name__ == "__main__":
    unittest.main()
