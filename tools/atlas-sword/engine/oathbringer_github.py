from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

from oathbringer_api import GitHubClient
from oathbringer_console import OathbringerConsole, render_result_text
from oathbringer_deflected import create as create_deflected_sword
from oathbringer_deflected import resolve_path as resolve_deflected_sword_path
from oathbringer_deflected import sanitize_evidence
from oathbringer_deflected import verify as verify_deflected_sword
from oathbringer_core import (
    CHANGE_METHOD,
    EXECUTION_ENVIRONMENT,
    FORMAT_VERSION,
    OPERATOR_INTERFACE,
    RUNTIME_MODE,
    ExecutionContext,
    OathbringerError,
    _require,
    validate_mission,
)
from oathbringer_runtime import changed_paths_between, execute_mission
from oathbringer_support import atomic_write_json_with_sha256


def render_result(result: dict[str, Any]) -> str:
    return render_result_text(result)


def build_receipt(
    mission: dict[str, Any] | None,
    context: ExecutionContext,
    *,
    status: str,
    result: dict[str, Any] | None,
    detail: str | None,
    exit_code: int,
) -> dict[str, Any]:
    receipt = {
        "receipt_version": "2.0",
        "format_version": FORMAT_VERSION,
        "change_method": CHANGE_METHOD,
        "execution_environment": EXECUTION_ENVIRONMENT,
        "operator_interface": OPERATOR_INTERFACE,
        "runtime_mode": RUNTIME_MODE,
        "status": status,
        "detail": detail,
        "exit_code": exit_code,
        "mission_id": None if mission is None else mission.get("mission_id"),
        "sword_identity": None if mission is None else mission.get("sword_identity"),
        "lane": None if mission is None else mission.get("lane"),
        "repository": None if mission is None else mission.get("repository"),
        "expected_base": None if mission is None else mission.get("expected_base"),
        "expected_head": None if mission is None else mission.get("expected_head"),
        "result": result,
        "remote_state": context.remote_state,
        "stage_ledger": context.ledger.as_dict(),
        "completion_flags": {
            "receipt_written": False,
            "github_called": context.github_called,
            "mutation_performed": context.mutation_performed,
            "automatic_retry": False,
            "automatic_rollback": False,
            "token_persisted": False,
        },
    }
    return sanitize_evidence(receipt)


def _default_receipt_path(mission_path: Path) -> Path:
    return mission_path.with_name(f"{mission_path.stem}.oathbringer.receipt.json")


def _optional_environment_path(name: str) -> Path | None:
    value = os.environ.get(name, "").strip()
    return Path(value).expanduser().resolve() if value else None


def _sanitize_receipt_in_place(receipt: dict[str, Any]) -> None:
    sanitized = sanitize_evidence(receipt)
    receipt.clear()
    receipt.update(sanitized)


def _record_artifact_failure(receipt: dict[str, Any], error_code: str) -> None:
    failures = receipt.setdefault("artifact_failures", [])
    if isinstance(failures, list) and error_code not in {item.get("error_code") for item in failures if isinstance(item, dict)}:
        failures.append({"error_code": error_code})


def _try_write_receipt(receipt_path: Path, receipt: dict[str, Any]) -> bool:
    flags = receipt.setdefault("completion_flags", {})
    if isinstance(flags, dict):
        flags["receipt_written"] = True
    _sanitize_receipt_in_place(receipt)
    try:
        atomic_write_json_with_sha256(receipt_path, receipt)
        return True
    except Exception:
        current_flags = receipt.setdefault("completion_flags", {})
        if isinstance(current_flags, dict):
            current_flags["receipt_written"] = False
        _record_artifact_failure(receipt, "RECEIPT_WRITE_FAILED")
        _sanitize_receipt_in_place(receipt)
        return False


