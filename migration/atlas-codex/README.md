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
  - specs/atlas-prime/codex-to-prime-migration-contract-v1.md
routes_to:
  - schemas/migration/atlas-codex-inventory-v1.schema.json
  - migration/atlas-codex/source-inventory.json
  - migration/atlas-codex/audits/source-inventory-preflight-v1.md
  - templates/codex-to-prime-reconciliation-record.md
private_boundary: This hub and its future child records may contain clean migration provenance and clean pointers only. They must not contain secrets, credentials, PHI, raw finance or account evidence, private runtime values, IP addresses, network maps, device registers, raw exports, or other prohibited evidence.
evidence_boundary: This directory records migration provenance. Atlas Codex source, Git history, current Atlas Prime source, original evidence systems, Spear artifacts, Noctua reports, pull requests, merge records, and recovery receipts remain distinct evidence sources.
supersedes: []
cleanup_path: Keep as the routed migration evidence entry point until migration closes. After cutover, retain or supersede it only through an approved retention and sunsetting decision.
last_verified: 2026-06-25
---

# Atlas Codex Migration Evidence Hub

## Current state

```text
Repository: Jktomy/atlas-prime
Predecessor: Jktomy/atlas-codex
Prime state: SHADOW
Migration control plane: PROPOSED
Source inventory: INVENTORY_COMPLETE
Preliminary disposition mapping: PRESENT — NOT EXECUTION AUTHORITY
Disposition ledger: NOT_STARTED
Migration map: NOT_STARTED
Content movement: NOT_AUTHORIZED
Spear writer: NOT_AUTHORIZED
Cutover: NOT_AUTHORIZED
```

This hub routes the exact predecessor inventory and its preflight audit.

The inventory accounts for every tracked Atlas Codex path at the pinned source commit. Its preliminary dispositions remain migration evidence only and require later reconciliation before any packet or protected source PR.

The disposition ledger, migration map, and migration batches do not yet exist.

## Governing contract

The controlling migration process is:

`specs/atlas-prime/codex-to-prime-migration-contract-v1.md`

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

## Planned artifacts

The following paths are planned, not active:

- `migration/atlas-codex/source-inventory.json`
- `migration/atlas-codex/disposition-ledger.json`
- `migration/atlas-codex/migration-map.md`
- `migration/atlas-codex/audits/`

They require later exact Previews and their appropriate migration PRs.

Do not create empty placeholder ledgers merely to satisfy topology.

## Evidence separation

This directory may retain source path/hash inventories, explicit dispositions, clean preserved/remodeled-element records, clean pointers, packet IDs, PR and merge lineage, Noctua outcomes, and readback/closure receipts.

It must not retain raw protected records, private exports, secrets, credentials, account or medical evidence, copied chat transcripts, generated working directories, temporary compiler output, or unstaged review packages.

## Closure rule

The migration is not complete until every tracked Codex path has one explicit disposition and every migrated entry has verified target readback and lineage closure.

A merged PR is not enough.

A complete-looking target repository is not enough.

A missing inventory row is a migration failure.
