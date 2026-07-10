from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ENGINE_PATH = ROOT / "tools/atlas-sword/engine"
MODULE_PATH = ENGINE_PATH / "oathbringer_github.py"
import sys
sys.path.insert(0, str(ENGINE_PATH))
SPEC = importlib.util.spec_from_file_location("oathbringer_github", MODULE_PATH)
assert SPEC and SPEC.loader
og = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = og
SPEC.loader.exec_module(og)


def sha1_bytes(value: bytes) -> str:
    return hashlib.sha1(value).hexdigest()


class FakeGitHubClient:
    def __init__(
        self,
        login: str = "Jktomy",
        *,
        pr_head_lag_reads: int = 0,
        pr_head_never_converges: bool = False,
    ) -> None:
        self.login = login
        self.base_branch = "main"
        self.base_commit = "a" * 40
        self.base_tree_sha = "1" * 40
        self.trees = {self.base_tree_sha: {"README.md": {"sha": "b" * 40, "mode": "100644", "type": "blob"}}}
        self.commits = {self.base_commit: {"tree": self.base_tree_sha, "parent": None}}
        self.refs = {"main": self.base_commit}
        self.blobs: dict[str, bytes] = {}
        self.pull_requests: dict[int, dict] = {}
        self.next_pr = 1
        self.calls: list[tuple] = []
        self.pr_head_lag_reads = max(0, int(pr_head_lag_reads))
        self.pr_head_never_converges = bool(pr_head_never_converges)
        self._pr_head_lag: dict[int, dict] = {}

    def get_authenticated_user(self):
        self.calls.append(("get_authenticated_user", self.login))
        return {"login": self.login}

    def get_ref(self, branch: str):
        self.calls.append(("get_ref", branch))
        sha = self.refs.get(branch)
        return None if sha is None else {"object": {"sha": sha}}

    def get_tree_for_commit(self, commit_sha: str):
        tree_sha = self.commits[commit_sha]["tree"]
        return tree_sha, copy.deepcopy(self.trees[tree_sha])

    def get_tree(self, tree_sha: str):
        return tree_sha, copy.deepcopy(self.trees[tree_sha])

    def create_blob(self, content: bytes) -> str:
        sha = sha1_bytes(b"blob:" + content)
        self.blobs[sha] = content
        self.calls.append(("create_blob", sha))
        return sha

    def create_tree(self, base_tree_sha: str, elements: list[dict]) -> str:
        tree = copy.deepcopy(self.trees[base_tree_sha])
        for item in elements:
            if item["sha"] is None:
                tree.pop(item["path"], None)
            else:
                tree[item["path"]] = {"sha": item["sha"], "mode": item["mode"], "type": item["type"]}
        payload = json.dumps(tree, sort_keys=True).encode()
        tree_sha = sha1_bytes(b"tree:" + payload)
        self.trees[tree_sha] = tree
        self.calls.append(("create_tree", base_tree_sha, tree_sha))
        return tree_sha

    def create_commit(self, message: str, tree_sha: str, parent_sha: str) -> str:
        payload = f"{message}|{tree_sha}|{parent_sha}".encode()
        commit_sha = sha1_bytes(b"commit:" + payload)
        self.commits[commit_sha] = {"tree": tree_sha, "parent": parent_sha}
        self.calls.append(("create_commit", commit_sha, parent_sha))
        return commit_sha

    def create_ref(self, branch: str, sha: str) -> None:
        if branch in self.refs:
            raise AssertionError("branch already exists")
        self.refs[branch] = sha
        self.calls.append(("create_ref", branch, sha))

    def update_ref(self, branch: str, sha: str) -> None:
        prior = self.refs[branch]
        if self.commits[sha]["parent"] != prior:
            raise AssertionError("not fast-forward")
        self.refs[branch] = sha
        for number, pr in self.pull_requests.items():
            if pr["head"]["ref"] == branch:
                pr["head"]["sha"] = prior
                self._pr_head_lag[number] = {
                    "remaining": self.pr_head_lag_reads,
                    "permanent": self.pr_head_never_converges,
                    "stale": prior,
                }
        self.calls.append(("update_ref", branch, sha))

    def find_open_pull_requests(self, branch: str, base_branch: str):
        return [pr for pr in self.pull_requests.values() if pr["state"] == "open" and pr["head"]["ref"] == branch and pr["base"]["ref"] == base_branch]

    def create_pull_request(self, branch: str, base_branch: str, contract: dict):
        number = self.next_pr
        self.next_pr += 1
        pr = {"number": number, "node_id": f"PR_{number}", "state": "open", "draft": True, "merged": False, "merged_at": None, "merge_commit_sha": None, "head": {"ref": branch, "sha": self.refs[branch]}, "base": {"ref": base_branch, "sha": self.refs[base_branch]}}
        self.pull_requests[number] = pr
        self.calls.append(("create_pull_request", number))
        return copy.deepcopy(pr)

    def get_pull_request(self, number: int):
        pr = self.pull_requests[number]
        lag = self._pr_head_lag.get(number)
        if lag is None:
            pr["head"]["sha"] = self.refs[pr["head"]["ref"]]
        elif lag["permanent"]:
            pr["head"]["sha"] = lag["stale"]
        elif lag["remaining"] > 0:
            pr["head"]["sha"] = lag["stale"]
            lag["remaining"] -= 1
        else:
            pr["head"]["sha"] = self.refs[pr["head"]["ref"]]
            self._pr_head_lag.pop(number, None)
        pr["base"]["sha"] = self.refs[pr["base"]["ref"]]
        return copy.deepcopy(pr)

    def list_pull_request_files(self, number: int):
        pr = self.get_pull_request(number)
        _, base_tree = self.get_tree_for_commit(pr["base"]["sha"])
        _, head_tree = self.get_tree_for_commit(pr["head"]["sha"])
        return [{"filename": path} for path in og.changed_paths_between(base_tree, head_tree)]

    def list_workflow_runs(self, head_sha: str):
        return []

    def mark_ready(self, node_id: str):
        number = int(node_id.split("_", 1)[1])
        self.pull_requests[number]["draft"] = False
        self.calls.append(("mark_ready", number))

    def merge_pull_request(self, number: int, expected_head: str, method: str):
        pr = self.pull_requests[number]
        if self.refs[pr["head"]["ref"]] != expected_head:
            return {"merged": False, "message": "head moved"}
        merge_sha = sha1_bytes(f"merge:{expected_head}:{method}".encode())
        self.commits[merge_sha] = {"tree": self.commits[expected_head]["tree"], "parent": self.refs[pr["base"]["ref"]]}
        self.refs[pr["base"]["ref"]] = merge_sha
        pr["merged"] = True
        pr["merged_at"] = "2026-07-10T00:00:00Z"
        pr["merge_commit_sha"] = merge_sha
        pr["state"] = "closed"
        self.calls.append(("merge_pull_request", number, expected_head, method))
        return {"merged": True, "sha": merge_sha, "message": "merged"}


