from __future__ import annotations

import argparse
import json
from pathlib import Path

from foundry import FoundryError, compile_carrier, load_json, read_live_state, verify_carrier


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
    compile_parser.add_argument("--live-state", type=Path)
    compile_parser.add_argument("--bind-live", action="store_true")
    compile_parser.add_argument("--seen-mission-id", action="append", default=[])
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
        if bool(args.live_state) == bool(args.bind_live):
            raise FoundryError("compile requires exactly one of --live-state or --bind-live")
        live = read_live_state(mission) if args.bind_live else load_json(args.live_state)
        result = compile_carrier(
            mission,
            input_root=args.input_root,
            source_root=args.source_root,
            output_dir=args.output_dir,
            live_state=live,
            seen_mission_ids=args.seen_mission_id,
        )
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
    except FoundryError as exc:
        print(f"Foundry rejected: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
