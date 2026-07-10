from __future__ import annotations

import io
import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ENGINE = ROOT / "tools/atlas-sword/engine"
sys.path.insert(0, str(ENGINE))

from oathbringer_console import OathbringerConsole, render_result_text
from oathbringer_deflected import create as create_deflected_sword
from oathbringer_support import wait_for_required_workflows


MISSION = {
    "mission_id": "CONSOLE-V2-PROOF",
    "sword_identity": "atlas-console-v2-r02",
    "lane": "REPAIR",
    "repository": "Jktomy/atlas-prime",
    "expected_base": "a" * 40,
    "expected_head": "b" * 40,
    "pull_request": 57,
    "authorization": {"github_login": "Jktomy"},
    "forbidden_actions": [
        "DIRECT_MAIN",
        "FORCE_PUSH",
        "SCOPE_WIDENING",
        "TOKEN_PERSISTENCE",
    ],
}


class FakeStream(io.StringIO):
    encoding = "utf-8"

    def isatty(self) -> bool:
        return True


class ConsoleV2Tests(unittest.TestCase):
    def test_plain_console_has_no_ansi_and_has_copy_block(self) -> None:
        stream = FakeStream()
        console = OathbringerConsole(
            stream=stream,
            color=False,
            unicode=False,
            monotonic=lambda: 10.0,
        )
        console.begin(MISSION)
        console.stage_enter("MISSION_CONTRACT", 3, "validate")
        console.stage_complete("contract valid")
        console.render_success(
            {
                "mission_id": "CONSOLE-V2-PROOF",
                "sword_identity": "atlas-console-v2-r02",
                "lane": "REPAIR",
                "repository": "Jktomy/atlas-prime",
                "status": "OATHBRINGER_REPAIR_PASS",
                "pull_request": 57,
                "expected_base": "a" * 40,
                "prior_head": "b" * 40,
                "commit_sha": "c" * 40,
                "changed_paths": ["proof/console-v2.txt"],
                "workflow_gate": {"status": "PASS", "required": {}},
                "completion_flags": {"mutation_performed": True},
                "stop_boundary": "Stop at the draft pull request.",
            }
        )
        output = stream.getvalue()
        self.assertNotIn("\x1b[", output)
        self.assertIn("O A T H B R I N G E R", output)
        self.assertIn("OATHBRINGER RESULT BLOCK", output)
        self.assertIn("Mutation performed: YES", output)
        self.assertIn("proof/console-v2.txt", output)

    def test_color_and_unicode_are_presentation_only(self) -> None:
        stream = FakeStream()
        console = OathbringerConsole(stream=stream, color=True, unicode=True)
        console.begin(MISSION)
        output = stream.getvalue()
        self.assertIn("\x1b[", output)
        self.assertIn("⚔", output)
        self.assertIn("Direct main write blocked", output)

    def test_failure_block_contains_repair_diagnostics(self) -> None:
        stream = FakeStream()
        console = OathbringerConsole(stream=stream, color=False, unicode=False)
        console.mission = MISSION
        console.render_failure(
            {
                "status": "OATHBRINGER_FAILED_PRESERVED_PARTIAL_STATE",
                "mission_id": "CONSOLE-V2-PROOF",
                "sword_identity": "atlas-console-v2-r02",
                "lane": "REPAIR",
                "repository": "Jktomy/atlas-prime",
                "detail": "simulated commit failure",
                "stage_ledger": {
                    "current_stage": "COMMIT",
                    "last_completed_stage": "CANDIDATE_TREE",
                },
                "remote_state": {
                    "pull_request": 57,
                    "candidate_tree_sha": "d" * 40,
                },
                "completion_flags": {"mutation_performed": True},
            }
        )
        output = stream.getvalue()
        self.assertIn("STRIKE DEFLECTED", output)
        self.assertIn("COMMIT", output)
        self.assertIn("CANDIDATE_TREE", output)
        self.assertIn("Deflected Sword ZIP", output)
        self.assertIn("Automatic retry: NO", output)

    def test_compatibility_renderer_is_plain_text(self) -> None:
        output = render_result_text(
            {
                "mission_id": "M",
                "sword_identity": "S",
                "lane": "BUILD",
                "repository": "R",
                "status": "PASS",
                "pull_request": 1,
                "commit_sha": "c" * 40,
                "changed_paths": [],
                "workflow_gate": {"status": "PASS", "required": {}},
                "completion_flags": {"mutation_performed": True},
                "stop_boundary": "Stop.",
            }
        )
        self.assertIn("STRIKE COMPLETE", output)
        self.assertNotIn("\x1b[", output)

    def test_python_creates_sanitized_deflected_sword(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            mission_path = root / "mission.json"
            receipt_path = root / "receipt.json"
            transcript_path = root / "terminal-output.txt"
            mission_path.write_text(json.dumps(MISSION) + "\n", encoding="utf-8")
            transcript_path.write_text("diagnostic output\n", encoding="utf-8")
            (root / "MANIFEST.json").write_text('{"files": []}\n', encoding="utf-8")
            receipt = {
                "status": "OATHBRINGER_FAILED_PRESERVED_PARTIAL_STATE",
                "mission_id": MISSION["mission_id"],
                "sword_identity": MISSION["sword_identity"],
                "lane": MISSION["lane"],
                "repository": MISSION["repository"],
                "detail": "simulated failure",
                "remote_state": {
                    "pull_request": 57,
                    "authorization_header": "must not survive",
                },
                "stage_ledger": {
                    "current_stage": "COMMIT",
                    "last_completed_stage": "CANDIDATE_TREE",
                },
                "completion_flags": {"mutation_performed": True},
                "result": {
                    "workflow_gate": {
                        "status": "FAIL",
                        "required": {"Prime": {"token": "must not survive"}},
                    }
                },
            }
            receipt_path.write_text(json.dumps(receipt) + "\n", encoding="utf-8")
            output_path = root / "Atlas-Deflected-Sword-test.zip"
            observed = create_deflected_sword(
                package_root=root,
                mission_path=mission_path,
                receipt_path=receipt_path,
                transcript_path=transcript_path,
                output_path=output_path,
                mission=MISSION,
                receipt=receipt,
            )
            self.assertEqual(observed, output_path.resolve())
            with zipfile.ZipFile(observed) as archive:
                names = set(archive.namelist())
                self.assertTrue(
                    {
                        "receipt.json",
                        "terminal-output.txt",
                        "mission.json",
                        "MANIFEST.json",
                        "failure-summary.txt",
                        "sanitized-remote-state.json",
                        "workflow-state.json",
                    }
                    <= names
                )
                remote = json.loads(archive.read("sanitized-remote-state.json"))
                workflow = json.loads(archive.read("workflow-state.json"))
                self.assertEqual(remote["authorization_header"], "<redacted>")
                self.assertEqual(
                    workflow["required"]["Prime"]["token"],
                    "<redacted>",
                )

    def test_power_shell_remains_ascii_only_and_thin(self) -> None:
        launcher_path = ENGINE / "Invoke-AtlasSword.ps1"
        module_path = ENGINE / "AtlasSword.Common.psm1"
        launcher = launcher_path.read_text(encoding="ascii")
        module = module_path.read_text(encoding="ascii")
        self.assertIn("OATHBRINGER_DEFLECTED_SWORD_PATH", launcher)
        self.assertIn("OATHBRINGER_TRANSCRIPT_PATH", launcher)
        self.assertIn("[switch]$NoColor", launcher)
        self.assertIn("[switch]$Ascii", launcher)
        self.assertNotIn("New-AtlasDeflectedSword", launcher)
        self.assertNotIn("ConvertFrom-Json", launcher)
        self.assertNotIn("ConvertTo-Json", launcher)
        self.assertNotIn("ConvertFrom-Json", module)
        self.assertNotIn("ConvertTo-Json", module)
        self.assertNotIn("Write-Host $Token", module)
        self.assertIn("Invoke-AtlasOathbringer", module)


class WorkflowClient:
    def __init__(self) -> None:
        self.calls = 0

    def list_workflow_runs(self, head: str):
        self.calls += 1
        if self.calls == 1:
            return [
                {
                    "id": 7,
                    "name": "Prime read-only validation",
                    "event": "pull_request",
                    "head_sha": head,
                    "status": "in_progress",
                    "conclusion": None,
                }
            ]
        return [
            {
                "id": 7,
                "name": "Prime read-only validation",
                "event": "pull_request",
                "head_sha": head,
                "status": "completed",
                "conclusion": "success",
            }
        ]


class WorkflowHeartbeatTests(unittest.TestCase):
    def test_waiter_reports_exact_run_state_to_presentation_callback(self) -> None:
        snapshots = []
        ticks = iter([0.0, 0.0, 1.0, 1.0, 2.0, 2.0])
        result = wait_for_required_workflows(
            WorkflowClient(),
            ["tools/atlas-sword/engine/oathbringer_console.py"],
            [
                {
                    "name": "Prime read-only validation",
                    "event": "pull_request",
                    "workflow_path": ".github/workflows/prime-validation.yml",
                    "workflow_blob": "a" * 40,
                    "appearance_grace_seconds": 5,
                    "completion_timeout_seconds": 5,
                    "expected_conclusion": "success",
                }
            ],
            "h" * 40,
            sleep=lambda _: None,
            monotonic=lambda: next(ticks),
            poll_seconds=0,
            progress=snapshots.append,
        )
        self.assertEqual(result["status"], "PASS")
        self.assertGreaterEqual(len(snapshots), 2)
        self.assertEqual(
            snapshots[-1]["required"]["Prime read-only validation"]["status"],
            "COMPLETED",
        )
        self.assertEqual(
            snapshots[-1]["required"]["Prime read-only validation"]["run_id"],
            7,
        )


if __name__ == "__main__":
    unittest.main()
