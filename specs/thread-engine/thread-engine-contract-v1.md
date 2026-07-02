---
title: Thread Engine Contract v1
atlas_id: thread-engine.contract.v1
format_version: "1.0"
status: PROPOSED
source_type: SPECIFICATION
authority_class: TOOL_CONTRACT
owner_project: Codex
owner_operation: Atlas Change Path Convergence
canonical_scope: Defines the normal deterministic multi-file Prime construction workflow, shared Weave contract, Spear and Arrow/Bow intake equivalence, exact candidate-tree behavior, receipts, recovery, and hard authority boundaries without activating writer authority.
protected_level: CRITICAL
routes_from:
  - specs/spear/spear-execution-convergence-v1.md
  - migration/atlas-codex/atlas-prime-rebuild-program-roadmap-v1.md
routes_to:
  - specs/sword/atlas-sword-contract-v1.md
  - quest-board/quest-board-shadow-v1.json
private_boundary: Public-clean contracts only; no secrets, credentials, PHI, raw finance/account evidence, private runtime values, network maps, device registers, or protected exports.
evidence_boundary: Implementation, workflows, packages, receipts, PRs, tests, activation records, and recovery proof remain separate evidence.
supersedes: []
cleanup_path: Retain through implementation and proof. Activation requires a separate exact transaction.
last_verified: 2026-07-02
---

# Thread Engine Contract v1

Thread Engine receives an exact multi-file Weave through Spear or Arrow/Bow intake.

It must:

- validate every operation before candidate publication;
- bind exact repository, base commit, expected path state, and candidate identity;
- reject duplicate, case-colliding, unsafe, stale, or undeclared paths;
- construct one exact candidate tree;
- create one deterministic branch and one single-parent commit;
- create one draft PR and one receipt;
- detect replay and partial state;
- stop before merge.

Primitive operations are `ADD`, `REPLACE`, and separately qualified `DELETE`.

This contract grants no writer activation, direct-main, force-push, automatic merge, migration, promotion, retirement, cleanup, or cutover authority.
