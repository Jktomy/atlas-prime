from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
HISTORICAL_PROOF = (
    ROOT
    / "proof/repairing-prime/"
    "rp-c07-acceptance-reconciliation-r01.json"
)
CURRENT_PROOF = (
    ROOT
    / "proof/repairing-prime/"
    "rp-c08-cap015-architecture-realignment-r01.json"
)
CONTRACT = ROOT / "governance/capability-acceptance-contract.md"


class RpC07AcceptanceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.historical = json.loads(
            HISTORICAL_PROOF.read_text(encoding="utf-8")
        )
        self.current = json.loads(CURRENT_PROOF.read_text(encoding="utf-8"))

    def test_historical_rp_c07_reconciliation_remains_immutable_context(self) -> None:
        self.assertEqual(
            set(self.historical["journeys"]),
            {f"AJ-{index:02d}" for index in range(1, 13)},
        )
        self.assertEqual(
            self.historical["journeys"]["AJ-01"]["state"],
            "UNPROVEN",
        )
        self.assertEqual(
            self.historical["campaign_gate_state"],
            "ACCEPTED",
        )

    def test_current_controlling_dispositions_apply_only_explicit_override(self) -> None:
        states = self.current["current_journeys"]
        self.assertEqual(
            set(states),
            {f"AJ-{index:02d}" for index in range(1, 13)},
        )
        self.assertEqual(states["AJ-01"], "PROVEN")
        self.assertEqual(states["AJ-02"], "PROVEN")
        self.assertEqual(states["AJ-03"], "UNPROVEN")
        self.assertEqual(states["AJ-11"], "UNPROVEN")
        self.assertEqual(states["AJ-12"], "UNPROVEN")
        for identity in (f"AJ-{index:02d}" for index in range(4, 11)):
            self.assertEqual(states[identity], "PROVEN")

    def test_hosted_identity_is_still_fully_separated(self) -> None:
        identity = self.historical["hosted_identity"]["identity"]
        required = {
            "authorizer",
            "event_actor",
            "triggering_actor",
            "workflow_ref",
            "workflow_source_sha",
            "credential_principal",
            "token_mode",
            "mission_id",
            "run_id",
            "run_attempt",
        }
        self.assertEqual(set(identity), required)
        self.assertEqual(
            self.historical["hosted_identity"]["receipt_sha256"],
            "110622846e1d42c65801eb7547ea56d783ee275ca48a33f3194b26d6cea1020e",
        )
        self.assertEqual(
            self.historical["hosted_identity"]["detached_review"],
            "GREEN",
        )

    def test_partial_rejection_set_cannot_promote_aj03(self) -> None:
        missing = set(self.historical["journeys"]["AJ-03"]["missing"])
        self.assertEqual(missing, {"NON_OWNER"})
        self.assertTrue(
            all(
                record["mutation"] is False
                for record in self.historical["partial_rejection_evidence"]
            )
        )
        self.assertEqual(
            self.current["current_journeys"]["AJ-03"],
            "UNPROVEN",
        )

    def test_final_main_journeys_and_cap027_remain_unproven(self) -> None:
        self.assertEqual(
            self.current["current_journeys"]["AJ-11"],
            "UNPROVEN",
        )
        self.assertEqual(
            self.current["current_journeys"]["AJ-12"],
            "UNPROVEN",
        )
        self.assertEqual(
            self.current["states"]["CAP-027"],
            "STILL_MISSING",
        )
        self.assertFalse(self.current["forbidden_promotions"]["CAP-027"])
        self.assertFalse(self.current["forbidden_promotions"]["QUEST_COMPLETE"])

    def test_contract_repeats_the_current_canonical_matrix(self) -> None:
        contract = CONTRACT.read_text(encoding="utf-8")
        for identity, state in self.current["current_journeys"].items():
            self.assertIn(f"{identity} {state}", contract)


if __name__ == "__main__":
    unittest.main()
