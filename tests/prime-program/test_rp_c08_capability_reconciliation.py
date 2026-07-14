from __future__ import annotations

import json
import unittest
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CURRENT_PROOF = (
    ROOT
    / "proof/repairing-prime/"
    "rp-c08-cap015-architecture-realignment-r01.json"
)


class RpC08CapabilityReconciliationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.register = json.loads(
            (ROOT / "governance/capability-parity-register.json").read_text(
                encoding="utf-8"
            )
        )
        self.proof = json.loads(CURRENT_PROOF.read_text(encoding="utf-8"))
        self.records = {
            record["id"]: record for record in self.register["capabilities"]
        }

    def test_exact_28_record_counts_match_current_proof(self) -> None:
        observed = Counter(
            record["capability_disposition"]
            for record in self.register["capabilities"]
        )
        expected = {
            key: value
            for key, value in self.proof["capability_counts"].items()
            if value
        }
        self.assertEqual(dict(observed), expected)
        self.assertEqual(
            self.register["capability_disposition_counts"],
            self.proof["capability_counts"],
        )
        self.assertEqual(sum(observed.values()), 28)

    def test_cap015_is_restored_only_by_accepted_direct_spear_evidence(self) -> None:
        cap015 = self.records["CAP-015"]
        evidence = self.proof["accepted_evidence"]["CAP-015"]
        self.assertEqual(cap015["capability_disposition"], "RESTORED")
        self.assertEqual(cap015["activation_state"], "ACTIVE")
        self.assertEqual(evidence["route"], "SPEAR")
        self.assertEqual(evidence["pull_request"], 39)
        self.assertEqual(
            evidence["head_sha"],
            "1f60f0496eca94fe97071217a04b8bdf70004b64",
        )
        self.assertEqual(evidence["validation_run"], 29056870868)
        self.assertEqual(evidence["ubuntu"], "GREEN")
        self.assertEqual(evidence["windows"], "GREEN")
        self.assertTrue(evidence["thread_engine_dependency"])
        self.assertEqual(
            evidence["corroborating_direct_spear"]["pull_request"],
            102,
        )

    def test_m02_is_proven_only_by_accepted_phoenix_blade_evidence(self) -> None:
        evidence = self.proof["accepted_evidence"]["RP-C01-M02"]
        self.assertEqual(evidence["state"], "PROVEN")
        self.assertEqual(evidence["route"], "PHOENIX_BLADE")
        self.assertEqual(evidence["pull_request"], 50)
        self.assertEqual(
            evidence["head_sha"],
            "d26927cb0663afe71775dbfd35df2b3fc49ad21b",
        )
        self.assertEqual(evidence["validation_run"], 29070149639)
        self.assertEqual(evidence["ubuntu"], "GREEN")
        self.assertEqual(evidence["windows"], "GREEN")
        self.assertFalse(evidence["thread_engine_dependency"])

    def test_aj01_is_currently_proven_as_athena_spear(self) -> None:
        evidence = self.proof["accepted_evidence"]["AJ-01"]
        self.assertEqual(evidence["state"], "PROVEN")
        self.assertEqual(evidence["journey"], "ATHENA_SPEAR_SUBMISSION")
        self.assertEqual(self.proof["current_journeys"]["AJ-01"], "PROVEN")
        for identity in ("AJ-03", "AJ-11", "AJ-12"):
            self.assertEqual(
                self.proof["current_journeys"][identity],
                "UNPROVEN",
            )

    def test_operator_routes_are_exact_and_not_conflated(self) -> None:
        architecture = self.proof["controlling_architecture"]
        self.assertEqual(
            architecture["athena"],
            {
                "spear": "THREAD_ENGINE",
                "phoenix_blade": "WIELD_EXACT_SWORD_NO_THREAD_ENGINE",
                "aegis_break": "DIRECT_GITHUB_NATIVE_OR_OTHER_BOUNDED_SAFE_ROUTE",
            },
        )
        self.assertEqual(
            architecture["jayson_artemis"]["arrow_bow"],
            "DELEGATED_THREAD_ENGINE_DELIVERY",
        )
        self.assertEqual(
            architecture["jayson"]["oathbringer"],
            "WIELD_EXACT_SWORD_NO_THREAD_ENGINE",
        )
        self.assertFalse(architecture["platform_origin_attestation_required"])
        self.assertFalse(architecture["external_bridge_required"])
        self.assertFalse(architecture["user_run_python_required"])
        self.assertFalse(architecture["user_run_powershell_required"])

    def test_retired_origin_experiment_is_absent(self) -> None:
        retired = self.proof["retired_experiment"]
        self.assertEqual(
            retired["classification"],
            "SUPERSEDED_HISTORICAL_ONLY",
        )
        self.assertFalse(retired["active_route"])
        self.assertFalse(retired["capability_gate"])
        self.assertFalse(retired["blocker"])
        for relative in retired["removed_paths"]:
            self.assertFalse((ROOT / relative).exists(), relative)

    def test_reconciliation_does_not_self_close(self) -> None:
        self.assertEqual(self.proof["states"]["RP-C01"], "IN_PROGRESS")
        self.assertEqual(self.proof["states"]["RP-C08"], "IN_PROGRESS")
        self.assertEqual(
            self.proof["states"]["QUEST-REPAIRING-PRIME-R01"],
            "IN_PROGRESS",
        )
        self.assertEqual(
            self.proof["states"]["CAP-027"],
            "STILL_MISSING",
        )
        self.assertTrue(
            all(
                value is False
                for value in self.proof["forbidden_promotions"].values()
            )
        )


if __name__ == "__main__":
    unittest.main()
