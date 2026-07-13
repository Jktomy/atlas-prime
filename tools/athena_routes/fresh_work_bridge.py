from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Protocol

from .guided_publisher import GuidedPublisherError, execute_preview
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


class FreshWorkBridgeError(RuntimeError):
    def __init__(self, message: str, code: str) -> None:
        super().__init__(message)
        self.code = code


class OriginVerifier(Protocol):
    def __call__(self, receipt: dict[str, Any]) -> dict[str, Any]:
        """Return a trusted, independently obtained verification result."""


Runner = Callable[..., Any]


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
    if expires <= issued or (expires - issued).total_seconds() > MAX_ORIGIN_LIFETIME_SECONDS:
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


def _verify_origin(
    receipt: dict[str, Any],
    *,
    verifier: OriginVerifier | None,
    now: datetime,
) -> dict[str, Any]:
    _verify_time_window(receipt, now)
    if verifier is None:
        raise FreshWorkBridgeError(
            "no independently trusted Work-origin verifier is available",
            "TRUSTED_ORIGIN_VERIFIER_UNAVAILABLE",
        )
    try:
        result = verifier(receipt)
    except Exception as exc:
        raise FreshWorkBridgeError(
            "trusted Work-origin verification failed",
            "TRUSTED_ORIGIN_VERIFICATION_FAILED",
        ) from exc
    expected_keys = {
        "verified",
        "verification_method",
        "verification_evidence_sha256",
        "task_identity_sha256",
        "origin_nonce_sha256",
    }
    if not isinstance(result, dict) or set(result) != expected_keys or result.get("verified") is not True:
        raise FreshWorkBridgeError(
            "trusted Work-origin verification was not affirmative",
            "TRUSTED_ORIGIN_VERIFICATION_FAILED",
        )
    for field in (
        "verification_method",
        "verification_evidence_sha256",
        "task_identity_sha256",
        "origin_nonce_sha256",
    ):
        if result.get(field) != receipt.get(field):
            raise FreshWorkBridgeError(
                "trusted Work-origin verification did not match the submitted receipt",
                "TRUSTED_ORIGIN_VERIFICATION_MISMATCH",
            )
    return result


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


def _validated_journey(value: dict[str, Any]) -> dict[str, Any]:
    try:
        validate_schema(load_schema(JOURNEY_SCHEMA), value)
    except Exception as exc:
        raise FreshWorkBridgeError(
            "fresh Work journey receipt construction failed",
            "FRESH_WORK_JOURNEY_RECEIPT_INVALID",
        ) from exc
    return value


def _reserve_json(path: Path, value: dict[str, Any]) -> None:
    payload = stable_json(_validated_journey(value)).encode("utf-8")
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


def _replace_json(path: Path, value: dict[str, Any]) -> None:
    payload = stable_json(_validated_journey(value)).encode("utf-8")
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as stream:
            temporary = Path(stream.name)
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except OSError as exc:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
        raise FreshWorkBridgeError(
            "fresh Work journey finalization failed; preserved intent receipt governs",
            "FRESH_WORK_JOURNEY_FINALIZE_FAILED",
        ) from exc


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


