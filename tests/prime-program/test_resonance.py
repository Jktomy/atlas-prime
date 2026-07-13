from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.athena_routes.schema import SchemaValidationError, validate_schema  # noqa: E402
from tools.resonance.reconcile import ResonanceValidationError, reconcile_findings, stable_json  # noqa: E402


class ResonanceContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fixture = json.loads((ROOT / "proof/repairing-prime/rp-c04-resonance-fixtures-r01.json").read_text(encoding="utf-8"))
        cls.committed = json.loads((ROOT / "proof/repairing-prime/rp-c04-aberration-register-r01.json").read_text(encoding="utf-8"))
        cls.register_schema = json.loads((ROOT / "schemas/aberration-register-v1.schema.json").read_text(encoding="utf-8"))

    def reconcile(self, findings: list[dict] | None = None) -> dict:
        return reconcile_findings(findings or self.fixture["findings"], input_sha256=self.fixture["input_sha256"], register_id=self.fixture["register_id"])

    def test_refract_is_deterministic_and_register_is_closed(self) -> None:
        first = self.reconcile()
        second = self.reconcile(list(reversed(self.fixture["findings"])))
        self.assertEqual(stable_json(first), stable_json(second))
        validate_schema(self.register_schema, first)
        self.assertEqual(first, self.committed)
        extra = dict(first)
        extra["provider_vote"] = True
        with self.assertRaises(SchemaValidationError):
            validate_schema(self.register_schema, extra)

    def test_aberration_register_preserves_consensus_conflict_and_novel(self) -> None:
        records = {record["claim_key"]: record for record in self.reconcile()["records"]}
        self.assertEqual(records["route.boundary"]["classification"], "CONSENSUS")
        self.assertEqual(records["runtime.local"]["classification"], "CONFLICT")
        self.assertEqual(records["provider.neutrality"]["classification"], "NOVEL")
        for record in records.values():
            self.assertEqual(record["disposition"], "OPEN_HUMAN_REVIEW")
            self.assertIsNone(record["human_decision"])
            self.assertFalse(record["athena_refraction"]["is_final"])

    def test_provider_labels_do_not_change_semantic_classification(self) -> None:
        changed = copy.deepcopy(self.fixture["findings"])
        for index, finding in enumerate(changed):
            finding["agent_identity"].update({"provider": f"PROVIDER-{index}", "model": f"MODEL-{index}"})
        baseline = [(item["claim_key"], item["classification"]) for item in self.reconcile()["records"]]
        observed = [(item["claim_key"], item["classification"]) for item in self.reconcile(changed)["records"]]
        self.assertEqual(observed, baseline)

    def test_input_drift_lane_reuse_visibility_and_local_runtime_fail_closed(self) -> None:
        cases = []
        drift = copy.deepcopy(self.fixture["findings"])
        drift[0]["input_sha256"] = "0" * 64
        cases.append((drift, "FINDING_INPUT_MISMATCH"))
        reused = copy.deepcopy(self.fixture["findings"])
        reused[1]["lane_id"] = reused[0]["lane_id"]
        cases.append((reused, "LANE_REUSE_REJECTED"))
        agent_reused = copy.deepcopy(self.fixture["findings"])
        agent_reused[1]["agent_identity"]["agent_id"] = agent_reused[0]["agent_identity"]["agent_id"]
        cases.append((agent_reused, "AGENT_ID_REUSE_REJECTED"))
        warrant_reused = copy.deepcopy(self.fixture["findings"])
        warrant_reused[1]["independence"]["warrant_id"] = warrant_reused[0]["independence"]["warrant_id"]
        cases.append((warrant_reused, "WARRANT_ID_REUSE_REJECTED"))
        visible = copy.deepcopy(self.fixture["findings"])
        visible[0]["independence"]["prior_lane_visibility"] = True
        cases.append((visible, "FINDING_SCHEMA_INVALID"))
        local = copy.deepcopy(self.fixture["findings"])
        local[0]["agent_identity"]["stormlight"] = "LOCAL"
        cases.append((local, "LOCAL_RUNTIME_PROOF_REQUIRED"))
        hybrid = copy.deepcopy(self.fixture["findings"])
        hybrid[0]["agent_identity"]["stormlight"] = "HYBRID"
        cases.append((hybrid, "LOCAL_RUNTIME_PROOF_REQUIRED"))
        evidence = copy.deepcopy(self.fixture["findings"])
        evidence[0]["evidence"][0]["sha256"] = "9" * 64
        cases.append((evidence, "FINDING_EVIDENCE_MISMATCH"))
        for findings, code in cases:
            with self.subTest(code=code), self.assertRaises(ResonanceValidationError) as raised:
                self.reconcile(findings)
            self.assertEqual(raised.exception.code, code)

    def test_local_model_and_promotions_remain_truthfully_blocked(self) -> None:
        register = self.reconcile()
        self.assertEqual(register["local_model"]["status"], "BLOCKED_RUNTIME_PROOF_ABSENT")
        self.assertIsNone(register["local_model"]["runtime_proof_sha256"])
        self.assertEqual(register["local_model"]["finding_ids"], [])
        self.assertEqual(register["promotion"], "NONE")

    def test_doctrine_separates_refract_register_and_athena_refraction(self) -> None:
        contract = " ".join((ROOT / "governance/resonance-reconciliation-contract.md").read_text(encoding="utf-8").split())
        for phrase in ("Refract", "sealed independent findings", "Aberration Register", "Athena Refraction", "providers to vote", "cannot rewrite", "BLOCKED_RUNTIME_PROOF_ABSENT"):
            self.assertIn(phrase, contract)


if __name__ == "__main__":
    unittest.main()
