from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

THREAD_ENGINE_ROOT = Path(__file__).resolve().parents[1] / "thread-engine"
if str(THREAD_ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(THREAD_ENGINE_ROOT))

from production_adapter.receipt import sha256_bytes, stable_json

from .core import PreparationError, prepare_package


ALLOWED_EVENT_NAMES = frozenset({"push", "workflow_dispatch"})


def bind_hosted_event(mission: dict[str, Any], event_name: str) -> dict[str, Any]:
    if event_name not in ALLOWED_EVENT_NAMES:
        raise PreparationError(
            "generated checkpoint hosted event is not allowlisted",
            "GENERATED_CHECKPOINT_EVENT",
        )
    profile = mission.get("generated_checkpoint_profile")
    if not isinstance(profile, dict):
        raise PreparationError(
            "generated checkpoint profile is unavailable",
            "GENERATED_CHECKPOINT_EVENT",
        )
    profile["event_name"] = event_name
    mission["mission_sha256"] = "0" * 64
    mission["mission_sha256"] = sha256_bytes(stable_json(mission).encode("utf-8"))
    return mission


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Prepare a generated checkpoint package and bind the trusted hosted event"
    )
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--register", type=Path, required=True)
    parser.add_argument("--reconciliation", type=Path, required=True)
    parser.add_argument("--package-root", type=Path, required=True)
    parser.add_argument("--replay-nonce", required=True)
    parser.add_argument("--public-clean-confirmation", required=True)
    parser.add_argument("--event-name", required=True)
    args = parser.parse_args(argv)

    try:
        mission = prepare_package(
            args.repo_root,
            args.register,
            args.reconciliation,
            args.package_root,
            replay_nonce=args.replay_nonce,
            public_clean_confirmation=args.public_clean_confirmation,
        )
        mission = bind_hosted_event(mission, args.event_name)
        mission_path = args.package_root.resolve() / "mission.json"
        mission_path.write_text(stable_json(mission), encoding="utf-8", newline="\n")
        sys.stdout.write(
            stable_json(
                {
                    "result": "PACKAGE_PREPARED",
                    "mission_id": mission["mission_id"],
                    "mission_sha256": mission["mission_sha256"],
                    "branch": mission["branch"],
                    "event_name": mission["generated_checkpoint_profile"]["event_name"],
                }
            )
        )
        return 0
    except (PreparationError, OSError, ValueError, KeyError) as exc:
        sys.stderr.write(
            stable_json(
                {
                    "result": "REJECTED",
                    "error_code": getattr(
                        exc,
                        "code",
                        "GENERATED_CHECKPOINT_PREPARATION_REJECTED",
                    ),
                    "message": str(exc),
                }
            )
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
