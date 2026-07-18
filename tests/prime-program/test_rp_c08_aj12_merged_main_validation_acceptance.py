from __future__ import annotations

import json
import unittest
from pathlib import Path

from tools.prime_continuity.engine import sha256 as continuity_sha256

ROOT = Path(__file__).resolve().parents[2]
PROOF_PATH = ROOT / "proof/repairing-prime/rp-c08-aj12-merged-main-validation-acceptance-r01.json"
FINAL_PATH = ROOT / "proof/repairing-prime/rp-c08-cap027-final-capability-reconciliation-r01.json"
STRIKEFORCE_PATH = ROOT / "proof/repairing-prime/rp-c08-final-whole-quest-strikeforce-reconciliation-r01.md"
RECOVERY_PATH = ROOT / "proof/repairing-prime/rp-c08-phoenix-recovery-acceptance-r01.json"
ACCEPTANCE_PATH = ROOT / "governance/capability-acceptance-contract.md"
ROUTE_PATH = ROOT / "governance/athena-execution-route-contract.md"
REGISTER_PATH = ROOT / "governance/capability-parity-register.json"
QUEST_PATH = ROOT / "quests/repairing-prime.md"
BOARD_PATH = ROOT / "quest-board/quest-board-v1.json"
CONTINUITY_PATH = ROOT / "continuity/prime-continuity-register-r01.json"
WORKFLOW_PATH = ROOT / ".github/workflows/prime-readonly-validation.yml"
PLANNER_PATH = ROOT / "tools/prime_checks/targeted_validation.py"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class Aj12MergedMainValidationAcceptanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.proof = load_json(PROOF_PATH)
        cls.final = load_json(FINAL_PATH)
        cls.recovery = load_json(RECOVERY_PATH)
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
        self.assertEqual(evidence["run_url"], "https://github.com/Jktomy/atlas-prime/actions/runs/29455372822")
        self.assertEqual(evidence["jobs"]["ubuntu"], {"job_id": 87487269033, "name": "validate (ubuntu-latest)", "status": "completed", "conclusion": "success"})
        self.assertEqual(evidence["jobs"]["windows"], {"job_id": 87487269036, "name": "validate (windows-latest)", "status": "completed", "conclusion": "success"})

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
        planner = PLANNER_PATH.read_text(encoding="utf-8")
        self.assertIn("contents: read", workflow)
        self.assertIn("ubuntu-latest", workflow)
        self.assertIn("windows-latest", workflow)
        self.assertIn("Run targeted pull-request validation", workflow)
        self.assertIn("Run explicit full validation", workflow)
        self.assertIn("inputs.include_windows == true", workflow)
        self.assertNotIn("contents: write", workflow)
        self.assertNotIn("pull-requests: write", workflow)

        expected_checks = (
            "kernel",
            "repository_policy",
            "privacy",
            "lifecycle",
            "thread_engine",
            "thread_engine_static",
            "atlas_sword_static",
            "generators",
            "prime_program",
            "athena_routes",
            "source_validation",
            "powershell_resolver",
        )
        for check_id in expected_checks:
            self.assertIn(f'"{check_id}"', planner)
        self.assertIn("FULL_CHECK_IDS: tuple[str, ...] = tuple(CHECKS)", planner)
        self.assertIn("selected.update(FULL_CHECK_IDS)", planner)

    def test_only_aj12_transitioned_in_its_historical_record(self) -> None:
        self.assertEqual(self.proof["transitions"], {"AJ-12": {"from": "UNPROVEN", "to": "PROVEN"}})
        self.assertEqual(self.proof["preserved_open"], ["CAP-027", "RP-C08", "QUEST-REPAIRING-PRIME-R01"])
        self.assertTrue(all(value is False for value in self.proof["forbidden_promotions"].values()))
        self.assertEqual(self.proof["capability_counts"], {"PRESERVED": 4, "IMPROVED": 7, "RESTORED": 14, "REPLACED": 1, "INTENTIONALLY_RETIRED": 1, "BLOCKED": 0, "STILL_MISSING": 1})
        self.assertEqual(self.recovery["transitions"], {"PHOENIX_RECOVERY": {"from": "PENDING", "to": "PROVEN/ACCEPTED"}})

    def test_cap027_historical_reconciliation_remains_exact(self) -> None:
        cap027 = next(item for item in self.register["capabilities"] if item["id"] == "CAP-027")
        self.assertEqual(cap027["capability_disposition"], "RESTORED")
        self.assertEqual(cap027["activation_state"], "ACTIVE")
        self.assertEqual(self.final["transitions"]["CAP-027"]["to"], "RESTORED/ACTIVE")
        self.assertEqual(self.register["capability_disposition_counts"], self.final["final_capability_recount"]["capability_counts"])
        self.assertEqual(self.final["final_capability_recount"]["capability_counts"]["RESTORED"], 15)
        self.assertEqual(self.final["final_capability_recount"]["capability_counts"]["STILL_MISSING"], 0)
        self.assertEqual(self.final["campaign_state"]["RP-C08"], "IN_PROGRESS")
        self.assertEqual(self.final["campaign_state"]["QUEST-REPAIRING-PRIME-R01"], "IN_PROGRESS")
        self.assertTrue(all(value is False for value in self.final["forbidden_promotions"].values()))

    def test_current_surfaces_close_after_later_recovery_sunset_and_completion(self) -> None:
        acceptance = ACCEPTANCE_PATH.read_text(encoding="utf-8")
        route = ROUTE_PATH.read_text(encoding="utf-8")
        quest = QUEST_PATH.read_text(encoding="utf-8")
        self.assertIn("AJ-12 PROVEN", acceptance)
        self.assertIn("run `29455372822`", acceptance)
        self.assertIn("CAP-027 RESTORED / ACTIVE", acceptance)
        self.assertIn("Final Phoenix recovery is `PROVEN` and `ACCEPTED`", acceptance)
        self.assertIn("AJ-11 and AJ-12 are now PROVEN; CAP-027 is RESTORED/ACTIVE by the separate final capability reconciliation; RP-C08 and Repairing Prime remain open.", route)
        self.assertIn("AJ-01 through AJ-12 are PROVEN", quest)
        self.assertIn("CAP-027: RESTORED / ACTIVE", quest)
        self.assertIn("RP-C08: COMPLETE", quest)
        self.assertIn("Repairing Prime: COMPLETE", quest)
        self.assertIn("PHOENIX RECOVERY: PROVEN / ACCEPTED", quest)
        self.assertIn("NEXT GATE: CLOSED", quest)
        self.assertTrue(STRIKEFORCE_PATH.is_file())
        repairing_board = next(item for item in self.board["entries"] if item["quest_id"] == "QUEST-REPAIRING-PRIME-R01")
        self.assertEqual(repairing_board["state"], "COMPLETE")
        self.assertEqual(repairing_board["next_gate"], "CLOSED")
        self.assertIn("Sunset PR #224", repairing_board["completion_basis"])

    def test_continuity_preserves_acceptance_history_and_records_final_closeout(self) -> None:
        aj12_event = "RP-C08-AJ12-MERGED-MAIN-VALIDATION-ACCEPTANCE-R01"
        cap027_event = "RP-C08-CAP027-FINAL-CAPABILITY-RECONCILIATION-R01"
        strikeforce_event = "RP-C08-FINAL-WHOLE-QUEST-STRIKEFORCE-RECONCILIATION-R01"
        recovery_event = "RP-C08-PHOENIX-RECOVERY-ACCEPTANCE-R01"
        completion_event = "RP-C08-FINAL-REPAIRING-PRIME-COMPLETION-R05"
        ordered = (aj12_event, cap027_event, strikeforce_event, recovery_event, completion_event)
        self.assertEqual(self.continuity["register_revision"], 33)
        self.assertEqual(self.continuity["source_base_sha"], "e87dbf05252fd80829143474b83b7fa180d66fb7")
        for event in ordered:
            self.assertEqual(self.continuity["event_ids"].count(event), 1)
        for left, right in zip(ordered, ordered[1:]):
            self.assertLess(self.continuity["event_ids"].index(left), self.continuity["event_ids"].index(right))
        self.assertNotIn("CONT-REPAIRING-PRIME-R01", {item["continuity_id"] for item in self.continuity["entries"]})
        self.assertEqual(self.continuity["quest_board_sha256"], continuity_sha256(self.board))

    def test_review_and_permanence_boundaries_remain_separate(self) -> None:
        boundary = self.final["review_boundary"]
        self.assertTrue(boundary["exact_head_ci_required"])
        self.assertTrue(boundary["fresh_detached_review_required"])
        self.assertTrue(boundary["separate_ready_authorization_required"])
        self.assertTrue(boundary["separate_merge_authorization_required"])
        self.assertEqual(self.final["next_gate"], "MERGE_THEN_FINAL_GENERATED_CURRENT_STATE_THEN_WHOLE_QUEST_STRIKEFORCE")


if __name__ == "__main__":
    unittest.main()
