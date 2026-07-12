from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from .hosted import HostedRouteError, preflight_hosted, run_hosted, stable_json


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Prime owner-only hosted Arrow/Bow intake")
    parser.add_argument("--receipt-dir", required=True, type=Path)
    parser.add_argument("--work-root", required=True, type=Path)
    parser.add_argument("--preflight-only", action="store_true")
    args = parser.parse_args(argv)
    encoded = os.environ.get("ATHENA_ARROW_B64", "")
    receipt_path = args.receipt_dir.resolve() / "athena-hosted-route-receipt.json"
    try:
        if args.preflight_only:
            receipt = preflight_hosted(
                encoded,
                env=dict(os.environ),
                evidence_dir=args.receipt_dir.resolve(),
                work_root=args.work_root.resolve(),
            )
        else:
            receipt = run_hosted(
                encoded,
                env=dict(os.environ),
                receipt_path=receipt_path,
                work_root=args.work_root.resolve(),
            )
    except HostedRouteError as exc:
        sys.stderr.write(f"Hosted Arrow/Bow stopped safely: {exc.code}\n")
        return 2
    sys.stdout.write(stable_json({
        "result": receipt["result"],
        "route": receipt["route"],
        "stage": receipt.get("stage", "READ_ONLY_PREFLIGHT"),
        "stop_point": receipt["stop_point"],
        "error_code": receipt.get("error_code"),
    }))
    return 0 if receipt["result"] in {"SUCCESS", "ACCEPTED"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
