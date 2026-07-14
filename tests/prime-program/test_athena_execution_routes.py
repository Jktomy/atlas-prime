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
M05_PARITY_SCHEMA = ROOT / "schemas/rp-c01-m05-parity-evidence-v1.schema.json"
ADAPTER_EVIDENCE_SCHEMA = ROOT / "schemas/athena-thread-engine-evidence-v2.schema.json"
CONTRACT = ROOT / "governance/athena-execution-route-contract.md"
ARCHITECTURE = ROOT / "governance/athena-route-architecture-r01.md"


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
    def test_closed_guided_schemas_preserve_forbidden_actions(self) -> None:
        for path in (
            GUIDED_PREVIEW_V1_SCHEMA,
            GUIDED_PREVIEW_SCHEMA,
            GUIDED_EXECUTE_SCHEMA,
        ):
            schema = json.loads(path.read_text(encoding="utf-8"))
            self.assertFalse(schema["additionalProperties"])
            forbidden = schema["properties"]["forbidden_actions"]
            self.assertFalse(forbidden["additionalProperties"])
            self.assertTrue(
                all(
                    value == {"const": False}
                    for value in forbidden["properties"].values()
                )
            )

    def test_hosted_request_and_receipt_are_closed(self) -> None:
        request_schema = json.loads(REQUEST_SCHEMA.read_text(encoding="utf-8"))
        receipt_schema = json.loads(RECEIPT_SCHEMA.read_text(encoding="utf-8"))
        self.assertFalse(request_schema["additionalProperties"])
        self.assertFalse(receipt_schema["additionalProperties"])
        self.assertEqual(
            request_schema["properties"]["route"]["const"],
            "ARROW_BOW_HOSTED",
        )
        validate_schema(request_schema, valid_request())
        validate_schema(receipt_schema, valid_success_receipt())

    def test_schema_rejects_wrong_route_or_token(self) -> None:
        schema = json.loads(REQUEST_SCHEMA.read_text(encoding="utf-8"))
        for path, value in (
            (("route",), "SPEAR_DIRECT"),
            (("credential_identity", "token_mode"), "USER_SESSION_TOKEN"),
        ):
            request = deepcopy(valid_request())
            target = request
            for key in path[:-1]:
                target = target[key]
            target[path[-1]] = value
            with self.assertRaises(ContractValidationError):
                validate_schema(schema, request)

    def test_receipt_rejects_false_success(self) -> None:
        schema = json.loads(RECEIPT_SCHEMA.read_text(encoding="utf-8"))
        receipt = valid_success_receipt()
        receipt["mutation"]["draft"] = False
        with self.assertRaises(ContractValidationError):
            validate_schema(schema, receipt)

    def test_m05_and_adapter_schemas_remain_closed(self) -> None:
        parity = json.loads(M05_PARITY_SCHEMA.read_text(encoding="utf-8"))
        adapter = json.loads(ADAPTER_EVIDENCE_SCHEMA.read_text(encoding="utf-8"))
        self.assertFalse(parity["additionalProperties"])
        self.assertEqual(parity["properties"]["result"]["const"], "PARITY_VERIFIED")
        self.assertFalse(adapter["additionalProperties"])

    def test_contract_preserves_one_engine_and_route_identity(self) -> None:
        text = " ".join(CONTRACT.read_text(encoding="utf-8").split())
        architecture = " ".join(ARCHITECTURE.read_text(encoding="utf-8").split())
        for phrase in (
            "SPEAR_DIRECT",
            "ARROW_BOW_HOSTED",
            "the same singular Prime Thread Engine production adapter",
            "DRAFT_PR_READBACK",
            "PARTIAL",
            "JSON on standard input",
            "ROLLBACK_POST_MERGE=REVIEWED_REVERT_PR",
        ):
            self.assertIn(phrase, text)
        self.assertIn("Spear belongs to Athena", text)
        self.assertIn("Arrow/Bow belongs to Jayson and Artemis", text)
        self.assertIn(
            "No platform-origin attestation or external bridge is required",
            text,
        )
        self.assertIn("Sword -> Phoenix Blade", architecture)
        self.assertIn(
            "Aegis Break is Athena's direct/adaptive safe method",
            architecture,
        )


if __name__ == "__main__":
    unittest.main()
