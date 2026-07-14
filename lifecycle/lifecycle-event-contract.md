---
title: "Atlas Shared Lifecycle Event Contract"
atlas_id: "prime.lifecycle.event-contract"
status: "CANONICAL_ACTIVE"
source_type: "PROTOCOL"
authority_class: "CANONICAL_AUTHORED_SOURCE"
owner_project: "Atlas"
owner_operation: "Source Governance"
protected_level: "CRITICAL"
---

# Atlas Shared Lifecycle Event Contract

## One envelope

This one-envelope contract prevents competing lifecycle event systems.
Every lifecycle event validates against
`lifecycle/schemas/lifecycle-event-v1.schema.json`, uses schema identity
`atlas.lifecycle.event`, and receives a content-addressed `LEV` record ID.
Canonical events will live under `lifecycle/events/` only after the applicable
apply level and authority cutover are separately accepted. G4-A contains
harmless `NONCANONICAL_FIXTURE` events only.

Lifecycle events are the sole exception to the general `<record_id>.json`
canonical filename rule. Before candidate generation, the authorized route
declares exactly one immutable repository-relative path beneath
`lifecycle/events/` ending in `.json`. It must pass normalization, traversal,
absolute-path, collision, case-fold, and protected-boundary checks. That exact
path is part of the content-addressed payload and cannot be reused by a
different event. Candidate manifests and receipts bind the exact path together
with the permanent `record_id`. All readers, projections, relationships,
lineage, replay protection, and supersession resolve identity by `record_id`,
never by physical path. No other record type inherits this exception.

The envelope carries target, Project and optional Operation, lifecycle
position, exact state expectations, evidence, protected-data classification,
semantic author, route authority, allowed paths, related records, replay key,
and explicit lineage. The inactive class payload is always `null`.

## Checkpoints

Checkpoint types are `GATE_PROGRESS_RECORDED`, `WORK_CHECKPOINT_ACCEPTED`,
`WORK_PAUSED`, `WORK_RESUMED`, `EVIDENCE_ADDED`, `DECISION_RECORDED`,
`BLOCKER_DISCOVERED`, and `APPROACH_SUPERSEDED`.

A checkpoint requires an admitted Quest, Campaign, Mission, and Gate. It keeps
the Gate `IN_PROGRESS`, preserves nonterminal Mission, Campaign, and Quest
state, creates no completion receipt, requests no position advance, and cannot
resolve a blocker. Completed and remaining substeps are concrete lists; minor
observations are consolidated rather than emitted as event or PR spam.

For every completed Sunset, the construction relationship is:

`Sunset invocation → one new sealed Feather → one Sunset bound to that Feather`

For an admitted Quest inside an incomplete Gate, the transaction continues:

`bound Sunset/Feather pair → CHECKPOINT event → generated projections`

Candidate-Quest, non-Quest, and protected-domain Sunset transactions still
create the exact Feather/Sunset pair but do not fabricate an admitted Quest,
Campaign, Mission, Gate, or checkpoint event. The Feather retains rich authored
meaning. A Quest checkpoint event retains exact restart position and locks.
Stable IDs link them without duplicating their full contents. Neither replaces
the Quest Emberline.

## Transitions

Transition types are `LANDMARK_COMPLETED`, `GATE_COMPLETED`,
`MISSION_COMPLETED`, `CAMPAIGN_COMPLETED`, `QUEST_COMPLETED`, `QUEST_REOPENED`,
`BLOCKER_RESOLVED`, `BLOCKER_REOPENED`, `QUEST_ADMITTED`, `FEATHER_SEALED`,
`FEATHER_ARCHIVED`, `FEATHER_SUPERSEDED`, `GOLDEN_WING_EVIDENCE_ADDED`,
`ACCEPTANCE_PROVEN`, `ACCEPTANCE_REVOKED`, `COMPLETION_REVOKED`, `CAPABILITY_RESTORED`,
`CAPABILITY_REVOKED`, `SUNSET_CHECKPOINT_ACCEPTED`,
`SUNRISE_CONTEXT_VERIFIED`, and `TRANSITION_SUPERSEDED`.

