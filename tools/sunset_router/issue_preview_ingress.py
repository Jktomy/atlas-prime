from __future__ import annotations

import argparse
import hashlib
import json
import re
import tempfile
from pathlib import Path
from typing import Any

from tools.atlas_lifecycle.errors import LifecycleError
from tools.atlas_lifecycle.jsonio import canonical_bytes
from tools.atlas_lifecycle.protection import enforce_clean_values, enforce_pointer_contract
from tools.atlas_lifecycle.repository import observed_head
from tools.atlas_lifecycle.schema import SchemaValidator
from tools.sunset_router.core import verify_router_preview

EXPECTED_REPOSITORY = "Jktomy/atlas-prime"
EXPECTED_OWNER = "Jktomy"
EXPECTED_ISSUE = 257
EXPECTED_BRANCH = "main"
MAX_COMMENT_BYTES = 32 * 1024
MAX_EVENT_BYTES = 1024 * 1024
MAX_COMMENTS_BYTES = 8 * 1024 * 1024
MAX_RESULT_COMMENT_BYTES = 60 * 1024
INTAKE_LANGUAGE = "atlas-sunset-router-preview-intake-v1"
RESULT_MARKER = "<!-- atlas-sunset-router-preview-receipt-v1 -->"
BINDING_LANGUAGE = "atlas-sunset-router-preview-binding-v1"
INTAKE_PATTERN = re.compile(
    rf"\A```{INTAKE_LANGUAGE}\n(?P<payload>[^\n]+)\n```(?:\n)?\Z"
)
BINDING_PATTERN = re.compile(
    rf"```{BINDING_LANGUAGE}\n(?P<payload>[^\n]+)\n```"
)


def _fail(code: str, message: str) -> None:
    raise LifecycleError(code, message)


def _digest(data: bytes) -> str:
    return f"sha256:{hashlib.sha256(data).hexdigest()}"


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            _fail("SUNSET_PREVIEW_INTAKE_JSON", "JSON contains a duplicate key")
        value[key] = item
    return value


def _reject_float(value: str) -> None:
    _fail("SUNSET_PREVIEW_INTAKE_JSON", "floating-point values are forbidden")


def _reject_constant(value: str) -> None:
    _fail("SUNSET_PREVIEW_INTAKE_JSON", "non-finite values are forbidden")


def _loads(text: str) -> Any:
    try:
        return json.loads(
            text,
            object_pairs_hook=_reject_duplicate_keys,
            parse_float=_reject_float,
            parse_constant=_reject_constant,
        )
    except LifecycleError:
        raise
    except (TypeError, ValueError, json.JSONDecodeError) as exc:
        raise LifecycleError(
            "SUNSET_PREVIEW_INTAKE_JSON", "JSON input is malformed"
        ) from exc


def _read_json(path: Path, limit: int) -> Any:
    if not path.is_file() or path.is_symlink():
        _fail("SUNSET_PREVIEW_INTAKE_FILE", "required JSON input is unavailable")
    data = path.read_bytes()
    if len(data) > limit:
        _fail("SUNSET_PREVIEW_INTAKE_SIZE", "JSON input exceeds its bounded size")
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise LifecycleError(
            "SUNSET_PREVIEW_INTAKE_ENCODING", "JSON input is not UTF-8"
        ) from exc
    return _loads(text)


def _read_canonical(path: Path, limit: int) -> dict[str, Any]:
    value = _read_json(path, limit)
    if not isinstance(value, dict) or path.read_bytes() != canonical_bytes(value):
        _fail("SUNSET_PREVIEW_INTAKE_CANONICAL", "artifact is not canonical JSON")
    return value


def _temporary_path(repo_root: Path, path: Path) -> Path:
    destination = path.resolve()
    repository = repo_root.resolve()
    temporary = Path(tempfile.gettempdir()).resolve()
    if destination == repository or repository in destination.parents:
        _fail("SUNSET_PREVIEW_INTAKE_OUTPUT_SCOPE", "output cannot be inside the repository")
    if temporary != destination.parent and temporary not in destination.parents:
        _fail("SUNSET_PREVIEW_INTAKE_OUTPUT_SCOPE", "output must be in system temporary storage")
    if destination.exists() or destination.is_symlink():
        _fail("SUNSET_PREVIEW_INTAKE_OUTPUT_EXISTS", "output path already exists")
    destination.parent.mkdir(parents=True, exist_ok=True)
    return destination


