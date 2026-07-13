from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Protocol

from .hosted import load_schema, sha256_bytes, stable_json
from .schema import validate_schema


ROOT = Path(__file__).resolve().parents[2]
ORIGIN_SCHEMA = ROOT / "schemas" / "athena-fresh-work-origin-receipt-v1.schema.json"
JOURNEY_SCHEMA = ROOT / "schemas" / "athena-fresh-work-journey-receipt-v1.schema.json"
REPOSITORY = "Jktomy/atlas-prime"
MAX_RECEIPT_BYTES = 16_384
MAX_ORIGIN_LIFETIME_SECONDS = 900

BRIDGE_MUTATION = {
    "git_tree": False,
    "commit": False,
    "branch": False,
    "push": False,
    "pull_request": False,
    "ready": False,
    "merge": False,
    "cleanup": False,
    "settings": False,
    "second_writer": False,
}
FORBIDDEN_ACTIONS = {
    "direct_main": False,
    "force_push": False,
    "ready": False,
    "merge": False,
    "cleanup": False,
    "settings": False,
    "standing_authority": False,
    "second_writer": False,
}
VERIFICATION_FIELDS = (
    "origin_receipt_sha256",
    "verification_method",
    "verification_evidence_sha256",
    "task_identity_sha256",
    "origin_nonce_sha256",
    "mission_id",
    "base_sha",
    "carrier_sha256",
    "preview_sha256",
    "workflow_blob_sha",
)


class FreshWorkBridgeError(RuntimeError):
    def __init__(self, message: str, code: str) -> None:
        super().__init__(message)
        self.code = code


class OriginReadback(Protocol):
    def __call__(
        self,
        receipt: dict[str, Any],
        origin_receipt_sha256: str,
    ) -> dict[str, Any]:
        """Return independently obtained, full-binding origin readback."""


def _canonical_json(
    path: Path,
    schema_path: Path,
    *,
    maximum: int = MAX_RECEIPT_BYTES,
) -> tuple[dict[str, Any], bytes]:
    try:
        if path.is_symlink() or not path.is_file():
            raise OSError("not a regular file")
        raw = path.read_bytes()
        if not raw or len(raw) > maximum:
            raise OSError("receipt size rejected")
        value = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise FreshWorkBridgeError(
            "fresh Work receipt is unreadable",
            "FRESH_WORK_RECEIPT_INVALID",
        ) from exc
    if not isinstance(value, dict) or raw != stable_json(value).encode("utf-8"):
        raise FreshWorkBridgeError(
            "fresh Work receipt is not canonical",
            "FRESH_WORK_RECEIPT_INVALID",
        )
    try:
        validate_schema(load_schema(schema_path), value)
    except Exception as exc:
        raise FreshWorkBridgeError(
            "fresh Work receipt schema rejected",
            "FRESH_WORK_RECEIPT_INVALID",
        ) from exc
    return value, raw


