---
title: "Atlas Lifecycle Source"
atlas_id: "prime.lifecycle.readme"
status: "CANONICAL_ACTIVE"
source_type: "REGISTER"
authority_class: "CANONICAL_AUTHORED_SOURCE"
owner_project: "Atlas"
owner_operation: "Source Governance"
protected_level: "HIGH"
---

# Atlas Lifecycle Source

This tree contains structured lifecycle source for Feathers, Feather Archives,
Golden Wings, Quest Emberlines, Quest checkpoints, Sunset, Sunrise, continuity,
and lifecycle receipts.

Authority is deliberately narrow:

- after the lifecycle authority cutover is proven, `quest-emberlines/` is the
  sole authority for current admitted-Quest state; the existing Quest Board
  retains its current role until that atomic cutover.
- Feathers and Quest checkpoints are immutable evidence of a position; they do
  not advance or replace Quest state.
- archive and supersession records change lifecycle interpretation without
  deleting an identity or breaking a reference.
- Golden Wings are reusable-lesson candidates, never doctrine.
- `fixtures/` is harmless test material and has no Atlas authority.
- `generated/lifecycle/` is a deterministic, noncanonical projection.

All canonical records are strict UTF-8 JSON. They must validate against the
declared schema, use canonical serialization, pass the protected-source
boundary, and carry exact source and concurrency locks defined by
`lifecycle-contract.md`.

The lifecycle engine remains `SCRIPT ASSIST — LEVEL 1`. Presence of source or
code does not activate a capability level.
