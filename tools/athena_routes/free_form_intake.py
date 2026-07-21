from __future__ import annotations

import argparse
import io
import json
import os
import re
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any, Callable

from .guided_publisher import (
    REMOTE_URL,
    WORKFLOW_REF,
    GuidedPublisherError,
    _compiled_output_identity,
    _read_live_identity,
    build_preview,
)
from .hosted import (
    MAX_CARRIER_BYTES,
    REPOSITORY,
    SENSITIVE,
    _engine_imports,
    classify_paths,
    expected_mission_branch,
    load_schema,
    mission_lock_sha256,
    privacy_scan,
    sha256_bytes,
    stable_json,
)
from .schema import SchemaValidationError, validate_schema


ROOT = Path(__file__).resolve().parents[2]
FIELDS_SCHEMA = ROOT / "schemas" / "athena-free-form-mission-fields-v1.schema.json"
RECEIPT_SCHEMA = ROOT / "schemas" / "athena-free-form-intake-receipt-v1.schema.json"
ZIP_EPOCH = (1980, 1, 1, 0, 0, 0)
MAX_CHANGES = 20
MAX_TOTAL_CONTENT_BYTES = 768 * 1024
SAFE_MISSION = re.compile(r"^[A-Z0-9]+(?:-[A-Z0-9]+)*$")


class FreeFormIntakeError(RuntimeError):
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
    "workflow_dispatch": False,
}


def _duplicate_key_rejector(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise FreeFormIntakeError("duplicate mission-field key rejected", "DUPLICATE_JSON_KEY")
        value[key] = item
    return value


def _load_fields(path: Path) -> dict[str, Any]:
    try:
        raw = path.read_bytes()
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=_duplicate_key_rejector)
    except FreeFormIntakeError:
        raise
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise FreeFormIntakeError("mission fields are unreadable", "MISSION_FIELDS_INVALID") from exc
    if not isinstance(value, dict):
        raise FreeFormIntakeError("mission fields must be one object", "MISSION_FIELDS_INVALID")
    try:
        validate_schema(load_schema(FIELDS_SCHEMA), value)
    except (SchemaValidationError, RuntimeError) as exc:
        raise FreeFormIntakeError("mission fields schema rejected", "MISSION_FIELDS_SCHEMA_REJECTED") from exc
    return value


def _normalize_text(value: str, *, single_line: bool = False) -> str:
    normalized = value.replace("\r\n", "\n").replace("\r", "\n")
    if "\x00" in normalized or any(0xD800 <= ord(char) <= 0xDFFF for char in normalized):
        raise FreeFormIntakeError("mission text contains invalid Unicode", "MISSION_TEXT_REJECTED")
    if single_line and "\n" in normalized:
        raise FreeFormIntakeError("single-line mission field contains a newline", "MISSION_TEXT_REJECTED")
    try:
        normalized.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise FreeFormIntakeError("mission text is not UTF-8 encodable", "MISSION_TEXT_REJECTED") from exc
    return normalized


def _safe_target_path(raw: str) -> str:
    if "\\" in raw or any(ord(char) < 32 or ord(char) == 127 for char in raw):
        raise FreeFormIntakeError("mission path contains forbidden characters", "MISSION_PATH_REJECTED")
    path = PurePosixPath(raw)
    if path.is_absolute() or not path.parts or any(part in {"", ".", ".."} for part in path.parts):
        raise FreeFormIntakeError("mission path is not a safe relative path", "MISSION_PATH_REJECTED")
    normalized = path.as_posix()
    if normalized != raw or normalized.startswith("/"):
        raise FreeFormIntakeError("mission path is not canonical", "MISSION_PATH_REJECTED")
    return normalized


def _payload_name(index: int, path: str) -> str:
    leaf = PurePosixPath(path).name.lower()
    safe = re.sub(r"[^a-z0-9._-]+", "-", leaf).strip(".-") or "payload"
    return f"{index:02d}-{safe}"


