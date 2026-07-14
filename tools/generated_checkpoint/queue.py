from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Sequence

QUEUE_SCHEMA = "atlas.generated-checkpoint.queue"
QUEUE_VERSION = "1.0.0"
GENERATED_HEAD_PREFIX = "generated/checkpoint-"
GENERATED_TITLE_PREFIX = "generated: deterministic checkpoint "
HEX40 = re.compile(r"^[0-9a-f]{40}$")
EXPECTED_KEYS = {
    "number",
    "isDraft",
    "headRefName",
    "headRefOid",
    "baseRefName",
    "title",
}


class QueueError(Exception):
    def __init__(self, message: str, code: str = "GENERATED_CHECKPOINT_QUEUE_REJECTED") -> None:
        super().__init__(message)
        self.code = code


def stable_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n"


def classify_open_pull_requests(pull_requests: Any) -> dict[str, Any]:
    if not isinstance(pull_requests, list) or len(pull_requests) > 1000:
        raise QueueError(
            "generated checkpoint open-PR queue is malformed or unbounded",
            "GENERATED_CHECKPOINT_QUEUE_HISTORY",
        )

    checkpoints: list[dict[str, Any]] = []
    for item in pull_requests:
        if not isinstance(item, dict) or set(item) != EXPECTED_KEYS:
            raise QueueError(
                "generated checkpoint open-PR entry has an invalid closed shape",
                "GENERATED_CHECKPOINT_QUEUE_ENTRY",
            )

        number = item["number"]
        is_draft = item["isDraft"]
        head = item["headRefName"]
        head_sha = item["headRefOid"]
        base = item["baseRefName"]
        title = item["title"]
        if (
            not isinstance(number, int)
            or isinstance(number, bool)
            or number < 1
            or not isinstance(is_draft, bool)
            or not isinstance(head, str)
            or not isinstance(head_sha, str)
            or not isinstance(base, str)
            or not isinstance(title, str)
        ):
            raise QueueError(
                "generated checkpoint open-PR entry contains invalid values",
                "GENERATED_CHECKPOINT_QUEUE_ENTRY",
            )

        head_marker = head.startswith(GENERATED_HEAD_PREFIX)
        title_marker = title.startswith(GENERATED_TITLE_PREFIX)
        if head_marker != title_marker:
            raise QueueError(
                "generated checkpoint open-PR identity is inconsistent",
                "GENERATED_CHECKPOINT_QUEUE_IDENTITY",
            )
        if not head_marker:
            continue
        if not is_draft:
            raise QueueError(
                "generated checkpoint open PR is not draft",
                "GENERATED_CHECKPOINT_QUEUE_STATE",
            )
        if base != "main":
            raise QueueError(
                "generated checkpoint open PR does not target main",
                "GENERATED_CHECKPOINT_QUEUE_BASE",
            )
        if HEX40.fullmatch(head_sha) is None:
            raise QueueError(
                "generated checkpoint open PR head SHA is invalid",
                "GENERATED_CHECKPOINT_QUEUE_HEAD",
            )
        checkpoints.append(
            {
                "number": number,
                "isDraft": True,
                "headRefName": head,
                "headRefOid": head_sha,
                "baseRefName": base,
                "title": title,
            }
        )

    if len(checkpoints) > 1:
        raise QueueError(
            "multiple generated checkpoint PRs are open",
            "GENERATED_CHECKPOINT_QUEUE_MULTIPLE_OPEN",
        )

    if checkpoints:
        return {
            "schema_id": QUEUE_SCHEMA,
            "schema_version": QUEUE_VERSION,
            "result": "DEFERRED_OPEN_CHECKPOINT",
            "open_checkpoint_count": 1,
            "checkpoint": checkpoints[0],
            "mutation_authorized": False,
        }

    return {
        "schema_id": QUEUE_SCHEMA,
        "schema_version": QUEUE_VERSION,
        "result": "CLEAR",
        "open_checkpoint_count": 0,
        "checkpoint": None,
        "mutation_authorized": False,
    }


def load_pull_requests(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise QueueError(
            "generated checkpoint open-PR queue JSON is unreadable",
            "GENERATED_CHECKPOINT_QUEUE_JSON",
        ) from exc


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Classify the open generated checkpoint queue.")
    parser.add_argument("--pull-requests", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        result = classify_open_pull_requests(load_pull_requests(args.pull_requests))
    except QueueError as exc:
        print(stable_json({"result": "REJECTED", "error": str(exc), "error_code": exc.code}), end="")
        return 2
    print(stable_json(result), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
