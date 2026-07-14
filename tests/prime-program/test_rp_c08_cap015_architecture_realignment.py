from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARCHITECTURE = ROOT / "governance/athena-route-architecture-r01.md"
PROOF = ROOT / "proof/repairing-prime/rp-c08-cap015-architecture-realignment-r01.json"


class Cap015ArchitectureRealignmentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.text = ARCHITECTURE.read_text(encoding="utf-8")
        self.normalized = " ".join(self.text.split())
        self.proof = json.loads(PROOF.read_text(encoding="utf-8"))

    def test_operator_methods_are_exact(self) -> None:
        for phrase in (
            "Spear is Athena's Thread Engine route",
            "Phoenix Blade is Athena's functional counterpart to Oathbringer",
            "Aegis Break is Athena's direct/adaptive safe method",
            "Arrow/Bow is Jayson and Artemis delegated delivery",
            "each operator wields an exact Sword without Thread Engine",
        ):
            self.assertIn(phrase, self.normalized)
        self.assertNotIn(
            "Phoenix Blade is Athena's direct repository-construction method",
            self.normalized,
        )

    def test_proof_binds_correct_architecture(self) -> None:
        architecture = self.proof["controlling_architecture"]
        self.assertEqual(architecture["athena"]["spear"], "THREAD_ENGINE")
        self.assertEqual(
            architecture["athena"]["phoenix_blade"],
            "WIELD_EXACT_SWORD_NO_THREAD_ENGINE",
        )
        self.assertEqual(
            architecture["athena"]["aegis_break"],
            "DIRECT_GITHUB_NATIVE_OR_OTHER_BOUNDED_SAFE_ROUTE",
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
        self.assertEqual(
            architecture["generated_checkpoint"],
            "POST_MERGE_INFRASTRUCTURE_NOT_OPERATOR_METHOD",
        )

    def test_evidence_and_nonpromotion_are_exact(self) -> None:
        evidence = self.proof["accepted_evidence"]
        self.assertEqual(evidence["RP-C01-M02"]["pull_request"], 50)
        self.assertFalse(evidence["RP-C01-M02"]["thread_engine_dependency"])
        self.assertEqual(evidence["CAP-015"]["pull_request"], 39)
        self.assertEqual(
            evidence["CAP-015"]["corroborating_direct_spear"]["pull_request"],
            102,
        )
        self.assertTrue(evidence["CAP-015"]["thread_engine_dependency"])
        self.assertEqual(evidence["AJ-01"]["state"], "PROVEN")
        self.assertEqual(self.proof["states"]["CAP-027"], "STILL_MISSING")
        for identity in ("AJ-03", "AJ-11", "AJ-12", "CAP-027"):
            self.assertFalse(self.proof["forbidden_promotions"][identity])

    def test_retired_bridge_paths_are_absent(self) -> None:
        for relative in self.proof["retired_experiment"]["removed_paths"]:
            self.assertFalse((ROOT / relative).exists(), relative)


if __name__ == "__main__":
    unittest.main()
