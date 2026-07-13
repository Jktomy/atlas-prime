from __future__ import annotations

import argparse
import sys
from pathlib import Path

THREAD_ENGINE_ROOT = Path(__file__).resolve().parents[1] / "thread-engine"
if str(THREAD_ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(THREAD_ENGINE_ROOT))

from production_adapter.receipt import stable_json

from .core import PreparationError, build_hash_register, load_github_event_inputs, prepare_package, reconcile_registers


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Read-only generated checkpoint package preparer")
    sub = parser.add_subparsers(dest="command", required=True)
    build = sub.add_parser("build-register")
    build.add_argument("--repo-root", type=Path, required=True)
    build.add_argument("--output", type=Path, required=True)
    build.add_argument("--mission-id")
    build.add_argument("--base-sha")
    build.add_argument("--replay-nonce")
    build.add_argument("--github-event", type=Path)
    build.add_argument("--workflow-ref", required=True)
    build.add_argument("--workflow-source-sha", required=True)
    build.add_argument("--workflow-run-id", required=True)
    build.add_argument("--workflow-run-attempt", required=True)
    reconcile = sub.add_parser("reconcile")
    reconcile.add_argument("--ubuntu-register", type=Path, required=True)
    reconcile.add_argument("--windows-register", type=Path, required=True)
    reconcile.add_argument("--output", type=Path, required=True)
    prepare = sub.add_parser("prepare")
    prepare.add_argument("--repo-root", type=Path, required=True)
    prepare.add_argument("--register", type=Path, required=True)
    prepare.add_argument("--reconciliation", type=Path, required=True)
    prepare.add_argument("--package-root", type=Path, required=True)
    prepare.add_argument("--replay-nonce")
    prepare.add_argument("--public-clean-confirmation")
    prepare.add_argument("--github-event", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "build-register":
            event_inputs = load_github_event_inputs(args.github_event) if args.github_event else {}
            mission_id = event_inputs.get("mission_id", args.mission_id)
            base_sha = event_inputs.get("base_sha", args.base_sha)
            replay_nonce = event_inputs.get("replay_nonce", args.replay_nonce)
            if not all(isinstance(value, str) and value for value in (mission_id, base_sha, replay_nonce)):
                raise PreparationError("register identity inputs are incomplete", "GENERATED_CHECKPOINT_EVENT")
            register, _ = build_hash_register(
                args.repo_root,
                mission_id=mission_id,
                base_sha=base_sha,
                replay_nonce=replay_nonce,
                workflow_ref=args.workflow_ref,
                workflow_source_sha=args.workflow_source_sha,
                workflow_run_id=args.workflow_run_id,
                workflow_run_attempt=args.workflow_run_attempt,
            )
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(stable_json(register), encoding="utf-8", newline="\n")
        elif args.command == "reconcile":
            result = reconcile_registers(args.ubuntu_register, args.windows_register)
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(stable_json(result), encoding="utf-8", newline="\n")
        else:
            event_inputs = load_github_event_inputs(args.github_event) if args.github_event else {}
            replay_nonce = event_inputs.get("replay_nonce", args.replay_nonce)
            public_clean = event_inputs.get("public_clean_confirmation", args.public_clean_confirmation)
            if not isinstance(replay_nonce, str) or not isinstance(public_clean, str):
                raise PreparationError("package event inputs are incomplete", "GENERATED_CHECKPOINT_EVENT")
            mission = prepare_package(
                args.repo_root,
                args.register,
                args.reconciliation,
                args.package_root,
                replay_nonce=replay_nonce,
                public_clean_confirmation=public_clean,
            )
            sys.stdout.write(stable_json({
                "result": "PACKAGE_PREPARED",
                "mission_id": mission["mission_id"],
                "mission_sha256": mission["mission_sha256"],
                "branch": mission["branch"],
            }))
        return 0
    except (PreparationError, OSError, ValueError, KeyError) as exc:
        sys.stderr.write(stable_json({
            "result": "REJECTED",
            "error_code": getattr(exc, "code", "GENERATED_CHECKPOINT_PREPARATION_REJECTED"),
            "message": str(exc),
        }))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
