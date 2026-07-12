from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REQUEST_SCHEMA = ROOT / "schemas/athena-hosted-route-request-v1.schema.json"
RECEIPT_SCHEMA = ROOT / "schemas/athena-hosted-route-receipt-v1.schema.json"
CONTRACT = ROOT / "governance/athena-execution-route-contract.md"


class AthenaExecutionRouteContractTests(unittest.TestCase):
    def test_request_schema_is_closed_and_binds_hosted_identity(self) -> None:
        schema = json.loads(REQUEST_SCHEMA.read_text(encoding="utf-8"))
        self.assertFalse(schema["additionalProperties"])
        self.assertEqual(
            schema["properties"]["route"]["enum"],
            ["SPEAR_DIRECT", "ARROW_BOW_HOSTED"],
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
        )
        self.assertEqual([phrase for phrase in required if phrase not in text], [])


if __name__ == "__main__":
    unittest.main()
