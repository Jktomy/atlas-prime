from __future__ import annotations

import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ENGINE = ROOT / "tools/atlas-sword/engine"
sys.path.insert(0, str(ENGINE))

from oathbringer_console import OathbringerConsole, render_result_text
from oathbringer_core import ExecutionContext
from oathbringer_deflected import create as create_deflected_sword
from oathbringer_deflected import DeflectedSwordError
from oathbringer_deflected import sanitize_text
from oathbringer_deflected import verify as verify_deflected_sword
from oathbringer_github import build_receipt
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
CLASSIC_GITHUB_MARKER = "gh" + "p_" + "abcdefghijklmnopqrstuvwxyz123456"
FINE_GITHUB_MARKER = "github" + "_pat_" + "abcdefghijklmnopqrstuvwxyz123456"
MODEL_KEY_MARKER = "s" + "k-" + "abcdefghijklmnopqrstuvwxyz123456"
BEARER_MARKER = "Bear" + "er " + "abcdefghijklmnopqrstuvwxyz123456"


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
            transcript_path.write_text(
                f"diagnostic {CLASSIC_GITHUB_MARKER}\n",
                encoding="utf-8",
            )
            (root / "MANIFEST.json").write_text('{"files": []}\n', encoding="utf-8")
            receipt = {
                "status": "OATHBRINGER_FAILED_PRESERVED_PARTIAL_STATE",
                "mission_id": MISSION["mission_id"],
                "sword_identity": MISSION["sword_identity"],
                "lane": MISSION["lane"],
                "repository": MISSION["repository"],
                "detail": f"simulated failure with {FINE_GITHUB_MARKER}",
                "remote_state": {
                    "pull_request": 57,
                    "authorization_header": "must not survive",
                    "note": BEARER_MARKER,
                },
                "stage_ledger": {
                    "current_stage": "COMMIT",
                    "last_completed_stage": "CANDIDATE_TREE",
                },
                "completion_flags": {"mutation_performed": True},
                "result": {
                    "workflow_gate": {
                        "status": "FAIL",
                        "required": {
                            "Prime": {
                                "token": "must not survive",
                                "note": MODEL_KEY_MARKER,
                            }
                        },
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
                self.assertEqual(remote["note"], "<redacted>")
                self.assertEqual(
                    workflow["required"]["Prime"]["token"],
                    "<redacted>",
                )
                self.assertEqual(workflow["required"]["Prime"]["note"], "<redacted>")
                combined = b"\n".join(archive.read(name) for name in archive.namelist())
                for marker in (
                    CLASSIC_GITHUB_MARKER.encode("ascii"),
                    FINE_GITHUB_MARKER.encode("ascii"),
                    b"abcdefghijklmnopqrstuvwxyz123456",
                ):
                    self.assertNotIn(marker, combined)
            verification = verify_deflected_sword(observed)
            self.assertEqual(verification["archive_sha256"], hashlib.sha256(observed.read_bytes()).hexdigest())
            self.assertEqual(
                observed.with_suffix(observed.suffix + ".sha256").read_text(encoding="ascii"),
                f"{verification['archive_sha256']}  {observed.name}\n",
            )
            second_output = root / "Atlas-Deflected-Sword-test-second.zip"
            create_deflected_sword(
                package_root=root,
                mission_path=mission_path,
                receipt_path=receipt_path,
                transcript_path=transcript_path,
                output_path=second_output,
                mission=MISSION,
                receipt=receipt,
            )
            self.assertEqual(observed.read_bytes(), second_output.read_bytes())

            tampered = root / "Atlas-Deflected-Sword-tampered.zip"
            with zipfile.ZipFile(observed) as archive:
                members = {name: archive.read(name) for name in archive.namelist()}
            control = json.loads(members["MANIFEST.json"])
            control["note"] = CLASSIC_GITHUB_MARKER
            members["MANIFEST.json"] = (
                json.dumps(control, sort_keys=True, separators=(",", ":")) + "\n"
            ).encode("utf-8")
            members["SHA256SUMS.txt"] = "".join(
                f"{hashlib.sha256(members[name]).hexdigest()}  {name}\n"
                for name in sorted(members)
                if name != "SHA256SUMS.txt"
            ).encode("ascii")
            with zipfile.ZipFile(tampered, "w", compression=zipfile.ZIP_STORED) as archive:
                for name in sorted(members):
                    info = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
                    info.create_system = 3
                    info.external_attr = 0o100644 << 16
                    info.compress_type = zipfile.ZIP_STORED
                    archive.writestr(info, members[name])
            tampered_digest = hashlib.sha256(tampered.read_bytes()).hexdigest()
            tampered.with_suffix(tampered.suffix + ".sha256").write_text(
                f"{tampered_digest}  {tampered.name}\n",
                encoding="ascii",
                newline="\n",
            )
            with self.assertRaisesRegex(DeflectedSwordError, "protected material"):
                verify_deflected_sword(tampered)

            malformed = root / "Atlas-Deflected-Sword-malformed.zip"
            malformed.write_bytes(b"not a zip")
            malformed_digest = hashlib.sha256(malformed.read_bytes()).hexdigest()
            malformed.with_suffix(malformed.suffix + ".sha256").write_text(
                f"{malformed_digest}  {malformed.name}\n",
                encoding="ascii",
                newline="\n",
            )
            with self.assertRaisesRegex(DeflectedSwordError, "safely verified"):
                verify_deflected_sword(malformed)

            self.assertEqual(
                create_deflected_sword(
                    package_root=root,
                    mission_path=mission_path,
                    receipt_path=receipt_path,
                    transcript_path=transcript_path,
                    output_path=output_path,
                    mission=MISSION,
                    receipt=receipt,
                ),
                observed,
            )

            missing_sidecar = root / "Atlas-Deflected-Sword-missing-sidecar.zip"
            missing_sidecar.write_bytes(observed.read_bytes())
            create_deflected_sword(
                package_root=root,
                mission_path=mission_path,
                receipt_path=receipt_path,
                transcript_path=transcript_path,
                output_path=missing_sidecar,
                mission=MISSION,
                receipt=receipt,
            )
            self.assertTrue(missing_sidecar.with_suffix(missing_sidecar.suffix + ".sha256").is_file())

            sidecar_first = root / "Atlas-Deflected-Sword-sidecar-first.zip"
            sidecar_first_digest = hashlib.sha256(observed.read_bytes()).hexdigest()
            sidecar_first.with_suffix(sidecar_first.suffix + ".sha256").write_text(
                f"{sidecar_first_digest}  {sidecar_first.name}\n",
                encoding="ascii",
                newline="\n",
            )
            create_deflected_sword(
                package_root=root,
                mission_path=mission_path,
                receipt_path=receipt_path,
                transcript_path=transcript_path,
                output_path=sidecar_first,
                mission=MISSION,
                receipt=receipt,
            )
            self.assertEqual(sidecar_first.read_bytes(), observed.read_bytes())

            collision_receipt = dict(receipt)
            collision_receipt["detail"] = "different sanitized failure"
            with self.assertRaisesRegex(DeflectedSwordError, "already exists"):
                create_deflected_sword(
                    package_root=root,
                    mission_path=mission_path,
                    receipt_path=receipt_path,
                    transcript_path=transcript_path,
                    output_path=output_path,
                    mission=MISSION,
                    receipt=collision_receipt,
                )

            symlink = root / "Atlas-Deflected-Sword-link.zip"
            try:
                symlink.symlink_to(observed)
            except OSError:
                pass
            else:
                with self.assertRaisesRegex(DeflectedSwordError, "symlink"):
                    verify_deflected_sword(symlink)
                with self.assertRaisesRegex(DeflectedSwordError, "symlink"):
                    create_deflected_sword(
                        package_root=root,
                        mission_path=mission_path,
                        receipt_path=receipt_path,
                        transcript_path=transcript_path,
                        output_path=symlink,
                        mission=MISSION,
                        receipt=receipt,
                    )

    def test_durable_receipt_recursively_sanitizes_remote_and_exception_values(self) -> None:
        context = ExecutionContext()
        context.remote_state = {
            "note": BEARER_MARKER,
            "authorization": "must not survive",
            CLASSIC_GITHUB_MARKER: "must not survive as a key",
        }
        receipt = build_receipt(
            MISSION,
            context,
            status="OATHBRINGER_FAILED_PRESERVED_PARTIAL_STATE",
            result={"diagnostic": CLASSIC_GITHUB_MARKER},
            detail=FINE_GITHUB_MARKER,
            exit_code=1,
        )
        encoded = json.dumps(receipt, sort_keys=True)
        self.assertNotIn(CLASSIC_GITHUB_MARKER, encoded)
        self.assertNotIn(FINE_GITHUB_MARKER, encoded)
        self.assertNotIn(BEARER_MARKER, encoded)
        self.assertEqual(receipt["remote_state"]["authorization"], "<redacted>")
        self.assertEqual(receipt["remote_state"]["<redacted-key>"], "<redacted>")
        self.assertFalse(receipt["completion_flags"]["receipt_written"])
        self.assertFalse(receipt["completion_flags"]["token_persisted"])

        nested = build_receipt(
            MISSION,
            context,
            status="OATHBRINGER_FAILED_PRESERVED_PARTIAL_STATE",
            result={"authorization": {"value": "opaquecredential"}, "token": ["opaquecredential"]},
            detail=None,
            exit_code=1,
        )
        self.assertEqual(nested["result"]["authorization"], "<redacted>")
        self.assertEqual(nested["result"]["token"], "<redacted>")

    def test_private_runtime_locations_are_fully_redacted(self) -> None:
        for value in (
            r"C:\Users\Alice\SecretClient\incident.txt",
            r"C:\Users\Alice\Secret,Client;case\incident.txt",
            "/home/alice/SecretClient/incident.txt",
            "/home/alice/Secret,Client;case/incident.txt",
        ):
            with self.subTest(value=value):
                self.assertEqual(sanitize_text(value), "<redacted-home>")

    def test_powershell_json_preflight_failure_is_one_document(self) -> None:
        shell = shutil.which("pwsh") or shutil.which("powershell")
        if shell is None:
            self.skipTest("PowerShell is unavailable")
        launcher = ENGINE / "Invoke-AtlasSword.ps1"
        missing = ENGINE / "missing-production-mission.json"
        completed = subprocess.run(
            [shell, "-NoProfile", "-File", str(launcher), "-MissionPath", str(missing), "-Json", "-NoColor", "-Ascii"],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        self.assertEqual(completed.returncode, 1)
        value = json.loads(completed.stdout)
        self.assertEqual(
            value,
            {
                "error_code": "OATHBRINGER_LAUNCHER_FAILED",
                "exit_code": 1,
                "status": "OATHBRINGER_LAUNCHER_FAILED",
            },
        )
        self.assertNotIn("STRIKE DEFLECTED", completed.stdout)

    def test_powershell_json_artifact_write_failure_remains_one_sanitized_document(self) -> None:
        shell = shutil.which("pwsh") or shutil.which("powershell")
        if shell is None:
            self.skipTest("PowerShell is unavailable")
        launcher = ENGINE / "Invoke-AtlasSword.ps1"
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            mission = root / "outside-package-mission.json"
            mission.write_text("{}\n", encoding="utf-8")
            receipt_directory = root / "receipt-is-a-directory"
            receipt_directory.mkdir()
            environment = dict(os.environ)
            environment["OATHBRINGER_GITHUB_TOKEN"] = "synthetic-not-a-real-token"
            completed = subprocess.run(
                [
                    shell,
                    "-NoProfile",
                    "-File",
                    str(launcher),
                    "-MissionPath",
                    str(mission),
                    "-ReceiptPath",
                    str(receipt_directory),
                    "-Json",
                    "-NoColor",
                    "-Ascii",
                ],
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                env=environment,
            )
        self.assertEqual(completed.returncode, 1)
        value = json.loads(completed.stdout)
        self.assertEqual(value["status"], "OATHBRINGER_FAILED_PRESERVED_PARTIAL_STATE")
        self.assertFalse(value["completion_flags"]["receipt_written"])
        self.assertIn(
            "RECEIPT_WRITE_FAILED",
            {item["error_code"] for item in value["artifact_failures"]},
        )
        self.assertNotIn(str(Path.home()), completed.stdout)
        self.assertNotIn("Traceback", completed.stderr)

    def test_foundry_json_rejection_is_one_document(self) -> None:
        cli = ROOT / "tools/oathbringer-foundry/cli.py"
        with tempfile.TemporaryDirectory() as temp_dir:
            malformed = Path(temp_dir) / "malformed.zip"
            malformed.write_bytes(b"not a zip")
            for carrier in (ROOT / "missing-carrier.zip", malformed):
                with self.subTest(carrier=carrier.name):
                    completed = subprocess.run(
                        [sys.executable, "-B", str(cli), "verify", "--carrier", str(carrier), "--json"],
                        check=False,
                        capture_output=True,
                        text=True,
                        encoding="utf-8",
                    )
                    self.assertEqual(completed.returncode, 1)
                    self.assertEqual(json.loads(completed.stdout)["error_code"], "FOUNDRY_REJECTED")
                    self.assertEqual(completed.stderr, "")

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
