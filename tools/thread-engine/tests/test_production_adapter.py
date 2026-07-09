from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

import sys

sys.path.insert(0, str(ROOT))

from production_adapter.adapter import AdapterError, execute_mission
from production_adapter.authority import MissionError, load_mission, operation_set_sha256, validate_mission
from production_adapter.git_runner import Completed, GitRunnerError
from production_adapter.readback import REVIEW_THREAD_QUERY, ReadbackError, verify_pr_readback
from production_adapter.receipt import declared_state_hash, sha256_bytes, tree_hash, stable_json
from production_adapter.recovery import classify_recovery


BASE = "d81fda533e7a15dcb4cc4ae08163dcc1c23f2b05"
HEAD = "2" * 40
WORKBOARD_PATH = "codex/atlas-active-workboard.md"
WORKBOARD_HEADER = (
    "| Last Touched | Atlas Project | Operation | Work Item | Status | Priority | Last Known State | Notes |\n"
    "| --- | --- | --- | --- | --- | --- | --- | --- |\n"
)
WORKBOARD_OLD_ROW = "| 2026-07-08 | Codex | Source Governance / Atlas Prime Rebuild | Thread Engine - Atlas Prime Transition | Ready for Athena | Critical | TE-C01 sealed. | Route proof pending. |"
WORKBOARD_NEW_ROW = "| 2026-07-08 | Codex | Source Governance / Atlas Prime Rebuild | Thread Engine - Atlas Prime Transition | Ready for Athena | Critical | WORKBOARD_ROW_UPDATE_V1 merged and under live proof. | Routine row route proof recorded. |"
WORKBOARD_OLD = (WORKBOARD_HEADER + WORKBOARD_OLD_ROW + "\n").encode("utf-8")
WORKBOARD_NEW = (WORKBOARD_HEADER + WORKBOARD_NEW_ROW + "\n").encode("utf-8")


def sha(data: bytes) -> str:
    return sha256_bytes(data)


def write_json(path: Path, data: dict) -> None:
    path.write_text(stable_json(data), encoding="utf-8")


def bind_mission(data: dict) -> dict:
    bound = json.loads(json.dumps(data))
    bound["mission_sha256"] = "0" * 64
    bound["mission_sha256"] = sha256_bytes(stable_json(bound).encode("utf-8"))
    return bound


def base_mission(tmp: Path, operations: list[dict], declared_paths: list[str], candidate: Path, final_root: Path) -> dict:
    data = {
        "schema_version": "atlas-thread-engine-production-mission-v1",
        "implementation_state": "THREAD_ENGINE_ACTIVE_MISSION_SCOPED",
        "adapter_mode": "DRAFT_PR_ONLY",
        "persistent_writer": "ABSENT",
        "activation_authority": "MISSION_SCOPED",
        "mission_id": "GATE7F-UNIT",
        "authority_id": "GATE7F-UNIT-AUTH",
        "build_identity": "GATE7F-UNIT-BUILD",
        "execute_identity": "GATE7F-UNIT-EXECUTE",
        "mission_sha256": "0" * 64,
        "repository": "Jktomy/atlas-prime",
        "remote_url": "https://github.com/Jktomy/atlas-prime.git",
        "base_sha": BASE,
        "branch": "source/gate-7f-unit",
        "commit_message": "codex: unit production adapter mission",
        "pr_title": "codex: unit production adapter mission",
        "pr_body": "Unit mission.\n",
        "declared_paths": declared_paths,
        "payload_root": "payloads",
        "candidate_tree_sha256": tree_hash(candidate),
        "final_pathset_sha256": declared_state_hash(final_root, tuple(declared_paths)),
        "source_blobs": {"docs/replace.txt": "1" * 40, "docs/delete.txt": "1" * 40},
        "operations": operations,
        "delete_authority_id": "DELETE-AUTH" if any(item["operation"] == "DELETE" for item in operations) else None,
        "network_allowlist": [
            "https://github.com/Jktomy/atlas-prime.git",
            "https://api.github.com/repos/Jktomy/atlas-prime",
        ],
        "receipt_name": "receipt.json",
        "stop_point": "DRAFT_PR_READBACK",
    }
    if data["delete_authority_id"] is None:
        del data["delete_authority_id"]
    return bind_mission(data)


def build_add_replace_delete_mission(tmp: Path, include_delete: bool = True) -> tuple[Path, dict]:
    payloads = tmp / "payloads"
    payloads.mkdir()
    add_data = b"new\n"
    replace_data = b"new replacement\n"
    old_data = b"old\n"
    delete_data = b"delete me\n"
    (payloads / "add.txt").write_bytes(add_data)
    (payloads / "replace.txt").write_bytes(replace_data)
    candidate = tmp / "candidate"
    (candidate / "docs").mkdir(parents=True)
    (candidate / "docs" / "new.txt").write_bytes(add_data)
    (candidate / "docs" / "replace.txt").write_bytes(replace_data)
    final_root = tmp / "final"
    (final_root / "docs").mkdir(parents=True)
    (final_root / "docs" / "new.txt").write_bytes(add_data)
    (final_root / "docs" / "replace.txt").write_bytes(replace_data)
    operations = [
        {
            "thread_id": "add",
            "operation": "ADD",
            "path": "docs/new.txt",
            "payload": "add.txt",
            "payload_sha256": sha(add_data),
            "expected_output_sha256": sha(add_data),
        },
        {
            "thread_id": "replace",
            "operation": "REPLACE",
            "path": "docs/replace.txt",
            "payload": "replace.txt",
            "payload_sha256": sha(replace_data),
            "expected_output_sha256": sha(replace_data),
            "source_sha256": sha(old_data),
        },
    ]
    declared = ["docs/new.txt", "docs/replace.txt"]
    if include_delete:
        operations.append(
            {
                "thread_id": "delete",
                "operation": "DELETE",
                "path": "docs/delete.txt",
                "source_sha256": sha(delete_data),
                "delete_authority_id": "DELETE-AUTH",
            }
        )
        declared.append("docs/delete.txt")
    data = base_mission(tmp, operations, declared, candidate, final_root)
    path = tmp / "mission.json"
    write_json(path, data)
    return path, data


