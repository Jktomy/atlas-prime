from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

THREAD_ENGINE = Path(__file__).resolve().parents[1]
if str(THREAD_ENGINE) not in sys.path:
    sys.path.insert(0, str(THREAD_ENGINE))

from production_adapter import resume


class ProductionAdapterResumeTests(unittest.TestCase):
    def write_mission(self, root: Path) -> tuple[Path, Path]:
        payload_root = root / "package" / "PAYLOADS"
        payload_root.mkdir(parents=True)
        payload = b"fixture\n"
        (payload_root / "fixture.txt").write_bytes(payload)
        mission = {
            "mission_id": "MISSION-TEST",
            "mission_sha256": "b" * 64,
            "repository": "Jktomy/atlas-prime",
            "remote_url": "https://github.com/Jktomy/atlas-prime.git",
            "base_sha": "a" * 40,
            "branch": "source/test",
            "commit_message": "test",
            "pr_title": "test",
            "pr_body": "test",
            "declared_paths": ["fixture.txt"],
            "payload_root": "PAYLOADS",
            "operations": [{
                "operation": "ADD",
                "path": "fixture.txt",
                "payload": "fixture.txt",
                "expected_output_sha256": hashlib.sha256(payload).hexdigest(),
            }],
        }
        path = root / "mission.json"
        path.write_text(json.dumps(mission), encoding="utf-8")
        return path, root / "package"

    def test_post_push_failure_is_partial(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            mission_path, package = self.write_mission(Path(directory))
            seal = {"seal_id": "MISSION-TEST:ATTEMPT:123", "seal_sha256": "c" * 64}
            exc = resume.AdapterError("after push", "READBACK_FAILED", "READBACK", partial=False)
            exc.receipt = {"last_completed_checkpoint": "PUSH", "head_sha": "d" * 40}
            remote = {"branch_exists": True, "head_sha": "d" * 40, "pull_request": None}
            mission = SimpleNamespace(
                mission_id="MISSION-TEST",
                mission_sha256="b" * 64,
                base_sha="a" * 40,
                branch="source/test",
                repository="Jktomy/atlas-prime",
            )
            with (
                patch.object(resume, "load_mission", return_value=mission),
                patch.object(resume, "_remote_state", return_value=remote),
            ):
                partial = resume._partial_receipt(exc, mission_path, package, seal)
            self.assertEqual(partial["result"], "PARTIAL")
            self.assertEqual(partial["remote_mutation"], "YES_EXACT")
            self.assertIs(partial["automatic_retry"], False)

    def test_cli_imports_from_thread_engine_working_directory(self) -> None:
        completed = subprocess.run(
            [sys.executable, "-B", "-m", "production_adapter.cli", "--help"],
            cwd=THREAD_ENGINE,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("candidate-seal", completed.stdout)

    def test_generic_cli_failure_is_reconciled_as_partial(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            mission_path, package = self.write_mission(Path(directory))
            exc = resume.AdapterError("after push", "READBACK_FAILED", "READBACK", partial=False)
            exc.receipt = {"last_completed_checkpoint": "PUSH", "head_sha": "d" * 40}
            remote = {"branch_exists": True, "head_sha": "d" * 40, "pull_request": None}
            mission = SimpleNamespace(
                mission_id="MISSION-TEST",
                mission_sha256="b" * 64,
                base_sha="a" * 40,
                branch="source/test",
                repository="Jktomy/atlas-prime",
            )
            with (
                patch.object(resume, "load_mission", return_value=mission),
                patch.object(resume, "_remote_state", return_value=remote),
            ):
                reconciled = resume.reconcile_adapter_error(mission_path, package_root=package, error=exc)
            self.assertIsNotNone(reconciled)
            if reconciled is None:
                self.fail("post-push reconciliation did not return a receipt")
            self.assertEqual(reconciled["result"], "PARTIAL")
            self.assertIsNone(reconciled["seal_id"])
            self.assertIs(reconciled["automatic_retry"], False)


if __name__ == "__main__":
    unittest.main()
