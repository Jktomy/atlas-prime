from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tests.lifecycle.test_sunset_candidate import request
from tools.atlas_lifecycle.errors import LifecycleError
from tools.atlas_lifecycle.jsonio import canonical_bytes
from tools.atlas_lifecycle.schema import SchemaValidator
from tools.sunset_router.core import (
    build_publication_receipt,
    build_resumable_receipt,
    generate_router_approval,
    generate_router_candidate,
    generate_router_preview,
    verify_router_candidate,
)

ROOT = Path(__file__).resolve().parents[2]


def wrapper(actor: str, route: str, transfer: bool) -> dict:
    return {
        "schema_id": "atlas.sunset-router.request",
        "schema_version": "1.0.0",
        "authority": "PUBLIC_CLEAN_REQUEST",
        "actor": actor,
        "requested_route": route,
        "operator_transfer_authorized": transfer,
        "lifecycle_request": request("NON_QUEST"),
    }


class SunsetRouterPrimeProgramTests(unittest.TestCase):
    def write(self, path: Path, value: dict) -> Path:
        path.write_bytes(canonical_bytes(value))
        return path

    def test_router_schemas_are_in_trusted_catalog(self) -> None:
        validator = SchemaValidator(ROOT / "lifecycle" / "schemas")
        validator.validate_sunset_router_request(wrapper("ATHENA", "AUTO", False))

    def test_operator_transfer_is_never_automatic(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            parent = Path(temp)
            with self.assertRaises(LifecycleError) as raised:
                generate_router_preview(
                    ROOT,
                    self.write(parent / "request.json", wrapper("JAYSON", "AUTO", False)),
                    parent / "preview",
                )
            self.assertEqual(raised.exception.code, "OPERATOR_TRANSFER_REQUIRED")

    def test_exact_jayson_route_has_only_operator_transfer_stop(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            parent = Path(temp)
            preview = parent / "preview"
            result = generate_router_preview(
                ROOT,
                self.write(
                    parent / "request.json",
                    wrapper("JAYSON", "JAYSON_OATHBRINGER_SWORD", True),
                ),
                preview,
            )
            self.assertEqual(result["selected_route"], "JAYSON_OATHBRINGER_SWORD")
            self.assertEqual(result["fallback_routes"], ["OPERATOR_TRANSFER_REQUIRED"])

    def test_resumable_and_publication_receipts_remain_non_promoting(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            parent = Path(temp)
            preview = parent / "preview"
            approval = parent / "approval"
            candidate = parent / "candidate"
            generate_router_preview(
                ROOT,
                self.write(parent / "request.json", wrapper("ATHENA", "AUTO", False)),
                preview,
            )
            generate_router_approval(ROOT, preview, approval, approval_mode="STANDARD")
            generate_router_candidate(ROOT, preview, approval, candidate)
            plan = verify_router_candidate(ROOT, preview, approval, candidate)["plan"]
            blocked = build_resumable_receipt(
                ROOT,
                plan,
                reason_code="CONNECTOR_UNAVAILABLE",
                next_safe_action="Resume the same exact plan after read-only reconciliation.",
            )
            self.assertEqual(blocked["state"], "BLOCKED_RESUMABLE")
            validation = build_publication_receipt(
                ROOT,
                plan,
                state="APPROVED_PENDING_VALIDATION",
                expected_head="a" * 40,
                pull_request=999,
            )
            self.assertFalse(validation["canonical_readback"])
            with self.assertRaises(LifecycleError) as raised:
                build_publication_receipt(
                    ROOT,
                    plan,
                    state="READBACK_COMPLETE",
                    expected_head="a" * 40,
                    pull_request=999,
                    merged_commit="b" * 40,
                )
            self.assertEqual(raised.exception.code, "SUNSET_ROUTER_READBACK")


if __name__ == "__main__":
    unittest.main()
