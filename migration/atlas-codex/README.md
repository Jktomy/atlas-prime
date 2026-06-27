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
  - migration/atlas-codex/audits/atlas-codex-delta-0001-merge-closeout-v1.md
  - migration/atlas-codex/audits/atlas-codex-delta-0001-final-closeout-v1.md
  - migration/atlas-codex/audits/atlas-active-workboard-authority-alignment-v1.md
  - migration/atlas-codex/migration-map.md
  - templates/codex-to-prime-reconciliation-record.md
private_boundary: This hub and its future child records may contain clean migration provenance and clean pointers only. They must not contain secrets, credentials, PHI, raw finance or account evidence, private runtime values, IP addresses, network maps, device registers, raw exports, or other prohibited evidence.
evidence_boundary: This directory records migration provenance. Atlas Codex source, Git history, current Atlas Prime source, original evidence systems, Spear artifacts, Noctua reports, pull requests, merge records, and recovery receipts remain distinct evidence sources.
supersedes: []
cleanup_path: Keep as the routed migration evidence entry point until migration closes. After cutover, retain or supersede it only through an approved retention and sunsetting decision.
last_verified: 2026-06-27
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
Effective inventory: 351 LIVE PATHS
M0-D closure: CLOSED — GENERATED AND WORKBOARD READBACK VERIFIED
Active Workboard authority: `Jktomy/atlas-codex/codex/atlas-active-workboard.md` — EXTERNAL COPIES NONCANONICAL
Preliminary disposition mapping: PRESENT — NOT EXECUTION AUTHORITY
Disposition ledger: NOT_STARTED
Migration map: PRESENT — PLANNING EVIDENCE ONLY
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

The map remains non-executing migration evidence. It does not finalize dispositions, approve packets, move content, activate S1, replace Atlas Codex authority, or authorize cutover.

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
