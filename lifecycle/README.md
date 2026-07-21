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
lifecycle receipts, and the shared checkpoint/transition event envelope.
`lifecycle-construction-contract.md` defines the closed Thread Engine and
Foundry construction binding without changing semantic authority.

Authority is deliberately narrow:

- after the lifecycle authority cutover is proven, `quest-emberlines/` is the
  sole authority for current admitted-Quest state; each admitted Quest has one
  stable living Emberline file containing Main, Side, Branched, and Final
  journey entries. The existing Quest Board retains its current role until
  that atomic cutover.
- Feathers and Quest checkpoints are immutable evidence of a position; they do
  not advance or replace Quest state.
- a living Emberline revision keeps its stable identity, increments its revision,
  binds the prior file digest, and preserves its complete readable journey;
- archive and supersession records change other lifecycle interpretation
  without deleting an identity or breaking a reference.
- Golden Wings are reusable-lesson candidates, never doctrine.
- a full Atlas Sunset begins with a user-visible Preview, then exact approval,
  then one route-neutral carrier, then the lifecycle closeout that creates one
  exact Feather/Sunset/Sunrise binding; the compact `prime_continuity` snapshot
  is a distinct read-only view and cannot claim closeout.
- the approved carrier is temporary execution evidence, never canonical
  lifecycle source or a substitute for merged readback.
- `fixtures/` is harmless test material and has no Atlas authority.
- `generated/lifecycle/` is a deterministic, noncanonical projection.

All canonical records are strict UTF-8 JSON. They must validate against the
declared schema, use canonical serialization, pass the protected-source
boundary, and carry exact source and concurrency locks defined by
`lifecycle-contract.md`.

The lifecycle engine remains `SCRIPT ASSIST — LEVEL 1`. Presence of source or
code does not activate a capability level. Only canonical merged-main readback
may claim `SUNSET COMPLETE`.