def add_aegis_break_authority(data: dict, protected_paths: list[str]) -> dict:
    data["aegis_break_authority"] = {
        "route_identity": "AEGIS_BREAK_PROTECTED_PATH_V1",
        "authority_id": data["authority_id"],
        "operator": "Jayson",
        "github_operator_login": "Jktomy",
        "repository": data["repository"],
        "base_sha": data["base_sha"],
        "branch": data["branch"],
        "declared_protected_paths": protected_paths,
        "source_blobs": dict(data["source_blobs"]),
        "candidate_tree_sha256": data["candidate_tree_sha256"],
        "final_pathset_sha256": data["final_pathset_sha256"],
        "operation_set_sha256": operation_set_sha256(data["operations"]),
        "stop_point": data["stop_point"],
        "persistent_writer": data["persistent_writer"],
        "direct_main_write": False,
        "force_push": False,
        "automatic_ready": False,
        "automatic_merge": False,
        "workflow_dispatch": False,
        "standing_authority": "NO",
    }
    return data


def row_hash(row: str) -> str:
    return sha((row + "\n").encode("utf-8"))


def add_workboard_row_update_authority(data: dict) -> dict:
    data["workboard_row_update_authority"] = {
        "route_identity": "WORKBOARD_ROW_UPDATE_V1",
        "authority_id": data["authority_id"],
        "operator": "Jayson",
        "github_operator_login": "Jktomy",
        "repository": data["repository"],
        "base_sha": data["base_sha"],
        "branch": data["branch"],
        "workboard_path": WORKBOARD_PATH,
        "workboard_source_blob": data["source_blobs"][WORKBOARD_PATH],
        "row_identity": {
            "Atlas Project": "Codex",
            "Operation": "Source Governance / Atlas Prime Rebuild",
            "Work Item": "Thread Engine - Atlas Prime Transition",
        },
        "allowed_fields": ["Last Known State", "Notes"],
        "before_row_sha256": row_hash(WORKBOARD_OLD_ROW),
        "after_row_sha256": row_hash(WORKBOARD_NEW_ROW),
        "candidate_tree_sha256": data["candidate_tree_sha256"],
        "final_pathset_sha256": data["final_pathset_sha256"],
        "operation_set_sha256": operation_set_sha256(data["operations"]),
        "stop_point": data["stop_point"],
        "persistent_writer": data["persistent_writer"],
        "direct_main_write": False,
        "force_push": False,
        "automatic_ready": False,
        "automatic_merge": False,
        "workflow_dispatch": False,
        "standing_authority": "NO",
    }
    return data


def build_protected_workboard_mission(tmp: Path, *, include_extra_protected: bool = False) -> tuple[Path, dict]:
    payloads = tmp / "payloads"
    payloads.mkdir()
    (payloads / "workboard.md").write_bytes(WORKBOARD_NEW)
    candidate = tmp / "candidate"
    (candidate / "codex").mkdir(parents=True)
    (candidate / WORKBOARD_PATH).write_bytes(WORKBOARD_NEW)
    final_root = tmp / "final"
    (final_root / "codex").mkdir(parents=True)
    (final_root / WORKBOARD_PATH).write_bytes(WORKBOARD_NEW)
    operations = [
        {
            "thread_id": "replace-workboard",
            "operation": "REPLACE",
            "path": WORKBOARD_PATH,
            "payload": "workboard.md",
            "payload_sha256": sha(WORKBOARD_NEW),
            "expected_output_sha256": sha(WORKBOARD_NEW),
            "source_sha256": sha(WORKBOARD_OLD),
        }
    ]
    declared = [WORKBOARD_PATH]
    protected = [WORKBOARD_PATH]
    source_blobs = {WORKBOARD_PATH: "1" * 40}
    if include_extra_protected:
        extra_data = b"noctua new\n"
        (payloads / "noctua.md").write_bytes(extra_data)
        (candidate / "noctua.md").write_bytes(extra_data)
        (final_root / "noctua.md").write_bytes(extra_data)
        operations.append(
            {
                "thread_id": "add-noctua",
                "operation": "ADD",
                "path": "noctua.md",
                "payload": "noctua.md",
                "payload_sha256": sha(extra_data),
                "expected_output_sha256": sha(extra_data),
            }
        )
        declared.append("noctua.md")
    data = base_mission(tmp, operations, declared, candidate, final_root)
    data["source_blobs"] = source_blobs
    data = add_aegis_break_authority(data, protected)
    data = bind_mission(data)
    path = tmp / "mission.json"
    write_json(path, data)
    return path, data


def build_workboard_row_update_mission(tmp: Path) -> tuple[Path, dict]:
    payloads = tmp / "payloads"
    payloads.mkdir()
    (payloads / "workboard.md").write_bytes(WORKBOARD_NEW)
    candidate = tmp / "candidate"
    (candidate / "codex").mkdir(parents=True)
    (candidate / WORKBOARD_PATH).write_bytes(WORKBOARD_NEW)
    final_root = tmp / "final"
    (final_root / "codex").mkdir(parents=True)
    (final_root / WORKBOARD_PATH).write_bytes(WORKBOARD_NEW)
    operations = [
        {
            "thread_id": "replace-workboard-row",
            "operation": "REPLACE",
            "path": WORKBOARD_PATH,
            "payload": "workboard.md",
            "payload_sha256": sha(WORKBOARD_NEW),
            "expected_output_sha256": sha(WORKBOARD_NEW),
            "source_sha256": sha(WORKBOARD_OLD),
        }
    ]
    data = base_mission(tmp, operations, [WORKBOARD_PATH], candidate, final_root)
    data["source_blobs"] = {WORKBOARD_PATH: "1" * 40}
    data = add_workboard_row_update_authority(data)
    data = bind_mission(data)
    path = tmp / "mission.json"
    write_json(path, data)
    return path, data


def review_thread_readback(number: int = 999, branch: str = "source/gate-7f-unit", count: object = 0) -> dict:
    return {
        "data": {
            "repository": {
                "pullRequests": {
                    "nodes": [
                        {
                            "number": number,
                            "headRefName": branch,
                            "reviewThreads": {"totalCount": count},
                        }
                    ]
                }
            }
        }
    }


