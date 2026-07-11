from __future__ import annotations

import argparse
import json
from pathlib import Path

from . import __version__
from .errors import LifecycleError
from .evidence import verify_bound_evidence
from .repository import validate_repository


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
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
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
        print(
            json.dumps(
                {"authority": "READ_ONLY", "status": "FAIL", **exc.sanitized()},
                sort_keys=True,
                separators=(",", ":"),
            )
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
