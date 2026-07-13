from __future__ import annotations

import copy
import json
import unittest

from tools.athena_routes.hosted import sha256_bytes, stable_json
from tools.athena_routes.m05_parity import (
    ADAPTER_FORBIDDEN_CONFIRMATION,
    M05ParityError,
    PARITY_SCHEMA,
    SUCCESS_CHECKPOINT_SEQUENCE,
    build_m05_parity_evidence,
)
from tools.athena_routes.schema import validate_schema


SHA40 = "a" * 40
HEAD = "b" * 40
TREE = "c" * 40
SHA64 = "1" * 64
MISSION = "2" * 64
CANDIDATE = "3" * 64
PATHSET = "4" * 64
BRANCH = "source/athena-bow-" + "d" * 20


def records() -> tuple[dict, dict, dict, dict, dict[str, bytes]]:
    mission_bytes = stable_json({"mission_sha256": MISSION, "candidate_tree_sha256": CANDIDATE, "final_pathset_sha256": PATHSET}).encode("utf-8")
    output_sha = sha256_bytes(mission_bytes)
    receipt_value = {
        "schema_version": "atlas-thread-engine-spear-compile-receipt-v1",
        "mission_sha256": MISSION,
        "output_mission_sha256": output_sha,
    }
    receipt_bytes = (json.dumps(receipt_value, indent=2, sort_keys=True) + "\n").encode("utf-8")
    compile_sha = sha256_bytes(receipt_bytes)
    direct_files = {
        "PAYLOADS/m05.md": b"m05 payload\n",
        "rp-c01-m05-live-compile-receipt.json": receipt_bytes,
        "rp-c01-m05-live-mission.json": mission_bytes,
    }
    preview = {
        "schema_version": "atlas.athena.guided-intake-preview.v2",
        "result": "ACCEPTED",
        "repository": "Jktomy/atlas-prime",
        "canonical_main_sha": SHA40,
        "workflow_ref": "Jktomy/atlas-prime/.github/workflows/athena-bow-hosted.yml@refs/heads/main",
        "workflow_blob_sha": "e" * 40,
        "carrier_sha256": SHA64,
        "manifest_sha256": "7" * 64,
        "weave_sha256": "8" * 64,
        "mission_id": "RP-C01-M05-LIVE-R01",
        "mission_sha256": MISSION,
        "mission_lock_sha256": "9" * 64,
        "compile_receipt_schema_version": "atlas-thread-engine-spear-compile-receipt-v1",
        "compile_receipt_filename": "rp-c01-m05-live-compile-receipt.json",
        "compile_receipt_sha256": compile_sha,
        "output_mission_filename": "rp-c01-m05-live-mission.json",
        "output_mission_sha256": output_sha,
        "candidate_tree_sha256": CANDIDATE,
        "final_pathset_sha256": PATHSET,
        "compiled_inventory": [
            {"path": path, "bytes": len(payload), "sha256": sha256_bytes(payload)}
            for path, payload in sorted(direct_files.items())
        ],
        "deterministic_branch": BRANCH,
        "path_classification": "ORDINARY",
        "paths": [{"operation": "ADD", "path": "proof/repairing-prime/m05-live.md", "payload_sha256": "0" * 64}],
        "public_clean": True,
        "stop_point": "PREVIEW_COMPLETE",
        "rollback": "NO_REMOTE_MUTATION",
        "forbidden_actions": {
            "adapter_invocation": False, "branch_write": False, "direct_main": False, "force_push": False,
            "merge": False, "pr_write": False, "ready": False, "repository_settings": False,
            "second_writer": False, "standing_authority": False,
        },
    }
    execute = {
        "schema_version": "atlas.athena.guided-intake-execute-receipt.v1",
        "result": "DISPATCHED",
        "error_code": None,
        "repository": "Jktomy/atlas-prime",
        "preview_sha256": sha256_bytes(stable_json(preview).encode("utf-8")),
        "carrier_sha256": SHA64,
        "mission_id": "RP-C01-M05-LIVE-R01",
        "mission_sha256": MISSION,
        "mission_lock_sha256": "9" * 64,
        "canonical_main_sha": SHA40,
        "workflow_ref": "Jktomy/atlas-prime/.github/workflows/athena-bow-hosted.yml@refs/heads/main",
        "workflow_blob_sha": "e" * 40,
        "launch_nonce_sha256": "f" * 64,
        "public_clean_confirmation": "PUBLIC_CLEAN_CONFIRMED",
        "dispatch_transport": "GH_WORKFLOW_JSON_STDIN",
        "workflow_run_id": 12345,
        "workflow_run_url": "https://github.com/Jktomy/atlas-prime/actions/runs/12345",
        "workflow_run_head_sha": SHA40,
        "stop_point": "HOSTED_WORKFLOW_DISPATCH_READBACK",
        "rollback": "HOSTED_ROUTE_RECEIPT_GOVERNS",
        "forbidden_actions": dict(preview["forbidden_actions"]),
    }
    adapter = {
        "schema_version": "atlas.athena.thread-engine-evidence.v2",
        "source_receipt_schema_version": "atlas-thread-engine-production-adapter-receipt-v2",
        "source_receipt_sha256": "a" * 64,
        "mission_id": "RP-C01-M05-LIVE-R01",
        "mission_sha256": MISSION,
        "candidate_tree_sha256": CANDIDATE,
        "commit_tree": TREE,
        "result": "SUCCESS",
        "error_code": None,
        "error_stage": None,
        "stop_point": "DRAFT_PR_READBACK",
        "forbidden_action_confirmation": dict(ADAPTER_FORBIDDEN_CONFIRMATION),
        "branch": BRANCH,
        "checkpoint_results": [
            {"checkpoint": name, "status": "COMPLETED"}
            for name in SUCCESS_CHECKPOINT_SEQUENCE
        ],
        "remote_state": {
            "readback": "VERIFIED", "branch_exists": True, "head_sha": HEAD,
            "pull_request": {"number": 159, "state": "OPEN", "is_draft": True, "head_ref_name": BRANCH, "head_ref_oid": HEAD},
        },
    }
    hosted = {
        "schema_version": "atlas.athena.hosted-route-receipt.v1",
        "result": "SUCCESS",
        "route": "ARROW_BOW_HOSTED",
        "identity": {
            "authorizer": "Jayson", "semantic_operator": "Codex SOL Goal", "requesting_surface": "Codex",
            "event_actor": "Jktomy", "triggering_actor": "Jktomy",
            "workflow_ref": "Jktomy/atlas-prime/.github/workflows/athena-bow-hosted.yml@refs/heads/main",
            "workflow_source_sha": SHA40, "credential_principal": "GITHUB_ACTIONS_REPOSITORY_TOKEN:Jktomy/atlas-prime",
            "token_mode": "GITHUB_TOKEN", "mission_id": "RP-C01-M05-LIVE-R01", "run_id": "12345", "run_attempt": 1,
        },
        "request_sha256": "b" * 64,
        "carrier_sha256": SHA64,
        "compile_receipt_sha256": compile_sha,
        "adapter_receipt_sha256": sha256_bytes(stable_json(adapter).encode("utf-8")),
        "replay_key": "sha256:" + "c" * 64,
        "stage": "DRAFT_PR_READBACK",
        "error_code": None,
        "stop_point": "DRAFT_PR_READBACK",
        "mutation": {"occurred": True, "branch": BRANCH, "pull_request": 159, "head_sha": HEAD, "draft": True},
        "rollback": {"pre_merge": "CLOSE_DRAFT_PR", "post_merge": "REVIEWED_REVERT_PR", "force_or_history_rewrite": False},
        "forbidden_action_confirmation": {
            "direct_main": False, "force_push": False, "ready": False, "merge": False, "settings": False,
            "standing_authority": False, "second_writer": False,
        },
    }
    return preview, execute, hosted, adapter, direct_files


