from __future__ import annotations

import argparse
import base64
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Callable
from urllib.parse import quote

from .hosted import (
    MAX_CARRIER_BYTES,
    OWNER,
    REPOSITORY,
    HostedRouteError,
    _engine_imports,
    classify_paths,
    expected_mission_branch,
    load_schema,
    mission_lock_sha256,
    privacy_scan,
    sha256_bytes,
    stable_json,
    write_json,
)
from .schema import SchemaValidationError, validate_schema


ROOT = Path(__file__).resolve().parents[2]
PREVIEW_SCHEMA = ROOT / "schemas" / "athena-guided-intake-preview-v1.schema.json"
EXECUTE_SCHEMA = ROOT / "schemas" / "athena-guided-intake-execute-receipt-v1.schema.json"
WORKFLOW = "athena-bow-hosted.yml"
WORKFLOW_PATH = ".github/workflows/athena-bow-hosted.yml"
WORKFLOW_REF = f"{REPOSITORY}/{WORKFLOW_PATH}@refs/heads/main"
REMOTE_URL = f"https://github.com/{REPOSITORY}.git"
SHA40 = re.compile(r"^[a-f0-9]{40}$")
SHA64 = re.compile(r"^[a-f0-9]{64}$")
RUN_URL = re.compile(r"^https://github[.]com/Jktomy/atlas-prime/actions/runs/([0-9]+)$")
LAUNCH_NONCE = re.compile(r"^[A-Za-z0-9._:-]{24,200}$")


class GuidedPublisherError(RuntimeError):
    def __init__(self, message: str, code: str) -> None:
        super().__init__(message)
        self.code = code


Runner = Callable[..., subprocess.CompletedProcess[str]]


FORBIDDEN_ACTIONS = {
    "adapter_invocation": False,
    "branch_write": False,
    "direct_main": False,
    "force_push": False,
    "merge": False,
    "pr_write": False,
    "ready": False,
    "repository_settings": False,
    "second_writer": False,
    "standing_authority": False,
}


def _run(runner: Runner, args: list[str], *, input_text: str | None = None) -> str:
    completed = runner(
        args,
        check=False,
        capture_output=True,
        text=True,
        input=input_text,
    )
    if completed.returncode != 0:
        raise GuidedPublisherError("guided publisher GitHub readback failed", "GITHUB_READBACK_FAILED")
    return completed.stdout.strip()


def _read_live_identity(runner: Runner) -> tuple[str, str]:
    main_sha = _run(runner, ["gh", "api", f"repos/{REPOSITORY}/commits/main", "--jq", ".sha"])
    workflow_sha = _run(
        runner,
        ["gh", "api", f"repos/{REPOSITORY}/contents/{WORKFLOW_PATH}?ref={main_sha}", "--jq", ".sha"],
    )
    if not SHA40.fullmatch(main_sha) or not SHA40.fullmatch(workflow_sha):
        raise GuidedPublisherError("canonical GitHub identity is malformed", "GITHUB_IDENTITY_INVALID")
    return main_sha, workflow_sha


def _assert_no_replay(runner: Runner, branch: str) -> None:
    ref = runner(
        ["gh", "api", f"repos/{REPOSITORY}/git/ref/heads/{quote(branch, safe='')}"],
        check=False,
        capture_output=True,
        text=True,
        input=None,
    )
    if ref.returncode == 0:
        raise GuidedPublisherError("guided mission branch already exists", "REPLAY_BRANCH_EXISTS")
    if "404" not in ref.stderr and "Not Found" not in ref.stderr:
        raise GuidedPublisherError("guided branch replay readback failed", "REPLAY_READBACK_FAILED")
    raw_prs = _run(
        runner,
        ["gh", "pr", "list", "--repo", REPOSITORY, "--state", "all", "--head", branch, "--json", "number,state"],
    )
    try:
        prs = json.loads(raw_prs)
    except json.JSONDecodeError as exc:
        raise GuidedPublisherError("guided PR replay readback failed", "REPLAY_READBACK_FAILED") from exc
    if not isinstance(prs, list):
        raise GuidedPublisherError("guided PR replay readback failed", "REPLAY_READBACK_FAILED")
    if prs:
        raise GuidedPublisherError("guided mission PR already exists", "REPLAY_PR_EXISTS")


