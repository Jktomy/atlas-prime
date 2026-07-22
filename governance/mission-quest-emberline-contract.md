---
title: "Mission Quest Label and Living Emberline Contract"
atlas_id: "prime.governance.mission-quest-emberline"
status: "CANONICAL_ACTIVE"
source_type: "PROTOCOL"
authority_class: "CANONICAL_AUTHORED_SOURCE"
owner_project: "Project Codex"
owner_operation: "Operation Source Governance"
protected_level: "CRITICAL"
routes_from:
  - governance/mission-board-contract.md
  - governance/quest-engine-continuity-contract.md
  - continuity/mission-board-quest-registry-r01.json
  - continuity/prime-continuity-register-r01.json
routes_to:
  - tools/prime_continuity/README.md
  - tools/prime_continuity/engine.py
  - recovery/elantris-recovery.md
private_boundary: "Only public-clean Quest identity, journey summaries, source bindings, blockers, approvals, and protected:// pointers may appear."
---

# Mission Quest Label and Living Emberline Contract

## Purpose

Every admitted active Quest has one live `mission/quest` parent Issue and one
stable human-readable Living Emberline. This contract extends the Mission Board
and continuity contracts without changing their authority model.

## Required label

Every admitted active Quest parent Issue must carry the exact `mission/quest`
label. The label is a visible type index only. It cannot admit a Quest, advance
Quest or Campaign state, grant protected authority, merge source, or replace the
Issue's `atlas.mission.v1` manifest.

The canonical registry row stores `parent_issue_label: mission/quest`. Missing,
different, or duplicated type binding is operational drift and fails validation
or readback. Repairing a label does not itself change canonical Quest state.

## Stable Emberline identity

Every canonical registry row binds one unique stable `emberline_id`. The ID
persists for the life of that admitted Quest. It is not regenerated when the
Quest moves between Campaigns, Missions, Gates, side paths, branches, or final
closeout.

The parent Issue presents a human-readable Emberline generated from exactly one
registry row and exactly one matching continuity entry. The presentation binds:

- Quest, Emberline, and parent Issue identity;
- required `mission/quest` label;
- registry revision and digest;
- continuity register revision and digest;
- current Quest state, Campaign, Mission, and Gate;
- current position and unresolved blockers;
- next safe action and next approval; and
- ordered `Main-*`, `Side-*`, `Branched-*`, and `Final-*` journey entries when
  those paths exist.

## Revision and append-only journey

The normal Emberline revision is the canonical continuity-entry revision. The
first Issue Emberline is appended after Quest admission or reconciliation.
Later revisions are appended as work moves down the Emberline; prior comments
are not rewritten.

A current Main path may contain Emberline, Campaign, Mission, and Gate entries.
A Side entry records bounded related work that returns to the Main path. A
Branched entry preserves the superseded direction and newly accepted direction.
A Final entry is permitted only when the canonical Quest is complete, blockers
are empty, and the next gate is `CLOSED`.

Child-Mission discussion may be summarized as a Side or Branched entry only
when its identity, reason, outcome, and return or supersession relationship are
preserved. Discussion alone cannot move the canonical current position.

## Authority and stale handling

Mission Quest Emberlines are human presentation and restart context. Merged
Mission Board registry and canonical continuity remain authoritative. Labels,
Issue bodies, comments, projections, generated output, and renderer success
cannot self-promote a Quest or Campaign or authorize runtime, infrastructure,
protected data, READY, or MERGE.

If the Issue Emberline conflicts with merged Prime, the Emberline is stale. The
operator must render from the current registry and continuity, append a repaired
revision, and preserve the stale historical comment. Live GitHub availability is
not required for recovery; merged registry and continuity remain sufficient.

## Lifecycle boundary

The older lifecycle proposal for a future sole-authority Quest Emberline cutover
is not activated. Mission #278 established the Mission Board registry as the
admitted-Quest authority. Lifecycle Emberline records may preserve journey
evidence, but they do not supersede the Mission Board registry or continuity.
Any future authority transfer requires a separate explicit atomic cutover,
validation, review, Jayson permanence, and exact merged-main readback.

## Deterministic renderer

`python -B -m tools.prime_continuity.cli mission-quest-emberline --quest-id QUEST_ID`
renders one digest-bound JSON object containing readable Markdown. The renderer
must reject missing registry or continuity coverage, duplicate Emberline IDs,
invalid labels, and unknown Quest identities. It writes nothing unless an
external output path is explicitly supplied and never mutates GitHub.
