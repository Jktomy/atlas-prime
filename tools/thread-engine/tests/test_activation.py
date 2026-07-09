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


class ActivationTests(unittest.TestCase):
    def test_repository_state_is_disabled_and_consistent(self) -> None:
        state = load_activation_state()
        self.assertEqual(state["implementation_state"], DISABLED_STATE)
        self.assertFalse(state["production_execution_authorized"])
        self.assertTrue(state["proof_required"])

    def test_direct_execute_mission_rejects_while_disabled_with_truthful_receipt(self) -> None:
        with tempfile.TemporaryDirectory(prefix="prime-thread-engine-disabled-") as tmp_text:
            root = Path(tmp_text)
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
        result = subprocess.run(
            [pwsh, "-NoLogo", "-NoProfile", "-File", str(ROOT / "Invoke-AtlasThreadEngineProductionAdapter.ps1")],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("PORT_CANDIDATE_DISABLED", result.stdout + result.stderr)

    def test_active_receipt_fields_are_derived_from_active_state(self) -> None:
        with tempfile.TemporaryDirectory(prefix="prime-thread-engine-active-receipt-") as tmp_text:
            journal = Journal(Path(tmp_text) / "journal.jsonl")
            receipt = _receipt(None, "REJECTED", journal, "PACKAGE_AUDIT", activation_state=dict(ACTIVE))
            self.assertEqual(receipt["implementation_state"], ACTIVE_STATE)
            self.assertEqual(receipt["adapter_mode"], "DRAFT_PR_ONLY")
            self.assertTrue(receipt["thread_engine_active"])
            self.assertTrue(receipt["production_execution_authorized"])
            self.assertEqual(receipt["authority_scope"], "MISSION_SCOPED")

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
