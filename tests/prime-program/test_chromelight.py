from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.athena_routes.schema import SchemaValidationError, validate_schema  # noqa: E402


class ChromelightEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.schema = json.loads((ROOT / "schemas/chromelight-evidence-register-v1.schema.json").read_text(encoding="utf-8"))
        cls.register = json.loads((ROOT / "proof/repairing-prime/rp-c03-chromelight-evidence-r01.json").read_text(encoding="utf-8"))
        cls.evaluations = {item["evaluation_id"]: item for item in cls.register["evaluations"]}

    def test_register_is_closed_and_exactly_covers_chromelight(self) -> None:
        validate_schema(self.schema, self.register)
        self.assertEqual(set(self.evaluations), {"GOOGLE-ELIGIBILITY", "GEMINI-SCOUT", "JULES", "ANTIGRAVITY-SHARDPLATE"})
        extra = dict(self.register)
        extra["provider_token"] = "forbidden"
        with self.assertRaises(SchemaValidationError):
            validate_schema(self.schema, extra)

    def test_sources_are_current_public_official_google_evidence(self) -> None:
        source_ids = {source["source_id"] for source in self.register["sources"]}
        self.assertEqual(len(source_ids), len(self.register["sources"]))
        allowed_hosts = {"developers.google.com", "jules.google", "blog.google", "antigravity.google", "codelabs.developers.google.com"}
        for source in self.register["sources"]:
            self.assertEqual(source["observed_on"], self.register["observed_on"])
            self.assertEqual(urlparse(source["url"]).scheme, "https")
            self.assertIn(urlparse(source["url"]).hostname, allowed_hosts)
        for evaluation in self.evaluations.values():
            self.assertTrue(set(evaluation["evidence_source_ids"]).issubset(source_ids))

    def test_gate_reconciles_evidence_without_provider_or_capability_activation(self) -> None:
        self.assertEqual(self.register["gate_status"], "EVIDENCE_RECONCILED")
        self.assertEqual(self.register["promotion"], "NONE")
        self.assertFalse(self.register["provider_activation"])
        self.assertFalse(self.register["repository_access_granted"])
        self.assertEqual(self.register["operator_account_readback"], "NOT_PERFORMED")
        for evaluation in self.evaluations.values():
            self.assertEqual(evaluation["activation_state"], "NOT_ACTIVATED")
            self.assertFalse(evaluation["mutation_route"])
            self.assertFalse(evaluation["permanence_authority"])
            self.assertTrue(evaluation["blockers"])

    def test_provider_and_atlas_identities_do_not_collapse(self) -> None:
        scout = self.evaluations["GEMINI-SCOUT"]
        self.assertEqual(scout["availability"], "ATLAS_ROLE_ONLY")
        self.assertNotEqual(scout["provider_surface"], scout["atlas_role"])
        self.assertEqual(scout["disposition"], "ROLE_DEFINED_SURFACE_UNSELECTED")
        jules = self.evaluations["JULES"]
        self.assertTrue(jules["account_action_required"])
        self.assertTrue(jules["repository_access_required"])
        antigravity = self.evaluations["ANTIGRAVITY-SHARDPLATE"]
        self.assertEqual(antigravity["atlas_role"], "Shardplate")
        self.assertEqual(antigravity["surface_class"], "AI_ASSISTED_WORK_SURFACE")

    def test_doctrine_requires_new_approval_before_external_action(self) -> None:
        contract = (ROOT / "governance/chromelight-provider-boundary.md").read_text(encoding="utf-8")
        normalized = " ".join(contract.split())
        for phrase in ("not provider enrollment", "Gemini Scout", "explicit selection of repositories", "never the delivery route", "No login", "new exact agentic warrant"):
            self.assertIn(phrase, normalized)
        self.assertGreaterEqual(len(self.register["unresolved_external_actions"]), 4)


if __name__ == "__main__":
    unittest.main()
