from __future__ import annotations

import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

from tools.athena_routes.fresh_work_bridge import (
    FreshWorkBridgeError,
    execute_fresh_work,
)
from tools.athena_routes.hosted import sha256_bytes, stable_json


NOW = datetime(2026, 7, 14, 22, 0, 0, tzinfo=timezone.utc)
MAIN = "1" * 40
WORKFLOW_BLOB = "2" * 40
MISSION_ID = "RP-C01-CAP015-FRESH-WORK-R01"
TASK_SHA = "3" * 64
ORIGIN_NONCE_SHA = "4" * 64
EVIDENCE_SHA = "5" * 64


class FreshWorkBridgeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.carrier = self.root / "carrier.zip"
        self.carrier.write_bytes(b"immutable public-clean carrier")
        self.preview = self.root / "preview.json"
        self.origin = self.root / "origin.json"
        self.journey = self.root / "journey.json"
        self.guided = self.root / "guided.json"

        self.preview_value = {
            "canonical_main_sha": MAIN,
            "workflow_blob_sha": WORKFLOW_BLOB,
            "carrier_sha256": sha256_bytes(self.carrier.read_bytes()),
            "mission_id": MISSION_ID,
        }
        self.preview.write_text(
            stable_json(self.preview_value),
            encoding="utf-8",
            newline="\n",
        )
        self.preview_sha = sha256_bytes(self.preview.read_bytes())
        self.origin_value = {
            "schema_version": "atlas.athena.fresh-work-origin-receipt.v1",
            "issuer": "OPENAI_CHATGPT_WORK",
            "verification_method": "INDEPENDENT_PLATFORM_READBACK",
            "authorizer": "Jayson",
            "semantic_invoker": "Athena",
            "originating_surface": "CHATGPT_WORK",
            "task_identity_sha256": TASK_SHA,
            "issued_at": "2026-07-14T21:55:00Z",
            "expires_at": "2026-07-14T22:05:00Z",
            "origin_nonce_sha256": ORIGIN_NONCE_SHA,
            "mission_id": MISSION_ID,
            "base_sha": MAIN,
            "carrier_sha256": self.preview_value["carrier_sha256"],
            "preview_sha256": self.preview_sha,
            "workflow_blob_sha": WORKFLOW_BLOB,
            "verification_evidence_sha256": EVIDENCE_SHA,
            "public_clean": True,
            "forbidden_fields_absent": {
                "raw_task_identifier": True,
                "raw_conversation_identifier": True,
                "transcript": True,
                "prompt": True,
                "account_email": True,
                "credential": True,
                "local_path": True,
                "network_value": True,
                "private_data": True,
            },
        }
        self.write_origin()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def write_origin(self) -> None:
        self.origin.write_text(
            stable_json(self.origin_value),
            encoding="utf-8",
            newline="\n",
        )

    def verifier(self, receipt: dict) -> dict:
        return {
            "verified": True,
            "verification_method": receipt["verification_method"],
            "verification_evidence_sha256": receipt[
                "verification_evidence_sha256"
            ],
            "task_identity_sha256": receipt["task_identity_sha256"],
            "origin_nonce_sha256": receipt["origin_nonce_sha256"],
        }

    def execute(self, *, verifier=None):
        return execute_fresh_work(
            self.origin,
            self.preview,
            self.carrier,
            self.journey,
            self.guided,
            confirmed_preview_sha256=self.preview_sha,
            launch_nonce="fresh-work-launch-nonce-000001",
            public_clean_confirmation="PUBLIC_CLEAN_CONFIRMED",
            verifier=verifier,
            now=NOW,
        )

    def test_missing_trusted_verifier_blocks_before_guided_dispatch(self) -> None:
        with patch("tools.athena_routes.fresh_work_bridge.execute_preview") as guided:
            receipt = self.execute(verifier=None)
        guided.assert_not_called()
        self.assertEqual(receipt["result"], "BLOCKED")
        self.assertEqual(
            receipt["error_code"],
            "TRUSTED_ORIGIN_VERIFIER_UNAVAILABLE",
        )
        self.assertFalse(receipt["remote_dispatch_possible"])
        self.assertTrue(
            all(value is False for value in receipt["bridge_mutation"].values())
        )

    def test_verified_origin_dispatches_existing_guided_route_and_binds_receipts(self) -> None:
        guided_value = {
            "result": "DISPATCHED",
            "error_code": None,
            "workflow_run_id": 12345,
            "workflow_run_url": (
                "https://github.com/Jktomy/atlas-prime/actions/runs/12345"
            ),
            "workflow_run_head_sha": MAIN,
        }

        def fake_execute(_preview, _carrier, receipt_path, **_kwargs):
            receipt_path.write_text(
                stable_json(guided_value),
                encoding="utf-8",
                newline="\n",
            )
            return guided_value

        with patch(
            "tools.athena_routes.fresh_work_bridge.execute_preview",
            side_effect=fake_execute,
        ) as guided:
            receipt = self.execute(verifier=self.verifier)

        guided.assert_called_once()
        self.assertEqual(receipt["result"], "DISPATCHED")
        self.assertEqual(receipt["mission_id"], MISSION_ID)
        self.assertEqual(receipt["task_identity_sha256"], TASK_SHA)
        self.assertEqual(receipt["workflow_run_id"], 12345)
        self.assertEqual(
            receipt["guided_execute_receipt_sha256"],
            sha256_bytes(self.guided.read_bytes()),
        )
        self.assertNotIn("transcript", json.dumps(receipt))
        self.assertTrue(
            all(value is False for value in receipt["forbidden_actions"].values())
        )

    def test_verifier_mismatch_blocks_without_dispatch(self) -> None:
        def mismatch(receipt: dict) -> dict:
            value = self.verifier(receipt)
            value["task_identity_sha256"] = "f" * 64
            return value

        with patch("tools.athena_routes.fresh_work_bridge.execute_preview") as guided:
            receipt = self.execute(verifier=mismatch)
        guided.assert_not_called()
        self.assertEqual(
            receipt["error_code"],
            "TRUSTED_ORIGIN_VERIFICATION_MISMATCH",
        )

    def test_expired_origin_blocks_without_dispatch(self) -> None:
        self.origin_value["issued_at"] = "2026-07-14T21:00:00Z"
        self.origin_value["expires_at"] = "2026-07-14T21:05:00Z"
        self.write_origin()
        with patch("tools.athena_routes.fresh_work_bridge.execute_preview") as guided:
            receipt = self.execute(verifier=self.verifier)
        guided.assert_not_called()
        self.assertEqual(receipt["error_code"], "FRESH_WORK_RECEIPT_STALE")

    def test_binding_mismatch_blocks_before_verification(self) -> None:
        self.origin_value["workflow_blob_sha"] = "f" * 40
        self.write_origin()
        with patch("tools.athena_routes.fresh_work_bridge.execute_preview") as guided:
            receipt = self.execute(verifier=self.verifier)
        guided.assert_not_called()
        self.assertEqual(receipt["error_code"], "FRESH_WORK_BINDING_MISMATCH")

    def test_guided_partial_is_preserved_without_retry(self) -> None:
        guided_value = {
            "result": "PARTIAL",
            "error_code": "DISPATCH_READBACK_FAILED",
            "workflow_run_id": None,
            "workflow_run_url": None,
            "workflow_run_head_sha": None,
        }

        def fake_execute(_preview, _carrier, receipt_path, **_kwargs):
            receipt_path.write_text(
                stable_json(guided_value),
                encoding="utf-8",
                newline="\n",
            )
            return guided_value

        with patch(
            "tools.athena_routes.fresh_work_bridge.execute_preview",
            side_effect=fake_execute,
        ):
            receipt = self.execute(verifier=self.verifier)
        self.assertEqual(receipt["result"], "PARTIAL")
        self.assertEqual(receipt["stop_point"], "PARTIAL_STATE_PRESERVED")
        self.assertEqual(receipt["rollback"], "PRESERVE_AND_REVIEW_NO_RETRY")
        self.assertTrue(receipt["remote_dispatch_possible"])

    def test_journey_receipt_is_no_clobber(self) -> None:
        self.journey.write_text("{}\n", encoding="utf-8")
        with self.assertRaises(FreshWorkBridgeError) as raised:
            self.execute(verifier=self.verifier)
        self.assertEqual(
            raised.exception.code,
            "FRESH_WORK_JOURNEY_RECEIPT_EXISTS",
        )

    def test_raw_origin_fields_are_rejected_by_closed_schema(self) -> None:
        self.origin_value["raw_task_identifier"] = "must-not-cross"
        self.write_origin()
        with self.assertRaises(FreshWorkBridgeError) as raised:
            self.execute(verifier=self.verifier)
        self.assertEqual(raised.exception.code, "FRESH_WORK_RECEIPT_INVALID")
        self.assertFalse(self.journey.exists())


if __name__ == "__main__":
    unittest.main()
