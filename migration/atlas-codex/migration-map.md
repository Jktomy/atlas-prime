---
title: Atlas Codex to Atlas Prime Migration Map v1
atlas_id: atlas-prime.migration.atlas-codex.map.v1
format_version: "1.0"
status: PROPOSED
source_type: MIGRATION_RECORD
authority_class: MIGRATION_EVIDENCE
owner_project: Codex
owner_operation: Source Governance
canonical_scope: Defines the review waves, collision-triage order, pilot-selection rules, route classes, and closure gates for reconciling the exact Atlas Codex source inventory into Atlas Prime without authorizing content movement.
protected_level: CRITICAL
routes_from:
  - specs/atlas-prime/codex-to-prime-migration-contract-v2.md
  - migration/atlas-codex/deltas/atlas-codex-delta-0001.json
  - migration/atlas-codex/audits/atlas-codex-delta-0001-preflight-v1.md
  - migration/atlas-codex/audits/atlas-codex-delta-0001-merge-closeout-v1.md
  - migration/atlas-codex/README.md
  - migration/atlas-codex/source-inventory.json
  - migration/atlas-codex/audits/source-inventory-preflight-v1.md
  - templates/codex-to-prime-reconciliation-record.md
routes_to:
  - templates/codex-to-prime-reconciliation-record.md
private_boundary: This migration map may contain clean source paths, target paths, counts, classifications, route assignments, dependencies, review states, and clean pointers only. It must not contain secrets, credentials, PHI, raw finance or account evidence, private runtime values, IP addresses, network maps, device registers, raw exports, or prohibited evidence.
evidence_boundary: This file is migration-planning evidence. Atlas Codex source, Atlas Prime source, Git history, original evidence systems, reconciliation records, Spear receipts, pull requests, Noctua reports, and Phoenix proofs remain distinct evidence sources.
supersedes: []
cleanup_path: Retain throughout the migration campaign. Replace only through a later versioned migration-map PR, and retain predecessor versions as migration evidence.
last_verified: 2026-06-27
---

# Atlas Codex to Atlas Prime Migration Map v1

## 1. Authority and current state

```text
Source repository: Jktomy/atlas-codex
Inventoried source commit: 3e4f06ed4abf8fbd44bd04ec1ad8997ffae7eda4
Current canonical repository: Jktomy/atlas-codex

Target repository: Jktomy/atlas-prime
Current target base: 0c7ef6566d6d3a5df19b21c055036844e7edafc8
Target state: SHADOW

Frozen inventory entries: 349
Frozen unique source paths: 349
Accepted delta chain head: atlas-codex-delta:0001 - MERGED
Current Codex chain head: cdc4ae62eaff1c0d4a53e9f6b12873213b9f2f9f
Effective live paths: 351
Accounted lineage paths: 351
Canonical inventory digest:
03fa76c0991e06350cb112d1b33b1dbf00fe6296cabb08199cb92808956dd4fa

Preliminary destination collision groups: 18
Semantic reconciliation complete: NO
Content movement authorized: NO
S1 authorized: NO
Writer authority: NO
Cutover authorized: NO
```

This map organizes review and migration sequencing.

It does not finalize any inventory disposition, authorize an overwrite, approve a packet, move content, activate a writer, retire predecessor source, or promote Atlas Prime.

## 2. Mapping rules

1. Every one of the 349 inventoried paths remains accounted for.
2. Preliminary inventory mappings remain provisional until reconciliation closes.
3. Collision groups are reviewed before any member is migrated.
4. `RETIRE`, `SUPERSEDE`, `OMIT_WITH_REASON`, `PRIVATE_POINTER`, `MERGE`, and high-consequence `REMODEL` entries receive explicit semantic review.
5. Structured registers and generated outputs do not use ordinary Markdown migration routes.
6. Protected doctrine, schemas, policies, tools, workflows, startup files, and source-order files use protected-source PRs.
7. Private or prohibited evidence remains outside GitHub.
8. Atlas Codex continues to control operational meaning until explicit cutover.
9. Atlas Prime doctrine controls the intended successor architecture.
10. Any material disagreement becomes `NEEDS_JAYSON`.

