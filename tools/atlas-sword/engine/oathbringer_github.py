from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

from oathbringer_api import GitHubClient
from oathbringer_console import OathbringerConsole, render_result_text
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
    return {
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
            "receipt_written": True,
            "github_called": context.github_called,
            "mutation_performed": context.mutation_performed,
            "automatic_retry": False,
            "automatic_rollback": False,
            "token_persisted": False,
        },
    }


def _default_receipt_path(mission_path: Path) -> Path:
    return mission_path.with_name(f"{mission_path.stem}.oathbringer.receipt.json")


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
        _require(bool(token), "OATHBRINGER_GITHUB_TOKEN was not provided by the thin PowerShell client")
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
        try:
            atomic_write_json_with_sha256(receipt_path, receipt)
        finally:
            if args.json:
                print(json.dumps(receipt, indent=2, sort_keys=True))
            elif console is not None:
                console.render_failure(receipt, interrupted=True)
            else:
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
        try:
            atomic_write_json_with_sha256(receipt_path, receipt)
        finally:
            if args.json:
                print(json.dumps(receipt, indent=2, sort_keys=True))
            elif console is not None:
                console.render_failure(receipt)
            else:
                print(f"\nOathbringer failed closed: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