def _write_canonical(repo_root: Path, path: Path, value: dict[str, Any]) -> None:
    _temporary_path(repo_root, path).write_bytes(canonical_bytes(value))


def _write_text(repo_root: Path, path: Path, value: str) -> None:
    destination = _temporary_path(repo_root, path)
    data = value.encode("utf-8")
    if len(data) > MAX_RESULT_COMMENT_BYTES:
        _fail("SUNSET_PREVIEW_RESULT_SIZE", "rendered Preview comment exceeds its bounded size")
    destination.write_bytes(data)


def _extract_envelope(body: Any) -> dict[str, Any]:
    if not isinstance(body, str):
        _fail("SUNSET_PREVIEW_INTAKE_BODY", "Issue comment body is unavailable")
    encoded = body.encode("utf-8")
    if len(encoded) > MAX_COMMENT_BYTES:
        _fail("SUNSET_PREVIEW_INTAKE_SIZE", "Issue comment exceeds 32 KiB")
    if "\r" in body:
        _fail("SUNSET_PREVIEW_INTAKE_CANONICAL", "Issue comment must use LF newlines")
    match = INTAKE_PATTERN.fullmatch(body)
    if match is None:
        _fail(
            "SUNSET_PREVIEW_INTAKE_FORMAT",
            f"Issue comment must contain only one `{INTAKE_LANGUAGE}` canonical JSON block",
        )
    payload = match.group("payload")
    value = _loads(payload)
    if not isinstance(value, dict) or payload.encode("utf-8") + b"\n" != canonical_bytes(value):
        _fail("SUNSET_PREVIEW_INTAKE_CANONICAL", "intake JSON must use canonical bytes")
    return value


def _binding_from_comment(body: Any) -> dict[str, Any] | None:
    if not isinstance(body, str) or RESULT_MARKER not in body:
        return None
    matches = list(BINDING_PATTERN.finditer(body))
    if len(matches) != 1:
        _fail("SUNSET_PREVIEW_REPLAY_EVIDENCE", "existing Preview receipt is malformed")
    payload = matches[0].group("payload")
    value = _loads(payload)
    if not isinstance(value, dict) or payload.encode("utf-8") + b"\n" != canonical_bytes(value):
        _fail("SUNSET_PREVIEW_REPLAY_EVIDENCE", "existing Preview binding is not canonical")
    return value


