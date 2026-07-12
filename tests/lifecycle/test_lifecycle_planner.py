from __future__ import annotations

import copy
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.atlas_lifecycle.errors import LifecycleError
from tools.atlas_lifecycle.jsonio import load_bounded, stable_record_id
from tools.atlas_lifecycle.planner import plan_event, validate_state_snapshot


FIXTURES = ROOT / "lifecycle/fixtures"


def digest(path: Path) -> str:
    return f"sha256:{hashlib.sha256(path.read_bytes()).hexdigest()}"


def build_inputs(name: str) -> tuple[dict, dict, dict]:
    event = copy.deepcopy(load_bounded(FIXTURES / name))
    expected = event["expectations"]
    transition = event["transition"]
    trust = {
        "schema_id": "atlas.lifecycle.event-trust-root",
        "schema_version": "1.0.0",
        "trust_root_id": "fixture-event-trust-root",
        "expected_main_sha": expected["expected_main_sha"],
        "expected_entity_revision": expected["expected_entity_revision"],
        "expected_quest_revision": expected["expected_quest_revision"],
        "accepted_event_schema_id": "atlas.lifecycle.event",
        "accepted_event_schema_digest": digest(
            ROOT / "lifecycle/schemas/lifecycle-event-v1.schema.json"
        ),
        "acceptance_contract_ref": {
            "ref_id": "lifecycle-event-contract",
            "authority": "CANONICAL_SOURCE",
            "uri": "lifecycle/lifecycle-event-contract.md",
        },
        "acceptance_contract_digest": digest(
            ROOT / "lifecycle/lifecycle-event-contract.md"
        ),
        "expected_evidence_sha": event["evidence"]["exact_subject_sha"],
        "allowed_route_authority": event["route"]["route_authority"],
        "allowed_paths": event["route"]["allowed_paths"],
    }
    state = {
        "schema_id": "atlas.lifecycle.current-state-snapshot",
        "schema_version": "1.0.0",
        "authority": "TRUSTED_READ_ONLY_STATE",
        "main_sha": expected["expected_main_sha"],
        "source_fingerprint": expected["expected_source_fingerprint"],
        "entity": {
            "entity_type": event["target"]["entity_type"],
            "entity_id": event["target"]["entity_id"],
            "revision": expected["expected_entity_revision"],
            "state": expected["expected_prior_state"],
            "exists": True,
            "declared_children_complete": True,
            "acceptance_criteria": [] if transition is None else transition["acceptance_criteria"],
            "satisfied_criteria": [] if transition is None else transition["acceptance_criteria"],
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
            "state": "COMPLETE" if event["event_type"] == "COMPLETION_REVOKED" else "IN_PROGRESS",
            "latest_checkpoint_id": expected["expected_parent_checkpoint_id"],
            "declared_gate_ids": [event["position"]["gate_id"], "gate-fixture-next"],
        },
        "blockers": [],
        "existing_event_ids": [],
        "replay_keys": [],
        "revision_claim_event_id": None,
    }
    if event["event_type"] == "COMPLETION_REVOKED":
        state["existing_event_ids"] = [event["lineage"]["revokes_event_id"]]
    event["record_id"] = stable_record_id(event)
    return event, trust, state


def write_json(path: Path, value: dict) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
        newline="\n",
    )


