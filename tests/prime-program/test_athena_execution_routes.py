from __future__ import annotations

import json
import re
import unittest
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REQUEST_SCHEMA = ROOT / "schemas/athena-hosted-route-request-v1.schema.json"
RECEIPT_SCHEMA = ROOT / "schemas/athena-hosted-route-receipt-v1.schema.json"
GUIDED_PREVIEW_V1_SCHEMA = ROOT / "schemas/athena-guided-intake-preview-v1.schema.json"
GUIDED_PREVIEW_SCHEMA = ROOT / "schemas/athena-guided-intake-preview-v2.schema.json"
GUIDED_EXECUTE_SCHEMA = ROOT / "schemas/athena-guided-intake-execute-receipt-v1.schema.json"
FREE_FORM_FIELDS_SCHEMA = ROOT / "schemas/athena-free-form-mission-fields-v1.schema.json"
FREE_FORM_RECEIPT_SCHEMA = ROOT / "schemas/athena-free-form-intake-receipt-v1.schema.json"
M05_PARITY_SCHEMA = ROOT / "schemas/rp-c01-m05-parity-evidence-v1.schema.json"
ADAPTER_EVIDENCE_SCHEMA = ROOT / "schemas/athena-thread-engine-evidence-v2.schema.json"
CONTRACT = ROOT / "governance/athena-execution-route-contract.md"


class ContractValidationError(ValueError):
    pass


def validate_schema(schema: dict, value: object, path: str = "$") -> None:
    for part in schema.get("allOf", []):
        validate_schema(part, value, path)
    condition = schema.get("if")
    if condition is not None:
        try:
            validate_schema(condition, value, path)
        except ContractValidationError:
            pass
        else:
            validate_schema(schema.get("then", {}), value, path)
    if "const" in schema and value != schema["const"]:
        raise ContractValidationError(f"{path}: const mismatch")
    if "enum" in schema and value not in schema["enum"]:
        raise ContractValidationError(f"{path}: enum mismatch")
    expected = schema.get("type")
    if expected is not None:
        expected_types = expected if isinstance(expected, list) else [expected]
        matches = {
            "object": isinstance(value, dict),
            "string": isinstance(value, str),
            "integer": isinstance(value, int) and not isinstance(value, bool),
            "boolean": isinstance(value, bool),
            "null": value is None,
        }
        if not any(matches.get(item, False) for item in expected_types):
            raise ContractValidationError(f"{path}: type mismatch")
    if isinstance(value, dict):
        required = set(schema.get("required", []))
        missing = required - set(value)
        if missing:
            raise ContractValidationError(f"{path}: missing {sorted(missing)}")
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            extras = set(value) - set(properties)
            if extras:
                raise ContractValidationError(f"{path}: unexpected {sorted(extras)}")
        for key, child in properties.items():
            if key in value:
                validate_schema(child, value[key], f"{path}.{key}")
    if isinstance(value, str):
        if len(value) < schema.get("minLength", 0):
            raise ContractValidationError(f"{path}: too short")
        pattern = schema.get("pattern")
        if pattern and re.search(pattern, value) is None:
            raise ContractValidationError(f"{path}: pattern mismatch")
    if isinstance(value, int) and not isinstance(value, bool):
        if value < schema.get("minimum", value):
            raise ContractValidationError(f"{path}: below minimum")


def valid_request() -> dict:
    return {
        "schema_version": "atlas.athena.hosted-route-request.v1",
        "authorizer": "Jayson",
        "semantic_operator": "Codex SOL Goal",
        "requesting_surface": "Codex",
        "repository": "Jktomy/atlas-prime",
        "base_sha": "1" * 40,
        "route": "ARROW_BOW_HOSTED",
        "mission_id": "RP-C01-PILOT-R01",
        "carrier_sha256": "2" * 64,
        "mission_lock_sha256": "6" * 64,
        "event_identity": {
            "event_name": "workflow_dispatch",
            "event_action": "requested",
            "event_node_or_delivery_id": "run-request-1",
            "created_at": "2026-07-12T00:00:00Z",
            "updated_at": "2026-07-12T00:00:00Z",
            "event_payload_sha256": "3" * 64,
            "event_actor": "Jktomy",
            "triggering_actor": "Jktomy",
            "workflow_ref": "Jktomy/atlas-prime/.github/workflows/athena-bow-hosted.yml@refs/heads/main",
            "workflow_source_sha": "4" * 40,
            "run_id": "12345",
            "run_attempt": 1,
        },
        "credential_identity": {
            "credential_principal": "github-actions[bot]",
            "token_mode": "GITHUB_TOKEN",
        },
        "replay_key": "sha256:" + "5" * 64,
        "protected_path_classification": "ORDINARY",
        "stop_boundary": "DRAFT_PR_READBACK",
        "forbidden_actions": {
            "direct_main": False,
            "force_push": False,
            "ready": False,
            "merge": False,
            "settings": False,
            "standing_authority": False,
            "second_writer": False,
        },
    }


