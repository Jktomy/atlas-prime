from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any, Mapping, Sequence

QUEUE_SCHEMA = "atlas.generated-checkpoint.queue"
QUEUE_VERSION = "1.0.0"
GENERATED_HEAD_PREFIX = "generated/checkpoint-"
GENERATED_TITLE_PREFIX = "generated: deterministic checkpoint "
MAX_OPEN_PULL_REQUESTS = 1000
QUERY_LIMIT = MAX_OPEN_PULL_REQUESTS + 1
QUERY_STATE = "open"
QUERY_FIELDS = (
    "number",
    "state",
    "isDraft",
    "isCrossRepository",
    "author",
    "headRefName",
    "headRefOid",
    "headRepository",
    "headRepositoryOwner",
    "baseRefName",
    "baseRefOid",
    "title",
    "body",
)
PROJECTION_FIELDS = (
    "number",
    "state",
    "isDraft",
    "isCrossRepository",
    "authorLogin",
    "authorIsBot",
    "headRefName",
    "headRefOid",
    "headRepositoryNameWithOwner",
    "headRepositoryOwnerLogin",
    "baseRefName",
    "baseRefOid",
    "title",
    "body",
)
EXPECTED_KEYS = set(PROJECTION_FIELDS)
CONTEXT_KEYS = {
    "repository",
    "event_name",
    "event_base_sha",
    "current_main_sha",
    "workflow_ref",
    "workflow_source_sha",
    "workflow_run_id",
    "workflow_run_attempt",
    "actor",
    "triggering_actor",
    "repository_owner",
    "credential_principal",
    "credential_mode",
}
EXPECTED_WORKFLOW_REF = (
    "Jktomy/atlas-prime/.github/workflows/"
    "generated-checkpoint-publisher.yml@refs/heads/main"
)
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
POSITIVE_DIGITS = re.compile(r"^[1-9][0-9]*$")
MISSION_ID = re.compile(r"^[A-Z0-9]+(?:-[A-Z0-9]+)*$")
GENERATED_TITLE = re.compile(
    rf"^{re.escape(GENERATED_TITLE_PREFIX)}(?P<mission>[A-Z0-9]+(?:-[A-Z0-9]+)*)$"
)
GENERATED_BODY_PREFIX = re.compile(
    r"\AHosted RP-C06 generated checkpoint `(?P<mission>[A-Z0-9]+(?:-[A-Z0-9]+)*)`\.\n\n"
    r"- Exact base: `(?P<base>[0-9a-f]{40})`\n"
    r"- Source fingerprint: `sha256:(?P<source>[0-9a-f]{64})`\n"
    r"- Workflow run: `(?P<run>[1-9][0-9]*)` attempt `(?P<attempt>[1-9][0-9]*)`\n"
    r"- Replay identity: `sha256:(?P<replay>[0-9a-f]{64})`\n"
    r"- Ubuntu/Windows register parity: exact\n"
    r"- Route: singular Thread Engine; draft PR readback stop\n"
    r"- Quest/capability promotion: none\n"
)


