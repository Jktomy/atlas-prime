from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

from tools.prime_continuity.engine import sha256 as continuity_sha256


ROOT = Path(__file__).resolve().parents[2]
PROOF_PATH = ROOT / "proof/repairing-prime/rp-c08-aj12-merged-main-validation-acceptance-r01.json"
ACCEPTANCE_PATH = ROOT / "governance/capability-acceptance-contract.md"
ROUTE_PATH = ROOT / "governance/athena-execution-route-contract.md"
REGISTER_PATH = ROOT / "governance/capability-parity-register.json"
QUEST_PATH = ROOT / "quests/repairing-prime.md"
BOARD_PATH = ROOT / "quest-board/quest-board-v1.json"
CONTINUITY_PATH = ROOT / "continuity/prime-continuity-register-r01.json"
WORKFLOW_PATH = ROOT / ".github/workflows/prime-readonly-validation.yml"
FINAL_PATH = ROOT / "proof/repairing-prime/rp-c08-cap027-final-capability-reconciliation-r01.json"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Aj12MergedMainValidationAcceptanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.proof = load_json(PROOF_PATH)
        cls.final = load_json(FINAL_PATH)
        cls.register = load_json(REGISTER_PATH)
        cls.board = load_json(BOARD_PATH)
        cls.continuity = load_json(CONTINUITY_PATH)

    def test_exact_run_sha_and_platform_jobs_are_bound(self) -> None:
        evidence = self.proof["accepted_workflow_evidence"]
        exact = "043648a85cf581d7805355a71cc819fdb83e738b"
        self.assertEqual(self.proof["transaction_base_sha"], exact)
        self.assertEqual(evidence["exact_merged_main_sha"], exact)
        self.assertEqual(evidence["canonical_main_before"], exact)
        self.assertEqual(evidence["canonical_main_after"], exact)
        self.assertEqual(evidence["run_id"], 29455372822)
        self.assertEqual(
            evidence["run_url"],
            "https://github.com/Jktomy/atlas-prime/actions/runs/29455372822",
        )
        self.assertEqual(
            evidence["jobs"]["ubuntu"],
            {
                "job_id": 87487269033,
                "name": "validate (ubuntu-latest)",
                "status": "completed",
                "conclusion": "success",
            },
        )
        self.assertEqual(
            evidence["jobs"]["windows"],
            {
                "job_id": 87487269036,
                "name": "validate (windows-latest)",
                "status": "completed",
                "conclusion": "success",
            },
        )

    def test_complete_matrix_and_read_only_boundary_are_accepted(self) -> None:
        evidence = self.proof["accepted_workflow_evidence"]
        self.assertEqual(evidence["permissions"], {"contents": "read"})
        self.assertEqual(len(evidence["substantive_stages"]), 12)
        self.assertTrue(evidence["all_substantive_stages_passed_on_both_platforms"])
        self.assertTrue(all(value is False for value in evidence["mutation"].values()))
        audit = self.proof["detached_readback"]
        self.assertTrue(audit["ubuntu_completed_success"])
        self.assertTrue(audit["windows_completed_success"])
        self.assertTrue(audit["all_reported_steps_success"])
        self.assertTrue(audit["exact_main_unchanged"])
        self.assertFalse(audit["protected_data_observed"])
        self.assertEqual(audit["result"], "GREEN")
        workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
        self.assertIn("contents: read", workflow)
        self.assertIn("ubuntu-latest", workflow)
        self.assertIn("windows-latest", workflow)
        for stage in evidence["substantive_stages"]:
            self.assertIn(stage, workflow)

    def test_only_aj12_transitioned_in_its_historical_record(self) -> None:
        self.assertEqual(
            self.proof["transitions"],
            {"AJ-12": {"from": "UNPROVEN", "to": "PROVEN"}},
        )
        self.assertEqual(
            self.proof["preserved_open"],
            ["CAP-027", "RP-C08", "QUEST-REPAIRING-PRIME-R01"],
        )
        self.assertTrue(
            all(value is False for value in self.proof["forbidden_promotions"].values())
        )
        self.assertEqual(
            self.proof["capability_counts"],
            {
                "PRESERVED": 4,
                "IMPROVED": 7,
                "RESTORED": 14,
                "REPLACED": 1,
                "INTENTIONALLY_RETIRED": 1,
                "BLOCKED": 0,
                "STILL_MISSING": 1,
            },
        )
        self.assertEqual(self.final["transitions"]["CAP-027"]["to"], "RESTORED/ACTIVE")
        cap027 = next(item for item in self.register["capabilities"] if item["id"] == "CAP-027")
        self.assertEqual(cap027["capability_disposition"], "RESTORED")
        self.assertEqual(cap027["activation_state"], "ACTIVE")
        self.assertEqual(
            [
                item["id"]
                for item in self.register["capabilities"]
                if item["capability_disposition"] == "STILL_MISSING"
            ],
            [],
        )

    def test_canonical_surfaces_preserve_aj12_and_advance_cap027_without_quest_completion(self) -> None:
        acceptance = ACCEPTANCE_PATH.read_text(encoding="utf-8")
        route = ROUTE_PATH.read_text(encoding="utf-8")
        quest = QUEST_PATH.read_text(encoding="utf-8")
        self.assertIn("AJ-12 PROVEN", acceptance)
        self.assertIn("run `29455372822`", acceptance)
        self.assertIn("AJ-11 and AJ-12 are now PROVEN", route)
        self.assertIn("AJ-01 through AJ-12 are PROVEN", quest)
        self.assertIn("AJ-12: PROVEN", quest)
        self.assertIn("CAP-027: RESTORED / ACTIVE", quest)
        self.assertIn("RP-C08: IN_PROGRESS", quest)
        self.assertIn("Repairing Prime: IN_PROGRESS", quest)
        repairing_board = next(
            item for item in self.board["entries"]
            if item["quest_id"] == "QUEST-REPAIRING-PRIME-R01"
        )
        self.assertEqual(repairing_board["state"], "IN_PROGRESS")
        self.assertIn("whole-Quest Strikeforce", repairing_board["next_gate"])

    def test_continuity_preserves_aj12_event_and_binds_later_cap027_event(self) -> None:
        aj12_event = "RP-C08-AJ12-MERGED-MAIN-VALIDATION-ACCEPTANCE-R01"
        final_event = "RP-C08-CAP027-FINAL-CAPABILITY-RECONCILIATION-R01"
        self.assertEqual(self.continuity["register_revision"], 29)
        self.assertEqual(
            self.continuity["source_base_sha"],
            "887c562f40c1ae6756054b322a08b113f6ce60ca",
        )
        self.assertEqual(self.continuity["event_ids"].count(aj12_event), 1)
        self.assertEqual(self.continuity["event_ids"].count(final_event), 1)
        repairing = next(
            item for item in self.continuity["entries"]
            if item["continuity_id"] == "CONT-REPAIRING-PRIME-R01"
        )
        self.assertEqual(repairing["revision"], 24)
        self.assertEqual(repairing["last_event_id"], final_event)
        self.assertEqual(repairing["quest_state"], "IN_PROGRESS")
        self.assertEqual(repairing["quest_source_sha256"], file_sha256(QUEST_PATH))
        self.assertEqual(self.continuity["quest_board_sha256"], continuity_sha256(self.board))
        self.assertIn("whole-Quest Strikeforce", repairing["next_action"])

    def test_historical_review_and_permanence_boundaries_remain_exact(self) -> None:
        boundary = self.proof["review_boundary"]
        self.assertTrue(boundary["exact_head_ci_required"])
        self.assertTrue(boundary["fresh_detached_review_required"])
        self.assertTrue(boundary["separate_ready_authorization_required"])
        self.assertTrue(boundary["separate_merge_authorization_required"])
        self.assertEqual(
            self.proof["next_gate"],
            "MERGE_THEN_GENERATED_CURRENT_STATE_THEN_CAP027_AND_RP_C08_FINAL_CAPABILITY_RECONCILIATION",
        )


if __name__ == "__main__":
    unittest.main()
