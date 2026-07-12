from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.atlas_lifecycle.errors import LifecycleError
from tools.atlas_lifecycle.event_paths import bind_event_storage_path, declared_event_path
from tools.atlas_lifecycle.jsonio import load_bounded, stable_record_id
from tools.atlas_lifecycle.schema import SchemaValidator


FIXTURES = ROOT / "lifecycle/fixtures"
SCHEMAS = ROOT / "lifecycle/schemas"


class LifecycleEventContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.validator = SchemaValidator(SCHEMAS)
        cls.checkpoint = load_bounded(FIXTURES / "lifecycle-event-checkpoint.json")
        cls.protected = load_bounded(
            FIXTURES / "lifecycle-event-protected-checkpoint.json"
        )
        cls.completion = load_bounded(
            FIXTURES / "lifecycle-event-gate-completed.json"
        )
        cls.revocation = load_bounded(
            FIXTURES / "lifecycle-event-completion-revoked.json"
        )

    def assert_rejected(self, record: dict) -> None:
        with self.assertRaises(LifecycleError):
            self.validator.validate_record(record)

    def test_one_envelope_validates_both_closed_event_classes(self) -> None:
        for record in (
            self.checkpoint,
            self.protected,
            self.completion,
            self.revocation,
        ):
            with self.subTest(record=record["record_id"]):
                self.validator.validate_record(record)
                self.assertEqual(record["schema_id"], "atlas.lifecycle.event")
                self.assertEqual(record["record_id"], stable_record_id(record))
                self.assertEqual(set(record), set(load_bounded(
                    SCHEMAS / "lifecycle-event-v1.schema.json"
                )["required"]))

    def test_event_path_is_single_exact_content_addressed_storage_location(self) -> None:
        seen_paths: set[str] = set()
        for record in (
            self.checkpoint,
            self.protected,
            self.completion,
            self.revocation,
        ):
            declared = declared_event_path(record)
            self.assertTrue(declared.startswith("lifecycle/events/"))
            self.assertTrue(declared.endswith(".json"))
            bind_event_storage_path(record, declared, seen_paths)

            changed = copy.deepcopy(record)
            changed["route"]["allowed_paths"] = [declared[:-5] + "-revision.json"]
            self.assertNotEqual(stable_record_id(changed), record["record_id"])

    def test_event_path_rejects_mismatch_reuse_casefold_and_unsafe_shapes(self) -> None:
        declared = declared_event_path(self.checkpoint)
        with self.assertRaises(LifecycleError) as raised:
            bind_event_storage_path(self.checkpoint, "lifecycle/events/other.json", set())
        self.assertEqual(raised.exception.code, "EVENT_PATH_MISMATCH")

        seen = {declared.casefold()}
        with self.assertRaises(LifecycleError) as raised:
            bind_event_storage_path(self.checkpoint, declared, seen)
        self.assertEqual(raised.exception.code, "EVENT_PATH_COLLISION")

        for unsafe in (
            "../escape.json",
            "/lifecycle/events/absolute.json",
            "lifecycle\\events\\backslash.json",
            "lifecycle/events/nested/event.json",
            "lifecycle/events/not-json.txt",
            "lifecycle/other/event.json",
        ):
            changed = copy.deepcopy(self.checkpoint)
            changed["route"]["allowed_paths"] = [unsafe]
            with self.subTest(path=unsafe), self.assertRaises(LifecycleError):
                declared_event_path(changed)

        changed = copy.deepcopy(self.checkpoint)
        changed["route"]["allowed_paths"] = [declared, "lifecycle/events/second.json"]
        with self.assertRaises(LifecycleError) as raised:
            declared_event_path(changed)
        self.assertEqual(raised.exception.code, "EVENT_PATH_CARDINALITY")

    def test_checkpoint_is_nonterminal_and_preserves_exact_position(self) -> None:
        checkpoint = self.checkpoint["checkpoint"]
        self.assertEqual(checkpoint["gate_state"], "IN_PROGRESS")
        self.assertFalse(checkpoint["completion_receipt_created"])
        self.assertFalse(checkpoint["position_advance_requested"])
        self.assertEqual(checkpoint["resolved_blocker_ids"], [])
        for field in ("quest_id", "campaign_id", "mission_id", "gate_id"):
            self.assertIsNotNone(self.checkpoint["position"][field])

        mutations = []
        for field, value in (
            ("gate_state", "COMPLETE"),
            ("completion_receipt_created", True),
            ("position_advance_requested", True),
            ("resolved_blocker_ids", ["fixture-blocker"]),
        ):
            record = copy.deepcopy(self.checkpoint)
            record["checkpoint"][field] = value
            mutations.append(record)
        for field in ("quest_id", "campaign_id", "mission_id", "gate_id"):
            record = copy.deepcopy(self.checkpoint)
            record["position"][field] = None
            mutations.append(record)
        for record in mutations:
            self.assert_rejected(record)

    def test_transition_requires_independent_receipt_and_forbids_merge_trigger(self) -> None:
        self.validator.validate_record(self.completion)
        receipt = self.completion["evidence"]["trusted_acceptance_receipt_ref"]
        self.assertIsNotNone(receipt)
        self.assertFalse(self.completion["transition"]["ordinary_merge_event"])
        self.assertFalse(self.completion["transition"]["generated_output_trigger"])

        for field, value in (
            ("ordinary_merge_event", True),
            ("generated_output_trigger", True),
            ("acceptance_semantically_authored", False),
        ):
            record = copy.deepcopy(self.completion)
            record["transition"][field] = value
            self.assert_rejected(record)
        record = copy.deepcopy(self.completion)
        record["evidence"]["trusted_acceptance_receipt_ref"] = None
        self.assert_rejected(record)

    def test_external_event_trust_root_is_closed_and_independent(self) -> None:
        trust_root = {
            "schema_id": "atlas.lifecycle.event-trust-root",
            "schema_version": "1.0.0",
            "trust_root_id": "fixture-event-trust-root",
            "expected_main_sha": "0" * 40,
            "expected_entity_revision": 1,
            "expected_quest_revision": 1,
            "accepted_event_schema_id": "atlas.lifecycle.event",
            "accepted_event_schema_digest": "sha256:" + "1" * 64,
            "acceptance_contract_ref": {
                "ref_id": "lifecycle-event-contract",
                "authority": "CANONICAL_SOURCE",
                "uri": "lifecycle/lifecycle-event-contract.md",
            },
            "acceptance_contract_digest": "sha256:" + "2" * 64,
            "expected_evidence_sha": "3" * 40,
            "allowed_route_authority": "ATHENA_DIRECT",
            "allowed_paths": ["lifecycle/events/fixture-event.json"],
        }
        self.validator.validate_event_trust_root(trust_root)
        for mutation in (
            {**trust_root, "expected_main_sha": "4" * 39},
            {**trust_root, "accepted_event_schema_id": "atlas.lifecycle.receipt"},
            {**trust_root, "allowed_paths": ["../escape.json"]},
            {**trust_root, "unexpected": "self-supplied"},
        ):
            with self.assertRaises(LifecycleError):
                self.validator.validate_event_trust_root(mutation)
        for record in (self.checkpoint, self.protected, self.completion, self.revocation):
            reference = record["expectations"]["trusted_expectation_ref"]
            self.assertEqual(
                reference["uri"],
                "lifecycle/trust-roots/fixture-event-trust-root.json",
            )

    def test_event_classes_cannot_exchange_payloads_or_types(self) -> None:
        record = copy.deepcopy(self.checkpoint)
        record["event_type"] = "GATE_COMPLETED"
        self.assert_rejected(record)
        record = copy.deepcopy(self.completion)
        record["checkpoint"] = copy.deepcopy(self.checkpoint["checkpoint"])
        self.assert_rejected(record)
        record = copy.deepcopy(self.completion)
        record["unexpected"] = "closed schema"
        self.assert_rejected(record)

    def test_explicit_revocation_and_protected_pointer_lineage(self) -> None:
        self.assertEqual(self.revocation["event_type"], "COMPLETION_REVOKED")
        self.assertEqual(
            self.revocation["lineage"]["revokes_event_id"],
            self.completion["record_id"],
        )
        protected = self.protected["protected_data"]
        self.assertEqual(protected["classification"], "PROTECTED_POINTER_ONLY")
        self.assertEqual(
            protected["protected_pointers"],
            ["protected://fixture/raphael/lifecycle-checkpoint"],
        )

    def test_contract_preserves_authority_and_activation_boundaries(self) -> None:
        decision = " ".join((
            ROOT / "lifecycle/architecture-decision-r02.md"
        ).read_text(encoding="utf-8").split())
        contract = " ".join((
            ROOT / "lifecycle/lifecycle-event-contract.md"
        ).read_text(encoding="utf-8").split())
        for phrase in (
            "current Quest Board retains its canonical role",
            "Thread Engine self-change",
            "No code presence activates GitHub processing",
        ):
            self.assertIn(phrase, decision)
        for phrase in (
            "one-envelope contract",
            "ordinary merge or generated projection cannot",
            "self-supplied trust expectations",
            "Structural validation is defense in depth",
            "sole exception to the general `<record_id>.json`",
            "never by physical path",
        ):
            self.assertIn(phrase, contract)


if __name__ == "__main__":
    unittest.main()
