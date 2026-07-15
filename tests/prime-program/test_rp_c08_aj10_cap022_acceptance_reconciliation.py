from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

from tools.atlas_lifecycle.projection import compact_context
from tools.atlas_lifecycle.repository import validate_repository


ROOT = Path(__file__).resolve().parents[2]
PROOF_PATH = ROOT / "proof/repairing-prime/rp-c08-aj10-cap022-acceptance-reconciliation-r04.json"
LIVE_PATH = ROOT / "proof/repairing-prime/rp-c08-aj10-cap022-live-acceptance-r03.json"
TRUTH_PATH = ROOT / "proof/repairing-prime/rp-c08-sunset-feather-truth-reconciliation-r03.json"


def contains_key(value, key: str) -> bool:
    if isinstance(value, dict):
        return key in value or any(contains_key(item, key) for item in value.values())
    if isinstance(value, list):
        return any(contains_key(item, key) for item in value)
    return False


class Aj10Cap022AcceptanceReconciliationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.proof = json.loads(PROOF_PATH.read_text(encoding="utf-8"))
        cls.live = json.loads(LIVE_PATH.read_text(encoding="utf-8"))
        cls.truth = json.loads(TRUTH_PATH.read_text(encoding="utf-8"))
        cls.register = json.loads(
            (ROOT / "governance/capability-parity-register.json").read_text(encoding="utf-8")
        )
        cls.continuity = json.loads(
            (ROOT / "continuity/prime-continuity-register-r01.json").read_text(encoding="utf-8")
        )
        cls.snapshot = validate_repository(ROOT)

    def load_bindings(self, scope: str) -> list[dict]:
        return [
            json.loads((ROOT / binding["path"]).read_text(encoding="utf-8"))
            for binding in self.proof["accepted_record_bindings"][scope]
        ]

    def test_exact_live_and_generated_prerequisites_are_bound(self) -> None:
        live = self.proof["accepted_live_transaction"]
        self.assertEqual(live["pull_request"], 193)
        self.assertEqual(live["head_sha"], "27717f23258d6a6307fa9099ca701e7b15e02d4b")
        self.assertEqual(live["merge_sha"], "8023622a7f3076a1a4a01b487b1693c415d66026")
        self.assertEqual(live["exact_head_ci"]["run"], 29354950823)
        self.assertEqual(live["exact_head_ci"]["result"], "GREEN")
        self.assertEqual(live["detached_strikeforce_r04"], "GREEN")
        generated = self.proof["prerequisite_generated_state"]
        self.assertEqual(generated["generated_pull_request"], 197)
        self.assertEqual(generated["generated_head_sha"], "85fc5b5c51b0640508c8a4e68a8c36d81645f55c")
        self.assertEqual(generated["generated_merge_sha"], self.proof["transaction_base_sha"])
        self.assertEqual(generated["post_merge_noop"]["workflow_run"], 29374547844)
        self.assertEqual(generated["post_merge_noop"]["result"], "NOOP")
        self.assertEqual(generated["post_merge_noop"]["changed_count"], 0)
        self.assertTrue(generated["post_merge_noop"]["byte_identical"])

    def test_all_eight_immutable_record_hashes_and_ids_match(self) -> None:
        for scope in ("admitted_quest", "nonquest"):
            for binding in self.proof["accepted_record_bindings"][scope]:
                path = ROOT / binding["path"]
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), binding["sha256"])
                self.assertEqual(json.loads(path.read_text(encoding="utf-8"))["record_id"], binding["record_id"])

    def test_admitted_quest_resolves_one_exact_pair_and_quest_state(self) -> None:
        records = self.load_bindings("admitted_quest")
        by_schema: dict[str, list[dict]] = {}
        for record in records:
            by_schema.setdefault(record["schema_id"], []).append(record)
        self.assertEqual({key: len(value) for key, value in by_schema.items()}, {
            "atlas.lifecycle.feather": 1,
            "atlas.lifecycle.sunset": 1,
            "atlas.lifecycle.sunrise": 1,
            "atlas.lifecycle.quest-checkpoint": 1,
            "atlas.lifecycle.quest-emberline": 1,
        })
        feather = by_schema["atlas.lifecycle.feather"][0]
        sunset = by_schema["atlas.lifecycle.sunset"][0]
        sunrise = by_schema["atlas.lifecycle.sunrise"][0]
        checkpoint = by_schema["atlas.lifecycle.quest-checkpoint"][0]
        emberline = by_schema["atlas.lifecycle.quest-emberline"][0]
        self.assertEqual(sunset["latest_feather_id"], feather["record_id"])
        self.assertEqual(sunrise["sunset_id"], sunset["record_id"])
        self.assertEqual(sunrise["latest_feather_id"], feather["record_id"])
        self.assertEqual(checkpoint["feather_id"], feather["record_id"])
        self.assertEqual(checkpoint["emberline_id"], emberline["record_id"])
        self.assertEqual(emberline["latest_feather_id"], feather["record_id"])
        self.assertEqual(emberline["next_gate"], self.proof["fresh_context_readback"]["next_gate"])
        context = compact_context(
            self.snapshot,
            quest_id="repairing-prime",
            projection_warning="Non-authoritative lifecycle website projection is missing.",
        )
        self.assertEqual(context["latest_valid_feather"], feather["record_id"])
        self.assertEqual(context["next_gate"], emberline["next_gate"])

    def test_nonquest_arm_invents_no_quest_identity(self) -> None:
        records = self.load_bindings("nonquest")
        schemas = [record["schema_id"] for record in records]
        self.assertEqual(schemas.count("atlas.lifecycle.feather"), 1)
        self.assertEqual(schemas.count("atlas.lifecycle.sunset"), 1)
        self.assertEqual(schemas.count("atlas.lifecycle.sunrise"), 1)
        self.assertNotIn("atlas.lifecycle.quest-checkpoint", schemas)
        self.assertNotIn("atlas.lifecycle.quest-emberline", schemas)
        self.assertFalse(contains_key(records, "quest_id"))

    def test_only_authorized_dispositions_transition(self) -> None:
        self.assertEqual(set(self.proof["transitions"]), {"AJ-10", "CAP-022", "RP-C05"})
        self.assertEqual(self.proof["transitions"]["AJ-10"], {"from": "UNPROVEN", "to": "PROVEN"})
        self.assertEqual(
            self.proof["transitions"]["CAP-022"],
            {"from": "STILL_MISSING/MISSING", "to": "RESTORED/ACTIVE"},
        )
        self.assertEqual(self.proof["transitions"]["RP-C05"], {"from": "PARTIAL", "to": "COMPLETE"})
        self.assertTrue(all(value is False for value in self.proof["forbidden_promotions"].values()))
        missing = [
            record["id"]
            for record in self.register["capabilities"]
            if record["capability_disposition"] == "STILL_MISSING"
        ]
        self.assertEqual(missing, ["CAP-027"])

    def test_historical_pre_acceptance_records_remain_truthful(self) -> None:
        for artifact in self.proof["historical_evidence"]["immutable_artifacts"]:
            self.assertEqual(
                hashlib.sha256((ROOT / artifact["path"]).read_bytes()).hexdigest(),
                artifact["sha256"],
            )
        self.assertEqual(self.live["acceptance_state"], "LIVE_TRANSACTION_CANDIDATE")
        self.assertFalse(self.live["promotion_authorized"])
        self.assertEqual(self.truth["current_dispositions"]["AJ-10"], "UNPROVEN")
        self.assertEqual(self.truth["current_dispositions"]["RP-C05"], "PARTIAL")
        self.assertTrue(self.proof["historical_evidence"]["historical_records_remain_immutable"])

    def test_continuity_preserves_gate_three_and_advances_through_gate_four(self) -> None:
        repairing = next(
            entry
            for entry in self.continuity["entries"]
            if entry["continuity_id"] == "CONT-REPAIRING-PRIME-R01"
        )
        gate_three_event = "RP-C08-AJ10-CAP022-ACCEPTANCE-RECONCILIATION-R04"
        gate_four_event = "RP-C01-M06-PROTECTED-DISPATCH-ACCEPTANCE-R04"
        self.assertEqual(self.continuity["register_revision"], 24)
        self.assertEqual(
            self.continuity["source_base_sha"],
            "91f4392880b7a76f675c933aa429e9f10d1c740e",
        )
        self.assertEqual(self.continuity["event_ids"].count(gate_three_event), 1)
        self.assertEqual(self.continuity["event_ids"].count(gate_four_event), 1)
        self.assertLess(
            self.continuity["event_ids"].index(gate_three_event),
            self.continuity["event_ids"].index(gate_four_event),
        )
        self.assertEqual(repairing["last_event_id"], gate_four_event)
        self.assertEqual(repairing["revision"], 19)
        self.assertEqual(
            repairing["quest_source_sha256"],
            hashlib.sha256((ROOT / "quests/repairing-prime.md").read_bytes()).hexdigest(),
        )
        self.assertEqual(repairing["quest_state"], "IN_PROGRESS")
        self.assertIn("R04 mandatory stop", repairing["next_action"])
        self.assertIn("M07/AJ-03", repairing["next_action"])
        self.assertFalse(any("AJ-10 requires" in blocker for blocker in repairing["blockers"]))
        self.assertFalse(any("CAP-022 remains" in blocker for blocker in repairing["blockers"]))
        self.assertFalse(any("RP-C01-M06" in blocker for blocker in repairing["blockers"]))
        self.assertTrue(any("genuine non-owner" in blocker for blocker in repairing["blockers"]))


if __name__ == "__main__":
    unittest.main()