def valid_success_receipt() -> dict:
    return {
        "schema_version": "atlas.athena.hosted-route-receipt.v1",
        "result": "SUCCESS",
        "route": "ARROW_BOW_HOSTED",
        "identity": {
            "authorizer": "Jayson",
            "semantic_operator": "Codex SOL Goal",
            "requesting_surface": "Codex",
            "event_actor": "Jktomy",
            "triggering_actor": "Jktomy",
            "workflow_ref": "Jktomy/atlas-prime/.github/workflows/athena-bow-hosted.yml@refs/heads/main",
            "workflow_source_sha": "4" * 40,
            "credential_principal": "github-actions[bot]",
            "token_mode": "GITHUB_TOKEN",
            "mission_id": "RP-C01-PILOT-R01",
            "run_id": "12345",
            "run_attempt": 1,
        },
        "request_sha256": "6" * 64,
        "carrier_sha256": "2" * 64,
        "compile_receipt_sha256": "7" * 64,
        "adapter_receipt_sha256": "8" * 64,
        "replay_key": "sha256:" + "5" * 64,
        "stage": "DRAFT_PR_READBACK",
        "error_code": None,
        "stop_point": "DRAFT_PR_READBACK",
        "mutation": {
            "occurred": True,
            "branch": "agent/rp-c01-pilot-r01",
            "pull_request": 100,
            "head_sha": "9" * 40,
            "draft": True,
        },
        "rollback": {
            "pre_merge": "CLOSE_DRAFT_PR",
            "post_merge": "REVIEWED_REVERT_PR",
            "force_or_history_rewrite": False,
        },
        "forbidden_action_confirmation": {
            "direct_main": False,
            "force_push": False,
            "ready": False,
            "merge": False,
            "settings": False,
            "standing_authority": False,
            "second_writer": False,
        },
    }


