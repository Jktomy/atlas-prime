from __future__ import annotations

import json
import unittest
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class RpC08CapabilityReconciliationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.register = json.loads((ROOT / "governance/capability-parity-register.json").read_text(encoding="utf-8"))
        self.proof = json.loads((ROOT / "proof/repairing-prime/rp-c08-capability-reconciliation-r01.json").read_text(encoding="utf-8"))

    def test_exact_28_record_counts_match_proof(self) -> None:
        observed = Counter(record["capability_disposition"] for record in self.register["capabilities"])
        expected = {key: value for key, value in self.proof["capability_counts"].items() if value}
        self.assertEqual(dict(observed), expected)
        self.assertEqual(self.register["capability_disposition_counts"], self.proof["capability_counts"])
        self.assertEqual(sum(observed.values()), 28)

    def test_only_evidence_backed_capabilities_are_newly_restored(self) -> None:
        self.assertEqual(
            set(self.proof["newly_restored"]),
            {"CAP-002", "CAP-003", "CAP-004", "CAP-005", "CAP-006", "CAP-008", "CAP-009", "CAP-022", "CAP-023"},
        )
        records = {record["id"]: record for record in self.register["capabilities"]}
        self.assertTrue(all(records[identity]["activation_state"] == "ACTIVE" for identity in self.proof["newly_restored"]))

    def test_live_multi_file_and_fresh_work_boundaries_remain_missing(self) -> None:
        records = {record["id"]: record for record in self.register["capabilities"]}
        self.assertEqual(set(self.proof["still_missing"]), {"CAP-010", "CAP-011", "CAP-015", "CAP-027"})
        for identity in self.proof["still_missing"]:
            self.assertEqual(records[identity]["capability_disposition"], "STILL_MISSING")
            self.assertEqual(records[identity]["activation_state"], "MISSING")
        self.assertEqual(self.proof["hosted_intake_evidence"]["live_authored_path_count"], 1)
        self.assertIn("multi-file source-pack journey remains unproven", records["CAP-011"]["current_state"])

    def test_reconciliation_does_not_self_close(self) -> None:
        self.assertEqual(self.proof["campaign_gate_state"], "IN_PROGRESS")
        self.assertTrue(all(value is False for value in self.proof["forbidden_promotions"].values()))


if __name__ == "__main__":
    unittest.main()
