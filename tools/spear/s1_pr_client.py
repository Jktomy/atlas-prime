from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Protocol

from .models import StateError

NO_AUTHORITY_STATEMENT = "This draft pull request grants no merge, deletion, migration, source-promotion, or cutover authority."
NOCTUA_STATEMENT = "Manual Noctua review and explicit Jayson approval are required before merge."


@dataclass(frozen=True)
class DraftPullRequestSpec:
    title: str
    body: str
    base: str
    head: str
    head_sha: str


@dataclass(frozen=True)
class DraftPullRequestReadback:
    number: int
    url: str
    title: str
    body: str
    base: str
    head: str
    draft: bool
    head_sha: str


class S1PrClient(Protocol):
    def find_open_draft_pr_for_branch(self, branch: str) -> DraftPullRequestReadback | None: ...
    def establish_definite_absence(self, branch: str) -> bool: ...
    def create_draft_pr(self, spec: DraftPullRequestSpec) -> DraftPullRequestReadback: ...
    def read_pull_request(self, number: int) -> DraftPullRequestReadback: ...
    def post_request_uncertainty_readback(self, branch: str) -> DraftPullRequestReadback | None: ...


class GitHubRestClient:
    """Future stdlib-only REST client. Tests inject fakes; no test calls this client."""

    def __init__(self, *, token: str, api_root: str = "https://api.github.com") -> None:
        self._token = token
        self._api_root = api_root.rstrip("/")

    def _request_json(self, method: str, path: str, payload: dict | None = None) -> dict:
        body = None if payload is None else json.dumps(payload, sort_keys=True).encode("utf-8")
        request = urllib.request.Request(
            f"{self._api_root}{path}",
            data=body,
            method=method,
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": "Bearer " + self._token,
                "Content-Type": "application/json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.URLError as exc:
            raise StateError("PR_API_UNAVAILABLE") from exc


def build_pr_title(packet: dict) -> str:
    return f"Spear: {packet['title']}"


def _json_block(value: Any) -> list[str]:
    return ["```json", json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2), "```"]


def build_pr_body(
    *,
    packet: dict,
    branch: str,
    commit_sha: str,
    manifest_sha256: str,
    preview_sha256: str,
    transport_sha256: str,
    approval_reference: str,
    changed_paths: list[str],
    contract_identities: list[dict[str, Any]],
    file_identities: list[dict[str, Any]],
    validation_results: list[str],
    warning_codes: list[str],
    protected_boundary: str,
    actor: str,
    event: str,
    workflow_sha: str,
    run_id: str,
    run_attempt: str,
    repository: str,
) -> str:
    """Generate the complete deterministic A2-required draft-PR body."""

    lines = [
        "## Spear S1 draft PR",
        "",
        "### Approved transaction identity",
        "",
        f"- Repository: `{repository}`",
        f"- Packet ID: `{packet['packet_id']}`",
        f"- Packet transport SHA-256: `{transport_sha256}`",
        f"- Approved normalized-manifest SHA-256: `{manifest_sha256}`",
        f"- Approved Preview SHA-256: `{preview_sha256}`",
        f"- Approval basis: `{packet['approval_basis']}`",
        f"- Approval reference: `{approval_reference}`",
        f"- Exact base commit: `{packet['base_commit']}`",
        f"- Branch: `{branch}`",
        f"- Commit SHA: `{commit_sha}`",
        "",
        "### Workflow run identity",
        "",
        f"- Authenticated actor: `{actor}`",
        f"- Event: `{event}`",
        f"- Workflow commit: `{workflow_sha}`",
        f"- Run ID: `{run_id}`",
        f"- Run attempt: `{run_attempt}`",
        "",
        "### Controlling contract identities",
        "",
    ]
    lines.extend(_json_block(sorted(contract_identities, key=lambda item: item["path"])))
    lines.extend(["", "### Exact changed filenames", ""])
    lines.extend(f"- `{path}`" for path in sorted(changed_paths))
    lines.extend(["", "### Old and new file identities", ""])
    lines.extend(_json_block(sorted(file_identities, key=lambda item: item["path"])))
    lines.extend(["", "### Validation summary", ""])
    lines.extend(f"- {result}" for result in sorted(validation_results))
    lines.extend(["", "### Warnings", ""])
    if warning_codes:
        lines.extend(f"- `{code}`" for code in sorted(warning_codes))
    else:
        lines.append("- None.")
    lines.extend(
        [
            "",
            f"- Protected-boundary outcome: `{protected_boundary}`",
            "- Rollback posture: S1 does not execute rollback; Phoenix Reborn review remains separate.",
            "- Requested Noctua audit: verify packet-to-PR fidelity, contracts, target state, branch, commit, PR metadata, checks, and receipt.",
            "",
            NO_AUTHORITY_STATEMENT,
            NOCTUA_STATEMENT,
        ]
    )
    return "\n".join(lines) + "\n"


def validate_pr_readback(readback: DraftPullRequestReadback, expected: DraftPullRequestSpec) -> None:
    if readback.title != expected.title:
        raise StateError("PR_METADATA_MISMATCH")
    if readback.body != expected.body:
        raise StateError("PR_METADATA_MISMATCH")
    if readback.base != expected.base or readback.head != expected.head:
        raise StateError("PR_METADATA_MISMATCH")
    if readback.draft is not True:
        raise StateError("PR_METADATA_MISMATCH")
    if readback.head_sha != expected.head_sha:
        raise StateError("PR_METADATA_MISMATCH")


@dataclass
class FakeS1PrClient:
    existing: DraftPullRequestReadback | None = None
    definite_absence: bool = True
    created: DraftPullRequestReadback | None = None
    mutate_created_body: bool = False
    uncertain_on_create: bool = False
    calls: list[str] | None = None

    def __post_init__(self) -> None:
        if self.calls is None:
            self.calls = []

    def find_open_draft_pr_for_branch(self, branch: str) -> DraftPullRequestReadback | None:
        self.calls.append(f"find_open_draft_pr_for_branch:{branch}")
        return self.existing

    def establish_definite_absence(self, branch: str) -> bool:
        self.calls.append(f"establish_definite_absence:{branch}")
        return self.definite_absence

    def create_draft_pr(self, spec: DraftPullRequestSpec) -> DraftPullRequestReadback:
        self.calls.append("create_draft_pr")
        if self.uncertain_on_create:
            raise StateError("PR_CREATION_UNCERTAIN")
        body = spec.body + "\nmutated\n" if self.mutate_created_body else spec.body
        self.created = DraftPullRequestReadback(
            1,
            "https://github.com/Jktomy/atlas-prime/pull/1",
            spec.title,
            body,
            spec.base,
            spec.head,
            True,
            spec.head_sha,
        )
        return self.created

    def read_pull_request(self, number: int) -> DraftPullRequestReadback:
        self.calls.append(f"read_pull_request:{number}")
        if self.created is None:
            raise StateError("PR_METADATA_MISMATCH")
        return self.created

    def post_request_uncertainty_readback(self, branch: str) -> DraftPullRequestReadback | None:
        self.calls.append(f"post_request_uncertainty_readback:{branch}")
        return self.existing
