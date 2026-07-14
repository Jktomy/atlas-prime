from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
HISTORICAL_PROOF = ROOT / "proof/repairing-prime/rp-c07-acceptance-reconciliation-r01.json"
CURRENT_PROOF = ROOT / "proof/repairing-prime/rp-c08-cap015-architecture-realignment-r02.json"
CONTRACT = ROOT / "governance/capability-acceptance-contract.md"


class RpC07AcceptanceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.historical = json.loads(HISTORICAL_PROOF.read_text(encoding="utf-8"))
        self.current = json.loads(CURRENT_PROOF.read_text(encoding="utf-8"))

    def test_historical_reconciliation_remains_exact(self) -> None:
        self.assertEqual(set(self.historical["journeys"]), {f"AJ-{index:02d}" for index in range(1, 13)})
        states = {identity: record["state"] for identity, record in self.historical["journeys"].items()}
        self.assertEqual(states["AJ-01"], "UNPROVEN")
        self.assertEqual(states["AJ-02"], "PROVEN")
        self.assertEqual(states["AJ-03"], "UNPROVEN")
        self.assertEqual(states["AJ-11"], "UNPROVEN")
        self.assertEqual(states["AJ-12"], "UNPROVEN")
        for identity in (f"AJ-{index:02d}" for index in range(4, 11)):
            self.assertEqual(states[identity], "PROVEN")

    def test_later_reconciliation_advances_only_aj01(self) -> None:
        self.assertEqual(self.current["transitions"]["AJ-01"]["to"], "PROVEN")
        self.assertEqual(self.current["accepted_evidence"]["direct_spear"]["pull_request"], 102)
        self.assertIn("AJ-03", self.current["preserved_open"])
        self.assertIn("AJ-11", self.current["preserved_open"])
        self.assertIn("AJ-12", self.current["preserved_open"])
        self.assertTrue(all(value is False for value in self.current["forbidden_promotions"].values()))

    def test_hosted_identity_is_fully_separated(self) -> None:
        identity = self.historical["hosted_identity"]["identity"]
        required = {
            "authorizer", "event_actor", "triggering_actor", "workflow_ref",
            "workflow_source_sha", "credential_principal", "token_mode",
            "mission_id", "run_id", "run_attempt",
        }
        self.assertEqual(set(identity), required)
        self.assertEqual(
            self.historical["hosted_identity"]["receipt_sha256"],
            "110622846e1d42c65801eb7547ea56d783ee275ca48a33f3194b26d6cea1020e",
        )
        self.assertEqual(self.historical["hosted_identity"]["detached_review"], "GREEN")

    def test_partial_rejection_set_cannot_promote_aj03(self) -> None:
        missing = set(self.historical["journeys"]["AJ-03"]["missing"])
        self.assertEqual(missing, {"NON_OWNER"})
        self.assertTrue(all(record["mutation"] is False for record in self.historical["partial_rejection_evidence"]))

    def test_contract_publishes_current_matrix_and_history_boundary(self) -> None:
        contract = CONTRACT.read_text(encoding="utf-8")
        for line in (
            "AJ-01 PROVEN",
            "AJ-02 PROVEN",
            "AJ-03 UNPROVEN",
            "AJ-11 UNPROVEN",
            "AJ-12 UNPROVEN",
        ):
            self.assertIn(line, contract)
        self.assertIn("historical RP-C07 reconciliation remains valid", contract)
        self.assertIn("later controlling transition for AJ-01 only", contract)


if __name__ == "__main__":
    unittest.main()
