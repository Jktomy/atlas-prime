from __future__ import annotations

import hashlib
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


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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
        self.assertEqual(
            self.recovery["transitions"],
            {"PHOENIX_RECOVERY": {"from": "PENDING", "to": "PROVEN/ACCEPTED"}},
        )

    def test_current_register_restores_cap027_without_quest_completion(self) -> None:
        cap027 = next(item for item in self.register["capabilities"] if item["id"] == "CAP-027")
        self.assertEqual(cap027["capability_disposition"], "RESTORED")
        self.assertEqual(cap027["activation_state"], "ACTIVE")
        self.assertEqual(self.final["transitions"]["CAP-027"]["to"], "RESTORED/ACTIVE")
        self.assertEqual(
            self.register["capability_disposition_counts"],
            self.final["final_capability_recount"]["capability_counts"],
        )
        self.assertEqual(self.final["final_capability_recount"]["capability_counts"]["RESTORED"], 15)
        self.assertEqual(self.final["final_capability_recount"]["capability_counts"]["STILL_MISSING"], 0)
        self.assertEqual(self.final["campaign_state"]["RP-C08"], "IN_PROGRESS")
        self.assertEqual(self.final["campaign_state"]["QUEST-REPAIRING-PRIME-R01"], "IN_PROGRESS")
        self.assertTrue(all(value is False for value in self.final["forbidden_promotions"].values()))

    def test_canonical_surfaces_advance_recovery_to_sunset_without_quest_completion(self) -> None:
        acceptance = ACCEPTANCE_PATH.read_text(encoding="utf-8")
        route = ROUTE_PATH.read_text(encoding="utf-8")
        quest = QUEST_PATH.read_text(encoding="utf-8")
        self.assertIn("AJ-12 PROVEN", acceptance)
        self.assertIn("run `29455372822`", acceptance)
        self.assertIn("CAP-027 RESTORED / ACTIVE", acceptance)
        self.assertIn("Final Phoenix recovery is `PROVEN` and `ACCEPTED`", acceptance)
        self.assertIn(
            "AJ-11 and AJ-12 are now PROVEN; CAP-027 is RESTORED/ACTIVE by the separate final capability reconciliation; RP-C08 and Repairing Prime remain open.",
            route,
        )
        self.assertIn("AJ-01 through AJ-12 are PROVEN", quest)
        self.assertIn("CAP-027: RESTORED / ACTIVE", quest)
        self.assertIn("RP-C08: IN_PROGRESS", quest)
        self.assertIn("Repairing Prime: IN_PROGRESS", quest)
        self.assertIn("PHOENIX RECOVERY: PROVEN / ACCEPTED", quest)
        self.assertIn("NEXT GATE: RESTART-SAFE SUNSET", quest)
        self.assertTrue(STRIKEFORCE_PATH.is_file())
        repairing_board = next(
            item for item in self.board["entries"]
            if item["quest_id"] == "QUEST-REPAIRING-PRIME-R01"
        )
        self.assertEqual(repairing_board["state"], "IN_PROGRESS")
        self.assertEqual(
            repairing_board["next_gate"],
            "Restart-safe Sunset, then final Quest closeout",
        )
        self.assertIn("Final Phoenix recovery is PROVEN", repairing_board["readiness_basis"])

    def test_continuity_binds_exact_recovery_event_and_source_digests(self) -> None:
        aj12_event = "RP-C08-AJ12-MERGED-MAIN-VALIDATION-ACCEPTANCE-R01"
        cap027_event = "RP-C08-CAP027-FINAL-CAPABILITY-RECONCILIATION-R01"
        strikeforce_event = "RP-C08-FINAL-WHOLE-QUEST-STRIKEFORCE-RECONCILIATION-R01"
        recovery_event = "RP-C08-PHOENIX-RECOVERY-ACCEPTANCE-R01"
        self.assertEqual(self.continuity["register_revision"], 31)
        self.assertEqual(
            self.continuity["source_base_sha"],
            "797fb2a1add829ccc304086a56f6d223d130d90d",
        )
        self.assertEqual(self.continuity["event_ids"].count(aj12_event), 1)
        self.assertEqual(self.continuity["event_ids"].count(cap027_event), 1)
        self.assertEqual(self.continuity["event_ids"].count(strikeforce_event), 1)
        self.assertEqual(self.continuity["event_ids"].count(recovery_event), 1)
        self.assertLess(
            self.continuity["event_ids"].index(aj12_event),
            self.continuity["event_ids"].index(cap027_event),
        )
        self.assertLess(
            self.continuity["event_ids"].index(cap027_event),
            self.continuity["event_ids"].index(strikeforce_event),
        )
        self.assertLess(
            self.continuity["event_ids"].index(strikeforce_event),
            self.continuity["event_ids"].index(recovery_event),
        )
        repairing = next(
            item for item in self.continuity["entries"]
            if item["continuity_id"] == "CONT-REPAIRING-PRIME-R01"
        )
        self.assertEqual(repairing["revision"], 26)
        self.assertEqual(repairing["last_event_id"], recovery_event)
        self.assertEqual(repairing["quest_state"], "IN_PROGRESS")
        self.assertEqual(repairing["quest_source_sha256"], file_sha256(QUEST_PATH))
        self.assertEqual(self.continuity["quest_board_sha256"], continuity_sha256(self.board))
        self.assertIn("restart-safe Sunset", repairing["next_action"])
        self.assertNotIn("final Phoenix recovery proof", repairing["next_action"])
        self.assertFalse(any("CAP-027 remains missing" in blocker for blocker in repairing["blockers"]))
        self.assertFalse(any("Final Phoenix recovery has not yet" in blocker for blocker in repairing["blockers"]))

    def test_review_and_permanence_boundaries_remain_separate(self) -> None:
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
