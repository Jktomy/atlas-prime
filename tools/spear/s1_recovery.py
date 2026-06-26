from __future__ import annotations

from dataclasses import dataclass

from .models import StateError
from .s1_git_adapter import CommitSpec
from .s1_pr_client import DraftPullRequestSpec


@dataclass(frozen=True)
class TransactionIdentity:
    repository: str
    packet_id: str
    packet_sha256: str
    manifest_sha256: str
    preview_sha256: str
    base_commit: str
    branch: str
    commit_sha: str | None
    tree_sha: str | None
    commit_spec: CommitSpec | None = None
    pr_spec: DraftPullRequestSpec | None = None


@dataclass(frozen=True)
class ExistingTransaction:
    identity: TransactionIdentity
    observed_branch: str
    has_branch: bool
    has_open_draft_pr: bool
    pr_head_sha: str | None


def assert_same_packet_identity(existing: TransactionIdentity, current: TransactionIdentity) -> None:
    if existing.repository != current.repository or existing.packet_id != current.packet_id:
        raise StateError("PACKET_IDENTITY_MISMATCH")
    for field in (
        "packet_sha256",
        "manifest_sha256",
        "preview_sha256",
        "base_commit",
        "branch",
        "commit_sha",
        "tree_sha",
        "commit_spec",
        "pr_spec",
    ):
        if getattr(existing, field) != getattr(current, field):
            raise StateError("PACKET_ID_REUSE_COLLISION")


def classify_existing_transaction(existing: ExistingTransaction, current: TransactionIdentity) -> str:
    if existing.observed_branch != current.branch:
        raise StateError("BRANCH_COLLISION")
    assert_same_packet_identity(existing.identity, current)
    if not existing.has_branch:
        raise StateError("BRANCH_COLLISION")
    if existing.has_open_draft_pr and existing.pr_head_sha == current.commit_sha:
        return "EXISTING_TRANSACTION_RETURNED"
    if not existing.has_open_draft_pr and existing.identity.commit_sha == current.commit_sha:
        return "DRAFT_PR_CREATED_RECOVERED"
    raise StateError("BRANCH_COLLISION")
