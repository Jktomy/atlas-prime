from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

from production_adapter.authority import EXPECTED_API, EXPECTED_REMOTE_URL, validate_mission
from production_adapter.path_policy import PolicyError, reject_runtime_byproducts, validate_declared_path_set, validate_relative_path
from production_adapter.receipt import declared_state_hash, sha256_bytes, stable_json, tree_hash, write_json

from .git_reader import EXPECTED_REMOTE, GitReader, GitReaderError, SourceAbsentError, SourceFile

WEAVE_SCHEMA_VERSION = "atlas-thread-engine-spear-weave-v1"
MANIFEST_IDENTITY = "atlas-thread-engine-spear-package-v1"
IMPLEMENTATION_STATE = "SPEAR_BRIDGE_DISABLED"
BRIDGE_MODE = "COMPILE_ONLY"
ROUTE = "SPEAR_DIRECT"
STOP_POINT = "MISSION_COMPILED"
REPOSITORY = "Jktomy/atlas-prime"

TOP_LEVEL_WEAVE_KEYS = {
    "schema_version",
    "implementation_state",
    "bridge_mode",
    "route",
    "persistent_writer",
    "dispatch_authority",
    "activation_authority",
    "standing_authority",
    "weave_id",
    "authority_id",
    "build_identity",
    "execute_identity",
    "repository",
    "base_sha",
    "branch",
    "commit_message",
    "pr_title",
    "pr_body",
    "threads",
    "delete_authority_id",
    "output_mission_filename",
    "compile_receipt_filename",
    "stop_point",
}
THREAD_KEYS = {"thread_id", "operation", "path", "payload", "delete_authority_id"}
MANIFEST_KEYS = {"manifest_identity", "files"}
MANIFEST_FILE_KEYS = {"path", "bytes", "sha256"}
HEX = set("0123456789abcdef")


class SpearBridgeError(Exception):
    def __init__(self, message: str, code: str = "SPEAR_BRIDGE_REJECTED", stage: str = "STOP") -> None:
        super().__init__(message)
        self.code = code
        self.stage = stage


