---
title: "Quest Engine and Prime Continuity Contract"
atlas_id: "prime.governance.quest-engine-continuity-contract"
status: "CANONICAL_ACTIVE"
source_type: "PROTOCOL"
authority_class: "CANONICAL_AUTHORED_SOURCE"
owner_project: "Project Codex"
owner_operation: "Operation Source Governance"
protected_level: "CRITICAL"
---

# Quest Engine and Prime continuity contract

## Registry authority

`continuity/mission-board-quest-registry-r01.json` is the canonical admitted
Quest registry. It is a merged, portable recovery snapshot of the live
`mission/quest` parent Issues and contains the exact active Quest identity,
source, owner, state, next gate, readiness basis, parent Issue, parent Mission,
and parent attempt.

Live GitHub Issues are the primary operational work surface. They add discussion,
assignment, dependencies, child Missions, and append-only state history. Issue
state alone cannot advance merged Quest state, grant runtime authority, or
replace Prime. If GitHub Issues are unavailable, the merged registry remains
sufficient to recover Quest identity and unfinished-work routing.

`quest-board/quest-board-v1.json` is frozen predecessor evidence from Mission
#278. Its rows remain immutable history, including completed Quests and the exact
pre-cutover active portfolio. Its legacy top-level `state` identifies the file as
a canonical evidence object; `registry_role: FROZEN_PREDECESSOR_EVIDENCE`
controls its authority. It cannot admit, update, or advance a Quest.

## Quest admission

A later Quest admission requires one atomic reviewed source transaction:

1. create and bind one unique `mission/quest` parent Issue;
2. add one schema-valid Quest source;
3. add one unique row to the Mission Board Quest registry;
4. increment the registry revision exactly once;
5. preserve every existing registry row and the Mission #278 cutover identity;
6. bind continuity if the new Quest is unfinished; and
7. validate, review, merge, and read back the exact candidate.

Validator code does not enumerate future Quest paths or identities. Attempting
admission through the frozen Quest Board fails closed with
`QUEST_BOARD_FROZEN`.

## Stable identity evidence

`continuity/quest-engine-identities-r01.json` fixes the historical Repairing
Prime Quest, Campaign, Mission, and Gate identities plus closed state
transitions. It remains accepted evidence and is not the general admitted-Quest
registry. A merge, generated output, Issue transition, or validation success
cannot self-certify a Campaign or Quest advance.

## Operational continuity

`continuity/prime-continuity-register-r01.json` is canonical operational
unfinished-work detail. It binds:

- the exact active Mission Board Quest registry digest;
- the frozen predecessor Quest Board digest;
- every active Quest source digest;
- one continuity row for every active registry row; and
- an append-only globally unique event ledger.

Its `source_base_sha` records the canonical main used to author the register; it
is evidence provenance, not a claim that later main must remain byte-identical.
Continuity supplements but never silently advances the active Quest registry.

## Bounded update

A continuity update binds the complete register digest, one continuity ID, one
entry revision, and one globally unique event ID retained in the replay ledger.
Only operational position, blockers, next action, next approval, and explicit
Campaign/Mission/Gate routing fields may change. Quest state, parent Issue
identity, registry membership, and registry authority cannot change through
this route.

The input and candidate both validate against the active registry, frozen
predecessor, stable identity register, and exact Quest source bytes. Exactly one
continuity entry, the register revision, and the replay ledger advance. Planning
is read-only; durable apply still requires an exact branch, draft PR, exact-head
review, merge, and canonical readback.

## Emberline, Sunset, Sunrise, and Argus

The deterministic Emberline is a non-authoritative projection of the exact
continuity register digest. The compact continuity `sunset` command seals one
entry and its register digest; it is not the full Atlas Sunset. `sunrise`
accepts the snapshot only when its register digest and entry exactly match the
supplied canonical register. Argus sorts unfinished work from the register
without chat memory and cannot mutate or promote it.

Generated projections report and never govern. Private data, provider state,
runtime placement, deployment, capability promotion, acceptance-journey
promotion, ready, merge, and protected external-action authority are outside
this contract.
