from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .adapter import AdapterError, execute_mission
from .receipt import stable_json


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Atlas mission-scoped Thread Engine production adapter")
    parser.add_argument("--mission", required=True)
    parser.add_argument("--mission-sha256")
    parser.add_argument("--mission-scoped-draft-pr", action="store_true")
    parser.add_argument("--execute-draft-pr", action="store_true")
    parser.add_argument("--aegis-break-protected-route", action="store_true")
    parser.add_argument("--aegis-break-authority-id")
    parser.add_argument("--generated-checkpoint-route", action="store_true")
    parser.add_argument("--work-root")
    args = parser.parse_args(argv)
    try:
        receipt = execute_mission(
            Path(args.mission),
            mission_scoped=args.mission_scoped_draft_pr,
            execute_draft_pr=args.execute_draft_pr,
            mission_sha256=args.mission_sha256,
            aegis_break_protected_route=args.aegis_break_protected_route,
            aegis_break_authority_id=args.aegis_break_authority_id,
            generated_checkpoint_route=args.generated_checkpoint_route,
            work_root=Path(args.work_root) if args.work_root else None,
        )
        sys.stdout.write(stable_json(receipt))
        return 0
    except AdapterError as exc:
        if exc.receipt:
            sys.stderr.write(stable_json(exc.receipt))
        else:
            sys.stderr.write(str(exc) + "\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
