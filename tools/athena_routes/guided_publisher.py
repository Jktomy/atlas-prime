from __future__ import annotations

import argparse
import base64
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Callable

from .hosted import (
    MAX_CARRIER_BYTES,
    OWNER,
    REPOSITORY,
    HostedRouteError,
    _engine_imports,
    classify_paths,
    load_schema,
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
    *,
    confirmed_preview_sha256: str,
    launch_nonce: str,
    runner: Runner = subprocess.run,
    package_reader: Callable[[Path, str], Any] | None = None,
    compiler: Callable[..., dict[str, Any]] | None = None,
) -> dict[str, Any]:
    preview, observed_preview_sha = _load_preview(preview_path)
    if not SHA64.fullmatch(confirmed_preview_sha256) or confirmed_preview_sha256 != observed_preview_sha:
        raise GuidedPublisherError("exact guided Preview confirmation is required", "PREVIEW_CONFIRMATION_MISMATCH")
    if not isinstance(launch_nonce, str) or not 24 <= len(launch_nonce) <= 200:
        raise GuidedPublisherError("guided launch nonce length rejected", "LAUNCH_NONCE_REJECTED")
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
    dispatch = {
        "arrow_b64": base64.b64encode(carrier).decode("ascii"),
        "arrow_sha256": preview["carrier_sha256"],
        "public_clean_confirmation": "PUBLIC_CLEAN_CONFIRMED",
    }
    output = _run(
        runner,
        ["gh", "workflow", "run", WORKFLOW, "--repo", REPOSITORY, "--ref", "main", "--json"],
        input_text=json.dumps(dispatch, sort_keys=True, separators=(",", ":")),
    )
    match = RUN_URL.fullmatch(output)
    if match is None:
        raise GuidedPublisherError("hosted workflow run identity was not returned", "DISPATCH_READBACK_FAILED")
    run_id = int(match.group(1))
    raw_run = _run(runner, ["gh", "api", f"repos/{REPOSITORY}/actions/runs/{run_id}"])
    try:
        run = json.loads(raw_run)
    except json.JSONDecodeError as exc:
        raise GuidedPublisherError("hosted workflow run readback was malformed", "DISPATCH_READBACK_FAILED") from exc
    if (
        not isinstance(run, dict)
        or run.get("id") != run_id
        or run.get("event") != "workflow_dispatch"
        or run.get("head_sha") != preview["canonical_main_sha"]
        or (run.get("actor") or {}).get("login") != OWNER
        or (run.get("triggering_actor") or {}).get("login") != OWNER
    ):
        raise GuidedPublisherError("hosted workflow run identity mismatch", "DISPATCH_READBACK_FAILED")
    receipt = {
        "schema_version": "atlas.athena.guided-intake-execute-receipt.v1",
        "result": "DISPATCHED",
        "repository": REPOSITORY,
        "preview_sha256": observed_preview_sha,
        "carrier_sha256": preview["carrier_sha256"],
        "mission_id": preview["mission_id"],
        "mission_sha256": preview["mission_sha256"],
        "canonical_main_sha": preview["canonical_main_sha"],
        "workflow_ref": preview["workflow_ref"],
        "workflow_blob_sha": preview["workflow_blob_sha"],
        "launch_nonce_sha256": sha256_bytes(launch_nonce.encode("utf-8")),
        "dispatch_transport": "GH_WORKFLOW_JSON_STDIN",
        "workflow_run_id": run_id,
        "workflow_run_url": output,
        "workflow_run_head_sha": run["head_sha"],
        "stop_point": "HOSTED_WORKFLOW_DISPATCH_READBACK",
        "rollback": "HOSTED_ROUTE_RECEIPT_GOVERNS",
        "forbidden_actions": dict(FORBIDDEN_ACTIONS),
    }
    try:
        validate_schema(load_schema(EXECUTE_SCHEMA), receipt)
    except (HostedRouteError, SchemaValidationError) as exc:
        raise GuidedPublisherError("guided Execute receipt construction failed", "EXECUTE_RECEIPT_INVALID") from exc
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
    execute_parser.add_argument("--receipt", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "preview":
            receipt = build_preview(args.carrier.resolve())
            target = args.receipt.resolve()
        else:
            receipt = execute_preview(
                args.preview.resolve(),
                args.carrier.resolve(),
                confirmed_preview_sha256=args.confirm_preview_sha256,
                launch_nonce=args.launch_nonce,
            )
            target = args.receipt.resolve()
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
