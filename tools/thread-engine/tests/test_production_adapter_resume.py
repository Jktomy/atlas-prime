from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

THREAD_ENGINE = Path(__file__).resolve().parents[1]
if str(THREAD_ENGINE) not in sys.path:
    sys.path.insert(0, str(THREAD_ENGINE))

from production_adapter import resume


def write_mission(tmp_path: Path) -> tuple[Path, Path]:
    payload_root = tmp_path / "package" / "PAYLOADS"
    payload_root.mkdir(parents=True)
    payload = b"fixture\n"
    (payload_root / "fixture.txt").write_bytes(payload)
    import hashlib
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
    path = tmp_path / "mission.json"
    path.write_text(json.dumps(mission), encoding="utf-8")
    return path, tmp_path / "package"


def test_post_push_failure_is_partial(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    mission_path, package = write_mission(tmp_path)
    seal = {"seal_id": "MISSION-TEST:ATTEMPT:123", "seal_sha256": "c" * 64}
    exc = resume.AdapterError("after push", "READBACK_FAILED", "READBACK", partial=False)
    exc.receipt = {"last_completed_checkpoint": "PUSH", "head_sha": "d" * 40}
    monkeypatch.setattr(resume, "_remote_state", lambda *_: {"branch_exists": True, "head_sha": "d" * 40, "pull_request": None})
    partial = resume._partial_receipt(exc, mission_path, package, seal)
    assert partial["result"] == "PARTIAL"
    assert partial["remote_mutation"] == "YES_EXACT"
    assert partial["automatic_retry"] is False

def test_cli_imports_from_thread_engine_working_directory() -> None:
    import subprocess
    completed = subprocess.run(
        [sys.executable, "-B", "-m", "production_adapter.cli", "--help"],
        cwd=THREAD_ENGINE,
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr
    assert "candidate-seal" in completed.stdout

def test_generic_cli_failure_is_reconciled_as_partial(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    mission_path, package = write_mission(tmp_path)
    exc = resume.AdapterError("after push", "READBACK_FAILED", "READBACK", partial=False)
    exc.receipt = {"last_completed_checkpoint": "PUSH", "head_sha": "d" * 40}
    monkeypatch.setattr(resume, "_remote_state", lambda *_: {"branch_exists": True, "head_sha": "d" * 40, "pull_request": None})
    reconciled = resume.reconcile_adapter_error(mission_path, package_root=package, error=exc)
    assert reconciled is not None
    assert reconciled["result"] == "PARTIAL"
    assert reconciled["seal_id"] is None
    assert reconciled["automatic_retry"] is False
