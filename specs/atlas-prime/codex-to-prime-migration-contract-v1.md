---
title: Atlas Codex to Atlas Prime Migration and Reconciliation Contract v1
atlas_id: atlas-prime.migration.codex-to-prime.v1
format_version: "1.0"
status: PROPOSED
source_type: SPECIFICATION
authority_class: TOOL_CONTRACT
owner_project: Codex
owner_operation: Source Governance
canonical_scope: Defines the source order, zero-silent-loss reconciliation method, migration routes, packet lifecycle, full-file replacement controls, proof requirements, closure rules, and cutover dependencies for rebuilding Atlas Codex into Atlas Prime.
protected_level: CRITICAL
routes_from:
  - README.md
  - athenas-spear.md
routes_to:
  - schemas/migration/atlas-codex-inventory-v1.schema.json
  - codex/codex-source-update-standard.md
  - migration/atlas-codex/README.md
  - templates/codex-to-prime-reconciliation-record.md
private_boundary: This contract may contain clean migration doctrine, classifications, schemas, and examples only. It must not contain secrets, credentials, PHI, raw finance or account evidence, private runtime values, IP addresses, network maps, device registers, raw protected exports, or other prohibited evidence.
evidence_boundary: Atlas Codex, current Atlas Prime source, approved session harvests, original evidence systems, Git history, Spear receipts, pull requests, Noctua reports, and recovery proofs remain distinct evidence sources. This contract governs how their clean meaning is reconciled but does not replace them.
supersedes: []
cleanup_path: Version this contract through a later reviewed specification when migration semantics change. Do not silently reinterpret v1, and do not delete predecessor source merely because a successor contract exists.
last_verified: 2026-06-25
---

# Atlas Codex to Atlas Prime Migration and Reconciliation Contract v1

## 1. Status and purpose

This specification defines the control plane for rebuilding Atlas Prime from current Atlas Codex source and approved Prime architecture.

It does not migrate content by itself.

It does not activate Spear writes.

It does not authorize S1, source promotion, retirement, deletion, cutover, automation, or direct modification of Atlas Codex.

During construction:

- `Jktomy/atlas-codex` remains the current canonical operational source of truth.
- `Jktomy/atlas-prime` remains the proposed next-generation target in `SHADOW`.
- Current merged Prime doctrine controls intended Prime architecture.
- Current Codex source supplies canonical operational meaning and predecessor evidence.
- Jayson decides unresolved meaning, permanent migration dispositions, merge, promotion, retirement, and cutover.

## 2. Governing sources

For every reconciliation record and migration batch, use this order:

1. current explicit Jayson instruction;
2. current merged Atlas Prime doctrine, lifecycle, repository-format, safety, and Spear contracts;
3. current Atlas Codex source at the exact inventoried source commit;
4. relevant approved Prime decisions and restart-safe session harvests;
5. approved original evidence systems when Codex contains only a summary, pointer, or stale representation;
6. Athena inference, clearly labeled and never silently promoted.

This order separates two questions:

- **What governs Atlas today?** Atlas Codex, until cutover.
- **What architecture are we building?** Current approved Atlas Prime source.

When current Codex terminology conflicts with locked Prime architecture, Athena must not copy either side blindly. The conflict receives an explicit reconciliation decision and migration disposition.

## 3. Zero-silent-loss rule

Every tracked path in the inventoried Atlas Codex commit must receive exactly one entry conforming to:

`schemas/migration/atlas-codex-inventory-v1.schema.json`

A missing entry is a migration failure.

An unread file is not an omission.

A prohibited private file is not copied merely to make the inventory look complete.

Every entry must preserve:

- source repository and source commit;
- source path;
- Git blob identity and SHA-256;
- source class and privacy class;
- chosen disposition;
- content-transfer classification;
- target paths;
- preserved elements;
- removed or remodeled elements;
- reason and dependencies;
- replacement routing;
- private pointer or omission reason where applicable;
- approval basis;
- packet, PR, merge, Noctua, and final-state lineage.

## 4. Reconciliation classifications

Athena first classifies meaning in human terms, then maps it to one schema disposition.

| Athena classification | Required inventory disposition |
|---|---|
| Preserve substantially unchanged at a new target | `MIGRATE` |
| Combine with another predecessor source | `MERGE` |
| Preserve meaning but redesign structure, terminology, or ownership | `REMODEL` |
| Recreate from authoritative structured inputs | `GENERATED_REBUILD` |
| Keep only as non-governing history | `HISTORICAL_REFERENCE` |
| Replace raw protected evidence with a clean external pointer | `PRIVATE_POINTER` |
| Replace governing predecessor meaning with approved Prime doctrine | `SUPERSEDE` |
| End active use after dependencies and routing are closed | `RETIRE` |
| Exclude for an explicit reviewed reason | `OMIT_WITH_REASON` |

The following are not final dispositions:

- “skip”;
- “probably obsolete”;
- “copy later”;
- “not important”;
- “already somewhere in Prime”;
- “handled by memory”;
- “covered by the chat.”

