from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from tools.atlas_lifecycle.errors import LifecycleError
from tools.atlas_lifecycle.jsonio import canonical_bytes
from tools.atlas_lifecycle.repository import observed_head
from tools.atlas_lifecycle.sunset import generate_sunset_candidate, verify_sunset_candidate


ROOT = Path(__file__).resolve().parents[2]
CANONICAL_DIRS = (
    "feathers",
    "quest-emberlines",
    "quest-checkpoints",
    "sunsets",
    "sunrises",
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_tree() -> dict[str, str]:
    values: dict[str, str] = {}
    for name in CANONICAL_DIRS:
        directory = ROOT / "lifecycle" / name
        if directory.is_dir():
            for path in sorted(directory.iterdir()):
                if path.is_file():
                    values[path.relative_to(ROOT).as_posix()] = digest(path)
    return values


def references() -> list[dict]:
    return [
        {
            "ref_id": "repairing-prime-source",
            "authority": "CANONICAL_SOURCE",
            "uri": "quests/repairing-prime.md",
        },
        {
            "ref_id": "lifecycle-contract",
            "authority": "CANONICAL_SOURCE",
            "uri": "lifecycle/lifecycle-contract.md",
        },
    ]


def request(scope_type: str) -> dict:
    quest_scope = (
        {"scope_type": "ADMITTED_QUEST", "quest_id": "repairing-prime"}
        if scope_type == "ADMITTED_QUEST"
        else {"scope_type": "NON_QUEST", "work_scope": "Harmless non-Quest Sunset test."}
    )
    durable = references()
    if scope_type == "NON_QUEST":
        durable = [item for item in durable if item["uri"] != "quests/repairing-prime.md"]
    return {
        "schema_id": "atlas.lifecycle.sunset-request",
        "schema_version": "2.0.0",
        "authority": "PUBLIC_CLEAN_REQUEST",
        "request_id": f"sunset-test-{scope_type.lower().replace('_', '-')}",
        "expected_main_sha": observed_head(ROOT),
        "project_id": "project-codex",
        "operation_id": "operation-source-governance",
        "quest_scope": quest_scope,
        "campaign": "rp-c08",
        "mission": "aj10-cap022-live-acceptance-r03",
        "gate": "aj10-cap022-live-acceptance",
        "context_summary": "Harmless exact-pair Sunset candidate test.",
        "completion_assessment": "The bounded candidate is ready for read-only verification.",
        "decisions": ["Require exactly one new sealed Feather."],
        "open_items": ["Do not publish from this unit test."],
        "current_position": "Candidate generation is under deterministic test.",
        "unresolved_blockers": ["Canonical publication remains separately gated."],
        "next_safe_action": "Verify the temporary candidate set.",
        "next_approval_gate": "No canonical write is authorized.",
        "next_gate": "Exact temporary readback.",
        "durable_source_references": durable,
        "evidence_pointers": [],
        "protected_data": {
            "classification": "INTERNAL_CLEAN",
            "clean_summary": "The test contains no protected values.",
            "protected_pointers": [],
        },
        "lesson_harvest": {
            "schema_id": "atlas.lifecycle.lesson-harvest",
            "schema_version": "1.0.0",
            "observations": [
                {
                    "key": "exact-cardinality",
                    "observation": "Full Sunset requires one Feather, Sunset, and Sunrise.",
                    "disposition": "LOCAL_ONLY",
                    "golden_wing_id": None,
                    "rationale": "The candidate test preserves the exact transaction invariant.",
                }
            ],
            "no_lesson_reason": None,
        },
    }


class SunsetCandidateTests(unittest.TestCase):
    def write_request(self, parent: Path, value: dict) -> Path:
        path = parent / "request.json"
        path.write_bytes(canonical_bytes(value))
        return path

    def test_admitted_quest_invocation_has_exact_cardinality(self) -> None:
        before = canonical_tree()
        with tempfile.TemporaryDirectory() as temp:
            parent = Path(temp)
            result = generate_sunset_candidate(
                ROOT,
                self.write_request(parent, request("ADMITTED_QUEST")),
                parent / "candidate",
            )
            self.assertEqual(result["status"], "PASS")
            self.assertEqual(result["assertions"]["feathers"], 1)
            self.assertEqual(result["assertions"]["sunsets"], 1)
            self.assertEqual(result["assertions"]["sunrises"], 1)
            self.assertEqual(result["assertions"]["quest_emberlines"], 1)
            self.assertEqual(result["assertions"]["quest_checkpoints"], 1)
            verified = verify_sunset_candidate(ROOT, parent / "candidate")
            self.assertEqual(verified["candidate_set_digest"], result["candidate_set_digest"])
            bundle = json.loads((parent / "candidate" / "candidate-bundle.json").read_text())
            feather = next(
                item["record"] for item in bundle["records"]
                if item["record"]["schema_id"] == "atlas.lifecycle.feather"
            )
            sunset = next(
                item["record"] for item in bundle["records"]
                if item["record"]["schema_id"] == "atlas.lifecycle.sunset"
            )
            self.assertEqual(feather["schema_version"], "2.0.0")
            self.assertEqual(sunset["schema_version"], "2.0.0")
            self.assertEqual(sunset["lesson_harvest_summary"]["observation_keys"], ["exact-cardinality"])
            emberline_entries = [
                item for item in bundle["records"]
                if item["record"]["schema_id"] == "atlas.lifecycle.quest-emberline"
            ]
            self.assertEqual(len(emberline_entries), 1)
            living = emberline_entries[0]["record"]
            current_path = ROOT / "lifecycle/quest-emberlines/QEM-R6QKBDHLY7I7PVVEKIGTZFMZZT.json"
            current = json.loads(current_path.read_text(encoding="utf-8"))
            self.assertEqual(living["record_id"], current["record_id"])
            self.assertEqual(living["schema_version"], "2.0.0")
            self.assertEqual(living["quest_revision"], current["quest_revision"] + 1)
            self.assertEqual(
                living["revision_parent_digest"],
                "sha256:" + hashlib.sha256(current_path.read_bytes()).hexdigest(),
            )
            self.assertEqual(
                emberline_entries[0]["path"],
                f'lifecycle/quest-emberlines/{current["record_id"]}.json',
            )
            self.assertEqual(living["journey_entries"][-1]["entry_type"], "MAIN")
            self.assertEqual(living["journey_entries"][-1]["scope"], "GATE")
        self.assertEqual(canonical_tree(), before)

    def test_nonquest_invocation_fabricates_no_quest_identity(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            parent = Path(temp)
            result = generate_sunset_candidate(
                ROOT,
                self.write_request(parent, request("NON_QUEST")),
                parent / "candidate",
            )
            self.assertEqual(result["assertions"]["feathers"], 1)
            self.assertEqual(result["assertions"]["sunsets"], 1)
            self.assertEqual(result["assertions"]["sunrises"], 1)
            self.assertEqual(result["assertions"]["quest_emberlines"], 0)
            self.assertEqual(result["assertions"]["quest_checkpoints"], 0)
            bundle = json.loads((parent / "candidate" / "candidate-bundle.json").read_text())
            serialized = json.dumps(bundle["records"], sort_keys=True)
            self.assertNotIn('"quest_id"', serialized)


    def test_stale_transaction_base_rejects_before_output(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            parent = Path(temp)
            value = request("NON_QUEST")
            value["expected_main_sha"] = "0" * 40
            if value["expected_main_sha"] == observed_head(ROOT):
                value["expected_main_sha"] = "f" * 40
            output = parent / "candidate"
            with self.assertRaises(LifecycleError) as raised:
                generate_sunset_candidate(
                    ROOT,
                    self.write_request(parent, value),
                    output,
                )
            self.assertEqual(raised.exception.code, "STALE_STATE")
            self.assertFalse(output.exists())

    def test_existing_output_rejects_without_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            parent = Path(temp)
            output = parent / "candidate"
            output.mkdir()
            with self.assertRaises(LifecycleError) as raised:
                generate_sunset_candidate(
                    ROOT,
                    self.write_request(parent, request("NON_QUEST")),
                    output,
                )
            self.assertEqual(raised.exception.code, "CANDIDATE_OUTPUT_EXISTS")

    def test_repository_output_rejects(self) -> None:
        request_path = ROOT / "sunset-test-request.json"
        request_path.write_bytes(canonical_bytes(request("NON_QUEST")))
        try:
            with self.assertRaises(LifecycleError) as raised:
                generate_sunset_candidate(ROOT, request_path, ROOT / "sunset-test-output")
            self.assertEqual(raised.exception.code, "CANDIDATE_REPOSITORY_WRITE")
        finally:
            request_path.unlink(missing_ok=True)

    def test_tampered_bundle_rejects(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            parent = Path(temp)
            generate_sunset_candidate(
                ROOT,
                self.write_request(parent, request("NON_QUEST")),
                parent / "candidate",
            )
            path = parent / "candidate" / "candidate-bundle.json"
            bundle = json.loads(path.read_text())
            bundle["request_id"] = "tampered-request"
            path.write_bytes(canonical_bytes(bundle))
            with self.assertRaises(LifecycleError) as raised:
                verify_sunset_candidate(ROOT, parent / "candidate")
            self.assertEqual(raised.exception.code, "SUNSET_CANDIDATE_BINDING")


if __name__ == "__main__":
    unittest.main()