def _load_preview(path: Path) -> tuple[dict[str, Any], str]:
    try:
        raw = path.read_bytes()
        value = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise GuidedPublisherError("guided Preview receipt is unreadable", "PREVIEW_RECEIPT_INVALID") from exc
    if not isinstance(value, dict) or raw != stable_json(value).encode("utf-8"):
        raise GuidedPublisherError("guided Preview receipt is not canonical", "PREVIEW_RECEIPT_INVALID")
    try:
        validate_schema(load_schema(PREVIEW_SCHEMA), value)
    except (HostedRouteError, SchemaValidationError) as exc:
        raise GuidedPublisherError("guided Preview receipt schema rejected", "PREVIEW_RECEIPT_INVALID") from exc
    return value, sha256_bytes(raw)


def _validated_execute_receipt(value: dict[str, Any]) -> dict[str, Any]:
    try:
        validate_schema(load_schema(EXECUTE_SCHEMA), value)
    except (HostedRouteError, SchemaValidationError) as exc:
        raise GuidedPublisherError("guided Execute receipt construction failed", "EXECUTE_RECEIPT_INVALID") from exc
    return value


def _reserve_receipt(path: Path, value: dict[str, Any]) -> None:
    payload = stable_json(_validated_execute_receipt(value)).encode("utf-8")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("xb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
    except FileExistsError as exc:
        raise GuidedPublisherError("guided Execute receipt path already exists", "EXECUTE_RECEIPT_EXISTS") from exc
    except OSError as exc:
        raise GuidedPublisherError("guided Execute receipt sink is unavailable", "EXECUTE_RECEIPT_UNAVAILABLE") from exc


def _replace_receipt(path: Path, value: dict[str, Any]) -> None:
    payload = stable_json(_validated_execute_receipt(value)).encode("utf-8")
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp", delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except OSError as exc:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
        raise GuidedPublisherError(
            "guided Execute receipt finalization failed; preserved intent receipt governs",
            "EXECUTE_RECEIPT_FINALIZE_FAILED",
        ) from exc


def build_preview(
    carrier_path: Path,
    *,
    runner: Runner = subprocess.run,
    package_reader: Callable[[Path, str], Any] | None = None,
    compiler: Callable[..., dict[str, Any]] | None = None,
) -> dict[str, Any]:
    try:
        carrier = carrier_path.read_bytes()
    except OSError as exc:
        raise GuidedPublisherError("guided carrier is unavailable", "CARRIER_UNAVAILABLE") from exc
    if not carrier or len(carrier) > MAX_CARRIER_BYTES:
        raise GuidedPublisherError("guided carrier size rejected", "CARRIER_SIZE_REJECTED")
    carrier_sha = sha256_bytes(carrier)
    if package_reader is None or compiler is None:
        _adapter_error, _execute_mission, imported_compiler, imported_reader = _engine_imports()
        package_reader = package_reader or imported_reader
        compiler = compiler or imported_compiler
    try:
        package = package_reader(carrier_path, carrier_sha)
        privacy_scan(package)
    except Exception as exc:
        code = str(getattr(exc, "code", "CARRIER_AUDIT_REJECTED"))
        raise GuidedPublisherError("guided carrier audit rejected", code) from exc
    threads = package.weave.get("threads")
    if not isinstance(threads, list) or not threads:
        raise GuidedPublisherError("guided carrier has no authored paths", "GUIDED_PATHS_REJECTED")
    paths = [item.get("path") for item in threads if isinstance(item, dict)]
    if len(paths) != len(threads) or not all(isinstance(path, str) for path in paths):
        raise GuidedPublisherError("guided carrier path inventory is malformed", "GUIDED_PATHS_REJECTED")
    classification, _route = classify_paths(paths)
    if classification != "ORDINARY":
        raise GuidedPublisherError("guided carrier is outside the ordinary route", classification)
    main_sha, workflow_blob_sha = _read_live_identity(runner)
    if package.weave.get("base_sha") != main_sha:
        raise GuidedPublisherError("guided carrier base is not canonical main", "STALE_BASE")
    expected_branch = expected_mission_branch(package.weave.get("weave_id", ""), main_sha)
    if package.weave.get("branch") != expected_branch:
        raise GuidedPublisherError("guided carrier branch is not deterministic", "GUIDED_BRANCH_MISMATCH")
    _assert_no_replay(runner, expected_branch)
    with tempfile.TemporaryDirectory(prefix="atlas-guided-preview-") as temporary:
        try:
            compile_receipt = compiler(
                carrier_path,
                package_sha256=carrier_sha,
                output_dir=Path(temporary) / "compiled",
                disabled_proof=True,
                compile_only=True,
                read_only_remote_url=REMOTE_URL,
            )
        except Exception as exc:
            code = str(getattr(exc, "code", "GUIDED_COMPILE_REJECTED"))
            raise GuidedPublisherError("guided carrier compile rejected", code) from exc
    inventory: list[dict[str, str]] = []
    for thread in threads:
        operation = thread.get("operation")
        payload_name = thread.get("payload")
        if operation not in {"ADD", "REPLACE"} or not isinstance(payload_name, str):
            raise GuidedPublisherError("guided publisher accepts ADD and REPLACE payloads only", "GUIDED_OPERATION_REJECTED")
        payload = package.payloads.get(f"PAYLOADS/{payload_name}")
        if not isinstance(payload, bytes):
            raise GuidedPublisherError("guided payload inventory is incomplete", "GUIDED_PAYLOAD_REJECTED")
        inventory.append({
            "operation": operation,
            "path": thread["path"],
            "payload_sha256": sha256_bytes(payload),
        })
    inventory.sort(key=lambda item: item["path"])
    preview = {
        "schema_version": "atlas.athena.guided-intake-preview.v1",
        "result": "ACCEPTED",
        "repository": REPOSITORY,
        "canonical_main_sha": main_sha,
        "workflow_ref": WORKFLOW_REF,
        "workflow_blob_sha": workflow_blob_sha,
        "carrier_sha256": carrier_sha,
        "manifest_sha256": package.manifest_sha256,
        "weave_sha256": package.weave_sha256,
        "mission_id": package.weave["weave_id"],
        "mission_sha256": compile_receipt["mission_sha256"],
        "mission_lock_sha256": mission_lock_sha256(package.weave["weave_id"], main_sha),
        "output_mission_sha256": compile_receipt["output_mission_sha256"],
        "deterministic_branch": package.weave["branch"],
        "path_classification": "ORDINARY",
        "paths": inventory,
        "public_clean": True,
        "stop_point": "PREVIEW_COMPLETE",
        "rollback": "NO_REMOTE_MUTATION",
        "forbidden_actions": dict(FORBIDDEN_ACTIONS),
    }
    try:
        validate_schema(load_schema(PREVIEW_SCHEMA), preview)
    except (HostedRouteError, SchemaValidationError) as exc:
        raise GuidedPublisherError("guided Preview receipt construction failed", "PREVIEW_RECEIPT_INVALID") from exc
    return preview


def execute_preview(
    preview_path: Path,
    carrier_path: Path,
    receipt_path: Path,
    *,
    confirmed_preview_sha256: str,
    launch_nonce: str,
    public_clean_confirmation: str,
    runner: Runner = subprocess.run,
    package_reader: Callable[[Path, str], Any] | None = None,
    compiler: Callable[..., dict[str, Any]] | None = None,
) -> dict[str, Any]:
    preview, observed_preview_sha = _load_preview(preview_path)
    if not SHA64.fullmatch(confirmed_preview_sha256) or confirmed_preview_sha256 != observed_preview_sha:
        raise GuidedPublisherError("exact guided Preview confirmation is required", "PREVIEW_CONFIRMATION_MISMATCH")
    if not isinstance(launch_nonce, str) or LAUNCH_NONCE.fullmatch(launch_nonce) is None:
        raise GuidedPublisherError("guided launch nonce length rejected", "LAUNCH_NONCE_REJECTED")
    if public_clean_confirmation != "PUBLIC_CLEAN_CONFIRMED":
        raise GuidedPublisherError("explicit public-clean confirmation is required", "PRE_INGRESS_PRIVACY_REQUIRED")
    rebuilt = build_preview(
        carrier_path,
        runner=runner,
        package_reader=package_reader,
        compiler=compiler,
    )
    if rebuilt != preview:
        raise GuidedPublisherError("guided Preview or carrier drifted", "PREVIEW_DRIFT")
    actor = _run(runner, ["gh", "api", "user", "--jq", ".login"])
    if actor != OWNER:
        raise GuidedPublisherError("repository owner session required", "OWNER_IDENTITY_REJECTED")
    carrier = carrier_path.read_bytes()
    if sha256_bytes(carrier) != preview["carrier_sha256"]:
        raise GuidedPublisherError("guided carrier changed before dispatch", "PREVIEW_DRIFT")
    dispatch = {
        "arrow_b64": base64.b64encode(carrier).decode("ascii"),
        "arrow_sha256": preview["carrier_sha256"],
        "mission_lock_sha256": preview["mission_lock_sha256"],
        "public_clean_confirmation": "PUBLIC_CLEAN_CONFIRMED",
    }
    common = {
        "schema_version": "atlas.athena.guided-intake-execute-receipt.v1",
        "repository": REPOSITORY,
        "preview_sha256": observed_preview_sha,
        "carrier_sha256": preview["carrier_sha256"],
        "mission_id": preview["mission_id"],
        "mission_sha256": preview["mission_sha256"],
        "mission_lock_sha256": preview["mission_lock_sha256"],
        "canonical_main_sha": preview["canonical_main_sha"],
        "workflow_ref": preview["workflow_ref"],
        "workflow_blob_sha": preview["workflow_blob_sha"],
        "launch_nonce_sha256": sha256_bytes(launch_nonce.encode("utf-8")),
        "public_clean_confirmation": public_clean_confirmation,
        "dispatch_transport": "GH_WORKFLOW_JSON_STDIN",
        "workflow_run_id": None,
        "workflow_run_url": None,
        "workflow_run_head_sha": None,
        "forbidden_actions": dict(FORBIDDEN_ACTIONS),
    }
    intent = common | {
        "result": "PARTIAL",
        "error_code": "DISPATCH_INTENT_JOURNALED",
        "stop_point": "PARTIAL_STATE_PRESERVED",
        "rollback": "PRESERVE_AND_REVIEW_NO_RETRY",
    }
    _reserve_receipt(receipt_path, intent)
    try:
        dispatch_call = runner(
            ["gh", "workflow", "run", WORKFLOW, "--repo", REPOSITORY, "--ref", "main", "--json"],
            check=False,
            capture_output=True,
            text=True,
            input=json.dumps(dispatch, sort_keys=True, separators=(",", ":")),
        )
    except Exception:
        receipt = common | {
            "result": "PARTIAL",
            "error_code": "DISPATCH_TRANSPORT_AMBIGUOUS",
            "stop_point": "PARTIAL_STATE_PRESERVED",
            "rollback": "PRESERVE_AND_REVIEW_NO_RETRY",
        }
        _replace_receipt(receipt_path, receipt)
        return receipt
    output = dispatch_call.stdout.strip()
    match = RUN_URL.fullmatch(output) if dispatch_call.returncode == 0 else None
    run_id = int(match.group(1)) if match is not None else None
    run: dict[str, Any] | None = None
    if run_id is not None:
        try:
            run_readback = runner(
                ["gh", "api", f"repos/{REPOSITORY}/actions/runs/{run_id}"],
                check=False,
                capture_output=True,
                text=True,
                input=None,
            )
        except Exception:
            run_readback = None
        if run_readback is not None and run_readback.returncode == 0:
            try:
                candidate = json.loads(run_readback.stdout)
            except json.JSONDecodeError:
                candidate = None
            if isinstance(candidate, dict):
                run = candidate
    exact_readback = (
        run_id is not None
        and run is not None
        and run.get("id") == run_id
        and run.get("event") == "workflow_dispatch"
        and run.get("head_sha") == preview["canonical_main_sha"]
        and (run.get("actor") or {}).get("login") == OWNER
        and (run.get("triggering_actor") or {}).get("login") == OWNER
    )
    common = common | {
        "workflow_run_id": run_id,
        "workflow_run_url": output if match is not None else None,
        "workflow_run_head_sha": run.get("head_sha") if isinstance(run, dict) and SHA40.fullmatch(str(run.get("head_sha", ""))) else None,
    }
    if exact_readback:
        receipt = common | {
            "result": "DISPATCHED",
            "error_code": None,
            "stop_point": "HOSTED_WORKFLOW_DISPATCH_READBACK",
            "rollback": "HOSTED_ROUTE_RECEIPT_GOVERNS",
        }
    else:
        receipt = common | {
            "result": "PARTIAL",
            "error_code": "DISPATCH_READBACK_FAILED",
            "stop_point": "PARTIAL_STATE_PRESERVED",
            "rollback": "PRESERVE_AND_REVIEW_NO_RETRY",
        }
    _replace_receipt(receipt_path, receipt)
    return receipt


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Owner-guided Preview to hosted Bow publisher")
    subparsers = parser.add_subparsers(dest="command", required=True)
    preview_parser = subparsers.add_parser("preview", help="Audit and compile one carrier without mutation")
    preview_parser.add_argument("--carrier", required=True, type=Path)
    preview_parser.add_argument("--receipt", required=True, type=Path)
    execute_parser = subparsers.add_parser("execute", help="Revalidate one exact Preview and dispatch the existing hosted route")
    execute_parser.add_argument("--carrier", required=True, type=Path)
    execute_parser.add_argument("--preview", required=True, type=Path)
    execute_parser.add_argument("--confirm-preview-sha256", required=True)
    execute_parser.add_argument("--launch-nonce", required=True)
    execute_parser.add_argument("--public-clean-confirmation", required=True, choices=["PUBLIC_CLEAN_CONFIRMED"])
    execute_parser.add_argument("--receipt", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "preview":
            receipt = build_preview(args.carrier.resolve())
            target = args.receipt.resolve()
        else:
            target = args.receipt.resolve()
            receipt = execute_preview(
                args.preview.resolve(),
                args.carrier.resolve(),
                target,
                confirmed_preview_sha256=args.confirm_preview_sha256,
                launch_nonce=args.launch_nonce,
                public_clean_confirmation=args.public_clean_confirmation,
            )
        if args.command == "preview":
            write_json(target, receipt)
    except GuidedPublisherError as exc:
        sys.stderr.write(f"Guided publisher stopped safely: {exc.code}\n")
        return 2
    sys.stdout.write(stable_json({
        "result": receipt["result"],
        "mission_id": receipt["mission_id"],
        "receipt_sha256": sha256_bytes(target.read_bytes()),
        "stop_point": receipt["stop_point"],
    }))
    return 0 if receipt["result"] in {"ACCEPTED", "DISPATCHED"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
