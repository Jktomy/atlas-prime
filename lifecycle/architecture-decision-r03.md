---
title: "Lifecycle Architecture Decision R03"
atlas_id: "prime.lifecycle.architecture.r03"
status: "CANONICAL_ACTIVE"
source_type: "ARCHITECTURE_DECISION"
authority_class: "CANONICAL_AUTHORED_SOURCE"
owner_project: "Atlas"
owner_operation: "Source Governance"
protected_level: "CRITICAL"
supersedes: "prime.lifecycle.architecture.r02"
---

# Lifecycle Architecture Decision R03

## Decision

Each admitted Quest has exactly one living Quest Emberline file and one stable
Emberline identity. The file is revisioned current state and contains the
readable journey that led to that state. Git preserves prior file revisions;
the current file preserves the complete bounded story needed for restart.

The journey vocabulary is:

- `Main-*` for the accepted active route;
- `Side-Campaign-*`, `Side-Mission-*`, or `Side-Gate-*` for temporary
  departures that explicitly return to the route;
- `Branched-Emberline-*`, `Branched-Campaign-*`,
  `Branched-Mission-*`, or `Branched-Gate-*` for an intentional change
  in direction;
- `Final-*` for accepted completion of the named scope.

A Side entry records where it departed, why, its outcome, and where it
returned. A Branched entry records the superseded direction and the newly
accepted direction. A completed Quest ends with a Final entry, an empty
blocker set, `quest_state: COMPLETE`, and `next_gate: CLOSED`.

## Identity and revision integrity

The living Emberline keeps its original `record_id` and repository path.
Every revision increments `quest_revision` and binds the SHA-256 digest of the
previous canonical file through `revision_parent_digest`. The stable identity
is not recomputed from mutable journey text. All other lifecycle records
retain content-addressed identity.

Feathers, Quest checkpoints, Sunsets, Sunrises, receipts, and lifecycle events
remain immutable. Their references to the stable Emberline ID therefore remain
valid across the Quest journey.

## Sunset behavior

For an admitted Quest, Sunset candidate generation replaces the exact living
Emberline payload at its existing path, appends one `Main-Gate-*` journey
entry, and emits one new immutable Feather, checkpoint, Sunset, and Sunrise.
The candidate does not create a second Emberline identity.

## Authority

Athena authors journey meaning. The lifecycle engine validates shape,
revision, prior-file binding, branch/return relationships, exact source locks,
and completion invariants. Oathbringer may publish only separately approved
exact bytes to a draft PR. No automatic READY, merge, or Quest completion is
authorized.
