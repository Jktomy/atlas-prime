---
title: "Atlas Lifecycle Contract"
atlas_id: "prime.lifecycle.contract"
status: "CANONICAL_ACTIVE"
source_type: "PROTOCOL"
authority_class: "CANONICAL_AUTHORED_SOURCE"
owner_project: "Atlas"
owner_operation: "Source Governance"
protected_level: "CRITICAL"
---

# Atlas Lifecycle Contract

## Storage

| Entity | Canonical source directory | Prefix | Immutability |
|---|---|---|---|
| Feather | `lifecycle/feathers/` | `FTR` | sealed records immutable |
| Feather Archive | `lifecycle/feather-archives/` | `FAR` | immutable event |
| Golden Wing | `lifecycle/golden-wings/` | `GWN` | revision or supersession |
| Quest Emberline | `lifecycle/quest-emberlines/` | `QEM` | revisioned current state |
| Quest checkpoint | `lifecycle/quest-checkpoints/` | `QCP` | immutable checkpoint |
| Sunset | `lifecycle/sunsets/` | `SUN` | immutable plan/checkpoint |
| Sunrise | `lifecycle/sunrises/` | `SRI` | immutable reconstruction |
| Continuity | `lifecycle/continuity/` | `CON` | immutable recovery record |
| Lifecycle receipt | `lifecycle/receipts/` | `LCR` | immutable independent binding |
| Lifecycle event | `lifecycle/events/` | `LEV` | append-only or explicit correction event |

Only schema-valid `.json` files belong in canonical record directories.
Except for lifecycle events, filenames are the case-sensitive `record_id` plus
`.json`. A lifecycle event is the sole filename exception: its authorized route
must declare one exact immutable repository-relative `.json` path beneath
`lifecycle/events/` before candidate generation. The event's full canonical
payload, including that declared path, remains in `record_id` derivation; only
`record_id` itself is omitted. The path is storage location, never identity,
and cannot be reused for another event. Readers, projections, relationships,
lineage, replay protection, and supersession continue to use `record_id`.
Candidate manifests and lifecycle receipts must independently bind both the
permanent event ID and exact path. No other lifecycle record type receives this
exception. Test fixtures live only under `lifecycle/fixtures/` and declare
`authority: NONCANONICAL_FIXTURE`.

## Lifecycle rules

Feather states are `DRAFT`, `SEALED`, `ARCHIVED`, `SUPERSEDED`, and
`INVALIDATED`. A sealed Feather is never edited. Archival and supersession are
new records that preserve stable readback and lineage.

Golden Wing states are `CANDIDATE`, `GATHERING_EVIDENCE`,
`READY_FOR_PHOENIX_BURN`, `ABSORBED`, `REJECTED`, `SUPERSEDED`, and
`HISTORICAL`. Advancement requires recurrence across independent contexts or
one explicitly justified systemic exception. The engine never creates or
promotes a Golden Wing automatically.

Lifecycle events use the one-envelope contract in
`lifecycle-event-contract.md`. `CHECKPOINT` events preserve an in-progress
position. `TRANSITION` events describe an Athena-authored requested state
change and require independently trusted acceptance evidence. An ordinary
merge or generated projection cannot create an authoritative transition.

Quest Emberlines use monotonically increasing integer revisions. A mutation
must bind the current record ID, revision, and canonical `main` SHA. Candidate
Quests use `candidate_quest_ref`; they do not receive a canonical `quest_id`.
Non-Quest work leaves both fields absent.

Every completed Sunset is one atomic continuity transaction that creates
exactly one new sealed Feather and exactly one immutable Sunset bound to that
Feather. This rule applies to admitted-Quest, candidate-Quest, non-Quest, and
protected-domain work; non-Quest work never receives an invented Quest identity.
The Feather retains the rich authored restart meaning, while the Sunset retains
the closeout assessment, unresolved items, next safe action, next approval gate,
source locks, and protected pointers.

Sunrise resolves one exact Sunset/Feather pair. It must name the same Feather
recorded by the Sunset and reconstruct only the bounded compact context. A
missing, null, dangling, reused, cross-scope, or mismatched Feather binding fails
closed.

## Plan, route, apply, verify

All operations follow `Plan → Route → Apply → Verify`.

- Plan is read-only and declares expected state and output.
- Route checks the approved Prime change route and protected boundary.
- Apply writes only temporary output unless Level 1C is separately active.
- Verify rereads every output, checks canonical bytes and identity, binds an
  independent receipt, and reports exact stale or mismatch diagnostics.

Canonical source is never silently mutated. Level 1C may write only to an
authorized branch, only within exact allowed paths, and may open only a draft
PR. It never marks ready or merges.

## Protected source

Lifecycle source rejects secrets, credentials, private keys, seed phrases,
real environment values, IP addresses or network topology, private runtime
registers, raw financial evidence, account records, PHI, medical records,
unrestricted private paths, and raw private exports. A protected source is
represented only by a sanitized summary, classification, and bounded
`protected://` pointer.

## Projections

`generated/lifecycle/` may contain deterministic website-facing indexes. Each
projection declares noncanonical authority, schema and generator versions,
source fingerprint, and generated timestamp. The timestamp is derived from the
locked lifecycle Git tree revision, never the generator's wall clock, so
repeated builds are byte-identical even in a shallow checkout. Consumers use
stable IDs and relationships, never physical source paths as identity. Stale
fingerprints are an error. The initial website contract is read-only.

Website index v2 carries compact restart and relationship fields while
preserving stable IDs as identity. During Level 1A, `index build` computes and
validates this projection only in memory and reports `CURRENT`, `STALE`,
`MISSING`, or `INVALID`; it never publishes or rewrites generated source.

## Acceptance

G3 and G4 cannot be GREEN until fixtures prove admitted-Quest, candidate-Quest,
non-Quest, and protected-domain Sunset with exactly one newly sealed Feather;
one-to-one Sunset/Feather binding; stale concurrency; archival readback;
supersession; exact-pair Sunrise reconstruction; rejection of null, missing,
dangling, reused, cross-scope, and mismatched Feather references; supported and
unsupported multi-Quest Golden Wings; deterministic indexes; stale-index,
duplicate, replay, and malformed-schema rejection; Linux/Windows parity; and
clean-context reconstruction.

The BEU pilot compares comparable manual and script-assisted operations. It
records files and bytes read, steps, retries, elapsed agent work, interventions,
reconstruction accuracy, errors, and protected-boundary failures. BEU or model
usage is reported only when a trusted measurement exists; otherwise it is
`NOT_MEASURED`.
