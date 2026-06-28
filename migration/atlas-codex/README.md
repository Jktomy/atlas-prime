---
title: Atlas Codex Migration Evidence Hub
atlas_id: atlas-prime.migration.atlas-codex.hub
format_version: "1.0"
status: PROPOSED
source_type: MIGRATION_RECORD
authority_class: MIGRATION_EVIDENCE
owner_project: Codex
owner_operation: Source Governance
canonical_scope: Entry point and evidence boundary for the future Atlas Codex to Atlas Prime source inventory, disposition ledger, migration map, audits, packet lineage, and closure records.
protected_level: CRITICAL
routes_from:
  - specs/atlas-prime/codex-to-prime-migration-contract-v2.md
routes_to:
  - schemas/migration/atlas-codex-inventory-v1.schema.json
  - schemas/migration/atlas-codex-delta-v1.schema.json
  - migration/atlas-codex/source-inventory.json
  - migration/atlas-codex/audits/source-inventory-preflight-v1.md
  - migration/atlas-codex/deltas/atlas-codex-delta-0001.json
  - migration/atlas-codex/audits/atlas-codex-delta-0001-preflight-v1.md
  - migration/atlas-codex/deltas/atlas-codex-delta-0002.json
  - migration/atlas-codex/audits/atlas-codex-delta-0002-preflight-v1.md
  - migration/atlas-codex/audits/atlas-codex-delta-0002-final-closeout-v1.md
  - migration/atlas-codex/audits/atlas-codex-delta-0001-merge-closeout-v1.md
  - migration/atlas-codex/audits/atlas-codex-delta-0001-final-closeout-v1.md
  - migration/atlas-codex/audits/atlas-active-workboard-authority-alignment-v1.md
  - migration/atlas-codex/reconciliations/c04-atlas-prime-core-doctrine-v1.md
  - migration/atlas-codex/migration-map.md
  - migration/atlas-codex/atlas-prime-rebuild-program-roadmap-v1.md
  - migration/atlas-codex/workboard-to-quest-board-crosswalk-v1.md
  - templates/codex-to-prime-reconciliation-record.md
private_boundary: This hub and its future child records may contain clean migration provenance and clean pointers only. They must not contain secrets, credentials, PHI, raw finance or account evidence, private runtime values, IP addresses, network maps, device registers, raw exports, or other prohibited evidence.
evidence_boundary: This directory records migration provenance. Atlas Codex source, Git history, current Atlas Prime source, original evidence systems, Spear artifacts, Noctua reports, pull requests, merge records, and recovery receipts remain distinct evidence sources.
supersedes: []
cleanup_path: Keep as the routed migration evidence entry point until migration closes. After cutover, retain or supersede it only through an approved retention and sunsetting decision.
last_verified: 2026-06-28
---

# Atlas Codex Migration Evidence Hub

## Current state

```text
Repository: Jktomy/atlas-prime
Predecessor: Jktomy/atlas-codex
Prime state: SHADOW
Migration control plane: ACTIVE — SHADOW-ONLY
Frozen source inventory: FROZEN_BASELINE — 349 PATHS
Ordered delta 0001: CLOSED — 15 CHANGED PATHS
Ordered delta 0002: CLOSED — 10 CHANGED PATHS
Accepted closed delta chain head: atlas-codex-delta:0002
Effective inventory after delta 0002: 352 LIVE PATHS
M0-D closure: CLOSED — GENERATED AND WORKBOARD READBACK VERIFIED
Active Workboard authority: `Jktomy/atlas-codex/codex/atlas-active-workboard.md` — EXTERNAL COPIES NONCANONICAL
C04 reconciliation: CLOSED_WITH_LINEAGE — PR #20 / `6c4662cf76d76d4af3958c77044d4ba4e7488591`
Preliminary disposition mapping: PRESENT — NOT EXECUTION AUTHORITY
Disposition ledger: NOT_STARTED
Migration map: PRESENT — PLANNING EVIDENCE ONLY
Program roadmap: PRESENT — PLANNING EVIDENCE ONLY
Quest Board: SHADOW SUCCESSOR — NOT CANONICAL
Content movement: NOT_AUTHORIZED
Spear writer: NOT_AUTHORIZED
Cutover: NOT_AUTHORIZED
```

