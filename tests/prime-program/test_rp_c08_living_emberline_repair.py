from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class RepairingPrimeLivingEmberlineTests(unittest.TestCase):
    def test_repairing_prime_has_one_stable_living_emberline(self) -> None:
        directory = ROOT / "lifecycle/quest-emberlines"
        records = []
        for path in sorted(directory.glob("*.json")):
            value = json.loads(path.read_text(encoding="utf-8"))
            if value.get("quest_id") == "repairing-prime":
                records.append(value)
        self.assertEqual(len(records), 1)
        record = records[0]
        self.assertEqual(record["record_id"], "QEM-R6QKBDHLY7I7PVVEKIGTZFMZZT")
        self.assertEqual(record["lineage_root_id"], record["record_id"])
        self.assertEqual(record["schema_version"], "2.0.0")
        self.assertEqual(record["quest_state"], "COMPLETE")
        self.assertEqual(record["next_gate"], "CLOSED")
        self.assertTrue({"MAIN", "SIDE", "BRANCHED", "FINAL"} <= {entry["entry_type"] for entry in record["journey_entries"]})
        self.assertEqual(record["current_entry_id"], record["journey_entries"][-1]["entry_id"])

    def test_checkpoint_reference_remains_valid(self) -> None:
        checkpoint = json.loads(
            (ROOT / "lifecycle/quest-checkpoints/QCP-VHH3SNDFKXN6NYD6S7IG7HGZAF.json").read_text(encoding="utf-8")
        )
        self.assertEqual(checkpoint["emberline_id"], "QEM-R6QKBDHLY7I7PVVEKIGTZFMZZT")

    def test_doctrine_names_side_branched_and_final_paths(self) -> None:
        decision = (ROOT / "lifecycle/architecture-decision-r03.md").read_text(encoding="utf-8")
        for phrase in (
            "Side-Campaign", "Side-Mission", "Side-Gate", "Branched-Emberline",
            "Branched-Campaign", "Branched-Mission", "Branched-Gate", "Final-*",
        ):
            self.assertIn(phrase, decision)


if __name__ == "__main__":
    unittest.main()
