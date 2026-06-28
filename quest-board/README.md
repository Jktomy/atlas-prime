---
title: Quest Board
atlas_id: atlas-prime.quest-board
format_version: "1.0"
status: PROPOSED
source_type: OPERATIONAL_REGISTER
authority_class: STRUCTURED_STATE
owner_project: Codex
owner_operation: Source Governance
canonical_scope: SHADOW successor register for the Atlas Codex Active Workboard.
protected_level: CRITICAL
routes_from:
  - specs/atlas-prime/quest-board-emberline-v1.md
  - migration/atlas-codex/workboard-to-quest-board-crosswalk-v1.md
routes_to:
  - schemas/quest-board-v1.schema.json
  - quest-board/quest-board-shadow-v1.json
private_boundary: Clean continuity state only.
evidence_boundary: Codex Workboard remains canonical until cutover.
supersedes: []
cleanup_path: Promote to canonical only through verified cutover; otherwise remain SHADOW migration evidence.
last_verified: 2026-06-28
---

# Quest Board

Prime Quest Board is the evolved successor name for the Codex Active Workboard.

Current authority: `SHADOW`.

It must not be used as current operational truth before verified cutover.