class FakeRunner:
    def __init__(
        self,
        mission: dict,
        *,
        branch_exists: bool = False,
        duplicate_pr: bool = False,
        stale_base: bool = False,
        dirty: bool = False,
        fail_at: str | None = None,
        readback_patch: dict | None = None,
        review_thread_result: dict | None = None,
        operator_login: str = "Jktomy",
    ) -> None:
        self.mission = mission
        self.branch_exists = branch_exists
        self.duplicate_pr = duplicate_pr
        self.stale_base = stale_base
        self.dirty = dirty
        self.fail_at = fail_at
        self.readback_patch = readback_patch or {}
        self.review_thread_result = review_thread_result
        self.operator_login = operator_login
        self.calls: list[tuple[str, ...]] = []
        self.committed = False
        self.pr_created = False

    def run(self, args: list[str], cwd: Path | None = None) -> Completed:
        self.calls.append(tuple(args))
        if self.fail_at and args[1:2] == [self.fail_at]:
            raise GitRunnerError(f"planned failure at {self.fail_at}")
        if args[:2] == ["git", "ls-remote"] and args[-1] == "refs/heads/main":
            sha = "0" * 40 if self.stale_base else BASE
            return Completed(tuple(args), 0, f"{sha}\trefs/heads/main\n", "")
        if args[:2] == ["git", "ls-remote"]:
            return Completed(tuple(args), 0, f"{HEAD}\trefs/heads/{self.mission['branch']}\n" if self.branch_exists else "", "")
        if args[:4] == ["gh", "pr", "list", "--repo"]:
            return Completed(tuple(args), 0, json.dumps([{"number": 999}]) if self.duplicate_pr else "[]", "")
        if args == ["gh", "api", "user", "--jq", ".login"]:
            return Completed(tuple(args), 0, self.operator_login + "\n", "")
        if args[:2] == ["git", "clone"]:
            checkout = Path(args[-1])
            (checkout / "docs").mkdir(parents=True)
            (checkout / "docs" / "replace.txt").write_bytes(b"old\n")
            (checkout / "docs" / "delete.txt").write_bytes(b"delete me\n")
            (checkout / "codex").mkdir(parents=True)
            (checkout / WORKBOARD_PATH).write_bytes(WORKBOARD_OLD)
            return Completed(tuple(args), 0, "", "")
        if args[:2] == ["git", "rev-parse"] and args[-1] == "HEAD":
            return Completed(tuple(args), 0, (HEAD if self.committed else BASE) + "\n", "")
        if args[:2] == ["git", "rev-parse"] and args[-1] == "HEAD^":
            return Completed(tuple(args), 0, BASE + "\n", "")
        if args[:2] == ["git", "rev-list"]:
            return Completed(tuple(args), 0, f"{HEAD} {BASE}\n", "")
        if args[:2] == ["git", "log"]:
            return Completed(tuple(args), 0, self.mission["commit_message"] + "\n", "")
        if args[:2] == ["git", "show"]:
            return Completed(tuple(args), 0, "3" * 40 + "\n", "")
        if args[:2] == ["git", "status"]:
            return Completed(tuple(args), 0, " M docs/replace.txt\n" if self.dirty else "", "")
        if args[:3] == ["git", "hash-object", "--"]:
            return Completed(tuple(args), 0, "1" * 40 + "\n", "")
        if args[:2] == ["git", "diff"] and "--name-only" in args:
            return Completed(tuple(args), 0, "\n".join(self.mission["declared_paths"]) + "\n", "")
        if args[:2] == ["git", "diff"]:
            return Completed(tuple(args), 0, "", "")
        if args[:2] == ["git", "switch"]:
            return Completed(tuple(args), 0, "", "")
        if args[:2] == ["git", "add"]:
            return Completed(tuple(args), 0, "", "")
        if args[:2] == ["git", "commit"]:
            self.committed = True
            if self.fail_at == "commit":
                raise GitRunnerError("planned post-commit failure")
            return Completed(tuple(args), 0, "[source/gate-7f-unit] commit\n", "")
        if args[:2] == ["git", "push"]:
            if self.fail_at == "push":
                raise GitRunnerError("planned post-push failure")
            return Completed(tuple(args), 0, "", "")
        if args[:3] == ["gh", "pr", "create"]:
            self.pr_created = True
            if self.fail_at == "create":
                raise GitRunnerError("planned post-PR failure")
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
            data.update(self.readback_patch)
            return Completed(tuple(args), 0, json.dumps(data), "")
        if args[:3] == ["gh", "api", "graphql"]:
            data = self.review_thread_result
            if data is None:
                data = review_thread_readback(branch=self.mission["branch"])
            return Completed(tuple(args), 0, json.dumps(data), "")
        raise GitRunnerError(f"unexpected command: {args}")