## 3. Review-state vocabulary

The map may use only these planning states:

- `UNREVIEWED`
- `IN_REVIEW`
- `NEEDS_JAYSON`
- `BLOCKED_PENDING_CONTRACT`
- `READY_FOR_RECONCILIATION`
- `RESOLVED_FOR_MAP`
- `READY_FOR_PILOT_PREVIEW`
- `CLOSED_WITH_LINEAGE`

These states describe planning evidence only.

They do not grant execution authority.

## 4. Migration waves

| Wave | Name | Purpose | Entry criteria | Exit gate | Content movement |
|---|---|---|---|---|---|
| M0 | Control-plane foundation | Maintain inventory, preflight, migration map, ledger, and clean migration evidence. | Migration-evidence artifacts only. | Evidence is internally consistent, reviewed, and merged. | No |
| M1 | Collision and consequence triage | Review all 18 collision groups and all high-consequence preliminary dispositions. | Collision member, `RETIRE`, `SUPERSEDE`, `OMIT_WITH_REASON`, `PRIVATE_POINTER`, `MERGE`, or high-risk `REMODEL`. | Each item is `RESOLVED_FOR_MAP`, `NEEDS_JAYSON`, or `BLOCKED_PENDING_CONTRACT`. | No |
| M2 | Low-risk pilot shortlist | Identify the safest candidates for the first migration pilot. | `MIGRATE`, `FULL`, `PUBLIC_CLEAN`, `MAPPED`, no collision, no protected surface, no structured or generated content, dependencies resolved. | One recommended pilot and up to two alternates are documented. | No |
| M3 | First controlled pilot | Complete one reconciliation record, exact Preview, execution, Noctua audit, manual merge, and main readback. | One approved M2 candidate. | Inventory and ledger lineage close for every pilot entry. | Only after separate approval |
| M4 | Low-risk ordinary waves | Migrate additional clean project and operation source using proven routes. | Same route class and risk profile as the successful pilot. | Each bounded batch closes independently. | Only after separate approvals |
| M5 | Merge and remodel waves | Reconcile duplicated, reorganized, or structurally redesigned source. | Reviewed `MERGE` and `REMODEL` entries with resolved target architecture. | Complete semantic reconciliation and visible old-to-new accounting. | Only after separate approvals |
| M6 | Private, prohibited, omission, and history closure | Close pointer-only, prohibited, omitted, and historical entries safely. | `PRIVATE_POINTER`, `OMIT_WITH_REASON`, `HISTORICAL_REFERENCE`, privacy-restricted entries. | Clean pointer, omission reason, or historical retention evidence is approved and recorded. | No raw protected transfer |
| M7 | Structured registers and generated rebuilds | Transition Workboard, Quest, Golden Wing, events, and generated archives through versioned contracts. | Structured or generated source. | Dedicated register or generator contract and proof exist. | Only after separate approvals |
| M8 | Protected doctrine and source-order transition | Reconcile root doctrine, governance, safety protocols, schemas, policies, tools, workflows, startup, routing, and source order. | Protected or critical source. | Complete readback, Noctua, rollback, and manual merge. | Only after separate approvals |
| M9 | Repository-wide proof and cutover preparation | Prove closure, restore, rollback, continuity, and successor readiness. | Earlier waves substantially closed. | Noctua repository audit, Phoenix isolated restore, rollback proof, and explicit Jayson decision. | No cutover without approval |

## 5. Preliminary collision register

The following collision groups are provisional and must be revalidated directly against the exact inventory before this map is written durably.