Unresolved items remain unresolved and block migration closure.

## 5. Required read-only reconciliation record

Before Athena prepares any migration packet or source PR, Athena must complete one reconciliation record using:

`templates/codex-to-prime-reconciliation-record.md`

The record must identify:

- exact Codex source commit and complete source reads;
- exact Prime base commit and complete target reads;
- relevant routes, policies, schemas, lifecycle meanings, Workboard rows, session harvests, and original evidence;
- source meaning to preserve;
- defects, duplication, contradictions, stale terminology, or unsafe structure to remove or remodel;
- proposed target files;
- migration disposition and content-transfer type;
- selected execution route;
- complete replacement or bounded-change plan;
- unresolved Decision Boxes;
- tests, recovery, Noctua, and closure requirements.

A reconciliation record is planning evidence. It is not canonical source, packet approval, or execution authority.

## 6. Migration route selection

No single packet route may pretend to cover every Atlas surface.

### 6.1 Ordinary project migration route

Use the ordinary Prime Spear packet route only for paths permitted by the active packet overlay and destination policy.

Current S0 ordinary packets are limited to approved Markdown operations under `projects/`.

Current S0 compiles and validates plans only. It cannot execute them.

Future execution requires a separately approved writer phase.

### 6.2 Protected source PR route

Use a separately reviewed source PR for:

- root bootstrap and governance files;
- `codex/governance/`;
- lifecycle and source-order doctrine;
- schemas and policies;
- Spear, Noctua, or Phoenix contracts;
- tool implementation;
- tests and fixtures;
- workflows;
- repository hygiene controls;
- any surface denied to ordinary packets.

Protected files require complete readback, expected-state binding, visible full diff, Noctua review, manual merge, and merged-main readback.

### 6.3 Migration evidence PR route

Use a migration PR for:

- source inventory;
- disposition ledger;
- migration map;
- migration audits;
- clean predecessor-to-successor provenance;
- clean private pointers.

Migration evidence does not become governing doctrine merely because it is complete.

### 6.4 Structured-register migration route

Active Workboard, future Quest Registry, Quest events, Golden Wing, and other structured registers require versioned register-transition contracts.

The Active Workboard must be mapped record by record. It must not disappear through a dashboard rewrite or broad full-file replacement.

### 6.5 Generated rebuild route

Generated projections must be recreated from declared authoritative inputs under a generator contract.

Do not copy stale generated output as authored source.

Ordinary generated refresh remains separate from source PRs except for an explicitly contracted atomic exception.

### 6.6 Private pointer route

When predecessor content contains prohibited evidence:

- inventory the source path and hash;
- classify the privacy boundary honestly;
- preserve only a clean summary or pointer in GitHub;
- keep raw evidence in the original approved system;
- never place secrets or protected raw records into a Spear packet, review package, migration ledger, or PR.

## 7. Full-file replacement default

For the Atlas Prime rebuild, full-file replacement is the preferred migration mechanism when it produces the cleanest auditable result.

It is not automatic semantic authority.

A full replacement requires:

- complete current source read;
- complete current Prime target read when the target exists;
- exact source commit and source blob;
- exact target base commit and expected target blob;
- complete proposed replacement bytes;
- source and target SHA-256 values;
- required-heading inventory;
- preserved-elements declaration;
- removed-or-remodeled-elements declaration and rationale;
- metadata and route validation;
- protected-boundary review;
- deletion-percentage warning;
- complete old-to-new diff;
- temporary-tree validation;
- explicit Preview -> Execute approval;
- Noctua audit;
- manual Jayson merge;
- merged-main readback.

Fail closed when:

- any complete protected file cannot be read;
- tool output is truncated;
- source or target state is stale;
- unrelated guardrails cannot be compared;
- valid meaning may disappear silently;
- private evidence would enter GitHub;
- authority is unresolved;
- the full diff cannot be reviewed reliably.

For a small safety-sensitive correction, a surgical source PR may be safer. Current S0 does not implement a surgical packet operation; Athena may still author a complete replacement that preserves all untouched material.

## 8. Migration batch boundaries

Each batch must be small enough for a complete semantic and mechanical audit.

A batch must have:

- one target repository;
- one exact Prime base commit;
- one exact inventoried Codex source commit;
- one controlling ownership zone or tightly coupled atomic set;
- one selected write lane;
- one explicit approval basis;
- no hidden generated refresh;
- no undeclared deletion, retirement, or supersession;
- no cross-domain protected evidence.

Current S0 packet limits remain authoritative for S0 plans.

Do not mix:

- authored source and ordinary generated output;
- unrelated Projects;
- private evidence and public clean source;
- protected engine changes and ordinary migration content;
- migration evidence changes and unrelated source changes;
- source promotion and cutover.

## 9. Packet lifecycle

The migration lifecycle is:

