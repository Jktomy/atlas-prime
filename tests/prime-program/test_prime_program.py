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
            "routing/command-surfaces.md",
            "projects/project-registry.md",
            "operations/operation-registry.md",
            "infrastructure/atlas-infrastructure-source.md",
            "recovery/phoenix-recovery.md",
            "tools/atlas-sword/engine/oathbringer_contract.py",
            "tools/build_index.py",
        )
        self.assertEqual([path for path in required if not (ROOT / path).is_file()], [])


if __name__ == "__main__":
    unittest.main()
