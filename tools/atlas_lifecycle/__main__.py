from __future__ import annotations

import argparse
import json
from pathlib import Path

from . import __version__
from .candidate import generate_event_candidate
from .errors import LifecycleError
from .evidence import verify_bound_evidence
from .pilot import run_context_pilot
from .planner import plan_event
from .projection import INDEX_RELATIVE_PATH, check_website_index, compact_context
from .repository import validate_repository
from .sunset import generate_sunset_candidate, verify_sunset_candidate


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m tools.atlas_lifecycle")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    subcommands = parser.add_subparsers(dest="command", required=True)
    subcommands.add_parser("validate", help="validate schemas, records, IDs, and protected boundaries")
    verify = subcommands.add_parser(
        "verify", help="validate plus exact-HEAD stale-state and optional evidence verification"
    )
    verify.add_argument("--archive", type=Path)
    verify.add_argument("--sidecar", type=Path)
    verify.add_argument("--receipt", type=Path)
    verify.add_argument("--trust-root", type=Path)
    context = subcommands.add_parser("context", help="return one compact deterministic Quest context")
    context.add_argument("--quest-id")
    index = subcommands.add_parser("index", help="website-facing lifecycle projection checks")
    index_commands = index.add_subparsers(dest="index_command", required=True)
    index_commands.add_parser("build", help="compute and compare the index without writing")
    pilot = subcommands.add_parser("pilot", help="measure manual versus compact context reconstruction")
    pilot.add_argument("--repetitions", type=int, default=500)
    event = subcommands.add_parser("event", help="lifecycle event plan and candidate mechanics")
    event_commands = event.add_subparsers(dest="event_command", required=True)
    event_plan = event_commands.add_parser("plan", help="validate and propose deterministic deltas")
    event_plan.add_argument("--event", type=Path, required=True)
    event_plan.add_argument("--trust-root", type=Path, required=True)
    event_plan.add_argument("--expected-trust-root-digest", required=True)
    event_plan.add_argument("--state", type=Path, required=True)
    event_plan.add_argument("--expected-state-digest", required=True)
    event_candidate = event_commands.add_parser(
        "candidate", help="generate exact lifecycle event candidate bytes in temporary output"
    )
    event_candidate.add_argument("--event", type=Path, required=True)
    event_candidate.add_argument("--trust-root", type=Path, required=True)
    event_candidate.add_argument("--expected-trust-root-digest", required=True)
    event_candidate.add_argument("--state", type=Path, required=True)
    event_candidate.add_argument("--expected-state-digest", required=True)
    event_candidate.add_argument("--output-dir", type=Path, required=True)
    sunset = subcommands.add_parser("sunset", help="build or verify one bounded Sunset candidate set")
    sunset_commands = sunset.add_subparsers(dest="sunset_command", required=True)
    sunset_candidate = sunset_commands.add_parser(
        "candidate", help="create exactly one Feather/Sunset/Sunrise candidate set"
    )
    sunset_candidate.add_argument("--request", type=Path, required=True)
    sunset_candidate.add_argument("--output-dir", type=Path, required=True)
    sunset_verify = sunset_commands.add_parser(
        "verify", help="verify one temporary Sunset candidate set"
    )
    sunset_verify.add_argument("--candidate-dir", type=Path, required=True)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        if args.command == "pilot":
            print(
                json.dumps(
                    run_context_pilot(args.repo_root, repetitions=args.repetitions),
                    sort_keys=True,
                    separators=(",", ":"),
                )
            )
            return 0

        if args.command == "sunset":
            if args.sunset_command == "candidate":
                output = generate_sunset_candidate(
                    args.repo_root,
                    args.request,
                    args.output_dir,
                )
            else:
                output = verify_sunset_candidate(
                    args.repo_root,
                    args.candidate_dir,
                )
            print(json.dumps(output, sort_keys=True, separators=(",", ":")))
            return 0

        if args.command == "event":
            if args.event_command == "candidate":
                output = generate_event_candidate(
                    args.repo_root,
                    args.event,
                    args.trust_root,
                    args.expected_trust_root_digest,
                    args.state,
                    args.expected_state_digest,
                    args.output_dir,
                )
            else:
                output = plan_event(
                    args.repo_root,
                    args.event,
                    args.trust_root,
                    args.expected_trust_root_digest,
                    args.state,
                    args.expected_state_digest,
                )
            print(
                json.dumps(
                    output,
                    sort_keys=True,
                    separators=(",", ":"),
                )
            )
            return 0

        if args.command in {"context", "index"}:
            check, snapshot = check_website_index(args.repo_root)
            if args.command == "context":
                output = compact_context(
                    snapshot,
                    quest_id=args.quest_id,
                    projection_warning=check.warning,
                )
            else:
                output = {
                    "authority": "GENERATED_NONCANONICAL_PROJECTION",
                    "command": "index build",
                    "expected_digest": check.expected_digest,
                    "index_path": INDEX_RELATIVE_PATH.as_posix(),
                    "index_status": check.status,
                    "mode": "CHECK_ONLY",
                    "source_fingerprint": check.source_fingerprint,
                    "source_revision": check.source_revision,
                }
            print(json.dumps(output, sort_keys=True, separators=(",", ":")))
            return 0

        result = validate_repository(
            args.repo_root,
            check_stale=args.command == "verify",
        )
        evidence_digest = None
        if args.command == "verify":
            evidence_args = (args.archive, args.sidecar, args.receipt, args.trust_root)
            if any(value is not None for value in evidence_args):
                if any(value is None for value in evidence_args):
                    raise LifecycleError(
                        "INCOMPLETE_EVIDENCE_INPUT",
                        "archive, sidecar, receipt, and trust root are all required",
                    )
                if args.trust_root.is_absolute() or ".." in args.trust_root.parts:
                    raise LifecycleError("TRUST_ROOT_PATH", "trust-root name must be a safe relative path")
                evidence_digest = verify_bound_evidence(
                    args.archive,
                    args.sidecar,
                    args.receipt,
                    args.repo_root / "lifecycle" / "schemas",
                    args.repo_root / "lifecycle" / "lifecycle-contract.md",
                    args.repo_root / "lifecycle" / "trust-roots" / args.trust_root,
                    args.repo_root / "lifecycle" / "trust-roots",
                )
        output = {
            "authority": "READ_ONLY",
            "command": args.command,
            "engine_class": "SCRIPT_ASSIST_LEVEL_1A",
            "engine_version": __version__,
            "fixtures": result.fixtures,
            "records": result.records,
            "trust_roots": result.trust_roots,
            "source_fingerprint": result.source_fingerprint,
            "status": "PASS",
        }
        if evidence_digest is not None:
            output["verified_evidence_digest"] = evidence_digest
        print(
            json.dumps(
                output,
                sort_keys=True,
                separators=(",", ":"),
            )
        )
        return 0
    except LifecycleError as exc:
        candidate_failure = (
            getattr(args, "command", None) == "event"
            and getattr(args, "event_command", None) == "candidate"
        )
        failure = {
            "authority": "TEMPORARY_CANDIDATE_ONLY" if candidate_failure else "READ_ONLY",
            "status": "FAIL",
            **exc.sanitized(),
        }
        if candidate_failure:
            failure.update({
                "canonical_writes": False,
                "github_actions": [],
                "temporary_output_state": "ABSENT_OR_PARTIAL_REVIEW_REQUIRED",
            })
        print(
            json.dumps(
                failure,
                sort_keys=True,
                separators=(",", ":"),
            )
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
