from __future__ import annotations

import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "governance" / "gemstone-evidence-lifecycle-contract.md"
SCHEMA = ROOT / "schemas" / "gemstone-carrier-v1.schema.json"
HEX = "a" * 64


def base_carrier(carrier_class: str) -> dict:
    return {
        "schema_version": "atlas.gemstone.carrier.v1",
        "carrier_id": f"GEMSTONE-{carrier_class}-R01",
        "carrier_class": carrier_class,
        "mission_id": "MISSION-GEMSTONE-EVIDENCE-LIFECYCLE-R01",
        "attempt_id": "ATTEMPT-01",
        "created_at": "2026-07-24T00:00:00Z",
        "producer": {
            "declared_worker": "Athena",
            "credential_principal": "Jktomy",
            "surface": "fixture",
        },
        "classification": "PROTECTED_ORIGINAL",
        "manifest_digest": HEX,
        "payload": {
            "sha256": HEX,
            "byte_length": 12,
            "media_type": "application/octet-stream",
            "private_pointer": "protected://cloud-atlas/originals/example",
            "embedded_in_public_clean": False,
        },
        "sources": [],
        "derivation": None,
        "worldhopper": None,
        "custody": [
            {
                "event": "ACQUIRED",
                "actor": "Emberdark",
                "timestamp": "2026-07-24T00:00:00Z",
                "receipt": "receipt-original",
            }
        ],
        "validation": {
            "status": "PASS",
            "replay_checked": True,
            "tamper_checked": True,
            "sanitization_checked": False,
            "quarantine_status": "NOT_APPLICABLE",
        },
        "recovery": {
            "model_independent": True,
            "original_retrievable": True,
            "instructions": "Resolve the private pointer and verify byte length and SHA-256.",
            "encryption_disposition": "DEFERRED_DECISION_GATE",
        },
    }


class GemstoneEvidenceLifecycleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        cls.validator = Draft202012Validator(cls.schema)
        cls.contract = CONTRACT.read_text(encoding="utf-8")

    def assert_valid(self, carrier: dict) -> None:
        errors = sorted(self.validator.iter_errors(carrier), key=lambda e: list(e.path))
        self.assertEqual([], [error.message for error in errors])

    def test_original_is_byte_bound_and_not_replaced_by_ocr(self) -> None:
        carrier = base_carrier("ORIGINAL")
        self.assert_valid(carrier)
        self.assertFalse(carrier["payload"]["embedded_in_public_clean"])
        self.assertIsNone(carrier["derivation"])
        for phrase in ("byte-for-byte", "never normalized", "cannot overwrite or masquerade as the original"):
            self.assertIn(phrase, self.contract)

    def test_working_requires_original_source_and_derivation(self) -> None:
        carrier = base_carrier("WORKING")
        carrier["classification"] = "PROTECTED_WORKING"
        carrier["sources"] = [{"carrier_id": "GEMSTONE-ORIGINAL-R01", "sha256": HEX, "relationship": "DERIVED_FROM"}]
        carrier["derivation"] = {
            "method": "OCR",
            "tool_identity": "fixture-tool",
            "output_digest": HEX,
            "limitations": "Synthetic fixture; confidence is not canonical truth.",
            "human_verified": False,
        }
        self.assert_valid(carrier)
        carrier["sources"] = []
        self.assertTrue(list(self.validator.iter_errors(carrier)))

    def test_worldhopper_is_recipient_bound_sanitized_and_quarantined_on_return(self) -> None:
        carrier = base_carrier("WORLDHOPPER")
        carrier["classification"] = "SANITIZED_WORLDHOPPER"
        carrier["payload"]["private_pointer"] = None
        carrier["sources"] = [{"carrier_id": "GEMSTONE-WORKING-R01", "sha256": HEX, "relationship": "SANITIZED_FROM"}]
        carrier["worldhopper"] = {
            "recipient": "WORLDHOPPER-FIXTURE",
            "purpose": "One bounded synthetic review",
            "allowed_fields": ["sanitized_summary"],
            "excluded_classes": ["original_bytes", "credentials", "protected_pointers"],
            "expires_at": "2026-07-25T00:00:00Z",
            "return_route": "EMBERDARK_QUARANTINE_TENSOON_VERIFY",
            "sanitization_receipt": "receipt-sanitized",
        }
        carrier["validation"]["sanitization_checked"] = True
        carrier["validation"]["quarantine_status"] = "PENDING"
        self.assert_valid(carrier)
        self.assertIn("cannot self-promote", self.contract)
        self.assertIn("Emberdark quarantine", self.contract)

    def test_unknown_fields_and_public_embedding_fail_closed(self) -> None:
        carrier = base_carrier("ORIGINAL")
        carrier["unexpected"] = "replay"
        self.assertTrue(list(self.validator.iter_errors(carrier)))
        carrier.pop("unexpected")
        carrier["payload"]["embedded_in_public_clean"] = True
        self.assertTrue(list(self.validator.iter_errors(carrier)))

    def test_encryption_mechanism_remains_separate_gate(self) -> None:
        self.assertIn("separate decision gate", self.contract)
        self.assertIn("selects no mechanism", self.contract)
        self.assertIn("DEFERRED_DECISION_GATE", json.dumps(self.schema))


if __name__ == "__main__":
    unittest.main()
