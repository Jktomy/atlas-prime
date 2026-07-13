from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
THREAD_ENGINE_ROOT = ROOT / "tools" / "thread-engine"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(THREAD_ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(THREAD_ENGINE_ROOT))

from production_adapter.adapter import execute_mission
from production_adapter.authority import MissionError, load_mission
from production_adapter.generated_checkpoint import (
    GeneratedCheckpointError,
    verify_generated_checkpoint_environment,
    verify_generated_checkpoint_history,
    verify_generated_checkpoint_package,
)
from production_adapter.git_runner import Completed, GitRunnerError
from production_adapter.receipt import stable_json
from tools.build_index import APPROVED_OUTPUTS, build_outputs, output_bytes
from tools.generated_checkpoint.core import (
    PreparationError,
    build_hash_register,
    load_github_event_inputs,
    prepare_package,
    reconcile_registers,
    git_blob_sha,
)


BASE = "a" * 40
WORKFLOW_REF = "Jktomy/atlas-prime/.github/workflows/generated-checkpoint-publisher.yml@refs/heads/main"
MISSION_ID = "RP-C06-GENERATED-UNIT-001"
NONCE = "rp-c06-generated-unit-replay-nonce-001"
HEAD = "b" * 40


class GeneratedRouteRunner:
    def __init__(self, mission: dict, source_root: Path, *, branch_exists: bool = False) -> None:
        self.mission = mission
        self.source_root = source_root
        self.branch_exists = branch_exists
        self.committed = False
        self.calls: list[tuple[str, ...]] = []

    def run(self, args: list[str], cwd: Path | None = None) -> Completed:
        self.calls.append(tuple(args))
        if args[:2] == ["git", "ls-remote"] and args[-1] == "refs/heads/main":
            return Completed(tuple(args), 0, f"{BASE}\trefs/heads/main\n", "")
        if args[:2] == ["git", "ls-remote"]:
            output = f"{HEAD}\trefs/heads/{self.mission['branch']}\n" if self.branch_exists else ""
            return Completed(tuple(args), 0, output, "")
        if args[:4] == ["gh", "pr", "list", "--repo"]:
            return Completed(tuple(args), 0, "[]", "")
        if args[:2] == ["git", "clone"]:
            shutil.copytree(self.source_root, Path(args[-1]), dirs_exist_ok=True)
            return Completed(tuple(args), 0, "", "")
        if args[:2] == ["git", "rev-parse"] and args[-1] == "HEAD":
            return Completed(tuple(args), 0, (HEAD if self.committed else BASE) + "\n", "")
        if args[:2] == ["git", "rev-parse"] and args[-1].endswith("generated-checkpoint-publisher.yml"):
            return Completed(tuple(args), 0, self.mission["generated_checkpoint_profile"]["workflow_blob_sha"] + "\n", "")
        if args[:2] == ["git", "hash-object"]:
            target = cwd.joinpath(*args[-1].split("/"))
            return Completed(tuple(args), 0, git_blob_sha(target.read_bytes()) + "\n", "")
        if args[:2] == ["git", "status"]:
            return Completed(tuple(args), 0, "", "")
        if args[:2] == ["git", "switch"] or args[:2] == ["git", "add"]:
            return Completed(tuple(args), 0, "", "")
        if args[:2] == ["git", "diff"] and "--name-only" in args:
            return Completed(tuple(args), 0, "\n".join(self.mission["declared_paths"]) + "\n", "")
        if args[:2] == ["git", "diff"]:
            return Completed(tuple(args), 0, "", "")
        if args[:2] == ["git", "commit"]:
            self.committed = True
            return Completed(tuple(args), 0, "commit\n", "")
        if args[:2] == ["git", "rev-list"]:
            return Completed(tuple(args), 0, f"{HEAD} {BASE}\n", "")
        if args[:2] == ["git", "log"]:
            return Completed(tuple(args), 0, self.mission["commit_message"] + "\n", "")
        if args[:2] == ["git", "show"]:
            return Completed(tuple(args), 0, "c" * 40 + "\n", "")
        if args[:2] == ["git", "push"]:
            return Completed(tuple(args), 0, "", "")
        if args[:3] == ["gh", "pr", "create"]:
            return Completed(tuple(args), 0, "https://github.com/Jktomy/atlas-prime/pull/999\n", "")
        if args[:3] == ["gh", "pr", "view"]:
            data = {
                "number": 999,
                "url": "https://github.com/Jktomy/atlas-prime/pull/999",
                "state": "OPEN",
                "isDraft": True,
                "baseRefName": "main",
                "baseRefOid": BASE,
                "headRefName": self.mission["branch"],
                "headRefOid": HEAD,
                "title": self.mission["pr_title"],
                "body": self.mission["pr_body"],
                "commits": [{"oid": HEAD}],
                "files": [{"path": path} for path in self.mission["declared_paths"]],
                "comments": [],
                "reviews": [],
            }
            return Completed(tuple(args), 0, json.dumps(data), "")
        if args[:3] == ["gh", "api", "graphql"]:
            data = {"data": {"repository": {"pullRequests": {"nodes": [{
                "number": 999,
                "headRefName": self.mission["branch"],
                "reviewThreads": {"totalCount": 0},
            }]}}}}
            return Completed(tuple(args), 0, json.dumps(data), "")
        raise GitRunnerError(f"unexpected generated-route command: {args}")


