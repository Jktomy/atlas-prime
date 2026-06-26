from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from .git_adapter import blob_sha_at_commit
from .models import StateError

BOT_NAME = "github-actions[bot]"
BOT_EMAIL = "41898282+github-actions[bot]@users.noreply.github.com"


@dataclass(frozen=True)
class GitIdentity:
    name: str
    email: str
    date: str


@dataclass(frozen=True)
class CommitSpec:
    parent: str
    tree_sha: str
    message: str
    author: GitIdentity
    committer: GitIdentity
    changed_paths: tuple[str, ...]


@dataclass(frozen=True)
class CommitReadback:
    sha: str
    parents: tuple[str, ...]
    tree_sha: str
    message: str
    author: GitIdentity
    committer: GitIdentity
    changed_paths: tuple[str, ...]


class S1GitAdapter(Protocol):
    def read_remote_main(self) -> str: ...
    def read_target_blob(self, path: str) -> str | None: ...
    def read_branch_ref(self, branch: str) -> str | None: ...
    def create_blob(self, path: str, content: str) -> str: ...
    def create_complete_tree(self, base_commit: str, blobs: dict[str, str]) -> str: ...
    def create_exact_single_parent_commit(self, spec: CommitSpec) -> str: ...
    def create_branch_ref_without_force(self, branch: str, commit_sha: str) -> None: ...
    def read_commit_and_changed_paths(self, commit_sha: str) -> CommitReadback: ...


@dataclass(frozen=True)
class LocalPlanningGitAdapter:
    """Read-only target-state adapter for the exact pinned local Prime commit."""

    repository: str
    base_commit: str

    def read_target_blob(self, path: str) -> str | None:
        return blob_sha_at_commit(self.repository, self.base_commit, path)


def exact_commit_message(
    *,
    title: str,
    packet_id: str,
    packet_sha256: str,
    manifest_sha256: str,
    preview_sha256: str,
    base_commit: str,
) -> str:
    """Build the complete deterministic commit identity used for replay safety."""

    return "\n".join(
        [
            f"Spear: {title}",
            "",
            f"Packet-ID: {packet_id}",
            f"Packet-Transport-SHA256: {packet_sha256}",
            f"Manifest-SHA256: {manifest_sha256}",
            f"Preview-SHA256: {preview_sha256}",
            f"Base-Commit: {base_commit}",
        ]
    )


def commit_spec(
    *,
    title: str,
    packet_id: str,
    packet_sha256: str,
    manifest_sha256: str,
    preview_sha256: str,
    parent: str,
    tree_sha: str,
    changed_paths: list[str],
    plan_timestamp: str,
) -> CommitSpec:
    identity = GitIdentity(BOT_NAME, BOT_EMAIL, plan_timestamp)
    return CommitSpec(
        parent=parent,
        tree_sha=tree_sha,
        message=exact_commit_message(
            title=title,
            packet_id=packet_id,
            packet_sha256=packet_sha256,
            manifest_sha256=manifest_sha256,
            preview_sha256=preview_sha256,
            base_commit=parent,
        ),
        author=identity,
        committer=identity,
        changed_paths=tuple(sorted(changed_paths)),
    )


def validate_commit_readback(readback: CommitReadback, expected: CommitSpec) -> None:
    if len(readback.parents) != 1 or readback.parents[0] != expected.parent:
        raise StateError("COMMIT_PARENT_MISMATCH")
    if readback.message != expected.message:
        raise StateError("COMMIT_MESSAGE_MISMATCH")
    if readback.tree_sha != expected.tree_sha or tuple(sorted(readback.changed_paths)) != expected.changed_paths:
        raise StateError("COMMIT_TREE_MISMATCH")
    if readback.author != expected.author or readback.committer != expected.committer:
        raise StateError("COMMIT_IDENTITY_MISMATCH")


@dataclass
class FakeS1GitAdapter:
    base_commit: str
    remote_main: str
    target_blobs: dict[str, str | None] = field(default_factory=dict)
    branches: dict[str, str] = field(default_factory=dict)
    commits: dict[str, CommitReadback] = field(default_factory=dict)
    calls: list[str] = field(default_factory=list)
    next_blob_counter: int = 1
    next_commit_sha: str = "c000000000000000000000000000000000000001"
    created_tree_sha: str = "7000000000000000000000000000000000000001"

    def read_remote_main(self) -> str:
        self.calls.append("read_remote_main")
        return self.remote_main

    def read_target_blob(self, path: str) -> str | None:
        self.calls.append(f"read_target_blob:{path}")
        return self.target_blobs.get(path)

    def read_branch_ref(self, branch: str) -> str | None:
        self.calls.append(f"read_branch_ref:{branch}")
        return self.branches.get(branch)

    def create_blob(self, path: str, content: str) -> str:
        self.calls.append(f"create_blob:{path}")
        blob = f"b{self.next_blob_counter:039d}"[-40:]
        self.next_blob_counter += 1
        return blob

    def create_complete_tree(self, base_commit: str, blobs: dict[str, str]) -> str:
        self.calls.append("create_complete_tree")
        if base_commit != self.base_commit:
            raise StateError("BASE_COMMIT_MISMATCH")
        return self.created_tree_sha

    def create_exact_single_parent_commit(self, spec: CommitSpec) -> str:
        self.calls.append("create_exact_single_parent_commit")
        readback = CommitReadback(
            sha=self.next_commit_sha,
            parents=(spec.parent,),
            tree_sha=spec.tree_sha,
            message=spec.message,
            author=spec.author,
            committer=spec.committer,
            changed_paths=spec.changed_paths,
        )
        self.commits[self.next_commit_sha] = readback
        return self.next_commit_sha

    def create_branch_ref_without_force(self, branch: str, commit_sha: str) -> None:
        self.calls.append(f"create_branch_ref_without_force:{branch}")
        if branch in self.branches:
            raise StateError("BRANCH_COLLISION")
        self.branches[branch] = commit_sha

    def read_commit_and_changed_paths(self, commit_sha: str) -> CommitReadback:
        self.calls.append(f"read_commit_and_changed_paths:{commit_sha}")
        return self.commits[commit_sha]
