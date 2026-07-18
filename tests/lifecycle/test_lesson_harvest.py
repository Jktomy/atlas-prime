from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from tests.lifecycle.test_sunset_candidate import canonical_tree, request
from tools.atlas_lifecycle.errors import LifecycleError
from tools.atlas_lifecycle.jsonio import canonical_bytes
from tools.atlas_lifecycle.repository import (
    _validate_lesson_harvest_bindings,
    validate_repository,
)
from tools.atlas_lifecycle.schema import SchemaValidator
from tools.atlas_lifecycle.sunset import generate_sunset_candidate
from tools.prime_continuity.cli import parser as continuity_parser


ROOT = Path(__file__).resolve().parents[2]


class LessonHarvestTests(unittest.TestCase):
    def write_request(self, parent: Path, value: dict) -> Path:
        path = parent / "request.json"
        path.write_bytes(canonical_bytes(value))
        return path

    def generate(self, value: dict) -> tuple[dict, dict]:
        with tempfile.TemporaryDirectory() as temp:
            parent = Path(temp)
            result = generate_sunset_candidate(
                ROOT, self.write_request(parent, value), parent / "candidate"
            )
            bundle = json.loads(
                (parent / "candidate" / "candidate-bundle.json").read_text(encoding="utf-8")
            )
            return result, bundle

    def assert_rejected(self, value: dict, code: str) -> None:
        before = canonical_tree()
        with tempfile.TemporaryDirectory() as temp:
            parent = Path(temp)
            output = parent / "candidate"
            with self.assertRaises(LifecycleError) as raised:
                generate_sunset_candidate(
                    ROOT, self.write_request(parent, value), output
                )
            self.assertEqual(raised.exception.code, code)
            self.assertFalse(output.exists())
        self.assertEqual(canonical_tree(), before)

    def test_observation_and_explicit_no_lesson_paths_are_closed(self) -> None:
        _, observed = self.generate(request("ADMITTED_QUEST"))
        feather = next(
            item["record"] for item in observed["records"]
            if item["record"]["schema_id"] == "atlas.lifecycle.feather"
        )
        sunset = next(
            item["record"] for item in observed["records"]
            if item["record"]["schema_id"] == "atlas.lifecycle.sunset"
        )
        self.assertEqual(feather["schema_version"], "2.0.0")
        self.assertEqual(sunset["schema_version"], "2.0.0")
        self.assertEqual(sunset["lesson_harvest_summary"]["observation_keys"], ["exact-cardinality"])

        no_lesson = request("NON_QUEST")
        no_lesson["lesson_harvest"].update(
            {"observations": [], "no_lesson_reason": "No reusable lesson arose from this bounded closeout."}
        )
        _, empty = self.generate(no_lesson)
        records = [item["record"] for item in empty["records"]]
        self.assertFalse(any(item["schema_id"] == "atlas.lifecycle.golden-wing" for item in records))

    def test_empty_conflicting_duplicate_and_unresolved_reinforcement_fail(self) -> None:
        empty = request("NON_QUEST")
        empty["lesson_harvest"].update({"observations": [], "no_lesson_reason": None})
        self.assert_rejected(empty, "SCHEMA_ONE_OF")

        conflicting = request("NON_QUEST")
        conflicting["lesson_harvest"]["no_lesson_reason"] = "Conflicts with observation."
        self.assert_rejected(conflicting, "SCHEMA_ONE_OF")

        duplicate = request("NON_QUEST")
        duplicate["lesson_harvest"]["observations"].append(
            copy.deepcopy(duplicate["lesson_harvest"]["observations"][0])
        )
        self.assert_rejected(duplicate, "LESSON_HARVEST_DUPLICATE_KEY")

        reinforcement = request("NON_QUEST")
        observation = reinforcement["lesson_harvest"]["observations"][0]
        observation.update(
            {"disposition": "REINFORCES_EXISTING", "golden_wing_id": "GWN-AAAAAAAAAAAAAAAAAAAAAAAAAA"}
        )
        self.assert_rejected(reinforcement, "LESSON_HARVEST_GOLDEN_WING")

    def test_summary_tamper_and_protected_value_fail_closed(self) -> None:
        _, bundle = self.generate(request("NON_QUEST"))
        records = [item["record"] for item in bundle["records"]]
        sunset = next(item for item in records if item["schema_id"] == "atlas.lifecycle.sunset")
        sunset["lesson_harvest_summary"]["observation_keys"] = ["tampered"]
        snapshot = validate_repository(ROOT)
        with self.assertRaises(LifecycleError) as raised:
            _validate_lesson_harvest_bindings(
                [*snapshot.canonical_records, *records], record_class="candidate"
            )
        self.assertEqual(raised.exception.code, "LESSON_HARVEST_SUMMARY_MISMATCH")

        protected = request("NON_QUEST")
        protected["lesson_harvest"]["observations"][0]["observation"] = (
            "api_key=should-never-enter-clean-source"
        )
        self.assert_rejected(protected, "PROTECTED_VALUE_REJECTED")

    def test_ids_are_deterministic_paths_are_cross_platform_and_no_canonical_write_occurs(self) -> None:
        before = canonical_tree()
        first, first_bundle = self.generate(request("NON_QUEST"))
        second, second_bundle = self.generate(request("NON_QUEST"))
        self.assertEqual(first["candidate_set_digest"], second["candidate_set_digest"])
        self.assertEqual(first["record_bindings"], second["record_bindings"])
        self.assertEqual(first_bundle["records"], second_bundle["records"])
        self.assertTrue(all("\\" not in item["path"] for item in first_bundle["records"]))
        self.assertFalse(any(
            item["record"]["schema_id"] == "atlas.lifecycle.golden-wing"
            for item in first_bundle["records"]
        ))
        self.assertEqual(canonical_tree(), before)

    def test_v1_history_remains_valid_and_continuity_help_is_truthful(self) -> None:
        validator = SchemaValidator(ROOT / "lifecycle/schemas")
        for schema_id in ("atlas.lifecycle.feather", "atlas.lifecycle.sunset"):
            fixture = next(
                json.loads(path.read_text(encoding="utf-8"))
                for path in (ROOT / "lifecycle/fixtures").glob("*.json")
                if json.loads(path.read_text(encoding="utf-8")).get("schema_id") == schema_id
            )
            self.assertEqual(fixture["schema_version"], "1.0.0")
            validator.validate_record(fixture)
        help_text = continuity_parser().format_help()
        self.assertIn("not the full Atlas Sunset", help_text)


if __name__ == "__main__":
    unittest.main()
