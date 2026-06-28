---
title: Workboard to Quest Board Crosswalk v1
atlas_id: atlas-prime.migration.workboard-quest-board-crosswalk.v1
format_version: "1.0"
status: PROPOSED
source_type: MIGRATION_RECORD
authority_class: MIGRATION_EVIDENCE
owner_project: Codex
owner_operation: Source Governance
canonical_scope: Defines the non-mutating field and authority crosswalk from the canonical Codex Active Workboard to the SHADOW Prime Quest Board.
protected_level: CRITICAL
routes_from:
  - migration/atlas-codex/README.md
  - migration/atlas-codex/migration-map.md
routes_to:
  - specs/atlas-prime/quest-board-emberline-v1.md
  - quest-board/README.md
private_boundary: Clean continuity state only.
evidence_boundary: Codex Workboard remains canonical.
supersedes: []
cleanup_path: Retain as migration evidence after cutover.
last_verified: 2026-06-28
---

# Workboard to Quest Board Crosswalk v1

Canonical predecessor evidence: `Jktomy/atlas-codex:codex/atlas-active-workboard.md` at the pinned Codex base.

| Codex Workboard | Prime Quest Board |
|---|---|
| Project | Quest owner Project |
| Operation | Quest owner Operation |
| Work Item | Quest, Campaign, gate, or work item after semantic classification |
| Status | Quest/Campaign status |
| Last Known State | Emberline current state |
| Why Unfinished | Remaining work |
| Blocker | Blockers |
| Waiting on Jayson / Athena / Tool | Dependencies and next approval gate |
| Next Physical / Athena Action | Next safe action |
| Source Confidence | Emberline confidence |
| Safety Boundary | Protected-boundary posture |
| Jump-Off Command | Restart command |
| Sunset Source | Emberline/Sunset lineage |

No row is migrated automatically. Each row requires semantic classification and exactly one parent Quest.
