---
title: Atlas Codex Ordered Delta 0001 Preflight v1
atlas_id: atlas-prime.migration.atlas-codex.delta-0001-preflight-v1
format_version: "1.0"
status: PROPOSED
source_type: MIGRATION_RECORD
authority_class: MIGRATION_EVIDENCE
owner_project: Codex
owner_operation: Source Governance
canonical_scope: Verifies ordered delta 0001 from the immutable 349-entry Codex baseline through exact Codex commit cdc4ae62eaff1c0d4a53e9f6b12873213b9f2f9f, including target observations and generated consequences, without authorizing migration execution.
protected_level: CRITICAL
routes_from:
  - specs/atlas-prime/codex-to-prime-migration-contract-v2.md
  - schemas/migration/atlas-codex-delta-v1.schema.json
  - migration/atlas-codex/deltas/atlas-codex-delta-0001.json
routes_to:
  - migration/atlas-codex/README.md
  - migration/atlas-codex/migration-map.md
private_boundary: This audit contains clean paths, counts, hashes, classifications, and target observations only. It must not contain secrets, credentials, PHI, raw finance or account evidence, private runtime values, IP addresses, network maps, device registers, or raw protected exports.
evidence_boundary: Codex Git objects, the immutable baseline, delta 0001, current Prime source, generated systems, later reconciliation records, pull requests, Noctua reports, and merge receipts remain distinct evidence sources.
supersedes: []
cleanup_path: Retain with delta 0001 as immutable migration evidence. Replace only through a later versioned audit; do not rewrite historical hashes or freshness results.
last_verified: 2026-06-27
---

# Atlas Codex Ordered Delta 0001 Preflight v1

## Bound repositories

- Frozen Codex start: `3e4f06ed4abf8fbd44bd04ec1ad8997ffae7eda4`
- Current Codex end: `cdc4ae62eaff1c0d4a53e9f6b12873213b9f2f9f`
- Prime target observation: `0c7ef6566d6d3a5df19b21c055036844e7edafc8`
- Prime state: `SHADOW`
- Codex remains canonical: **YES**

## Frozen baseline

- Inventory blob: `f95c3fab4ce296c11f4f277c8e4675071cc92091`
- Inventory file SHA-256: `4d883149cef72e6d94805da73b0deda322ef1350ea848b29edf25cc6931c1856`
- Canonical inventory digest: `03fa76c0991e06350cb112d1b33b1dbf00fe6296cabb08199cb92808956dd4fa`
- Entries and unique paths: **349 / 349**
- Historical inventory modified: **NO**

## Ordered delta identity

- Delta ID: `atlas-codex-delta:0001`
- Status: `PREVIEWED`
- Schema blob: `507370d186762358223f196a47afe13c4474327e`
- Schema SHA-256: `4bf2ee9ca3d285f5cc08745d9f17360f75a681bf29dbaefc1da60c87bca98b11`
- Canonical delta digest: `d1c6043a1ccba63d1134e939eacf163384e0fd7e2f77abb6b016123cd9e8b3f0`
- Execution authority: `NONE`

## Reproduced comparison

- Commits: **17**
- Changed paths: **15**
- Added: **2**
- Modified: **13**
- Removed: **0**
- Renamed: **0**
- Contiguous and zero-behind: **PASS**

## Effective inventory

- Live paths: **351**
- Accounted lineage: **351**
- Normalized or case-only live collisions: **0**
- Unresolved delta entries: **0**

## Generated consequences

The following five changed Codex projections remain `GENERATED_REBUILD` evidence and are not copied or manually authored in Prime:

- `generated/atlas-duplicate-scope-report.md`
- `generated/atlas-file-inventory.md`
- `generated/atlas-metadata-inventory.md`
- `generated/atlas-orphan-report.md`
- `generated/atlas-routing-inventory.md`

A later Prime generator contract and separate generated-output route remain required.

## Structured-register consequence

`codex/atlas-active-workboard.md` changed in Codex, but no Workboard update is included in this migration-evidence proposal. Workboard-to-Quest continuity remains a separate structured-register transition.

## Authority boundary

This preflight does not authorize content movement, collision resolution, disposition-ledger creation, generated-output creation, Workboard transition, S1 dispatch or activation, branch cleanup, promotion, Codex retirement, deletion, or cutover.

## Outcome

```text
Frozen baseline identity: PASS
Baseline-to-current comparison: PASS
Every changed path represented exactly once: PASS
Delta canonical digest: PASS
Effective path accounting: PASS
Target observations bound to exact Prime commit: PASS
Source/generated separation: PASS
Migration execution authority: NO
```