class M05ParityTests(unittest.TestCase):
    def test_exact_same_carrier_route_join_builds_closed_nonpromoting_evidence(self) -> None:
        evidence = build_m05_parity_evidence(*records())
        validate_schema(json.loads(PARITY_SCHEMA.read_text(encoding="utf-8")), evidence)
        self.assertEqual(evidence["result"], "PARITY_VERIFIED")
        self.assertTrue(all(evidence["invariants"].values()))
        self.assertEqual(evidence["promotion_boundary"], "SEPARATE_AUTHORED_RECONCILIATION_REQUIRED")
        self.assertNotEqual(evidence["adapter"]["source_receipt_sha256"], evidence["adapter"]["sanitized_evidence_sha256"])

    def test_any_cross_route_identity_drift_rejects(self) -> None:
        mutations = (
            lambda p, _e, _h, _a, _f: p.__setitem__("carrier_sha256", "d" * 64),
            lambda _p, _e, h, _a, _f: h.__setitem__("compile_receipt_sha256", "d" * 64),
            lambda _p, _e, _h, a, _f: a.__setitem__("candidate_tree_sha256", "d" * 64),
            lambda _p, _e, h, _a, _f: h["mutation"].__setitem__("head_sha", "d" * 40),
            lambda _p, _e, _h, a, _f: a["forbidden_action_confirmation"].__setitem__("force_push", True),
            lambda _p, _e, _h, _a, f: f.__setitem__("PAYLOADS/m05.md", b"edited payload\n"),
            lambda _p, _e, _h, a, _f: a["forbidden_action_confirmation"].pop("force_push"),
            lambda _p, _e, _h, a, _f: a["forbidden_action_confirmation"].__setitem__("unexpected", False),
            lambda _p, _e, _h, a, _f: a["checkpoint_results"].pop(),
            lambda _p, _e, _h, a, _f: a["checkpoint_results"].append({"checkpoint": "EXTRA", "status": "COMPLETED"}),
            lambda _p, _e, _h, a, _f: a["checkpoint_results"].reverse(),
        )
        for index, mutate in enumerate(mutations):
            with self.subTest(index=index):
                values = [copy.deepcopy(item) for item in records()]
                mutate(*values)
                values[2]["adapter_receipt_sha256"] = sha256_bytes(stable_json(values[3]).encode("utf-8"))
                with self.assertRaises(M05ParityError):
                    build_m05_parity_evidence(*values)


if __name__ == "__main__":
    unittest.main()
