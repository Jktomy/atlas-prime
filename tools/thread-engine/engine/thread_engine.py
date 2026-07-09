from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any, Callable

from production_adapter.protected_paths import is_protected_path

VERSION = "gate7b-fixture-0.2"
ENGINE_STATE = "PILOT_DISABLED"
MODE = "FIXTURE_ONLY"

CHECKPOINTS = [
    "PACKAGE_AUDIT",
    "PARSER_PREFLIGHT",
    "WEAVE_SCHEMA",
    "FIXTURE_BOUNDARY",
    "BASE_TREE_VERIFY",
    "THREAD_SET_VERIFY",
    "CANDIDATE_STAGE",
    "CANDIDATE_TREE_VERIFY",
    "RECEIPT",
    "STOP",
]

FORBIDDEN_ACTIONS = [
    "git clone",
    "git checkout",
    "git branch",
    "git commit",
    "git push",
    "gh",
    "github mutation",
    "http mutation",
    "workflow dispatch",
    "pr creation or merge",
    "repository setting mutation",
    "direct-main write",
    "force push",
    "shell eval",
    "caller-supplied executable command",
    "arbitrary source-checkout mutation",
]

RUNTIME_BYPRODUCTS = {"__pycache__", ".pytest_cache"}
RUNTIME_SUFFIXES = {".pyc", ".pyo"}


class ThreadEngineError(Exception):
    def __init__(
        self,
        message: str,
        error_code: str = "REJECTED",
        error_stage: str = "STOP",
        receipt: dict[str, Any] | None = None,
    ):
        super().__init__(message)
        self.error_code = error_code
        self.error_stage = error_stage
        self.stop_point = error_stage
        self.receipt = receipt or {}


def reject(message: str, error_code: str, error_stage: str) -> None:
    raise ThreadEngineError(message, error_code, error_stage)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def stable_json(data: dict[str, Any]) -> str:
    return json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(stable_json(data), encoding="utf-8")


