from __future__ import annotations

import hashlib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class InvestitureSourceIdentityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.contract = (ROOT / "governance/investiture-source-identity-contract.md").read_text(encoding="utf-8")
        self.normalized = " ".join(self.contract.split())

    def test_exact_lights_and_beu_mapping_are_canonical(self) -> None:
        for provider, light in (
            ("OpenAI model token", "`Spirallight`"),
            ("Google model token", "`Chromelight`"),
            ("Atlas-controlled local-model token", "`Emberlight`"),
        ):
            self.assertIn(f"| {provider} | {light} |", self.contract)
        self.assertIn("One trusted provider/runtime-reported model token equals one BEU", self.normalized)
        for rule in (
            "1 OpenAI model token = 1 BEU of Spirallight",
            "1 Google model token = 1 BEU of Chromelight",
            "1 Atlas-controlled local-model token = 1 BEU of Emberlight",
            "Total Investiture BEU is the arithmetic sum of all non-overlapping Spirallight, Chromelight, and Emberlight entries",
        ):
            self.assertIn(rule, self.normalized)
        for forbidden in ("Spiral Light", "SpiralLight", "Chrome light", "Ember Light"):
            self.assertNotIn(forbidden, self.contract)

    def test_overlap_mixed_provider_zero_and_unavailable_are_fail_closed(self) -> None:
        for phrase in (
            "exactly one non-overlapping entry and one Light",
            "Mixed-provider work uses separate entries",
            "There is no hybrid Light",
            "either one trusted authoritative total or a declared set of disjoint leaf categories",
            "never added again",
            "`UNAVAILABLE`; they are never inferred as zero",
            "Deterministic non-model work has no Light and consumes exactly zero BEU",
            "not Emberlight",
        ):
            self.assertIn(phrase, self.normalized)

    def test_operational_identity_and_authority_do_not_collapse_into_lights(self) -> None:
        for identity in (
            "human authorizer and operator",
            "provider and model",
            "runtime and Atlas runtime-control status",
            "AI-assisted work surface",
            "delivery route and launcher",
            "repository engine and substrate",
            "credential principal and token mode",
            "exact candidate and permanence authority",
        ):
            self.assertIn(identity, self.contract)
        self.assertIn("Shardplate and Shardblade are operational concepts, never Lights", self.normalized)

    def test_stormlight_is_legacy_only_and_chromelight_does_not_activate_google(self) -> None:
        self.assertIn("`Stormlight` is retired as the active accounting-system and model-source identity name", self.normalized)
        self.assertIn("must not emit a `stormlight` field", self.normalized)
        self.assertIn("Only trusted reported Google model tokens do", self.normalized)
        for path in (
            "operations/protocol-library.md",
            "governance/change-routes.md",
            "methods/phoenix-blade.md",
        ):
            active = (ROOT / path).read_text(encoding="utf-8")
            self.assertNotIn("Stormlight identifies", active)
            self.assertNotIn("Stormlight: CLOUD, LOCAL, HYBRID, or NONE", active)

    def test_accepted_v1_schemas_and_proofs_remain_byte_identical(self) -> None:
        expected = {
            "schemas/chromelight-evidence-register-v1.schema.json": "2431aa1f6f8eb7c422a6fbae0b010e1bf8b35a849d78637a6c74c557db28e9e9",
            "schemas/resonance-finding-v1.schema.json": "3cd57f3e93f13efa692f95441fb130b8a5db53763265463ff70d9b7885fd8a06",
            "schemas/aberration-register-v1.schema.json": "f2d797171c60e54b8ea97590887cca1d66e25863149da7545ec8f87e76e04b17",
            "proof/repairing-prime/rp-c03-chromelight-evidence-r01.json": "cd812b216688e64d036de873014b2c6b9c5d9222d65a3ccf03ff8f6cceaf84f9",
            "proof/repairing-prime/rp-c04-resonance-fixtures-r01.json": "5dbf825866cb748e906d1e154a40de883d9444ffc1f9accd7c3dcefd5a378796",
            "proof/repairing-prime/rp-c04-aberration-register-r01.json": "57882e89460c9c7d99914cd97436f4cdc1f143d3c0594693be2da1215678c9d9",
        }
        observed = {path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest() for path in expected}
        self.assertEqual(observed, expected)


if __name__ == "__main__":
    unittest.main()
