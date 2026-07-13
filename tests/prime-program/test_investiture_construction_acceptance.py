from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

from tools.athena_routes.schema import validate_schema


ROOT = Path(__file__).resolve().parents[2]
RECORD = ROOT / "proof/found-silverlight/fs-c01-m02-m03-construction-acceptance-r01.json"


class InvestitureConstructionAcceptanceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.record = json.loads(RECORD.read_text(encoding="utf-8"))
        self.schema = json.loads(
            (ROOT / "schemas/investiture-construction-acceptance-v1.schema.json").read_text(encoding="utf-8")
        )

    def test_record_is_closed_schema_valid_and_hash_bound(self) -> None:
        validate_schema(self.schema, self.record)
        for relative, expected in self.record["implementation_hashes"].items():
            actual = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
            self.assertEqual(actual, expected, relative)
        fixture = ROOT / "tests/prime-program/fixtures/investiture-events-v1.json"
        self.assertEqual(hashlib.sha256(fixture.read_bytes()).hexdigest(), self.record["fixture_corpus_sha256"])

    def test_exact_construction_lineage_and_results_are_accepted(self) -> None:
        self.assertEqual(self.record["source_base_sha"], "765e1b29bf315bfcc4a4f039caab28bfb43b806d")
        self.assertEqual(self.record["construction_head_sha"], "aedc1768bcc3ae851d5d75bab4f3c96f6df50a35")
        self.assertEqual(self.record["construction_merge_sha"], "f88dd11875b7891212a05dd7b66f3e11f128526f")
        self.assertEqual(self.record["validation_run_id"], 29282806209)
        self.assertEqual(self.record["detached_review"], "GREEN")
        self.assertEqual(self.record["deterministic_results"]["committed_record_count"], 5)
        self.assertEqual(self.record["deterministic_results"]["known_beu_subtotal"], 29)
        self.assertFalse(self.record["deterministic_results"]["complete_total_available"])
        self.assertEqual(
            self.record["mission_states"],
            {"FS-C01-M02": "PROVEN", "FS-C01-M03": "PROVEN", "FS-C01-M04": "UNPROVEN"},
        )

    def test_live_authority_and_campaign_completion_remain_unclaimed(self) -> None:
        self.assertFalse(self.record["external_store_selected"])
        self.assertFalse(self.record["real_provider_usage_accepted"])
        self.assertEqual(
            self.record["remaining_blocker"],
            "JAYSON_SELECTED_PROTECTED_EXTERNAL_STORE_AND_TRUSTED_PROVIDER_RUNTIME_USAGE_EVIDENCE_REQUIRED",
        )
        proof = (ROOT / "proof/found-silverlight/fs-c01-m02-m03-construction-acceptance-r01.md").read_text(encoding="utf-8")
        self.assertIn("FS-C01-M04` remains `UNPROVEN", proof)
        self.assertIn("temporary exercise store was removed", proof)
        self.assertNotIn("Found Silverlight is complete", proof)


if __name__ == "__main__":
    unittest.main()
