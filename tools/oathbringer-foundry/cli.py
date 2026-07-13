from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from foundry import FoundryError, compile_carrier, load_json, read_live_state, verify_carrier


REPLAY_LEDGER_NAME = "FOUNDRY-REPLAY-LEDGER.json"


def _read_replay_ledger(path: Path) -> list[str]:
    if not path.exists():
        return []
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise FoundryError("production replay ledger is unreadable") from exc
    if not isinstance(value, dict) or set(value) != {"format_version", "mission_ids"} or value["format_version"] != "1.0":
        raise FoundryError("production replay ledger is malformed")
    mission_ids = value["mission_ids"]
    if not isinstance(mission_ids, list) or any(not isinstance(item, str) for item in mission_ids) or len(mission_ids) != len(set(mission_ids)):
        raise FoundryError("production replay ledger is malformed")
    return mission_ids


def _record_replay_ledger(path: Path, mission_id: str) -> None:
    mission_ids = _read_replay_ledger(path)
    if mission_id in mission_ids:
        raise FoundryError(f"replayed mission identity: {mission_id}")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    try:
        temporary.write_text(json.dumps({"format_version": "1.0", "mission_ids": [*mission_ids, mission_id]}, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8", newline="\n")
        temporary.replace(path)
    except OSError as exc:
        raise FoundryError("production replay ledger could not be recorded") from exc


def _result(value: object, as_json: bool) -> None:
    if as_json:
        print(json.dumps(value, indent=2, sort_keys=True))
    elif isinstance(value, dict):
        for key, item in value.items():
            print(f"{key}: {item}")
    else:
        print(value)


def main() -> int:
    parser = argparse.ArgumentParser(description="Compile or verify deterministic Oathbringer Foundry carriers.")
    sub = parser.add_subparsers(dest="command", required=True)
    compile_parser = sub.add_parser("compile")
    compile_parser.add_argument("--input-root", required=True, type=Path)
    compile_parser.add_argument("--source-root", required=True, type=Path)
    compile_parser.add_argument("--output-dir", required=True, type=Path)
    compile_parser.add_argument("--json", action="store_true")
    verify_parser = sub.add_parser("verify")
    verify_parser.add_argument("--carrier", required=True, type=Path)
    verify_parser.add_argument("--json", action="store_true")
    snapshot_parser = sub.add_parser("snapshot")
    snapshot_parser.add_argument("--input-root", required=True, type=Path)
    snapshot_parser.add_argument("--source-root", required=True, type=Path)
    snapshot_parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        if args.command == "verify":
            _result(verify_carrier(args.carrier), args.json)
            return 0
        mission = load_json(args.input_root / "foundry-mission.json")
        if args.command == "snapshot":
            _result(read_live_state(mission), args.json)
            return 0
        # Production compilation always obtains a new read-only GitHub snapshot.
        # The injectable library argument exists solely to make the compiler's
        # deterministic rejection rules independently unit-testable.
        live = read_live_state(mission)
        ledger = args.output_dir / REPLAY_LEDGER_NAME
        seen_mission_ids = _read_replay_ledger(ledger)
        result = compile_carrier(
            mission,
            input_root=args.input_root,
            source_root=args.source_root,
            output_dir=args.output_dir,
            live_state=live,
            seen_mission_ids=seen_mission_ids,
        )
        _record_replay_ledger(ledger, str(mission["mission_id"]))
        _result(
            {
                "carrier_path": str(result.carrier_path),
                "carrier_sha256": result.carrier_sha256,
                "manifest_sha256": result.manifest_sha256,
                "forge_receipt_sha256": result.forge_receipt_sha256,
                "member_count": result.member_count,
                "bound_live_state_sha256": result.bound_live_state_sha256,
                "compiler_is_writer": False,
            },
            args.json,
        )
        return 0
    except Exception as exc:
        if getattr(args, "json", False):
            _result(
                {
                    "error_code": "FOUNDRY_REJECTED",
                    "result": "REJECTED",
                },
                True,
            )
        else:
            detail = str(exc) if isinstance(exc, FoundryError) else "carrier input could not be safely processed"
            print(f"Foundry rejected: {detail}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
