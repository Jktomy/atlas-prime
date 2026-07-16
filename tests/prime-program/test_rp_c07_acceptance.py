from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
HISTORICAL_PROOF = ROOT / "proof/repairing-prime/rp-c07-acceptance-reconciliation-r01.json"
AJ01_PROOF = ROOT / "proof/repairing-prime/rp-c08-cap015-architecture-realignment-r02.json"
AJ03_PROOF = ROOT / "proof/repairing-prime/rp-c01-m07-non-owner-acceptance-r01.json"
AJ11_PROOF = ROOT / "proof/repairing-prime/rp-c08-aj11-clean-clone-acceptance-r08.json"
AJ12_PROOF = ROOT / "proof/repairing-prime/rp-c08-aj12-merged-main-validation-acceptance-r01.json"
CAP027_PROOF = ROOT / "proof/repairing-prime/rp-c08-cap027-final-capability-reconciliation-r01.json"
CONTRACT = ROOT / "governance/capability-acceptance-contract.md"


class RpC07AcceptanceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.historical = json.loads(HISTORICAL_PROOF.read_text(encoding="utf-8"))
        self.aj01 = json.loads(AJ01_PROOF.read_text(encoding="utf-8"))
        self.aj03 = json.loads(AJ03_PROOF.read_text(encoding="utf-8"))
        self.aj11 = json.loads(AJ11_PROOF.read_text(encoding="utf-8"))
        self.aj12 = json.loads(AJ12_PROOF.read_text(encoding="utf-8"))
        self.cap027 = json.loads(CAP027_PROOF.read_text(encoding="utf-8"))

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

    def test_later_reconciliations_advance_journeys_and_cap027_separately(self) -> None:
        self.assertEqual(self.aj01["transitions"]["AJ-01"]["to"], "PROVEN")
        self.assertIn("AJ-03", self.aj01["preserved_open"])
        self.assertEqual(self.aj03["transitions"]["AJ-03"], {"from": "UNPROVEN", "to": "PROVEN"})
        self.assertEqual(self.aj03["acceptance_journey_state"], "PROVEN")
        self.assertIn("AJ-11", self.aj03["remaining_open"])
        self.assertIn("AJ-12", self.aj03["remaining_open"])
        self.assertEqual(self.aj11["transitions"]["AJ-11"], {"from": "UNPROVEN", "to": "PROVEN"})
        self.assertEqual(self.aj11["preserved_open"], ["AJ-12", "CAP-027", "RP-C08", "QUEST-REPAIRING-PRIME-R01"])
        self.assertEqual(self.aj12["transitions"]["AJ-12"], {"from": "UNPROVEN", "to": "PROVEN"})
        self.assertEqual(self.cap027["transitions"]["CAP-027"], {"from": "STILL_MISSING/MISSING", "to": "RESTORED/ACTIVE"})
        self.assertTrue(all(value is False for value in self.aj03["forbidden_promotions"].values()))
        self.assertTrue(all(value is False for value in self.aj11["forbidden_promotions"].values()))
        self.assertTrue(all(value is False for value in self.aj12["forbidden_promotions"].values()))
        self.assertTrue(all(value is False for value in self.cap027["forbidden_promotions"].values()))

    def test_hosted_identity_is_fully_separated(self) -> None:
        identity = self.historical["hosted_identity"]["identity"]
        required = {
            "authorizer", "event_actor", "triggering_actor", "workflow_ref",
            "workflow_source_sha", "credential_principal", "token_mode",
            "mission_id", "run_id", "run_attempt",
        }
        self.assertEqual(set(identity), required)
        self.assertEqual(self.historical["hosted_identity"]["receipt_sha256"], "110622846e1d42c65801eb7547ea56d783ee275ca48a33f3194b26d6cea1020e")
        self.assertEqual(self.historical["hosted_identity"]["detached_review"], "GREEN")

    def test_partial_rejection_set_remains_historical(self) -> None:
        self.assertEqual(set(self.historical["journeys"]["AJ-03"]["missing"]), {"NON_OWNER"})
        self.assertTrue(all(record["mutation"] is False for record in self.historical["partial_rejection_evidence"]))

    def test_contract_publishes_current_matrix_and_history_boundary(self) -> None:
        contract = CONTRACT.read_text(encoding="utf-8")
        for line in (
            "AJ-01 PROVEN",
            "AJ-02 PROVEN",
            "AJ-03 PROVEN",
            "AJ-11 PROVEN",
            "AJ-12 PROVEN",
            "CAP-027 RESTORED / ACTIVE",
        ):
            self.assertIn(line, contract)
        self.assertIn("historical RP-C07 reconciliation remains valid", contract)
        self.assertIn("later controlling transition for AJ-01 only", contract)
        self.assertIn("later controlling transition for AJ-03", contract)
        self.assertIn("controlling transition for AJ-11 only", contract)
        self.assertIn("controlling transition for AJ-12 only", contract)
        self.assertIn("controlling transition for CAP-027", contract)


if __name__ == "__main__":
    unittest.main()