Every transition requires a nonempty acceptance checklist, Athena-authored
semantic acceptance, exact accepted evidence, and a trusted acceptance receipt
reference. `ordinary_merge_event` and `generated_output_trigger` are fixed to
`false`; an ordinary merge or generated projection cannot advance lifecycle
state.

## State-machine rules

| Event family | Required prior state | Permitted result | Additional rule |
|---|---|---|---|
| Checkpoint | current Gate `IN_PROGRESS` | same lifecycle position | no completion, blocker resolution, or advance |
| Gate completion | declared Gate `IN_PROGRESS` | Gate `COMPLETE`; predetermined next Gate only | every declared criterion current and accepted |
| Mission completion | every declared Gate complete | Mission `COMPLETE` | no nonexistent or inferred next Mission |
| Campaign completion | every declared Mission complete | Campaign `COMPLETE` | no inferred Quest completion |
| Quest completion | declared outcome accepted | Quest `COMPLETE` | Athena-authored acceptance required |
| Blocker resolution | blocker `OPEN` | blocker `RESOLVED` | blocker ID must be explicitly authorized |
| Seal/archive/supersede | permitted Feather state | declared next Feather state | sealed content remains immutable |
| Acceptance/capability proof | prior status and acceptance contract match | declared accepted/restored state | exact evidence and external trust required |
| Reopen/revoke/reverse | explicit earlier event exists | declared prior status restored | lineage remains append-only |
| Quest admission | candidate has approved admission contract | admitted Quest identity | never inferred from candidate activity |

The G4-B planner must reject missing targets or declared next positions, stale
main/entity/Quest/Gate state, stale parent checkpoints, mismatched prior state,
duplicate or replayed events, concurrent advancement, unauthorized blocker
resolution, missing acceptance evidence, self-supplied trust expectations,
changed exact SHA, generated triggers, protected material, malformed or unknown
fields, and unsupported schema versions.

## Lineage and correction

`parent_event_id` links the accepted lineage. `supersedes_event_id`,
`invalidates_event_id`, `reverses_event_id`, `revokes_event_id`, and
`reopens_event_id` make corrections explicit. A later planner must require the
lineage field appropriate to each corrective event type and reject ambiguous or
multiple correction meanings.

## Trust and protected source

The event's trusted expectation and acceptance receipt references point outside
the submitted payload. A payload, archive, receipt, sidecar, and claimed digest
cannot collectively replace their trusted expectations. Verification retains
bounded bytes, members, paths, parsing depth, schema identity, independent
sidecar/receipt binding, sanitized failure evidence, and preserved diagnostics.
The read-only planner additionally requires the repository-controlled event
trust root to match an independently supplied digest from the controlling
handoff and the current-state snapshot to match its independent digest; the
submitted event cannot select or replace either digest.

## Level 1B candidate generation

G4-C may serialize an Athena-authored, fully validated event into a new system
temporary directory only. The deterministic candidate set contains the exact
event bytes, one closed allowed-path manifest, and one closed candidate
receipt. Manifest and receipt each bind the permanent event `record_id`, the
exact immutable repository path, expected canonical base, expected entity
revision, trusted event-schema digest, acceptance-contract digest, external
trust-root digest, and current-state snapshot digest. Existing output, an
occupied or case-fold-colliding event path, and any repository output fail
closed. Repeat generation into separate fresh temporary directories must be
byte-identical.

This candidate set is not canonical evidence and grants no branch, repository,
GitHub, Quest advancement, Thread Engine, Foundry, ready, merge, or direct-main
authority. Level 1C remains inactive during G4-C.

GitHub receives only clean summaries and `protected://` pointers. Structural
validation is defense in depth; Athena remains responsible for semantic privacy
interpretation.
