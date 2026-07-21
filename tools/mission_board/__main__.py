from __future__ import annotations

import argparse
import json
from pathlib import Path

from .core import MissionError, parse_json_document, resume_plan, sequence_missions, validate_mission


def _load(path: Path) -> dict[str, object]:
    return parse_json_document(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Read-only Atlas Mission Board validation and resume planner.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate")
    validate_parser.add_argument("mission", type=Path)

    resume_parser = subparsers.add_parser("resume")
    resume_parser.add_argument("mission", type=Path)
    resume_parser.add_argument("--canonical-head", required=True)
    resume_parser.add_argument("--pr-snapshot", type=Path)

    sequence_parser = subparsers.add_parser("sequence")
    sequence_parser.add_argument("--mission", action="append", required=True, help="NUMBER=PATH")
    sequence_parser.add_argument("numbers", nargs="+", type=int)

    args = parser.parse_args()
    try:
        if args.command == "validate":
            mission = validate_mission(_load(args.mission))
            result = {"result": "PASS", "mission_id": mission["mission_id"], "issue_number": mission["issue_number"]}
        elif args.command == "resume":
            pr_snapshot = _load(args.pr_snapshot) if args.pr_snapshot else None
            result = resume_plan(_load(args.mission), args.canonical_head, pr_snapshot=pr_snapshot)
        else:
            missions: dict[int, dict[str, object]] = {}
            for binding in args.mission:
                number, separator, raw_path = binding.partition("=")
                if not separator:
                    raise MissionError(f"INVALID_BINDING: {binding}")
                missions[int(number)] = _load(Path(raw_path))
            result = sequence_missions(missions, args.numbers)
    except (MissionError, OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"result": "BLOCKED", "error": str(exc)}, indent=2, sort_keys=True))
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
