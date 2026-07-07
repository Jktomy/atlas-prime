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
  - migration/atlas-codex/deltas/atlas-codex-delta-0002.json
  - migration/atlas-codex/audits/atlas-codex-delta-0002-preflight-v1.md
  - migration/atlas-codex/audits/atlas-codex-delta-0002-final-closeout-v1.md
  - migration/atlas-codex/audits/atlas-codex-delta-0001-merge-closeout-v1.md
  - migration/atlas-codex/audits/atlas-codex-delta-0001-final-closeout-v1.md
  - migration/atlas-codex/audits/atlas-active-workboard-authority-alignment-v1.md
  - migration/atlas-codex/reconciliations/c04-atlas-prime-core-doctrine-v1.md
  - migration/atlas-codex/reconciliations/c07-source-update-standard-v1.md
  - migration/atlas-codex/README.md
  - migration/atlas-codex/source-inventory.json
  - migration/atlas-codex/audits/source-inventory-preflight-v1.md
  - templates/codex-to-prime-reconciliation-record.md
routes_to:
  - migration/atlas-codex/atlas-prime-rebuild-program-roadmap-v1.md
  - migration/atlas-codex/workboard-to-quest-board-crosswalk-v1.md
  - templates/codex-to-prime-reconciliation-record.md
private_boundary: This migration map may contain clean source paths, target paths, counts, classifications, route assignments, dependencies, review states, and clean pointers only. It must not contain secrets, credentials, PHI, raw finance or account evidence, private runtime values, IP addresses, network maps, device registers, raw exports, or prohibited evidence.
evidence_boundary: This file is migration-planning evidence. Atlas Codex source, Atlas Prime source, Git history, original evidence systems, reconciliation records, Spear receipts, pull requests, Noctua reports, and Phoenix proofs remain distinct evidence sources.
supersedes: []
cleanup_path: Retain throughout the migration campaign. Replace only through a later versioned migration-map PR, and retain predecessor versions as migration evidence.
last_verified: 2026-07-06
---

# Atlas Codex to Atlas Prime Migration Map v1

## 1. Authority and current state