def _parse_time(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise FreshWorkBridgeError(
            "fresh Work timestamp is invalid",
            "FRESH_WORK_TIME_INVALID",
        ) from exc
    if parsed.tzinfo is None:
        raise FreshWorkBridgeError(
            "fresh Work timestamp lacks timezone",
            "FRESH_WORK_TIME_INVALID",
        )
    return parsed.astimezone(timezone.utc)


def _verify_time_window(receipt: dict[str, Any], now: datetime) -> None:
    issued = _parse_time(receipt["issued_at"])
    expires = _parse_time(receipt["expires_at"])
    observed = now.astimezone(timezone.utc)
    if (
        expires <= issued
        or (expires - issued).total_seconds() > MAX_ORIGIN_LIFETIME_SECONDS
    ):
        raise FreshWorkBridgeError(
            "fresh Work receipt lifetime rejected",
            "FRESH_WORK_TIME_INVALID",
        )
    if observed < issued or observed > expires:
        raise FreshWorkBridgeError(
            "fresh Work receipt is stale or not yet valid",
            "FRESH_WORK_RECEIPT_STALE",
        )


def _assert_external(path: Path, label: str) -> None:
    resolved = path.resolve()
    try:
        resolved.relative_to(ROOT.resolve())
    except ValueError:
        return
    raise FreshWorkBridgeError(
        f"{label} must remain outside canonical Prime source",
        "FRESH_WORK_PRIVATE_BOUNDARY_REJECTED",
    )


def _read_bound_inputs(
    origin_receipt_path: Path,
    preview_path: Path,
    carrier_path: Path,
    *,
    confirmed_preview_sha256: str,
) -> tuple[dict[str, Any], str]:
    for path, label in (
        (origin_receipt_path, "origin receipt"),
        (preview_path, "Preview receipt"),
        (carrier_path, "carrier"),
    ):
        _assert_external(path, label)

    origin, origin_raw = _canonical_json(origin_receipt_path, ORIGIN_SCHEMA)
    try:
        if preview_path.is_symlink() or not preview_path.is_file():
            raise OSError("Preview is not a regular file")
        if carrier_path.is_symlink() or not carrier_path.is_file():
            raise OSError("carrier is not a regular file")
        preview_raw = preview_path.read_bytes()
        preview = json.loads(preview_raw.decode("utf-8"))
        carrier_sha = sha256_bytes(carrier_path.read_bytes())
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise FreshWorkBridgeError(
            "fresh Work bound input is invalid",
            "FRESH_WORK_BOUND_INPUT_INVALID",
        ) from exc
    if not isinstance(preview, dict):
        raise FreshWorkBridgeError(
            "fresh Work Preview is not an object",
            "FRESH_WORK_BOUND_INPUT_INVALID",
        )

    observed_preview_sha = sha256_bytes(preview_raw)
    bindings = {
        "preview_sha256": observed_preview_sha,
        "carrier_sha256": carrier_sha,
        "mission_id": preview.get("mission_id"),
        "base_sha": preview.get("canonical_main_sha"),
        "workflow_blob_sha": preview.get("workflow_blob_sha"),
    }
    for field, observed in bindings.items():
        if origin.get(field) != observed:
            raise FreshWorkBridgeError(
                "fresh Work origin binding mismatch",
                "FRESH_WORK_BINDING_MISMATCH",
            )
    if confirmed_preview_sha256 != observed_preview_sha:
        raise FreshWorkBridgeError(
            "exact Preview confirmation is required",
            "PREVIEW_CONFIRMATION_MISMATCH",
        )
    return origin, sha256_bytes(origin_raw)


def _expected_readback(
    origin: dict[str, Any],
    origin_receipt_sha256: str,
) -> dict[str, Any]:
    return {
        "verified": True,
        "origin_receipt_sha256": origin_receipt_sha256,
        "verification_method": origin["verification_method"],
        "verification_evidence_sha256": origin["verification_evidence_sha256"],
        "task_identity_sha256": origin["task_identity_sha256"],
        "origin_nonce_sha256": origin["origin_nonce_sha256"],
        "mission_id": origin["mission_id"],
        "base_sha": origin["base_sha"],
        "carrier_sha256": origin["carrier_sha256"],
        "preview_sha256": origin["preview_sha256"],
        "workflow_blob_sha": origin["workflow_blob_sha"],
    }


def build_verified_dispatch_plan(
    origin_receipt_path: Path,
    preview_path: Path,
    carrier_path: Path,
    *,
    confirmed_preview_sha256: str,
    readback: OriginReadback | None,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Build a read-only, non-executable binding plan.

    This construction contains no workflow-dispatch or repository-mutation path.
    A later protected integration must supply a platform trust anchor and
    separately wire an accepted plan to the existing guided Execute route.
    """
    origin, origin_sha = _read_bound_inputs(
        origin_receipt_path,
        preview_path,
        carrier_path,
        confirmed_preview_sha256=confirmed_preview_sha256,
    )
    _verify_time_window(origin, now or datetime.now(timezone.utc))
    if readback is None:
        raise FreshWorkBridgeError(
            "no independently trusted Work-origin readback is available",
            "TRUSTED_ORIGIN_VERIFIER_UNAVAILABLE",
        )
    try:
        observed = readback(origin, origin_sha)
    except Exception as exc:
        raise FreshWorkBridgeError(
            "trusted Work-origin readback failed",
            "TRUSTED_ORIGIN_VERIFICATION_FAILED",
        ) from exc
    expected = _expected_readback(origin, origin_sha)
    if not isinstance(observed, dict) or set(observed) != set(expected):
        raise FreshWorkBridgeError(
            "trusted Work-origin readback is incomplete",
            "TRUSTED_ORIGIN_VERIFICATION_FAILED",
        )
    if any(observed.get(field) != value for field, value in expected.items()):
        raise FreshWorkBridgeError(
            "trusted Work-origin readback does not match the bound receipt",
            "TRUSTED_ORIGIN_VERIFICATION_MISMATCH",
        )
    return {
        "schema_version": "atlas.athena.fresh-work-dispatch-plan.v1",
        "state": "READ_ONLY_CANDIDATE_NOT_EXECUTABLE",
        "repository": REPOSITORY,
        "authorizer": "Jayson",
        "semantic_invoker": "Athena",
        "originating_surface": "CHATGPT_WORK",
        **{field: expected[field] for field in VERIFICATION_FIELDS},
        "remote_dispatch_authority": False,
        "guided_execute_invoked": False,
        "bridge_mutation": dict(BRIDGE_MUTATION),
        "forbidden_actions": dict(FORBIDDEN_ACTIONS),
        "next_gate": (
            "SEPARATE_PROTECTED_PLATFORM_TRUST_INTEGRATION_AND_LIVE_PREVIEW"
        ),
    }


def _journey_base(origin: dict[str, Any], origin_sha256: str) -> dict[str, Any]:
    return {
        "schema_version": "atlas.athena.fresh-work-journey-receipt.v1",
        "repository": REPOSITORY,
        "authorizer": "Jayson",
        "semantic_invoker": "Athena",
        "originating_surface": "CHATGPT_WORK",
        "origin_receipt_sha256": origin_sha256,
        "verification_method": origin["verification_method"],
        "verification_evidence_sha256": origin["verification_evidence_sha256"],
        "task_identity_sha256": origin["task_identity_sha256"],
        "origin_nonce_sha256": origin["origin_nonce_sha256"],
        "preview_sha256": origin["preview_sha256"],
        "carrier_sha256": origin["carrier_sha256"],
        "mission_id": origin["mission_id"],
        "canonical_main_sha": origin["base_sha"],
        "workflow_blob_sha": origin["workflow_blob_sha"],
        "bridge_mutation": dict(BRIDGE_MUTATION),
        "forbidden_actions": dict(FORBIDDEN_ACTIONS),
    }


def _blocked(base: dict[str, Any], *, code: str) -> dict[str, Any]:
    return base | {
        "result": "BLOCKED",
        "guided_execute_receipt_sha256": None,
        "workflow_run_id": None,
        "workflow_run_url": None,
        "workflow_run_head_sha": None,
        "stage": "ORIGIN_VERIFICATION",
        "error_code": code,
        "stop_point": "PRE_DISPATCH_BLOCKED",
        "remote_dispatch_possible": False,
        "rollback": "NO_REMOTE_MUTATION",
    }


def _reserve_blocked(path: Path, value: dict[str, Any]) -> None:
    _assert_external(path, "journey receipt")
    try:
        validate_schema(load_schema(JOURNEY_SCHEMA), value)
        payload = stable_json(value).encode("utf-8")
    except Exception as exc:
        raise FreshWorkBridgeError(
            "fresh Work blocked receipt construction failed",
            "FRESH_WORK_JOURNEY_RECEIPT_INVALID",
        ) from exc
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("xb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
    except FileExistsError as exc:
        raise FreshWorkBridgeError(
            "fresh Work journey receipt path already exists",
            "FRESH_WORK_JOURNEY_RECEIPT_EXISTS",
        ) from exc
    except OSError as exc:
        raise FreshWorkBridgeError(
            "fresh Work journey receipt sink is unavailable",
            "FRESH_WORK_JOURNEY_RECEIPT_UNAVAILABLE",
        ) from exc


def build_unavailable_receipt(
    origin_receipt_path: Path,
    preview_path: Path,
    carrier_path: Path,
    journey_receipt_path: Path,
    *,
    confirmed_preview_sha256: str,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Record the current construction's truthful no-verifier boundary."""
    origin, origin_sha = _read_bound_inputs(
        origin_receipt_path,
        preview_path,
        carrier_path,
        confirmed_preview_sha256=confirmed_preview_sha256,
    )
    base = _journey_base(origin, origin_sha)
    try:
        _verify_time_window(origin, now or datetime.now(timezone.utc))
        code = "TRUSTED_ORIGIN_VERIFIER_UNAVAILABLE"
    except FreshWorkBridgeError as exc:
        code = exc.code
    receipt = _blocked(base, code=code)
    _reserve_blocked(journey_receipt_path, receipt)
    return receipt


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Read-only fresh Work/Athena origin construction boundary; "
            "no workflow dispatch is implemented"
        )
    )
    parser.add_argument("--origin-receipt", required=True, type=Path)
    parser.add_argument("--preview", required=True, type=Path)
    parser.add_argument("--carrier", required=True, type=Path)
    parser.add_argument("--journey-receipt", required=True, type=Path)
    parser.add_argument("--confirm-preview-sha256", required=True)
    args = parser.parse_args(argv)

    try:
        receipt = build_unavailable_receipt(
            args.origin_receipt.resolve(),
            args.preview.resolve(),
            args.carrier.resolve(),
            args.journey_receipt.resolve(),
            confirmed_preview_sha256=args.confirm_preview_sha256,
        )
    except FreshWorkBridgeError as exc:
        sys.stderr.write(f"Fresh Work bridge stopped safely: {exc.code}\n")
        return 2
    sys.stdout.write(stable_json({
        "result": receipt["result"],
        "mission_id": receipt["mission_id"],
        "origin_receipt_sha256": receipt["origin_receipt_sha256"],
        "stop_point": receipt["stop_point"],
        "error_code": receipt["error_code"],
    }))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
