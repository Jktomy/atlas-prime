---
title: "Atlas Lifecycle Construction Contract"
atlas_id: "prime.lifecycle.construction-contract"
status: "CANONICAL_ACTIVE"
source_type: "PROTOCOL"
authority_class: "CANONICAL_AUTHORED_SOURCE"
owner_project: "Atlas"
owner_operation: "Source Governance"
protected_level: "CRITICAL"
---

# Atlas Lifecycle Construction Contract

## Shared profile

G4-D uses one closed `atlas.lifecycle.construction-profile` envelope with the
profiles `LIFECYCLE_CHECKPOINT_V1` and `LIFECYCLE_TRANSITION_V1`. The profile
binds the permanent event ID and immutable repository path, event schema and
class, Athena semantic author, exact target entity identity, expected main and entity/Quest/Gate revisions,
parent and correction lineage, candidate event/manifest/receipt/set digests,
external trust-root and state-snapshot digests, replay key, protected-data
classification, rollback and reversal contracts, exact allowed path, approved
route, and draft-PR stop boundary.

The profile is deterministic construction metadata. It cannot decide whether
meaning, completion, privacy, acceptance, blocker resolution, Quest admission,
capability restoration, Golden Wing promotion, or doctrine promotion is valid.

## Thread Engine profile

Canonical lifecycle source is protected. A lifecycle construction mission uses
the existing mission-scoped Aegis Break protected route, exactly one `ADD`
operation, exactly one route-declared path below `lifecycle/events/`, and the
three-file G4-C candidate set under `payload/lifecycle-candidate/`. Thread Engine
verifies the event, manifest, receipt, independent expectations, candidate set,
mission base, revision locks, replay state, path set, and byte hashes before it
may construct one branch, one commit, and one draft pull request.

The stop boundary is `DRAFT_PR_READBACK`. Direct-main write, force push,
automatic ready, automatic merge, workflow dispatch, cleanup, standing
authority, generated-source mutation, and Thread Engine self-change remain
forbidden.

## Foundry compatibility decision

The generic Foundry operation inventory can carry the exact event payload, but
its closed carrier contract cannot preserve and bind the G4-C manifest and
candidate receipt. G4-D therefore requires a separate narrow lifecycle carrier
binding. That adapter may package and verify exact construction bytes and
digests only; it does not evaluate semantic completion or gain GitHub authority.

The Thread Engine profile lands first. The Foundry binding follows as a separate
authored transaction so neither review surface can mask the other.
