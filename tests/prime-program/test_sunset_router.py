from __future__ import annotations

import json
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
    verify_router_preview,
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

    def tamper_receipt(self, directory: Path, **changes: object) -> None:
        path = directory / "sunset-router-receipt.json"
        receipt = json.loads(path.read_text(encoding="utf-8"))
        receipt.update(changes)
        path.write_bytes(canonical_bytes(receipt))

    def preview(self, parent: Path) -> Path:
        preview = parent / "preview"
        generate_router_preview(
            ROOT,
            self.write(parent / "request.json", wrapper("ATHENA", "AUTO", False)),
            preview,
        )
        return preview

    def pipeline(self, parent: Path) -> tuple[Path, Path, Path]:
        preview = self.preview(parent)
        approval = parent / "approval"
        candidate = parent / "candidate"
        generate_router_approval(ROOT, preview, approval, approval_mode="STANDARD")
        generate_router_candidate(ROOT, preview, approval, candidate)
        return preview, approval, candidate

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

    def test_preview_receipt_must_exactly_match_preview_plan(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            preview = self.preview(Path(temp))
            self.tamper_receipt(
                preview,
                state="BLOCKED_RESUMABLE",
                reason_code="SCHEMA_VALID_TAMPER",
            )
            with self.assertRaises(LifecycleError) as raised:
                verify_router_preview(ROOT, preview)
            self.assertEqual(raised.exception.code, "SUNSET_ROUTER_BINDING")

    def test_approval_receipt_must_exactly_match_preview_and_approval(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            parent = Path(temp)
            preview = self.preview(parent)
            approval = parent / "approval"
            generate_router_approval(ROOT, preview, approval, approval_mode="STANDARD")
            self.tamper_receipt(approval, request_digest="sha256:" + ("0" * 64))
            with self.assertRaises(LifecycleError) as raised:
                generate_router_candidate(ROOT, preview, approval, parent / "candidate")
            self.assertEqual(raised.exception.code, "SUNSET_ROUTER_BINDING")

    def test_publication_receipt_must_exactly_match_candidate_plan(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            preview, approval, candidate = self.pipeline(Path(temp))
            self.tamper_receipt(candidate, next_safe_action="Schema-valid tampered action.")
            with self.assertRaises(LifecycleError) as raised:
                verify_router_candidate(ROOT, preview, approval, candidate)
            self.assertEqual(raised.exception.code, "SUNSET_ROUTER_BINDING")

    def test_resumable_and_publication_receipts_remain_non_promoting(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            preview, approval, candidate = self.pipeline(Path(temp))
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
