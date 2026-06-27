---
title: Atlas Active Workboard Authority Alignment v1
atlas_id: atlas-prime.migration.atlas-codex.active-workboard-authority-alignment-v1
format_version: "1.0"
status: ACTIVE
source_type: MIGRATION_RECORD
authority_class: MIGRATION_EVIDENCE
owner_project: Codex
owner_operation: Source Governance
canonical_scope: Records the post-M0 decision that the GitHub Atlas Codex Workboard is the sole canonical operational register while the Drive revision remains historical M0 evidence only.
protected_level: CRITICAL
routes_from:
  - migration/atlas-codex/audits/atlas-codex-delta-0001-final-closeout-v1.md
  - migration/atlas-codex/README.md
  - migration/atlas-codex/migration-map.md
routes_to:
  - migration/atlas-codex/README.md
  - migration/atlas-codex/migration-map.md
  - templates/codex-to-prime-reconciliation-record.md
private_boundary: This record contains clean repository paths, commit identities, Drive revision identity, SHA-256, and authority statements only. It must not contain protected operational values or raw private evidence.
evidence_boundary: The Drive revision remains historical M0 execution evidence. Current operational Workboard truth is read only from the GitHub Codex path after merged-main readback.
supersedes: []
cleanup_path: Retain as additive correction evidence. Do not rewrite the immutable M0 final-closeout record.
last_verified: 2026-06-27
---

# Atlas Active Workboard Authority Alignment v1

## Decision

Jayson selected the following authority model before M1:

```text
Sole canonical Active Workboard:
Jktomy/atlas-codex/codex/atlas-active-workboard.md on main

Google Drive and other external copies:
NONCANONICAL
UNSYNCHRONIZED
MAY REMAIN STALE
NOT A FALLBACK OPERATIONAL SOURCE
```

A document stored outside GitHub because a GitHub route failed is temporary holding evidence only. It must be re-reviewed and merged into the canonical GitHub source before it affects Atlas operational truth.

## M0 evidence preservation

M0-D used and read back this Drive revision:

- file ID: `19sDQ4l7HcS4J1mE-lJ0lJ3RSHQXRgHJM`
- revision: `0Bz1aLTIXmYtUaXhFUGhCT2gvNzhLaTdKSURnZVNqNGVzQVhjPQ`
- SHA-256: `8f735bcadf7b7f770332ad0586fdde6d1768ce46285c8279f682d2535d9aa477`
- bytes: `28935`

That evidence remains valid for the exact M0 structured-register gate. This alignment does not invalidate PR #18, reopen ordered delta `0001`, or change its `CLOSED` digest.

## Current repository state

- Atlas Codex main at decision time: `cdc4ae62eaff1c0d4a53e9f6b12873213b9f2f9f`
- Atlas Prime M0 closeout main: `8993d0bffce3bb64b6659ca60fe029d2818f050c`
- Prime state: `SHADOW`
- Codex canonical: `YES`
- M0-D: `CLOSED`
- M1 content movement: `NOT AUTHORIZED`

## Future operating rule

Sunrise, Argus, Sunset, Aegis, migration planning, and future Athena must use the GitHub Workboard.

No synchronization obligation exists for the Drive copy.

The future Prime hierarchy remains:

`Questboard -> Quests -> Campaigns`

The C13 Workboard-to-Quest transition remains unexecuted and requires its own versioned contract and exact Preview -> Execute gate.

## M1 gate

The pre-alignment M1-A evidence package is stale once these source changes merge.

After Codex and Prime alignment PRs merge and are read back:

1. resolve the new exact Codex and Prime `main` heads;
2. regenerate the M1-A read-only evidence preflight;
3. audit all 18 collision groups and the high-consequence queue;
4. preserve no content-movement, S1, disposition-ledger, Questboard, promotion, retirement, deletion, or cutover authority.
