from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

from tools.prime_continuity.engine import sha256 as continuity_sha256


ROOT = Path(__file__).resolve().parents[2]


def load(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


class Aj12MergedMainValidationAcceptanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.aj12 = load("proof/repairing-prime/rp-c08-aj12-merged-main-validation-acceptance-r01.json")
        cls.final = load("proof/repairing-prime/rp-c08-cap027-final-capability-reconciliation-r01.json")
        cls.register = load("governance/capability-parity-register.json")
        cls.board = load("quest-board/quest-board-v1.json")
        cls.continuity = load("continuity/prime-continuity-register-r01.json")

    def test_aj12_exact_read_only_evidence_is_immutable(self) -> None:
        evidence = self.aj12["accepted_workflow_evidence"]
        exact = "043648a85cf581d7805355a71cc819fdb83e738b"
        self.assertEqual(self.aj12["transaction_base_sha"], exact)
        self.assertEqual(evidence["exact_merged_main_sha"], exact)
        self.assertEqual(evidence["canonical_main_before"], exact)
        self.assertEqual(evidence["canonical_main_after"], exact)
        self.assertEqual(evidence["run_id"], 29455372822)
        self.assertEqual(evidence["jobs"]["ubuntu"]["job_id"], 87487269033)
        self.assertEqual(evidence["jobs"]["windows"]["job_id"], 87487269036)
        self.assertEqual(evidence["jobs"]["ubuntu"]["conclusion"], "success")
        self.assertEqual(evidence["jobs"]["windows"]["conclusion"], "success")
        self.assertEqual(evidence["permissions"], {"contents": "read"})
        self.assertTrue(evidence["all_substantive_stages_passed_on_both_platforms"])
        self.assertTrue(all(value is False for value in evidence["mutation"].values()))

    def test_aj12_historical_boundary_precedes_cap027_transition(self) -> None:
        self.assertEqual(self.aj12["transitions"], {"AJ-12": {"from": "UNPROVEN", "to": "PROVEN"}})
        self.assertEqual(self.aj12["preserved_open"], ["CAP-027", "RP-C08", "QUEST-REPAIRING-PRIME-R01"])
        self.assertEqual(self.aj12["capability_counts"]["RESTORED"], 14)
        self.assertEqual(self.aj12["capability_counts"]["STILL_MISSING"], 1)
        self.assertTrue(all(value is False for value in self.aj12["forbidden_promotions"].values()))
        self.assertEqual(self.final["transitions"]["CAP-027"]["to"], "RESTORED/ACTIVE")
        self.assertEqual(self.final["final_capability_recount"]["capability_counts"]["RESTORED"], 15)
        self.assertEqual(self.final["final_capability_recount"]["capability_counts"]["STILL_MISSING"], 0)

    def test_current_register_restores_cap027_without_quest_completion(self) -> None:
        cap027 = next(item for item in self.register["capabilities"] if item["id"] == "CAP-027")
        self.assertEqual(cap027["capability_disposition"], "RESTORED")
        self.assertEqual(cap027["activation_state"], "ACTIVE")
        self.assertEqual(self.register["capability_disposition_counts"], self.final["final_capability_recount"]["capability_counts"])
        self.assertEqual(self.final["campaign_state"]["RP-C08"], "IN_PROGRESS")
        self.assertEqual(self.final["campaign_state"]["QUEST-REPAIRING-PRIME-R01"], "IN_PROGRESS")
        self.assertTrue(all(value is False for value in self.final["forbidden_promotions"].values()))

    def test_board_and_continuity_bind_the_later_event(self) -> None:
        repairing_board = next(item for item in self.board["entries"] if item["quest_id"] == "QUEST-REPAIRING-PRIME-R01")
        repairing = next(item for item in self.continuity["entries"] if item["continuity_id"] == "CONT-REPAIRING-PRIME-R01")
        quest_path = ROOT / "quests/repairing-prime.md"
        self.assertEqual(repairing_board["state"], "IN_PROGRESS")
        self.assertIn("whole-Quest Strikeforce", repairing_board["next_gate"])
        self.assertEqual(self.continuity["register_revision"], 29)
        self.assertEqual(self.continuity["source_base_sha"], "887c562f40c1ae6756054b322a08b113f6ce60ca")
        self.assertEqual(repairing["last_event_id"], "RP-C08-CAP027-FINAL-CAPABILITY-RECONCILIATION-R01")
        self.assertEqual(repairing["revision"], 24)
        self.assertEqual(repairing["quest_source_sha256"], hashlib.sha256(quest_path.read_bytes()).hexdigest())
        self.assertEqual(self.continuity["quest_board_sha256"], continuity_sha256(self.board))
        self.assertIn("whole-Quest Strikeforce", repairing["next_action"])

    def test_separate_permanence_gates_remain_required(self) -> None:
        boundary = self.final["review_boundary"]
        self.assertTrue(boundary["exact_head_ci_required"])
        self.assertTrue(boundary["fresh_detached_review_required"])
        self.assertTrue(boundary["separate_ready_authorization_required"])
        self.assertTrue(boundary["separate_merge_authorization_required"])
        self.assertEqual(
            self.final["next_gate"],
            "MERGE_THEN_FINAL_GENERATED_CURRENT_STATE_THEN_WHOLE_QUEST_STRIKEFORCE",
        )


if __name__ == "__main__":
    unittest.main()