def base_mission(payload_sha: str, lessons_sha: str) -> dict:
    return {
        "format_version": "2.0",
        "mission_id": "WAVE-03-HARMLESS-PROOF",
        "sword_identity": "atlas-prime-oathbringer-proof-r01",
        "forge_standard": "SWORD_FORGE_STANDARD_V1",
        "package_manifest_required": True,
        "lessons_register": {"schema_version": "prime-sword-lessons-v1", "path": "source/methods/sword-lessons.json", "source_sha256": lessons_sha},
        "lesson_applicability": [{"lesson_id": f"SWORD-L{number:03d}", "status": "APPLIED"} for number in range(1, 14)],
        "change_method": "OATHBRINGER",
        "execution_environment": "GITHUB",
        "operator_interface": "POWERSHELL",
        "framework_state": "PILOT_READY_PROOF_PENDING",
        "runtime_mode": "PRODUCTION_GITHUB_NATIVE",
        "lane": "BUILD",
        "repository": "Jktomy/atlas-prime",
        "base_branch": "main",
        "expected_base": "a" * 40,
        "expected_head": None,
        "branch": "proof/oathbringer-harmless-r01",
        "pull_request": None,
        "commit_message": "Proof: add harmless Oathbringer fixture",
        "pull_request_contract": {"title": "Proof: Oathbringer harmless build", "body": "Harmless Wave 3 proof.", "draft": True},
        "declared_paths": [{"path": "proof/oathbringer-harmless.txt", "operation": "ADD", "payload_path": "payload/oathbringer-harmless.txt", "payload_sha256": payload_sha}],
        "workflow_rules": [],
        "receipt_contract": {"write_on_interrupt": True, "write_on_failure": True, "write_on_success": True, "automatic_retry": False, "automatic_rollback": False, "interrupt_exit_code": 130, "failure_exit_code": 1},
        "authorization": {"approved_preview": True, "execution_authorized": True, "authorizer": "JAYSON", "operator": "JAYSON", "github_login": "Jktomy"},
        "stop_boundary": "Stop at the harmless draft pull request.",
        "forbidden_actions": ["DIRECT_MAIN", "FORCE_PUSH", "SCOPE_WIDENING", "TOKEN_PERSISTENCE"],
    }
