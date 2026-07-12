from __future__ import annotations

import copy
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.atlas_lifecycle.candidate import generate_event_candidate, verify_candidate_set
from tools.atlas_lifecycle.errors import LifecycleError
from tools.atlas_lifecycle.jsonio import canonical_bytes, load_bounded, stable_record_id
from tools.atlas_lifecycle.schema import SchemaValidator


FIXTURES = ROOT / "lifecycle/fixtures"


def digest(path: Path) -> str:
    return f"sha256:{hashlib.sha256(path.read_bytes()).hexdigest()}"


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_bytes(value))


def build_inputs(name: str) -> tuple[dict, dict, dict]:
    event = copy.deepcopy(load_bounded(FIXTURES / name))
    event["authority"] = "CANONICAL_RECORD"
    event["record_id"] = stable_record_id(event)
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
    return event, trust, state


class LifecycleCandidateTests(unittest.TestCase):
    def prepare(self, directory: Path, fixture: str = "lifecycle-event-checkpoint.json"):
        repo = directory / "repo"
        shutil.copytree(ROOT / "lifecycle", repo / "lifecycle")
        event, trust, state = build_inputs(fixture)
        event_path = directory / "event-input.json"
        trust_path = repo / "lifecycle/trust-roots/fixture-event-trust-root.json"
        state_path = directory / "state-input.json"
        write_json(event_path, event)
        write_json(trust_path, trust)
        write_json(state_path, state)
        return repo, event, event_path, trust_path, state_path

    def generate(self, directory: Path, output_name: str = "candidate-one"):
        repo, event, event_path, trust_path, state_path = self.prepare(directory)
        output = directory / output_name
        result = generate_event_candidate(
            repo,
            event_path,
            trust_path,
            digest(trust_path),
            state_path,
            digest(state_path),
            output,
        )
        return repo, event, event_path, trust_path, state_path, output, result

    def verify_set(
        self,
        repo: Path,
        event: dict,
        trust_path: Path,
        state_path: Path,
        output: Path,
    ) -> str:
        return verify_candidate_set(
            output,
            repo / "lifecycle/schemas",
            expected_event_id=event["record_id"],
            expected_repository_path=event["route"]["allowed_paths"][0],
            expected_trust_root_digest=digest(trust_path),
            expected_state_digest=digest(state_path),
        )

    def test_exact_candidate_manifest_and_receipt_bind_id_path_and_locks(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            repo, event, _, trust_path, state_path, output, result = self.generate(directory)
            self.assertEqual(set(path.name for path in output.iterdir()), {
                "event.json", "candidate-manifest.json", "candidate-receipt.json"
            })
            self.assertEqual((output / "event.json").read_bytes(), canonical_bytes(event))
            manifest = load_bounded(output / "candidate-manifest.json")
            receipt = load_bounded(output / "candidate-receipt.json")
            validator = SchemaValidator(repo / "lifecycle/schemas")
            validator.validate_event_candidate_manifest(manifest)
            validator.validate_event_candidate_receipt(receipt)

            declared = event["route"]["allowed_paths"][0]
            self.assertEqual(manifest["event_binding"]["record_id"], event["record_id"])
            self.assertEqual(manifest["event_binding"]["repository_path"], declared)
            self.assertEqual(manifest["allowed_paths"], [declared])
            self.assertEqual(receipt["event_record_id"], event["record_id"])
            self.assertEqual(receipt["repository_path"], declared)
            self.assertEqual(receipt["expected_main_sha"], event["expectations"]["expected_main_sha"])
            self.assertEqual(
                receipt["expected_entity_revision"],
                event["expectations"]["expected_entity_revision"],
            )
            self.assertEqual(receipt["trust_root_digest"], digest(trust_path))
            self.assertEqual(receipt["state_snapshot_digest"], digest(state_path))
            self.assertFalse(receipt["write_boundary"]["canonical_writes"])
            self.assertEqual(receipt["write_boundary"]["github_actions"], [])
            self.assertEqual(result["repository_path"], declared)
            self.assertNotIn(str(directory), json.dumps(result))

    def test_repeat_generation_is_byte_identical_and_repository_unchanged(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            repo, event, event_path, trust_path, state_path = self.prepare(directory)
            before = {
                path.relative_to(repo).as_posix(): path.read_bytes()
                for path in repo.rglob("*") if path.is_file()
            }
            results = []
            trees = []
            for name in ("candidate-one", "candidate-two"):
                output = directory / name
                results.append(generate_event_candidate(
                    repo, event_path, trust_path, digest(trust_path),
                    state_path, digest(state_path), output,
                ))
                trees.append({path.name: path.read_bytes() for path in output.iterdir()})
            after = {
                path.relative_to(repo).as_posix(): path.read_bytes()
                for path in repo.rglob("*") if path.is_file()
            }
            self.assertEqual(trees[0], trees[1])
            self.assertEqual(results[0], results[1])
            self.assertEqual(before, after)
            self.assertEqual(results[0]["writes_performed"], ["SYSTEM_TEMPORARY_DIRECTORY"])
            self.assertFalse(results[0]["canonical_writes"])
            self.assertEqual(results[0]["github_actions"], [])
            self.assertEqual(results[0]["event_id"], event["record_id"])

    def test_checkpoint_and_transition_candidate_classes_generate(self) -> None:
        for fixture in (
            "lifecycle-event-checkpoint.json",
            "lifecycle-event-gate-completed.json",
        ):
            with self.subTest(fixture=fixture), tempfile.TemporaryDirectory() as raw:
                directory = Path(raw)
                repo, event, event_path, trust_path, state_path = self.prepare(directory, fixture)
                output = directory / "candidate"
                result = generate_event_candidate(
                    repo, event_path, trust_path, digest(trust_path),
                    state_path, digest(state_path), output,
                )
                self.assertEqual(result["event_id"], event["record_id"])
                self.assertEqual(load_bounded(output / "event.json")["event_class"], event["event_class"])

    def test_candidate_rejects_noncanonical_input_unsafe_output_and_path_reuse(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            repo, event, event_path, trust_path, state_path = self.prepare(directory)

            fixture = copy.deepcopy(event)
            fixture["authority"] = "NONCANONICAL_FIXTURE"
            fixture["record_id"] = stable_record_id(fixture)
            write_json(event_path, fixture)
            with self.assertRaises(LifecycleError) as raised:
                generate_event_candidate(
                    repo, event_path, trust_path, digest(trust_path),
                    state_path, digest(state_path), directory / "fixture-output",
                )
            self.assertEqual(raised.exception.code, "CANDIDATE_EVENT_AUTHORITY")

            write_json(event_path, event)
            existing = directory / "already-exists"
            existing.mkdir()
            for output, code in (
                (Path("relative-output"), "CANDIDATE_OUTPUT_PATH"),
                (existing, "CANDIDATE_OUTPUT_EXISTS"),
                (repo / "candidate-output", "CANDIDATE_REPOSITORY_WRITE"),
            ):
                with self.subTest(code=code), self.assertRaises(LifecycleError) as raised:
                    generate_event_candidate(
                        repo, event_path, trust_path, digest(trust_path),
                        state_path, digest(state_path), output,
                    )
                self.assertEqual(raised.exception.code, code)

            declared = event["route"]["allowed_paths"][0]
            occupied = repo / Path(*declared.split("/"))
            occupied.parent.mkdir(parents=True, exist_ok=True)
            occupied.write_text("occupied", encoding="utf-8")
            with self.assertRaises(LifecycleError) as raised:
                generate_event_candidate(
                    repo, event_path, trust_path, digest(trust_path),
                    state_path, digest(state_path), directory / "occupied-output",
                )
            self.assertEqual(raised.exception.code, "EVENT_PATH_ALREADY_EXISTS")

    def test_candidate_readback_rejects_tamper_and_extra_members(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            repo, event, _, trust_path, state_path, output, _ = self.generate(directory)
            receipt_path = output / "candidate-receipt.json"
            receipt = load_bounded(receipt_path)
            receipt["repository_path"] = "lifecycle/events/tampered.json"
            write_json(receipt_path, receipt)
            with self.assertRaises(LifecycleError) as raised:
                self.verify_set(repo, event, trust_path, state_path, output)
            self.assertEqual(raised.exception.code, "CANDIDATE_BINDING_MISMATCH")

        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            repo, event, _, trust_path, state_path, output, _ = self.generate(directory)
            (output / "extra.json").write_text("{}\n", encoding="utf-8")
            with self.assertRaises(LifecycleError) as raised:
                self.verify_set(repo, event, trust_path, state_path, output)
            self.assertEqual(raised.exception.code, "CANDIDATE_SET_MEMBERS")

        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            repo, event, _, trust_path, state_path, output, _ = self.generate(directory)
            with self.assertRaises(LifecycleError) as raised:
                verify_candidate_set(
                    output,
                    repo / "lifecycle/schemas",
                    expected_event_id=event["record_id"],
                    expected_repository_path=event["route"]["allowed_paths"][0],
                    expected_trust_root_digest="sha256:" + "f" * 64,
                    expected_state_digest=digest(state_path),
                )
            self.assertEqual(raised.exception.code, "CANDIDATE_TRUST_BINDING")

    def test_cli_generates_only_explicit_temporary_output(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            repo, event, event_path, trust_path, state_path = self.prepare(directory)
            output = directory / "cli-candidate"
            completed = subprocess.run(
                [
                    sys.executable, "-B", "-m", "tools.atlas_lifecycle",
                    "--repo-root", str(repo), "event", "candidate",
                    "--event", str(event_path), "--trust-root", str(trust_path),
                    "--expected-trust-root-digest", digest(trust_path),
                    "--state", str(state_path),
                    "--expected-state-digest", digest(state_path),
                    "--output-dir", str(output),
                ],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            result = json.loads(completed.stdout)
            self.assertEqual(result["status"], "PASS")
            self.assertEqual(result["engine_class"], "SCRIPT_ASSIST_LEVEL_1B")
            self.assertEqual(result["event_id"], event["record_id"])
            self.assertTrue(output.is_dir())

    @unittest.skipUnless(os.name == "nt", "Windows alias parity fixture")
    def test_windows_case_alias_uses_filesystem_identity(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            repo, event, event_path, trust_path, state_path = self.prepare(directory)
            alias_parent = Path(str(directory).swapcase())
            output = alias_parent / "case-alias-candidate"
            result = generate_event_candidate(
                repo,
                event_path,
                trust_path,
                digest(trust_path),
                state_path,
                digest(state_path),
                output,
            )
            self.assertEqual(result["event_id"], event["record_id"])
            self.assertTrue(output.is_dir())

        source = (ROOT / "tools/atlas_lifecycle/candidate.py").read_text(encoding="utf-8")
        self.assertIn("os.path.samefile", source)
        self.assertNotIn("relative_to(temporary_root)", source)


if __name__ == "__main__":
    unittest.main()
