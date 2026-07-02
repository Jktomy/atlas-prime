---
title: Atlas Sword Contract v1
atlas_id: atlas-sword.contract.v1
format_version: "1.0"
status: PROPOSED
source_type: SPECIFICATION
authority_class: TOOL_CONTRACT
owner_project: Codex
owner_operation: Atlas Change Path Convergence
canonical_scope: Defines the mission-specific sealed local direct-execution path for applying an Athena-authored Weave without Thread Engine while preserving Build/Execute separation, exact PR review, recovery, and authority boundaries.
protected_level: CRITICAL
routes_from:
  - specs/spear/spear-execution-convergence-v1.md
  - migration/atlas-codex/atlas-prime-rebuild-program-roadmap-v1.md
routes_to:
  - specs/thread-engine/thread-engine-contract-v1.md
  - quest-board/quest-board-shadow-v1.json
private_boundary: Public-clean contracts only; local paths, tokens, raw receipts, authentication output, and protected evidence remain outside GitHub.
evidence_boundary: Every Sword package, receipt, Git object, PR, Noctua report, and merge record remains separate proof.
supersedes: []
cleanup_path: Retain as the mission-specific local fallback contract. No standing authority is implied.
last_verified: 2026-07-02
---

# Atlas Sword Contract v1

Sword consumes the same exact transaction meaning as Thread Engine but performs candidate construction through a sealed mission-specific local package.

A Build Sword may verify, construct candidates, create deterministic branches and commits, push without force, open draft PRs, and emit one consolidated receipt. It must stop before merge.

An Execute Sword exists only after Strikeforce verifies the Build receipt, Noctua returns `YES` on exact current heads, and Jayson authorizes the exact Execute Sword.

Sword grants no direct-main, force-push, automatic merge, standing local authority, hidden scope, migration, promotion, retirement, cleanup, or cutover authority.