def execute_fresh_work(
    origin_receipt_path: Path,
    preview_path: Path,
    carrier_path: Path,
    journey_receipt_path: Path,
    guided_execute_receipt_path: Path,
    *,
    confirmed_preview_sha256: str,
    launch_nonce: str,
    public_clean_confirmation: str,
    verifier: OriginVerifier | None,
    now: datetime | None = None,
    runner: Runner | None = None,
    package_reader: Callable[[Path, str], Any] | None = None,
    compiler: Callable[..., dict[str, Any]] | None = None,
) -> dict[str, Any]:
    for path, label in (
        (origin_receipt_path, "origin receipt"),
        (preview_path, "Preview receipt"),
        (carrier_path, "carrier"),
        (journey_receipt_path, "journey receipt"),
        (guided_execute_receipt_path, "guided Execute receipt"),
    ):
        _assert_external(path, label)

    origin, origin_raw = _canonical_json(origin_receipt_path, ORIGIN_SCHEMA)
    origin_sha = sha256_bytes(origin_raw)
    base = _journey_base(origin, origin_sha)

    try:
        preview_raw = preview_path.read_bytes()
        preview = json.loads(preview_raw.decode("utf-8"))
        carrier_sha = sha256_bytes(carrier_path.read_bytes())
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        blocked = _blocked(base, code="FRESH_WORK_BOUND_INPUT_INVALID")
        _reserve_json(journey_receipt_path, blocked)
        return blocked

    observed_preview_sha = sha256_bytes(preview_raw)
    bindings = {
        "preview_sha256": observed_preview_sha,
        "carrier_sha256": carrier_sha,
        "mission_id": preview.get("mission_id") if isinstance(preview, dict) else None,
        "base_sha": preview.get("canonical_main_sha") if isinstance(preview, dict) else None,
        "workflow_blob_sha": preview.get("workflow_blob_sha") if isinstance(preview, dict) else None,
    }
    for field, observed in bindings.items():
        if origin.get(field) != observed:
            blocked = _blocked(base, code="FRESH_WORK_BINDING_MISMATCH")
            _reserve_json(journey_receipt_path, blocked)
            return blocked
    if confirmed_preview_sha256 != observed_preview_sha:
        blocked = _blocked(base, code="PREVIEW_CONFIRMATION_MISMATCH")
        _reserve_json(journey_receipt_path, blocked)
        return blocked

    try:
        _verify_origin(
            origin,
            verifier=verifier,
            now=now or datetime.now(timezone.utc),
        )
    except FreshWorkBridgeError as exc:
        blocked = _blocked(base, code=exc.code)
        _reserve_json(journey_receipt_path, blocked)
        return blocked

    intent = base | {
        "result": "PARTIAL",
        "guided_execute_receipt_sha256": None,
        "workflow_run_id": None,
        "workflow_run_url": None,
        "workflow_run_head_sha": None,
        "stage": "PARTIAL_STATE_PRESERVED",
        "error_code": "FRESH_WORK_DISPATCH_INTENT_JOURNALED",
        "stop_point": "PARTIAL_STATE_PRESERVED",
        "remote_dispatch_possible": True,
        "rollback": "PRESERVE_AND_REVIEW_NO_RETRY",
    }
    _reserve_json(journey_receipt_path, intent)

    kwargs: dict[str, Any] = {
        "confirmed_preview_sha256": confirmed_preview_sha256,
        "launch_nonce": launch_nonce,
        "public_clean_confirmation": public_clean_confirmation,
        "runner": runner,
        "package_reader": package_reader,
        "compiler": compiler,
    }
    if runner is None:
        kwargs.pop("runner")
    if package_reader is None:
        kwargs.pop("package_reader")
    if compiler is None:
        kwargs.pop("compiler")

    try:
        guided = execute_preview(
            preview_path,
            carrier_path,
            guided_execute_receipt_path,
            **kwargs,
        )
    except GuidedPublisherError as exc:
        blocked = _blocked(base, code=exc.code)
        _replace_json(journey_receipt_path, blocked)
        return blocked

    guided_digest = sha256_bytes(guided_execute_receipt_path.read_bytes())
    if guided.get("result") == "DISPATCHED":
        final = base | {
            "result": "DISPATCHED",
            "guided_execute_receipt_sha256": guided_digest,
            "workflow_run_id": guided.get("workflow_run_id"),
            "workflow_run_url": guided.get("workflow_run_url"),
            "workflow_run_head_sha": guided.get("workflow_run_head_sha"),
            "stage": "GUIDED_DISPATCH_READBACK",
            "error_code": None,
            "stop_point": "HOSTED_WORKFLOW_DISPATCH_READBACK",
            "remote_dispatch_possible": True,
            "rollback": "HOSTED_ROUTE_RECEIPT_GOVERNS",
        }
    else:
        final = base | {
            "result": "PARTIAL",
            "guided_execute_receipt_sha256": guided_digest,
            "workflow_run_id": guided.get("workflow_run_id"),
            "workflow_run_url": guided.get("workflow_run_url"),
            "workflow_run_head_sha": guided.get("workflow_run_head_sha"),
            "stage": "PARTIAL_STATE_PRESERVED",
            "error_code": guided.get("error_code") or "GUIDED_DISPATCH_PARTIAL",
            "stop_point": "PARTIAL_STATE_PRESERVED",
            "remote_dispatch_possible": True,
            "rollback": "PRESERVE_AND_REVIEW_NO_RETRY",
        }
    _replace_json(journey_receipt_path, final)
    return _validated_journey(final)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Fail-closed fresh Work/Athena origin bridge over the existing "
            "guided publisher"
        )
    )
    parser.add_argument("--origin-receipt", required=True, type=Path)
    parser.add_argument("--preview", required=True, type=Path)
    parser.add_argument("--carrier", required=True, type=Path)
    parser.add_argument("--journey-receipt", required=True, type=Path)
    parser.add_argument("--guided-execute-receipt", required=True, type=Path)
    parser.add_argument("--confirm-preview-sha256", required=True)
    parser.add_argument("--launch-nonce", required=True)
    parser.add_argument(
        "--public-clean-confirmation",
        required=True,
        choices=["PUBLIC_CLEAN_CONFIRMED"],
    )
    args = parser.parse_args(argv)

    receipt = execute_fresh_work(
        args.origin_receipt.resolve(),
        args.preview.resolve(),
        args.carrier.resolve(),
        args.journey_receipt.resolve(),
        args.guided_execute_receipt.resolve(),
        confirmed_preview_sha256=args.confirm_preview_sha256,
        launch_nonce=args.launch_nonce,
        public_clean_confirmation=args.public_clean_confirmation,
        verifier=None,
    )
    sys.stdout.write(stable_json({
        "result": receipt["result"],
        "mission_id": receipt["mission_id"],
        "origin_receipt_sha256": receipt["origin_receipt_sha256"],
        "stop_point": receipt["stop_point"],
        "error_code": receipt["error_code"],
    }))
    return 0 if receipt["result"] == "DISPATCHED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
