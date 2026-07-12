from __future__ import annotations

import json
import re
import unittest
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REQUEST_SCHEMA = ROOT / "schemas/athena-hosted-route-request-v1.schema.json"
RECEIPT_SCHEMA = ROOT / "schemas/athena-hosted-route-receipt-v1.schema.json"
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
    def test_request_schema_is_closed_and_binds_hosted_identity(self) -> None:
        schema = json.loads(REQUEST_SCHEMA.read_text(encoding="utf-8"))
        self.assertFalse(schema["additionalProperties"])
        self.assertEqual(
            schema["properties"]["route"]["const"],
            "ARROW_BOW_HOSTED",
        )
        event = schema["properties"]["event_identity"]
        credential = schema["properties"]["credential_identity"]
        self.assertFalse(event["additionalProperties"])
        self.assertFalse(credential["additionalProperties"])
        self.assertEqual(
            set(event["required"]),
            {
                "event_name",
                "event_action",
                "event_node_or_delivery_id",
                "created_at",
                "updated_at",
                "event_payload_sha256",
                "event_actor",
                "triggering_actor",
                "workflow_ref",
                "workflow_source_sha",
                "run_id",
                "run_attempt",
            },
        )
        self.assertEqual(
            set(credential["required"]),
            {"credential_principal", "token_mode"},
        )
        self.assertEqual(
            credential["properties"]["token_mode"], {"const": "GITHUB_TOKEN"}
        )
        self.assertEqual(
            schema["properties"]["protected_path_classification"],
            {"const": "ORDINARY"},
        )

    def test_receipt_schema_separates_every_aj_02_identity(self) -> None:
        schema = json.loads(RECEIPT_SCHEMA.read_text(encoding="utf-8"))
        self.assertFalse(schema["additionalProperties"])
        identity = schema["properties"]["identity"]
        self.assertFalse(identity["additionalProperties"])
        self.assertEqual(
            set(identity["required"]),
            {
                "authorizer",
                "semantic_operator",
                "requesting_surface",
                "event_actor",
                "triggering_actor",
                "workflow_ref",
                "workflow_source_sha",
                "credential_principal",
                "token_mode",
                "mission_id",
                "run_id",
                "run_attempt",
            },
        )

    def test_forbidden_actions_are_fixed_false_in_request_and_receipt(self) -> None:
        for path in (REQUEST_SCHEMA, RECEIPT_SCHEMA):
            schema = json.loads(path.read_text(encoding="utf-8"))
            forbidden = schema["properties"][
                "forbidden_actions"
                if path == REQUEST_SCHEMA
                else "forbidden_action_confirmation"
            ]
            self.assertFalse(forbidden["additionalProperties"])
            self.assertEqual(
                set(forbidden["required"]),
                {
                    "direct_main",
                    "force_push",
                    "ready",
                    "merge",
                    "settings",
                    "standing_authority",
                    "second_writer",
                },
            )
            self.assertTrue(
                all(item == {"const": False} for item in forbidden["properties"].values())
            )

    def test_contract_converges_on_one_engine_and_preserves_proof_boundaries(self) -> None:
        text = CONTRACT.read_text(encoding="utf-8")
        required = (
            "the same singular Prime Thread Engine production adapter",
            "AEGIS_BREAK_TO_OATHBRINGER",
            "GENERATED_SOURCE_MIXING",
            "DRAFT_PR_READBACK",
            "fresh Work/Athena context",
            "does not promote CAP-009, CAP-010, CAP-011, or CAP-015",
            "AJ-01, AJ-02, and AJ-03 remain unproven",
            "COMPONENT_EVIDENCE_CANNOT_ASSERT_ROUTE_GATE",
            "Only a locally pre-screened, public-clean, size-bounded carrier",
            "never echo carrier bytes",
            "ROLLBACK_POST_MERGE=REVIEWED_REVERT_PR",
        )
        self.assertEqual([phrase for phrase in required if phrase not in text], [])

    def test_complete_request_instances_enforce_route_token_and_classification(self) -> None:
        schema = json.loads(REQUEST_SCHEMA.read_text(encoding="utf-8"))
        request = valid_request()
        validate_schema(schema, request)
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

    def test_complete_receipts_reject_counterfeit_or_incoherent_state(self) -> None:
        schema = json.loads(RECEIPT_SCHEMA.read_text(encoding="utf-8"))
        success = valid_success_receipt()
        validate_schema(schema, success)

        counterfeit_success = deepcopy(success)
        counterfeit_success["stop_point"] = "PRE_MUTATION_REJECTION"
        counterfeit_success["mutation"] = {
            "occurred": False,
            "branch": None,
            "pull_request": None,
            "head_sha": None,
            "draft": None,
        }
        with self.assertRaises(ContractValidationError):
            validate_schema(schema, counterfeit_success)

        rejected_with_mutation = deepcopy(success)
        rejected_with_mutation["result"] = "REJECTED"
        rejected_with_mutation["error_code"] = "MALFORMED_CARRIER"
        with self.assertRaises(ContractValidationError):
            validate_schema(schema, rejected_with_mutation)

        missing_remote_identity = deepcopy(success)
        missing_remote_identity["mutation"]["branch"] = None
        with self.assertRaises(ContractValidationError):
            validate_schema(schema, missing_remote_identity)

        nondraft_success = deepcopy(success)
        nondraft_success["mutation"]["draft"] = False
        with self.assertRaises(ContractValidationError):
            validate_schema(schema, nondraft_success)


if __name__ == "__main__":
    unittest.main()
