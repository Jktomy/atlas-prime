from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from tools.atlas_lifecycle.errors import LifecycleError
from tools.atlas_lifecycle.repository import _validate_sunset_feather_bindings


ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "lifecycle" / "fixtures"


def load(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


class SunsetFeatherInvariantTests(unittest.TestCase):
    def setUp(self) -> None:
        self.records = [
            load("feather-quest-bound.json"),
            load("sunset-quest-bound.json"),
            load("feather-non-quest.json"),
            load("sunset-non-quest.json"),
            load("feather-candidate-quest.json"),
            load("sunset-candidate-quest.json"),
            load("feather-protected-domain.json"),
            load("sunset-protected-domain.json"),
        ]

    def assert_code(self, records: list[dict], code: str) -> None:
        with self.assertRaises(LifecycleError) as raised:
            _validate_sunset_feather_bindings(records, record_class="fixture")
        self.assertEqual(raised.exception.code, code)

    def test_all_scope_classes_have_exact_one_to_one_pairs(self) -> None:
        _validate_sunset_feather_bindings(self.records, record_class="fixture")
        sunsets = [record for record in self.records if record["schema_id"] == "atlas.lifecycle.sunset"]
        self.assertEqual(len(sunsets), 4)
        self.assertEqual(len({record["latest_feather_id"] for record in sunsets}), 4)

    def test_null_and_dangling_feather_reject(self) -> None:
        records = copy.deepcopy(self.records)
        next(record for record in records if record["schema_id"] == "atlas.lifecycle.sunset")["latest_feather_id"] = None
        self.assert_code(records, "SUNSET_FEATHER_REQUIRED")

        records = copy.deepcopy(self.records)
        next(record for record in records if record["schema_id"] == "atlas.lifecycle.sunset")["latest_feather_id"] = "FTR-AAAAAAAAAAAAAAAAAAAAAAAAAA"
        self.assert_code(records, "SUNSET_FEATHER_MISSING")

    def test_reused_and_cross_scope_feather_reject(self) -> None:
        records = copy.deepcopy(self.records)
        sunsets = [record for record in records if record["schema_id"] == "atlas.lifecycle.sunset"]
        sunsets[1]["latest_feather_id"] = sunsets[0]["latest_feather_id"]
        self.assert_code(records, "SUNSET_FEATHER_REUSED")

        records = copy.deepcopy(self.records)
        sunset = next(record for record in records if record["schema_id"] == "atlas.lifecycle.sunset")
        feather = next(record for record in records if record["record_id"] == sunset["latest_feather_id"])
        feather["project_id"] = "project-mismatch"
        self.assert_code(records, "SUNSET_FEATHER_SCOPE_MISMATCH")

    def test_sunrise_must_resolve_the_exact_pair(self) -> None:
        records = copy.deepcopy(self.records)
        sunset = next(record for record in records if record["schema_id"] == "atlas.lifecycle.sunset")
        other = next(
            record for record in records
            if record["schema_id"] == "atlas.lifecycle.feather"
            and record["record_id"] != sunset["latest_feather_id"]
        )
        records.append(
            {
                "schema_id": "atlas.lifecycle.sunrise",
                "record_id": "SRI-AAAAAAAAAAAAAAAAAAAAAAAAAA",
                "sunset_id": sunset["record_id"],
                "latest_feather_id": other["record_id"],
            }
        )
        self.assert_code(records, "SUNRISE_FEATHER_MISMATCH")


if __name__ == "__main__":
    unittest.main()