| ID | Proposed Prime target | Preliminary source count | Route class | Risk | Required review |
|---|---|---:|---|---|---|
| C01 | `codex/golden-wing/candidates.json` | 36 | Structured-register transition | High | Determine candidate identity, deduplication, state, and event lineage. |
| C02 | `codex/golden-wing/events/2026/2026-06.jsonl` | 36 | Structured-register transition | High | Preserve append-only event identity and ordering; do not flatten into authored prose. |
| C03 | `atlas-feather-archives/2026/2026-06.md` | 22 | Generated rebuild / historical projection | High | Identify authoritative inputs and rebuild contract before transfer. |
| C04 | `atlas-prime.md` | 7 | Protected root doctrine | Critical | Reconcile authority, predecessor meaning, and current Prime doctrine without overwriting blindly. |
| C05 | `atlas-index.md` | 6 | Protected routing source | Critical | Resolve routing ownership and generated-versus-authored boundaries. |
| C06 | `codex/governance/protected-source-boundary.md` | 6 | Protected governance | Critical | Consolidate without weakening private-source boundaries. |
| C07 | `codex/codex-source-update-standard.md` | 5 | Protected source standard | Critical | Preserve Preview → Execute, recovery, readback, and audit safeguards. |
| C08 | `atlas-command-surface.md` | 4 | Protected root command surface | Critical | Reconcile current command semantics and successor routing. |
| C09 | `atlas-aegis.md` | 3 | Protected safety doctrine | Critical | Preserve all hard stops and authority boundaries. |
| C10 | `atlas-knowledge-lifecycle.md` | 3 | Protected lifecycle doctrine | Critical | Reconcile lifecycle states, source classes, retention, and supersession. |
| C11 | `athenas-spear.md` | 2 | Protected tool contract | Critical | Keep operational Codex Spear distinct from Prime S0 and future S1. |
| C12 | `codex/governance/versioning-and-supersession.md` | 2 | Protected governance | Critical | Resolve predecessor retention and non-destructive supersession. |
| C13 | `codex/quests/quest-registry.json` | 2 | Structured-register transition | High | Require record-by-record Workboard-to-Quest transition contract. |
| C14 | `noctua.md` | 2 | Protected audit doctrine | Critical | Preserve independent audit, packet fidelity, and merged-main readback. |
| C15 | `phoenix-flare.md` | 2 | Protected recovery/continuity doctrine | Critical | Separate continuity handoff from actual Phoenix restore proof. |
| C16 | `projects/artemis/operations/nexus/protocols/argus.md` | 2 | Protected protocol merge | High | Reconcile router, parent protocol, and operational behavior. |
| C17 | `projects/odyssey/operations/runtime-governance/operation.md` | 2 | Protected/private-boundary route | Critical | Preserve clean pointers only; do not import private runtime values. |
| C18 | `sunsetting-protocol.md` | 2 | Protected continuity protocol | Critical | Preserve durable/chat-only/unfinished/archive-safe distinctions and Workboard handoff. |

## 6. Collision-review procedure

Each collision group must be handled as one reconciliation unit.

For each group:

1. Enumerate every source member from the exact inventory.
2. Verify source path, blob SHA, SHA-256, privacy class, preliminary disposition, transfer class, and dependencies.
3. Read every source member completely.
4. Read the current Prime target completely, when it exists.
5. Identify unique meaning, duplicated meaning, stale meaning, contradictions, private boundaries, and generated or structured state.
6. Select one proposed resolution:
   - merge into one target;
   - split into multiple targets;
   - retain multiple distinct targets;
   - generated rebuild;
   - structured-register transition;
   - private pointer;
   - historical retention;
   - blocked pending contract;
   - `NEEDS_JAYSON`.
7. Record preserved and removed or remodeled elements.
8. Identify the correct migration route.
9. Define tests, recovery, Noctua, and merged-main closure requirements.
10. Do not prepare an execution packet until the reconciliation record is complete.

## 7. High-consequence disposition review

Review priority:

