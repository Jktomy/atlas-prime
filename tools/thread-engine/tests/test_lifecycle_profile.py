from __future__ import annotations

import copy
import hashlib
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


THREAD_ENGINE_ROOT = Path(__file__).resolve().parents[1]
PRIME_ROOT = THREAD_ENGINE_ROOT.parents[1]
TESTS_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(TESTS_ROOT))
sys.path.insert(0, str(THREAD_ENGINE_ROOT))
sys.path.insert(0, str(PRIME_ROOT))

from production_adapter.adapter import AdapterError, execute_mission
from production_adapter.authority import MissionError, validate_mission
from production_adapter.lifecycle_profile import (
    LifecycleProfileError,
    reject_lifecycle_replay,
    verify_lifecycle_candidate_package,
)
from production_adapter.receipt import declared_state_hash, sha256_bytes, stable_json, tree_hash
from tools.atlas_lifecycle.candidate import generate_event_candidate
from tools.atlas_lifecycle.jsonio import canonical_bytes, load_bounded, stable_record_id
from tools.atlas_lifecycle.schema import SchemaValidator

from test_production_adapter import (
    ACTIVE_STATE,
    BASE,
    FakeRunner,
    add_aegis_break_authority,
    base_mission,
    bind_mission,
    sha,
    write_json,
)


EVENT_PATH = "lifecycle/events/found-silverlight-gate-progress-r01.json"


def fingerprint(data: bytes) -> str:
    return f"sha256:{hashlib.sha256(data).hexdigest()}"


def file_fingerprint(path: Path) -> str:
    return fingerprint(path.read_bytes())


def write_canonical(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_bytes(value))


def build_candidate_inputs(repo: Path) -> tuple[dict, Path, Path, Path]:
    event = copy.deepcopy(load_bounded(PRIME_ROOT / "lifecycle/fixtures/lifecycle-event-checkpoint.json"))
    event["authority"] = "CANONICAL_RECORD"
    event["route"]["route_authority"] = "AEGIS_BREAK_THREAD_ENGINE_PROTECTED"
    event["route"]["allowed_paths"] = [EVENT_PATH]
    event["expectations"]["expected_main_sha"] = BASE
    event["record_id"] = stable_record_id(event)
    expected = event["expectations"]

    trust = {
        "schema_id": "atlas.lifecycle.event-trust-root",
        "schema_version": "1.0.0",
        "trust_root_id": "fixture-event-trust-root",
        "expected_main_sha": BASE,
        "expected_entity_revision": expected["expected_entity_revision"],
        "expected_quest_revision": expected["expected_quest_revision"],
        "accepted_event_schema_id": "atlas.lifecycle.event",
        "accepted_event_schema_digest": file_fingerprint(repo / "lifecycle/schemas/lifecycle-event-v1.schema.json"),
        "acceptance_contract_ref": {
            "ref_id": "lifecycle-event-contract",
            "authority": "CANONICAL_SOURCE",
            "uri": "lifecycle/lifecycle-event-contract.md",
        },
        "acceptance_contract_digest": file_fingerprint(repo / "lifecycle/lifecycle-event-contract.md"),
        "expected_evidence_sha": event["evidence"]["exact_subject_sha"],
        "allowed_route_authority": event["route"]["route_authority"],
        "allowed_paths": [EVENT_PATH],
    }
    state = {
        "schema_id": "atlas.lifecycle.current-state-snapshot",
        "schema_version": "1.0.0",
        "authority": "TRUSTED_READ_ONLY_STATE",
        "main_sha": BASE,
        "source_fingerprint": expected["expected_source_fingerprint"],
        "entity": {
            "entity_type": event["target"]["entity_type"],
            "entity_id": event["target"]["entity_id"],
            "revision": expected["expected_entity_revision"],
            "state": expected["expected_prior_state"],
            "exists": True,
            "declared_children_complete": True,
            "acceptance_criteria": [],
            "satisfied_criteria": [],
        },
        "quest": {
            "quest_id": event["position"]["quest_id"],
            "revision": expected["expected_quest_revision"],
            "state": "IN_PROGRESS",
            "current_campaign_id": event["position"]["campaign_id"],
            "current_mission_id": event["position"]["mission_id"],
            "current_gate_id": event["position"]["gate_id"],
        },
        "gate": {
            "gate_id": event["position"]["gate_id"],
            "revision": expected["expected_gate_revision"],
            "state": "IN_PROGRESS",
            "latest_checkpoint_id": expected["expected_parent_checkpoint_id"],
            "declared_gate_ids": [event["position"]["gate_id"], "gate-fixture-next"],
        },
        "blockers": [],
        "existing_event_ids": [],
        "replay_keys": [],
        "revision_claim_event_id": None,
    }
    event_path = repo.parent / "event-input.json"
    trust_path = repo / "lifecycle/trust-roots/fixture-event-trust-root.json"
    state_path = repo.parent / "state-input.json"
    write_canonical(event_path, event)
    write_canonical(trust_path, trust)
    write_canonical(state_path, state)
    return event, event_path, trust_path, state_path


