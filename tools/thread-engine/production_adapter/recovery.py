from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RecoveryDecision:
    classification: str
    safe_to_continue: bool
    required_checkpoint: str
    reason: str


def classify_recovery(checkpoint: str, branch_exists: bool = False, pr_exists: bool = False, head_matches: bool = False) -> RecoveryDecision:
    if checkpoint in {"PACKAGE_AUDIT", "MISSION_PARSE", "MISSION_SCHEMA", "MISSION_INTEGRITY", "REMOTE_LOCK", "DUPLICATE_CHECK"}:
        return RecoveryDecision("PRE_MUTATION_RETRY_ALLOWED", True, checkpoint, "no repository mutation has been attempted")
    if checkpoint in {"FRESH_CLONE", "CLEAN_START", "SOURCE_BLOB_VERIFY", "CANDIDATE_STAGE", "PATH_POLICY_VERIFY", "TREE_VERIFY", "INSTALL", "DIFF_CHECK", "STAGE_VERIFY"}:
        return RecoveryDecision("LOCAL_ONLY_REBUILD_REQUIRED", True, checkpoint, "discard local candidate only after preserving receipt")
    if checkpoint in {"COMMIT", "COMMIT_VERIFY"}:
        return RecoveryDecision("LOCAL_COMMIT_PRESERVE_BEFORE_RETRY", False, checkpoint, "preserve local commit evidence before any continuation")
    if checkpoint == "PUSH":
        if branch_exists and head_matches:
            return RecoveryDecision("REMOTE_BRANCH_CONTINUATION_REQUIRES_READBACK", True, "DRAFT_PR", "branch exists at expected head")
        return RecoveryDecision("REMOTE_BRANCH_REPAIR_REQUIRED", False, checkpoint, "remote branch state must be classified before continuation")
    if checkpoint in {"DRAFT_PR", "READBACK"}:
        if branch_exists and pr_exists and head_matches:
            return RecoveryDecision("PR_READBACK_CONTINUATION_ALLOWED", True, "READBACK", "draft PR exists at expected head")
        return RecoveryDecision("PR_PARTIAL_STATE_REPAIR_REQUIRED", False, checkpoint, "PR state does not match the recorded mission")
    return RecoveryDecision("BLIND_REPLAY_REJECTED", False, checkpoint, "unknown or completed checkpoint cannot be replayed blindly")
