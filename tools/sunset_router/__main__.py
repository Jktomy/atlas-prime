from __future__ import annotations

import argparse
import json
from pathlib import Path

from tools.atlas_lifecycle.errors import LifecycleError

from .core import (
    generate_router_approval,
    generate_router_candidate,
    generate_router_preview,
    verify_router_candidate,
    verify_router_preview,
    build_publication_receipt,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m tools.sunset_router")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    commands = parser.add_subparsers(dest="command", required=True)

    preview = commands.add_parser("preview")
    preview.add_argument("--request", type=Path, required=True)
    preview.add_argument("--output-dir", type=Path, required=True)

    approve = commands.add_parser("approve")
    approve.add_argument("--router-dir", type=Path, required=True)
    approve.add_argument(
        "--approval-mode",
        required=True,
        choices=("STANDARD", "GODDESS_MODE", "GODDESS_MODE_SHARDBLADE"),
    )
    approve.add_argument("--output-dir", type=Path, required=True)

    candidate = commands.add_parser("candidate")
    candidate.add_argument("--router-dir", type=Path, required=True)
    candidate.add_argument("--approval-dir", type=Path, required=True)
    candidate.add_argument("--output-dir", type=Path, required=True)

    verify = commands.add_parser("verify")
    verify.add_argument("--router-dir", type=Path, required=True)
    verify.add_argument("--approval-dir", type=Path)
    verify.add_argument("--candidate-dir", type=Path)

    receipt = commands.add_parser("receipt")
    receipt.add_argument("--candidate-dir", type=Path, required=True)
    receipt.add_argument("--router-dir", type=Path, required=True)
    receipt.add_argument("--approval-dir", type=Path, required=True)
    receipt.add_argument(
        "--state",
        required=True,
        choices=(
            "APPROVED_PENDING_VALIDATION",
            "APPROVED_PENDING_PERMANENCE",
            "READBACK_COMPLETE",
        ),
    )
    receipt.add_argument("--expected-head", required=True)
    receipt.add_argument("--pull-request", type=int, required=True)
    receipt.add_argument("--merged-commit")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        if args.command == "preview":
            result = generate_router_preview(args.repo_root, args.request, args.output_dir)
        elif args.command == "approve":
            result = generate_router_approval(
                args.repo_root,
                args.router_dir,
                args.output_dir,
                approval_mode=args.approval_mode,
            )
        elif args.command == "candidate":
            result = generate_router_candidate(
                args.repo_root,
                args.router_dir,
                args.approval_dir,
                args.output_dir,
            )
        elif args.command == "verify":
            if args.candidate_dir is not None:
                if args.approval_dir is None:
                    raise LifecycleError(
                        "SUNSET_ROUTER_VERIFY_INPUT",
                        "candidate verification requires approval-dir",
                    )
                verified = verify_router_candidate(
                    args.repo_root, args.router_dir, args.approval_dir, args.candidate_dir
                )
            else:
                verified = verify_router_preview(
                    args.repo_root, args.router_dir, require_current_head=False
                )
            result = {
                "authority": "READ_ONLY",
                "command": "sunset-router verify",
                "plan_id": verified["plan"]["plan_id"],
                "state": verified["receipt"]["state"],
                "status": "PASS",
            }
        else:
            verified = verify_router_candidate(
                args.repo_root, args.router_dir, args.approval_dir, args.candidate_dir
            )
            result = build_publication_receipt(
                args.repo_root,
                verified["plan"],
                state=args.state,
                expected_head=args.expected_head,
                pull_request=args.pull_request,
                merged_commit=args.merged_commit,
            )
        print(json.dumps(result, sort_keys=True, separators=(",", ":")))
        return 0
    except LifecycleError as exc:
        print(
            json.dumps(
                {
                    "authority": "READ_ONLY",
                    "state": "BLOCKED_RESUMABLE",
                    "status": "FAIL",
                    **exc.sanitized(),
                },
                sort_keys=True,
                separators=(",", ":"),
            )
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
