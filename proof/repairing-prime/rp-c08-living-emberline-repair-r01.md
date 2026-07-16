---
title: "RP-C08 Living Emberline Architecture Repair R01"
status: "CANDIDATE_SOURCE_REPAIR"
source_type: "PROOF"
authority_class: "CANONICAL_AUTHORED_SOURCE"
owner_project: "Codex"
owner_operation: "Repairing Prime"
protected_level: "CRITICAL"
---

# RP-C08 Living Emberline Architecture Repair R01

Exact base: `4e297f7cb1206f16230d282c9da9ecbb986c1a8a`

This candidate repairs the lifecycle conflict discovered by restart-safe Sunset
R01 without deleting the original Repairing Prime Emberline or breaking its
immutable checkpoint reference.

## Accepted design

- one living Emberline file and stable identity per admitted Quest;
- `Main-*` entries for the active route;
- `Side-Campaign-*`, `Side-Mission-*`, and `Side-Gate-*` entries for bounded
  departures that return;
- `Branched-*` entries for intentional changes in direction;
- `Final-*` entries for accepted completion;
- every revision binds the SHA-256 digest of the previous canonical file;
- Feathers, checkpoints, Sunsets, Sunrises, receipts, and events remain
  immutable.

The current Repairing Prime Emberline is migrated in place at
`lifecycle/quest-emberlines/QEM-R6QKBDHLY7I7PVVEKIGTZFMZZT.json` and retains ID `QEM-R6QKBDHLY7I7PVVEKIGTZFMZZT`.

## Boundaries

PR #221 remains preserved as DEFLECTED evidence. RP-C08 and Repairing Prime
remain `IN_PROGRESS`. This transaction creates no Sunset, performs no Quest
completion, changes no generated file, and grants no READY or merge authority.
