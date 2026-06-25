---
title: Atlas Codex Source Inventory Preflight v1
atlas_id: atlas-prime.migration.atlas-codex.source-inventory-preflight-v1
format_version: "1.0"
status: PROPOSED
source_type: MIGRATION_RECORD
authority_class: MIGRATION_EVIDENCE
owner_project: Codex
owner_operation: Source Governance
canonical_scope: Verifies the exact 349-path Atlas Codex source inventory, current predecessor commit, internal digest, preliminary classifications, privacy boundaries, and non-execution status before the inventory is proposed for Atlas Prime.
protected_level: CRITICAL
routes_from:
  - migration/atlas-codex/source-inventory.json
  - specs/atlas-prime/codex-to-prime-migration-contract-v1.md
routes_to:
  - migration/atlas-codex/README.md
private_boundary: This audit names clean paths, counts, hashes, and risk classes only. It must not reproduce secrets, credentials, PHI, raw finance or account evidence, private runtime values, IP addresses, network maps, device registers, or raw protected exports.
evidence_boundary: Atlas Codex Git objects remain predecessor evidence. The inventory is migration evidence and its preliminary target mappings do not replace semantic reconciliation, source PRs, Spear receipts, Noctua review, or merged-main readback.
supersedes: []
cleanup_path: Retain with the inventory until replaced by a versioned inventory audit against a different Atlas Codex commit.
last_verified: 2026-06-25
---

# Atlas Codex Source Inventory Preflight v1

## Pinned state

- Source repository: `Jktomy/atlas-codex`
- Source branch: `main`
- Exact source commit: `3e4f06ed4abf8fbd44bd04ec1ad8997ffae7eda4`
- Source commit still equals live `main`: **YES**
- Target repository: `Jktomy/atlas-prime`
- Target base for this preview: `e8ed4058b7923857be4a13d73c7658c0d5df1860`
- Prime state: `SHADOW`
- Atlas Codex remains canonical: **YES**

## Inventory identity

- Migration ID: `atlas-codex-to-prime:pr1b-inventory-v2`
- Inventory status: `MAPPING_COMPLETE`
- Tracked-entry count: **349**
- Unique source-path count: **349**
- Normalized/case-only source collisions: **0**
- Inventory file SHA-256: `4d883149cef72e6d94805da73b0deda322ef1350ea848b29edf25cc6931c1856`
- Stored canonical inventory digest: `03fa76c0991e06350cb112d1b33b1dbf00fe6296cabb08199cb92808956dd4fa`
- Recomputed canonical inventory digest: `03fa76c0991e06350cb112d1b33b1dbf00fe6296cabb08199cb92808956dd4fa`
- Digest match: **PASS**

## Schema provenance

- Current schema path: `schemas/migration/atlas-codex-inventory-v1.schema.json`
- Schema Git blob: `5ac6bfa486f43831f96cc62eed9ddf3c51eefa03`
- Schema SHA-256: `dca21c29e3becb08c23e0a97dec55a7c0589dd71f9290a34ed41d3d238c4cc67`
- Prior reproducible PR1B v3 official-schema validation: **PASS**
- Current source commit unchanged since that validation: **YES**
- Current schema identity unchanged since that validation: **YES**
- Local structural and semantic-contract checks: **PASS**

## Preliminary disposition totals

- `GENERATED_REBUILD`: 7
- `HISTORICAL_REFERENCE`: 54
- `MERGE`: 60
- `MIGRATE`: 11
- `OMIT_WITH_REASON`: 66
- `PRIVATE_POINTER`: 3
- `REMODEL`: 145
- `RETIRE`: 1
- `SUPERSEDE`: 2

## Privacy totals

- `POINTER_ONLY`: 1
- `PRIVATE_CLEAN_SUMMARY`: 37
- `PROHIBITED`: 2
- `PUBLIC_CLEAN`: 309

## Content-transfer totals

- `FULL`: 53
- `GENERATED_REBUILD`: 7
- `NONE`: 69
- `PARTIAL`: 217
- `POINTER_ONLY`: 3

## Current record states

- `DEFERRED`: 66
- `MAPPED`: 283

## Collision and semantic-review boundary

- Preliminary destination collision groups: **18**
- Every collision group requires a later Athena reconciliation record.
- No target path in this inventory grants overwrite, merge, retirement, supersession, or source-promotion authority.
- Existing Prime source controls intended target architecture.
- Atlas Codex controls current operational meaning until cutover.
- Any disagreement becomes `NEEDS_JAYSON`.

## Protected boundary

- `PUBLIC_CLEAN`: 309
- `PRIVATE_CLEAN_SUMMARY`: 37
- `POINTER_ONLY`: 1
- `PROHIBITED`: 2
- Private or prohibited entries remain pointer-only or explicitly omitted.
- No raw protected value is reproduced by this audit.

## Interpretation of `MAPPING_COMPLETE`

The inventory's historical status `MAPPING_COMPLETE` means that every source path has a provisional schema-valid disposition and proposed route.

It does **not** mean:

- semantic reconciliation is complete;
- target source is approved;
- a packet is approved;
- writer authority exists;
- migration has begun;
- a predecessor can be deleted or retired;
- Prime is ready for cutover.

Every entry still requires the route and closure process defined by the current migration contract.

## Preflight outcome

```text
Exact predecessor accounting: PASS
Source commit freshness: PASS
Unique path coverage: PASS
Internal digest: PASS
Preliminary classification presence: PASS
Migration execution authority: NO
S1 authority: NO
Writer authority: NO
Promotion/cutover authority: NO
```
