---
title: Atlas Change-Path Execution Convergence v2
atlas_id: atlas.change-path.execution-convergence.v2
format_version: "2.0"
status: PROPOSED
source_type: SPECIFICATION
authority_class: TOOL_CONTRACT
owner_project: Codex
owner_operation: Atlas Change Path Convergence
canonical_scope: Defines the common Athena-authored Weave, Thread Engine normal execution, Sword direct local execution, Spear and Arrow/Bow intake roles, equivalent receipts, Gates 1-8 posture, replay, recovery, and authority boundaries without activating writer or merge authority.
protected_level: CRITICAL
routes_from:
  - athenas-spear.md
  - specs/spear/spear-capability-lifecycle-v1.md
  - specs/thread-engine/thread-engine-contract-v1.md
  - specs/sword/atlas-sword-contract-v1.md
routes_to:
  - schemas/spear/spear-packet-v1.schema.json
  - policies/operations/spear/spear-policy-v1.yaml
  - migration/atlas-codex/atlas-prime-rebuild-program-roadmap-v1.md
  - quest-board/quest-board-shadow-v1.json
private_boundary: Public-clean contracts, repository identities, route names, limits, tests, and recovery rules only. No secrets, credentials, PHI, finance/account evidence, private runtime values, network maps, device registers, or protected exports.
evidence_boundary: Implementation, workflow runs, Arrow and Sword packages, receipts, PRs, Noctua reports, activation records, and recovery proof remain separate evidence.
supersedes:
  - spear.execution-convergence.v1
cleanup_path: Retain through Gates 6-8 and later absorb stable semantics into active maintenance contracts after cutover.
last_verified: 2026-07-02
---

# Atlas Change-Path Execution Convergence v2

## Status

This specification grants no writer, merge, migration, promotion, retirement, deletion, cleanup, or cutover authority.

Codex remains canonical. Prime remains SHADOW.

## Common transaction

Athena authors one runner-neutral multi-file **Weave** binding:

- repository and exact base;
- ordered file operations;
- expected absence or current Git blob;
- exact candidate bytes or deterministic sealed transformation;
- allowed paths and route profile;
- tests and validation;
- protected boundaries;
- branch, commit, and PR expectations;
- replay and recovery rules;
- Noctua criteria;
- forbidden actions.

Caller-selected executable code and hidden authority are prohibited.

## Execution paths

### Thread Engine

Thread Engine is the intended normal deterministic multi-file workflow.

```text
Spear direct delivery
or
Arrow -> Bow delegated delivery
-> Thread Engine
-> exact branch, single-parent commit, draft PR, receipt
-> stop before merge
```

### Sword

Sword is the mission-specific local direct-execution path.

```text
Athena-made sealed Sword ZIP
-> exact local command
-> direct Git/GitHub candidate construction
-> exact branch, single-parent commit, draft PR, receipt
-> stop before merge
```

Sword is used for fallback, recovery, or Thread Engine self-change. It creates no standing local authority.

## Operators

Jayson remains ultimate authority. An authorized agent or future local LLM may operate Bow or Sword only under the exact same artifact, authority capsule, receipt, and stop point. Artemis is optional and inactive until separately proven and activated.

## Build and Execute

Every durable mission separates:

```text
Build artifact
-> Strikeforce
-> Noctua exact-head review
-> separately authorized Execute artifact
```

Build success never grants Execute authority.

## Common receipts

Both paths emit equivalent sanitized receipts containing:

- mission, artifact, and package identity;
- runner and operator;
- repository bases;
- manifest and candidate identities;
- changed files;
- branches, commits, PRs, and exact heads;
- result and last completed checkpoint;
- partial-state and recovery context;
- authority used;
- forbidden-action confirmation.

## Replay and recovery

Active paths must detect exact replay, stale base, branch-created, commit-pushed, PR-missing, PR-verified, partial repository success, merge/readback incomplete, and complete states.

Recovery resumes only missing permitted work. It never resets successful work, force-pushes, deletes branches, closes PRs, creates duplicates, or broadens scope.

## Gates

```text
Gates 1-5 — COMPLETE
  Transaction, receipt, GitHub-native, and local direct-execution foundations.

Gate 6 — CHANGE PATH CONVERGENCE
  Thread Engine, Sword, Spear, Arrow, Bow, Noctua, Workboard, roadmap, and Quest alignment.

Gate 7 — DUAL-PATH PROOF
  Multi-file ADD/REPLACE through Thread Engine;
  mixed ADD/REPLACE/DELETE and linked-repository recovery through Sword;
  exact-head Noctua and replay/partial-state proof.

Gate 8 — C07 PROTECTED RECONCILIATION
  Read-only semantic reconciliation, exact protected Weave Preview, approved proven path, Noctua, and Jayson Execute gate.
```

## Current posture

- Codex: CANONICAL
- Prime: SHADOW
- Gates 1-5: COMPLETE
- Gate 6: closes through the reviewed doctrine and Quest Reforge
- Gate 7: next
- Persistent Thread Engine writer: DISABLED
- Sword standing authority: NONE; every Sword is mission-specific
- Artemis Local Operator: INACTIVE / OPTIONAL
- C07: DEFERRED TO GATE 8
