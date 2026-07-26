from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .adapter import AdapterError, execute_mission
from .receipt import stable_json
from .resume import execute_sealed_mission, reconcile_adapter_error, resume_exact_partial


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
    parser.add_argument("--package-root")
    parser.add_argument("--candidate-seal")
    parser.add_argument("--candidate-seal-context")
    parser.add_argument("--resume-partial-receipt")
    args = parser.parse_args(argv)
    try:
        if args.resume_partial_receipt:
            if not args.candidate_seal:
                raise AdapterError("resume requires candidate seal", "CANDIDATE_SEAL_REQUIRED", "PACKAGE_AUDIT")
            receipt = resume_exact_partial(
                Path(args.mission),
                partial_receipt_path=Path(args.resume_partial_receipt),
                seal_path=Path(args.candidate_seal),
            )
        elif args.candidate_seal or args.candidate_seal_context:
            if not args.candidate_seal or not args.candidate_seal_context or not args.package_root:
                raise AdapterError("sealed execution requires seal, context, and package root", "CANDIDATE_SEAL_REQUIRED", "PACKAGE_AUDIT")
            receipt = execute_sealed_mission(
                Path(args.mission),
                package_root=Path(args.package_root),
                seal_path=Path(args.candidate_seal),
                context_path=Path(args.candidate_seal_context),
                mission_sha256=args.mission_sha256,
                work_root=Path(args.work_root) if args.work_root else None,
            )
        else:
            receipt = execute_mission(
                Path(args.mission),
                mission_scoped=args.mission_scoped_draft_pr,
                execute_draft_pr=args.execute_draft_pr,
                mission_sha256=args.mission_sha256,
                aegis_break_protected_route=args.aegis_break_protected_route,
                aegis_break_authority_id=args.aegis_break_authority_id,
                generated_checkpoint_route=args.generated_checkpoint_route,
                work_root=Path(args.work_root) if args.work_root else None,
                package_root=Path(args.package_root) if args.package_root else None,
            )
        sys.stdout.write(stable_json(receipt))
        return 0
    except AdapterError as exc:
        mission_path = Path(args.mission)
        package_root = Path(args.package_root) if args.package_root else mission_path.resolve().parent
        reconciled = reconcile_adapter_error(mission_path, package_root=package_root, error=exc)
        if reconciled:
            sys.stderr.write(stable_json(reconciled))
        elif exc.receipt:
            sys.stderr.write(stable_json(exc.receipt))
        else:
            sys.stderr.write(stable_json({
                "result": "REJECTED",
                "error_code": exc.code,
                "error_stage": exc.stage,
                "message": "Thread Engine adapter rejected before receipt initialization.",
            }))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
