from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "governance" / "worldhopper-isolation-handoff-contract.md"
SCHEMA = ROOT / "schemas" / "worldhopper-workspace-v1.schema.json"
HEX = "a" * 64


def workspace() -> dict:
    return {
        "schema_version": "atlas.worldhopper.workspace.v1",
        "workspace_id": "WORLDHOPPER-WORKSPACE-R01",
        "mission_id": "MISSION-WORLDHOPPER-ISOLATION-HANDOFF-R01",
        "attempt_id": "MISSION-WORLDHOPPER-ISOLATION-HANDOFF-R01-ATTEMPT-01",
        "worker_identity": "WORLDHOPPER-FIXTURE",
        "credential_identity": "WORLDHOPPER-FIXTURE-CREDENTIAL",
        "carrier": {
            "carrier_id": "GEMSTONE-WORLDHOPPER-FIXTURE-R01",
            "sha256": HEX,
            "recipient": "WORLDHOPPER-FIXTURE",
            "purpose": "One bounded synthetic review",
            "expires_at": "2026-07-26T00:00:00Z",
            "sanitization_receipt": "receipt-sanitized",
        },
        "purpose": "One bounded synthetic review",
        "created_at": "2026-07-25T00:00:00Z",
        "expires_at": "2026-07-26T00:00:00Z",
        "allowed_tools": ["READ_SANITIZED_PACKET", "WRITE_RETURN_PACKET"],
        "allowed_destinations": ["EMBERDARK_RETURN_ENDPOINT"],
        "denied_resources": [
            "COPPERMIND", "ORIGINAL_VAULT", "PRIVATE_GLASS_CODEX", "PHOENIX",
            "PRIME_WRITE", "PROTECTED_POINTER_RESOLVER", "HOST_FILESYSTEM",
            "SHARED_CLIPBOARD", "LOCAL_LAN", "UNRESTRICTED_NETWORK",
            "SHARED_CREDENTIALS", "OTHER_MISSION_DATA",
        ],
        "isolation": {
            "process": "ISOLATED",
            "extension_host": "ISOLATED",
            "filesystem": "MISSION_BOUND",
            "temporary_files": "WORKSPACE_BOUND",
            "clipboard": "NO_HOST_BRIDGE",
            "caches": "WORKSPACE_BOUND",
            "logs": "WORKSPACE_BOUND",
            "crash_reports": "DISABLED",
            "network": "DESTINATION_ALLOWLIST",
            "repositories": "NO_STANDING_AUTHORITY",
            "models": "MISSION_BOUND",
            "tools": "ALLOWLIST_ONLY",
        },
        "lifecycle": {"status": "ACTIVE", "revoked_at": None, "destroyed_at": None, "residual_risk": []},
        "return_route": "EMBERDARK_QUARANTINE_TENSOON_VERIFY",
        "receipts": {
            "creation": "receipt-create",
            "delivery": "receipt-deliver",
            "revocation": None,
            "destruction": None,
            "return_quarantine": None,
            "verification": None,
        },
        "recovery": {
            "model_independent": True,
            "provider_replaceable": True,
            "instructions": "Rebuild only from the manifest, carrier digest, policy, receipts, and return disposition.",
        },
    }


class WorldhopperIsolationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = CONTRACT.read_text(encoding="utf-8")
        cls.schema = json.loads(SCHEMA.read_text(encoding="utf-8"))

    def test_schema_is_closed_and_fixture_has_exact_keys(self) -> None:
        item = workspace()
        self.assertFalse(self.schema["additionalProperties"])
        self.assertEqual(set(self.schema["required"]), set(item))
        self.assertEqual("atlas.worldhopper.workspace.v1", item["schema_version"])

    def test_protected_and_ambient_authority_are_denied(self) -> None:
        denied = set(workspace()["denied_resources"])
        for resource in (
            "COPPERMIND", "ORIGINAL_VAULT", "PRIVATE_GLASS_CODEX", "PHOENIX",
            "PRIME_WRITE", "PROTECTED_POINTER_RESOLVER", "HOST_FILESYSTEM",
            "SHARED_CLIPBOARD", "LOCAL_LAN", "UNRESTRICTED_NETWORK",
            "SHARED_CREDENTIALS", "OTHER_MISSION_DATA",
        ):
            self.assertIn(resource, denied)
        self.assertIn("profile name, editor workspace, prompt, or model policy is not a security boundary", self.contract)

    def test_all_isolation_surfaces_are_explicit(self) -> None:
        isolation = workspace()["isolation"]
        expected = {
            "process", "extension_host", "filesystem", "temporary_files", "clipboard",
            "caches", "logs", "crash_reports", "network", "repositories", "models", "tools",
        }
        self.assertEqual(expected, set(isolation))
        self.assertEqual("DESTINATION_ALLOWLIST", isolation["network"])
        self.assertEqual("NO_STANDING_AUTHORITY", isolation["repositories"])

    def test_delivery_is_exact_and_return_is_quarantined(self) -> None:
        item = workspace()
        self.assertEqual(item["worker_identity"], item["carrier"]["recipient"])
        self.assertEqual(item["purpose"], item["carrier"]["purpose"])
        self.assertEqual("EMBERDARK_QUARANTINE_TENSOON_VERIFY", item["return_route"])
        self.assertIn("cannot self-promote", self.contract)
        self.assertIn("TenSoon independently verifies", self.contract)

    def test_revocation_precedes_destruction_and_receipts_remain_explicit(self) -> None:
        item = workspace()
        item["lifecycle"] = {
            "status": "DESTROYED",
            "revoked_at": "2026-07-25T01:00:00Z",
            "destroyed_at": "2026-07-25T01:05:00Z",
            "residual_risk": ["Provider deletion not independently provable"],
        }
        item["receipts"]["revocation"] = "receipt-revoke"
        item["receipts"]["destruction"] = "receipt-destroy"
        self.assertLess(item["lifecycle"]["revoked_at"], item["lifecycle"]["destroyed_at"])
        self.assertTrue(item["receipts"]["revocation"])
        self.assertTrue(item["receipts"]["destruction"])
        self.assertIn("residual risk", self.contract)

    def test_provider_and_model_are_noncanonical_and_replaceable(self) -> None:
        recovery = workspace()["recovery"]
        self.assertTrue(recovery["model_independent"])
        self.assertTrue(recovery["provider_replaceable"])
        self.assertIn("External providers remain visible, bounded, replaceable, and noncanonical", self.contract)
        self.assertIn("cannot block Cloud Atlas, Prime, original recovery, or Mission Board continuity", self.contract)

    def test_unknown_fields_fail_closed_by_schema_contract(self) -> None:
        item = workspace()
        item["unexpected"] = "ambient-authority"
        self.assertNotIn("unexpected", self.schema["properties"])
        self.assertFalse(self.schema["additionalProperties"])


if __name__ == "__main__":
    unittest.main()
