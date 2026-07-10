from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from oathbringer_test_support import FakeGitHubClient, base_mission, og

ROOT = Path(__file__).resolve().parents[2]

class OathbringerGitHubNativeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        payload = self.root / "payload/oathbringer-harmless.txt"
        payload.parent.mkdir(parents=True)
        payload.write_text("Oathbringer harmless proof.\n", encoding="utf-8", newline="\n")
        self.payload_sha = hashlib.sha256(payload.read_bytes()).hexdigest()
        self.client = FakeGitHubClient()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_build_creates_exact_single_commit_draft_pr(self) -> None:
        mission = base_mission(self.payload_sha)
        result, context = og.execute_mission(mission, self.root, self.client, json_mode=True)
        self.assertEqual(result["status"], "OATHBRINGER_BUILD_PASS")
        self.assertEqual(result["changed_paths"], ["proof/oathbringer-harmless.txt"])
        self.assertEqual(result["pull_request"], 1)
        self.assertTrue(self.client.pull_requests[1]["draft"])
        self.assertEqual(self.client.commits[result["commit_sha"]]["parent"], mission["expected_base"])
        self.assertTrue(context.github_called)
        self.assertTrue(context.mutation_performed)
        self.assertNotIn("main", [call[1] for call in self.client.calls if call[0] == "create_ref"])

    def test_repair_fast_forwards_the_exact_existing_pr(self) -> None:
        build = base_mission(self.payload_sha)
        first, _ = og.execute_mission(build, self.root, self.client, json_mode=True)
        payload = self.root / "payload/oathbringer-harmless.txt"
        payload.write_text("Oathbringer repaired proof.\n", encoding="utf-8", newline="\n")
        repaired_sha = hashlib.sha256(payload.read_bytes()).hexdigest()
        repair = base_mission(repaired_sha)
        repair.update({"lane": "REPAIR", "expected_head": first["commit_sha"], "pull_request": 1, "commit_message": "Proof: repair harmless Oathbringer fixture"})
        repair.pop("pull_request_contract")
        second, _ = og.execute_mission(repair, self.root, self.client, json_mode=True)
        self.assertEqual(second["status"], "OATHBRINGER_REPAIR_PASS")
        self.assertEqual(self.client.commits[second["commit_sha"]]["parent"], first["commit_sha"])
        self.assertIn(("update_ref", repair["branch"], second["commit_sha"]), self.client.calls)
        self.assertTrue(self.client.pull_requests[1]["draft"])

    def test_execute_marks_ready_and_merges_only_audited_head(self) -> None:
        build = base_mission(self.payload_sha)
        first, _ = og.execute_mission(build, self.root, self.client, json_mode=True)
        execute = base_mission(self.payload_sha)
        execute.update({"lane": "EXECUTE", "expected_head": first["commit_sha"], "pull_request": 1, "independent_audit": {"verdict": "GREEN", "exact_head": first["commit_sha"], "receipt_sha256": "d" * 64}, "merge_method": "squash", "stop_boundary": "Stop after merged-main readback."})
        execute.pop("commit_message")
        execute.pop("pull_request_contract")
        result, _ = og.execute_mission(execute, self.root, self.client, json_mode=True)
        self.assertEqual(result["status"], "OATHBRINGER_EXECUTE_PASS")
        self.assertTrue(self.client.pull_requests[1]["merged"])
        self.assertIn(("mark_ready", 1), self.client.calls)
        self.assertIn(("merge_pull_request", 1, first["commit_sha"], "squash"), self.client.calls)

    def test_unknown_lesson_status_and_payload_escape_fail_closed(self) -> None:
        mission = base_mission(self.payload_sha)
        mission["lesson_applicability"][0]["status"] = "UNKNOWN"
        with self.assertRaisesRegex(og.OathbringerError, "invalid lesson status"):
            og.validate_mission(mission)
        mission = base_mission(self.payload_sha)
        mission["declared_paths"][0]["payload_path"] = "../outside.txt"
        with self.assertRaisesRegex(og.OathbringerError, "must not contain"):
            og.validate_mission(mission)

    def test_failure_after_candidate_tree_preserves_partial_remote_state(self) -> None:
        class CommitFailingClient(FakeGitHubClient):
            def create_commit(self, message: str, tree_sha: str, parent_sha: str) -> str:
                raise RuntimeError("simulated commit failure")
        mission = base_mission(self.payload_sha)
        context = og.ExecutionContext()
        with self.assertRaisesRegex(RuntimeError, "simulated commit failure"):
            og.execute_mission(mission, self.root, CommitFailingClient(), json_mode=True, context=context)
        self.assertTrue(context.github_called)
        self.assertTrue(context.mutation_performed)
        self.assertEqual(context.ledger.current_stage, "COMMIT")
        self.assertIn("candidate_tree_sha", context.remote_state)

    def test_prime_source_wires_thin_client_and_production_schema(self) -> None:
        launcher = (ROOT / "tools/atlas-sword/engine/Invoke-AtlasSword.ps1").read_text(encoding="utf-8")
        module = (ROOT / "tools/atlas-sword/engine/AtlasSword.Common.psm1").read_text(encoding="utf-8")
        schema = json.loads((ROOT / "tools/atlas-sword/schema/oathbringer-production-mission-v2.schema.json").read_text(encoding="utf-8"))
        doctrine = (ROOT / "methods/atlas-sword.md").read_text(encoding="utf-8")
        readme = (ROOT / "tools/atlas-sword/README.md").read_text(encoding="utf-8")
        self.assertIn("oathbringer_github.py", launcher)
        self.assertIn("Resolve-AtlasGitHubToken", module)
        self.assertIn("auth token", module)
        self.assertIn("OATHBRINGER_GITHUB_TOKEN", module)
        self.assertNotIn("Write-Host $Token", module)
        self.assertEqual(schema["properties"]["execution_environment"]["const"], "GITHUB")
        self.assertEqual(schema["properties"]["operator_interface"]["const"], "POWERSHELL")
        self.assertIn("PILOT_READY_PROOF_PENDING", doctrine)
        self.assertIn("Production mutation adapter", readme)
        self.assertIn("Wave 3", readme)

    def test_execute_rejects_audit_bound_to_another_head(self) -> None:
        mission = base_mission(self.payload_sha)
        mission.update({"lane": "EXECUTE", "expected_head": "e" * 40, "pull_request": 1, "independent_audit": {"verdict": "GREEN", "exact_head": "f" * 40, "receipt_sha256": "d" * 64}})
        mission.pop("commit_message")
        mission.pop("pull_request_contract")
        with self.assertRaisesRegex(og.OathbringerError, "independent audit"):
            og.validate_mission(mission)

if __name__ == "__main__":
    unittest.main()
