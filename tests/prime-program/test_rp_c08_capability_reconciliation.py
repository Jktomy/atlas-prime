from __future__ import annotations

import json
import unittest
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class RpC08CapabilityReconciliationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.register = json.loads((ROOT / "governance/capability-parity-register.json").read_text(encoding="utf-8"))
        self.proof = json.loads((ROOT / "proof/repairing-prime/rp-c08-cap011-reconciliation-r01.json").read_text(encoding="utf-8"))

    def test_exact_28_record_counts_match_proof(self) -> None:
        observed = Counter(record["capability_disposition"] for record in self.register["capabilities"])
        expected = {key: value for key, value in self.proof["capability_counts"].items() if value}
        self.assertEqual(dict(observed), expected)
        self.assertEqual(self.register["capability_disposition_counts"], self.proof["capability_counts"])
        self.assertEqual(sum(observed.values()), 28)

    def test_cap011_is_restored_only_by_live_multifile_evidence(self) -> None:
        records = {record["id"]: record for record in self.register["capabilities"]}
        self.assertEqual(records["CAP-011"]["capability_disposition"], "RESTORED")
        self.assertEqual(records["CAP-011"]["activation_state"], "ACTIVE")
        evidence = self.proof["hosted_multifile_evidence"]
        self.assertEqual(evidence["pull_request"], 147)
        self.assertEqual(evidence["head_sha"], "2766deee39a72db9f942fc6bae6ae87e0ca7a8a9")
        self.assertEqual(len(evidence["authored_paths"]), 2)
        self.assertEqual(evidence["exact_head_ci"]["result"], "GREEN")
        self.assertEqual(evidence["detached_review"], "GREEN")

    def test_guided_fresh_work_and_final_acceptance_boundaries_remain_missing(self) -> None:
        records = {record["id"]: record for record in self.register["capabilities"]}
        self.assertEqual(set(self.proof["still_missing"]), {"CAP-010", "CAP-015", "CAP-027"})
        for identity in self.proof["still_missing"]:
            self.assertEqual(records[identity]["capability_disposition"], "STILL_MISSING")
            self.assertEqual(records[identity]["activation_state"], "MISSING")
        self.assertIn("fresh Work/Athena reachability", records["CAP-015"]["current_state"])

    def test_reconciliation_does_not_self_close(self) -> None:
        self.assertEqual(self.proof["campaign_gate_state"], "IN_PROGRESS")
        self.assertTrue(all(value is False for value in self.proof["forbidden_promotions"].values()))


if __name__ == "__main__":
    unittest.main()
