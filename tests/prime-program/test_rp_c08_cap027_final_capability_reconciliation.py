from __future__ import annotations

import hashlib
import json
import unittest
from collections import Counter
from pathlib import Path

from tools.prime_continuity.engine import sha256 as continuity_sha256


ROOT = Path(__file__).resolve().parents[2]
PROOF_PATH = ROOT / "proof/repairing-prime/rp-c08-cap027-final-capability-reconciliation-r01.json"
REGISTER_PATH = ROOT / "governance/capability-parity-register.json"
ACCEPTANCE_PATH = ROOT / "governance/capability-acceptance-contract.md"
QUEST_PATH = ROOT / "quests/repairing-prime.md"
BOARD_PATH = ROOT / "quest-board/quest-board-v1.json"
CONTINUITY_PATH = ROOT / "continuity/prime-continuity-register-r01.json"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class Cap027FinalCapabilityReconciliationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.proof = load_json(PROOF_PATH)
        cls.register = load_json(REGISTER_PATH)
        cls.board = load_json(BOARD_PATH)
        cls.continuity = load_json(CONTINUITY_PATH)
        cls.records = {item["id"]: item for item in cls.register["capabilities"]}

    def test_exact_base_and_generated_current_prerequisite_are_bound(self) -> None:
        self.assertEqual(
            self.proof["transaction_base_sha"],
            "887c562f40c1ae6756054b322a08b113f6ce60ca",
        )
        generated = self.proof["prerequisite_generated_current_state"]
        self.assertEqual(generated["aj12_source_pull_request"], 209)
        self.assertEqual(generated["aj12_source_merge_sha"], "52bd5fb2d1c452d5da93dcc52efd3d1a110de5fb")
        self.assertEqual(generated["publisher_run"], 29457577094)
        self.assertEqual(generated["generated_pull_request"], 210)
        self.assertEqual(generated["generated_head_sha"], "cd4b2710071f4cd650e94282f2e0501c57bfdff7")
        self.assertEqual(generated["required_validation_run"], 29457663498)
        self.assertEqual(generated["required_validation_jobs"]["ubuntu"]["job_id"], 87500973978)
        self.assertEqual(generated["required_validation_jobs"]["windows"]["job_id"], 87500974005)
        self.assertEqual(generated["generated_merge_sha"], "887c562f40c1ae6756054b322a08b113f6ce60ca")
        self.assertEqual(generated["result"], "CURRENT")

    def test_final_open_journey_evidence_is_exact(self) -> None:
        journeys = self.proof["accepted_journey_bindings"]
        self.assertEqual(journeys["AJ-03"]["workflow_run"], 29421543076)
        self.assertEqual(journeys["AJ-03"]["error_code"], "OWNER_IDENTITY_REJECTED")
        self.assertFalse(journeys["AJ-03"]["thread_engine_invoked"])
        self.assertFalse(journeys["AJ-03"]["mutation_occurred"])
        self.assertTrue(journeys["AJ-03"]["temporary_access_removed"])
        self.assertEqual(
            journeys["AJ-11"]["receipt_self_sha256"],
            "5907e446bee11a013e8fa5202e1f712af8e922ea5b72621ae129b936d5ec9b45",
        )
        self.assertEqual(journeys["AJ-11"]["validation_commands_passed"], 13)
        self.assertFalse(journeys["AJ-11"]["normal_atlas_codex_dependency"])
        self.assertEqual(journeys["AJ-12"]["workflow_run"], 29455372822)
        self.assertEqual(journeys["AJ-12"]["ubuntu_job"], 87487269033)
        self.assertEqual(journeys["AJ-12"]["windows_job"], 87487269036)
        self.assertTrue(journeys["AJ-12"]["all_substantive_stages_passed_on_both_platforms"])
        self.assertFalse(journeys["AJ-12"]["repository_mutation"])

    def test_all_twelve_journeys_are_bound_without_historical_rewrite(self) -> None:
        layer = self.proof["complete_acceptance_layer"]
        self.assertEqual(layer["journey_ids"], [f"AJ-{index:02d}" for index in range(1, 13)])
        self.assertTrue(layer["all_journeys_proven"])
        self.assertFalse(layer["historical_records_rewritten"])
        self.assertFalse(layer["generated_reports_used_as_authority"])
        self.assertFalse(layer["local_only_evidence_used_as_promotion"])

    def test_cap027_is_the_only_transition_and_counts_total_28(self) -> None:
        self.assertEqual(
            self.proof["transitions"],
            {"CAP-027": {"from": "STILL_MISSING/MISSING", "to": "RESTORED/ACTIVE"}},
        )
        cap027 = self.records["CAP-027"]
        self.assertEqual(cap027["capability_disposition"], "RESTORED")
        self.assertEqual(cap027["activation_state"], "ACTIVE")
        self.assertEqual(cap027["audit_severity"], "GREEN")
        observed = Counter(item["capability_disposition"] for item in self.register["capabilities"])
        self.assertEqual(self.register["capability_disposition_counts"], self.proof["capability_counts"])
        self.assertEqual(dict(observed), {key: value for key, value in self.proof["capability_counts"].items() if value})
        self.assertEqual(sum(observed.values()), 28)
        self.assertEqual([item["id"] for item in self.register["capabilities"] if item["capability_disposition"] == "STILL_MISSING"], [])

    def test_rp_c08_and_quest_remain_open(self) -> None:
        self.assertEqual(self.proof["campaign_state"], {"RP-C08": "IN_PROGRESS", "repairing_prime": "IN_PROGRESS"})
        self.assertTrue(all(value is False for value in self.proof["forbidden_promotions"].values()))
        quest = QUEST_PATH.read_text(encoding="utf-8")
        self.assertIn("RP-C08: IN_PROGRESS", quest)
        self.assertIn("Repairing Prime: IN_PROGRESS", quest)
        self.assertIn("CAP-027: RESTORED / ACTIVE", quest)
        repairing_board = next(item for item in self.board["entries"] if item["quest_id"] == "QUEST-REPAIRING-PRIME-R01")
        self.assertEqual(repairing_board["state"], "IN_PROGRESS")
        self.assertIn("whole-Quest Strikeforce", repairing_board["next_gate"])

    def test_continuity_binds_exact_source_board_and_event(self) -> None:
        self.assertEqual(self.continuity["register_revision"], 29)
        self.assertEqual(self.continuity["source_base_sha"], "887c562f40c1ae6756054b322a08b113f6ce60ca")
        self.assertEqual(self.continuity["quest_board_sha256"], continuity_sha256(self.board))
        event = "RP-C08-CAP027-FINAL-CAPABILITY-RECONCILIATION-R01"
        self.assertEqual(self.continuity["event_ids"].count(event), 1)
        repairing = next(item for item in self.continuity["entries"] if item["continuity_id"] == "CONT-REPAIRING-PRIME-R01")
        self.assertEqual(repairing["revision"], 24)
        self.assertEqual(repairing["last_event_id"], event)
        self.assertEqual(repairing["quest_state"], "IN_PROGRESS")
        self.assertEqual(repairing["quest_source_sha256"], hashlib.sha256(QUEST_PATH.read_bytes()).hexdigest())
        self.assertIn("0 STILL_MISSING", repairing["current_position"])
        self.assertIn("whole-Quest Strikeforce", repairing["next_action"])

    def test_acceptance_contract_names_the_later_controlling_transition(self) -> None:
        acceptance = ACCEPTANCE_PATH.read_text(encoding="utf-8")
        self.assertIn("CAP-027 is `RESTORED` and `ACTIVE`", acceptance)
        self.assertIn("15 RESTORED and 0 STILL_MISSING", acceptance)
        self.assertIn("controlling transition for CAP-027 only", acceptance)

    def test_review_and_permanence_boundaries_remain_separate(self) -> None:
        boundary = self.proof["review_boundary"]
        self.assertTrue(boundary["exact_head_ubuntu_windows_validation_required"])
        self.assertTrue(boundary["fresh_detached_review_required"])
        self.assertTrue(boundary["separate_ready_authorization_required"])
        self.assertTrue(boundary["separate_merge_authorization_required"])
        self.assertTrue(boundary["generated_current_readback_required_after_merge"])
        self.assertEqual(self.proof["next_gate"], "MERGE_THEN_GENERATED_CURRENT_STATE_THEN_WHOLE_QUEST_STRIKEFORCE")


if __name__ == "__main__":
    unittest.main()
