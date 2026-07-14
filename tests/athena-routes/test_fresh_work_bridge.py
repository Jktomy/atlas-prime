from __future__ import annotations

import ast
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from tools.athena_routes.fresh_work_bridge import (
    FreshWorkBridgeError,
    build_unavailable_receipt,
    build_verified_dispatch_plan,
)
from tools.athena_routes.hosted import sha256_bytes, stable_json


ROOT = Path(__file__).resolve().parents[2]
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
        self.preview_value = {
            "canonical_main_sha": MAIN,
            "workflow_blob_sha": WORKFLOW_BLOB,
            "carrier_sha256": sha256_bytes(self.carrier.read_bytes()),
            "mission_id": MISSION_ID,
        }
        self.preview.write_text(stable_json(self.preview_value), encoding="utf-8", newline="\n")
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
        self.origin.write_text(stable_json(self.origin_value), encoding="utf-8", newline="\n")

    def readback(self, receipt: dict, origin_sha: str) -> dict:
        return {
            "verified": True,
            "origin_receipt_sha256": origin_sha,
            "verification_method": receipt["verification_method"],
            "verification_evidence_sha256": receipt["verification_evidence_sha256"],
            "task_identity_sha256": receipt["task_identity_sha256"],
            "origin_nonce_sha256": receipt["origin_nonce_sha256"],
            "mission_id": receipt["mission_id"],
            "base_sha": receipt["base_sha"],
            "carrier_sha256": receipt["carrier_sha256"],
            "preview_sha256": receipt["preview_sha256"],
            "workflow_blob_sha": receipt["workflow_blob_sha"],
        }

    def plan(self, *, readback=None):
        return build_verified_dispatch_plan(
            self.origin,
            self.preview,
            self.carrier,
            confirmed_preview_sha256=self.preview_sha,
            readback=readback,
            now=NOW,
        )

    def test_current_cli_boundary_records_no_verifier_without_dispatch(self) -> None:
        receipt = build_unavailable_receipt(
            self.origin,
            self.preview,
            self.carrier,
            self.journey,
            confirmed_preview_sha256=self.preview_sha,
            now=NOW,
        )
        self.assertEqual(receipt["result"], "BLOCKED")
        self.assertEqual(receipt["error_code"], "TRUSTED_ORIGIN_VERIFIER_UNAVAILABLE")
        self.assertFalse(receipt["remote_dispatch_possible"])
        self.assertTrue(all(value is False for value in receipt["bridge_mutation"].values()))
        self.assertIsNone(receipt["workflow_run_id"])
        self.assertIsNone(receipt["guided_execute_receipt_sha256"])

    def test_verified_origin_builds_only_read_only_candidate(self) -> None:
        plan = self.plan(readback=self.readback)
        self.assertEqual(plan["state"], "READ_ONLY_CANDIDATE_NOT_EXECUTABLE")
        self.assertEqual(plan["mission_id"], MISSION_ID)
        self.assertEqual(plan["task_identity_sha256"], TASK_SHA)
        self.assertFalse(plan["remote_dispatch_authority"])
        self.assertFalse(plan["guided_execute_invoked"])
        self.assertTrue(all(value is False for value in plan["forbidden_actions"].values()))
        self.assertNotIn("workflow_run_id", plan)
        self.assertNotIn("transcript", json.dumps(plan))

    def test_missing_readback_cannot_build_candidate(self) -> None:
        with self.assertRaises(FreshWorkBridgeError) as raised:
            self.plan(readback=None)
        self.assertEqual(raised.exception.code, "TRUSTED_ORIGIN_VERIFIER_UNAVAILABLE")

    def test_readback_must_bind_every_origin_and_mission_field(self) -> None:
        def mismatch(receipt: dict, origin_sha: str) -> dict:
            value = self.readback(receipt, origin_sha)
            value["base_sha"] = "f" * 40
            return value

        with self.assertRaises(FreshWorkBridgeError) as raised:
            self.plan(readback=mismatch)
        self.assertEqual(raised.exception.code, "TRUSTED_ORIGIN_VERIFICATION_MISMATCH")

        def incomplete(receipt: dict, origin_sha: str) -> dict:
            value = self.readback(receipt, origin_sha)
            value.pop("workflow_blob_sha")
            return value

        with self.assertRaises(FreshWorkBridgeError) as raised:
            self.plan(readback=incomplete)
        self.assertEqual(raised.exception.code, "TRUSTED_ORIGIN_VERIFICATION_FAILED")

    def test_expired_origin_cannot_build_candidate(self) -> None:
        self.origin_value["issued_at"] = "2026-07-14T21:00:00Z"
        self.origin_value["expires_at"] = "2026-07-14T21:05:00Z"
        self.write_origin()
        with self.assertRaises(FreshWorkBridgeError) as raised:
            self.plan(readback=self.readback)
        self.assertEqual(raised.exception.code, "FRESH_WORK_RECEIPT_STALE")

    def test_binding_mismatch_stops_before_origin_readback(self) -> None:
        self.origin_value["workflow_blob_sha"] = "f" * 40
        self.write_origin()
        called = False

        def should_not_run(_receipt: dict, _origin_sha: str) -> dict:
            nonlocal called
            called = True
            return {}

        with self.assertRaises(FreshWorkBridgeError) as raised:
            self.plan(readback=should_not_run)
        self.assertEqual(raised.exception.code, "FRESH_WORK_BINDING_MISMATCH")
        self.assertFalse(called)

    def test_journey_receipt_is_no_clobber(self) -> None:
        self.journey.write_text("{}\n", encoding="utf-8")
        with self.assertRaises(FreshWorkBridgeError) as raised:
            build_unavailable_receipt(
                self.origin,
                self.preview,
                self.carrier,
                self.journey,
                confirmed_preview_sha256=self.preview_sha,
                now=NOW,
            )
        self.assertEqual(raised.exception.code, "FRESH_WORK_JOURNEY_RECEIPT_EXISTS")

    def test_raw_origin_fields_are_rejected_by_closed_schema(self) -> None:
        self.origin_value["raw_task_identifier"] = "must-not-cross"
        self.write_origin()
        with self.assertRaises(FreshWorkBridgeError) as raised:
            self.plan(readback=self.readback)
        self.assertEqual(raised.exception.code, "FRESH_WORK_RECEIPT_INVALID")


