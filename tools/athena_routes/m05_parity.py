from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .hosted import ADAPTER_EVIDENCE_SCHEMA, RECEIPT_SCHEMA, load_schema, sha256_bytes, stable_json
from .guided_publisher import EXECUTE_SCHEMA, PREVIEW_SCHEMA
from .schema import SchemaValidationError, validate_schema


ROOT = Path(__file__).resolve().parents[2]
PARITY_SCHEMA = ROOT / "schemas" / "rp-c01-m05-parity-evidence-v1.schema.json"
SUCCESS_CHECKPOINT_SEQUENCE = (
    "ACTIVATION_GATE",
    "PACKAGE_AUDIT",
    "MISSION_PARSE",
    "MISSION_SCHEMA",
    "MISSION_INTEGRITY",
    "PROTECTED_ROUTE_INTENT",
    "OPERATOR_VERIFY",
    "REMOTE_LOCK",
    "DUPLICATE_CHECK",
    "FRESH_CLONE",
    "CLEAN_START",
    "SOURCE_BLOB_VERIFY",
    "CANDIDATE_STAGE",
    "PATH_POLICY_VERIFY",
    "TREE_VERIFY",
    "INSTALL",
    "DIFF_CHECK",
    "STAGE_VERIFY",
    "COMMIT",
    "COMMIT_VERIFY",
    "PRE_PUSH_REMOTE_LOCK",
    "PUSH",
    "DRAFT_PR",
    "READBACK",
)
ADAPTER_FORBIDDEN_CONFIRMATION = {
    "direct_main_write": False,
    "force_push": False,
    "auto_merge": False,
    "ready_transition": False,
    "workflow_dispatch": False,
    "repository_setting_mutation": False,
    "unprofiled_generated_output_mutation": False,
    "protected_board_mutation": False,
    "production_authority_activated": False,
    "standing_authority": "NO",
}


class M05ParityError(RuntimeError):
    def __init__(self, message: str, code: str = "M05_PARITY_REJECTED") -> None:
        super().__init__(message)
        self.code = code


def _reject(condition: bool, message: str, code: str = "M05_PARITY_REJECTED") -> None:
    if not condition:
        raise M05ParityError(message, code)


def _validate_inputs(
    preview: dict[str, Any], execute: dict[str, Any], hosted: dict[str, Any], adapter: dict[str, Any]
) -> None:
    try:
        validate_schema(load_schema(PREVIEW_SCHEMA), preview)
        validate_schema(load_schema(EXECUTE_SCHEMA), execute)
        validate_schema(load_schema(RECEIPT_SCHEMA), hosted)
        validate_schema(load_schema(ADAPTER_EVIDENCE_SCHEMA), adapter)
    except (SchemaValidationError, RuntimeError) as exc:
        raise M05ParityError("M05 parity input schema rejected", "M05_PARITY_INPUT_INVALID") from exc


def _all_forbidden_actions_false(
    preview: dict[str, Any], execute: dict[str, Any], hosted: dict[str, Any], adapter: dict[str, Any]
) -> bool:
    simple = (*preview["forbidden_actions"].values(), *execute["forbidden_actions"].values())
    hosted_values = hosted["forbidden_action_confirmation"].values()
    return (
        all(value is False for value in simple)
        and all(value is False for value in hosted_values)
        and adapter.get("forbidden_action_confirmation") == ADAPTER_FORBIDDEN_CONFIRMATION
    )