def build_lifecycle_mission(tmp: Path) -> tuple[Path, dict, Path]:
    repo = tmp / "fixture-repo"
    shutil.copytree(PRIME_ROOT / "lifecycle", repo / "lifecycle")
    event, event_path, trust_path, state_path = build_candidate_inputs(repo)
    candidate_root = tmp / "payload" / "lifecycle-candidate"
    candidate_root.parent.mkdir()
    result = generate_event_candidate(
        repo,
        event_path,
        trust_path,
        file_fingerprint(trust_path),
        state_path,
        file_fingerprint(state_path),
        candidate_root,
    )

    event_bytes = (candidate_root / "event.json").read_bytes()
    event_digest = fingerprint(event_bytes)
    manifest_digest = file_fingerprint(candidate_root / "candidate-manifest.json")
    receipt_digest = file_fingerprint(candidate_root / "candidate-receipt.json")
    members = [
        {"artifact_path": "event.json", "digest": event_digest},
        {"artifact_path": "candidate-manifest.json", "digest": manifest_digest},
        {"artifact_path": "candidate-receipt.json", "digest": receipt_digest},
    ]
    candidate_set_digest = fingerprint(canonical_bytes({"members": members}))

    candidate_tree = tmp / "candidate-tree"
    (candidate_tree / "lifecycle/events").mkdir(parents=True)
    (candidate_tree / EVENT_PATH).write_bytes(event_bytes)
    final_root = tmp / "final-tree"
    (final_root / "lifecycle/events").mkdir(parents=True)
    (final_root / EVENT_PATH).write_bytes(event_bytes)
    operation = {
        "thread_id": "lifecycle-event",
        "operation": "ADD",
        "path": EVENT_PATH,
        "payload": "event.json",
        "payload_sha256": sha(event_bytes),
        "expected_output_sha256": sha(event_bytes),
    }
    data = base_mission(tmp, [operation], [EVENT_PATH], candidate_tree, final_root)
    data["mission_id"] = "G4-D1-LIFECYCLE-UNIT"
    data["authority_id"] = "G4-D1-LIFECYCLE-AUTH"
    data["branch"] = "source/g4-d1-lifecycle-unit"
    data["payload_root"] = "payload/lifecycle-candidate"
    data["source_blobs"] = {}
    data["candidate_tree_sha256"] = tree_hash(candidate_tree)
    data["final_pathset_sha256"] = declared_state_hash(final_root, (EVENT_PATH,))
    profile = {
        "schema_id": "atlas.lifecycle.construction-profile",
        "schema_version": "1.0.0",
        "profile_id": "LIFECYCLE_CHECKPOINT_V1",
        "event_record_id": event["record_id"],
        "event_class": event["event_class"],
        "event_type": event["event_type"],
        "event_schema_id": event["schema_id"],
        "event_schema_version": event["schema_version"],
        "semantic_author": event["semantic_author"],
        "repository_path": EVENT_PATH,
        "allowed_paths": [EVENT_PATH],
        "candidate_root": "payload/lifecycle-candidate",
        "route_authority": "AEGIS_BREAK_THREAD_ENGINE_PROTECTED",
        "target_entity_type": event["target"]["entity_type"],
        "target_entity_id": event["target"]["entity_id"],
        "expected_main_sha": BASE,
        "expected_entity_revision": event["expectations"]["expected_entity_revision"],
        "expected_quest_revision": event["expectations"]["expected_quest_revision"],
        "expected_gate_revision": event["expectations"]["expected_gate_revision"],
        "expected_parent_event_id": event["expectations"]["expected_parent_checkpoint_id"],
        "expected_source_fingerprint": event["expectations"]["expected_source_fingerprint"],
        "candidate_event_digest": event_digest,
        "candidate_manifest_digest": manifest_digest,
        "candidate_receipt_digest": receipt_digest,
        "candidate_set_digest": candidate_set_digest,
        "trust_root_digest": file_fingerprint(trust_path),
        "state_snapshot_digest": file_fingerprint(state_path),
        "trusted_acceptance_receipt_digest": None,
        "protected_data_classification": event["protected_data"]["classification"],
        "replay_key": event["replay_key"],
        "lineage": event["lineage"],
        "rollback_contract": "Close the draft PR and delete only its source branch.",
        "reversal_contract": "Use a separately accepted lifecycle reversal event.",
        "stop_boundary": "DRAFT_PR_READBACK",
        "write_boundary": {
            "branch_scoped_only": True,
            "canonical_writes": False,
            "direct_main": False,
            "automatic_ready": False,
            "automatic_merge": False,
            "standing_authority": False,
        },
    }
    data["lifecycle_profile"] = profile
    data = add_aegis_break_authority(data, [EVENT_PATH])
    data = bind_mission(data)
    mission_path = tmp / "mission.json"
    write_json(mission_path, data)
    return mission_path, data, candidate_root