class QueueError(Exception):
    def __init__(
        self,
        message: str,
        code: str = "GENERATED_CHECKPOINT_QUEUE_REJECTED",
        *,
        input_sha256: str | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.input_sha256 = input_sha256


def stable_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n"


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _canonical_sha256(value: Any) -> str:
    return sha256_bytes(stable_json(value).encode("utf-8"))


def _seal_receipt(receipt: dict[str, Any]) -> dict[str, Any]:
    sealed = dict(receipt)
    sealed["receipt_sha256"] = "0" * 64
    sealed["receipt_sha256"] = _canonical_sha256(sealed)
    return sealed


def _closed_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def _reject_json_constant(_: str) -> None:
    raise ValueError("non-finite JSON number")


def _validate_context(context: Mapping[str, Any]) -> dict[str, str]:
    if not isinstance(context, Mapping) or set(context) != CONTEXT_KEYS:
        raise QueueError(
            "generated checkpoint queue context has an invalid closed shape",
            "GENERATED_CHECKPOINT_QUEUE_CONTEXT",
        )
    result: dict[str, str] = {}
    for key in CONTEXT_KEYS:
        value = context[key]
        if not isinstance(value, str) or not value:
            raise QueueError(
                "generated checkpoint queue context contains invalid values",
                "GENERATED_CHECKPOINT_QUEUE_CONTEXT",
            )
        result[key] = value
    constants = {
        "repository": "Jktomy/atlas-prime",
        "workflow_ref": EXPECTED_WORKFLOW_REF,
        "actor": "Jktomy",
        "triggering_actor": "Jktomy",
        "repository_owner": "Jktomy",
        "credential_principal": "github-actions[bot]",
        "credential_mode": "GITHUB_TOKEN",
    }
    if any(result[key] != expected for key, expected in constants.items()):
        raise QueueError(
            "generated checkpoint queue context identity is invalid",
            "GENERATED_CHECKPOINT_QUEUE_CONTEXT",
        )
    if result["event_name"] not in {"push", "workflow_dispatch"}:
        raise QueueError(
            "generated checkpoint queue event is invalid",
            "GENERATED_CHECKPOINT_QUEUE_CONTEXT",
        )
    for key in ("event_base_sha", "current_main_sha", "workflow_source_sha"):
        if HEX40.fullmatch(result[key]) is None:
            raise QueueError(
                "generated checkpoint queue context SHA is invalid",
                "GENERATED_CHECKPOINT_QUEUE_CONTEXT",
            )
    if result["event_base_sha"] != result["workflow_source_sha"]:
        raise QueueError(
            "generated checkpoint queue event base differs from workflow source",
            "GENERATED_CHECKPOINT_QUEUE_STALE_BASE",
        )
    for key in ("workflow_run_id", "workflow_run_attempt"):
        if POSITIVE_DIGITS.fullmatch(result[key]) is None:
            raise QueueError(
                "generated checkpoint queue workflow identity is invalid",
                "GENERATED_CHECKPOINT_QUEUE_CONTEXT",
            )
    return result


def _query_evidence(pull_requests: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "state": QUERY_STATE,
        "limit": QUERY_LIMIT,
        "max_accepted_entries": MAX_OPEN_PULL_REQUESTS,
        "requested_fields": list(QUERY_FIELDS),
        "projection_fields": list(PROJECTION_FIELDS),
        "returned_count": len(pull_requests),
        "snapshot_sha256": _canonical_sha256(pull_requests),
    }


def _receipt_base(context: Mapping[str, str], pull_requests: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema_id": QUEUE_SCHEMA,
        "schema_version": QUEUE_VERSION,
        "repository": context["repository"],
        "event_name": context["event_name"],
        "event_base_sha": context["event_base_sha"],
        "current_main_sha": context["current_main_sha"],
        "workflow_ref": context["workflow_ref"],
        "workflow_source_sha": context["workflow_source_sha"],
        "workflow_run_id": context["workflow_run_id"],
        "workflow_run_attempt": context["workflow_run_attempt"],
        "actor": context["actor"],
        "triggering_actor": context["triggering_actor"],
        "repository_owner": context["repository_owner"],
        "credential_principal": context["credential_principal"],
        "credential_mode": context["credential_mode"],
        "query": _query_evidence(pull_requests),
        "mutation_authorized": False,
    }


def _validate_entry(item: Any) -> dict[str, Any]:
    if not isinstance(item, dict) or set(item) != EXPECTED_KEYS:
        raise QueueError(
            "generated checkpoint open-PR entry has an invalid closed shape",
            "GENERATED_CHECKPOINT_QUEUE_ENTRY",
        )
    number = item["number"]
    scalar_types = {
        "state": str,
        "isDraft": bool,
        "isCrossRepository": bool,
        "headRefName": str,
        "headRefOid": str,
        "baseRefName": str,
        "baseRefOid": str,
        "title": str,
        "body": str,
    }
    if not isinstance(number, int) or isinstance(number, bool) or number < 1:
        raise QueueError(
            "generated checkpoint open-PR entry contains invalid values",
            "GENERATED_CHECKPOINT_QUEUE_ENTRY",
        )
    if any(not isinstance(item[key], expected) for key, expected in scalar_types.items()):
        raise QueueError(
            "generated checkpoint open-PR entry contains invalid values",
            "GENERATED_CHECKPOINT_QUEUE_ENTRY",
        )
    for key, expected in (
        ("authorLogin", str),
        ("authorIsBot", bool),
        ("headRepositoryNameWithOwner", str),
        ("headRepositoryOwnerLogin", str),
    ):
        if item[key] is not None and not isinstance(item[key], expected):
            raise QueueError(
                "generated checkpoint open-PR entry contains invalid identity values",
                "GENERATED_CHECKPOINT_QUEUE_ENTRY",
            )
    if item["state"] != "OPEN" or HEX40.fullmatch(item["headRefOid"]) is None:
        raise QueueError(
            "generated checkpoint open-PR query result is inconsistent",
            "GENERATED_CHECKPOINT_QUEUE_ENTRY",
        )
    if HEX40.fullmatch(item["baseRefOid"]) is None:
        raise QueueError(
            "generated checkpoint open-PR base SHA is invalid",
            "GENERATED_CHECKPOINT_QUEUE_ENTRY",
        )
    return dict(item)


def _checkpoint_identity(item: dict[str, Any]) -> dict[str, Any] | None:
    head = item["headRefName"]
    title = item["title"]
    head_marker = head.startswith(GENERATED_HEAD_PREFIX)
    title_marker = title.startswith(GENERATED_TITLE_PREFIX)
    if head_marker != title_marker:
        raise QueueError(
            "generated checkpoint open-PR identity is inconsistent",
            "GENERATED_CHECKPOINT_QUEUE_IDENTITY",
        )
    if not head_marker:
        return None
    if item["isDraft"] is not True:
        raise QueueError(
            "generated checkpoint open PR is not draft",
            "GENERATED_CHECKPOINT_QUEUE_STATE",
        )
    exact_identity = {
        "isCrossRepository": False,
        "authorLogin": "app/github-actions",
        "authorIsBot": True,
        "headRepositoryNameWithOwner": "Jktomy/atlas-prime",
        "headRepositoryOwnerLogin": "Jktomy",
        "baseRefName": "main",
    }
    if any(item[key] != expected for key, expected in exact_identity.items()):
        raise QueueError(
            "generated checkpoint open PR is not publisher-owned",
            "GENERATED_CHECKPOINT_QUEUE_IDENTITY",
        )
    title_match = GENERATED_TITLE.fullmatch(title)
    body = item["body"].replace("\r\n", "\n").replace("\r", "\n")
    body_match = GENERATED_BODY_PREFIX.match(body)
    if title_match is None or body_match is None:
        raise QueueError(
            "generated checkpoint open PR provenance is invalid",
            "GENERATED_CHECKPOINT_QUEUE_PROVENANCE",
        )
    identity = body_match.groupdict()
    mission = title_match.group("mission")
    if MISSION_ID.fullmatch(mission) is None or identity["mission"] != mission:
        raise QueueError(
            "generated checkpoint mission identity is inconsistent",
            "GENERATED_CHECKPOINT_QUEUE_IDENTITY",
        )
    if identity["base"] != item["baseRefOid"]:
        raise QueueError(
            "generated checkpoint body base does not match PR readback",
            "GENERATED_CHECKPOINT_QUEUE_BASE",
        )
    replay_digest = identity["replay"]
    expected_branch = f"{GENERATED_HEAD_PREFIX}{mission.lower()}-{replay_digest[:12]}"
    if head != expected_branch:
        raise QueueError(
            "generated checkpoint branch does not match replay identity",
            "GENERATED_CHECKPOINT_QUEUE_IDENTITY",
        )
    return {
        "number": item["number"],
        "is_draft": True,
        "author_login": item["authorLogin"],
        "author_is_bot": item["authorIsBot"],
        "head_repository": item["headRepositoryNameWithOwner"],
        "head_repository_owner": item["headRepositoryOwnerLogin"],
        "head_branch": head,
        "head_sha": item["headRefOid"],
        "base_branch": item["baseRefName"],
        "base_sha": item["baseRefOid"],
        "title": title,
        "mission_id": mission,
        "source_fingerprint": f"sha256:{identity['source']}",
        "publisher_workflow_run_id": identity["run"],
        "publisher_workflow_run_attempt": identity["attempt"],
        "replay_identity_sha256": replay_digest,
        "canonical_body_prefix_sha256": sha256_bytes(
            body_match.group(0).encode("utf-8")
        ),
    }


def classify_open_pull_requests(
    pull_requests: Any,
    context: Mapping[str, Any],
) -> dict[str, Any]:
    validated_context = _validate_context(context)
    if not isinstance(pull_requests, list) or len(pull_requests) > MAX_OPEN_PULL_REQUESTS:
        raise QueueError(
            "generated checkpoint open-PR queue is malformed or exceeds its bound",
            "GENERATED_CHECKPOINT_QUEUE_HISTORY",
        )

    validated = [_validate_entry(item) for item in pull_requests]
    validated.sort(key=lambda item: item["number"])
    numbers = [item["number"] for item in validated]
    if len(numbers) != len(set(numbers)):
        raise QueueError(
            "generated checkpoint open-PR queue contains duplicate PR numbers",
            "GENERATED_CHECKPOINT_QUEUE_DUPLICATE",
        )

    checkpoints = [
        checkpoint
        for item in validated
        if (checkpoint := _checkpoint_identity(item)) is not None
    ]
    if len(checkpoints) > 1:
        raise QueueError(
            "multiple generated checkpoint PRs are open",
            "GENERATED_CHECKPOINT_QUEUE_MULTIPLE_OPEN",
        )
    if not checkpoints and validated_context["current_main_sha"] != validated_context["event_base_sha"]:
        raise QueueError(
            "generated checkpoint queue CLEAR decision has a stale event base",
            "GENERATED_CHECKPOINT_QUEUE_STALE_BASE",
        )

    receipt = _receipt_base(validated_context, validated)
    if checkpoints:
        receipt.update(
            {
                "result": "DEFERRED_OPEN_CHECKPOINT",
                "open_checkpoint_count": 1,
                "checkpoint": checkpoints[0],
                "error_code": None,
            }
        )
    else:
        receipt.update(
            {
                "result": "CLEAR",
                "open_checkpoint_count": 0,
                "checkpoint": None,
                "error_code": None,
            }
        )
    return _seal_receipt(receipt)


def load_pull_requests(path: Path) -> tuple[Any, str]:
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise QueueError(
            "generated checkpoint open-PR queue JSON is unreadable",
            "GENERATED_CHECKPOINT_QUEUE_JSON",
        ) from exc
    raw_sha256 = sha256_bytes(raw)
    try:
        return (
            json.loads(
                raw.decode("utf-8"),
                object_pairs_hook=_closed_pairs,
                parse_constant=_reject_json_constant,
            ),
            raw_sha256,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise QueueError(
            "generated checkpoint open-PR queue JSON is invalid",
            "GENERATED_CHECKPOINT_QUEUE_JSON",
            input_sha256=raw_sha256,
        ) from exc


def _rejection_receipt(
    context: Mapping[str, Any],
    exc: QueueError,
    *,
    pull_requests: Any,
    input_sha256: str,
) -> dict[str, Any]:
    try:
        validated_context = _validate_context(context)
    except QueueError:
        validated_context = {
            key: context.get(key) if isinstance(context.get(key), str) else "INVALID"
            for key in CONTEXT_KEYS
        }
    returned_count = len(pull_requests) if isinstance(pull_requests, list) else None
    snapshot_sha256 = (
        _canonical_sha256(pull_requests)
        if pull_requests is not None
        else input_sha256
    )
    receipt = {
        "schema_id": QUEUE_SCHEMA,
        "schema_version": QUEUE_VERSION,
        **validated_context,
        "query": {
            "state": QUERY_STATE,
            "limit": QUERY_LIMIT,
            "max_accepted_entries": MAX_OPEN_PULL_REQUESTS,
            "requested_fields": list(QUERY_FIELDS),
            "projection_fields": list(PROJECTION_FIELDS),
            "returned_count": returned_count,
            "snapshot_sha256": snapshot_sha256,
        },
        "result": "REJECTED",
        "open_checkpoint_count": None,
        "checkpoint": None,
        "mutation_authorized": False,
        "error_code": exc.code,
    }
    return _seal_receipt(receipt)


def _context_from_args(args: argparse.Namespace) -> dict[str, str]:
    return {
        "repository": args.repository,
        "event_name": args.event_name,
        "event_base_sha": args.event_base_sha,
        "current_main_sha": args.current_main_sha,
        "workflow_ref": args.workflow_ref,
        "workflow_source_sha": args.workflow_source_sha,
        "workflow_run_id": args.workflow_run_id,
        "workflow_run_attempt": args.workflow_run_attempt,
        "actor": args.actor,
        "triggering_actor": args.triggering_actor,
        "repository_owner": args.repository_owner,
        "credential_principal": args.credential_principal,
        "credential_mode": args.credential_mode,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Classify the open generated checkpoint queue.")
    parser.add_argument("--pull-requests", type=Path, required=True)
    parser.add_argument("--repository", required=True)
    parser.add_argument("--event-name", required=True)
    parser.add_argument("--event-base-sha", required=True)
    parser.add_argument("--current-main-sha", required=True)
    parser.add_argument("--workflow-ref", required=True)
    parser.add_argument("--workflow-source-sha", required=True)
    parser.add_argument("--workflow-run-id", required=True)
    parser.add_argument("--workflow-run-attempt", required=True)
    parser.add_argument("--actor", required=True)
    parser.add_argument("--triggering-actor", required=True)
    parser.add_argument("--repository-owner", required=True)
    parser.add_argument("--credential-principal", required=True)
    parser.add_argument("--credential-mode", required=True)
    args = parser.parse_args(argv)
    context = _context_from_args(args)
    pull_requests: Any = None
    input_sha256 = "0" * 64
    try:
        pull_requests, input_sha256 = load_pull_requests(args.pull_requests)
        result = classify_open_pull_requests(pull_requests, context)
    except QueueError as exc:
        if exc.input_sha256 is not None:
            input_sha256 = exc.input_sha256
        print(
            stable_json(
                _rejection_receipt(
                    context,
                    exc,
                    pull_requests=pull_requests,
                    input_sha256=input_sha256,
                )
            ),
            end="",
        )
        return 2
    print(stable_json(result), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
