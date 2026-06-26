from __future__ import annotations

import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "tests/fixtures/spear/golden-transactions-v1.json"
SCHEMA = ROOT / "schemas/spear/spear-golden-transaction-suite-v1.schema.json"


class GoldenTransactionSuiteTests(unittest.TestCase):
    def setUp(self) -> None:
        self.suite = json.loads(FIXTURE.read_text(encoding="utf-8"))
        self.schema = json.loads(SCHEMA.read_text(encoding="utf-8"))

    def test_fixture_validates_against_schema(self) -> None:
        Draft202012Validator.check_schema(self.schema)
        errors = list(Draft202012Validator(self.schema, format_checker=FormatChecker()).iter_errors(self.suite))
        self.assertEqual(errors, [])

    def test_exact_vector_count_and_unique_ids(self) -> None:
        ids = [item["vector_id"] for item in self.suite["vectors"]]
        self.assertEqual(len(ids), 43)
        self.assertEqual(len(set(ids)), 43)

    def test_every_a2_section_five_through_twenty_three_is_covered(self) -> None:
        covered = {section for item in self.suite["vectors"] for section in item["a2_contract_sections"]}
        self.assertEqual(covered, set(range(5, 24)))
        self.assertEqual(self.suite["required_a2_sections"], list(range(5, 24)))

    def test_reproduced_red_team_failures_have_dedicated_vectors(self) -> None:
        ids = {item["vector_id"] for item in self.suite["vectors"]}
        required = {
            "GT-N12", "GT-N22", "GT-N25", "GT-N28",
            "GT-N29", "GT-N31", "GT-N33", "GT-N35",
        }
        self.assertTrue(required.issubset(ids))

    def test_every_vector_has_receipt_noctua_and_repository_effects(self) -> None:
        for item in self.suite["vectors"]:
            with self.subTest(vector=item["vector_id"]):
                self.assertTrue(item["expected_repository_effect"].strip())
                self.assertTrue(item["required_receipt_evidence"])
                self.assertTrue(item["required_noctua_assertions"])

    def test_suite_grants_no_authority(self) -> None:
        self.assertTrue(all(value is False for value in self.suite["authority"].values()))


if __name__ == "__main__":
    unittest.main()
