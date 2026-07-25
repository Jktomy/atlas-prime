from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from tools.ciel.engine import (
    CielValidationError,
    validate_absorption_record,
    validate_code_capsule,
    validate_harvest_record,
    validate_registry,
    validate_repository,
)


ROOT = Path(__file__).resolve().parents[2]
HEX = "a" * 64


def load(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


class CielOperationTests(unittest.TestCase):
    def harvest(self) -> dict:
        return {
            "schema_version": "atlas.ciel.harvest-record.v1",
            "record_id": "HARVEST-SYNTHETIC-R01",
            "title": "Synthetic Harvest",
            "source": {
                "kind": "REPOSITORY",
                "locator": "https://example.invalid/repo",
                "revision": "a" * 40,
                "retrieved_at": "2026-07-24T00:00:00Z",
                "license_status": "VERIFIED",
            },
            "observed_at": "2026-07-24T00:00:00Z",
            "source_class": "PUBLIC_CLEAN",
            "verification": {"state": "VERIFIED", "evidence_refs": ["synthetic"], "unresolved": []},
            "claims": [{"claim": "Synthetic only", "status": "VERIFIED", "evidence_refs": ["synthetic"]}],
            "atlas_fit": {
                "current_problem": "Synthetic validation",
                "future_risk": "Synthetic drift",
                "affected_components": ["Operation Ciel"],
                "recommendation": "ABSORB_CANDIDATE",
            },
            "protected_boundary": {"classification": "PUBLIC_CLEAN", "excluded_classes": ["SECRETS"]},
            "status": "REVIEWED",
        }

    def absorption(self) -> dict:
        return {
            "schema_version": "atlas.ciel.absorption-record.v1",
            "absorption_id": "ABSORB-SYNTHETIC-R01",
            "source_harvest_id": "HARVEST-SYNTHETIC-R01",
            "created_at": "2026-07-24T00:00:00Z",
            "findings": [{
                "finding_id": "FINDING-SYNTHETIC",
                "summary": "Synthetic finding",
                "disposition": "PRESERVE",
                "owner": "Project Artemis / Operation Ciel",
                "benefit": "Exercises the schema",
                "risk": "None outside the fixture",
                "validation": ["Schema validation"],
                "rollback": "Remove the fixture",
                "follow_on_required": False,
            }],
            "authority_boundary": {
                "self_promotion": False,
                "build_authorized": False,
                "runtime_authorized": False,
                "permanence_authorized": False,
            },
            "status": "REVIEWED",
        }

    def capsule(self) -> dict:
        return {
            "schema_version": "atlas.rimuru.code-capsule.v1",
            "capsule_id": "CAPSULE-SYNTHETIC-R01",
            "classification": "REFERENCE_ONLY",
            "source": {
                "repository": "owner/repo",
                "revision": "a" * 40,
                "path": "src/example.py",
                "sha256": HEX,
            },
            "license": {
                "spdx_id": "MIT",
                "verified_at": "2026-07-24T00:00:00Z",
                "attribution_required": True,
                "notice": "Synthetic MIT fixture",
            },
            "content": {
                "storage": "INERT_JSON_ONLY",
                "excerpt_sha256": HEX,
                "modifications": [],
            },
            "dependencies": [],
            "security_review": ["No execution"],
            "tests": ["Schema validation"],
            "authority_boundary": {
                "executable": False,
                "runtime_import": False,
                "installation_authorized": False,
                "permanence_authorized": False,
            },
            "status": "REVIEWED",
        }

    def test_canonical_ciel_boundary_and_empty_initial_registry_validate(self) -> None:
        receipt = validate_repository()
        self.assertEqual(receipt["result"], "PASS")
        self.assertEqual(receipt["authority"], "NONCANONICAL_EXTERNAL_INTELLIGENCE")
        self.assertEqual(receipt["entry_count"], 0)
        registry = load("knowledge/rimuru/registry-r01.json")
        self.assertEqual(registry["registry_revision"], 1)
        self.assertEqual(registry["entries"], [])

    def test_closed_record_schemas_and_nonpromotion_validate(self) -> None:
        validate_harvest_record(self.harvest())
        validate_absorption_record(self.absorption())
        validate_code_capsule(self.capsule())

    def test_unresolved_license_and_protected_values_fail_closed(self) -> None:
        capsule = self.capsule()
        capsule["license"]["spdx_id"] = "UNKNOWN"
        with self.assertRaises(CielValidationError):
            validate_code_capsule(capsule)

        harvest = self.harvest()
        harvest["claims"][0]["claim"] = "api_key=secret-value"
        with self.assertRaisesRegex(CielValidationError, "PROTECTED_MATERIAL_REJECTED"):
            validate_harvest_record(harvest)

    def test_registry_rejects_duplicate_source_and_unsafe_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "knowledge" / "rimuru" / "records").mkdir(parents=True)
            payload = self.harvest()
            record_path = root / "knowledge" / "rimuru" / "records" / "synthetic.json"
            record_path.write_text(json.dumps(payload), encoding="utf-8")
            registry = load("knowledge/rimuru/registry-r01.json")
            entry = {
                "record_id": payload["record_id"],
                "record_type": "HARVEST",
                "path": "knowledge/rimuru/records/synthetic.json",
                "source_locator": payload["source"]["locator"],
                "source_revision": payload["source"]["revision"],
                "license_status": "VERIFIED",
                "status": "REVIEWED",
            }
            registry["entries"] = [entry, copy.deepcopy(entry)]
            with self.assertRaisesRegex(CielValidationError, "RIMURU_DUPLICATE"):
                validate_registry(registry, root=root)

            registry["entries"] = [{**entry, "path": "knowledge/rimuru/records/payload.zip"}]
            with self.assertRaises(CielValidationError):
                validate_registry(registry, root=root)

    def test_command_and_lifecycle_terms_are_distinct(self) -> None:
        operation = (ROOT / "operations" / "ciel.md").read_text(encoding="utf-8")
        lesson = (ROOT / "governance" / "lesson-harvest-protocol.md").read_text(encoding="utf-8")
        quest = (ROOT / "quests" / "ciels-awakening.md").read_text(encoding="utf-8")
        for marker in ("HARVEST <X>", "ABSORB <Y>", "Rimuru", "A disposition is analysis, not authority"):
            self.assertIn(marker, operation)
        self.assertIn("Ciel Harvest", lesson)
        self.assertIn("Sunset Lesson Harvest", lesson)
        self.assertIn("M02 is ineligible", quest)


if __name__ == "__main__":
    unittest.main()