1. `RETIRE`
2. `SUPERSEDE`
3. `OMIT_WITH_REASON`
4. `PRIVATE_POINTER`
5. `MERGE`
6. high-risk `REMODEL`

For each item, verify:

- no surviving operational dependency;
- no routing orphan;
- no silent loss of unique meaning;
- no private evidence copied into GitHub;
- no generated output mistaken for authored source;
- no predecessor deleted merely because a proposed successor exists;
- explicit approval basis;
- rollback and retention requirements.

## 8. Pilot-selection filter

A first-pilot candidate must satisfy all of the following:

- preliminary disposition `MIGRATE`;
- content transfer `FULL`;
- privacy class `PUBLIC_CLEAN`;
- record state `MAPPED`;
- not part of any collision group;
- proposed target beneath an ordinary `projects/` route;
- not a root, governance, schema, policy, tool, test, workflow, structured-register, generated, startup, source-order, finance-evidence, medical-evidence, or private-runtime surface;
- dependencies resolved;
- current source can be read completely, and the proposed Prime target can be read completely when it exists; otherwise, target absence is verified against the pinned Prime base;
- no unresolved Decision Box;
- bounded enough for full human diff and merged-main readback.

The M2 output should identify:

- one recommended pilot;
- up to two alternates;
- exact source and target paths;
- reason each candidate is safe;
- route class;
- expected tests;
- recovery plan;
- explicit exclusions.

Selecting a pilot does not authorize execution.

## 9. Per-wave closure rule

A planning wave closes only when every included entry has:

- completed reconciliation or planning evidence appropriate to the wave;
- an approved disposition, review state, or explicit `NEEDS_JAYSON` or `BLOCKED_PENDING_CONTRACT` state;
- an approved route or documented reason that no execution route is yet applicable;
- all required wave outputs reviewed and durably recorded;
- unresolved obligations recorded explicitly.

When a wave executes a migration packet or protected source PR, closure additionally requires:

- packet or source-PR identity;
- Noctua result;
- PR identity;
- merge commit;
- merged-main readback;
- final target hash;
- inventory and disposition-ledger closure state.

Planning-only waves do not require execution lineage that has not yet been authorized.

An executed migration is not complete until all applicable execution-lineage evidence is closed.

## 10. M0-D ordered-delta closure gate

Current M0-D evidence:

- frozen baseline remains immutable at `3e4f06ed4abf8fbd44bd04ec1ad8997ffae7eda4`;
- delta `0001` spans `17` contiguous commits through `cdc4ae62eaff1c0d4a53e9f6b12873213b9f2f9f`;
- all `15` changed paths are represented exactly once;
- PR `#14` was squash-merged as `3a93006397d780cb6099a97a82524a90009df1fe` and Prime `main` readback passed;
- delta `0001` is recorded as `MERGED`, while final M0-D closure remains pending;
- effective live and accounted-lineage counts are `351`;
- five changed generated projections remain on the separate `GENERATED_REBUILD` route;
- the Active Workboard consequence remains on the separate structured-register route;
- content movement, collision resolution, the disposition ledger, S1 activation, promotion, retirement, and cutover remain unauthorized.

M1-A remains blocked until generated consequences are closed through their own route, the Workboard records the current M0-D gate, and the final delta transition from `MERGED` to `CLOSED` is merged and read back.

## 11. Immediate next planning action

The next read-only actions after this merge closeout should be:

```text
Complete the two remaining M0-D closure routes before M1-A:

1. Approve a Prime generator contract and rebuild the five generated projections
   through a separate generated-output route.
2. Update the Atlas Active Workboard through its separate structured-register route.
3. Read both routes back from their canonical destinations.
4. Prepare the final delta transition from MERGED to CLOSED.

M1-A remains blocked until those closure obligations are complete.
```

No content movement, target replacement, retirement, supersession, omission closure, structured-register transition, S1 work, or cutover is authorized by this map.
