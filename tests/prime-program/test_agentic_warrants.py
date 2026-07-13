from __future__ import annotations

import copy
import json
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.athena_routes.schema import SchemaValidationError, validate_schema  # noqa: E402
from tools.agentic_warrants.validator import (  # noqa: E402
    WarrantValidationError, assert_transition, sha256, validate_receipt,
    validate_replacement, validate_warrant, warrant_body_sha256, warrant_sha256,
)


class ReplayLedger:
    def __init__(self) -> None:
        self.seen_requests: set[str] = set()
        self.seen_receipts: set[tuple[str, str, str]] = set()

    def consume(self, request_sha256: str, receipt_id: str, attempt_id: str, nonce: str) -> bool:
        key = (receipt_id, attempt_id, nonce)
        if request_sha256 in self.seen_requests or key in self.seen_receipts:
            return False
        self.seen_requests.add(request_sha256)
        self.seen_receipts.add(key)
        return True


class AgenticWarrantContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.schema = json.loads((ROOT / "schemas/agentic-capability-warrant-v1.schema.json").read_text(encoding="utf-8"))
        cls.receipt_schema = json.loads((ROOT / "schemas/agentic-warrant-receipt-v1.schema.json").read_text(encoding="utf-8"))
        cls.fixtures = json.loads((ROOT / "proof/repairing-prime/rp-c02-agentic-warrant-fixtures-r01.json").read_text(encoding="utf-8"))
        cls.parent, cls.child = cls.fixtures["parent"], cls.fixtures["child"]
        cls.parent_activation = cls.fixtures["activation_records"]["parent"]
        cls.child_activation = cls.fixtures["activation_records"]["child"]
        cls.now = datetime(2026, 7, 13, 1, tzinfo=timezone.utc)

    @staticmethod
    def trusted(record: dict) -> bool:
        return record["authorizer"] == "Jayson" and record["signature"].startswith("trusted-fixture-")

    def reactivate(self, warrant: dict, label: str) -> dict:
        record = copy.deepcopy(self.child_activation)
        record["warrant_id"] = warrant["warrant_id"]
        record["warrant_body_sha256"] = warrant_body_sha256(warrant)
        record["scope_sha256"] = sha256(warrant["scope"])
        record["signature"] = f"trusted-fixture-{label}"
        warrant["authority"]["activation_record_sha256"] = sha256(record)
        return record

    def test_closed_schemas_and_trusted_activation_validate(self) -> None:
        validate_schema(self.schema, self.parent)
        validate_schema(self.schema, self.child)
        validate_warrant(self.parent, activation_record=self.parent_activation, verifier=self.trusted, now=self.now)
        validate_warrant(self.child, activation_record=self.child_activation, verifier=self.trusted, parent=self.parent, parent_activation_record=self.parent_activation, now=self.now)
        extra = copy.deepcopy(self.parent)
        extra["undeclared_authority"] = True
        with self.assertRaises(SchemaValidationError):
            validate_schema(self.schema, extra)

    def test_self_asserted_or_untrusted_authority_is_rejected(self) -> None:
        with self.assertRaises(WarrantValidationError) as missing:
            validate_warrant(self.parent, verifier=self.trusted, now=self.now)
        self.assertEqual(missing.exception.code, "ACTIVATION_RECORD_REQUIRED")
        with self.assertRaises(WarrantValidationError) as forged:
            validate_warrant(self.parent, activation_record=self.parent_activation, verifier=lambda _record: False, now=self.now)
        self.assertEqual(forged.exception.code, "TRUSTED_AUTHORIZER_REJECTED")

    def test_route_action_and_protected_policy_are_fail_closed(self) -> None:
        read_write = copy.deepcopy(self.parent)
        read_write["scope"]["route"] = "READ_ONLY"
        with self.assertRaises(WarrantValidationError) as route:
            validate_warrant(read_write, now=self.now)
        self.assertEqual(route.exception.code, "ROUTE_ACTION_MISMATCH")
        protected = copy.deepcopy(self.parent)
        protected["scope"]["paths"] = ["governance/change-routes.md"]
        with self.assertRaises(WarrantValidationError) as boundary:
            validate_warrant(protected, now=self.now)
        self.assertEqual(boundary.exception.code, "PROTECTED_ROUTE_REQUIRED")
        self.assertFalse(self.parent["scope"]["private_data_allowed"])

    def test_delegation_cascades_parent_state_and_cannot_relax_controls(self) -> None:
        revoked = copy.deepcopy(self.parent)
        revoked["status"] = "REVOKED"
        revoked["lifecycle"]["revoked_at"] = "2026-07-13T00:30:00Z"
        with self.assertRaises(WarrantValidationError) as inactive:
            validate_warrant(self.child, activation_record=self.child_activation, verifier=self.trusted, parent=revoked, now=self.now)
        self.assertEqual(inactive.exception.code, "PARENT_WARRANT_INACTIVE")
        cases = []
        widened = copy.deepcopy(self.child)
        widened["scope"]["paths"].append("proof/repairing-prime/not-in-parent.md")
        cases.append((widened, "DELEGATION_SCOPE_WIDENED"))
        route = copy.deepcopy(self.child)
        route["scope"]["route"] = "AEGIS_BREAK_PROTECTED"
        cases.append((route, "DELEGATION_ROUTE_WIDENED"))
        evidence = copy.deepcopy(self.child)
        evidence["evidence"]["required_checks"] = ["READ_ONLY_VERIFY"]
        cases.append((evidence, "DELEGATION_EVIDENCE_RELAXED"))
        for warrant, code in cases:
            activation = self.reactivate(warrant, code.lower())
            with self.subTest(code=code), self.assertRaises(WarrantValidationError) as raised:
                validate_warrant(warrant, activation_record=activation, verifier=self.trusted, parent=self.parent, parent_activation_record=self.parent_activation, now=self.now)
            self.assertEqual(raised.exception.code, code)

    def test_lifecycle_ttl_timestamps_transitions_and_replacement_close(self) -> None:
        for forbidden in ("REVOKED->ACTIVE", "EXPIRED->ACTIVE", "REPLACED->ACTIVE", "DRAFT->MERGE"):
            previous, current = forbidden.split("->")
            with self.assertRaises(WarrantValidationError):
                assert_transition(previous, current)
        ttl = copy.deepcopy(self.parent)
        ttl["lifecycle"]["expires_at"] = "2026-07-15T00:00:01Z"
        with self.assertRaises(WarrantValidationError) as standing:
            validate_warrant(ttl, now=self.now)
        self.assertEqual(standing.exception.code, "EXPIRY_ORDER_INVALID")
        conflict = copy.deepcopy(self.parent)
        conflict["status"] = "SUSPENDED"
        conflict["lifecycle"]["suspended_at"] = "not-a-time"
        with self.assertRaises(WarrantValidationError) as time_error:
            validate_warrant(conflict, now=self.now)
        self.assertEqual(time_error.exception.code, "TIME_INVALID")
        future = copy.deepcopy(self.parent)
        future["lifecycle"]["issued_at"] = "2026-07-13T02:00:00Z"
        with self.assertRaises(WarrantValidationError) as not_yet_valid:
            validate_warrant(future, now=self.now)
        self.assertEqual(not_yet_valid.exception.code, "WARRANT_NOT_YET_VALID")
        previous = copy.deepcopy(self.parent)
        successor = copy.deepcopy(self.parent)
        previous["status"] = "REPLACED"
        previous["lifecycle"].update({"replaced_at": "2026-07-13T00:30:00Z", "replaced_by": "RP-C02-SUCCESSOR-R01"})
        successor["warrant_id"] = "RP-C02-SUCCESSOR-R01"
        successor["lifecycle"]["supersedes"] = previous["warrant_id"]
        validate_replacement(previous, successor)

    def receipt(self) -> dict:
        evidence = {"preview_sha256": self.child["evidence"]["preview_sha256"], "candidate_tree_sha256": None, "completed_checks": self.child["evidence"]["required_checks"]}
        return {
            "schema_version": "atlas.agentic-warrant-receipt.v1", "receipt_id": "RP-C02-RECEIPT-R01", "attempt_id": "RP-C02-ATTEMPT-R01",
            "nonce": "rp-c02-receipt-nonce-r01", "request_sha256": "4" * 64, "executed_at": "2026-07-13T01:00:00Z",
            "warrant_id": self.child["warrant_id"], "warrant_sha256": warrant_sha256(self.child),
            "observed_agent_id": self.child["agent_identity"]["agent_id"], "observed_credential_principal": self.child["authority"]["credential_principal"],
            "repository": "Jktomy/atlas-prime", "base_sha": self.child["scope"]["base_sha"], "head_sha": None, "route": "READ_ONLY",
            "actions": ["READ"], "paths": self.child["scope"]["paths"], "approval_record_sha256s": [], "result": "SUCCESS", "error_code": None,
            "stop_point": "READ_ONLY_RECEIPT", **evidence, "evidence_sha256": sha256(evidence), "rollback": "NO_MUTATION",
            "forbidden_action_confirmation": self.child["forbidden_actions"],
        }

    def test_receipt_binds_evidence_stop_rollback_identity_and_replay(self) -> None:
        receipt, ledger = self.receipt(), ReplayLedger()
        validate_schema(self.receipt_schema, receipt)
        validate_receipt(receipt, self.child, activation_record=self.child_activation, verifier=self.trusted, replay_guard=ledger.consume, request_sha256="4" * 64, parent=self.parent, parent_activation_record=self.parent_activation, now=self.now)
        with self.assertRaises(WarrantValidationError) as replay:
            validate_receipt(receipt, self.child, activation_record=self.child_activation, verifier=self.trusted, replay_guard=ledger.consume, request_sha256="4" * 64, parent=self.parent, parent_activation_record=self.parent_activation, now=self.now)
        self.assertEqual(replay.exception.code, "RECEIPT_REPLAYED")
        relabeled_replay = self.receipt()
        relabeled_replay.update({"receipt_id": "RP-C02-RECEIPT-R02", "attempt_id": "RP-C02-ATTEMPT-R02", "nonce": "rp-c02-receipt-nonce-r02"})
        with self.assertRaises(WarrantValidationError) as request_replay:
            validate_receipt(relabeled_replay, self.child, activation_record=self.child_activation, verifier=self.trusted, replay_guard=ledger.consume, request_sha256="4" * 64, parent=self.parent, parent_activation_record=self.parent_activation, now=self.now)
        self.assertEqual(request_replay.exception.code, "RECEIPT_REPLAYED")
        for field, value in (("stop_point", "ARBITRARY"), ("rollback", "ARBITRARY"), ("evidence_sha256", "9" * 64), ("observed_agent_id", "impersonator"), ("request_sha256", "8" * 64)):
            altered = self.receipt()
            altered[field] = value
            with self.subTest(field=field), self.assertRaises(WarrantValidationError):
                validate_receipt(altered, self.child, activation_record=self.child_activation, verifier=self.trusted, replay_guard=ReplayLedger().consume, request_sha256="4" * 64, parent=self.parent, parent_activation_record=self.parent_activation, now=self.now)
        inactive = copy.deepcopy(self.child)
        inactive["status"] = "SUSPENDED"
        inactive["lifecycle"]["suspended_at"] = "2026-07-13T00:30:00Z"
        with self.assertRaises(WarrantValidationError) as inactive_receipt:
            validate_receipt(self.receipt(), inactive, activation_record=self.child_activation, verifier=self.trusted, replay_guard=ReplayLedger().consume, request_sha256="4" * 64, parent=self.parent, parent_activation_record=self.parent_activation, now=self.now)
        self.assertEqual(inactive_receipt.exception.code, "WARRANT_INACTIVE")

    def test_contract_covers_required_agentic_boundaries(self) -> None:
        contract = (ROOT / "governance/agentic-warrant-contract.md").read_text(encoding="utf-8")
        for phrase in ("Identity and authority separation", "Lifecycle", "Delegation", "Human approval and routes", "Receipts and fail-closed behavior", "No transitive", "standing repository writer"):
            self.assertIn(phrase, contract)


if __name__ == "__main__":
    unittest.main()