def admit_issue_comment(
    repo_root: Path,
    event_path: Path,
    comments_path: Path,
    request_output: Path,
    admission_output: Path,
) -> dict[str, Any]:
    root = repo_root.resolve()
    event = _read_json(event_path, MAX_EVENT_BYTES)
    if not isinstance(event, dict):
        _fail("SUNSET_PREVIEW_EVENT", "GitHub event is not an object")
    repository = event.get("repository", {})
    issue = event.get("issue", {})
    comment = event.get("comment", {})
    sender = event.get("sender", {})
    if (
        event.get("action") != "created"
        or not isinstance(repository, dict)
        or repository.get("full_name") != EXPECTED_REPOSITORY
        or repository.get("default_branch") != EXPECTED_BRANCH
        or not isinstance(repository.get("owner"), dict)
        or repository["owner"].get("login") != EXPECTED_OWNER
    ):
        _fail("SUNSET_PREVIEW_REPOSITORY_IDENTITY", "repository event identity is invalid")
    if (
        not isinstance(issue, dict)
        or issue.get("number") != EXPECTED_ISSUE
        or issue.get("pull_request") is not None
    ):
        _fail("SUNSET_PREVIEW_ISSUE_IDENTITY", "event does not target Mission Issue #257")
    if (
        not isinstance(comment, dict)
        or not isinstance(comment.get("id"), int)
        or comment["id"] < 1
        or not isinstance(comment.get("user"), dict)
        or comment["user"].get("login") != EXPECTED_OWNER
        or comment.get("author_association") != "OWNER"
        or not isinstance(sender, dict)
        or sender.get("login") != EXPECTED_OWNER
    ):
        _fail("SUNSET_PREVIEW_OWNER_IDENTITY", "Issue comment is not owner-authenticated")

    envelope = _extract_envelope(comment.get("body"))
    validator = SchemaValidator(root / "lifecycle" / "schemas")
    validator.validate_sunset_router_preview_intake(envelope)
    enforce_clean_values(envelope)
    enforce_pointer_contract(envelope)

    current_main = observed_head(root)
    router_request = envelope["router_request"]
    lifecycle_request = router_request["lifecycle_request"]
    if (
        envelope["expected_main_sha"] != current_main
        or lifecycle_request["expected_main_sha"] != current_main
    ):
        _fail("STALE_STATE", "intake base does not equal current canonical main")
    if (
        router_request["actor"] != "ATHENA"
        or router_request["requested_route"] != "ATHENA_SPEAR_THREAD_ENGINE"
        or router_request["operator_transfer_authorized"] is not False
    ):
        _fail("SUNSET_PREVIEW_ROUTE_IDENTITY", "Preview intake requires exact Athena Spear route")

    request_digest = _digest(canonical_bytes(router_request))
    replay_seed = {
        "repository": EXPECTED_REPOSITORY,
        "issue_number": EXPECTED_ISSUE,
        "comment_id": comment["id"],
        "replay_nonce": envelope["replay_nonce"],
        "request_digest": request_digest,
    }
    replay_id = _digest(canonical_bytes(replay_seed))

    comments = _read_json(comments_path, MAX_COMMENTS_BYTES)
    if not isinstance(comments, list):
        _fail("SUNSET_PREVIEW_REPLAY_EVIDENCE", "Issue comments input is not an array")
    for item in comments:
        if not isinstance(item, dict):
            _fail("SUNSET_PREVIEW_REPLAY_EVIDENCE", "Issue comments contain an invalid item")
        user = item.get("user", {})
        if not isinstance(user, dict) or user.get("login") != "github-actions[bot]":
            continue
        binding = _binding_from_comment(item.get("body"))
        if binding is not None and binding.get("replay_id") == replay_id:
            _fail("REPLAY", "this exact Preview intake already has a successful receipt")

    admission = {
        "authority": "PREVIEW_ONLY_ADMISSION",
        "repository": EXPECTED_REPOSITORY,
        "issue_number": EXPECTED_ISSUE,
        "comment_id": comment["id"],
        "owner": EXPECTED_OWNER,
        "expected_main_sha": current_main,
        "request_digest": request_digest,
        "replay_nonce": envelope["replay_nonce"],
        "replay_id": replay_id,
        "mutation_authorized": False,
        "next_safe_action": "Invoke only the canonical Sunset Router Preview in temporary storage.",
    }
    _write_canonical(root, request_output, router_request)
    _write_canonical(root, admission_output, admission)
    return admission