def build_m05_parity_evidence(
    preview: dict[str, Any],
    execute: dict[str, Any],
    hosted: dict[str, Any],
    adapter: dict[str, Any],
    direct_compiled_files: dict[str, bytes],
) -> dict[str, Any]:
    """Build a closed, non-promoting parity record from one guided hosted journey."""
    _validate_inputs(preview, execute, hosted, adapter)
    _reject(execute["result"] == "DISPATCHED", "guided Execute did not reach exact dispatch readback")
    _reject(hosted["result"] == "SUCCESS" and hosted["route"] == "ARROW_BOW_HOSTED", "hosted route did not succeed")
    _reject(adapter.get("result") == "SUCCESS", "Thread Engine evidence did not succeed")
    preview_sha = sha256_bytes(stable_json(preview).encode("utf-8"))
    _reject(execute["preview_sha256"] == preview_sha, "guided Preview digest mismatch")

    carrier = preview["carrier_sha256"]
    _reject(execute["carrier_sha256"] == carrier == hosted["carrier_sha256"], "carrier parity mismatch")
    mission_id = preview["mission_id"]
    _reject(execute["mission_id"] == mission_id == hosted["identity"]["mission_id"] == adapter.get("mission_id"), "mission identity mismatch")
    mission_sha = preview["mission_sha256"]
    _reject(execute["mission_sha256"] == mission_sha == adapter.get("mission_sha256"), "canonical mission digest mismatch")
    base = preview["canonical_main_sha"]
    _reject(execute["canonical_main_sha"] == base, "guided canonical base mismatch")
    _reject(hosted["identity"]["workflow_source_sha"] == base, "hosted workflow source/base mismatch")
    _reject(execute["workflow_run_head_sha"] == base, "guided run head/base mismatch")
    run_id = execute["workflow_run_id"]
    _reject(run_id == int(hosted["identity"]["run_id"]), "workflow run identity mismatch")

    compile_sha = preview["compile_receipt_sha256"]
    _reject(hosted["compile_receipt_sha256"] == compile_sha, "compiler receipt parity mismatch")
    inventory = preview["compiled_inventory"]
    by_path = {item["path"]: item for item in inventory}
    _reject(len(by_path) == len(inventory), "compiled inventory contains duplicate paths")
    _reject(by_path.get(preview["compile_receipt_filename"], {}).get("sha256") == compile_sha, "compiled receipt inventory mismatch")
    _reject(by_path.get(preview["output_mission_filename"], {}).get("sha256") == preview["output_mission_sha256"], "compiled mission inventory mismatch")
    observed_inventory = [
        {"path": path, "bytes": len(payload), "sha256": sha256_bytes(payload)}
        for path, payload in sorted(direct_compiled_files.items())
    ]
    _reject(observed_inventory == inventory, "retained direct compiled files do not match Preview inventory")
    receipt_bytes = direct_compiled_files.get(preview["compile_receipt_filename"])
    _reject(isinstance(receipt_bytes, bytes) and sha256_bytes(receipt_bytes) == compile_sha, "retained direct compiler receipt mismatch")
    try:
        direct_receipt = json.loads(receipt_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise M05ParityError("retained direct compiler receipt is invalid", "M05_DIRECT_RECEIPT_INVALID") from exc
    _reject(direct_receipt.get("schema_version") == preview["compile_receipt_schema_version"], "direct compiler schema mismatch")
    _reject(direct_receipt.get("mission_sha256") == mission_sha, "direct compiler mission digest mismatch")
    _reject(direct_receipt.get("output_mission_sha256") == preview["output_mission_sha256"], "direct compiler output mission mismatch")

    sanitized_sha = sha256_bytes(stable_json(adapter).encode("utf-8"))
    _reject(hosted["adapter_receipt_sha256"] == sanitized_sha, "sanitized adapter evidence digest mismatch")
    _reject(adapter.get("source_receipt_schema_version") == "atlas-thread-engine-production-adapter-receipt-v2", "adapter source schema mismatch")
    _reject(adapter.get("candidate_tree_sha256") == preview["candidate_tree_sha256"], "candidate tree parity mismatch")
    _reject(adapter.get("stop_point") == "DRAFT_PR_READBACK", "adapter stop boundary mismatch")

    branch = preview["deterministic_branch"]
    mutation = hosted["mutation"]
    remote = adapter.get("remote_state")
    _reject(isinstance(remote, dict), "adapter remote readback missing")
    pr = remote.get("pull_request") if isinstance(remote, dict) else None
    _reject(isinstance(pr, dict), "adapter pull-request readback missing")
    _reject(adapter.get("branch") == branch == mutation["branch"], "route branch mismatch")
    _reject(remote.get("readback") == "VERIFIED" and remote.get("branch_exists") is True, "remote branch readback not exact")
    _reject(remote.get("head_sha") == mutation["head_sha"] == pr.get("head_ref_oid"), "exact head readback mismatch")
    _reject(pr.get("head_ref_name") == branch and pr.get("number") == mutation["pull_request"], "pull-request identity mismatch")
    _reject(pr.get("state") == "OPEN" and pr.get("is_draft") is True and mutation["draft"] is True, "draft pull-request state mismatch")

    checkpoints = adapter.get("checkpoint_results")
    _reject(isinstance(checkpoints, list) and all(isinstance(item, dict) for item in checkpoints), "adapter checkpoint sequence missing")
    checkpoint_names = [item.get("checkpoint") for item in checkpoints]
    _reject(checkpoint_names == list(SUCCESS_CHECKPOINT_SEQUENCE), "adapter checkpoint sequence drifted")
    _reject(all(item.get("status") == "COMPLETED" for item in checkpoints), "adapter checkpoint did not complete")
    _reject(_all_forbidden_actions_false(preview, execute, hosted, adapter), "forbidden-action confirmation failed")

    source_receipt_sha = adapter.get("source_receipt_sha256")
    commit_tree = adapter.get("commit_tree")
    _reject(isinstance(source_receipt_sha, str) and len(source_receipt_sha) == 64, "adapter source receipt digest missing")
    _reject(isinstance(commit_tree, str) and len(commit_tree) == 40, "adapter commit tree missing")
    evidence = {
        "schema_version": "atlas.repairing-prime.rp-c01-m05-parity-evidence.v1",
        "result": "PARITY_VERIFIED",
        "repository": "Jktomy/atlas-prime",
        "mission_id": mission_id,
        "base_sha": base,
        "carrier_sha256": carrier,
        "preview_sha256": preview_sha,
        "workflow_run_id": run_id,
        "compiler": {
            "schema_version": preview["compile_receipt_schema_version"],
            "compile_receipt_sha256": compile_sha,
            "output_mission_sha256": preview["output_mission_sha256"],
            "candidate_tree_sha256": preview["candidate_tree_sha256"],
            "final_pathset_sha256": preview["final_pathset_sha256"],
            "compiled_inventory_sha256": sha256_bytes(stable_json(inventory).encode("utf-8")),
        },
        "adapter": {
            "source_receipt_schema_version": adapter["source_receipt_schema_version"],
            "source_receipt_sha256": source_receipt_sha,
            "sanitized_evidence_sha256": sanitized_sha,
            "candidate_tree_sha256": adapter["candidate_tree_sha256"],
            "commit_tree": commit_tree,
            "branch": branch,
            "pull_request": mutation["pull_request"],
            "head_sha": mutation["head_sha"],
            "checkpoint_sequence_sha256": sha256_bytes(stable_json(checkpoints).encode("utf-8")),
            "stop_point": "DRAFT_PR_READBACK",
        },
        "invariants": {
            "same_carrier": True,
            "same_mission": True,
            "same_compiler_receipt": True,
            "same_candidate_tree": True,
            "same_branch": True,
            "exact_draft_pr_readback": True,
            "singular_adapter_execution": True,
            "all_forbidden_actions_false": True,
        },
        "promotion_boundary": "SEPARATE_AUTHORED_RECONCILIATION_REQUIRED",
    }
    try:
        validate_schema(load_schema(PARITY_SCHEMA), evidence)
    except (SchemaValidationError, RuntimeError) as exc:
        raise M05ParityError("constructed M05 parity evidence schema rejected", "M05_PARITY_EVIDENCE_INVALID") from exc
    return evidence