def _normalize_fields(fields: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, bytes]]:
    normalized = dict(fields)
    for key in ("objective", "pr_body"):
        normalized[key] = _normalize_text(fields[key])
    for key in ("commit_message", "pr_title"):
        normalized[key] = _normalize_text(fields[key], single_line=True)
    changes = fields.get("changes")
    if not isinstance(changes, list) or not 1 <= len(changes) <= MAX_CHANGES:
        raise FreeFormIntakeError("mission change count rejected", "MISSION_CHANGE_COUNT_REJECTED")
    prepared: list[dict[str, Any]] = []
    folded: set[str] = set()
    total_bytes = 0
    for change in changes:
        if not isinstance(change, dict):
            raise FreeFormIntakeError("mission change is not an object", "MISSION_FIELDS_SCHEMA_REJECTED")
        path = _safe_target_path(change["path"])
        if path.casefold() in folded:
            raise FreeFormIntakeError("mission paths collide", "MISSION_PATH_COLLISION")
        folded.add(path.casefold())
        content = _normalize_text(change["content"])
        payload = content.encode("utf-8")
        total_bytes += len(payload)
        prepared.append({"operation": change["operation"], "path": path, "content": content, "payload": payload})
    if total_bytes > MAX_TOTAL_CONTENT_BYTES:
        raise FreeFormIntakeError("mission payload bytes exceed the local intake limit", "MISSION_CONTENT_SIZE_REJECTED")
    prepared.sort(key=lambda item: item["path"])
    normalized_changes: list[dict[str, str]] = []
    payloads: dict[str, bytes] = {}
    paths: list[dict[str, Any]] = []
    for index, item in enumerate(prepared, start=1):
        payload_name = _payload_name(index, item["path"])
        payloads[f"PAYLOADS/{payload_name}"] = item["payload"]
        normalized_changes.append({"operation": item["operation"], "path": item["path"], "content": item["content"]})
        paths.append({
            "operation": item["operation"],
            "path": item["path"],
            "bytes": len(item["payload"]),
            "payload_name": payload_name,
            "payload_sha256": sha256_bytes(item["payload"]),
        })
    normalized["changes"] = normalized_changes
    return normalized, paths, payloads


def _privacy_scan_local(normalized_fields: dict[str, Any], payloads: dict[str, bytes]) -> None:
    values = [stable_json(normalized_fields).encode("utf-8"), *payloads.values()]
    if any(any(pattern.search(value) for pattern in SENSITIVE) for value in values):
        raise FreeFormIntakeError("mission fields failed the public-clean privacy screen", "MISSION_PRIVACY_REJECTED")


def _weave(fields: dict[str, Any], paths: list[dict[str, Any]], branch: str) -> dict[str, Any]:
    mission_id = fields["mission_id"]
    slug = mission_id.lower()
    body = fields["pr_body"].rstrip("\n") + (
        f"\n\nFree-form intake objective: {fields['objective']}\n"
        f"Carrier nonce: {fields['carrier_nonce']}\n"
        "Route: owner-guided hosted Bow; stop at exact draft PR readback.\n"
        "Fresh Work/Athena origin, protected execution, permanence, and standing authority are not asserted.\n"
    )
    threads = [
        {
            "thread_id": f"free-form-{index:02d}-{sha256_bytes(item['path'].encode('utf-8'))[:12]}",
            "operation": item["operation"],
            "path": item["path"],
            "payload": item["payload_name"],
        }
        for index, item in enumerate(paths, start=1)
    ]
    return {
        "schema_version": "atlas-thread-engine-spear-weave-v1",
        "implementation_state": "SPEAR_BRIDGE_DISABLED",
        "bridge_mode": "COMPILE_ONLY",
        "route": "SPEAR_DIRECT",
        "persistent_writer": "ABSENT",
        "dispatch_authority": "ABSENT",
        "activation_authority": "ABSENT",
        "standing_authority": "NO",
        "weave_id": mission_id,
        "authority_id": f"{mission_id}-FREE-FORM-AUTHORITY",
        "build_identity": f"{mission_id}-FREE-FORM-BUILD",
        "execute_identity": f"{mission_id}-FREE-FORM-EXECUTE",
        "repository": REPOSITORY,
        "base_sha": fields["expected_main_sha"],
        "branch": branch,
        "commit_message": fields["commit_message"],
        "pr_title": fields["pr_title"],
        "pr_body": body,
        "threads": threads,
        "output_mission_filename": f"{slug}-mission.json",
        "compile_receipt_filename": f"{slug}-compile-receipt.json",
        "stop_point": "MISSION_COMPILED",
    }


def _manifest(weave_bytes: bytes, payloads: dict[str, bytes]) -> tuple[dict[str, Any], bytes]:
    values = {"SPEAR-WEAVE.json": weave_bytes, **payloads}
    manifest = {
        "manifest_identity": "atlas-thread-engine-spear-package-v1",
        "files": [
            {"path": path, "bytes": len(data), "sha256": sha256_bytes(data)}
            for path, data in sorted(values.items())
        ],
    }
    return manifest, stable_json(manifest).encode("utf-8")


