from __future__ import annotations

import csv
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FINAL_STATUSES = {
    "MIGRATED",
    "MERGED_INTO_DESTINATION",
    "REMODELED_IN_PRIME",
    "REGENERATED_IN_PRIME",
    "ARCHIVED_IN_CODEX",
    "EXCLUDED_WITH_PROOF",
}


class PrimeProgramTests(unittest.TestCase):
    def test_disposition_ledger_is_terminal_and_complete(self) -> None:
        with (ROOT / "migration/source-disposition-ledger.csv").open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 525)
        self.assertEqual(len({row["source_path"] for row in rows}), 525)
        self.assertEqual({row["final_status"] for row in rows}, FINAL_STATUSES)
        required = (
            "source_blob_sha1",
            "source_class",
            "current_authority",
            "disposition",
            "prime_target",
            "reason",
            "migration_pr_or_ref",
            "migration_commit",
            "verification",
            "privacy_classification",
            "final_status",
        )
        for field in required:
            self.assertEqual([row["source_path"] for row in rows if not row[field].strip()], [], field)

    def test_prime_native_canonical_quest_board(self) -> None:
        board = json.loads((ROOT / "quest-board/quest-board-v1.json").read_text(encoding="utf-8"))
        self.assertEqual(board["canonical_repository"], "Jktomy/atlas-prime")
        self.assertEqual(board["predecessor_workboard_route"], "HISTORICAL_ONLY")
        self.assertEqual(board["state"], "CANONICAL_ACTIVE")
        self.assertEqual(next(item for item in board["entries"] if item["quest_id"] == "PRIME-REBORN-QUEST-R01")["state"], "COMPLETE")

    def test_repairing_prime_is_admitted_without_changing_independent_quests(self) -> None:
        board = json.loads((ROOT / "quest-board/quest-board-v1.json").read_text(encoding="utf-8"))
        repairing_prime = [
            item
            for item in board["entries"]
            if item["quest_id"] == "QUEST-REPAIRING-PRIME-R01"
        ]
        self.assertEqual(
            repairing_prime,
            [
                {
                    "next_gate": "RP-C08 Preview — Final Capability-Parity and Quest Closeout",
                    "owner": "Codex / Source Governance",
                    "quest_id": "QUEST-REPAIRING-PRIME-R01",
                    "source": "quests/repairing-prime.md",
                    "state": "IN_PROGRESS",
                }
            ],
        )
        repairing_source = (ROOT / "quests/repairing-prime.md").read_text(encoding="utf-8")
        conservation = (ROOT / "governance/deterministic-conservation-contract.md").read_text(encoding="utf-8")
        for mission in (f"RP-C06-M{index:02d}" for index in range(1, 8)):
            self.assertIn(mission, repairing_source)
        self.assertIn("Former G4-E means only the construction layer", conservation)
        self.assertIn("Former G4-F means only the later live", conservation)
        self.assertIn("invokes only the singular Thread Engine", conservation)
        independent = {
            item["quest_id"]: (item["source"], item["state"], item["next_gate"])
            for item in board["entries"]
            if item["quest_id"] != "QUEST-REPAIRING-PRIME-R01"
        }
        expected_preserved = {
                "PRIME-REBORN-QUEST-R01": (
                    "quests/prime-reborn.md",
                    "COMPLETE",
                    "CLOSED",
                ),
                "QUEST-FOUND-SILVERLIGHT-R01": (
                    "quests/found-silverlight.md",
                    "IN_PROGRESS",
                    "FS-C01-M04 — Prove the Light",
                ),
                "QUEST-PROMETHEUS-FIRE-20260701": (
                    "quests/prometheus-fire.md",
                    "READY_FOR_CAMPAIGN_1_PREVIEW",
                    "PF-C01 preview and Jayson-side hardware readiness",
                ),
                "QUEST-NOTUMS-WATCH-20260708": (
                    "quests/notums-watch.md",
                    "READY_FOR_JAYSON_EXECUTION_PACKAGE",
                    "NW-C01 readiness package and Jayson-side proof",
                ),
            }
        self.assertEqual(
            {identity: independent[identity] for identity in expected_preserved},
            expected_preserved,
        )
        self.assertEqual(
            independent["QUEST-PRIME-CONTINUITY-PROOF-R01"],
            (
                "quests/prime-continuity-proof.md",
                "READY_FOR_CAMPAIGN_1_PREVIEW",
                "PCP-C01-PREVIEW",
            ),
        )

    def test_prime_is_canonical_and_codex_is_predecessor_only(self) -> None:
        policy = json.loads((ROOT / "policies/repository-policy.json").read_text(encoding="utf-8"))
        self.assertEqual(policy["state"], "CANONICAL_ACTIVE")
        self.assertEqual(policy["canonical_repository"], "Jktomy/atlas-prime")
        self.assertEqual(policy["predecessor_repository"], "Jktomy/atlas-codex")
        self.assertEqual(policy["predecessor_role"], "FROZEN_PREDECESSOR_ROLLBACK_EVIDENCE")

    def test_required_program_surfaces_exist(self) -> None:
        required = (
            "safety/atlas-safety-doctrine.md",
            "governance/source-lifecycle.md",
            "governance/investiture-accounting-contract.md",
            "routing/command-surfaces.md",
            "projects/project-registry.md",
            "operations/operation-registry.md",
            "infrastructure/atlas-infrastructure-source.md",
            "recovery/phoenix-recovery.md",
            "quests/repairing-prime.md",
            "tools/atlas-sword/engine/oathbringer_contract.py",
            "tools/build_index.py",
        )
        self.assertEqual([path for path in required if not (ROOT / path).is_file()], [])


if __name__ == "__main__":
    unittest.main()
