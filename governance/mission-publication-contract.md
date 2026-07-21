---
title: "Mission Publication Contract"
atlas_id: "prime.governance.mission-publication"
status: "CANDIDATE"
source_type: "PROTOCOL"
authority_class: "CANONICAL_AUTHORED_SOURCE"
owner_project: "Project Codex"
owner_operation: "Operation Phoenix"
protected_level: "CRITICAL"
---

# Mission publication contract

Mission publication converts one validated public-clean Mission snapshot into one immutable publication plan. The deterministic compiler is read-only: it never calls GitHub or Gitea, creates a branch or pull request, changes READY state, merges, archives, deploys, or grants authority.

An authenticated adapter may execute a plan only after fresh canonical-main and Issue/PR readback. It must bind repository, Issue, Mission ID, attempt ID, exact base, branch, sorted changed paths, path digest, candidate tree, expected head, and pull request. Duplicate or conflicting bindings fail closed.

## Required invariants

- one Mission attempt produces at most one branch, one commit, and one draft pull request;
- branch names are deterministic and Mission-scoped;
- changed paths are normalized, sorted, case-fold unique, and inside the sealed inventory;
- public-clean scanning occurs before a plan or receipt is emitted;
- interruption causes read-only reconciliation, never blind retry;
- READY, MERGE, canonical readback, Sunset completion, and archival remain separate gates;
- no adapter may write directly to `main`, force-push, rewrite history, change settings, or infer authority from assignment.

## Recovery

Before merge, close the exact draft PR and preserve the Mission evidence. After merge, use one reviewed revert or repair-forward PR. A connector or worker outage preserves `BLOCKED_RESUMABLE` and one exact next safe action.