class ProductionAdapterTests(unittest.TestCase):
    def execute(self, mission_path: Path, data: dict, **runner_kwargs) -> dict:
        protected = data.get("aegis_break_authority") is not None
        workboard = data.get("workboard_row_update_authority") is not None
        aegis_break_protected_route = runner_kwargs.pop("aegis_break_protected_route", protected)
        aegis_break_authority_id = runner_kwargs.pop("aegis_break_authority_id", data["authority_id"] if protected else None)
        workboard_row_update = runner_kwargs.pop("workboard_row_update", workboard)
        workboard_row_update_authority_id = runner_kwargs.pop("workboard_row_update_authority_id", data["authority_id"] if workboard else None)
        return execute_mission(
            mission_path,
            mission_scoped=True,
            execute_draft_pr=True,
            mission_sha256=data["mission_sha256"],
            aegis_break_protected_route=aegis_break_protected_route,
            aegis_break_authority_id=aegis_break_authority_id,
            workboard_row_update=workboard_row_update,
            workboard_row_update_authority_id=workboard_row_update_authority_id,
            work_root=mission_path.parent,
            package_root=mission_path.parent,
            runner=FakeRunner(data, **runner_kwargs),
        )

    def execute_with_runner(self, mission_path: Path, data: dict) -> tuple[dict, FakeRunner]:
        protected = data.get("aegis_break_authority") is not None
        workboard = data.get("workboard_row_update_authority") is not None
        runner = FakeRunner(data)
        receipt = execute_mission(
            mission_path,
            mission_scoped=True,
            execute_draft_pr=True,
            mission_sha256=data["mission_sha256"],
            aegis_break_protected_route=protected,
            aegis_break_authority_id=data["authority_id"] if protected else None,
            workboard_row_update=workboard,
            workboard_row_update_authority_id=data["authority_id"] if workboard else None,
            work_root=mission_path.parent,
            package_root=mission_path.parent,
            runner=runner,
        )
        return receipt, runner

    def assert_no_forbidden_delivery_actions(self, runner: FakeRunner) -> None:
        for call in runner.calls:
            with self.subTest(call=call):
                self.assertNotEqual(call[:3], ("gh", "pr", "ready"))
                self.assertNotEqual(call[:3], ("gh", "pr", "merge"))
                self.assertNotEqual(call[:3], ("gh", "workflow", "run"))
                self.assertNotEqual(call[:3], ("gh", "pr", "close"))
                self.assertNotEqual(call[:2], ("git", "merge"))
                self.assertFalse(call[:2] == ("git", "push") and ("--force" in call or "--delete" in call))
                self.assertFalse(call[:2] == ("git", "branch") and ("-d" in call or "-D" in call))

    def test_successful_add_replace_delete(self) -> None:
        with tempfile.TemporaryDirectory(prefix="atlas-gate7f-unit-") as tmp_text:
            mission_path, data = build_add_replace_delete_mission(Path(tmp_text))
            receipt = self.execute(mission_path, data)
            self.assertEqual(receipt["result"], "SUCCESS")
            self.assertEqual(receipt["head_sha"], HEAD)
            self.assertTrue(receipt["thread_engine_active"])
            self.assertEqual(receipt["authority_scope"], "MISSION_SCOPED")
            self.assertFalse(receipt["production_authority_activated"])
            self.assertTrue(receipt["human_merge_required"])

    def test_successful_add_replace_without_delete(self) -> None:
        with tempfile.TemporaryDirectory(prefix="atlas-gate7f-unit-") as tmp_text:
            mission_path, data = build_add_replace_delete_mission(Path(tmp_text), include_delete=False)
            receipt = self.execute(mission_path, data)
            self.assertEqual(receipt["result"], "SUCCESS")

    def test_readback_uses_supported_core_view_and_graphql_review_threads(self) -> None:
        with tempfile.TemporaryDirectory(prefix="atlas-gate7f-unit-") as tmp_text:
            mission_path, data = build_add_replace_delete_mission(Path(tmp_text), include_delete=False)
            runner = FakeRunner(data)
            receipt = execute_mission(
                mission_path,
                mission_scoped=True,
                execute_draft_pr=True,
                mission_sha256=data["mission_sha256"],
                work_root=mission_path.parent,
                package_root=mission_path.parent,
                runner=runner,
            )
            self.assertEqual(receipt["result"], "SUCCESS")
            core_views = [call for call in runner.calls if call[:3] == ("gh", "pr", "view")]
            self.assertEqual(len(core_views), 1)
            self.assertNotIn("reviewThreads", core_views[0])
            self.assertIn(
                (
                    "gh",
                    "api",
                    "graphql",
                    "-f",
                    f"query={REVIEW_THREAD_QUERY}",
                    "-f",
                    "owner=Jktomy",
                    "-f",
                    "name=atlas-prime",
                    "-f",
                    f"head={data['branch']}",
                ),
                runner.calls,
            )
            self.assertEqual(receipt["review_thread_count"], 0)

    def test_delete_authority_rejections(self) -> None:
        with tempfile.TemporaryDirectory(prefix="atlas-gate7f-unit-") as tmp_text:
            mission_path, data = build_add_replace_delete_mission(Path(tmp_text))
            data["operations"][2]["delete_authority_id"] = "WRONG"
            data = bind_mission(data)
            write_json(mission_path, data)
            with self.assertRaises(AdapterError) as raised:
                self.execute(mission_path, data)
            self.assertEqual(raised.exception.code, "DELETE_AUTHORITY_REQUIRED")

    def test_stale_base_branch_pr_and_dirty_stops(self) -> None:
        cases = [
            ({"stale_base": True}, "STALE_BASE"),
            ({"branch_exists": True}, "BRANCH_EXISTS"),
            ({"duplicate_pr": True}, "PR_EXISTS"),
            ({"dirty": True}, "DIRTY_CHECKOUT"),
        ]
        for runner_kwargs, code in cases:
            with self.subTest(code=code), tempfile.TemporaryDirectory(prefix="atlas-gate7f-unit-") as tmp_text:
                mission_path, data = build_add_replace_delete_mission(Path(tmp_text))
                with self.assertRaises(AdapterError) as raised:
                    self.execute(mission_path, data, **runner_kwargs)
                self.assertEqual(raised.exception.code, code)

    def test_mission_schema_rejections(self) -> None:
        with tempfile.TemporaryDirectory(prefix="atlas-gate7f-unit-") as tmp_text:
            mission_path, data = build_add_replace_delete_mission(Path(tmp_text))
            for patch, code in [
                ({"unknown": True}, "UNKNOWN_PROPERTY"),
                ({"mission_sha256": "0" * 64}, "MISSION_SHA_MISMATCH"),
                ({"remote_url": "https://example.invalid/repo.git"}, "REMOTE_REJECTED"),
                ({"receipt_name": "../receipt.json"}, "RECEIPT_NAME_REJECTED"),
                ({"declared_paths": [".github/workflows/x.yml"]}, "PROTECTED_PATH"),
                ({"declared_paths": ["generated/x.md"]}, "PROTECTED_PATH"),
                ({"declared_paths": ["codex/atlas-active-workboard.md"]}, "PROTECTED_PATH"),
                ({"declared_paths": ["codex/thread-engine-spear-weave-contract.md"]}, "PROTECTED_PATH"),
                ({"declared_paths": ["tools/thread-engine/production_adapter/adapter.py"]}, "PROTECTED_PATH"),
                ({"declared_paths": ["tools/atlas-sword/engine/Invoke-AtlasSword.ps1"]}, "PROTECTED_PATH"),
                ({"declared_paths": ["C:/x"]}, "PATH_REJECTED"),
                ({"declared_paths": ["../x"]}, "PATH_REJECTED"),
                ({"declared_paths": ["dir\\x"]}, "PATH_REJECTED"),
            ]:
                candidate = json.loads(json.dumps(data))
                candidate.update(patch)
                if "mission_sha256" not in patch:
                    candidate = bind_mission(candidate)
                with self.subTest(code=code, patch=patch):
                    with self.assertRaises(MissionError) as raised:
                        validate_mission(candidate)
                    self.assertEqual(raised.exception.code, code)
            mission_path.write_text('{"schema_version":"x","schema_version":"y"}', encoding="utf-8")
            with self.assertRaises(MissionError) as raised:
                load_mission(mission_path)
            self.assertEqual(raised.exception.code, "DUPLICATE_JSON_KEY")

    def test_operation_specific_rejections(self) -> None:
        with tempfile.TemporaryDirectory(prefix="atlas-gate7f-unit-") as tmp_text:
            _, data = build_add_replace_delete_mission(Path(tmp_text))
            data["operations"][0]["source_sha256"] = "0" * 64
            data = bind_mission(data)
            with self.assertRaises(MissionError):
                validate_mission(data)

    def test_ordinary_thread_engine_mission_rejects_workboard(self) -> None:
        with tempfile.TemporaryDirectory(prefix="atlas-gate7f-unit-") as tmp_text:
            _, data = build_protected_workboard_mission(Path(tmp_text))
            data.pop("aegis_break_authority")
            data = bind_mission(data)
            with self.assertRaises(MissionError) as raised:
                validate_mission(data)
            self.assertEqual(raised.exception.code, "PROTECTED_PATH")

    def test_workboard_row_update_accepts_exact_authorized_row(self) -> None:
        with tempfile.TemporaryDirectory(prefix="atlas-gate7f-unit-") as tmp_text:
            mission_path, data = build_workboard_row_update_mission(Path(tmp_text))
            receipt, runner = self.execute_with_runner(mission_path, data)
            self.assertEqual(receipt["result"], "SUCCESS")
            route = receipt["workboard_row_update_route"]
            self.assertEqual(route["route_identity"], "WORKBOARD_ROW_UPDATE_V1")
            self.assertEqual(route["authority_id"], data["authority_id"])
            self.assertEqual(route["operator"], "Jayson")
            self.assertEqual(route["expected_operator_login"], "Jktomy")
            self.assertEqual(route["observed_operator_login"], "Jktomy")
            self.assertEqual(route["workboard_path"], WORKBOARD_PATH)
            self.assertEqual(route["workboard_source_blob"], "1" * 40)
            self.assertEqual(route["row_identity"]["Work Item"], "Thread Engine - Atlas Prime Transition")
            self.assertEqual(route["allowed_fields"], ["Last Known State", "Notes"])
            self.assertEqual(route["before_row_sha256"], row_hash(WORKBOARD_OLD_ROW))
            self.assertEqual(route["after_row_sha256"], row_hash(WORKBOARD_NEW_ROW))
            self.assertEqual(route["operation_set_sha256"], operation_set_sha256(data["operations"]))
            self.assertEqual(receipt["workboard_row_update_evidence"]["changed_fields"], ["Last Known State", "Notes"])
            self.assertEqual(receipt["workboard_row_update_evidence"]["after_status"], "Ready for Athena")
            self.assertEqual(route["standing_authority"], "NO")
            self.assertFalse(route["direct_main_write"])
            self.assertFalse(route["force_push"])
            self.assertFalse(route["automatic_ready"])
            self.assertFalse(route["automatic_merge"])
            self.assertFalse(route["workflow_dispatch"])
            self.assertTrue(receipt["draft_pr_only"])
            self.assertTrue(receipt["human_merge_required"])
            self.assertTrue(runner.committed)
            self.assertTrue(runner.pr_created)
            self.assertEqual(len([call for call in runner.calls if call[:2] == ("git", "clone")]), 1)
            self.assertEqual(len([call for call in runner.calls if call == ("gh", "api", "user", "--jq", ".login")]), 1)
            self.assertEqual(len([call for call in runner.calls if call[:2] == ("git", "commit")]), 1)
            self.assertEqual(len([call for call in runner.calls if call[:3] == ("gh", "pr", "create")]), 1)
            self.assertIn("--draft", next(call for call in runner.calls if call[:3] == ("gh", "pr", "create")))
            self.assert_no_forbidden_delivery_actions(runner)

    def test_workboard_row_update_rejects_absent_launch_intent(self) -> None:
        with tempfile.TemporaryDirectory(prefix="atlas-gate7f-unit-") as tmp_text:
            mission_path, data = build_workboard_row_update_mission(Path(tmp_text))
            runner = FakeRunner(data)
            with self.assertRaises(AdapterError) as raised:
                execute_mission(
                    mission_path,
                    mission_scoped=True,
                    execute_draft_pr=True,
                    mission_sha256=data["mission_sha256"],
                    workboard_row_update=False,
                    workboard_row_update_authority_id=None,
                    work_root=mission_path.parent,
                    package_root=mission_path.parent,
                    runner=runner,
                )
            self.assertEqual(raised.exception.code, "WORKBOARD_INTENT_REQUIRED")
            self.assertEqual(raised.exception.stage, "PROTECTED_ROUTE_INTENT")
            self.assertFalse(runner.committed)
            self.assertFalse(runner.pr_created)

    def test_workboard_row_update_rejects_wrong_launch_authority_id(self) -> None:
        with tempfile.TemporaryDirectory(prefix="atlas-gate7f-unit-") as tmp_text:
            mission_path, data = build_workboard_row_update_mission(Path(tmp_text))
            with self.assertRaises(AdapterError) as raised:
                self.execute(mission_path, data, workboard_row_update_authority_id="WRONG-AUTHORITY")
            self.assertEqual(raised.exception.code, "WORKBOARD_AUTHORITY_MISMATCH")
            self.assertEqual(raised.exception.stage, "PROTECTED_ROUTE_INTENT")

    def test_workboard_row_update_rejects_authenticated_operator_mismatch(self) -> None:
        with tempfile.TemporaryDirectory(prefix="atlas-gate7f-unit-") as tmp_text:
            mission_path, data = build_workboard_row_update_mission(Path(tmp_text))
            with self.assertRaises(AdapterError) as raised:
                self.execute(mission_path, data, operator_login="OtherOperator")
            self.assertEqual(raised.exception.code, "WORKBOARD_OPERATOR_MISMATCH")
            self.assertEqual(raised.exception.stage, "OPERATOR_VERIFY")
            self.assertEqual(raised.exception.receipt["workboard_row_update_route"]["observed_operator_login"], "OtherOperator")

    def test_workboard_row_update_rejects_stale_source_blob(self) -> None:
        with tempfile.TemporaryDirectory(prefix="atlas-gate7f-unit-") as tmp_text:
            mission_path, data = build_workboard_row_update_mission(Path(tmp_text))
            data["source_blobs"][WORKBOARD_PATH] = "0" * 40
            data["workboard_row_update_authority"]["workboard_source_blob"] = "0" * 40
            data = bind_mission(data)
            write_json(mission_path, data)
            with self.assertRaises(AdapterError) as raised:
                self.execute(mission_path, data)
            self.assertEqual(raised.exception.code, "SOURCE_BLOB_MISMATCH")
            self.assertEqual(raised.exception.stage, "SOURCE_BLOB_VERIFY")

    def test_workboard_row_update_rejects_extra_protected_path(self) -> None:
        with tempfile.TemporaryDirectory(prefix="atlas-gate7f-unit-") as tmp_text:
            _, data = build_workboard_row_update_mission(Path(tmp_text))
            data["declared_paths"].append("noctua.md")
            data["operations"].append(
                {
                    "thread_id": "add-noctua",
                    "operation": "ADD",
                    "path": "noctua.md",
                    "payload": "noctua.md",
                    "payload_sha256": sha(b"noctua\n"),
                    "expected_output_sha256": sha(b"noctua\n"),
                }
            )
            data = bind_mission(data)
            with self.assertRaises(MissionError) as raised:
                validate_mission(data)
            self.assertEqual(raised.exception.code, "WORKBOARD_PATH_MISMATCH")

    def test_workboard_row_update_rejects_row_hash_mismatch(self) -> None:
        with tempfile.TemporaryDirectory(prefix="atlas-gate7f-unit-") as tmp_text:
            mission_path, data = build_workboard_row_update_mission(Path(tmp_text))
            data["workboard_row_update_authority"]["after_row_sha256"] = "0" * 64
            data = bind_mission(data)
            write_json(mission_path, data)
            with self.assertRaises(AdapterError) as raised:
                self.execute(mission_path, data)
            self.assertEqual(raised.exception.code, "WORKBOARD_ROW_HASH_MISMATCH")
            self.assertEqual(raised.exception.stage, "CANDIDATE_STAGE")

    def test_aegis_break_accepts_exact_authorized_workboard(self) -> None:
        with tempfile.TemporaryDirectory(prefix="atlas-gate7f-unit-") as tmp_text:
            mission_path, data = build_protected_workboard_mission(Path(tmp_text))
            receipt, runner = self.execute_with_runner(mission_path, data)
            self.assertEqual(receipt["result"], "SUCCESS")
            self.assertEqual(receipt["head_sha"], HEAD)
            self.assertEqual(receipt["pr_readback"]["headRefName"], data["branch"])
            self.assertEqual(receipt["pr_readback"]["headRefOid"], HEAD)
            self.assertEqual(receipt["review_thread_count"], 0)
            route = receipt["aegis_break_protected_route"]
            self.assertEqual(route["route_identity"], "AEGIS_BREAK_PROTECTED_PATH_V1")
            self.assertEqual(route["authority_id"], data["authority_id"])
            self.assertEqual(route["operator"], "Jayson")
            self.assertEqual(route["expected_operator_login"], "Jktomy")
            self.assertEqual(route["observed_operator_login"], "Jktomy")
            self.assertEqual(route["declared_protected_paths"], [WORKBOARD_PATH])
            self.assertEqual(route["exact_protected_paths"], [WORKBOARD_PATH])
            self.assertEqual(route["protected_source_blobs"], {WORKBOARD_PATH: "1" * 40})
            self.assertEqual(route["protected_source_blobs_sha256"], sha256_bytes(stable_json({WORKBOARD_PATH: "1" * 40}).encode("utf-8")))
            self.assertEqual(route["operation_set_sha256"], operation_set_sha256(data["operations"]))
            self.assertEqual(route["candidate_tree_sha256"], data["candidate_tree_sha256"])
            self.assertEqual(route["final_pathset_sha256"], data["final_pathset_sha256"])
            self.assertEqual(route["standing_authority"], "NO")
            self.assertFalse(route["direct_main_write"])
            self.assertFalse(route["force_push"])
            self.assertFalse(route["automatic_ready"])
            self.assertFalse(route["automatic_merge"])
            self.assertFalse(route["workflow_dispatch"])
            self.assertEqual(route["forbidden_action_confirmation"]["standing_authority"], "NO")
            self.assertFalse(route["forbidden_action_confirmation"]["direct_main_write"])
            self.assertFalse(route["forbidden_action_confirmation"]["force_push"])
            self.assertFalse(route["forbidden_action_confirmation"]["automatic_ready"])
            self.assertFalse(route["forbidden_action_confirmation"]["automatic_merge"])
            self.assertFalse(route["forbidden_action_confirmation"]["workflow_dispatch"])
            self.assertTrue(receipt["draft_pr_only"])
            self.assertTrue(receipt["human_merge_required"])
            self.assertTrue(runner.committed)
            self.assertTrue(runner.pr_created)
            self.assertEqual(len([call for call in runner.calls if call[:2] == ("git", "clone")]), 1)
            self.assertEqual(len([call for call in runner.calls if call == ("gh", "api", "user", "--jq", ".login")]), 1)
            self.assertEqual(len([call for call in runner.calls if call[:2] == ("git", "commit")]), 1)
            self.assertEqual(len([call for call in runner.calls if call[:3] == ("gh", "pr", "create")]), 1)
            self.assertEqual(len([call for call in runner.calls if call[:3] == ("gh", "pr", "view")]), 1)
            self.assertIn("--draft", next(call for call in runner.calls if call[:3] == ("gh", "pr", "create")))
            self.assert_no_forbidden_delivery_actions(runner)

    def test_aegis_break_rejects_extra_protected_path(self) -> None:
        with tempfile.TemporaryDirectory(prefix="atlas-gate7f-unit-") as tmp_text:
            _, data = build_protected_workboard_mission(Path(tmp_text), include_extra_protected=True)
            with self.assertRaises(MissionError) as raised:
                validate_mission(data)
            self.assertEqual(raised.exception.code, "AEGIS_BREAK_PATH_MISMATCH")

    def test_aegis_break_rejects_protected_replace_missing_source_blob(self) -> None:
        with tempfile.TemporaryDirectory(prefix="atlas-gate7f-unit-") as tmp_text:
            _, data = build_protected_workboard_mission(Path(tmp_text))
            data["source_blobs"].pop(WORKBOARD_PATH)
            data = add_aegis_break_authority(data, [WORKBOARD_PATH])
            data = bind_mission(data)
            with self.assertRaises(MissionError) as raised:
                validate_mission(data)
            self.assertEqual(raised.exception.code, "AEGIS_BREAK_SOURCE_BLOB_REQUIRED")

    def test_aegis_break_rejects_stale_source_blob(self) -> None:
        with tempfile.TemporaryDirectory(prefix="atlas-gate7f-unit-") as tmp_text:
            mission_path, data = build_protected_workboard_mission(Path(tmp_text))
            data["source_blobs"][WORKBOARD_PATH] = "0" * 40
            data = add_aegis_break_authority(data, [WORKBOARD_PATH])
            data = bind_mission(data)
            write_json(mission_path, data)
            with self.assertRaises(AdapterError) as raised:
                self.execute(mission_path, data)
            self.assertEqual(raised.exception.code, "SOURCE_BLOB_MISMATCH")
            self.assertEqual(raised.exception.stage, "SOURCE_BLOB_VERIFY")

    def test_aegis_break_rejects_absent_launch_intent(self) -> None:
        with tempfile.TemporaryDirectory(prefix="atlas-gate7f-unit-") as tmp_text:
            mission_path, data = build_protected_workboard_mission(Path(tmp_text))
            runner = FakeRunner(data)
            with self.assertRaises(AdapterError) as raised:
                execute_mission(
                    mission_path,
                    mission_scoped=True,
                    execute_draft_pr=True,
                    mission_sha256=data["mission_sha256"],
                    aegis_break_protected_route=False,
                    aegis_break_authority_id=None,
                    work_root=mission_path.parent,
                    package_root=mission_path.parent,
                    runner=runner,
                )
            self.assertEqual(raised.exception.code, "AEGIS_BREAK_INTENT_REQUIRED")
            self.assertEqual(raised.exception.stage, "PROTECTED_ROUTE_INTENT")
            self.assertFalse(runner.committed)
            self.assertFalse(runner.pr_created)

    def test_aegis_break_rejects_wrong_launch_authority_id(self) -> None:
        with tempfile.TemporaryDirectory(prefix="atlas-gate7f-unit-") as tmp_text:
            mission_path, data = build_protected_workboard_mission(Path(tmp_text))
            runner = FakeRunner(data)
            with self.assertRaises(AdapterError) as raised:
                execute_mission(
                    mission_path,
                    mission_scoped=True,
                    execute_draft_pr=True,
                    mission_sha256=data["mission_sha256"],
                    aegis_break_protected_route=True,
                    aegis_break_authority_id="WRONG-AUTHORITY",
                    work_root=mission_path.parent,
                    package_root=mission_path.parent,
                    runner=runner,
                )
            self.assertEqual(raised.exception.code, "AEGIS_BREAK_AUTHORITY_MISMATCH")
            self.assertEqual(raised.exception.stage, "PROTECTED_ROUTE_INTENT")
            self.assertFalse(runner.committed)
            self.assertFalse(runner.pr_created)

    def test_aegis_break_rejects_authenticated_operator_mismatch(self) -> None:
        with tempfile.TemporaryDirectory(prefix="atlas-gate7f-unit-") as tmp_text:
            mission_path, data = build_protected_workboard_mission(Path(tmp_text))
            runner = FakeRunner(data, operator_login="OtherOperator")
            with self.assertRaises(AdapterError) as raised:
                execute_mission(
                    mission_path,
                    mission_scoped=True,
                    execute_draft_pr=True,
                    mission_sha256=data["mission_sha256"],
                    aegis_break_protected_route=True,
                    aegis_break_authority_id=data["authority_id"],
                    work_root=mission_path.parent,
                    package_root=mission_path.parent,
                    runner=runner,
                )
            self.assertEqual(raised.exception.code, "AEGIS_BREAK_OPERATOR_MISMATCH")
            self.assertEqual(raised.exception.stage, "OPERATOR_VERIFY")
            self.assertEqual(raised.exception.receipt["aegis_break_protected_route"]["observed_operator_login"], "OtherOperator")
            self.assertFalse(runner.committed)
            self.assertFalse(runner.pr_created)

    def test_aegis_break_rejects_wrong_route_authority_operator_and_bindings(self) -> None:
        cases = [
            ("route_identity", "ORDINARY_THREAD_ENGINE", "AEGIS_BREAK_ROUTE_REJECTED"),
            ("authority_id", "WRONG-AUTHORITY", "AEGIS_BREAK_AUTHORITY_MISMATCH"),
            ("operator", "Athena", "AEGIS_BREAK_OPERATOR_MISMATCH"),
            ("github_operator_login", "OtherOperator", "AEGIS_BREAK_OPERATOR_MISMATCH"),
            ("repository", "Jktomy/atlas-prime", "AEGIS_BREAK_BINDING_MISMATCH"),
            ("base_sha", "0" * 40, "AEGIS_BREAK_BINDING_MISMATCH"),
            ("branch", "source/wrong-aegis-break-branch", "AEGIS_BREAK_BINDING_MISMATCH"),
            ("candidate_tree_sha256", "0" * 64, "AEGIS_BREAK_BINDING_MISMATCH"),
            ("operation_set_sha256", "0" * 64, "AEGIS_BREAK_OPERATION_SET_MISMATCH"),
        ]
        for field, value, code in cases:
            with self.subTest(field=field), tempfile.TemporaryDirectory(prefix="atlas-gate7f-unit-") as tmp_text:
                _, data = build_protected_workboard_mission(Path(tmp_text))
                data["aegis_break_authority"][field] = value
                data = bind_mission(data)
                with self.assertRaises(MissionError) as raised:
                    validate_mission(data)
                self.assertEqual(raised.exception.code, code)

    def test_aegis_break_rejects_forbidden_delivery_authority(self) -> None:
        cases = [
            ("direct_main_write", True),
            ("force_push", True),
            ("automatic_ready", True),
            ("automatic_merge", True),
            ("workflow_dispatch", True),
            ("standing_authority", "YES"),
        ]
        for field, value in cases:
            with self.subTest(field=field), tempfile.TemporaryDirectory(prefix="atlas-gate7f-unit-") as tmp_text:
                _, data = build_protected_workboard_mission(Path(tmp_text))
                data["aegis_break_authority"][field] = value
                data = bind_mission(data)
                with self.assertRaises(MissionError) as raised:
                    validate_mission(data)
                self.assertEqual(raised.exception.code, "AEGIS_BREAK_FORBIDDEN_ACTION")

    def test_aegis_break_does_not_authorize_thread_engine_self_change(self) -> None:
        for self_change_path in ("tools/thread-engine/production_adapter/adapter.py", "thread-engine.md"):
            with self.subTest(self_change_path=self_change_path), tempfile.TemporaryDirectory(prefix="atlas-gate7f-unit-") as tmp_text:
                _, data = build_protected_workboard_mission(Path(tmp_text))
                data["declared_paths"] = [self_change_path]
                data["operations"][0]["path"] = self_change_path
                data["source_blobs"] = {self_change_path: "1" * 40}
                data = add_aegis_break_authority(data, [self_change_path])
                data = bind_mission(data)
                with self.assertRaises(MissionError) as raised:
                    validate_mission(data)
                self.assertEqual(raised.exception.code, "THREAD_ENGINE_SELF_CHANGE_REJECTED")

    def test_payload_source_candidate_and_final_hash_rejections(self) -> None:
        cases = [
            ("payload_sha256", "PAYLOAD_HASH_MISMATCH"),
            ("source_sha256", "SOURCE_HASH_MISMATCH"),
            ("candidate_tree_sha256", "CANDIDATE_TREE_MISMATCH"),
            ("final_pathset_sha256", "FINAL_PATHSET_MISMATCH"),
        ]
        for field, code in cases:
            with self.subTest(field=field), tempfile.TemporaryDirectory(prefix="atlas-gate7f-unit-") as tmp_text:
                mission_path, data = build_add_replace_delete_mission(Path(tmp_text))
                if field in {"payload_sha256", "source_sha256"}:
                    data["operations"][0 if field == "payload_sha256" else 1][field] = "0" * 64
                else:
                    data[field] = "0" * 64
                data = bind_mission(data)
                write_json(mission_path, data)
                with self.assertRaises(AdapterError) as raised:
                    self.execute(mission_path, data)
                self.assertEqual(raised.exception.code, code)

    def test_readback_mismatches_reject(self) -> None:
        patches = [
            {"state": "CLOSED"},
            {"isDraft": False},
            {"baseRefName": "develop"},
            {"headRefName": "wrong"},
            {"headRefOid": "0" * 40},
            {"title": "wrong"},
            {"body": "wrong"},
            {"commits": [{"oid": HEAD}, {"oid": "3" * 40}]},
            {"files": [{"path": "docs/new.txt"}]},
            {"comments": [{"body": "x"}]},
            {"reviews": [{"state": "COMMENTED"}]},
        ]
        for patch in patches:
            with self.subTest(patch=patch), tempfile.TemporaryDirectory(prefix="atlas-gate7f-unit-") as tmp_text:
                mission_path, data = build_add_replace_delete_mission(Path(tmp_text))
                with self.assertRaises(AdapterError) as raised:
                    self.execute(mission_path, data, readback_patch=patch)
                self.assertEqual(raised.exception.code, "READBACK_MISMATCH")

    def test_review_thread_graphql_rejections(self) -> None:
        cases = [
            ({"data": {"repository": {"pullRequests": {"nodes": []}}}}, "zero"),
            ({"data": {"repository": {"pullRequests": {"nodes": [{}, {}]}}}}, "duplicate"),
            (review_thread_readback(number=1000), "number"),
            ({"errors": [{"message": "x"}]}, "errors"),
            ({"data": {}}, "missing repository"),
            ({"data": {"repository": {"pullRequests": {}}}}, "missing nodes"),
            ({"data": {"repository": {"pullRequests": {"nodes": [None]}}}}, "malformed node"),
            ({"data": {"repository": {"pullRequests": {"nodes": [{"number": 999, "headRefName": "source/gate-7f-unit"}]}}}}, "missing count"),
            (review_thread_readback(count=True), "bool count"),
            (review_thread_readback(count="0"), "string count"),
            (review_thread_readback(count=0.0), "float count"),
            (review_thread_readback(count=-1), "negative count"),
            (review_thread_readback(count=1), "nonzero count"),
        ]
        for result, label in cases:
            with self.subTest(label=label), tempfile.TemporaryDirectory(prefix="atlas-gate7f-unit-") as tmp_text:
                mission_path, data = build_add_replace_delete_mission(Path(tmp_text), include_delete=False)
                with self.assertRaises(AdapterError) as raised:
                    self.execute(mission_path, data, review_thread_result=result)
                self.assertEqual(raised.exception.code, "READBACK_MISMATCH")
                self.assertEqual(raised.exception.receipt["result"], "REJECTED")
                self.assertEqual(raised.exception.receipt["error_stage"], "READBACK")

    def test_partial_state_failures_are_classified(self) -> None:
        for fail_at, expected in [("commit", "REJECTED"), ("push", "REJECTED"), ("create", "REJECTED")]:
            with self.subTest(fail_at=fail_at), tempfile.TemporaryDirectory(prefix="atlas-gate7f-unit-") as tmp_text:
                mission_path, data = build_add_replace_delete_mission(Path(tmp_text))
                with self.assertRaises(AdapterError) as raised:
                    self.execute(mission_path, data, fail_at=fail_at)
                self.assertEqual(raised.exception.receipt["result"], expected)

    def test_recovery_classifier_refuses_blind_replay(self) -> None:
        self.assertTrue(classify_recovery("FRESH_CLONE").safe_to_continue)
        self.assertFalse(classify_recovery("UNKNOWN").safe_to_continue)
        self.assertEqual(classify_recovery("UNKNOWN").classification, "BLIND_REPLAY_REJECTED")

    def test_readback_helper_requires_number_and_url(self) -> None:
        with self.assertRaises(ReadbackError):
            verify_pr_readback({}, mission_branch="source/x", base_sha=BASE, head_sha=HEAD, title="t", body="b", declared_paths=())

    def test_intent_and_mission_sha_arguments_required(self) -> None:
        with tempfile.TemporaryDirectory(prefix="atlas-gate7f-unit-") as tmp_text:
            mission_path, data = build_add_replace_delete_mission(Path(tmp_text))
            with self.assertRaises(AdapterError) as raised:
                execute_mission(mission_path, mission_scoped=False, execute_draft_pr=True, package_root=Path(tmp_text))
            self.assertEqual(raised.exception.code, "INTENT_REQUIRED")
            with self.assertRaises(AdapterError) as raised:
                execute_mission(mission_path, mission_scoped=True, execute_draft_pr=True, mission_sha256="0" * 64, package_root=Path(tmp_text), runner=FakeRunner(data))
            self.assertEqual(raised.exception.code, "MISSION_SHA_MISMATCH")


    def test_powershell_launcher_prepares_missing_work_root(self) -> None:
        launcher = (ROOT / "Invoke-AtlasThreadEngineProductionAdapter.ps1").read_text(encoding="utf-8")
        self.assertIn("[switch] $AegisBreakProtectedRoute", launcher)
        self.assertIn("[string] $AegisBreakAuthorityId", launcher)
        self.assertIn("Aegis Break protected-route intent requires an exact authority id.", launcher)
        self.assertIn("--aegis-break-protected-route", launcher)
        self.assertIn("--aegis-break-authority-id", launcher)
        self.assertNotIn("$argumentList.Add((Resolve-Path -LiteralPath $WorkRoot).Path)", launcher)
        self.assertIn("GetUnresolvedProviderPathFromPSPath($WorkRoot)", launcher)
        self.assertIn("Test-Path -LiteralPath $resolvedWorkRoot -PathType Leaf", launcher)
        self.assertIn("[System.IO.Directory]::CreateDirectory($resolvedWorkRoot)", launcher)
        self.assertIn("Test-Path -LiteralPath $resolvedWorkRoot -PathType Container", launcher)
        create_at = launcher.index("[System.IO.Directory]::CreateDirectory($resolvedWorkRoot)")
        append_at = launcher.index("$argumentList.Add($resolvedWorkRoot)")
        self.assertLess(create_at, append_at)

if __name__ == "__main__":
    unittest.main()
