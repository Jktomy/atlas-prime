from __future__ import annotations

import base64
import hashlib
import json
import re
import unittest
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
LIFECYCLE = ROOT / "lifecycle"
SCHEMAS = LIFECYCLE / "schemas"
FIXTURES = LIFECYCLE / "fixtures"

ENTITY_SCHEMAS = {
    "atlas.lifecycle.feather": ("feather-v1.schema.json", "FTR"),
    "atlas.lifecycle.feather-archive": ("feather-archive-v1.schema.json", "FAR"),
    "atlas.lifecycle.golden-wing": ("golden-wing-v1.schema.json", "GWN"),
    "atlas.lifecycle.quest-emberline": ("quest-emberline-v1.schema.json", "QEM"),
    "atlas.lifecycle.quest-checkpoint": ("quest-checkpoint-v1.schema.json", "QCP"),
    "atlas.lifecycle.sunset": ("sunset-v1.schema.json", "SUN"),
    "atlas.lifecycle.sunrise": ("sunrise-v1.schema.json", "SRI"),
    "atlas.lifecycle.continuity": ("continuity-v1.schema.json", "CON"),
    "atlas.lifecycle.receipt": ("lifecycle-receipt-v1.schema.json", "LCR"),
    "atlas.lifecycle.event": ("lifecycle-event-v1.schema.json", "LEV"),
    "atlas.lifecycle.event-trust-root": ("lifecycle-event-trust-root-v1.schema.json", ""),
    "atlas.lifecycle.event-candidate-manifest": (
        "lifecycle-event-candidate-manifest-v1.schema.json", ""
    ),
    "atlas.lifecycle.event-candidate-receipt": (
        "lifecycle-event-candidate-receipt-v1.schema.json", ""
    ),
    "atlas.lifecycle.construction-profile": (
        "lifecycle-construction-profile-v1.schema.json", ""
    ),
    "atlas.lifecycle.website-index": ("website-index-v1.schema.json", ""),
}
VERSIONED_AND_AUXILIARY_SCHEMAS = {
    "quest-emberline-v2.schema.json",
    "website-index-v2.schema.json",
    "lesson-harvest-v1.schema.json",
    "feather-v2.schema.json",
    "sunset-v2.schema.json",
    "sunset-request-v2.schema.json",
    "sunset-preview-v1.schema.json",
    "sunset-approval-v1.schema.json",
    "sunset-carrier-v1.schema.json",
    "sunset-request-v3.schema.json",
    "sunset-router-request-v1.schema.json",
    "sunset-router-plan-v1.schema.json",
    "sunset-router-receipt-v1.schema.json",
    "sunset-router-preview-intake-v1.schema.json",
}


def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(
        path.read_text(encoding="utf-8"),
        object_pairs_hook=reject_duplicate_keys,
        parse_float=lambda value: (_ for _ in ()).throw(
            ValueError(f"floating-point number is forbidden: {value}")
        ),
        parse_constant=lambda value: (_ for _ in ()).throw(
            ValueError(f"non-finite number is forbidden: {value}")
        ),
    )