This hub routes the immutable predecessor inventory, its historical preflight, the ordered delta chain, delta preflight evidence, and the migration map.

The inventory accounts for every tracked Atlas Codex path at the pinned source commit. Its preliminary dispositions remain migration evidence only and require later reconciliation before any packet or protected source PR.

The migration map organizes review waves, collision triage, pilot-selection rules, route classes, and closure gates. It does not authorize content movement, writer activation, source retirement, promotion, or cutover.

The disposition ledger and migration batches do not yet exist.

## Governing contract

The controlling migration process is:

`specs/atlas-prime/codex-to-prime-migration-contract-v2.md`

The machine-readable inventory must conform to:

`schemas/migration/atlas-codex-inventory-v1.schema.json`

Athena prepares each read-only reconciliation record from:

`templates/codex-to-prime-reconciliation-record.md`

## Current source inventory

- Path: `migration/atlas-codex/source-inventory.json`
- Source commit: `3e4f06ed4abf8fbd44bd04ec1ad8997ffae7eda4`
- Entries: `349`
- Unique source paths: `349`
- Internal inventory SHA-256: `03fa76c0991e06350cb112d1b33b1dbf00fe6296cabb08199cb92808956dd4fa`
- Preflight: `migration/atlas-codex/audits/source-inventory-preflight-v1.md`

`MAPPING_COMPLETE` in the inventory means every predecessor path has a provisional schema-valid disposition. It does not authorize migration, deletion, retirement, supersession, source promotion, writer activation, or cutover.

## Current ordered delta chain

- Delta path: `migration/atlas-codex/deltas/atlas-codex-delta-0001.json`
- Delta ID: `atlas-codex-delta:0001`
- Status: `CLOSED`
- Range: `3e4f06ed4abf8fbd44bd04ec1ad8997ffae7eda4` → `cdc4ae62eaff1c0d4a53e9f6b12873213b9f2f9f`
- Commits: `17`
- Changed paths: `15` (`2` added, `13` modified)
- Effective live paths: `351`
- Canonical delta digest: `8685089fec21cc5b8ec571ab6a5ace4519b71c8454b8ba1d872281e611738810`
- Preflight: `migration/atlas-codex/audits/atlas-codex-delta-0001-preflight-v1.md`
- Merge PR: `#14`
- Squash commit: `3a93006397d780cb6099a97a82524a90009df1fe`
- Merge closeout: `migration/atlas-codex/audits/atlas-codex-delta-0001-merge-closeout-v1.md`
- Final closeout: `migration/atlas-codex/audits/atlas-codex-delta-0001-final-closeout-v1.md`

The delta is CLOSED as M0-D control-plane evidence. Closure confirms the Prime generated-output and Codex Active Workboard consequences were completed and read back. It grants no content movement, collision resolution, Questboard migration, writer activation, promotion, retirement, deletion, or cutover authority.

### Accepted ordered delta 0002

- Delta path: `migration/atlas-codex/deltas/atlas-codex-delta-0002.json`
- Delta ID: `atlas-codex-delta:0002`
- Status: `CLOSED`
- Previous chain head: `atlas-codex-delta:0001` / `cdc4ae62eaff1c0d4a53e9f6b12873213b9f2f9f`
- Range: `cdc4ae62eaff1c0d4a53e9f6b12873213b9f2f9f` → `5cbf79a0851e0dda803be7b1abf153fffbad8414`
- Commits: `4`
- Changed paths: `10` (`1` added, `9` modified)
- Effective live paths after delta: `352`
- Previous PREVIEWED canonical digest: `4dae5e3e9f5a7928b332503288291fddf87a7b2148c5eeed461ab4d62757706f`
- Preflight: `migration/atlas-codex/audits/atlas-codex-delta-0002-preflight-v1.md`
- Source PR: `#22`
- Squash merge and Prime `main` readback: `17c01c481da9ce19fb1a2b74017aee08a5eb29f6`
- Final closeout: `migration/atlas-codex/audits/atlas-codex-delta-0002-final-closeout-v1.md`
- Closed canonical delta digest: `e233a0ef37ab407935ff6d701cd7ff28b5848f0788718cc8d2e06044f2ec9cb4`

