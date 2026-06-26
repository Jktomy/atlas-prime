from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

from .models import StateError
from .s1_contracts import load_s1_contracts
from .s1_git_adapter import LocalPlanningGitAdapter
from .s1_receipts import bounded_receipt, canonical_json_bytes, receipt_artifact_identity, safe_code, state_for_blocker
from .s1_writer import (
    RuntimeContext,
    build_plan,
    load_compile_context,
    parse_and_validate_envelope,
    validate_disabled_dual_activation,
    validate_runtime_context,
)
from .validate import load_json_file


def _write_receipt(output_root: Path, receipt: dict) -> Path:
    artifact, filename = receipt_artifact_identity(receipt["run_id"], receipt["run_attempt"])
    target = output_root / artifact / filename
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(canonical_json_bytes(receipt) + b"\n")
    return target


def _failure_receipt(context: RuntimeContext, code: str, gate: str, packet_id: str | None = None) -> dict:
    return bounded_receipt(
        transaction_state=state_for_blocker(code),
        last_completed_gate=gate,
        blocker_codes=[code],
        repository=context.repository,
        packet_id=packet_id,
        actor=context.actor,
        event=context.event,
        workflow_sha=context.workflow_sha,
        run_id=context.run_id,
        run_attempt=context.run_attempt,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Athena's Spear S1 disabled writer entrypoint")
    parser.add_argument("--packet-id", required=True)
    parser.add_argument("--envelope", required=True)
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--repository-path", default=".")
    parser.add_argument("--actor", required=True)
    parser.add_argument("--event", required=True)
    parser.add_argument("--repository", required=True)
    parser.add_argument("--workflow-sha", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--run-attempt", required=True)
    parser.add_argument("--observed-at", required=True, help="Injected authenticated workflow observation time in ISO-8601")
    parser.add_argument("--envelope-schema", default="schemas/spear/spear-execution-envelope-v1.schema.json")
    args = parser.parse_args(argv)
    context = RuntimeContext(args.actor, args.event, args.repository, args.workflow_sha, args.run_id, args.run_attempt)
    gate = "NONE"
    receipt: dict
    try:
        validate_runtime_context(context)
        gate = "CONTEXT_VALIDATED"
        envelope_bytes = Path(args.envelope).read_bytes()
        schema = load_json_file(args.envelope_schema)
        observed_at = datetime.fromisoformat(args.observed_at.replace("Z", "+00:00"))
        envelope = parse_and_validate_envelope(envelope_bytes, schema, now=observed_at)
        gate = "ENVELOPE_VALIDATED"
        base_commit = envelope["expected_base_commit"]
        contracts = load_s1_contracts(args.repository_path, base_commit, require_enabled=False)
        validate_disabled_dual_activation(contracts["activation"], contracts["controlling"]["destination"])
        compile_context = load_compile_context(
            args.repository_path,
            base_commit,
            additional_contract_identities=[contracts["activation_identity"]],
        )
        plan = build_plan(
            dispatch_packet_id=args.packet_id,
            envelope=envelope,
            branch_regex=contracts["controlling"]["future_branch_regex"],
            compile_context=compile_context,
            target_reader=LocalPlanningGitAdapter(args.repository_path, base_commit),
        )
        gate = "PLAN_VALIDATED"
        receipt = bounded_receipt(
            transaction_state="FAILED_WITH_RECEIPT",
            last_completed_gate=gate,
            blocker_codes=["S1_APPLY_DISABLED"],
            repository=context.repository,
            base_commit=plan.base_commit,
            packet_id=plan.packet["packet_id"],
            packet_transport_sha256=plan.packet_sha256,
            manifest_sha256=plan.manifest_sha256,
            preview_sha256=plan.preview_sha256,
            approval_reference=plan.approval_reference,
            actor=context.actor,
            event=context.event,
            workflow_sha=context.workflow_sha,
            run_id=context.run_id,
            run_attempt=context.run_attempt,
            changed_files=list(plan.changed_paths),
            branch=plan.branch,
            validation_results=list(plan.validation_results),
            contract_identities=list(plan.contract_identities),
            file_identities=list(plan.file_identities),
        )
    except StateError as exc:
        receipt = _failure_receipt(context, safe_code(exc), gate, packet_id=args.packet_id)
    except Exception:
        receipt = _failure_receipt(context, "UNEXPECTED_EXCEPTION", gate, packet_id=args.packet_id)
    target = _write_receipt(Path(args.output_root), receipt)
    print(json.dumps({"status": receipt["transaction_state"], "receipt": str(target)}, sort_keys=True))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