class AthenaExecutionRouteContractTests(unittest.TestCase):
    def test_route_architecture_is_exact_and_nonconflated(self) -> None:
        contract = CONTRACT.read_text(encoding="utf-8")
        required = (
            "ATHENA_SPEAR",
            "JAYSON_ARTEMIS_ARROW_BOW",
            "ATHENA_PHOENIX_BLADE",
            "ATHENA_AEGIS_BREAK",
            "Phoenix Blade mirrors what Oathbringer is to Jayson",
            "Aegis Break owns safe alternate-route selection",
            "DIRECT_GITHUB_NATIVE_ROUTE=AEGIS_BREAK",
            "PHOENIX_BLADE_USES_THREAD_ENGINE=false",
            "BOW_ARROW_OWNERSHIP=JAYSON_AND_ARTEMIS",
            "NORMAL_STOP_BOUNDARY=DRAFT_PR_READBACK",
        )
        self.assertEqual([phrase for phrase in required if phrase not in contract], [])
        self.assertNotIn("Phoenix Blade remains the Athena-native direct control route", contract)

    def test_cap015_and_aj01_use_accepted_direct_spear_evidence(self) -> None:
        contract = CONTRACT.read_text(encoding="utf-8")
        acceptance = (ROOT / "governance/capability-acceptance-contract.md").read_text(encoding="utf-8")
        proof = json.loads(
            (ROOT / "proof/repairing-prime/rp-c08-cap015-architecture-realignment-r02.json").read_text(encoding="utf-8")
        )
        self.assertIn("Direct Spear compilation and Thread Engine delivery are already proven", contract)
        self.assertIn("AJ-01 is `PROVEN`", acceptance)
        self.assertEqual(proof["accepted_evidence"]["direct_spear"]["pull_request"], 102)
        self.assertEqual(proof["transitions"]["CAP-015"]["to"], "RESTORED/ACTIVE")
        self.assertFalse(proof["superseded_premise"]["external_bridge_required"])

    def test_remaining_acceptance_boundaries_are_preserved(self) -> None:
        contract = CONTRACT.read_text(encoding="utf-8")
        acceptance = (ROOT / "governance/capability-acceptance-contract.md").read_text(encoding="utf-8")
        self.assertIn("`AJ-03` is PROVEN", contract)
        self.assertIn("AJ-03 PROVEN", acceptance)
        self.assertIn("AJ-11 PROVEN", acceptance)
        self.assertIn("AJ-12 UNPROVEN", acceptance)
        self.assertIn("does not promote AJ-11, AJ-12, CAP-027", contract)

    def test_guided_publisher_contracts_remain_closed(self) -> None:
        for path in (GUIDED_PREVIEW_V1_SCHEMA, GUIDED_PREVIEW_SCHEMA, GUIDED_EXECUTE_SCHEMA):
            schema = json.loads(path.read_text(encoding="utf-8"))
            self.assertFalse(schema["additionalProperties"])
            forbidden = schema["properties"]["forbidden_actions"]
            self.assertFalse(forbidden["additionalProperties"])
            self.assertTrue(all(value == {"const": False} for value in forbidden["properties"].values()))

    def test_free_form_and_parity_surfaces_remain_nonpromoting(self) -> None:
        fields = json.loads(FREE_FORM_FIELDS_SCHEMA.read_text(encoding="utf-8"))
        receipt = json.loads(FREE_FORM_RECEIPT_SCHEMA.read_text(encoding="utf-8"))
        parity = json.loads(M05_PARITY_SCHEMA.read_text(encoding="utf-8"))
        adapter = json.loads(ADAPTER_EVIDENCE_SCHEMA.read_text(encoding="utf-8"))
        self.assertFalse(fields["additionalProperties"])
        self.assertFalse(receipt["additionalProperties"])
        self.assertEqual(receipt["properties"]["stop_point"]["const"], "FREE_FORM_CARRIER_CONSTRUCTED")
        self.assertEqual(parity["properties"]["promotion_boundary"]["const"], "SEPARATE_AUTHORED_RECONCILIATION_REQUIRED")
        self.assertFalse(adapter["additionalProperties"])

    def test_hosted_request_schema_binds_route_token_and_identity(self) -> None:
        schema = json.loads(REQUEST_SCHEMA.read_text(encoding="utf-8"))
        request = valid_request()
        validate_schema(schema, request)
        self.assertEqual(schema["properties"]["route"]["const"], "ARROW_BOW_HOSTED")
        for path, invalid_value in (
            (("route",), "SPEAR_DIRECT"),
            (("credential_identity", "token_mode"), "USER_SESSION_TOKEN"),
            (("protected_path_classification",), "THREAD_ENGINE_SELF_CHANGE"),
        ):
            invalid = deepcopy(request)
            target = invalid
            for key in path[:-1]:
                target = target[key]
            target[path[-1]] = invalid_value
            with self.assertRaises(ContractValidationError):
                validate_schema(schema, invalid)

    def test_hosted_receipt_rejects_incoherent_state(self) -> None:
        schema = json.loads(RECEIPT_SCHEMA.read_text(encoding="utf-8"))
        success = valid_success_receipt()
        validate_schema(schema, success)

        nondraft = deepcopy(success)
        nondraft["mutation"]["draft"] = False
        with self.assertRaises(ContractValidationError):
            validate_schema(schema, nondraft)

        rejected_with_mutation = deepcopy(success)
        rejected_with_mutation["result"] = "REJECTED"
        rejected_with_mutation["error_code"] = "MALFORMED_CARRIER"
        with self.assertRaises(ContractValidationError):
            validate_schema(schema, rejected_with_mutation)

        partial = deepcopy(success)
        partial.update(
            {
                "result": "PARTIAL",
                "error_code": "PR_READBACK_MISMATCH",
                "stop_point": "PARTIAL_STATE_PRESERVED",
                "mutation": {
                    "occurred": True,
                    "branch": "agent/rp-c01-pilot-r01",
                    "pull_request": None,
                    "head_sha": "9" * 40,
                    "draft": None,
                },
                "rollback": {
                    "pre_merge": "PRESERVE_PARTIAL_STATE_AND_REVIEW",
                    "post_merge": "NO_MERGE_OCCURRED",
                    "force_or_history_rewrite": False,
                },
            }
        )
        validate_schema(schema, partial)


if __name__ == "__main__":
    unittest.main()