Delta 0002 is CLOSED as a non-executing control-plane extension. It accounts for current Codex bytes and corrects C05 membership evidence; it does not move source content, create the disposition ledger, activate a writer, alter Workboard authority, promote Prime, retire Codex, or authorize cutover.

## Active Workboard authority alignment

The Google Drive revision used during M0-D remains valid historical execution evidence for the exact structured-register gate that was completed and read back.

Ongoing operational authority is now explicit:

- sole canonical Workboard: `Jktomy/atlas-codex/codex/atlas-active-workboard.md` on `main`;
- Google Drive and other external copies: noncanonical, unsynchronized, and permitted to remain stale;
- failed GitHub intake stored elsewhere: holding evidence only until reviewed and merged into GitHub;
- future Prime hierarchy: `Questboard -> Quests -> Campaigns`, not yet executed.

The alignment record is:

`migration/atlas-codex/audits/atlas-active-workboard-authority-alignment-v1.md`

This correction does not reopen M0-D and does not authorize M1 content movement.

## Current migration map

- Path: `migration/atlas-codex/migration-map.md`
- State: `PRESENT — PLANNING EVIDENCE ONLY`
- Inventory entries covered: `349`
- Preliminary collision groups: `18`
- C04 state: `CLOSED_WITH_LINEAGE`
- C04 protected-source merge: `6c4662cf76d76d4af3958c77044d4ba4e7488591`
- C05 preliminary source count: `7` — corrected from `6` by exact effective-inventory reconstruction

The map remains non-executing migration evidence. It does not approve broad migration packets, move unrelated content, activate S1, replace Atlas Codex authority, or authorize cutover.

## Quest Board and one-Arrow coordination

The Codex Active Workboard remains canonical. Prime Quest Board is the SHADOW successor governed by the crosswalk and Quest Board specification.

The rebuild program may be coordinated by one immutable Arrow with sealed stages, but this does not activate S1, authorize content movement, promote Prime, retire Codex, or authorize cutover.

The next safe planning gate is C07 read-only semantic reconciliation for `codex/codex-source-update-standard.md`, under a separate Preview -> Execute route.

## C04 protected-root-doctrine closure

Collision group C04 is closed with verified lineage:

- resolution: `SPLIT_INTO_MULTIPLE_TARGETS`;
- source members accounted for: `7/7`;
- target: `atlas-prime.md`;
- protected-source PR: `#20`;
- audited head: `519a4b8017035b079a7eea0fcba06517ff092d8b`;
- squash merge: `6c4662cf76d76d4af3958c77044d4ba4e7488591`;
- merged Git blob: `07c7636c78cd3c1c6456f7a06cf3f825fc167738`;
- merged SHA-256: `3aec2f99762149cb9e775b311c28ea99f28a94135a3317ced5faa28a563c5485`;
- Noctua outcome: `YES`;
- merged-main readback: `PASS`;
- Prime state: `SHADOW`;
- Codex canonical: `YES`.

Closure record:

`migration/atlas-codex/reconciliations/c04-atlas-prime-core-doctrine-v1.md`

No predecessor or addendum was deleted or retired. No broad content movement, disposition-ledger creation, S1 activation, Prime promotion, or cutover occurred.

## Remaining planned artifacts

The following path remains planned and is not active:

- `migration/atlas-codex/disposition-ledger.json`

It requires a later exact Preview and its appropriate migration PR.

Do not create empty placeholder ledgers merely to satisfy topology.

## Evidence separation

This directory may retain source path/hash inventories, explicit dispositions, clean preserved/remodeled-element records, clean pointers, packet IDs, PR and merge lineage, Noctua outcomes, and readback/closure receipts.

It must not retain raw protected records, private exports, secrets, credentials, account or medical evidence, copied chat transcripts, generated working directories, temporary compiler output, or unstaged review packages.

## Closure rule

The migration is not complete until every tracked Codex path has one explicit disposition and every migrated entry has verified target readback and lineage closure.

A merged PR is not enough.

A complete-looking target repository is not enough.

A missing inventory row is a migration failure.
