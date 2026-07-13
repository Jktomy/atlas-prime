from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .engine import (
    ROOT,
    argus,
    plan_one_entry_update,
    render_emberline,
    stable_json,
    sunrise,
    sunset,
    validate_identity_register,
    validate_register,
)


REGISTER = ROOT / "continuity" / "prime-continuity-register-r01.json"
BOARD = ROOT / "quest-board" / "quest-board-v1.json"
IDENTITIES = ROOT / "continuity" / "quest-engine-identities-r01.json"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def emit(value: Any, output: str | None) -> None:
    payload = stable_json(value)
    if output:
        path = Path(output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)
    else:
        print(payload.decode("utf-8"), end="")


def parser() -> argparse.ArgumentParser:
    command = argparse.ArgumentParser(description="Prime continuity read-only command surface")
    subcommands = command.add_subparsers(dest="command", required=True)
    subcommands.add_parser("validate")
    for name in ("emberline", "argus"):
        item = subcommands.add_parser(name)
        item.add_argument("--output")
    sunset_parser = subcommands.add_parser("sunset")
    sunset_parser.add_argument("--continuity-id", required=True)
    sunset_parser.add_argument("--output")
    sunrise_parser = subcommands.add_parser("sunrise")
    sunrise_parser.add_argument("--snapshot", required=True)
    sunrise_parser.add_argument("--output")
    plan = subcommands.add_parser("plan-update")
    plan.add_argument("--continuity-id", required=True)
    plan.add_argument("--expected-register-sha256", required=True)
    plan.add_argument("--expected-entry-revision", required=True, type=int)
    plan.add_argument("--event-id", required=True)
    plan.add_argument("--changes-json", required=True)
    plan.add_argument("--output")
    return command


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    register = load(REGISTER)
    board = load(BOARD)
    identities = load(IDENTITIES)
    validate_identity_register(identities)
    validate_register(register, board)
    if args.command == "validate":
        emit({"result": "PASS", "register_id": register["register_id"], "register_revision": register["register_revision"]}, None)
    elif args.command == "emberline":
        emit(render_emberline(register), args.output)
    elif args.command == "argus":
        emit(argus(register), args.output)
    elif args.command == "sunset":
        emit(sunset(register, args.continuity_id), args.output)
    elif args.command == "sunrise":
        emit(sunrise(load(Path(args.snapshot)), register), args.output)
    elif args.command == "plan-update":
        changes = json.loads(args.changes_json)
        if not isinstance(changes, dict):
            raise SystemExit("changes-json must be a JSON object")
        emit(
            plan_one_entry_update(
                register,
                board,
                identities,
                continuity_id=args.continuity_id,
                expected_register_sha256=args.expected_register_sha256,
                expected_entry_revision=args.expected_entry_revision,
                event_id=args.event_id,
                changes=changes,
            ),
            args.output,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