```text
Source repository: Jktomy/atlas-codex
Inventoried source commit: 3e4f06ed4abf8fbd44bd04ec1ad8997ffae7eda4
Current canonical repository: Jktomy/atlas-codex

Target repository: Jktomy/atlas-prime
C04 protected-source merge: 6c4662cf76d76d4af3958c77044d4ba4e7488591
Target state: SHADOW

Frozen inventory entries: 349
Frozen unique source paths: 349
Accepted closed delta chain head: atlas-codex-delta:0002 - CLOSED
Current Codex chain head: 5cbf79a0851e0dda803be7b1abf153fffbad8414
Effective live paths after delta 0002: 352
Accounted lineage paths after delta 0002: 352
Canonical inventory digest:
03fa76c0991e06350cb112d1b33b1dbf00fe6296cabb08199cb92808956dd4fa

Preliminary destination collision groups: 18
C04 collision state: CLOSED_WITH_LINEAGE
C04 closure record: migration/atlas-codex/reconciliations/c04-atlas-prime-core-doctrine-v1.md
C07 collision state: CLOSED_WITH_LINEAGE
C07 closure record: migration/atlas-codex/reconciliations/c07-source-update-standard-v1.md
Semantic reconciliation complete: NO
Program roadmap: PRESENT — PLANNING EVIDENCE ONLY
Quest Board authority: SHADOW
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
| M1 | Collision and consequence triage | Review all 18 collision groups and all high-consequence preliminary dispositions. | Collision member, `RETIRE`, `SUPERSEDE`, `OMIT_WITH_REASON`, `PRIVATE_POINTER`, `MERGE`, or high-risk `REMODEL`. | Each item is `RESOLVED_FOR_MAP`, `CLOSED_WITH_LINEAGE`, `NEEDS_JAYSON`, or `BLOCKED_PENDING_CONTRACT`. | No |
| M2 | Low-risk pilot shortlist | Identify the safest candidates for the first migration pilot. | `MIGRATE`, `FULL`, `PUBLIC_CLEAN`, `MAPPED`, no collision, no protected surface, no structured or generated content, dependencies resolved. | One recommended pilot and up to two alternates are documented. | No |
| M3 | First controlled pilot | Complete one reconciliation record, exact Preview, execution, Noctua audit, manual merge, and main readback. | One approved M2 candidate. | Inventory and ledger lineage close for every pilot entry. | Only after separate approval |
| M4 | Low-risk ordinary waves | Migrate additional clean project and operation source using proven routes. | Same route class and risk profile as the successful pilot. | Each bounded batch closes independently. | Only after separate approvals |
| M5 | Merge and remodel waves | Reconcile duplicated, reorganized, or structurally redesigned source. | Reviewed `MERGE` and `REMODEL` entries with resolved target architecture. | Complete semantic reconciliation and visible old-to-new accounting. | Only after separate approvals |
| M6 | Private, prohibited, omission, and history closure | Close pointer-only, prohibited, omitted, and historical entries safely. | `PRIVATE_POINTER`, `OMIT_WITH_REASON`, `HISTORICAL_REFERENCE`, privacy-restricted entries. | Clean pointer, omission reason, or historical retention evidence is approved and recorded. | No raw protected transfer |
| M7 | Structured registers and generated rebuilds | Transition Workboard, Quest, Golden Wing, events, and generated archives through versioned contracts. | Structured or generated source. | Dedicated register or generator contract and proof exist. | Only after separate approvals |
| M8 | Protected doctrine and source-order transition | Reconcile root doctrine, governance, safety protocols, schemas, policies, tools, workflows, startup, routing, and source order. | Protected or critical source. | Complete readback, Noctua, rollback, and manual merge. | Only after separate approvals |
| M9 | Repository-wide proof and cutover preparation | Prove closure, restore, rollback, continuity, and successor readiness. | Earlier waves substantially closed. | Noctua repository audit, Phoenix isolated restore, rollback proof, and explicit Jayson decision. | No cutover without approval |

### Cross-campaign architecture

The parent Quest is `Atlas Prime Rebuild`.

Child Campaigns include Codex-to-Prime migration, Google Drive dependency retirement, Spear/Bow/Arrow development, and Quest Board/Emberline architecture.

The Codex Workboard remains canonical. Prime Quest Board remains SHADOW.

One immutable Arrow may coordinate the source PRs and generated follow-through through separately approved sealed stages. This statement grants no writer, merge, migration, promotion, retirement, deletion, or cutover authority.

## 5. Preliminary collision register

This register began as provisional. Each unresolved collision group must be revalidated directly against the exact inventory before resolution; closed groups carry explicit lineage.

| ID | Proposed Prime target | Preliminary source count | Route class | Risk | Required review |
|---|---|---:|---|---|---|
| C01 | `codex/golden-wing/candidates.json` | 36 | Structured-register transition | High | Determine candidate identity, deduplication, state, and event lineage. |
| C02 | `codex/golden-wing/events/2026/2026-06.jsonl` | 36 | Structured-register transition | High | Preserve append-only event identity and ordering; do not flatten into authored prose. |
| C03 | `atlas-feather-archives/2026/2026-06.md` | 22 | Generated rebuild / historical projection | High | Identify authoritative inputs and rebuild contract before transfer. |
| C04 | `atlas-prime.md` | 7 | Protected root doctrine | Critical | `CLOSED_WITH_LINEAGE` — protected-source PR `#20` merged and read back; see `migration/atlas-codex/reconciliations/c04-atlas-prime-core-doctrine-v1.md`. |
| C05 | `atlas-index.md` | 7 | Protected routing source | Critical | Exact reconstruction corrected the preliminary count from 6 to 7; resolve routing ownership and generated-versus-authored boundaries. |
| C06 | `codex/governance/protected-source-boundary.md` | 6 | Protected governance | Critical | Consolidate without weakening private-source boundaries. |
| C07 | `codex/codex-source-update-standard.md` | 5 | Protected source standard | Critical | `CLOSED_WITH_LINEAGE` — PR `#34` merged/read back; see `migration/atlas-codex/reconciliations/c07-source-update-standard-v1.md`. |
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