class GeneratedCheckpointTests(unittest.TestCase):
    def make_repo(self, root: Path) -> None:
        root.mkdir(parents=True)
        (root / "README.md").write_text("# Prime before\n", encoding="utf-8", newline="\n")
        outputs, _ = build_outputs(root)
        generated = root / "generated"
        generated.mkdir()
        for name in APPROVED_OUTPUTS:
            (generated / name).write_bytes(output_bytes(outputs[name]))
        (root / "README.md").write_text("# Prime after\n", encoding="utf-8", newline="\n")
        workflow = root / ".github" / "workflows" / "generated-checkpoint-publisher.yml"
        workflow.parent.mkdir(parents=True)
        workflow.write_text("name: Generated checkpoint publisher\n", encoding="utf-8", newline="\n")

    def build_evidence(self, root: Path) -> tuple[Path, Path, dict]:
        register, _ = build_hash_register(
            root,
            mission_id=MISSION_ID,
            base_sha=BASE,
            replay_nonce=NONCE,
            workflow_ref=WORKFLOW_REF,
            workflow_source_sha=BASE,
            workflow_run_id="123456789",
            workflow_run_attempt="1",
        )
        ubuntu = root.parent / "ubuntu.json"
        windows = root.parent / "windows.json"
        ubuntu.write_text(stable_json(register), encoding="utf-8", newline="\n")
        windows.write_text(stable_json(register), encoding="utf-8", newline="\n")
        reconciliation = reconcile_registers(ubuntu, windows)
        reconciliation_path = root.parent / "reconciliation.json"
        reconciliation_path.write_text(stable_json(reconciliation), encoding="utf-8", newline="\n")
        return ubuntu, reconciliation_path, register

    def test_register_is_byte_identical_and_package_is_exact(self) -> None:
        with tempfile.TemporaryDirectory(prefix="generated-checkpoint-") as raw:
            root = Path(raw) / "repo"
            self.make_repo(root)
            register_path, reconciliation_path, _ = self.build_evidence(root)
            package = Path(raw) / "package"
            mission = prepare_package(
                root,
                register_path,
                reconciliation_path,
                package,
                replay_nonce=NONCE,
                public_clean_confirmation="PUBLIC_CLEAN_CONFIRMED",
            )
            loaded = load_mission(package / "mission.json")
            self.assertEqual(loaded.mission_id, MISSION_ID)
            self.assertEqual(len(loaded.operations), 5)
            self.assertEqual(loaded.generated_checkpoint_profile["profile_id"], "GENERATED_CHECKPOINT_V1")
            evidence = verify_generated_checkpoint_package(loaded.generated_checkpoint_profile, package)
            self.assertTrue(evidence["ubuntu_windows_byte_parity"])
            self.assertFalse(evidence["preparer_git_or_github_invocation"])
            self.assertEqual(mission["branch"], loaded.branch)

    def test_parity_payload_identity_and_profile_drift_reject(self) -> None:
        with tempfile.TemporaryDirectory(prefix="generated-checkpoint-") as raw:
            root = Path(raw) / "repo"
            self.make_repo(root)
            register_path, reconciliation_path, _ = self.build_evidence(root)
            windows = Path(raw) / "windows-drift.json"
            windows.write_bytes(register_path.read_bytes() + b" ")
            with self.assertRaises(PreparationError) as raised:
                reconcile_registers(register_path, windows)
            self.assertEqual(raised.exception.code, "GENERATED_CHECKPOINT_PARITY")

            package = Path(raw) / "package"
            mission = prepare_package(
                root,
                register_path,
                reconciliation_path,
                package,
                replay_nonce=NONCE,
                public_clean_confirmation="PUBLIC_CLEAN_CONFIRMED",
            )
            payload = package / "payloads" / "generated" / APPROVED_OUTPUTS[0]
            payload.write_bytes(payload.read_bytes() + b"tamper\n")
            with self.assertRaises(GeneratedCheckpointError) as raised:
                verify_generated_checkpoint_package(mission["generated_checkpoint_profile"], package)
            self.assertEqual(raised.exception.code, "GENERATED_CHECKPOINT_PAYLOAD")

            mission["generated_checkpoint_profile"]["automatic_merge"] = True
            mission["mission_sha256"] = "0" * 64
            from production_adapter.receipt import sha256_bytes
            mission["mission_sha256"] = sha256_bytes(stable_json(mission).encode("utf-8"))
            (package / "mission.json").write_text(stable_json(mission), encoding="utf-8", newline="\n")
            with self.assertRaises(MissionError) as raised:
                load_mission(package / "mission.json")
            self.assertEqual(raised.exception.code, "GENERATED_CHECKPOINT_FORBIDDEN_ACTION")

    def test_hosted_environment_is_exact(self) -> None:
        with tempfile.TemporaryDirectory(prefix="generated-checkpoint-") as raw:
            root = Path(raw) / "repo"
            self.make_repo(root)
            register_path, reconciliation_path, _ = self.build_evidence(root)
            package = Path(raw) / "package"
            mission = prepare_package(
                root,
                register_path,
                reconciliation_path,
                package,
                replay_nonce=NONCE,
                public_clean_confirmation="PUBLIC_CLEAN_CONFIRMED",
            )
            profile = mission["generated_checkpoint_profile"]
            environment = {
                "GITHUB_ACTIONS": "true",
                "GITHUB_REPOSITORY": "Jktomy/atlas-prime",
                "GITHUB_REPOSITORY_OWNER": "Jktomy",
                "GITHUB_ACTOR": "Jktomy",
                "GITHUB_TRIGGERING_ACTOR": "Jktomy",
                "GITHUB_EVENT_NAME": "workflow_dispatch",
                "GITHUB_REF": "refs/heads/main",
                "GITHUB_WORKFLOW_REF": WORKFLOW_REF,
                "GITHUB_WORKFLOW_SHA": BASE,
                "GITHUB_SHA": BASE,
                "GITHUB_RUN_ID": "123456789",
                "GITHUB_RUN_ATTEMPT": "1",
                "GH_TOKEN": "present-only-in-test",
            }
            evidence = verify_generated_checkpoint_environment(profile, environment)
            self.assertTrue(evidence["token_present"])
            environment["GITHUB_TRIGGERING_ACTOR"] = "Other"
            with self.assertRaises(GeneratedCheckpointError) as raised:
                verify_generated_checkpoint_environment(profile, environment)
            self.assertEqual(raised.exception.code, "GENERATED_CHECKPOINT_ENVIRONMENT")

    def test_singular_thread_engine_route_creates_exact_draft_and_replay_rejects(self) -> None:
        with tempfile.TemporaryDirectory(prefix="generated-checkpoint-") as raw:
            root = Path(raw) / "repo"
            self.make_repo(root)
            register_path, reconciliation_path, _ = self.build_evidence(root)
            package = Path(raw) / "package"
            mission = prepare_package(
                root,
                register_path,
                reconciliation_path,
                package,
                replay_nonce=NONCE,
                public_clean_confirmation="PUBLIC_CLEAN_CONFIRMED",
            )
            environment = {
                "GITHUB_ACTIONS": "true",
                "GITHUB_REPOSITORY": "Jktomy/atlas-prime",
                "GITHUB_REPOSITORY_OWNER": "Jktomy",
                "GITHUB_ACTOR": "Jktomy",
                "GITHUB_TRIGGERING_ACTOR": "Jktomy",
                "GITHUB_EVENT_NAME": "workflow_dispatch",
                "GITHUB_REF": "refs/heads/main",
                "GITHUB_WORKFLOW_REF": WORKFLOW_REF,
                "GITHUB_WORKFLOW_SHA": BASE,
                "GITHUB_SHA": BASE,
                "GITHUB_RUN_ID": "123456789",
                "GITHUB_RUN_ATTEMPT": "1",
                "GH_TOKEN": "present-only-in-test",
            }
            active = {
                "implementation_state": "THREAD_ENGINE_ACTIVE_MISSION_SCOPED",
                "production_execution_authorized": True,
                "proof_required": False,
                "standing_authority": False,
                "automatic_merge": False,
                "direct_main": False,
            }
            runner = GeneratedRouteRunner(mission, root)
            with patch.dict(os.environ, environment, clear=False), patch(
                "production_adapter.adapter.load_activation_state", return_value=active
            ):
                receipt = execute_mission(
                    package / "mission.json",
                    mission_scoped=True,
                    execute_draft_pr=True,
                    mission_sha256=mission["mission_sha256"],
                    generated_checkpoint_route=True,
                    work_root=Path(raw) / "nested" / "thread-engine-work",
                    package_root=package,
                    runner=runner,
                )
            self.assertEqual(receipt["result"], "SUCCESS")
            self.assertTrue(receipt["pr_readback"]["isDraft"])
            self.assertEqual(receipt["pr_readback"]["baseRefOid"], BASE)
            self.assertEqual(receipt["pr_readback"]["headRefOid"], HEAD)
            self.assertTrue(receipt["generated_checkpoint_profile"]["fresh_clone_reproduction"]["fresh_clone_reproduction"])
            self.assertEqual(len([call for call in runner.calls if call[:3] == ("gh", "pr", "create")]), 1)

            replay_runner = GeneratedRouteRunner(mission, root, branch_exists=True)
            with patch.dict(os.environ, environment, clear=False), patch(
                "production_adapter.adapter.load_activation_state", return_value=active
            ), self.assertRaises(Exception) as raised:
                execute_mission(
                    package / "mission.json",
                    mission_scoped=True,
                    execute_draft_pr=True,
                    mission_sha256=mission["mission_sha256"],
                    generated_checkpoint_route=True,
                    work_root=Path(raw),
                    package_root=package,
                    runner=replay_runner,
                )
            self.assertEqual(getattr(raised.exception, "code", None), "BRANCH_EXISTS")
            self.assertEqual(raised.exception.receipt["result"], "REJECTED")
            self.assertEqual(len([call for call in replay_runner.calls if call[:2] == ("git", "push")]), 0)

    def test_history_rejects_open_collision_and_each_replay_axis(self) -> None:
        with tempfile.TemporaryDirectory(prefix="generated-checkpoint-") as raw:
            root = Path(raw) / "repo"
            self.make_repo(root)
            register_path, reconciliation_path, _ = self.build_evidence(root)
            mission = prepare_package(
                root,
                register_path,
                reconciliation_path,
                Path(raw) / "package",
                replay_nonce=NONCE,
                public_clean_confirmation="PUBLIC_CLEAN_CONFIRMED",
            )
            profile = mission["generated_checkpoint_profile"]
            base_item = {
                "number": 800,
                "state": "MERGED",
                "isDraft": False,
                "headRefName": "generated/checkpoint-historical-000000000000",
                "headRefOid": "c" * 40,
                "title": "generated: deterministic checkpoint HISTORICAL-MISSION",
                "body": "Historical checkpoint.\n",
            }
            open_item = dict(base_item, state="OPEN")
            with self.assertRaises(GeneratedCheckpointError) as raised:
                verify_generated_checkpoint_history(profile, [open_item])
            self.assertEqual(raised.exception.code, "GENERATED_CHECKPOINT_PR_COLLISION")

            mission_replay = dict(base_item, title=mission["pr_title"])
            with self.assertRaises(GeneratedCheckpointError) as raised:
                verify_generated_checkpoint_history(profile, [mission_replay])
            self.assertEqual(raised.exception.code, "GENERATED_CHECKPOINT_MISSION_REPLAY")

            nonce_replay = dict(
                base_item,
                body=f"- Replay identity: `sha256:{profile['replay_nonce_sha256']}`\n",
            )
            with self.assertRaises(GeneratedCheckpointError) as raised:
                verify_generated_checkpoint_history(profile, [nonce_replay])
            self.assertEqual(raised.exception.code, "GENERATED_CHECKPOINT_NONCE_REPLAY")

            evidence = verify_generated_checkpoint_history(profile, [base_item])
            self.assertEqual(evidence["checkpoint_entries_checked"], 1)

    def test_preparer_has_no_process_or_github_route(self) -> None:
        source = (ROOT / "tools" / "generated_checkpoint" / "core.py").read_text(encoding="utf-8")
        self.assertNotIn("subprocess", source)
        self.assertNotIn("gh pr", source)
        self.assertNotIn("git ", source.casefold())

    def test_github_event_inputs_are_closed_without_workflow_echo(self) -> None:
        with tempfile.TemporaryDirectory(prefix="generated-checkpoint-") as raw:
            event_path = Path(raw) / "event.json"
            inputs = {
                "base_sha": BASE,
                "mission_id": MISSION_ID,
                "replay_nonce": NONCE,
                "public_clean_confirmation": "PUBLIC_CLEAN_CONFIRMED",
            }
            event_path.write_text(json.dumps({"inputs": inputs}), encoding="utf-8", newline="\n")
            self.assertEqual(load_github_event_inputs(event_path), inputs)
            event_path.write_text(json.dumps({"inputs": {**inputs, "extra": "rejected"}}), encoding="utf-8", newline="\n")
            with self.assertRaises(PreparationError) as raised:
                load_github_event_inputs(event_path)
            self.assertEqual(raised.exception.code, "GENERATED_CHECKPOINT_EVENT")


if __name__ == "__main__":
    unittest.main()
