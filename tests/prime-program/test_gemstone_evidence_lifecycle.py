from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "governance" / "gemstone-evidence-lifecycle-contract.md"
SCHEMA = ROOT / "schemas" / "gemstone-carrier-v1.schema.json"
FIXTURE = ROOT / "tests" / "prime-program" / "fixtures" / "gemstone-evidence-lifecycle-r01.json"
HEX = "a" * 64
SHA256 = re.compile(r"^[0-9a-f]{64}$")
CARRIER_CLASSES = {"ORIGINAL", "WORKING", "WORLDHOPPER"}
TOP_LEVEL = {
    "schema_version", "carrier_id", "carrier_class", "mission_id", "attempt_id",
    "created_at", "producer", "classification", "manifest_digest", "payload",
    "sources", "derivation", "worldhopper", "custody", "validation", "recovery",
}


def base_carrier(carrier_class: str) -> dict:
    return {
        "schema_version": "atlas.gemstone.carrier.v1",
        "carrier_id": f"GEMSTONE-{carrier_class}-R01",
        "carrier_class": carrier_class,
        "mission_id": "MISSION-GEMSTONE-EVIDENCE-LIFECYCLE-R01",
        "attempt_id": "ATTEMPT-01",
        "created_at": "2026-07-24T00:00:00Z",
        "producer": {"declared_worker": "Athena", "credential_principal": "Jktomy", "surface": "fixture"},
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
        "custody": [{"event": "ACQUIRED", "actor": "Emberdark", "timestamp": "2026-07-24T00:00:00Z", "receipt": "receipt-original"}],
        "validation": {
            "status": "PASS", "replay_checked": True, "tamper_checked": True,
            "sanitization_checked": False, "quarantine_status": "NOT_APPLICABLE",
        },
        "recovery": {
            "model_independent": True, "original_retrievable": True,
            "instructions": "Resolve the private pointer and verify byte length and SHA-256.",
            "encryption_disposition": "DEFERRED_DECISION_GATE",
        },
    }


def validate_carrier(carrier: dict) -> list[str]:
    errors: list[str] = []
    if set(carrier) != TOP_LEVEL:
        errors.append("top-level fields must be closed and complete")
    if carrier.get("schema_version") != "atlas.gemstone.carrier.v1":
        errors.append("schema version")
    carrier_class = carrier.get("carrier_class")
    if carrier_class not in CARRIER_CLASSES:
        errors.append("carrier class")
    if not SHA256.fullmatch(str(carrier.get("manifest_digest", ""))):
        errors.append("manifest digest")
    payload = carrier.get("payload", {})
    if not SHA256.fullmatch(str(payload.get("sha256", ""))):
        errors.append("payload digest")
    if payload.get("embedded_in_public_clean") is not False:
        errors.append("public-clean embedding forbidden")
    sources = carrier.get("sources")
    if not isinstance(sources, list):
        errors.append("sources")
        sources = []
    if carrier_class == "ORIGINAL":
        if carrier.get("classification") != "PROTECTED_ORIGINAL" or sources or carrier.get("derivation") is not None or carrier.get("worldhopper") is not None:
            errors.append("original constraints")
    elif carrier_class == "WORKING":
        if carrier.get("classification") != "PROTECTED_WORKING" or not sources or not isinstance(carrier.get("derivation"), dict) or carrier.get("worldhopper") is not None:
            errors.append("working constraints")
    elif carrier_class == "WORLDHOPPER":
        worldhopper = carrier.get("worldhopper")
        if carrier.get("classification") != "SANITIZED_WORLDHOPPER" or not sources or not isinstance(worldhopper, dict):
            errors.append("worldhopper constraints")
        elif worldhopper.get("return_route") != "EMBERDARK_QUARANTINE_TENSOON_VERIFY" or not worldhopper.get("allowed_fields") or not worldhopper.get("excluded_classes"):
            errors.append("worldhopper boundary")
    recovery = carrier.get("recovery", {})
    if recovery.get("model_independent") is not True:
        errors.append("model-independent recovery")
    return errors


class GemstoneEvidenceLifecycleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        cls.contract = CONTRACT.read_text(encoding="utf-8")

    def test_schema_and_fixture_are_closed_json_documents(self) -> None:
        self.assertFalse(self.schema["additionalProperties"])
        fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
        self.assertEqual([], validate_carrier(fixture))

    def test_original_is_byte_bound_and_not_replaced_by_ocr(self) -> None:
        carrier = base_carrier("ORIGINAL")
        self.assertEqual([], validate_carrier(carrier))
        for phrase in ("byte-for-byte", "never normalized", "cannot overwrite or masquerade as the original"):
            self.assertIn(phrase, self.contract)

    def test_working_requires_original_source_and_derivation(self) -> None:
        carrier = base_carrier("WORKING")
        carrier["classification"] = "PROTECTED_WORKING"
        carrier["sources"] = [{"carrier_id": "GEMSTONE-ORIGINAL-R01", "sha256": HEX, "relationship": "DERIVED_FROM"}]
        carrier["derivation"] = {"method": "OCR", "tool_identity": "fixture-tool", "output_digest": HEX, "limitations": "Synthetic fixture.", "human_verified": False}
        self.assertEqual([], validate_carrier(carrier))
        carrier["sources"] = []
        self.assertIn("working constraints", validate_carrier(carrier))

    def test_worldhopper_is_sanitized_recipient_bound_and_return_quarantined(self) -> None:
        carrier = base_carrier("WORLDHOPPER")
        carrier["classification"] = "SANITIZED_WORLDHOPPER"
        carrier["payload"]["private_pointer"] = None
        carrier["sources"] = [{"carrier_id": "GEMSTONE-WORKING-R01", "sha256": HEX, "relationship": "SANITIZED_FROM"}]
        carrier["worldhopper"] = {
            "recipient": "WORLDHOPPER-FIXTURE", "purpose": "One bounded synthetic review",
            "allowed_fields": ["sanitized_summary"],
            "excluded_classes": ["original_bytes", "credentials", "protected_pointers"],
            "expires_at": "2026-07-25T00:00:00Z",
            "return_route": "EMBERDARK_QUARANTINE_TENSOON_VERIFY",
            "sanitization_receipt": "receipt-sanitized",
        }
        self.assertEqual([], validate_carrier(carrier))
        self.assertIn("cannot self-promote", self.contract)
        self.assertIn("Emberdark quarantine", self.contract)

    def test_unknown_fields_and_public_embedding_fail_closed(self) -> None:
        carrier = base_carrier("ORIGINAL")
        carrier["unexpected"] = "replay"
        self.assertIn("top-level fields must be closed and complete", validate_carrier(carrier))
        carrier.pop("unexpected")
        carrier["payload"]["embedded_in_public_clean"] = True
        self.assertIn("public-clean embedding forbidden", validate_carrier(carrier))

    def test_encryption_mechanism_remains_separate_gate(self) -> None:
        self.assertIn("separate decision gate", self.contract)
        self.assertIn("selects no mechanism", self.contract)
        self.assertIn("DEFERRED_DECISION_GATE", json.dumps(self.schema))


if __name__ == "__main__":
    unittest.main()