### Closed collision lineage

| ID | State | Resolution | Source members | Protected-source PR | Merge commit | Final target SHA-256 |
|---|---|---|---:|---|---|---|
| C04 | `CLOSED_WITH_LINEAGE` | `SPLIT_INTO_MULTIPLE_TARGETS` | 7/7 accounted | `#20` | `6c4662cf76d76d4af3958c77044d4ba4e7488591` | `3aec2f99762149cb9e775b311c28ea99f28a94135a3317ced5faa28a563c5485` |
| C07 | `CLOSED_WITH_LINEAGE` | `MERGE_INTO_ONE_TARGET_WITH_RETAINED_PREDECESSORS` | 5/5 accounted | `#34` | `1dd3d689931d52258f049a38546681c9498692dc` | `a59a835cc97a337b38fc797a0ef14bbb77223513db1010f21f6b5e2364ed021d` |

C04 closed only the protected root-doctrine target. Its predecessor sources and temporary addenda remain retained and routed. No source deletion, retirement, broad content movement, Prime promotion, or cutover occurred.

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
- PR `#14` was squash-merged as `3a93006397d780cb6099a97a82524a90009df1fe` and its merge closeout remains immutable;
- PR `#16` merged the Prime-native generated-index foundation as `0b09425172df0562cbe65a418fce9fbead0e9472`;
- PR `#17` rebuilt the five Prime generated projections and was read back from Prime `main` at `126a7e4329dc217dc99661da375a2966d76d119c`;
- Drive revision `0Bz1aLTIXmYtUaXhFUGhCT2gvNzhLaTdKSURnZVNqNGVzQVhjPQ` with SHA-256 `8f735bcadf7b7f770332ad0586fdde6d1768ce46285c8279f682d2535d9aa477` remains valid historical M0-D execution evidence;
- ongoing Active Workboard authority belongs only to `Jktomy/atlas-codex/codex/atlas-active-workboard.md` on `main`; external copies are noncanonical, unsynchronized, and may remain stale;
- delta `0001` is recorded as `CLOSED`;
- accepted delta `0002` spans `4` contiguous commits from `cdc4ae62eaff1c0d4a53e9f6b12873213b9f2f9f` through `5cbf79a0851e0dda803be7b1abf153fffbad8414` and records `10` changed paths;
- PR `#22` was squash-merged and read back from Prime `main` at `17c01c481da9ce19fb1a2b74017aee08a5eb29f6`;
- delta `0002` is recorded as `CLOSED`; final closeout: `migration/atlas-codex/audits/atlas-codex-delta-0002-final-closeout-v1.md`;
- C05 preliminary source accounting is corrected from `6` to `7` exact members;
- effective live and accounted-lineage counts become `352` after delta `0002`;
- M0-D itself authorized no content movement, collision resolution, disposition-ledger creation, S1 activation, Questboard migration, promotion, retirement, or cutover; later C04 closure authority is recorded separately.

The M1-A read-only evidence preflight and collision-review corpus were completed against verified Codex and Prime heads. C04 is now `CLOSED_WITH_LINEAGE`; the remaining collision groups continue through separate semantic reconciliation routes. No broad content movement or writer activation is authorized.

## 11. Immediate next planning action

After Stage 1 merges, the next safe planning action is Stage 2 Codex Workboard synchronization, gated on readback of the exact Stage 1 Prime candidate blobs recorded in `source-bindings.json`. After Stage 2 merges, generated refresh remains a separate route for both repositories and the next M1 read-only recommendation is C06 protected-boundary governance.

No predecessor retirement, Prime promotion, Codex retirement, generated refresh, or cutover is authorized by this map.