class FreshWorkBridgeSourceTests(unittest.TestCase):
    def test_historical_surface_is_retained_but_quarantined(self) -> None:
        required = (
            "governance/athena-fresh-work-origin-contract.md",
            "schemas/athena-fresh-work-origin-receipt-v1.schema.json",
            "schemas/athena-fresh-work-journey-receipt-v1.schema.json",
            "tools/athena_routes/fresh_work_bridge.py",
        )
        for relative in required:
            self.assertTrue((ROOT / relative).is_file())

        contract = (ROOT / required[0]).read_text(encoding="utf-8")
        readme = (ROOT / "tools/athena_routes/README.md").read_text(encoding="utf-8")
        routing = (ROOT / "routing/command-surfaces.md").read_text(encoding="utf-8")
        self.assertIn('status: "SUPERSEDED_HISTORICAL_CONSTRUCTION"', contract)
        self.assertIn("superseded false blocker", contract.lower())
        self.assertIn("retained as inert historical construction evidence", readme)
        self.assertIn("Historical fresh-origin construction", routing)
        self.assertIn("never required", routing)

    def test_cap015_is_restored_without_activating_bridge(self) -> None:
        register = json.loads(
            (ROOT / "governance/capability-parity-register.json").read_text(encoding="utf-8")
        )
        cap015 = next(item for item in register["capabilities"] if item["id"] == "CAP-015")
        self.assertEqual(cap015["capability_disposition"], "RESTORED")
        self.assertEqual(cap015["activation_state"], "ACTIVE")
        self.assertIn("direct Spear", cap015["current_state"])
        contract = (ROOT / "governance/athena-fresh-work-origin-contract.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("has no guided Execute import", contract)
        self.assertIn("must not be selected by automatic routing", contract)

    def test_source_has_no_dispatch_writer_or_dynamic_trust_loader(self) -> None:
        source = (ROOT / "tools/athena_routes/fresh_work_bridge.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        imported = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".")[0])
        self.assertTrue(
            imported.isdisjoint(
                {"subprocess", "shutil", "socket", "requests", "urllib", "git", "github", "importlib"}
            )
        )
        for forbidden in (
            "execute_preview",
            "guided_publisher",
            "gh workflow",
            "workflow run",
            "create_tree",
            "create_commit",
            "update_ref",
            "create_pull_request",
            "merge_pull_request",
            "mark_pull_request_ready_for_review",
            "eval(",
            "exec(",
        ):
            self.assertNotIn(forbidden, source)
        self.assertIn("READ_ONLY_CANDIDATE_NOT_EXECUTABLE", source)
        self.assertIn('"remote_dispatch_authority": False', source)
        self.assertIn('"guided_execute_invoked": False', source)

    def test_origin_and_journey_schemas_remain_closed_historical_evidence(self) -> None:
        origin = json.loads(
            (ROOT / "schemas/athena-fresh-work-origin-receipt-v1.schema.json").read_text(
                encoding="utf-8"
            )
        )
        journey = json.loads(
            (ROOT / "schemas/athena-fresh-work-journey-receipt-v1.schema.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertFalse(origin["additionalProperties"])
        self.assertFalse(journey["additionalProperties"])
        self.assertEqual(origin["properties"]["authorizer"]["const"], "Jayson")
        self.assertEqual(origin["properties"]["semantic_invoker"]["const"], "Athena")
        forbidden = origin["properties"]["forbidden_fields_absent"]
        self.assertFalse(forbidden["additionalProperties"])
        self.assertTrue(all(value == {"const": True} for value in forbidden["properties"].values()))
        bridge_mutation = journey["properties"]["bridge_mutation"]
        self.assertFalse(bridge_mutation["additionalProperties"])
        self.assertTrue(all(value == {"const": False} for value in bridge_mutation["properties"].values()))


if __name__ == "__main__":
    unittest.main()