class LifecyclePlannerTests(unittest.TestCase):
    def run_plan(self, event: dict, trust: dict, state: dict) -> dict:
        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            repo = directory / "repo"
            shutil.copytree(ROOT / "lifecycle", repo / "lifecycle")
            event_path = directory / "event.json"
            trust_path = repo / "lifecycle/trust-roots/fixture-event-trust-root.json"
            state_path = directory / "state.json"
            write_json(event_path, event)
            write_json(trust_path, trust)
            write_json(state_path, state)
            return plan_event(
                repo, event_path, trust_path, digest(trust_path),
                state_path, digest(state_path),
            )

    def assert_code(self, code: str, event: dict, trust: dict, state: dict) -> None:
        with self.assertRaises(LifecycleError) as raised:
            self.run_plan(event, trust, state)
        self.assertEqual(raised.exception.code, code)

    def test_checkpoint_plan_preserves_position_and_is_deterministic(self) -> None:
        event, trust, state = build_inputs("lifecycle-event-checkpoint.json")
        first = self.run_plan(event, trust, state)
        second = self.run_plan(event, trust, state)
        self.assertEqual(first, second)
        self.assertEqual(first["authority"], "READ_ONLY_PLAN")
        self.assertFalse(first["writes_performed"])
        self.assertFalse(first["candidate_bytes_created"])
        self.assertEqual(first["github_actions"], [])
        emberline = first["proposed_deltas"]["emberline"]
        self.assertEqual(emberline["current_gate_id"], state["quest"]["current_gate_id"])
        self.assertEqual(emberline["gate_state"], "IN_PROGRESS")
        self.assertEqual(emberline["latest_checkpoint_id"], event["record_id"])

    def test_gate_completion_and_revocation_propose_only_declared_state(self) -> None:
        completion = build_inputs("lifecycle-event-gate-completed.json")
        result = self.run_plan(*completion)
        delta = result["proposed_deltas"]["emberline"]
        self.assertEqual(delta["completed_gate_id"], "gate-fixture")
        self.assertEqual(delta["current_gate_id"], "gate-fixture-next")

        revocation = build_inputs("lifecycle-event-completion-revoked.json")
        result = self.run_plan(*revocation)
        delta = result["proposed_deltas"]["emberline"]
        self.assertEqual(delta["reopened_gate_id"], "gate-fixture")
        self.assertEqual(
            delta["revoked_event_id"], revocation[0]["lineage"]["revokes_event_id"]
        )

    def test_non_quest_transition_does_not_invent_quest_or_gate_state(self) -> None:
        event, trust, state = build_inputs("lifecycle-event-gate-completed.json")
        event["event_type"] = "SUNSET_CHECKPOINT_ACCEPTED"
        event["target"] = {"entity_type": "SUNSET", "entity_id": "fixture-sunset"}
        event["position"].update(
            {"quest_id": None, "campaign_id": None, "mission_id": None, "gate_id": None}
        )
        event["expectations"].update(
            {
                "expected_quest_revision": None,
                "expected_gate_revision": None,
                "expected_parent_checkpoint_id": None,
                "expected_prior_state": "Sunset candidate is awaiting acceptance.",
            }
        )
        event["transition"]["declared_next_gate"] = None
        event["lineage"]["parent_event_id"] = None
        event["related_record_ids"] = []
        event["record_id"] = stable_record_id(event)
        trust["expected_quest_revision"] = None
        state["entity"].update(
            {
                "entity_type": "SUNSET",
                "entity_id": "fixture-sunset",
                "state": "Sunset candidate is awaiting acceptance.",
            }
        )
        state["quest"] = None
        state["gate"] = None
        result = self.run_plan(event, trust, state)
        self.assertIsNone(result["proposed_deltas"]["emberline"])
        self.assertEqual(
            result["proposed_deltas"]["target"]["entity_id"], "fixture-sunset"
        )

    def test_domain_specific_deltas_are_routed_without_semantic_inference(self) -> None:
        cases = (
            ("FEATHER_ARCHIVED", "FEATHER", "fixture-feather", "feather"),
            ("GOLDEN_WING_EVIDENCE_ADDED", "GOLDEN_WING", "fixture-wing", "golden_wing"),
            ("ACCEPTANCE_PROVEN", "ACCEPTANCE", "fixture-acceptance", "acceptance"),
            ("CAPABILITY_RESTORED", "CAPABILITY", "fixture-capability", "capability"),
        )
        for event_type, entity_type, entity_id, delta_name in cases:
            with self.subTest(event_type=event_type):
                event, trust, state = build_inputs("lifecycle-event-gate-completed.json")
                event["event_type"] = event_type
                event["target"] = {"entity_type": entity_type, "entity_id": entity_id}
                event["expectations"]["expected_prior_state"] = "Declared prior state."
                event["transition"]["declared_next_gate"] = None
                event["record_id"] = stable_record_id(event)
                state["entity"].update(
                    {"entity_type": entity_type, "entity_id": entity_id, "state": "Declared prior state."}
                )
                result = self.run_plan(event, trust, state)
                self.assertIsNotNone(result["proposed_deltas"][delta_name])

        event, trust, state = build_inputs("lifecycle-event-gate-completed.json")
        event["event_type"] = "BLOCKER_RESOLVED"
        event["target"] = {"entity_type": "BLOCKER", "entity_id": "fixture-blocker"}
        event["expectations"]["expected_prior_state"] = "OPEN"
        event["transition"]["declared_next_gate"] = None
        event["transition"]["authorized_blocker_ids"] = ["fixture-blocker"]
        event["record_id"] = stable_record_id(event)
        state["entity"].update(
            {"entity_type": "BLOCKER", "entity_id": "fixture-blocker", "state": "OPEN"}
        )
        state["blockers"] = [{"blocker_id": "fixture-blocker", "state": "OPEN"}]
        result = self.run_plan(event, trust, state)
        self.assertIsNotNone(result["proposed_deltas"]["blocker"])

    def test_stale_replay_concurrency_target_and_prior_state_rejections(self) -> None:
        event, trust, state = build_inputs("lifecycle-event-checkpoint.json")
        cases = []
        changed = copy.deepcopy(state); changed["main_sha"] = "f" * 40
        cases.append(("STALE_MAIN", event, trust, changed))
        changed = copy.deepcopy(state); changed["entity"]["revision"] += 1
        cases.append(("STALE_ENTITY_REVISION", event, trust, changed))
        changed = copy.deepcopy(state); changed["quest"]["revision"] += 1
        cases.append(("STALE_QUEST_REVISION", event, trust, changed))
        changed = copy.deepcopy(state); changed["gate"]["revision"] += 1
        cases.append(("STALE_GATE_REVISION", event, trust, changed))
        changed = copy.deepcopy(state); changed["source_fingerprint"] = "sha256:" + "f" * 64
        cases.append(("STALE_SOURCE_FINGERPRINT", event, trust, changed))
        changed = copy.deepcopy(state); changed["gate"]["latest_checkpoint_id"] = "LEV-AAAAAAAAAAAAAAAAAAAAAAAAAA"
        cases.append(("STALE_PARENT_CHECKPOINT", event, trust, changed))
        changed = copy.deepcopy(state); changed["existing_event_ids"] = [event["record_id"]]
        cases.append(("DUPLICATE_EVENT", event, trust, changed))
        changed = copy.deepcopy(state); changed["replay_keys"] = [event["replay_key"]]
        cases.append(("REPLAYED_EVENT", event, trust, changed))
        changed = copy.deepcopy(state); changed["revision_claim_event_id"] = "LEV-AAAAAAAAAAAAAAAAAAAAAAAAAA"
        cases.append(("CONCURRENT_REVISION", event, trust, changed))
        changed = copy.deepcopy(state); changed["entity"]["exists"] = False
        cases.append(("TARGET_NOT_FOUND", event, trust, changed))
        changed = copy.deepcopy(state); changed["entity"]["state"] = "Different prior state."
        cases.append(("PRIOR_STATE_MISMATCH", event, trust, changed))
        for code, candidate, root, snapshot in cases:
            with self.subTest(code=code):
                self.assert_code(code, candidate, root, snapshot)

    def test_transition_acceptance_next_gate_blocker_and_revocation_rejections(self) -> None:
        event, trust, state = build_inputs("lifecycle-event-gate-completed.json")
        changed = copy.deepcopy(state); changed["entity"]["satisfied_criteria"] = []
        self.assert_code("INCOMPLETE_ACCEPTANCE", event, trust, changed)
        changed = copy.deepcopy(state); changed["gate"]["declared_gate_ids"] = ["gate-fixture"]
        self.assert_code("NEXT_GATE_NOT_FOUND", event, trust, changed)
        changed = copy.deepcopy(state); changed["blockers"] = [{"blocker_id": "fixture-blocker", "state": "OPEN"}]
        self.assert_code("OPEN_BLOCKER", event, trust, changed)
        changed_event = copy.deepcopy(event)
        changed_event["transition"]["authorized_blocker_ids"] = ["fixture-blocker"]
        changed_event["record_id"] = stable_record_id(changed_event)
        self.assert_code("UNAUTHORIZED_BLOCKER_RESOLUTION", changed_event, trust, state)

        revoked, revoked_trust, revoked_state = build_inputs(
            "lifecycle-event-completion-revoked.json"
        )
        revoked_state["existing_event_ids"] = []
        self.assert_code("REVOCATION_LINEAGE", revoked, revoked_trust, revoked_state)

    def test_external_trust_binding_rejects_forged_expectations(self) -> None:
        event, trust, state = build_inputs("lifecycle-event-gate-completed.json")
        cases = []
        changed = copy.deepcopy(trust); changed["accepted_event_schema_digest"] = "sha256:" + "f" * 64
        cases.append(("TRUST_SCHEMA_DIGEST", changed))
        changed = copy.deepcopy(trust); changed["acceptance_contract_digest"] = "sha256:" + "f" * 64
        cases.append(("TRUST_ACCEPTANCE_CONTRACT", changed))
        changed = copy.deepcopy(trust); changed["expected_evidence_sha"] = "f" * 40
        cases.append(("TRUST_EVIDENCE_SHA", changed))
        changed = copy.deepcopy(trust); changed["allowed_route_authority"] = "PHOENIX_BLADE"
        cases.append(("TRUST_ROUTE", changed))
        changed = copy.deepcopy(trust); changed["allowed_paths"] = ["lifecycle/events/other.json"]
        cases.append(("TRUST_ALLOWED_PATHS", changed))
        for code, candidate in cases:
            with self.subTest(code=code):
                self.assert_code(code, event, candidate, state)

    def test_caller_supplied_trust_root_outside_repository_is_rejected(self) -> None:
        event, trust, state = build_inputs("lifecycle-event-checkpoint.json")
        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            repo = directory / "repo"
            shutil.copytree(ROOT / "lifecycle", repo / "lifecycle")
            event_path = directory / "event.json"
            trust_path = directory / "self-supplied-trust.json"
            state_path = directory / "state.json"
            for path, value in ((event_path, event), (trust_path, trust), (state_path, state)):
                write_json(path, value)
            with self.assertRaises(LifecycleError) as raised:
                plan_event(
                    repo, event_path, trust_path, digest(trust_path),
                    state_path, digest(state_path),
                )
            self.assertEqual(raised.exception.code, "TRUST_ROOT_LOCATION")

    def test_changed_trust_root_rejects_against_independent_digest(self) -> None:
        event, trust, state = build_inputs("lifecycle-event-checkpoint.json")
        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            repo = directory / "repo"
            shutil.copytree(ROOT / "lifecycle", repo / "lifecycle")
            event_path = directory / "event.json"
            trust_path = repo / "lifecycle/trust-roots/fixture-event-trust-root.json"
            state_path = directory / "state.json"
            write_json(event_path, event)
            write_json(trust_path, trust)
            write_json(state_path, state)
            expected_digest = digest(trust_path)
            changed = copy.deepcopy(trust)
            changed["expected_entity_revision"] += 1
            write_json(trust_path, changed)
            with self.assertRaises(LifecycleError) as raised:
                plan_event(
                    repo, event_path, trust_path, expected_digest,
                    state_path, digest(state_path),
                )
            self.assertEqual(raised.exception.code, "TRUST_ROOT_DIGEST")

    def test_changed_state_rejects_against_independent_digest(self) -> None:
        event, trust, state = build_inputs("lifecycle-event-checkpoint.json")
        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            repo = directory / "repo"
            shutil.copytree(ROOT / "lifecycle", repo / "lifecycle")
            event_path = directory / "event.json"
            trust_path = repo / "lifecycle/trust-roots/fixture-event-trust-root.json"
            state_path = directory / "state.json"
            write_json(event_path, event)
            write_json(trust_path, trust)
            write_json(state_path, state)
            expected_state_digest = digest(state_path)
            state["entity"]["state"] = "Self-consistent replacement state."
            write_json(state_path, state)
            with self.assertRaises(LifecycleError) as raised:
                plan_event(
                    repo, event_path, trust_path, digest(trust_path),
                    state_path, expected_state_digest,
                )
            self.assertEqual(raised.exception.code, "STATE_DIGEST")

    def test_state_snapshot_is_closed_and_protected_material_rejects(self) -> None:
        _event, _trust, state = build_inputs("lifecycle-event-checkpoint.json")
        validate_state_snapshot(state)
        changed = copy.deepcopy(state); changed["unexpected"] = True
        with self.assertRaises(LifecycleError) as raised:
            validate_state_snapshot(changed)
        self.assertEqual(raised.exception.code, "STATE_SCHEMA")
        changed = copy.deepcopy(state)
        changed["entity"]["state"] = "pass" + "word=fixture-private-value"
        with self.assertRaises(LifecycleError) as raised:
            validate_state_snapshot(changed)
        self.assertEqual(raised.exception.code, "PROTECTED_VALUE_REJECTED")

    def test_cli_is_read_only_and_json_clean(self) -> None:
        event, trust, state = build_inputs("lifecycle-event-checkpoint.json")
        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            repo = directory / "repo"
            shutil.copytree(ROOT / "lifecycle", repo / "lifecycle")
            paths = [
                directory / "event.json",
                repo / "lifecycle/trust-roots/fixture-event-trust-root.json",
                directory / "state.json",
            ]
            for path, value in zip(paths, (event, trust, state), strict=True):
                write_json(path, value)
            before = subprocess.run(
                ["git", "status", "--porcelain"], cwd=ROOT, check=True,
                capture_output=True, text=True,
            ).stdout
            result = subprocess.run(
                [
                    sys.executable, "-B", "-m", "tools.atlas_lifecycle", "--repo-root", str(repo),
                    "event", "plan",
                    "--event", str(paths[0]), "--trust-root", str(paths[1]),
                    "--expected-trust-root-digest", digest(paths[1]),
                    "--state", str(paths[2]),
                    "--expected-state-digest", digest(paths[2]),
                ],
                cwd=ROOT, check=True, capture_output=True, text=True,
            )
            self.assertEqual(json.loads(result.stdout)["status"], "PASS")
            after = subprocess.run(
                ["git", "status", "--porcelain"], cwd=ROOT, check=True,
                capture_output=True, text=True,
            ).stdout
            self.assertEqual(after, before)


if __name__ == "__main__":
    unittest.main()