```text
Exact Codex inventory
-> Athena reconciliation record
-> disposition and route decision
-> complete proposed Prime source
-> Spear packet when the selected route supports it
-> S0 compile and deterministic review evidence
-> exact Preview
-> explicit Jayson Execute approval
-> future authorized writer or protected manual source-PR route
-> narrow branch
-> exact source or migration PR
-> Noctua audit
-> Jayson manual merge
-> merged-main readback
-> inventory and disposition-ledger closure
-> Phoenix Reborn obligation when the batch affects a recovery claim
```

### 9.1 Packet-ready does not mean execution-ready

A packet may be structurally valid, policy valid, reproducible, and Noctua-auditable and still lack writer authority.

### 9.2 Merge does not mean migration closure

A merged source file is not enough.

Closure requires:

- intended target state read back from `main`;
- routing verified;
- migration entry updated with PR and merge lineage;
- Noctua outcome recorded;
- preserved and remodeled elements confirmed;
- no unresolved loss or conflict;
- final state recorded.

## 10. Conflict and Decision Box rules

Return `NEEDS_JAYSON` when:

- Codex and Prime encode different durable meanings;
- two target locations are both reasonable;
- retention, retirement, or supersession has downstream consequences;
- the correct privacy classification is uncertain;
- a source combines multiple Projects or owners;
- a full replacement would remove potentially valid material;
- an original evidence system conflicts with Codex;
- the migration would alter source order, actor authority, lifecycle meaning, or cutover posture.

Athena must state competing interpretations, controlling sources, recommendation, safe default, downstream consequences, and the next evidence needed.

No unresolved Decision Box may be hidden inside a packet.

## 11. Special predecessor obligations

### 11.1 Active Workboard

Map every Workboard row to a Quest record and event history, an approved historical reference, an approved omission reason, or another explicit target.

No row disappears silently.

### 11.2 Emberline

Emberline may be superseded or retired only after its safeguards are demonstrably absorbed into packet and plan binding, transaction atomicity, Noctua verification, Quest continuity, source/route/readback/cleanup discipline, and honest blocked and manual-item reporting.

### 11.3 Current Codex Spear

The current operational Codex Spear remains active during Prime construction.

Prime Spear does not silently replace it.

Its eventual disposition requires a separate comparison, continuity plan, rollback posture, and explicit approval.

### 11.4 Startup and source-order surfaces

`bootstrap.md`, `atlas-start-here.md`, `atlas-prime.md`, command surfaces, index, and project instructions are cutover-critical.

They remain protected source-PR work and must be migrated late enough to describe the true repository state, not the hoped-for state.

## 12. Noctua requirements

For every batch, Noctua verifies source order, exact commits, inventory coverage, disposition validity, complete reads, preserved and remodeled meaning, ownership and routing, metadata and policies, protected boundaries, packet/plan/PR fidelity, exact changed filenames, complete diff, tests and reproducibility, source/generated separation, PR lineage, manual merge, merged-main readback, and migration-ledger closure.

Valid outcomes remain `YES`, `NO`, `NEEDS_JAYSON`, `BLOCKED`, and `CAPTURE_ONLY`.

A Noctua `YES` does not authorize execution or merge by itself.

## 13. Failure behavior

Stop and preserve source when:

- Codex or Prime head changed;
- the source inventory is incomplete;
- a target has no owner or route;
- the selected route does not permit the target;
- a packet attempts to broaden policy;
- protected evidence is detected;
- complete-file readback is unavailable;
- the proposed diff is incomplete;
- one member of an atomic set fails;
- a connector blocks and no already-approved supported continuation exists;
- migration meaning is unresolved;
- the proposal includes silent omission, deletion, retirement, supersession, promotion, or cutover.

Do not repair a stale packet by changing only its SHA.

Reread, reconcile, regenerate, and present a new Preview.

## 14. S1 dependency boundary

This contract must be accepted before S1 writer design.

S1 design must begin from accepted migration routes, expected-state protections, transaction atomicity, branch and PR recovery, packet-to-PR fidelity, migration-ledger update semantics, protected-route denial, Noctua evidence, and Phoenix Reborn independence.

This contract does not authorize S1 implementation.

## 15. Cutover boundary

Prime may become `CUTOVER_CANDIDATE` only after complete Codex inventory, zero unexplained gaps, every disposition closed or explicitly blocked, work continuity mapped, current Spear and Emberline obligations dispositioned, source and generated surfaces verified, writer pilots proven, Noctua repository-wide audit passed, Phoenix Reborn backup and isolated restore passed, rollback and Codex retention documented, and startup/source-order files updated to reality.

Prime becomes `CANONICAL` only through explicit Jayson approval.

## 16. Acceptance criteria for this contract

This contract is acceptable when it introduces no migration content, moves no Codex source, changes no schema or policy, activates no writer, adds no workflow, creates no inventory entry, establishes a discoverable migration hub and reconciliation template, preserves current Prime/Codex authority boundaries, acknowledges current S0 ordinary-path limits, defines protected and generated routes honestly, requires zero-silent-loss closure, and stops before S1 design and execution.
