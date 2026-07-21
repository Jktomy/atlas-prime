from __future__ import annotations

import argparse
import json
from pathlib import Path

from .core import PublicationError, build_plan


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a read-only Atlas Mission publication plan")
    parser.add_argument("mission", type=Path)
    parser.add_argument("--canonical-base", required=True)
    parser.add_argument("--changed-path", action="append", default=[])
    parser.add_argument("--sealed-path", action="append", default=[])
    args = parser.parse_args()
    try:
        mission = json.loads(args.mission.read_text(encoding="utf-8"))
        plan = build_plan(mission, args.canonical_base, args.changed_path, args.sealed_path)
    except (OSError, json.JSONDecodeError, PublicationError) as exc:
        print(json.dumps({"status":"BLOCKED_RESUMABLE","error":str(exc)}, sort_keys=True))
        return 2
    print(json.dumps(plan, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
