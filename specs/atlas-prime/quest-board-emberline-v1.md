---
title: Atlas Prime Quest Board and Emberline Specification v1
atlas_id: atlas-prime.quest-board-emberline.v1
format_version: "1.0"
status: PROPOSED
source_type: SPECIFICATION
authority_class: TOOL_CONTRACT
owner_project: Codex
owner_operation: Source Governance
canonical_scope: Defines the Prime Quest Board successor model, Quest parent / Campaign child hierarchy, unified Emberline status model, SHADOW authority, and cutover requirements.
protected_level: CRITICAL
routes_from:
  - atlas-prime.md
  - migration/atlas-codex/workboard-to-quest-board-crosswalk-v1.md
routes_to:
  - schemas/quest-board-v1.schema.json
  - templates/quest-emberline-template.md
  - quest-board/README.md
private_boundary: Clean continuity state only; no raw protected evidence.
evidence_boundary: Codex Workboard remains canonical until verified cutover.
supersedes: []
cleanup_path: Keep as the v1 Quest Board contract; version future incompatible changes.
last_verified: 2026-06-28
---

# Quest Board and Emberline Specification v1

## Authority

Prime Quest Board is SHADOW while Codex is canonical.

## Hierarchy

- Quest is the parent.
- Campaign is the child/subquest.
- Every Campaign has exactly one parent Quest.
- Campaigns do not contain Campaigns.
- A Quest may have zero Campaigns.
- Every substantial Quest has one canonical Emberline.

## Board identity

The Codex Active Workboard and Prime Quest Board are the same system across repository generations.

## Emberline

Emberline is the complete Quest roadmap and current-state view. Campaign detail rolls upward into the Quest Emberline.

## Cutover

Authority changes only after crosswalk, schema validation, state reconciliation, restart proof, rollback proof, Noctua, and explicit Jayson approval.