def _write_failure_artifacts(
    *,
    mission: dict[str, Any] | None,
    receipt: dict[str, Any],
    package_root: Path,
    mission_path: Path,
    receipt_path: Path,
    console: OathbringerConsole | None,
    interrupted: bool,
    json_mode: bool,
) -> Path | None:
    explicit = os.environ.get("OATHBRINGER_DEFLECTED_SWORD_PATH", "").strip() or None
    try:
        destination = resolve_deflected_sword_path(mission, receipt_path, explicit)
    except Exception:
        receipt["deflected_sword"] = {"created": False, "error_code": "DEFLECTED_SWORD_PATH_FAILED"}
        _record_artifact_failure(receipt, "DEFLECTED_SWORD_PATH_FAILED")
        _try_write_receipt(receipt_path, receipt)
        return None
    receipt["deflected_sword_path"] = sanitize_evidence(str(destination))
    _try_write_receipt(receipt_path, receipt)

    if not json_mode and console is not None:
        try:
            console.render_failure(receipt, interrupted=interrupted)
        except Exception:
            _record_artifact_failure(receipt, "CONSOLE_RENDER_FAILED")

    try:
        deflected = create_deflected_sword(
            package_root=package_root,
            mission_path=mission_path,
            receipt_path=receipt_path,
            transcript_path=_optional_environment_path("OATHBRINGER_TRANSCRIPT_PATH"),
            output_path=destination,
            mission=mission,
            receipt=receipt,
        )
        verification = verify_deflected_sword(deflected)
        receipt["deflected_sword"] = {
            "created": True,
            "archive_path": sanitize_evidence(verification["archive_path"]),
            "archive_sha256": verification["archive_sha256"],
            "sidecar_path": sanitize_evidence(verification["sidecar_path"]),
            "member_count": verification["member_count"],
        }
        _try_write_receipt(receipt_path, receipt)
    except Exception:
        receipt["deflected_sword"] = {
            "created": False,
            "error_code": "DEFLECTED_SWORD_CREATE_FAILED",
        }
        _record_artifact_failure(receipt, "DEFLECTED_SWORD_CREATE_FAILED")
        _try_write_receipt(receipt_path, receipt)
        if not json_mode:
            print("\nDeflected Sword creation failed safely.", flush=True)
        return None

    if not json_mode:
        print(f"\nDeflected Sword: {sanitize_evidence(str(deflected))}", flush=True)
    return deflected


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mission", required=True)
    parser.add_argument("--package-root", required=True)
    parser.add_argument("--receipt")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    mission_path = Path(args.mission).resolve()
    package_root = Path(args.package_root).resolve()
    receipt_path = Path(args.receipt).resolve() if args.receipt else _default_receipt_path(mission_path)
    context = ExecutionContext()
    mission: dict[str, Any] | None = None
    result: dict[str, Any] | None = None
    console: OathbringerConsole | None = None

    try:
        _require(
            mission_path == package_root or package_root in mission_path.parents,
            "production mission must be inside the sealed package root",
        )
        mission_relative_path = mission_path.relative_to(package_root).as_posix()
        mission = json.loads(mission_path.read_text(encoding="utf-8"))
        if not args.json:
            console = OathbringerConsole()
            context.console = console
            console.begin(mission)

        token = os.environ.get("OATHBRINGER_GITHUB_TOKEN", "")
        _require(
            bool(token),
            "OATHBRINGER_GITHUB_TOKEN was not provided by the thin PowerShell client",
        )
        client = GitHubClient(token, str(mission.get("repository") or ""))
        result, context = execute_mission(
            mission,
            package_root,
            client,
            mission_relative_path=mission_relative_path,
            json_mode=args.json,
            context=context,
        )
        result["mission_id"] = mission["mission_id"]
        result["sword_identity"] = mission["sword_identity"]
        receipt = build_receipt(
            mission,
            context,
            status=result["status"],
            result=result,
            detail=None,
            exit_code=0,
        )
        receipt["completion_flags"]["receipt_written"] = True
        result["receipt_write"] = atomic_write_json_with_sha256(receipt_path, receipt)
        if args.json:
            print(json.dumps(result, indent=2, sort_keys=True))
        elif console is not None:
            console.render_success(result)
        else:
            print(render_result(result))
        return 0

    except KeyboardInterrupt:
        context.ledger.fail("operator interrupt")
        receipt = build_receipt(
            mission,
            context,
            status="OATHBRINGER_INTERRUPTED_PRESERVED_PARTIAL_STATE",
            result=result,
            detail="operator interrupt",
            exit_code=130,
        )
        _write_failure_artifacts(
            mission=mission,
            receipt=receipt,
            package_root=package_root,
            mission_path=mission_path,
            receipt_path=receipt_path,
            console=console,
            interrupted=True,
            json_mode=args.json,
        )
        if args.json:
            print(json.dumps(receipt, indent=2, sort_keys=True))
        elif console is None:
            print("\nOathbringer interrupted; partial state preserved in receipt.")
        return 130

    except Exception as exc:
        context.ledger.fail(str(exc))
        receipt = build_receipt(
            mission,
            context,
            status="OATHBRINGER_FAILED_PRESERVED_PARTIAL_STATE",
            result=result,
            detail=str(exc),
            exit_code=1,
        )
        _write_failure_artifacts(
            mission=mission,
            receipt=receipt,
            package_root=package_root,
            mission_path=mission_path,
            receipt_path=receipt_path,
            console=console,
            interrupted=False,
            json_mode=args.json,
        )
        if args.json:
            print(json.dumps(receipt, indent=2, sort_keys=True))
        elif console is None:
            print(f"\nOathbringer failed closed: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
