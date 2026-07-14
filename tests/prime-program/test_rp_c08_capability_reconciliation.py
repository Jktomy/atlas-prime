from __future__ import annotations

import json
import unittest
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class RpC08CapabilityReconciliationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.register = json.loads(
            (ROOT / "governance/capability-parity-register.json").read_text(encoding="utf-8")
        )
        self.proof = json.loads(
            (ROOT / "proof/repairing-prime/rp-c08-cap015-architecture-realignment-r02.json").read_text(
                encoding="utf-8"
            )
        )
        self.cap010 = json.loads(
            (ROOT / "proof/repairing-prime/rp-c08-cap010-reconciliation-r01.json").read_text(
                encoding="utf-8"
            )
        )
        self.cap011 = json.loads(
            (ROOT / "proof/repairing-prime/rp-c08-cap011-reconciliation-r01.json").read_text(
                encoding="utf-8"
            )
        )
        self.records = {record["id"]: record for record in self.register["capabilities"]}

    def test_exact_28_record_counts_match_controlling_proof(self) -> None:
        observed = Counter(record["capability_disposition"] for record in self.register["capabilities"])
        expected = {key: value for key, value in self.proof["capability_counts"].items() if value}
        self.assertEqual(dict(observed), expected)
        self.assertEqual(self.register["capability_disposition_counts"], self.proof["capability_counts"])
        self.assertEqual(sum(observed.values()), 28)

    def test_cap011_remains_restored_by_live_multifile_evidence(self) -> None:
        self.assertEqual(self.records["CAP-011"]["capability_disposition"], "RESTORED")
        evidence = self.cap011["hosted_multifile_evidence"]
        self.assertEqual(evidence["pull_request"], 147)
        self.assertEqual(evidence["head_sha"], "2766deee39a72db9f942fc6bae6ae87e0ca7a8a9")
        self.assertEqual(evidence["exact_head_ci"]["result"], "GREEN")
        self.assertEqual(evidence["detached_review"], "GREEN")

    def test_cap010_remains_restored_by_guided_live_evidence(self) -> None:
        self.assertEqual(self.records["CAP-010"]["capability_disposition"], "RESTORED")
        construction = self.cap010["guided_publisher_construction"]
        evidence = self.cap010["guided_live_evidence"]
        self.assertEqual(construction["pull_request"], 150)
        self.assertEqual(construction["exact_head_ci"]["result"], "GREEN")
        self.assertEqual(evidence["pull_request"], 151)
        self.assertEqual(evidence["head_sha"], "337d86615594b6c8b07cd474b8d23ddc032b2c42")
        self.assertEqual(evidence["detached_review"], "GREEN")

    def test_cap015_aj01_and_m02_are_reconciled_only(self) -> None:
        self.assertEqual(self.records["CAP-015"]["capability_disposition"], "RESTORED")
        self.assertEqual(self.records["CAP-015"]["activation_state"], "ACTIVE")
        self.assertEqual(self.proof["transitions"]["AJ-01"]["to"], "PROVEN")
        self.assertEqual(self.proof["transitions"]["RP-C01-M02"]["to"], "PROVEN")
        self.assertEqual(self.proof["accepted_evidence"]["direct_spear"]["pull_request"], 102)
        self.assertFalse(self.proof["superseded_premise"]["platform_attestation_required"])

    def test_only_cap027_remains_missing(self) -> None:
        missing = [record["id"] for record in self.register["capabilities"] if record["capability_disposition"] == "STILL_MISSING"]
        self.assertEqual(missing, ["CAP-027"])
        self.assertEqual(self.records["CAP-027"]["activation_state"], "MISSING")

    def test_reconciliation_does_not_self_close(self) -> None:
        self.assertEqual(self.proof["campaign_state"]["RP-C01"], "IN_PROGRESS")
        self.assertEqual(self.proof["campaign_state"]["RP-C08"], "IN_PROGRESS")
        self.assertEqual(self.proof["campaign_state"]["repairing_prime"], "IN_PROGRESS")
        self.assertTrue(all(value is False for value in self.proof["forbidden_promotions"].values()))
        self.assertEqual(
            set(self.proof["preserved_open"]),
            {
                "RP-C01-M06",
                "RP-C01-M07",
                "AJ-03",
                "CAP-027",
                "AJ-11",
                "AJ-12",
                "RP-C01",
                "RP-C08",
                "QUEST-REPAIRING-PRIME-R01",
            },
        )


if __name__ == "__main__":
    unittest.main()
