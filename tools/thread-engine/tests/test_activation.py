from __future__ import annotations

import contextlib
import io
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from production_adapter.activation import ACTIVE_STATE, DISABLED_STATE, ActivationError, load_activation_state
from production_adapter.adapter import AdapterError, Journal, _receipt, execute_mission
from production_adapter.cli import main as cli_main


ACTIVE = {
    "implementation_state": ACTIVE_STATE,
    "production_execution_authorized": True,
    "proof_required": False,
    "standing_authority": False,
    "automatic_merge": False,
    "direct_main": False,
}

DISABLED = {
    "implementation_state": DISABLED_STATE,
    "production_execution_authorized": False,
    "proof_required": True,
    "standing_authority": False,
    "automatic_merge": False,
    "direct_main": False,
}


class ActivationTests(unittest.TestCase):
    def test_repository_state_is_active_mission_scoped_and_consistent(self) -> None:
        state = load_activation_state()
        self.assertEqual(state["implementation_state"], ACTIVE_STATE)
        self.assertTrue(state["production_execution_authorized"])
        self.assertFalse(state["proof_required"])
        self.assertFalse(state["standing_authority"])
        self.assertFalse(state["automatic_merge"])
        self.assertFalse(state["direct_main"])

    def test_direct_execute_mission_rejects_while_disabled_with_truthful_receipt(self) -> None:
        with tempfile.TemporaryDirectory(prefix="prime-thread-engine-disabled-") as tmp_text:
            root = Path(tmp_text)
            with patch("production_adapter.adapter.load_activation_state", return_value=dict(DISABLED)):
                with self.assertRaises(AdapterError) as raised:
                    execute_mission(
                        root / "missing-mission.json",
                        mission_scoped=True,
                        execute_draft_pr=True,
                        work_root=root,
                        package_root=root,
                    )
            self.assertEqual(raised.exception.code, "THREAD_ENGINE_DISABLED")
            self.assertEqual(raised.exception.stage, "ACTIVATION_GATE")
            receipt = raised.exception.receipt
            self.assertIsNotNone(receipt)
            self.assertEqual(receipt["implementation_state"], DISABLED_STATE)
            self.assertEqual(receipt["adapter_mode"], "DISABLED")
            self.assertFalse(receipt["thread_engine_active"])
            self.assertFalse(receipt["production_execution_authorized"])
            self.assertEqual(receipt["authority_scope"], "NONE")

    def test_cli_rejects_while_disabled(self) -> None:
        with tempfile.TemporaryDirectory(prefix="prime-thread-engine-cli-disabled-") as tmp_text:
            root = Path(tmp_text)
            stderr = io.StringIO()
            with patch("production_adapter.adapter.load_activation_state", return_value=dict(DISABLED)):
                with contextlib.redirect_stderr(stderr):
                    result = cli_main(
                        [
                            "--mission",
                            str(root / "missing-mission.json"),
                            "--mission-scoped-draft-pr",
                            "--execute-draft-pr",
                            "--work-root",
                            str(root),
                        ]
                    )
            self.assertEqual(result, 2)
            body = json.loads(stderr.getvalue())
            self.assertEqual(body["error_code"], "THREAD_ENGINE_DISABLED")
            self.assertFalse(body["thread_engine_active"])

    def test_powershell_launcher_rejects_while_disabled(self) -> None:
        pwsh = shutil.which("pwsh")
        if not pwsh:
            self.skipTest("PowerShell 7 is unavailable")
        with tempfile.TemporaryDirectory(prefix="prime-thread-engine-pwsh-disabled-") as tmp_text:
            copied_repo = Path(tmp_text) / "repo"
            copied_root = copied_repo / "tools" / "thread-engine"
            copied_root.parent.mkdir(parents=True)
            shutil.copytree(ROOT, copied_root)
            shutil.copytree(ROOT.parents[1] / "policies", copied_repo / "policies")
            status_path = copied_root / "PRIME-PORT-STATUS.json"
            status = json.loads(status_path.read_text(encoding="utf-8"))
            status.update(DISABLED)
            status_path.write_text(json.dumps(status), encoding="utf-8")
            mission_path = copied_root / "disabled-proof-mission.json"
            mission_path.write_text("{}\n", encoding="utf-8")
            result = subprocess.run(
                [
                    pwsh,
                    "-NoLogo",
                    "-NoProfile",
                    "-File",
                    str(copied_root / "Invoke-AtlasThreadEngineProductionAdapter.ps1"),
                    "-MissionPath",
                    str(mission_path),
                    "-MissionScopedDraftPr",
                    "-ExecuteDraftPr",
                    "-WorkRoot",
                    str(copied_root / "work"),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            output = result.stdout + result.stderr
            self.assertIn("THREAD_ENGINE_DISABLED", output)
            self.assertIn('"thread_engine_active": false', output)

    def test_powershell_launcher_resolves_native_python_while_active(self) -> None:
        pwsh = shutil.which("pwsh")
        if not pwsh:
            self.skipTest("PowerShell 7 is unavailable")
        result = subprocess.run(
            [
                pwsh,
                "-NoLogo",
                "-NoProfile",
                "-File",
                str(ROOT / "Invoke-AtlasThreadEngineProductionAdapter.ps1"),
                "-ResolverSelfTest",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        body = json.loads(result.stdout)
        self.assertEqual(body["invocation"], "native-argument-array")
        self.assertEqual(body["implementation_state"], ACTIVE_STATE)

    def test_active_receipt_fields_are_derived_from_active_state(self) -> None:
        with tempfile.TemporaryDirectory(prefix="prime-thread-engine-active-receipt-") as tmp_text:
            journal = Journal(Path(tmp_text) / "journal.jsonl")
            receipt = _receipt(None, "REJECTED", journal, "PACKAGE_AUDIT", activation_state=dict(ACTIVE))
            self.assertEqual(receipt["implementation_state"], ACTIVE_STATE)
            self.assertEqual(receipt["adapter_mode"], "DRAFT_PR_ONLY")
            self.assertTrue(receipt["thread_engine_active"])
            self.assertTrue(receipt["production_execution_authorized"])
            self.assertEqual(receipt["authority_scope"], "MISSION_SCOPED")
            self.assertFalse(receipt["production_authority_activated"])

    def test_inconsistent_or_unsafe_activation_state_fails_closed(self) -> None:
        cases = [
            {**ACTIVE, "production_execution_authorized": False},
            {**ACTIVE, "standing_authority": True},
            {**ACTIVE, "automatic_merge": True},
            {**ACTIVE, "direct_main": True},
            {**ACTIVE, "implementation_state": "UNKNOWN"},
        ]
        for data in cases:
            with self.subTest(data=data), tempfile.TemporaryDirectory(prefix="prime-thread-engine-state-") as tmp_text:
                path = Path(tmp_text) / "status.json"
                path.write_text(json.dumps(data), encoding="utf-8")
                with self.assertRaises(ActivationError):
                    load_activation_state(path)


if __name__ == "__main__":
    unittest.main()