def render_preview_comment(
    repo_root: Path,
    router_dir: Path,
    admission_path: Path,
    output_path: Path,
) -> dict[str, Any]:
    root = repo_root.resolve()
    admission = _read_canonical(admission_path, MAX_EVENT_BYTES)
    verified = verify_router_preview(root, router_dir, require_current_head=True)
    plan = verified["plan"]
    router_receipt = verified["receipt"]
    lifecycle_preview = verified["preview"]["preview"]
    if (
        admission.get("authority") != "PREVIEW_ONLY_ADMISSION"
        or admission.get("repository") != EXPECTED_REPOSITORY
        or admission.get("issue_number") != EXPECTED_ISSUE
        or admission.get("expected_main_sha") != plan["expected_main_sha"]
        or admission.get("request_digest") != plan["request_digest"]
        or admission.get("mutation_authorized") is not False
    ):
        _fail("SUNSET_PREVIEW_RENDER_BINDING", "admission does not bind the exact Router Preview")

    router_receipt_digest = _digest(canonical_bytes(router_receipt))
    binding = {
        "repository": EXPECTED_REPOSITORY,
        "issue_number": EXPECTED_ISSUE,
        "trigger_comment_id": admission["comment_id"],
        "replay_id": admission["replay_id"],
        "expected_main_sha": plan["expected_main_sha"],
        "request_digest": plan["request_digest"],
        "plan_id": plan["plan_id"],
        "plan_digest": router_receipt["plan_digest"],
        "preview_id": plan["preview_id"],
        "preview_digest": plan["preview_digest"],
        "semantic_digest": lifecycle_preview["semantic_digest"],
        "router_receipt_id": router_receipt["receipt_id"],
        "router_receipt_digest": router_receipt_digest,
        "state": "PREVIEW_READY",
        "source_write_authorized": False,
        "permanence_authorized": False,
    }
    preview_json = canonical_bytes(lifecycle_preview).decode("utf-8").rstrip("\n")
    receipt_json = canonical_bytes(router_receipt).decode("utf-8").rstrip("\n")
    binding_json = canonical_bytes(binding).decode("utf-8").rstrip("\n")
    approval_command = (
        f"APPROVE SUNSET PREVIEW {plan['preview_id']} {plan['preview_digest']} "
        f"{lifecycle_preview['semantic_digest']} WITH GODDESS MODE AND SHARDBLADE"
    )
    body = (
        f"{RESULT_MARKER}\n"
        f"## Mission #257 — Exact Sunset Router Preview\n\n"
        f"**State:** `PREVIEW_READY`  \n"
        f"**Canonical base:** `{plan['expected_main_sha']}`  \n"
        f"**Selected route:** `{plan['selected_route']}`  \n"
        f"**Fallback routes:** `{', '.join(plan['fallback_routes'])}`  \n"
        f"**Preview ID:** `{plan['preview_id']}`  \n"
        f"**Preview digest:** `{plan['preview_digest']}`  \n"
        f"**Semantic digest:** `{lifecycle_preview['semantic_digest']}`  \n"
        f"**Router receipt ID:** `{router_receipt['receipt_id']}`  \n"
        f"**Router receipt digest:** `{router_receipt_digest}`\n\n"
        f"### Exact lifecycle Preview\n\n"
        f"```atlas-sunset-preview-v1\n{preview_json}\n```\n\n"
        f"### Exact Router receipt\n\n"
        f"```atlas-sunset-router-receipt-v1\n{receipt_json}\n```\n\n"
        f"### Ingress binding\n\n"
        f"```{BINDING_LANGUAGE}\n{binding_json}\n```\n\n"
        f"This is Preview-only evidence. It creates no branch or PR, writes no source, "
        f"grants no READY or MERGE authority, advances no Quest or runtime state, and "
        f"cannot claim `SUNSET COMPLETE`.\n\n"
        f"### Exact approval gate\n\n"
        f"```text\n{approval_command}\n```\n"
    )
    _write_text(root, output_path, body)
    return {
        "authority": "PREVIEW_ONLY",
        "preview_id": plan["preview_id"],
        "preview_digest": plan["preview_digest"],
        "semantic_digest": lifecycle_preview["semantic_digest"],
        "router_receipt_digest": router_receipt_digest,
        "replay_id": admission["replay_id"],
        "status": "PASS",
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m tools.sunset_router.issue_preview_ingress"
    )
    commands = parser.add_subparsers(dest="command", required=True)
    admit = commands.add_parser("admit")
    admit.add_argument("--repo-root", type=Path, required=True)
    admit.add_argument("--event", type=Path, required=True)
    admit.add_argument("--comments", type=Path, required=True)
    admit.add_argument("--request-output", type=Path, required=True)
    admit.add_argument("--admission-output", type=Path, required=True)
    render = commands.add_parser("render")
    render.add_argument("--repo-root", type=Path, required=True)
    render.add_argument("--router-dir", type=Path, required=True)
    render.add_argument("--admission", type=Path, required=True)
    render.add_argument("--output", type=Path, required=True)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        if args.command == "admit":
            result = admit_issue_comment(
                args.repo_root,
                args.event,
                args.comments,
                args.request_output,
                args.admission_output,
            )
        else:
            result = render_preview_comment(
                args.repo_root,
                args.router_dir,
                args.admission,
                args.output,
            )
        print(json.dumps(result, sort_keys=True, separators=(",", ":")))
        return 0
    except LifecycleError as exc:
        print(
            json.dumps(
                {
                    "authority": "READ_ONLY",
                    "state": "BLOCKED_RESUMABLE",
                    "status": "FAIL",
                    **exc.sanitized(),
                },
                sort_keys=True,
                separators=(",", ":"),
            )
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
