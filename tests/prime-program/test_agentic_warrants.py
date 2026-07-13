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
    WarrantValidationError,
    assert_transition,
    validate_receipt,
    validate_warrant,
    warrant_sha256,
)


class AgenticWarrantContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.schema = json.loads((ROOT / "schemas/agentic-capability-warrant-v1.schema.json").read_text(encoding="utf-8"))
        cls.receipt_schema = json.loads((ROOT / "schemas/agentic-warrant-receipt-v1.schema.json").read_text(encoding="utf-8"))
        cls.fixtures = json.loads((ROOT / "proof/repairing-prime/rp-c02-agentic-warrant-fixtures-r01.json").read_text(encoding="utf-8"))
        cls.parent = cls.fixtures["parent"]
        cls.child = cls.fixtures["child"]

    def test_closed_parent_and_child_warrants_validate(self) -> None:
        validate_schema(self.schema, self.parent)
        validate_schema(self.schema, self.child)
        extra = copy.deepcopy(self.parent)
        extra["undeclared_authority"] = True
        with self.assertRaises(SchemaValidationError):
            validate_schema(self.schema, extra)

    def test_semantic_validator_accepts_exact_parent_and_child(self) -> None:
        now = datetime(2026, 7, 13, 1, tzinfo=timezone.utc)
        validate_warrant(self.parent, now=now)
        validate_warrant(self.child, parent=self.parent, now=now)

    def test_semantic_validator_rejects_scope_expiry_lifecycle_and_approval_drift(self) -> None:
        now = datetime(2026, 7, 13, 1, tzinfo=timezone.utc)
        cases = []
        widened = copy.deepcopy(self.child)
        widened["scope"]["paths"].append("proof/repairing-prime/not-in-parent.md")
        cases.append((widened, "DELEGATION_SCOPE_WIDENED"))
        route_widened = copy.deepcopy(self.child)
        route_widened["scope"]["route"] = "AEGIS_BREAK_PROTECTED"
        cases.append((route_widened, "DELEGATION_ROUTE_WIDENED"))
        expired = copy.deepcopy(self.parent)
        expired["lifecycle"]["expires_at"] = "2026-07-13T00:30:00Z"
        cases.append((expired, "WARRANT_EXPIRED"))
        suspended = copy.deepcopy(self.parent)
        suspended["status"] = "SUSPENDED"
        cases.append((suspended, "LIFECYCLE_STATE_INVALID"))
        approval = copy.deepcopy(self.parent)
        approval["scope"]["actions"].append("MERGE")
        approval["human_approval"]["merge"] = False
        cases.append((approval, "HUMAN_APPROVAL_REQUIRED"))
        unsafe_path = copy.deepcopy(self.parent)
        unsafe_path["scope"]["paths"] = ["../escape"]
        cases.append((unsafe_path, "PATH_SCOPE_INVALID"))
        for warrant, code in cases:
            with self.subTest(code=code), self.assertRaises(WarrantValidationError) as raised:
                validate_warrant(warrant, parent=self.parent if warrant in (widened, route_widened) else None, now=now)
            self.assertEqual(raised.exception.code, code)

    def test_delegation_is_depth_one_subset_only(self) -> None:
        self.assertTrue(self.parent["delegation"]["allowed"])
        self.assertEqual(self.child["delegation"]["parent_warrant_id"], self.parent["warrant_id"])
        self.assertEqual(self.child["delegation"]["depth"], 1)
        self.assertTrue(set(self.child["scope"]["actions"]).issubset(self.parent["scope"]["actions"]))
        self.assertTrue(set(self.child["scope"]["paths"]).issubset(self.parent["scope"]["paths"]))
        self.assertEqual(self.child["scope"]["repository"], self.parent["scope"]["repository"])
        self.assertEqual(self.child["scope"]["base_sha"], self.parent["scope"]["base_sha"])
        self.assertFalse(self.child["delegation"]["allowed"])

    def test_lifecycle_is_fail_closed_and_terminal(self) -> None:
        allowed = set(self.fixtures["allowed_transitions"])
        for transition in ("DRAFT->ACTIVE", "ACTIVE->SUSPENDED", "SUSPENDED->ACTIVE", "ACTIVE->REVOKED"):
            self.assertIn(transition, allowed)
        for terminal in self.fixtures["terminal_states"]:
            self.assertFalse(any(item.startswith(terminal + "->") for item in allowed))
        for forbidden in ("REVOKED->ACTIVE", "EXPIRED->ACTIVE", "REPLACED->ACTIVE", "DRAFT->MERGE"):
            self.assertNotIn(forbidden, allowed)
            with self.assertRaises(WarrantValidationError):
                previous, current = forbidden.split("->")
                assert_transition(previous, current)

    def test_identity_principal_route_and_approval_are_independent(self) -> None:
        self.assertNotEqual(self.parent["agent_identity"]["agent_id"], self.parent["authority"]["authorizer"])
        self.assertIn("credential_principal", self.parent["authority"])
        self.assertIn("route", self.parent["scope"])
        for boundary in ("ready", "merge", "settings", "provider_activation", "protected_action", "destructive_action"):
            self.assertTrue(self.parent["human_approval"][boundary])
        self.assertFalse(any(self.parent["forbidden_actions"].values()))

    def test_receipt_binds_warrant_observed_identity_scope_and_evidence(self) -> None:
        receipt = {
            "schema_version": "atlas.agentic-warrant-receipt.v1", "warrant_id": self.child["warrant_id"], "warrant_sha256": warrant_sha256(self.child),
            "observed_agent_id": self.child["agent_identity"]["agent_id"], "observed_credential_principal": self.child["authority"]["credential_principal"],
            "repository": "Jktomy/atlas-prime", "base_sha": self.child["scope"]["base_sha"], "head_sha": None, "route": self.child["scope"]["route"],
            "actions": self.child["scope"]["actions"], "paths": self.child["scope"]["paths"], "approval_record_sha256": None,
            "result": "SUCCESS", "error_code": None, "stop_point": self.child["scope"]["stop_boundary"], "evidence_sha256": "5" * 64,
            "rollback": "NO_MUTATION", "forbidden_action_confirmation": self.child["forbidden_actions"],
        }
        validate_schema(self.receipt_schema, receipt)
        validate_receipt(receipt, self.child, parent=self.parent)
        mismatch = copy.deepcopy(receipt)
        mismatch["repository"] = "Jktomy/atlas-codex"
        with self.assertRaises(SchemaValidationError):
            validate_schema(self.receipt_schema, mismatch)
        principal_mismatch = copy.deepcopy(receipt)
        principal_mismatch["observed_credential_principal"] = "someone-else"
        with self.assertRaises(WarrantValidationError):
            validate_receipt(principal_mismatch, self.child, parent=self.parent)

    def test_contract_covers_required_agentic_boundaries(self) -> None:
        contract = (ROOT / "governance/agentic-warrant-contract.md").read_text(encoding="utf-8")
        for phrase in ("Identity and authority separation", "Lifecycle", "Delegation", "Human approval and routes", "Receipts and fail-closed behavior", "No transitive", "standing repository writer"):
            self.assertIn(phrase, contract)


if __name__ == "__main__":
    unittest.main()
