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
    render_mission_quest_emberline,
    stable_json,
    sunrise,
    sunset,
    validate_board,
    validate_identity_register,
    validate_quest_registry,
    validate_register,
)


REGISTER = ROOT / "continuity" / "prime-continuity-register-r01.json"
REGISTRY = ROOT / "continuity" / "mission-board-quest-registry-r01.json"
FROZEN_BOARD = ROOT / "quest-board" / "quest-board-v1.json"
IDENTITIES = ROOT / "continuity" / "quest-engine-identities-r01.json"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def emit(value: Any, output: str | None) -> None:
    payload = stable_json(value)
    if output:
        path = Path(output).resolve()
        if path.is_relative_to(ROOT.resolve()):
            raise ValueError("OUTPUT_INSIDE_CANONICAL_REPOSITORY")
        if path.exists() or path.is_symlink():
            raise ValueError("OUTPUT_ALREADY_EXISTS")
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("xb") as handle:
            handle.write(payload)
    else:
        print(payload.decode("utf-8"), end="")


def parser() -> argparse.ArgumentParser:
    command = argparse.ArgumentParser(
        description="Prime continuity read-only snapshots; not the full Atlas Sunset"
    )
    subcommands = command.add_subparsers(dest="command", required=True)
    subcommands.add_parser("validate")
    for name in ("emberline", "argus"):
        item = subcommands.add_parser(name)
        item.add_argument("--output")
    mission_quest = subcommands.add_parser(
        "mission-quest-emberline",
        help="render one human-readable Mission Quest Emberline projection",
    )
    mission_quest.add_argument("--quest-id", required=True)
    mission_quest.add_argument("--output")
    sunset_parser = subcommands.add_parser(
        "sunset", help="render a continuity snapshot, not the full Atlas Sunset"
    )
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
    registry = load(REGISTRY)
    frozen_board = load(FROZEN_BOARD)
    identities = load(IDENTITIES)
    validate_board(frozen_board)
    validate_quest_registry(registry, frozen_board)
    validate_identity_register(identities)
    validate_register(register, frozen_board, registry=registry)
    if args.command == "validate":
        emit(
            {
                "result": "PASS",
                "registry_id": registry["registry_id"],
                "registry_revision": registry["registry_revision"],
                "register_id": register["register_id"],
                "register_revision": register["register_revision"],
                "frozen_predecessor": frozen_board["registry_role"],
            },
            None,
        )
    elif args.command == "emberline":
        emit(render_emberline(register), args.output)
    elif args.command == "argus":
        emit(argus(register), args.output)
    elif args.command == "mission-quest-emberline":
        emit(render_mission_quest_emberline(register, registry, args.quest_id), args.output)
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
                frozen_board,
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
