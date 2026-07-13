from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from tools.investiture_accounting.core import (
    InvestitureError,
    ZERO_SHA256,
    build_manifest,
    build_record,
    build_summary,
    event_from_bytes,
    sha256_object,
    stable_json,
    strict_loads,
    validate_event,
    validate_manifest,
)


ROOT = Path(__file__).resolve().parents[2]
FIXTURES = json.loads(
    (ROOT / "tests/prime-program/fixtures/investiture-events-v1.json").read_text(encoding="utf-8")
)["events"]


class InvestitureAccountingTests(unittest.TestCase):
    def test_closed_schema_surface_and_future_acceptance_boundary(self) -> None:
        names = (
            "investiture-event-v1.schema.json",
            "investiture-ledger-manifest-v1.schema.json",
            "investiture-ledger-record-v1.schema.json",
            "investiture-operation-receipt-v1.schema.json",
            "investiture-summary-v1.schema.json",
            "investiture-construction-acceptance-v1.schema.json",
        )
        for name in names:
            schema = json.loads((ROOT / "schemas" / name).read_text(encoding="utf-8"))
            self.assertFalse(schema["additionalProperties"])
        record_schema = json.loads((ROOT / "schemas/investiture-ledger-record-v1.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(record_schema["properties"]["event"]["$ref"], "investiture-event-v1.schema.json")
        acceptance = json.loads((ROOT / "schemas/investiture-construction-acceptance-v1.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(
            acceptance["properties"]["promotion_boundary"]["const"],
            "SEPARATE_AUTHORED_ACCEPTANCE_RECONCILIATION_REQUIRED",
        )
        self.assertFalse(acceptance["properties"]["external_store_selected"]["const"])
        self.assertFalse(acceptance["properties"]["real_provider_usage_accepted"]["const"])
        implementation = acceptance["properties"]["implementation_hashes"]
        self.assertFalse(implementation["additionalProperties"])
        self.assertEqual(set(implementation["required"]), set(implementation["properties"]))
        deterministic = acceptance["properties"]["deterministic_results"]
        self.assertEqual(deterministic["properties"]["fixture_event_count"]["const"], 5)
        self.assertEqual(deterministic["properties"]["committed_record_count"]["const"], 5)
        self.assertEqual(deterministic["properties"]["known_beu_subtotal"]["const"], 29)
        self.assertFalse(deterministic["properties"]["complete_total_available"]["const"])
        self.assertEqual(acceptance["properties"]["mission_states"]["properties"]["FS-C01-M04"]["const"], "UNPROVEN")

    def test_fixture_events_validate_and_only_usage_has_measurement(self) -> None:
        self.assertEqual(len(FIXTURES), 5)
        for event in FIXTURES:
            self.assertEqual(validate_event(copy.deepcopy(event)), event)
            if event["event_type"] == "USAGE_REPORTED":
                self.assertIsInstance(event["measurement"], dict)
                self.assertEqual(event["bound_usage_event_ids"], [])
            else:
                self.assertIsNone(event["measurement"])

    def test_strict_json_and_unknown_fields_fail_closed(self) -> None:
        with self.assertRaisesRegex(InvestitureError, "DUPLICATE_JSON_KEY"):
            strict_loads(b'{"schema_version":"x","schema_version":"y"}')
        unknown = copy.deepcopy(FIXTURES[0])
        unknown["raw_prompt"] = "must not enter the ledger"
        with self.assertRaisesRegex(InvestitureError, "EVENT_SCHEMA_INVALID"):
            event_from_bytes(stable_json(unknown))
        estimated = copy.deepcopy(FIXTURES[0])
        estimated["measurement"]["state"] = "ESTIMATED"
        with self.assertRaisesRegex(InvestitureError, "EVENT_SCHEMA_INVALID"):
            validate_event(estimated)

    def test_provider_light_and_local_control_are_independent_and_exact(self) -> None:
        wrong = copy.deepcopy(FIXTURES[0])
        wrong["measurement"]["light"] = "Chromelight"
        with self.assertRaisesRegex(InvestitureError, "LIGHT_IDENTITY_MISMATCH"):
            validate_event(wrong)
        local = copy.deepcopy(FIXTURES[0])
        local["measurement"].update({"provider_origin": "ATLAS_LOCAL", "light": "Emberlight", "atlas_runtime_control": False})
        with self.assertRaisesRegex(InvestitureError, "LOCAL_RUNTIME_CONTROL_REQUIRED"):
            validate_event(local)
        secret = copy.deepcopy(FIXTURES[0])
        secret["measurement"]["model_id"] = "sk-SENTINELSECRET123456"
        with self.assertRaisesRegex(InvestitureError, "SENSITIVE_VALUE_REJECTED"):
            validate_event(secret)
        private_address = copy.deepcopy(FIXTURES[0])
        private_address["measurement"]["runtime_id"] = "192.168.1.25"
        with self.assertRaisesRegex(InvestitureError, "SENSITIVE_VALUE_REJECTED"):
            validate_event(private_address)
        private_ipv6 = copy.deepcopy(FIXTURES[0])
        private_ipv6["measurement"]["runtime_id"] = "fd00::25"
        with self.assertRaisesRegex(InvestitureError, "SENSITIVE_VALUE_REJECTED"):
            validate_event(private_ipv6)

    def test_counting_basis_rejects_overlap_and_wrong_totals(self) -> None:
        total = copy.deepcopy(FIXTURES[0])
        total["measurement"]["categories"][1]["role"] = "COUNTED"
        with self.assertRaisesRegex(InvestitureError, "AUTHORITATIVE_TOTAL_INVALID"):
            validate_event(total)
        leaves = copy.deepcopy(FIXTURES[1])
        leaves["measurement"]["categories"][1]["parent_category_id"] = "INPUT"
        with self.assertRaisesRegex(InvestitureError, "COUNTED_CATEGORY_OVERLAP"):
            validate_event(leaves)
        subtotal = copy.deepcopy(FIXTURES[1])
        subtotal["measurement"]["known_beu_subtotal"] = 9
        with self.assertRaisesRegex(InvestitureError, "PARTIAL_SUBTOTAL_INVALID"):
            validate_event(subtotal)

    def test_unavailable_and_zero_model_never_invent_light_or_precision(self) -> None:
        unavailable = copy.deepcopy(FIXTURES[2])
        unavailable["measurement"]["total_investiture_beu"] = 0
        with self.assertRaisesRegex(InvestitureError, "UNAVAILABLE_VALUE_FORBIDDEN"):
            validate_event(unavailable)
        zero = copy.deepcopy(FIXTURES[3])
        zero["measurement"]["light"] = "Emberlight"
        with self.assertRaisesRegex(InvestitureError, "ZERO_MODEL_IDENTITY_FORBIDDEN"):
            validate_event(zero)

    def test_lifecycle_binding_never_recounts_and_summary_is_deterministic(self) -> None:
        manifest = build_manifest(
            ledger_id="FS-C01-LEDGER-R01",
            generation_id="FS-C01-GEN-R01",
            created_at="2026-07-13T19:00:00Z",
        )
        records = []
        prior = ZERO_SHA256
        for index, event in enumerate(FIXTURES, start=1):
            record = build_record(manifest, copy.deepcopy(event), sequence=index, prior_sha256=prior)
            records.append(record)
            prior = record["record_sha256"]
        first = build_summary(manifest, records)
        second = build_summary(manifest, copy.deepcopy(records))
        self.assertEqual(stable_json(first), stable_json(second))
        self.assertEqual(first["record_count"], 5)
        self.assertEqual(first["light_known_beu"], {"Spirallight": 21, "Chromelight": 8, "Emberlight": 0})
        self.assertEqual(first["known_beu_subtotal"], 29)
        self.assertIsNone(first["total_investiture_beu"])
        self.assertFalse(first["complete_total_available"])
        self.assertEqual(first["measurement_counts"], {"MEASURED": 1, "PARTIAL": 1, "UNAVAILABLE": 1, "ZERO_MODEL": 1})
        tampered = copy.deepcopy(records)
        tampered[0]["event"]["measurement"]["total_investiture_beu"] = 999
        with self.assertRaises(InvestitureError):
            build_summary(manifest, tampered)

    def test_inherited_generation_totals_and_identity_cardinality_fail_closed(self) -> None:
        inherited_summary = {
            "record_count": 1,
            "measurement_counts": {"MEASURED": 1, "PARTIAL": 0, "UNAVAILABLE": 0, "ZERO_MODEL": 0},
            "light_known_beu": {"Spirallight": 21, "Chromelight": 0, "Emberlight": 0},
            "known_beu_subtotal": 21,
            "total_investiture_beu": 21,
            "complete_total_available": True,
        }
        event_identity = "a" * 64
        inherited_identities = {
            "event": [event_identity],
            "replay": ["b" * 64],
            "usage_event": [event_identity],
            "usage_scope": ["c" * 64],
            "source_receipt": ["d" * 64],
        }
        with self.assertRaisesRegex(InvestitureError, "MANIFEST_INHERITANCE_REQUIRED"):
            build_manifest(
                ledger_id="FS-C01-LEDGER-R01",
                generation_id="FS-C01-GEN-R02",
                created_at="2026-07-13T20:00:00Z",
                previous_generation_id="FS-C01-GEN-R01",
                previous_last_record_sha256="e" * 64,
            )
        manifest = build_manifest(
            ledger_id="FS-C01-LEDGER-R01",
            generation_id="FS-C01-GEN-R02",
            created_at="2026-07-13T20:00:00Z",
            previous_generation_id="FS-C01-GEN-R01",
            previous_last_record_sha256="e" * 64,
            inherited_summary=inherited_summary,
            inherited_identities=inherited_identities,
        )
        wrong_total = copy.deepcopy(manifest)
        wrong_total["inherited_known_beu_subtotal"] = 22
        wrong_total["manifest_sha256"] = sha256_object({key: value for key, value in wrong_total.items() if key != "manifest_sha256"})
        with self.assertRaisesRegex(InvestitureError, "MANIFEST_INHERITED_TOTAL_INVALID"):
            validate_manifest(wrong_total)
        wrong_cardinality = copy.deepcopy(manifest)
        wrong_cardinality["inherited_replay_identity_sha256s"] = []
        wrong_cardinality["manifest_sha256"] = sha256_object({key: value for key, value in wrong_cardinality.items() if key != "manifest_sha256"})
        with self.assertRaisesRegex(InvestitureError, "MANIFEST_INHERITED_CARDINALITY_INVALID"):
            validate_manifest(wrong_cardinality)


if __name__ == "__main__":
    unittest.main()
