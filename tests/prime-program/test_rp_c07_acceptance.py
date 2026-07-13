from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PROOF = ROOT / "proof/repairing-prime/rp-c07-acceptance-reconciliation-r01.json"
CONTRACT = ROOT / "governance/capability-acceptance-contract.md"


class RpC07AcceptanceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.proof = json.loads(PROOF.read_text(encoding="utf-8"))

    def test_every_journey_has_one_controlling_disposition(self) -> None:
        self.assertEqual(set(self.proof["journeys"]), {f"AJ-{index:02d}" for index in range(1, 13)})
        states = {identity: record["state"] for identity, record in self.proof["journeys"].items()}
        self.assertEqual(set(states.values()), {"PROVEN", "UNPROVEN"})
        self.assertEqual(states["AJ-01"], "UNPROVEN")
        self.assertEqual(states["AJ-02"], "PROVEN")
        self.assertEqual(states["AJ-03"], "UNPROVEN")
        self.assertEqual(states["AJ-11"], "UNPROVEN")
        self.assertEqual(states["AJ-12"], "UNPROVEN")
        for identity in (f"AJ-{index:02d}" for index in range(4, 11)):
            self.assertEqual(states[identity], "PROVEN")

    def test_hosted_identity_is_fully_separated(self) -> None:
        identity = self.proof["hosted_identity"]["identity"]
        required = {
            "authorizer", "event_actor", "triggering_actor", "workflow_ref",
            "workflow_source_sha", "credential_principal", "token_mode",
            "mission_id", "run_id", "run_attempt",
        }
        self.assertEqual(set(identity), required)
        self.assertEqual(self.proof["hosted_identity"]["receipt_sha256"], "110622846e1d42c65801eb7547ea56d783ee275ca48a33f3194b26d6cea1020e")
        self.assertEqual(self.proof["hosted_identity"]["detached_review"], "GREEN")

    def test_partial_rejection_set_cannot_promote_aj03(self) -> None:
        missing = set(self.proof["journeys"]["AJ-03"]["missing"])
        self.assertEqual(missing, {"NON_OWNER", "EDITED_INPUT", "REPLAY", "DUPLICATE_BRANCH", "DUPLICATE_PR"})
        self.assertTrue(all(record["mutation"] is False for record in self.proof["partial_rejection_evidence"]))

    def test_final_main_journeys_remain_unproven(self) -> None:
        self.assertEqual(self.proof["historical_clean_clone"]["state"], "REGRESSION_EVIDENCE_NOT_FINAL_AJ11_ACCEPTANCE")
        self.assertFalse(self.proof["historical_clean_clone"]["normal_codex_dependency"])
        self.assertEqual(self.proof["capability_promotion"], "NONE")
        self.assertEqual(
            self.proof["forbidden_promotions"],
            {"RP-C01_COMPLETE": False, "QUEST_COMPLETE": False, "CAP_027_ACTIVE": False, "permanence_granted": False, "standing_authority": False},
        )

    def test_contract_repeats_the_canonical_matrix(self) -> None:
        contract = CONTRACT.read_text(encoding="utf-8")
        for identity, record in self.proof["journeys"].items():
            self.assertIn(f"{identity} {record['state']}", contract)


if __name__ == "__main__":
    unittest.main()