def relative_posix(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def reject_runtime_byproducts(root: Path) -> None:
    for path in root.rglob("*"):
        if path.name in RUNTIME_BYPRODUCTS or path.suffix in RUNTIME_SUFFIXES:
            reject(f"runtime byproduct is not allowed: {path.name}", "RUNTIME_BYPRODUCT", "PACKAGE_AUDIT")


def validate_no_symlinks(root: Path, is_symlink: Callable[[Path], bool] | None = None) -> None:
    classifier = is_symlink or (lambda item: item.is_symlink())
    for path in root.rglob("*"):
        if classifier(path):
            reject(f"symlink is not allowed: {relative_posix(path, root)}", "SYMLINK_REJECTED", "FIXTURE_BOUNDARY")


def tree_hash(root: Path) -> str:
    root = root.resolve()
    validate_no_symlinks(root)
    entries: list[tuple[str, int, str]] = []
    for path in sorted(root.rglob("*"), key=lambda item: item.relative_to(root).as_posix()):
        if path.is_dir():
            continue
        if not path.is_file():
            reject(f"non-regular file is not allowed: {relative_posix(path, root)}", "REGULAR_FILE_REQUIRED", "FIXTURE_BOUNDARY")
        rel = relative_posix(path, root)
        data_hash = sha256_file(path)
        entries.append((rel, path.stat().st_size, data_hash))
    digest = hashlib.sha256()
    for rel, size, data_hash in entries:
        digest.update(rel.encode("utf-8"))
        digest.update(b"\0file\0")
        digest.update(str(size).encode("ascii"))
        digest.update(b"\0")
        digest.update(data_hash.encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def validate_relative_path(value: str) -> PurePosixPath:
    if not isinstance(value, str) or value == "":
        reject("path must be a non-empty string", "PATH_REJECTED", "THREAD_SET_VERIFY")
    if "\\" in value:
        reject(f"backslash path is rejected: {value}", "PATH_REJECTED", "THREAD_SET_VERIFY")
    path = PurePosixPath(value)
    if path.is_absolute() or ":" in value:
        reject(f"absolute path is rejected: {value}", "PATH_REJECTED", "THREAD_SET_VERIFY")
    if any(part in ("", ".", "..") for part in path.parts):
        reject(f"traversal or empty path segment is rejected: {value}", "PATH_REJECTED", "THREAD_SET_VERIFY")
    return path


def resolve_under(root: Path, relative: PurePosixPath, stage: str = "FIXTURE_BOUNDARY") -> Path:
    target = root.joinpath(*relative.parts).resolve(strict=False)
    root_resolved = root.resolve()
    try:
        target.relative_to(root_resolved)
    except ValueError as exc:
        raise ThreadEngineError(f"path escapes sandbox: {relative.as_posix()}", "BOUNDARY_REJECTED", stage) from exc
    return target


def load_weave(weave_path: Path) -> dict[str, Any]:
    try:
        return json.loads(weave_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ThreadEngineError(f"invalid JSON: {exc}", "INVALID_JSON", "PARSER_PREFLIGHT") from exc


def require_sha(value: str, field: str) -> None:
    if not isinstance(value, str) or len(value) != 64 or any(char not in "0123456789abcdef" for char in value):
        reject(f"{field} must be a lowercase SHA-256 hex digest", "WEAVE_SCHEMA", "WEAVE_SCHEMA")


def validate_weave_shape(weave: dict[str, Any]) -> None:
    required = [
        "format_version",
        "weave_id",
        "engine_state",
        "mode",
        "base_fixture",
        "payload_root",
        "expected_base_tree_sha256",
        "threads",
        "expected_candidate_tree_sha256",
        "resume_from",
        "stop_boundary",
        "forbidden_actions",
        "receipt_name",
    ]
    missing = [field for field in required if field not in weave]
    if missing:
        reject(f"missing required weave fields: {', '.join(missing)}", "WEAVE_SCHEMA", "WEAVE_SCHEMA")
    if weave["format_version"] != "atlas-thread-engine-weave-v1":
        reject("unsupported weave format_version", "WEAVE_SCHEMA", "WEAVE_SCHEMA")
    if weave["engine_state"] != ENGINE_STATE or weave["mode"] != MODE:
        reject("weave must target PILOT_DISABLED FIXTURE_ONLY", "WEAVE_SCHEMA", "WEAVE_SCHEMA")
    if weave["stop_boundary"] != "STOP":
        reject("stop_boundary must be STOP", "WEAVE_SCHEMA", "WEAVE_SCHEMA")
    if not isinstance(weave["threads"], list) or not weave["threads"]:
        reject("threads must be a non-empty array", "WEAVE_SCHEMA", "WEAVE_SCHEMA")
    require_sha(weave["expected_base_tree_sha256"], "expected_base_tree_sha256")
    require_sha(weave["expected_candidate_tree_sha256"], "expected_candidate_tree_sha256")
    if not isinstance(weave["forbidden_actions"], list):
        reject("forbidden_actions must be an array", "WEAVE_SCHEMA", "WEAVE_SCHEMA")
    for action in FORBIDDEN_ACTIONS:
        if action not in weave["forbidden_actions"]:
            reject(f"forbidden action is not declared: {action}", "WEAVE_SCHEMA", "WEAVE_SCHEMA")


def validate_path_set(threads: list[dict[str, Any]]) -> list[tuple[dict[str, Any], PurePosixPath]]:
    seen_ids: set[str] = set()
    seen_paths: dict[str, str] = {}
    normalized: list[tuple[dict[str, Any], PurePosixPath]] = []
    for thread in threads:
        if not isinstance(thread, dict):
            reject("thread must be an object", "THREAD_SET_REJECTED", "THREAD_SET_VERIFY")
        for field in ("thread_id", "operation", "path"):
            if field not in thread:
                reject(f"thread missing {field}", "THREAD_SET_REJECTED", "THREAD_SET_VERIFY")
        thread_id = thread["thread_id"]
        if thread_id in seen_ids:
            reject(f"duplicate thread_id rejected: {thread_id}", "THREAD_SET_REJECTED", "THREAD_SET_VERIFY")
        seen_ids.add(thread_id)
        operation = thread["operation"]
        if operation not in {"ADD", "REPLACE", "DELETE"}:
            reject(f"unsupported operation: {operation}", "THREAD_SET_REJECTED", "THREAD_SET_VERIFY")
        rel = validate_relative_path(thread["path"])
        if is_protected_path(rel):
            reject(f"protected path requires a separate route: {rel.as_posix()}", "PROTECTED_PATH", "THREAD_SET_VERIFY")
        folded = rel.as_posix().casefold()
        if folded in seen_paths:
            reject(f"duplicate or case-fold collision rejected: {rel.as_posix()}", "THREAD_SET_REJECTED", "THREAD_SET_VERIFY")
        seen_paths[folded] = rel.as_posix()
        normalized.append((thread, rel))
    return normalized


def assert_existing_regular(path: Path, stage: str) -> None:
    if path.is_symlink():
        reject(f"symlink rejected: {path.name}", "SYMLINK_REJECTED", stage)
    if not path.exists() or not path.is_file():
        reject(f"required regular file is absent: {path.name}", "REGULAR_FILE_REQUIRED", stage)


def journal(journal_path: Path, checkpoint: str) -> None:
    with journal_path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps({"checkpoint": checkpoint}, sort_keys=True) + "\n")


def forbidden_confirmation() -> dict[str, Any]:
    return {
        "github_called": False,
        "network_called": False,
        "repository_checkout_mutated": False,
        "production_adapter_present": False,
        "persistent_writer_present": False,
        "workflow_authority_present": False,
        "standing_authority": "NO",
    }


def checkpoint_results(completed: list[str], rejected_stage: str | None = None) -> list[dict[str, str]]:
    results = [{"checkpoint": checkpoint, "status": "PASS"} for checkpoint in completed]
    if rejected_stage and rejected_stage not in completed:
        results.append({"checkpoint": rejected_stage, "status": "REJECTED"})
    return results


def make_receipt(
    weave: dict[str, Any],
    result: str,
    stop_point: str,
    completed_checkpoints: list[str],
    thread_results: list[dict[str, Any]],
    expected_base: str,
    observed_base: str | None,
    expected_candidate: str,
    observed_candidate: str | None,
    error_code: str | None = None,
    error_stage: str | None = None,
    message: str | None = None,
) -> dict[str, Any]:
    confirmation = forbidden_confirmation()
    receipt: dict[str, Any] = {
        "schema_version": "atlas-thread-engine-receipt-v1",
        "weave_id": weave.get("weave_id", "UNKNOWN"),
        "engine_state": ENGINE_STATE,
        "runtime_mode": MODE,
        "engine": {
            "version": VERSION,
            "state": ENGINE_STATE,
            "mode": MODE,
        },
        "expected_base_tree_sha256": expected_base,
        "observed_base_tree_sha256": observed_base,
        "checkpoint_results": checkpoint_results(completed_checkpoints, error_stage if result == "REJECTED" else None),
        "checkpoints": completed_checkpoints + (["STOP"] if result == "SUCCESS" and "STOP" not in completed_checkpoints else []),
        "last_completed_checkpoint": completed_checkpoints[-1] if completed_checkpoints else None,
        "thread_results": thread_results,
        "expected_candidate_tree_sha256": expected_candidate,
        "observed_candidate_tree_sha256": observed_candidate,
        "result": result,
        "error_code": error_code,
        "error_stage": error_stage,
        "stop_point": stop_point,
        "forbidden_action_confirmation": confirmation,
        "github_called": confirmation["github_called"],
        "network_called": confirmation["network_called"],
        "repository_checkout_mutated": confirmation["repository_checkout_mutated"],
        "production_adapter_present": confirmation["production_adapter_present"],
        "fixture_sandbox_classification": "unique-temporary-fixture-sandbox",
    }
    if message:
        receipt["message"] = message
    return receipt


def execute_weave(
    weave_path: Path,
    *,
    fixture_only: bool,
    audit_only: bool,
    sandbox_root: Path | None = None,
    allow_fixture_delete: bool = False,
    delete_authority_id: str | None = None,
    package_root: Path | None = None,
) -> dict[str, Any]:
    if not fixture_only or not audit_only:
        raise ThreadEngineError("explicit fixture-only and audit-only intent is required", "INTENT_REQUIRED", "PACKAGE_AUDIT")

    package_root = (package_root or Path(__file__).resolve().parents[1]).resolve()
    weave_path = weave_path.resolve()
    completed: list[str] = []
    thread_results: list[dict[str, Any]] = []
    observed_base: str | None = None
    observed_candidate: str | None = None
    weave: dict[str, Any] = {}
    root = Path(tempfile.mkdtemp(prefix="atlas-thread-engine-", dir=str(sandbox_root) if sandbox_root else None))
    worktree = root / "fixture-worktree"
    receipt_path = root / "receipt.json"
    journal_path = root / "state-journal.jsonl"

    def enter(checkpoint: str) -> None:
        journal(journal_path, checkpoint)

    def complete(checkpoint: str) -> None:
        completed.append(checkpoint)

    def write_rejection(error: ThreadEngineError) -> None:
        expected_base = str(weave.get("expected_base_tree_sha256", ""))
        expected_candidate = str(weave.get("expected_candidate_tree_sha256", ""))
        receipt = make_receipt(
            weave,
            "REJECTED",
            error.stop_point,
            completed,
            thread_results,
            expected_base,
            observed_base,
            expected_candidate,
            observed_candidate,
            error_code=error.error_code,
            error_stage=error.error_stage,
            message=str(error),
        )
        write_json(receipt_path, receipt)
        error.receipt = receipt

    try:
        enter("PACKAGE_AUDIT")
        reject_runtime_byproducts(package_root)
        complete("PACKAGE_AUDIT")

        enter("PARSER_PREFLIGHT")
        weave = load_weave(weave_path)
        receipt_path = root / str(weave.get("receipt_name", "receipt.json"))
        complete("PARSER_PREFLIGHT")

        enter("WEAVE_SCHEMA")
        validate_weave_shape(weave)
        complete("WEAVE_SCHEMA")

        resume_from = weave["resume_from"]
        if resume_from not in ("START", "PACKAGE_AUDIT"):
            reject(f"resume_from mismatch for new unique sandbox: {resume_from}", "RESUME_MISMATCH", "PACKAGE_AUDIT")

        enter("FIXTURE_BOUNDARY")
        base_rel = validate_relative_path(weave["base_fixture"])
        payload_rel = validate_relative_path(weave["payload_root"])
        base_fixture = resolve_under(package_root, base_rel)
        payload_root = resolve_under(package_root, payload_rel)
        if not base_fixture.exists() or not base_fixture.is_dir():
            reject("base_fixture is absent", "REGULAR_FILE_REQUIRED", "FIXTURE_BOUNDARY")
        if not payload_root.exists() or not payload_root.is_dir():
            reject("payload_root is absent", "REGULAR_FILE_REQUIRED", "FIXTURE_BOUNDARY")
        validate_no_symlinks(base_fixture)
        validate_no_symlinks(payload_root)
        shutil.copytree(base_fixture, worktree)
        complete("FIXTURE_BOUNDARY")

        enter("BASE_TREE_VERIFY")
        observed_base = tree_hash(worktree)
        if observed_base != weave["expected_base_tree_sha256"]:
            reject("base tree SHA-256 mismatch", "TREE_HASH_MISMATCH", "BASE_TREE_VERIFY")
        complete("BASE_TREE_VERIFY")

        enter("THREAD_SET_VERIFY")
        normalized_threads = validate_path_set(weave["threads"])
        complete("THREAD_SET_VERIFY")

        enter("CANDIDATE_STAGE")
        for thread, rel in normalized_threads:
            operation = thread["operation"]
            target = resolve_under(worktree, rel, "CANDIDATE_STAGE")
            if operation == "ADD":
                if target.exists():
                    reject(f"ADD target already exists: {rel.as_posix()}", "THREAD_SET_REJECTED", "CANDIDATE_STAGE")
                payload_rel_thread = validate_relative_path(thread.get("payload", ""))
                payload = resolve_under(payload_root, payload_rel_thread, "CANDIDATE_STAGE")
                assert_existing_regular(payload, "CANDIDATE_STAGE")
                require_sha(thread.get("payload_sha256", ""), "payload_sha256")
                require_sha(thread.get("expected_output_sha256", ""), "expected_output_sha256")
                payload_hash = sha256_file(payload)
                if payload_hash != thread["payload_sha256"]:
                    reject(f"payload hash mismatch: {thread['thread_id']}", "PAYLOAD_HASH_MISMATCH", "CANDIDATE_STAGE")
                if payload_hash != thread["expected_output_sha256"]:
                    reject(f"output hash mismatch: {thread['thread_id']}", "OUTPUT_HASH_MISMATCH", "CANDIDATE_STAGE")
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(payload, target)
                thread_results.append({"thread_id": thread["thread_id"], "operation": operation, "path": rel.as_posix(), "result": "APPLIED"})
            elif operation == "REPLACE":
                assert_existing_regular(target, "CANDIDATE_STAGE")
                require_sha(thread.get("source_sha256", ""), "source_sha256")
                source_hash = sha256_file(target)
                if source_hash != thread["source_sha256"]:
                    reject(f"source hash mismatch: {thread['thread_id']}", "SOURCE_HASH_MISMATCH", "CANDIDATE_STAGE")
                payload_rel_thread = validate_relative_path(thread.get("payload", ""))
                payload = resolve_under(payload_root, payload_rel_thread, "CANDIDATE_STAGE")
                assert_existing_regular(payload, "CANDIDATE_STAGE")
                require_sha(thread.get("payload_sha256", ""), "payload_sha256")
                require_sha(thread.get("expected_output_sha256", ""), "expected_output_sha256")
                payload_hash = sha256_file(payload)
                if payload_hash != thread["payload_sha256"]:
                    reject(f"payload hash mismatch: {thread['thread_id']}", "PAYLOAD_HASH_MISMATCH", "CANDIDATE_STAGE")
                if payload_hash != thread["expected_output_sha256"]:
                    reject(f"output hash mismatch: {thread['thread_id']}", "OUTPUT_HASH_MISMATCH", "CANDIDATE_STAGE")
                shutil.copyfile(payload, target)
                thread_results.append({"thread_id": thread["thread_id"], "operation": operation, "path": rel.as_posix(), "result": "APPLIED"})
            elif operation == "DELETE":
                assert_existing_regular(target, "CANDIDATE_STAGE")
                require_sha(thread.get("source_sha256", ""), "source_sha256")
                source_hash = sha256_file(target)
                if source_hash != thread["source_sha256"]:
                    reject(f"delete source hash mismatch: {thread['thread_id']}", "SOURCE_HASH_MISMATCH", "CANDIDATE_STAGE")
                declared_authority = thread.get("delete_authority_id")
                if not allow_fixture_delete or not delete_authority_id or declared_authority != delete_authority_id:
                    reject(f"DELETE lacks matching fixture authority: {thread['thread_id']}", "DELETE_AUTHORITY_REQUIRED", "CANDIDATE_STAGE")
                target.unlink()
                thread_results.append({"thread_id": thread["thread_id"], "operation": operation, "path": rel.as_posix(), "result": "APPLIED"})
        complete("CANDIDATE_STAGE")

        enter("CANDIDATE_TREE_VERIFY")
        observed_candidate = tree_hash(worktree)
        if observed_candidate != weave["expected_candidate_tree_sha256"]:
            reject("candidate tree SHA-256 mismatch", "CANDIDATE_TREE_MISMATCH", "CANDIDATE_TREE_VERIFY")
        complete("CANDIDATE_TREE_VERIFY")

        enter("RECEIPT")
        complete("RECEIPT")
        receipt = make_receipt(
            weave,
            "SUCCESS",
            "STOP",
            completed,
            thread_results,
            weave["expected_base_tree_sha256"],
            observed_base,
            weave["expected_candidate_tree_sha256"],
            observed_candidate,
        )
        write_json(receipt_path, receipt)
        return receipt
    except ThreadEngineError as exc:
        if not exc.receipt:
            write_rejection(exc)
        raise exc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Atlas Gate 7B disabled Thread Engine fixture runner")
    parser.add_argument("--weave", required=True)
    parser.add_argument("--fixture-only", action="store_true")
    parser.add_argument("--audit-only", action="store_true")
    parser.add_argument("--sandbox-root")
    parser.add_argument("--allow-fixture-delete", action="store_true")
    parser.add_argument("--delete-authority-id")
    args = parser.parse_args(argv)

    try:
        receipt = execute_weave(
            Path(args.weave),
            fixture_only=args.fixture_only,
            audit_only=args.audit_only,
            sandbox_root=Path(args.sandbox_root) if args.sandbox_root else None,
            allow_fixture_delete=args.allow_fixture_delete,
            delete_authority_id=args.delete_authority_id,
        )
        sys.stdout.write(stable_json(receipt))
        return 0
    except ThreadEngineError as exc:
        if exc.receipt:
            sys.stderr.write(stable_json(exc.receipt))
        else:
            sys.stderr.write(str(exc) + "\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