def stable_record_id(record: dict[str, Any], prefix: str) -> str:
    payload = {key: value for key, value in record.items() if key != "record_id"}
    canonical = (
        json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")
    digest = base64.b32encode(hashlib.sha256(canonical).digest()).decode("ascii")
    return f"{prefix}-{digest.rstrip('=')[:26]}"


def walk(value: Any):
    yield value
    if isinstance(value, dict):
        for nested in value.values():
            yield from walk(nested)
    elif isinstance(value, list):
        for nested in value:
            yield from walk(nested)


class LifecycleContractTests(unittest.TestCase):
    def test_exact_schema_catalog_is_strict_and_locally_resolvable(self) -> None:
        expected = {"common-v1.schema.json"} | {
            filename for filename, _ in ENTITY_SCHEMAS.values()
        } | VERSIONED_AND_AUXILIARY_SCHEMAS
        self.assertEqual({path.name for path in SCHEMAS.glob("*.json")}, expected)

        schema_ids: set[str] = set()
        schema_versions: set[tuple[str, str]] = set()
        for path in sorted(SCHEMAS.glob("*.json")):
            schema = load_json(path)
            with self.subTest(schema=path.name):
                self.assertEqual(
                    schema["$schema"],
                    "https://json-schema.org/draft/2020-12/schema",
                )
                self.assertTrue(schema["$id"].endswith(f"/{path.name}"))
                if path.name != "common-v1.schema.json":
                    self.assertFalse(schema["additionalProperties"])
                    schema_id = schema["properties"]["schema_id"]["const"]
                    schema_version = schema["properties"]["schema_version"]["const"]
                    self.assertNotIn((schema_id, schema_version), schema_versions)
                    schema_versions.add((schema_id, schema_version))
                    schema_ids.add(schema_id)

                for value in walk(schema):
                    if not isinstance(value, str) or not value.startswith("common-"):
                        continue
                    referenced_file = value.split("#", 1)[0]
                    self.assertTrue((SCHEMAS / referenced_file).is_file(), value)

        self.assertEqual(
            schema_ids,
            set(ENTITY_SCHEMAS)
            | {
                "atlas.lifecycle.lesson-harvest",
                "atlas.lifecycle.sunset-request",
                "atlas.lifecycle.sunset-preview",
                "atlas.lifecycle.sunset-approval",
                "atlas.lifecycle.sunset-carrier",
                "atlas.sunset-router.request",
                "atlas.sunset-router.plan",
                "atlas.sunset-router.receipt",
                "atlas.sunset-router.preview-intake",
            },
        )

    def test_fixtures_are_closed_shape_and_content_addressed(self) -> None:
        seen_ids: set[str] = set()
        for path in sorted(FIXTURES.glob("*.json")):
            record = load_json(path)
            schema_file, prefix = ENTITY_SCHEMAS[record["schema_id"]]
            schema = load_json(SCHEMAS / schema_file)
            with self.subTest(fixture=path.name):
                self.assertEqual(record["authority"], "NONCANONICAL_FIXTURE")
                self.assertEqual(set(record), set(schema["required"]))
                self.assertEqual(record["record_id"], stable_record_id(record, prefix))
                self.assertNotIn(record["record_id"].casefold(), seen_ids)
                seen_ids.add(record["record_id"].casefold())

    def test_required_sunset_scope_fixtures_are_distinct(self) -> None:
        sunsets = {
            path.stem: load_json(path)
            for path in FIXTURES.glob("sunset-*.json")
        }
        self.assertEqual(
            set(sunsets),
            {
                "sunset-quest-bound",
                "sunset-non-quest",
                "sunset-protected-domain",
                "sunset-candidate-quest",
            },
        )
        self.assertEqual(
            sunsets["sunset-quest-bound"]["quest_scope"]["scope_type"],
            "ADMITTED_QUEST",
        )
        self.assertEqual(
            sunsets["sunset-non-quest"]["quest_scope"]["scope_type"],
            "NON_QUEST",
        )
        candidate_scope = sunsets["sunset-candidate-quest"]["quest_scope"]
        self.assertEqual(candidate_scope["scope_type"], "CANDIDATE_QUEST")
        self.assertEqual(candidate_scope["candidate_quest_ref"], "notums-watch-candidate")
        self.assertNotIn("quest_id", candidate_scope)

    def test_protected_fixture_contains_only_clean_pointer(self) -> None:
        record = load_json(FIXTURES / "sunset-protected-domain.json")
        protected = record["protected_data"]
        self.assertEqual(protected["classification"], "PROTECTED_POINTER_ONLY")
        self.assertTrue(protected["protected_pointers"])
        for pointer in protected["protected_pointers"]:
            self.assertRegex(pointer, r"^protected://[a-z0-9][a-z0-9._/-]*$")
        self.assertNotIn("quest_id", record["quest_scope"])

    def test_reference_path_patterns_reject_traversal_and_absolute_paths(self) -> None:
        common = load_json(SCHEMAS / "common-v1.schema.json")
        branch = common["$defs"]["source_reference"]["allOf"][0]
        protected_pattern = branch["then"]["properties"]["uri"]["pattern"]
        relative_pattern = branch["else"]["properties"]["uri"]["pattern"]

        for value in ("quests/found-silverlight.md", "proof/fixture-01.json"):
            self.assertIsNotNone(re.fullmatch(relative_pattern, value), value)
        for value in ("../escape.json", "a/../escape.json", "/absolute.json", "C:/private"):
            self.assertIsNone(re.fullmatch(relative_pattern, value), value)

        valid_pointer = "protected://fixture/raphael/continuity-evidence"
        self.assertIsNotNone(re.fullmatch(protected_pattern, valid_pointer))
        for value in ("protected://../escape", "protected://fixture/../escape", "proof/fixture.json"):
            self.assertIsNone(re.fullmatch(protected_pattern, value), value)

    def test_golden_wing_remains_human_decided_candidate(self) -> None:
        record = load_json(FIXTURES / "golden-wing-multi-context.json")
        self.assertEqual(record["lifecycle_status"], "CANDIDATE")
        self.assertEqual(record["scope"], "CROSS_PROJECT")
        self.assertGreaterEqual(len(record["supporting_feather_ids"]), 2)
        self.assertGreaterEqual(len(record["originating_quest_ids"]), 2)
        self.assertGreaterEqual(len(record["originating_project_ids"]), 2)
        self.assertGreaterEqual(len(record["recurrence_evidence"]), 2)
        self.assertTrue(record["promotion_readiness"]["human_decision_required"])
        self.assertNotEqual(
            record["promotion_readiness"]["state"], "APPROVED_FOR_REVIEW"
        )

    def test_fixture_text_has_no_private_path_or_network_value(self) -> None:
        private_path = re.compile(r"(?i)(?:[a-z]:\\|/users/|/home/|\\\\)")
        network_value = re.compile(r"(?<![A-Za-z0-9])(?:\d{1,3}\.){3}\d{1,3}(?![A-Za-z0-9])")
        forbidden_terms = ("BEGIN PRIVATE KEY", "seed phrase", "recovery code", ".env=")
        for path in sorted(FIXTURES.glob("*.json")):
            text = path.read_text(encoding="utf-8")
            with self.subTest(fixture=path.name):
                self.assertIsNone(private_path.search(text))
                self.assertIsNone(network_value.search(text))
                for term in forbidden_terms:
                    self.assertNotIn(term.casefold(), text.casefold())

    def test_contract_declares_non_autonomous_activation_boundaries(self) -> None:
        decision = (LIFECYCLE / "architecture-decision-r01.md").read_text(
            encoding="utf-8"
        )
        contract = (LIFECYCLE / "lifecycle-contract.md").read_text(encoding="utf-8")
        for phrase in (
            "SCRIPT ASSIST — LEVEL 1",
            "Code presence never activates a higher level",
            "atomic lifecycle authority cutover is proven",
            "The future website is out of scope",
        ):
            self.assertIn(phrase, decision)
        for phrase in (
            "Plan → Route → Apply → Verify",
            "A sealed Feather is never edited",
            "never marks ready or merges",
            "`NOT_MEASURED`",
            "Mandatory Sunset Preview and approval",
        ):
            self.assertIn(phrase, contract)


if __name__ == "__main__":
    unittest.main()
