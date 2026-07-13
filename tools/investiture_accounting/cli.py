from __future__ import annotations

import argparse
import json
import os
import stat
from pathlib import Path
from typing import Any

from .core import InvestitureError, event_from_bytes, sha256_bytes, stable_json
from .storage import append_event, initialize_store, recover_generation, recover_interrupted, rollback_plan, verify_store


def _path(value: str) -> Path:
    return Path(value)


def _print(value: dict[str, Any]) -> None:
    print(stable_json(value).decode("utf-8"), end="")


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog="python -m tools.investiture_accounting")
    commands = root.add_subparsers(dest="command", required=True)

    validate = commands.add_parser("validate-event")
    validate.add_argument("--event", required=True, type=_path)

    initialize = commands.add_parser("init")
    initialize.add_argument("--store-root", required=True, type=_path)
    initialize.add_argument("--ledger-id", required=True)
    initialize.add_argument("--generation-id", required=True)
    initialize.add_argument("--created-at", required=True)
    initialize.add_argument("--request-id", required=True)

    append = commands.add_parser("append")
    append.add_argument("--store-root", required=True, type=_path)
    append.add_argument("--expected-head", required=True)
    append.add_argument("--request-id", required=True)
    append.add_argument("--event", required=True, type=_path)

    verify = commands.add_parser("verify")
    verify.add_argument("--store-root", required=True, type=_path)

    summarize = commands.add_parser("summarize")
    summarize.add_argument("--store-root", required=True, type=_path)
    summarize.add_argument("--scope-id", required=True)

    interrupted = commands.add_parser("recover-interrupted")
    interrupted.add_argument("--store-root", required=True, type=_path)
    interrupted.add_argument("--request-id", required=True)
    interrupted.add_argument("--expected-head", required=True)

    generation = commands.add_parser("recover-generation")
    generation.add_argument("--source-root", required=True, type=_path)
    generation.add_argument("--destination-root", required=True, type=_path)
    generation.add_argument("--expected-valid-head", required=True)
    generation.add_argument("--new-generation-id", required=True)
    generation.add_argument("--created-at", required=True)
    generation.add_argument("--request-id", required=True)

    rollback = commands.add_parser("rollback-plan")
    rollback.add_argument("--current-root", required=True, type=_path)
    rollback.add_argument("--target-root", required=True, type=_path)
    rollback.add_argument("--expected-current-head", required=True)
    rollback.add_argument("--expected-target-head", required=True)
    return root


def _read_event(path: Path) -> bytes:
    try:
        before = path.lstat()
        attributes = getattr(before, "st_file_attributes", 0)
        reparse = bool(attributes & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0))
        if not stat.S_ISREG(before.st_mode) or reparse or before.st_size > 1_000_000 or before.st_nlink != 1:
            raise InvestitureError("EVENT_FILE_INVALID")
        descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
        try:
            opened = os.fstat(descriptor)
            if (
                not stat.S_ISREG(opened.st_mode)
                or opened.st_size > 1_000_000
                or opened.st_nlink != 1
                or (opened.st_dev, opened.st_ino) != (before.st_dev, before.st_ino)
            ):
                raise InvestitureError("EVENT_FILE_INVALID")
            chunks: list[bytes] = []
            while True:
                chunk = os.read(descriptor, 65536)
                if not chunk:
                    break
                chunks.append(chunk)
            raw = b"".join(chunks)
            after_open = os.fstat(descriptor)
        finally:
            os.close(descriptor)
        after_path = path.lstat()
        identity = (before.st_dev, before.st_ino)
        if (
            (after_open.st_dev, after_open.st_ino) != identity
            or (after_path.st_dev, after_path.st_ino) != identity
            or after_path.st_size != len(raw)
        ):
            raise InvestitureError("EVENT_FILE_INVALID")
        return raw
    except OSError as exc:
        raise InvestitureError("EVENT_FILE_INVALID") from exc


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.command == "validate-event":
            raw = _read_event(args.event)
            event = event_from_bytes(raw)
            result = {"result": "VALID", "event_id": event["event_id"], "event_sha256": sha256_bytes(stable_json(event))}
        elif args.command == "init":
            manifest = initialize_store(
                args.store_root,
                ledger_id=args.ledger_id,
                generation_id=args.generation_id,
                created_at=args.created_at,
            )
            result = {
                "result": "INITIALIZED",
                "ledger_id": manifest["ledger_id"],
                "generation_id": manifest["generation_id"],
                "manifest_sha256": manifest["manifest_sha256"],
                "request_id_sha256": sha256_bytes(args.request_id.encode("utf-8")),
            }
        elif args.command == "append":
            result = append_event(
                args.store_root,
                _read_event(args.event),
                expected_head=args.expected_head,
                request_id=args.request_id,
            )
        elif args.command == "verify":
            result = verify_store(args.store_root)
        elif args.command == "summarize":
            result = verify_store(args.store_root)
            if result["generation_id"] != args.scope_id:
                raise InvestitureError("SUMMARY_SCOPE_MISMATCH")
        elif args.command == "recover-interrupted":
            result = recover_interrupted(args.store_root, request_id=args.request_id, expected_head=args.expected_head)
        elif args.command == "recover-generation":
            result = recover_generation(
                args.source_root,
                args.destination_root,
                expected_valid_head=args.expected_valid_head,
                new_generation_id=args.new_generation_id,
                created_at=args.created_at,
            )
            result["request_id_sha256"] = sha256_bytes(args.request_id.encode("utf-8"))
        elif args.command == "rollback-plan":
            result = rollback_plan(
                args.current_root,
                args.target_root,
                expected_current_head=args.expected_current_head,
                expected_target_head=args.expected_target_head,
            )
        else:
            raise InvestitureError("COMMAND_INVALID")
    except InvestitureError as exc:
        _print({"result": "REJECTED", "error_code": exc.code})
        return 1
    except (OSError, UnicodeError, json.JSONDecodeError):
        _print({"result": "REJECTED", "error_code": "IO_OR_JSON_FAILURE"})
        return 1
    _print(result)
    return 0