def _carrier_bytes(weave_bytes: bytes, manifest_bytes: bytes, payloads: dict[str, bytes]) -> bytes:
    entries = [("PACKAGE-MANIFEST.json", manifest_bytes), ("SPEAR-WEAVE.json", weave_bytes), *sorted(payloads.items())]
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_STORED, allowZip64=False) as archive:
        for name, data in entries:
            info = zipfile.ZipInfo(name, ZIP_EPOCH)
            info.create_system = 3
            info.compress_type = zipfile.ZIP_STORED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data)
    carrier = stream.getvalue()
    if not carrier or len(carrier) > MAX_CARRIER_BYTES:
        raise FreeFormIntakeError("constructed carrier size rejected", "CARRIER_SIZE_REJECTED")
    return carrier


def _validate_receipt(receipt: dict[str, Any]) -> None:
    try:
        validate_schema(load_schema(RECEIPT_SCHEMA), receipt)
    except (SchemaValidationError, RuntimeError) as exc:
        raise FreeFormIntakeError("free-form receipt construction failed", "INTAKE_RECEIPT_INVALID") from exc


def construct_free_form_intake(
    fields_path: Path,
    output_dir: Path,
    *,
    runner: Runner = subprocess.run,
    package_reader: Callable[[Path, str], Any] | None = None,
    compiler: Callable[..., dict[str, Any]] | None = None,
) -> dict[str, Any]:
    fields_path = fields_path.resolve()
    output_dir = output_dir.absolute()
    if output_dir.exists() or output_dir.is_symlink():
        raise FreeFormIntakeError("output directory already exists", "OUTPUT_DIRECTORY_EXISTS")
    try:
        if output_dir.resolve().is_relative_to(ROOT.resolve()):
            raise FreeFormIntakeError("output directory is inside canonical source", "OUTPUT_INSIDE_CANONICAL_REPOSITORY")
    except FileNotFoundError:
        pass
    fields = _load_fields(fields_path)
    normalized, paths, payloads = _normalize_fields(fields)
    if not SAFE_MISSION.fullmatch(normalized["mission_id"]):
        raise FreeFormIntakeError("mission identity rejected", "MISSION_FIELDS_SCHEMA_REJECTED")
    _privacy_scan_local(normalized, payloads)
    classification, _route = classify_paths([item["path"] for item in paths])
    if classification != "SAFE_DECLARED":
        raise FreeFormIntakeError("mission paths are outside the safe declared authored route", classification)
    try:
        main_sha, workflow_blob_sha = _read_live_identity(runner)
    except GuidedPublisherError as exc:
        raise FreeFormIntakeError("canonical identity readback failed", exc.code) from exc
    if normalized["expected_main_sha"] != main_sha:
        raise FreeFormIntakeError("mission fields are not bound to current main", "STALE_BASE")
    branch = expected_mission_branch(normalized["mission_id"], main_sha)
    weave = _weave(normalized, paths, branch)
    weave_bytes = stable_json(weave).encode("utf-8")
    _manifest_value, manifest_bytes = _manifest(weave_bytes, payloads)
    carrier = _carrier_bytes(weave_bytes, manifest_bytes, payloads)
    carrier_sha = sha256_bytes(carrier)
    normalized_sha = sha256_bytes(stable_json(normalized).encode("utf-8"))
    if package_reader is None or compiler is None:
        _adapter_error, _execute_mission, imported_compiler, imported_reader = _engine_imports()
        package_reader = package_reader or imported_reader
        compiler = compiler or imported_compiler
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".athena-free-form-", dir=output_dir.parent) as temporary:
        staged = Path(temporary) / "artifact"
        compiled = staged / "compiled"
        staged.mkdir()
        carrier_path = staged / "carrier.zip"
        carrier_path.write_bytes(carrier)
        try:
            preview = build_preview(
                carrier_path,
                runner=runner,
                package_reader=package_reader,
                compiler=compiler,
            )
        except GuidedPublisherError as exc:
            raise FreeFormIntakeError("constructed carrier Preview rejected", exc.code) from exc
        try:
            package = package_reader(carrier_path, carrier_sha)
            privacy_scan(package)
            compile_receipt = compiler(
                carrier_path,
                package_sha256=carrier_sha,
                output_dir=compiled,
                disabled_proof=True,
                compile_only=True,
                read_only_remote_url=REMOTE_URL,
            )
            compile_sha, compiled_inventory, compiled_identity = _compiled_output_identity(compiled, compile_receipt)
        except Exception as exc:
            code = str(getattr(exc, "code", "FREE_FORM_COMPILE_REJECTED"))
            raise FreeFormIntakeError("retained canonical compilation rejected", code) from exc
        exact_join = (
            preview["canonical_main_sha"] == main_sha
            and preview["carrier_sha256"] == carrier_sha
            and preview["manifest_sha256"] == sha256_bytes(manifest_bytes)
            and preview["weave_sha256"] == sha256_bytes(weave_bytes)
            and preview["compile_receipt_sha256"] == compile_sha
            and preview["compiled_inventory"] == compiled_inventory
            and preview["mission_sha256"] == compiled_identity["mission_sha256"]
            and preview["candidate_tree_sha256"] == compiled_identity["candidate_tree_sha256"]
            and preview["final_pathset_sha256"] == compiled_identity["final_pathset_sha256"]
            and preview["deterministic_branch"] == branch
        )
        if not exact_join:
            raise FreeFormIntakeError("retained compilation drifted from Preview", "RETAINED_COMPILE_DRIFT")
        preview_bytes = stable_json(preview).encode("utf-8")
        (staged / "preview.json").write_bytes(preview_bytes)
        receipt_paths = [
            {"operation": item["operation"], "path": item["path"], "bytes": item["bytes"], "payload_sha256": item["payload_sha256"]}
            for item in paths
        ]
        receipt = {
            "schema_version": "atlas.athena.free-form-intake-receipt.v1",
            "result": "CONSTRUCTED",
            "repository": REPOSITORY,
            "normalized_fields_sha256": normalized_sha,
            "canonical_main_sha": main_sha,
            "workflow_ref": WORKFLOW_REF,
            "workflow_blob_sha": workflow_blob_sha,
            "mission_id": normalized["mission_id"],
            "carrier_nonce_sha256": sha256_bytes(normalized["carrier_nonce"].encode("utf-8")),
            "carrier_filename": "carrier.zip",
            "carrier_bytes": len(carrier),
            "carrier_sha256": carrier_sha,
            "manifest_sha256": sha256_bytes(manifest_bytes),
            "weave_sha256": sha256_bytes(weave_bytes),
            "mission_lock_sha256": mission_lock_sha256(normalized["mission_id"], main_sha),
            "compile_receipt_schema_version": compile_receipt["schema_version"],
            "compile_receipt_filename": compile_receipt["compile_receipt_filename"],
            "compile_receipt_sha256": compile_sha,
            "output_mission_filename": compile_receipt["output_mission_filename"],
            "output_mission_sha256": compile_receipt["output_mission_sha256"],
            "mission_sha256": compiled_identity["mission_sha256"],
            "candidate_tree_sha256": compiled_identity["candidate_tree_sha256"],
            "final_pathset_sha256": compiled_identity["final_pathset_sha256"],
            "compiled_inventory": compiled_inventory,
            "preview_filename": "preview.json",
            "preview_sha256": sha256_bytes(preview_bytes),
            "deterministic_branch": branch,
            "path_classification": classification,
            "paths": receipt_paths,
            "public_clean": True,
            "origin_classification": "OWNER_GUIDED_LOCAL_NOT_FRESH_WORK_ORIGIN",
            "stop_point": "FREE_FORM_CARRIER_CONSTRUCTED",
            "next_step": "GUIDED_PREVIEW_CONFIRMATION_REQUIRED",
            "rollback": "DELETE_UNDISPATCHED_LOCAL_OUTPUT_DIRECTORY",
            "promotion_boundary": "LIVE_HOSTED_ACCEPTANCE_AND_SEPARATE_AUTHORED_RECONCILIATION_REQUIRED",
            "forbidden_actions": dict(FORBIDDEN_ACTIONS),
        }
        _validate_receipt(receipt)
        (staged / "intake-receipt.json").write_bytes(stable_json(receipt).encode("utf-8"))
        try:
            os.replace(staged, output_dir)
        except OSError as exc:
            raise FreeFormIntakeError("atomic output publication failed", "OUTPUT_PUBLICATION_FAILED") from exc
    return receipt


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Construct one deterministic public-clean Athena carrier from ordinary mission fields")
    parser.add_argument("--fields", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        receipt = construct_free_form_intake(args.fields, args.output_dir)
    except FreeFormIntakeError as exc:
        sys.stderr.write(f"Free-form intake stopped safely: {exc.code}\n")
        return 2
    receipt_path = args.output_dir.absolute() / "intake-receipt.json"
    sys.stdout.write(stable_json({
        "result": receipt["result"],
        "mission_id": receipt["mission_id"],
        "carrier_sha256": receipt["carrier_sha256"],
        "mission_sha256": receipt["mission_sha256"],
        "receipt_sha256": sha256_bytes(receipt_path.read_bytes()),
        "stop_point": receipt["stop_point"],
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