class LifecycleProfileTests(unittest.TestCase):
    def setUp(self) -> None:
        self.activation_patcher = patch("production_adapter.adapter.load_activation_state", return_value=dict(ACTIVE_STATE))
        self.activation_patcher.start()

    def tearDown(self) -> None:
        self.activation_patcher.stop()

    def test_profile_executes_one_protected_add_and_stops_at_draft_readback(self) -> None:
        with tempfile.TemporaryDirectory(prefix="atlas-g4d1-") as raw:
            tmp = Path(raw)
            mission_path, data, _ = build_lifecycle_mission(tmp)
            mission = validate_mission(data)
            SchemaValidator(PRIME_ROOT / "lifecycle/schemas").validate_lifecycle_construction_profile(
                mission.lifecycle_profile
            )
            self.assertEqual(mission.lifecycle_profile["event_record_id"], data["lifecycle_profile"]["event_record_id"])
            runner = FakeRunner(data)
            receipt = execute_mission(
                mission_path,
                mission_scoped=True,
                execute_draft_pr=True,
                mission_sha256=data["mission_sha256"],
                aegis_break_protected_route=True,
                aegis_break_authority_id=data["authority_id"],
                work_root=tmp,
                package_root=tmp,
                runner=runner,
            )
            self.assertEqual(receipt["result"], "SUCCESS")
            self.assertEqual(receipt["lifecycle_profile"]["repository_path"], EVENT_PATH)
            self.assertFalse(receipt["lifecycle_profile"]["semantic_validation_performed"])
            self.assertTrue(runner.pr_created)
            self.assertTrue(any(call[:3] == ("gh", "pr", "create") and "--draft" in call for call in runner.calls))
            self.assertFalse(any(call[:3] in {("gh", "pr", "ready"), ("gh", "pr", "merge")} for call in runner.calls))

    def test_candidate_bytes_manifest_receipt_and_route_are_exactly_bound(self) -> None:
        with tempfile.TemporaryDirectory(prefix="atlas-g4d1-") as raw:
            tmp = Path(raw)
            mission_path, data, candidate_root = build_lifecycle_mission(tmp)
            (candidate_root / "event.json").write_bytes((candidate_root / "event.json").read_bytes() + b" ")
            with self.assertRaises(AdapterError) as raised:
                execute_mission(
                    mission_path,
                    mission_scoped=True,
                    execute_draft_pr=True,
                    mission_sha256=data["mission_sha256"],
                    aegis_break_protected_route=True,
                    aegis_break_authority_id=data["authority_id"],
                    work_root=tmp,
                    package_root=tmp,
                    runner=FakeRunner(data),
                )
            self.assertEqual(raised.exception.code, "LIFECYCLE_NONCANONICAL_JSON")
            self.assertFalse(raised.exception.receipt["production_authority_activated"])

        with tempfile.TemporaryDirectory(prefix="atlas-g4d1-") as raw:
            tmp = Path(raw)
            _, data, candidate_root = build_lifecycle_mission(tmp)
            manifest = load_bounded(candidate_root / "candidate-manifest.json")
            manifest["undeclared_authority"] = True
            write_canonical(candidate_root / "candidate-manifest.json", manifest)
            with self.assertRaises(LifecycleProfileError) as raised:
                verify_lifecycle_candidate_package(data["lifecycle_profile"], tmp)
            self.assertEqual(raised.exception.code, "LIFECYCLE_TRUSTED_SCHEMA")

        with tempfile.TemporaryDirectory(prefix="atlas-g4d1-") as raw:
            tmp = Path(raw)
            _, data, candidate_root = build_lifecycle_mission(tmp)
            receipt = load_bounded(candidate_root / "candidate-receipt.json")
            receipt["replay_key"] = "sha256:" + "9" * 64
            write_canonical(candidate_root / "candidate-receipt.json", receipt)
            event_digest = file_fingerprint(candidate_root / "event.json")
            manifest_digest = file_fingerprint(candidate_root / "candidate-manifest.json")
            receipt_digest = file_fingerprint(candidate_root / "candidate-receipt.json")
            profile = copy.deepcopy(data["lifecycle_profile"])
            profile["candidate_receipt_digest"] = receipt_digest
            profile["candidate_set_digest"] = fingerprint(canonical_bytes({
                "members": [
                    {"artifact_path": "event.json", "digest": event_digest},
                    {"artifact_path": "candidate-manifest.json", "digest": manifest_digest},
                    {"artifact_path": "candidate-receipt.json", "digest": receipt_digest},
                ]
            }))
            with self.assertRaises(LifecycleProfileError) as raised:
                verify_lifecycle_candidate_package(profile, tmp)
            self.assertEqual(raised.exception.code, "LIFECYCLE_CANDIDATE_BINDING")

    def test_profile_rejects_revision_route_and_transition_receipt_drift(self) -> None:
        cases = (
            ("expected_entity_revision", 99, "LIFECYCLE_CANDIDATE_BINDING"),
            ("route_authority", "ATHENA_DIRECT", "LIFECYCLE_PROFILE_ROUTE"),
        )
        for field, value, expected_code in cases:
            with self.subTest(field=field), tempfile.TemporaryDirectory(prefix="atlas-g4d1-") as raw:
                _, data, _ = build_lifecycle_mission(Path(raw))
                data["lifecycle_profile"][field] = value
                data = bind_mission(data)
                if expected_code == "LIFECYCLE_CANDIDATE_BINDING":
                    mission = validate_mission(data)
                    with self.assertRaises(LifecycleProfileError) as raised:
                        verify_lifecycle_candidate_package(mission.lifecycle_profile, Path(raw))
                    self.assertEqual(raised.exception.code, expected_code)
                else:
                    with self.assertRaises(MissionError) as raised:
                        validate_mission(data)
                    self.assertEqual(raised.exception.code, expected_code)

        with tempfile.TemporaryDirectory(prefix="atlas-g4d1-") as raw:
            _, data, _ = build_lifecycle_mission(Path(raw))
            data["lifecycle_profile"]["event_class"] = "TRANSITION"
            data["lifecycle_profile"]["profile_id"] = "LIFECYCLE_TRANSITION_V1"
            data["lifecycle_profile"]["event_type"] = "GATE_COMPLETED"
            data = bind_mission(data)
            with self.assertRaises(MissionError) as raised:
                validate_mission(data)
            self.assertEqual(raised.exception.code, "LIFECYCLE_PROFILE_RECEIPT")

    def test_replay_parent_and_concurrent_revision_are_rejected_by_record_identity(self) -> None:
        with tempfile.TemporaryDirectory(prefix="atlas-g4d1-") as raw:
            tmp = Path(raw)
            _, data, candidate_root = build_lifecycle_mission(tmp)
            checkout = tmp / "checkout"
            event_dir = checkout / "lifecycle/events"
            event_dir.mkdir(parents=True)
            event = load_bounded(candidate_root / "event.json")
            write_canonical(event_dir / "different-physical-name.json", event)
            with self.assertRaisesRegex(Exception, "event or replay key already exists"):
                reject_lifecycle_replay(checkout, data["lifecycle_profile"])

            event["semantic_author"] = "athena.replay-fixture"
            event["replay_key"] = "sha256:" + "9" * 64
            event["record_id"] = stable_record_id(event)
            write_canonical(event_dir / "different-physical-name.json", event)
            with self.assertRaisesRegex(Exception, "entity revision is already claimed"):
                reject_lifecycle_replay(checkout, data["lifecycle_profile"])

            event_dir.joinpath("different-physical-name.json").unlink()
            data["lifecycle_profile"]["expected_parent_event_id"] = "LEV-AAAAAAAAAAAAAAAAAAAAAAAAAA"
            with self.assertRaisesRegex(Exception, "expected lifecycle parent is absent"):
                reject_lifecycle_replay(checkout, data["lifecycle_profile"])

    def test_generic_mission_remains_valid_without_lifecycle_profile(self) -> None:
        with tempfile.TemporaryDirectory(prefix="atlas-g4d1-") as raw:
            tmp = Path(raw)
            payload = tmp / "payloads"
            payload.mkdir()
            data_bytes = b"new\n"
            (payload / "add.txt").write_bytes(data_bytes)
            candidate = tmp / "candidate"
            (candidate / "docs").mkdir(parents=True)
            (candidate / "docs/new.txt").write_bytes(data_bytes)
            final_root = tmp / "final"
            (final_root / "docs").mkdir(parents=True)
            (final_root / "docs/new.txt").write_bytes(data_bytes)
            operation = {
                "thread_id": "add",
                "operation": "ADD",
                "path": "docs/new.txt",
                "payload": "add.txt",
                "payload_sha256": sha(data_bytes),
                "expected_output_sha256": sha(data_bytes),
            }
            mission = validate_mission(base_mission(tmp, [operation], ["docs/new.txt"], candidate, final_root))
            self.assertIsNone(mission.lifecycle_profile)


if __name__ == "__main__":
    unittest.main()
