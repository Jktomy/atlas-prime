from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from .hosted import HostedRouteError, preflight_hosted, run_hosted, stable_json


def event_environment(environment: dict[str, str]) -> tuple[dict[str, str], str]:
    event_path = environment.get("GITHUB_EVENT_PATH")
    if not event_path:
        raise HostedRouteError("trusted event path is missing", "TRUSTED_ENVIRONMENT_MISSING")
    try:
        event = json.loads(Path(event_path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise HostedRouteError("trusted event payload is unavailable", "TRUSTED_EVENT_REJECTED") from exc
    inputs = event.get("inputs") if isinstance(event, dict) else None
    if not isinstance(inputs, dict):
        raise HostedRouteError("trusted workflow inputs are unavailable", "TRUSTED_EVENT_REJECTED")
    mapping = {
        "arrow_b64": "ATHENA_ARROW_B64",
        "arrow_sha256": "ATHENA_ARROW_SHA256",
        "mission_lock_sha256": "ATHENA_MISSION_LOCK_SHA256",
        "public_clean_confirmation": "ATHENA_PUBLIC_CLEAN_CONFIRMATION",
    }
    values = dict(environment)
    for event_key, environment_key in mapping.items():
        value = inputs.get(event_key)
        if not isinstance(value, str) or not value:
            raise HostedRouteError("trusted workflow input is missing", "TRUSTED_EVENT_REJECTED")
        values[environment_key] = value
    return values, values.pop("ATHENA_ARROW_B64")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Prime owner-only hosted Arrow/Bow intake")
    parser.add_argument("--receipt-dir", required=True, type=Path)
    parser.add_argument("--work-root", required=True, type=Path)
    parser.add_argument("--preflight-only", action="store_true")
    args = parser.parse_args(argv)
    receipt_path = args.receipt_dir.resolve() / "athena-hosted-route-receipt.json"
    try:
        environment, encoded = event_environment(dict(os.environ))
        if args.preflight_only:
            receipt = preflight_hosted(
                encoded,
                env=environment,
                evidence_dir=args.receipt_dir.resolve(),
                work_root=args.work_root.resolve(),
            )
        else:
            receipt = run_hosted(
                encoded,
                env=environment,
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
