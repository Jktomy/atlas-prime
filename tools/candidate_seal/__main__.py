from __future__ import annotations

import argparse
import json
from pathlib import Path

from .core import (
    CandidateSealError,
    build_candidate_seal,
    build_repair_batch,
    reconcile_publication_state,
    verify_candidate_seal,
)


def _json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def _candidate_files(root: Path, paths: list[str]) -> dict[str, bytes]:
    return {path: root.joinpath(*path.split("/")).read_bytes() for path in paths}


def _checks(values: list[str]) -> dict[str, str]:
    checks: dict[str, str] = {}
    for value in values:
        name, separator, digest = value.partition("=")
        if not separator or name in checks:
            raise CandidateSealError("INVALID_CHECK_EVIDENCE", value)
        checks[name] = digest
    return checks


def _common_candidate(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--candidate-root", type=Path, required=True)
    parser.add_argument("--path", action="append", default=[], required=True)
    parser.add_argument("--canonical-base", required=True)
    parser.add_argument("--branch", required=True)
    parser.add_argument("--expected-tree", required=True)
    parser.add_argument("--expected-head")
    parser.add_argument("--check", action="append", default=[], required=True, metavar="NAME=SHA256")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build and verify read-only Prime candidate seals")
    subparsers = parser.add_subparsers(dest="command", required=True)

    create = subparsers.add_parser("create")
    create.add_argument("mission", type=Path)
    _common_candidate(create)
    create.add_argument("--authorizer", required=True)
    create.add_argument("--operator", required=True)
    create.add_argument("--route", required=True)
    create.add_argument("--generated-state", required=True)

    verify = subparsers.add_parser("verify")
    verify.add_argument("seal", type=Path)
    _common_candidate(verify)
    verify.add_argument("--consumed-seal-id", action="append", default=[])

    reconcile = subparsers.add_parser("reconcile")
    reconcile.add_argument("seal", type=Path)
    reconcile.add_argument("remote_state", type=Path)

    repair = subparsers.add_parser("repair-batch")
    repair.add_argument("seal", type=Path)
    repair.add_argument("findings", type=Path)

    args = parser.parse_args()
    try:
        if args.command == "create":
            mission = _json(args.mission)
            result = build_candidate_seal(
                mission,
                canonical_base_sha=args.canonical_base,
                branch_intent=args.branch,
                candidate_files=_candidate_files(args.candidate_root, args.path),
                expected_candidate_tree_sha=args.expected_tree,
                expected_head_sha=args.expected_head,
                prepublication_checks=_checks(args.check),
                authorizer=args.authorizer,
                operator=args.operator,
                route=args.route,
                generated_state=args.generated_state,
            )
        elif args.command == "verify":
            result = verify_candidate_seal(
                _json(args.seal),
                canonical_base_sha=args.canonical_base,
                branch_intent=args.branch,
                candidate_files=_candidate_files(args.candidate_root, args.path),
                expected_candidate_tree_sha=args.expected_tree,
                expected_head_sha=args.expected_head,
                prepublication_checks=_checks(args.check),
                consumed_seal_ids=args.consumed_seal_id,
            )
        elif args.command == "reconcile":
            result = reconcile_publication_state(_json(args.seal), _json(args.remote_state))
        else:
            result = build_repair_batch(_json(args.seal), _json(args.findings))
    except (OSError, json.JSONDecodeError, CandidateSealError) as exc:
        code = exc.code if isinstance(exc, CandidateSealError) else "INPUT_ERROR"
        print(json.dumps({"status": "BLOCKED_RESUMABLE", "error_code": code, "error": str(exc)}, sort_keys=True))
        return 2
    print(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
