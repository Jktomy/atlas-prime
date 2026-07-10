from __future__ import annotations

import csv
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class PrimeProgramTests(unittest.TestCase):
    def test_disposition_ledger_is_closed(self) -> None:
        with (ROOT / "migration/source-disposition-ledger.csv").open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 525)
        self.assertEqual(len({row["source_path"] for row in rows}), 525)
        self.assertEqual(
            {row["disposition"] for row in rows},
            {"KEEP", "MERGE", "REMODEL", "REGENERATE", "ARCHIVE", "EXCLUDE"},
        )

    def test_prime_native_quest_board(self) -> None:
        board = json.loads((ROOT / "quest-board/quest-board-v1.json").read_text(encoding="utf-8"))
        self.assertEqual(board["canonical_repository"], "Jktomy/atlas-prime")
        self.assertEqual(board["predecessor_workboard_route"], "ABSENT")
        self.assertEqual(len(board["entries"]), 3)

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
