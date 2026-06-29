---
title: Spear/Bow Gates 1-2 Execution Convergence Record
atlas_id: atlas-prime.migration.spear-bow-convergence.2026-06-29
format_version: "1.0"
status: ACTIVE
source_type: MIGRATION_RECORD
authority_class: MIGRATION_EVIDENCE
owner_project: Codex
owner_operation: Atlas Prime Rebuild Program
canonical_scope: Records the CLI-primary Gates 1-8 decision, Gates 1-2 convergence transaction scope, exact pre-transaction heads, authority boundaries, deferred Workboard reconciliation, and restart-safe next gates.
protected_level: HIGH
routes_from:
  - specs/spear/spear-execution-convergence-v1.md
  - migration/atlas-codex/atlas-prime-rebuild-program-roadmap-v1.md
routes_to:
  - quest-board/quest-board-shadow-v1.json
  - tools/spear/operator-runbook.md
  - tools/spear/recovery-runbook.md
private_boundary: This record contains clean program continuity only and must not include credentials, PHI, raw finance or account evidence, private runtime values, network maps, device registers, or protected exports.
evidence_boundary: Arrow manifests, receipts, commits, PRs, Noctua reports, and main readback remain primary execution evidence.
supersedes: []
cleanup_path: Retain through Gates 1-2 closure and later absorb stable semantics into the roadmap and runbooks through reviewed transactions.
last_verified: 2026-06-29
---

# Spear/Bow Gates 1-2 Execution Convergence Record

## Controlling decision

Bow and Arrow CLI is the primary repository-mutation route for Atlas Prime Rebuild Gates 1-8.

The long-term hierarchy remains:

```text
Athena prepares and attempts supported remote operation
-> Artemis Local Operator performs approved local execution when available
-> Jayson is the final manual fallback
```

Jayson remains the ultimate authority and operates the Bow until Artemis is proven and activated.

## Exact pre-transaction state

```text
Codex main: 091c7e88f6403e93a9016670cb5a872b4c8d0c7d
Prime main: 0d2249b864a90804605b7bfa47ac189e51d3e431
Codex authority: CANONICAL
Prime state: SHADOW
```

## Gates 1-2 Build transaction

The Build Arrow updates the existing Codex convergence PR branch, creates a Prime convergence branch and draft PR, writes exact candidate files, verifies allowed paths, emits receipts, and stops before merge.

The canonical Codex Workboard update is intentionally deferred until exact convergence PR heads exist, preventing prospective or self-referential transaction facts from being embedded in stable source.

## Current non-authority

This record does not activate S1, grant Artemis execution authority, authorize merge, migrate content, promote Prime, retire Codex, delete evidence, modify Google Drive, or perform cutover.

## Next gates

```text
Build Arrow receipts
-> exact-head Noctua
-> Jayson merge consent
-> separate Execute Arrow
-> Codex merge and readback
-> Prime merge and readback
-> canonical Workboard reconciliation
-> Gate 3 transaction-contract work
```
