from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

from tools.prime_continuity.engine import sha256 as continuity_sha256


ROOT = Path(__file__).resolve().parents[2]
PROOF_PATH = ROOT / "proof" / "repairing-prime" / "rp-c08-aj11-clean-clone-acceptance-r08.json"
FINAL_PATH = ROOT / "proof" / "repairing-prime" / "rp-c08-cap027-final-capability-reconciliation-r01.json"
STRIKEFORCE_PATH = ROOT / "proof" / "repairing-prime" / "rp-c08-final-whole-quest-strikeforce-reconciliation-r01.md"
QUEST_PATH = ROOT / "quests" / "repairing-prime.md"
BOARD_PATH = ROOT / "quest-board" / "quest-board-v1.json"
CONTINUITY_PATH = ROOT / "continuity" / "prime-continuity-register-r01.json"
ACCEPTANCE_PATH = ROOT / "governance" / "capability-acceptance-contract.md"
ROUTE_PATH = ROOT / "governance" / "athena-execution-route-contract.md"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Aj11CleanCloneAcceptanceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.proof = load_json(PROOF_PATH)
        self.final = load_json(FINAL_PATH)

    def test_receipt_and_exact_main_bindings_are_exact(self) -> None:
        accepted = self.proof["accepted_local_proof"]
        self.assertEqual(
            accepted["receipt_self_sha256"],
            "5907e446bee11a013e8fa5202e1f712af8e922ea5b72621ae129b936d5ec9b45",
        )
        self.assertEqual(
            accepted["receipt_file_sha256"],
            "1976b29f9a05a93d86a887e63edd960b19f91967ee916e719aff44728f82240c",
        )
        exact = "af97c00df41be8943ba5d4c942a8ecc2c5aff822"
        self.assertEqual(accepted["expected_sha"], exact)
        self.assertEqual(accepted["observed_sha"], exact)
        self.assertEqual(accepted["remote_main_before"], exact)
        self.assertEqual(accepted["remote_main_after"], exact)
        self.assertTrue(self.proof["detached_audit"]["receipt_self_hash_valid"])
        self.assertTrue(self.proof["detached_audit"]["receipt_file_sidecar_valid"])
        self.assertEqual(self.proof["detached_audit"]["result"], "GREEN")

    def test_clean_clone_validation_regeneration_and_rollback_are_accepted(self) -> None:
        accepted = self.proof["accepted_local_proof"]
        self.assertTrue(accepted["clone_isolated"])
        self.assertEqual(accepted["inherited_hooks"], [])
        self.assertEqual(accepted["inherited_worktrees"], [])
        self.assertTrue(accepted["working_tree_clean_before"])
        self.assertTrue(accepted["working_tree_clean_after"])
        validation = accepted["validation"]
        self.assertEqual(validation["result"], "GREEN")
        self.assertEqual(validation["command_count"], 13)
        self.assertEqual(validation["pass_count"], 13)
        self.assertTrue(all(row["result"] == "PASS" for row in validation["commands"]))
        generated = accepted["generated_state"]
        self.assertEqual(generated["status"], "CURRENT")
        self.assertEqual(generated["changed_paths"], [])
        self.assertEqual(len(generated["hashes"]), 5)
        for binding in generated["hashes"].values():
            self.assertTrue(binding["byte_equal"])
            self.assertEqual(binding["committed_sha256"], binding["regenerated_sha256"])
        self.assertFalse(accepted["normal_atlas_codex_dependency"])
        rollback = accepted["rollback_classification"]
        self.assertEqual(rollback["source_rollback"], "NEW_REVIEWED_PR")
        self.assertEqual(rollback["force_push"], "FORBIDDEN")
        self.assertEqual(rollback["history_rewrite"], "FORBIDDEN")

    def test_only_aj11_transitioned_in_its_historical_record(self) -> None:
        self.assertEqual(self.proof["transitions"], {"AJ-11": {"from": "UNPROVEN", "to": "PROVEN"}})
        mutation = self.proof["accepted_local_proof"]["mutation"]
        self.assertTrue(all(value is False for value in mutation.values()))
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
            self.proof["preserved_open"],
            ["AJ-12", "CAP-027", "RP-C08", "QUEST-REPAIRING-PRIME-R01"],
        )
        self.assertTrue(all(value is False for value in self.proof["forbidden_promotions"].values()))
        self.assertEqual(self.final["transitions"]["CAP-027"]["to"], "RESTORED/ACTIVE")

    def test_canonical_surfaces_preserve_aj11_and_advance_to_phoenix(self) -> None:
        acceptance = ACCEPTANCE_PATH.read_text(encoding="utf-8")
        route = ROUTE_PATH.read_text(encoding="utf-8")
        quest = QUEST_PATH.read_text(encoding="utf-8")
        board = load_json(BOARD_PATH)
        continuity = load_json(CONTINUITY_PATH)

        self.assertIn("AJ-11 PROVEN", acceptance)
        self.assertIn("AJ-12 PROVEN", acceptance)
        self.assertIn("CAP-027 RESTORED / ACTIVE", acceptance)
        self.assertIn("final whole-Quest Strikeforce at that exact main is GREEN", acceptance)
        self.assertIn("AJ-01 through AJ-12 are PROVEN", quest)
        self.assertIn("CAP-027: RESTORED / ACTIVE", quest)
        self.assertIn("NEXT GATE: PHOENIX RECOVERY", quest)
        self.assertTrue(STRIKEFORCE_PATH.is_file())
        self.assertIn(
            "AJ-11 and AJ-12 are now PROVEN; CAP-027 is RESTORED/ACTIVE by the separate final capability reconciliation; RP-C08 and Repairing Prime remain open.",
            route,
        )

        repairing = next(
            entry for entry in board["entries"]
            if entry["quest_id"] == "QUEST-REPAIRING-PRIME-R01"
        )
        self.assertEqual(repairing["state"], "IN_PROGRESS")
        self.assertEqual(
            repairing["next_gate"],
            "Phoenix recovery, then restart-safe Sunset and final Quest closeout",
        )

        entry = next(
            item for item in continuity["entries"]
            if item["continuity_id"] == "CONT-REPAIRING-PRIME-R01"
        )
        self.assertEqual(continuity["source_base_sha"], "3fbcc5fdb95c40665cbd6ee3fff752b149a81cb9")
        self.assertEqual(continuity["register_revision"], 30)
        self.assertEqual(entry["revision"], 25)
        self.assertEqual(
            entry["last_event_id"],
            "RP-C08-FINAL-WHOLE-QUEST-STRIKEFORCE-RECONCILIATION-R01",
        )
        self.assertEqual(entry["quest_source_sha256"], sha256(QUEST_PATH))
        self.assertEqual(continuity["quest_board_sha256"], continuity_sha256(board))
        self.assertIn("Phoenix recovery", entry["next_action"])
        self.assertNotIn("whole-Quest Strikeforce", entry["next_action"])
        self.assertFalse(any("AJ-11 requires" in blocker for blocker in entry["blockers"]))
        self.assertFalse(any("CAP-027 remains missing" in blocker for blocker in entry["blockers"]))
        self.assertIn("RP-C08-AJ11-CLEAN-CLONE-ACCEPTANCE-RECONCILIATION-R08", continuity["event_ids"])
        self.assertIn("RP-C08-AJ12-MERGED-MAIN-VALIDATION-ACCEPTANCE-R01", continuity["event_ids"])
        self.assertIn("RP-C08-CAP027-FINAL-CAPABILITY-RECONCILIATION-R01", continuity["event_ids"])
        self.assertIn("RP-C08-FINAL-WHOLE-QUEST-STRIKEFORCE-RECONCILIATION-R01", continuity["event_ids"])


if __name__ == "__main__":
    unittest.main()