def _duplicate_key_rejector(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise SpearBridgeError(f"duplicate JSON key rejected: {key}", "DUPLICATE_JSON_KEY", "JSON_PARSE")
        result[key] = value
    return result


def load_json_bytes(data: bytes, stage: str) -> dict[str, Any]:
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise SpearBridgeError("JSON input is not valid UTF-8", "INVALID_UTF8", stage) from exc
    try:
        value = json.loads(text, object_pairs_hook=_duplicate_key_rejector)
    except json.JSONDecodeError as exc:
        raise SpearBridgeError(f"invalid JSON: {exc}", "INVALID_JSON", stage) from exc
    if not isinstance(value, dict):
        raise SpearBridgeError("JSON root must be an object", "JSON_SCHEMA", stage)
    return value


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _require_sha(value: Any, field: str) -> str:
    if not isinstance(value, str) or len(value) != 64 or any(char not in HEX for char in value):
        raise SpearBridgeError(f"{field} must be a lowercase 64-character SHA-256", "MANIFEST_REJECTED", "MANIFEST")
    return value


def _safe_package_path(value: str) -> PurePosixPath:
    path = validate_relative_path(value)
    if path.as_posix().casefold().endswith(".zip"):
        raise SpearBridgeError("nested ZIP entry rejected", "NESTED_ZIP", "PACKAGE_AUDIT")
    return path


def _safe_filename(value: str) -> str:
    if not isinstance(value, str) or not value.endswith(".json") or "/" in value or "\\" in value or value in {"", ".", ".."}:
        raise SpearBridgeError("output filename must be one safe .json filename", "OUTPUT_NAME_REJECTED", "WEAVE_SCHEMA")
    return value


@dataclass(frozen=True)
class PackageData:
    carrier_sha256: str
    manifest_sha256: str
    weave_sha256: str
    manifest: dict[str, Any]
    weave: dict[str, Any]
    payloads: dict[str, bytes]


def read_spear_package(package: Path, expected_sha256: str) -> PackageData:
    if not package.exists() or not package.is_file():
        raise SpearBridgeError("Spear package is absent", "PACKAGE_ABSENT", "PACKAGE_AUDIT")
    carrier = _sha(package.read_bytes())
    if carrier != expected_sha256:
        raise SpearBridgeError("carrier SHA mismatch", "CARRIER_SHA_MISMATCH", "PACKAGE_AUDIT")
    seen: set[str] = set()
    folded: set[str] = set()
    raw_files: dict[str, bytes] = {}
    try:
        with zipfile.ZipFile(package) as archive:
            for info in archive.infolist():
                name = info.filename
                path = _safe_package_path(name)
                if path.as_posix() in seen or path.as_posix().casefold() in folded:
                    raise SpearBridgeError("duplicate or case-fold archive name rejected", "PATH_COLLISION", "PACKAGE_AUDIT")
                seen.add(path.as_posix())
                folded.add(path.as_posix().casefold())
                entry_type = _zip_entry_type(info)
                if entry_type == "directory":
                    if path.parts[0] != "PAYLOADS":
                        raise SpearBridgeError(f"unexpected directory entry: {name}", "PACKAGE_MANIFEST", "PACKAGE_AUDIT")
                    continue
                if entry_type != "file":
                    raise SpearBridgeError("nonregular archive entry rejected", "PACKAGE_MANIFEST", "PACKAGE_AUDIT")
                if path.as_posix() in {"SPEAR-WEAVE.json", "PACKAGE-MANIFEST.json"}:
                    raw_files[path.as_posix()] = archive.read(info)
                elif path.parts[0] == "PAYLOADS" and len(path.parts) > 1:
                    raw_files[path.as_posix()] = archive.read(info)
                else:
                    raise SpearBridgeError(f"unexpected regular file entry: {name}", "PACKAGE_MANIFEST", "PACKAGE_AUDIT")
    except zipfile.BadZipFile as exc:
        raise SpearBridgeError("invalid ZIP carrier", "INVALID_ZIP", "PACKAGE_AUDIT") from exc
    if "SPEAR-WEAVE.json" not in raw_files or "PACKAGE-MANIFEST.json" not in raw_files:
        raise SpearBridgeError("required package roots are missing", "PACKAGE_MANIFEST", "PACKAGE_AUDIT")
    manifest_bytes = raw_files.pop("PACKAGE-MANIFEST.json")
    weave_bytes = raw_files.pop("SPEAR-WEAVE.json")
    manifest = load_json_bytes(manifest_bytes, "MANIFEST")
    weave = load_json_bytes(weave_bytes, "WEAVE_SCHEMA")
    _verify_manifest(manifest, raw_files | {"SPEAR-WEAVE.json": weave_bytes})
    return PackageData(carrier, _sha(manifest_bytes), _sha(weave_bytes), manifest, weave, raw_files)


def _verify_manifest(manifest: dict[str, Any], observed: dict[str, bytes]) -> None:
    if set(manifest) != MANIFEST_KEYS:
        raise SpearBridgeError("manifest has unknown or missing root properties", "MANIFEST_REJECTED", "MANIFEST")
    if manifest.get("manifest_identity") != MANIFEST_IDENTITY:
        raise SpearBridgeError("manifest identity mismatch", "MANIFEST_REJECTED", "MANIFEST")
    files = manifest.get("files")
    if not isinstance(files, list) or not files:
        raise SpearBridgeError("manifest files must be a non-empty array", "MANIFEST_REJECTED", "MANIFEST")
    expected: dict[str, tuple[int, str]] = {}
    folded: set[str] = set()
    for item in files:
        if not isinstance(item, dict) or set(item) != MANIFEST_FILE_KEYS:
            raise SpearBridgeError("manifest file entry malformed", "MANIFEST_REJECTED", "MANIFEST")
        raw_path = item["path"]
        if not isinstance(raw_path, str) or not raw_path:
            raise SpearBridgeError("manifest path must be a non-empty safe string", "MANIFEST_REJECTED", "MANIFEST")
        path = _safe_package_path(raw_path).as_posix()
        if path == "PACKAGE-MANIFEST.json":
            raise SpearBridgeError("manifest must not list itself", "MANIFEST_REJECTED", "MANIFEST")
        folded_path = path.casefold()
        if path in expected or folded_path in folded:
            raise SpearBridgeError("duplicate manifest path rejected", "PATH_COLLISION", "MANIFEST")
        folded.add(folded_path)
        byte_count = item["bytes"]
        if isinstance(byte_count, bool) or not isinstance(byte_count, int) or byte_count < 0:
            raise SpearBridgeError("manifest bytes must be a non-negative integer", "MANIFEST_REJECTED", "MANIFEST")
        expected[path] = (byte_count, _require_sha(item["sha256"], "sha256"))
    observed_map = {path: (len(data), _sha(data)) for path, data in observed.items()}
    if expected != observed_map:
        raise SpearBridgeError("manifest does not match observed package", "MANIFEST_TAMPER", "MANIFEST")


def _require_const(data: dict[str, Any], field: str, expected: str) -> None:
    if data.get(field) != expected:
        raise SpearBridgeError(f"{field} must be {expected}", "WEAVE_SCHEMA", "WEAVE_SCHEMA")


def _validate_weave(weave: dict[str, Any]) -> None:
    unknown = set(weave) - TOP_LEVEL_WEAVE_KEYS
    missing = TOP_LEVEL_WEAVE_KEYS - set(weave) - {"delete_authority_id"}
    if unknown or missing:
        raise SpearBridgeError("weave has unknown or missing properties", "WEAVE_SCHEMA", "WEAVE_SCHEMA")
    for field, expected in {
        "schema_version": WEAVE_SCHEMA_VERSION,
        "implementation_state": IMPLEMENTATION_STATE,
        "bridge_mode": BRIDGE_MODE,
        "route": ROUTE,
        "persistent_writer": "ABSENT",
        "dispatch_authority": "ABSENT",
        "activation_authority": "ABSENT",
        "standing_authority": "NO",
        "repository": REPOSITORY,
        "stop_point": STOP_POINT,
    }.items():
        _require_const(weave, field, expected)
    if weave.get("build_identity") == weave.get("execute_identity"):
        raise SpearBridgeError("build and execute identities must be distinct", "IDENTITY_COLLISION", "WEAVE_SCHEMA")
    mission_name = _safe_filename(weave.get("output_mission_filename", ""))
    receipt_name = _safe_filename(weave.get("compile_receipt_filename", ""))
    if mission_name == receipt_name:
        raise SpearBridgeError("mission and receipt filenames must differ", "OUTPUT_COLLISION", "WEAVE_SCHEMA")
    threads = weave.get("threads")
    if not isinstance(threads, list) or not threads:
        raise SpearBridgeError("threads must be a non-empty array", "WEAVE_SCHEMA", "WEAVE_SCHEMA")
    ids: set[str] = set()
    paths: list[str] = []
    for thread in threads:
        if not isinstance(thread, dict) or set(thread) - THREAD_KEYS:
            raise SpearBridgeError("thread has unknown properties", "UNKNOWN_PROPERTY", "WEAVE_SCHEMA")
        thread_id = thread.get("thread_id")
        if not isinstance(thread_id, str) or not thread_id or thread_id in ids:
            raise SpearBridgeError("duplicate or invalid thread_id", "THREAD_COLLISION", "WEAVE_SCHEMA")
        ids.add(thread_id)
        operation = thread.get("operation")
        path = validate_relative_path(thread.get("path", "")).as_posix()
        paths.append(path)
        if operation in {"ADD", "REPLACE"}:
            if set(thread) != {"thread_id", "operation", "path", "payload"}:
                raise SpearBridgeError("ADD/REPLACE thread requires only payload", "WEAVE_SCHEMA", "WEAVE_SCHEMA")
            _safe_package_path(thread["payload"])
        elif operation == "DELETE":
            if set(thread) != {"thread_id", "operation", "path", "delete_authority_id"}:
                raise SpearBridgeError("DELETE thread requires only delete authority", "WEAVE_SCHEMA", "WEAVE_SCHEMA")
            if thread.get("delete_authority_id") != weave.get("delete_authority_id"):
                raise SpearBridgeError("DELETE authority mismatch", "DELETE_AUTHORITY_REQUIRED", "WEAVE_SCHEMA")
        else:
            raise SpearBridgeError("unsupported operation", "WEAVE_SCHEMA", "WEAVE_SCHEMA")
    validate_declared_path_set(paths)


class ReaderProtocol:
    observed_base: str | None

    def prepare(self) -> None: ...
    def read_source(self, path: str) -> SourceFile: ...


def compile_package(package_path: Path, *, package_sha256: str, output_dir: Path, disabled_proof: bool, compile_only: bool, reader: ReaderProtocol | None = None, read_only_remote_url: str | None = None) -> dict[str, Any]:
    if not disabled_proof or not compile_only:
        raise SpearBridgeError("explicit disabled-proof and compile-only intent required", "INTENT_REQUIRED", "PACKAGE_AUDIT")
    checkpoints: list[str] = []
    staging_root = Path(tempfile.mkdtemp(prefix="atlas-spear-bridge-stage-"))
    owned_reader: GitReader | None = None
    publish_started = False
    try:
        _validate_output_target(output_dir)
        checkpoints.append("PACKAGE_AUDIT")
        package = read_spear_package(package_path, package_sha256)
        checkpoints.append("WEAVE_SCHEMA")
        _validate_weave(package.weave)
        weave = package.weave
        referenced_payloads = _referenced_payloads(weave)
        if set(package.payloads) != referenced_payloads:
            raise SpearBridgeError("observed payload set must equal referenced ADD/REPLACE payloads", "PAYLOAD_SET_MISMATCH", "WEAVE_SCHEMA")
        checkpoints.append("READ_ONLY_GIT")
        active_reader = reader
        if active_reader is None:
            if read_only_remote_url is None:
                owned_reader = GitReader(base_sha=weave["base_sha"])
            else:
                owned_reader = GitReader(remote_url=read_only_remote_url, base_sha=weave["base_sha"])
            active_reader = owned_reader
        active_reader.prepare()
        observed_base = getattr(active_reader, "observed_base", None)
        if not isinstance(observed_base, str) or observed_base != weave["base_sha"]:
            raise SpearBridgeError("observed base does not match authored base", "BASE_MISMATCH", "READ_ONLY_GIT")

        payload_root = staging_root / "_payloads"
        candidate_root = staging_root / "_candidate_tree"
        final_root = staging_root / "_final_state"
        staged_output = staging_root / "_output"
        payload_root.mkdir()
        candidate_root.mkdir()
        final_root.mkdir()
        staged_output.mkdir()
        staged_payload_output = staged_output / "PAYLOADS"
        staged_payload_output.mkdir()

        source_blobs: dict[str, str] = {}
        operations: list[dict[str, Any]] = []
        declared_paths: list[str] = []
        for thread in weave["threads"]:
            operation = thread["operation"]
            path = validate_relative_path(thread["path"]).as_posix()
            declared_paths.append(path)
            target = final_root.joinpath(*path.split("/"))
            if operation == "ADD":
                source = None
                if not _source_absent(active_reader, path):
                    raise SpearBridgeError(f"ADD target exists: {path}", "THREAD_REJECTED", "THREAD_COMPILE")
            else:
                source = active_reader.read_source(path)
                source_blobs[path] = source.blob
                if operation == "REPLACE":
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(source.data)
            if operation in {"ADD", "REPLACE"}:
                payload_name = validate_relative_path(thread["payload"]).as_posix()
                package_key = f"PAYLOADS/{payload_name}"
                payload_data = package.payloads[package_key]
                for root in (payload_root, staged_payload_output):
                    payload_file = root.joinpath(*payload_name.split("/"))
                    payload_file.parent.mkdir(parents=True, exist_ok=True)
                    payload_file.write_bytes(payload_data)
                candidate_target = candidate_root.joinpath(*path.split("/"))
                candidate_target.parent.mkdir(parents=True, exist_ok=True)
                candidate_target.write_bytes(payload_data)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(payload_data)
                compiled = {
                    "thread_id": thread["thread_id"],
                    "operation": operation,
                    "path": path,
                    "payload": payload_name,
                    "payload_sha256": _sha(payload_data),
                    "expected_output_sha256": _sha(payload_data),
                }
                if operation == "REPLACE":
                    if source is None:
                        raise SpearBridgeError("REPLACE source missing", "SOURCE_REJECTED", "THREAD_COMPILE")
                    compiled["source_sha256"] = source.sha256
            else:
                if source is None:
                    raise SpearBridgeError("DELETE source missing", "SOURCE_REJECTED", "THREAD_COMPILE")
                compiled = {
                    "thread_id": thread["thread_id"],
                    "operation": "DELETE",
                    "path": path,
                    "source_sha256": source.sha256,
                    "delete_authority_id": thread["delete_authority_id"],
                }
            operations.append(compiled)
        checkpoints.append("MISSION_DERIVE")
        validate_declared_path_set(declared_paths)
        mission = {
            "schema_version": "atlas-thread-engine-production-mission-v1",
            "implementation_state": "THREAD_ENGINE_ACTIVE_MISSION_SCOPED",
            "adapter_mode": "DRAFT_PR_ONLY",
            "persistent_writer": "ABSENT",
            "activation_authority": "MISSION_SCOPED",
            "mission_id": weave["weave_id"],
            "authority_id": weave["authority_id"],
            "build_identity": weave["build_identity"],
            "execute_identity": weave["execute_identity"],
            "mission_sha256": "0" * 64,
            "repository": REPOSITORY,
            "remote_url": EXPECTED_REMOTE_URL,
            "base_sha": weave["base_sha"],
            "branch": weave["branch"],
            "commit_message": weave["commit_message"],
            "pr_title": weave["pr_title"],
            "pr_body": weave["pr_body"],
            "declared_paths": declared_paths,
            "payload_root": "PAYLOADS",
            "candidate_tree_sha256": tree_hash(candidate_root),
            "final_pathset_sha256": declared_state_hash(final_root, tuple(declared_paths)),
            "source_blobs": source_blobs,
            "operations": operations,
            "network_allowlist": [EXPECTED_REMOTE_URL, EXPECTED_API],
            "receipt_name": "production-adapter-receipt.json",
            "stop_point": "DRAFT_PR_READBACK",
        }
        if weave.get("delete_authority_id") is not None:
            mission["delete_authority_id"] = weave["delete_authority_id"]
        mission["mission_sha256"] = sha256_bytes(stable_json(mission).encode("utf-8"))
        validate_mission(mission)
        checkpoints.append("MISSION_VALIDATE")
        clone_disposed = False
        if owned_reader is not None:
            owned_reader.close()
            clone_disposed = True

        mission_path = staged_output / _safe_filename(weave["output_mission_filename"])
        receipt_path = staged_output / _safe_filename(weave["compile_receipt_filename"])
        write_json(mission_path, mission)
        payload_inventory = _payload_inventory(staged_payload_output)
        expected_output_paths = sorted([mission_path.name, receipt_path.name] + [f"PAYLOADS/{item['path']}" for item in payload_inventory])
        receipt = {
            "schema_version": "atlas-thread-engine-spear-compile-receipt-v1",
            "implementation_state": IMPLEMENTATION_STATE,
            "bridge_mode": BRIDGE_MODE,
            "route": ROUTE,
            "package_identity": MANIFEST_IDENTITY,
            "carrier_sha256": package.carrier_sha256,
            "manifest_sha256": package.manifest_sha256,
            "weave_sha256": package.weave_sha256,
            "base_expected": weave["base_sha"],
            "base_observed": observed_base,
            "mission_sha256": mission["mission_sha256"],
            "output_mission_filename": mission_path.name,
            "output_mission_sha256": _sha(mission_path.read_bytes()),
            "compile_receipt_filename": receipt_path.name,
            "payload_inventory": payload_inventory,
            "output_inventory": expected_output_paths,
            "checkpoints": checkpoints + ["RECEIPT", "STOP"],
            "result": "SUCCESS",
            "stop_point": STOP_POINT,
            "forbidden_action_confirmation": {
                "adapter_invoked": False,
                "github_mutation": False,
                "production_authority_activated": False,
                "standing_authority": "NO",
            },
        }
        if owned_reader is not None:
            receipt["read_only_clone_disposed"] = clone_disposed
        write_json(receipt_path, receipt)
        if _relative_file_paths(staged_output) != expected_output_paths:
            raise SpearBridgeError("staged output inventory mismatch", "OUTPUT_INVENTORY_MISMATCH", "OUTPUT")
        reject_runtime_byproducts(staged_output)
        output_dir.mkdir(parents=True, exist_ok=True)
        if any(output_dir.iterdir()):
            raise SpearBridgeError("output directory changed before publish", "OUTPUT_COLLISION", "OUTPUT")
        publish_started = True
        for child in staged_output.iterdir():
            destination = output_dir / child.name
            if child.is_dir():
                shutil.copytree(child, destination)
            else:
                shutil.copy2(child, destination)
        if _file_hashes(output_dir) != _file_hashes(staged_output):
            raise SpearBridgeError("published output readback mismatch", "OUTPUT_INVENTORY_MISMATCH", "OUTPUT")
        reject_runtime_byproducts(output_dir)
        return receipt
    except (SpearBridgeError, PolicyError, GitReaderError, OSError, ValueError, json.JSONDecodeError) as exc:
        if publish_started:
            _empty_directory(output_dir)
        raise exc if isinstance(exc, SpearBridgeError) else SpearBridgeError(str(exc), getattr(exc, "code", "SPEAR_BRIDGE_REJECTED"), "STOP")
    finally:
        if owned_reader is not None:
            try:
                owned_reader.close()
            except GitReaderError:
                pass
        shutil.rmtree(staging_root, ignore_errors=True)


def _source_absent(reader: ReaderProtocol, path: str) -> bool:
    try:
        reader.read_source(path)
        return False
    except SourceAbsentError:
        return True


def _referenced_payloads(weave: dict[str, Any]) -> set[str]:
    payloads: set[str] = set()
    for thread in weave["threads"]:
        if thread["operation"] in {"ADD", "REPLACE"}:
            payloads.add(f"PAYLOADS/{validate_relative_path(thread['payload']).as_posix()}")
    return payloads


def _payload_inventory(root: Path) -> list[dict[str, Any]]:
    inventory: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*"), key=lambda item: item.relative_to(root).as_posix()):
        if path.is_dir():
            continue
        if not path.is_file() or path.is_symlink():
            raise SpearBridgeError("payload output contains nonregular entry", "OUTPUT_INVENTORY_MISMATCH", "OUTPUT")
        inventory.append({"path": path.relative_to(root).as_posix(), "bytes": path.stat().st_size, "sha256": _sha(path.read_bytes())})
    return inventory


def _relative_file_paths(root: Path) -> list[str]:
    paths: list[str] = []
    for path in sorted(root.rglob("*"), key=lambda item: item.relative_to(root).as_posix()):
        if path.is_dir():
            continue
        if not path.is_file() or path.is_symlink():
            raise SpearBridgeError("output contains nonregular entry", "OUTPUT_INVENTORY_MISMATCH", "OUTPUT")
        paths.append(path.relative_to(root).as_posix())
    return paths


def _file_hashes(root: Path) -> list[tuple[str, int, str]]:
    result: list[tuple[str, int, str]] = []
    for path in sorted(root.rglob("*"), key=lambda item: item.relative_to(root).as_posix()):
        if path.is_dir():
            continue
        if not path.is_file() or path.is_symlink():
            raise SpearBridgeError("output contains nonregular entry", "OUTPUT_INVENTORY_MISMATCH", "OUTPUT")
        result.append((path.relative_to(root).as_posix(), path.stat().st_size, _sha(path.read_bytes())))
    return result


def _empty_directory(path: Path) -> None:
    if path.is_symlink() or not path.exists() or not path.is_dir():
        return
    for child in path.iterdir():
        if child.is_dir() and not child.is_symlink():
            shutil.rmtree(child, ignore_errors=True)
        else:
            child.unlink(missing_ok=True)


def _validate_output_target(path: Path) -> None:
    if path.is_symlink():
        raise SpearBridgeError("output directory must not be a symlink", "OUTPUT_COLLISION", "OUTPUT")
    if path.exists():
        if not path.is_dir() or any(path.iterdir()):
            raise SpearBridgeError("output directory must be absent or empty", "OUTPUT_COLLISION", "OUTPUT")


def _zip_entry_type(info: zipfile.ZipInfo) -> str:
    mode = (info.external_attr >> 16) & 0o170000
    if mode == 0:
        return "directory" if info.is_dir() else "file"
    if mode == 0o040000:
        return "directory" if info.is_dir() else "other"
    if mode == 0o100000:
        return "file" if not info.is_dir() else "other"
    return "other"
