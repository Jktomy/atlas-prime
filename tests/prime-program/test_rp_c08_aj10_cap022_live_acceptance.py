from __future__ import annotations

import json
import unittest
from pathlib import Path

from tools.atlas_lifecycle.projection import compact_context
from tools.atlas_lifecycle.repository import _validate_sunset_feather_bindings, validate_repository


ROOT = Path(__file__).resolve().parents[2]
PROOF = ROOT / "proof/repairing-prime/rp-c08-aj10-cap022-live-acceptance-r03.json"


def contains_key(value, key: str) -> bool:
    if isinstance(value, dict):
        return key in value or any(contains_key(item, key) for item in value.values())
    if isinstance(value, list):
        return any(contains_key(item, key) for item in value)
    return False


class Aj10Cap022LiveAcceptanceCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.proof = json.loads(PROOF.read_text(encoding="utf-8"))
        cls.snapshot = validate_repository(ROOT)

    def records_for(self, invocation: dict) -> list[dict]:
        return [
            json.loads((ROOT / binding["path"]).read_text(encoding="utf-8"))
            for binding in invocation["record_bindings"]
        ]

    def test_candidate_does_not_self_promote(self) -> None:
        self.assertEqual(self.proof["acceptance_state"], "LIVE_TRANSACTION_CANDIDATE")
        self.assertEqual(
            self.proof["current_dispositions"]["AJ-10"],
            "UNPROVEN_PENDING_MERGE_AND_FRESH_CONTEXT_READBACK",
        )
        self.assertEqual(
            self.proof["current_dispositions"]["CAP-022"],
            "STILL_MISSING_PENDING_ACCEPTED_LIVE_JOURNEY",
        )
        self.assertFalse(self.proof["promotion_authorized"])

    def test_each_invocation_has_one_exact_pair(self) -> None:
        self.assertEqual(len(self.proof["invocations"]), 2)
        for invocation in self.proof["invocations"]:
            records = self.records_for(invocation)
            _validate_sunset_feather_bindings(records, record_class="canonical-live-candidate")
            by_schema = {}
            for record in records:
                by_schema.setdefault(record["schema_id"], []).append(record)
            self.assertEqual(len(by_schema["atlas.lifecycle.feather"]), 1)
            self.assertEqual(len(by_schema["atlas.lifecycle.sunset"]), 1)
            self.assertEqual(len(by_schema["atlas.lifecycle.sunrise"]), 1)
            feather = by_schema["atlas.lifecycle.feather"][0]
            sunset = by_schema["atlas.lifecycle.sunset"][0]
            sunrise = by_schema["atlas.lifecycle.sunrise"][0]
            self.assertEqual(sunset["latest_feather_id"], feather["record_id"])
            self.assertEqual(sunrise["sunset_id"], sunset["record_id"])
            self.assertEqual(sunrise["latest_feather_id"], feather["record_id"])

    def test_admitted_quest_adds_checkpoint_and_emberline(self) -> None:
        invocation = next(
            item for item in self.proof["invocations"] if item["scope_type"] == "ADMITTED_QUEST"
        )
        records = self.records_for(invocation)
        schemas = [record["schema_id"] for record in records]
        self.assertEqual(schemas.count("atlas.lifecycle.quest-emberline"), 1)
        self.assertEqual(schemas.count("atlas.lifecycle.quest-checkpoint"), 1)
        feather = next(record for record in records if record["schema_id"] == "atlas.lifecycle.feather")
        context = compact_context(
            self.snapshot,
            quest_id="repairing-prime",
            projection_warning="Generated lifecycle projection awaits post-merge checkpoint.",
        )
        self.assertEqual(context["latest_valid_feather"], feather["record_id"])
        historical_gate = self.proof["fresh_context_readback"]["expected_next_gate"]
        self.assertEqual(
            historical_gate,
            "MERGE_THEN_FRESH_CONTEXT_AJ10_CAP022_READBACK",
        )
        emberline = next(
            record
            for record in self.snapshot.canonical_records
            if record.get("schema_id") == "atlas.lifecycle.quest-emberline"
            and record.get("quest_id") == "repairing-prime"
        )
        self.assertEqual(context["next_gate"], emberline["next_gate"])
        self.assertNotEqual(context["next_gate"], historical_gate)
        qem_binding = next(
            binding
            for binding in invocation["record_bindings"]
            if binding["schema_id"] == "atlas.lifecycle.quest-emberline"
        )
        self.assertEqual(emberline["record_id"], qem_binding["record_id"])

    def test_nonquest_adds_no_quest_identity(self) -> None:
        invocation = next(
            item for item in self.proof["invocations"] if item["scope_type"] == "NON_QUEST"
        )
        records = self.records_for(invocation)
        schemas = [record["schema_id"] for record in records]
        self.assertNotIn("atlas.lifecycle.quest-emberline", schemas)
        self.assertNotIn("atlas.lifecycle.quest-checkpoint", schemas)
        self.assertFalse(contains_key(records, "quest_id"))

    def test_exact_paths_and_ids_are_bound(self) -> None:
        for invocation in self.proof["invocations"]:
            for binding in invocation["record_bindings"]:
                path = ROOT / binding["path"]
                self.assertTrue(path.is_file())
                record = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(record["record_id"], binding["record_id"])
                self.assertEqual(record["schema_id"], binding["schema_id"])


if __name__ == "__main__":
    unittest.main()
