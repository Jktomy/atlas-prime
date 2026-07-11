---
title: "Lifecycle Architecture Decision R02"
atlas_id: "prime.lifecycle.architecture.r02"
status: "CANONICAL_ACTIVE"
source_type: "ARCHITECTURE_DECISION"
authority_class: "CANONICAL_AUTHORED_SOURCE"
owner_project: "Atlas"
owner_operation: "Source Governance"
protected_level: "CRITICAL"
supersedes: "prime.lifecycle.architecture.r01"
---

# Lifecycle Architecture Decision R02

## Decision

Atlas uses one shared, append-only lifecycle-event envelope for durable
checkpoint history and authoritative transition candidates. The two event
classes are `CHECKPOINT` and `TRANSITION`; they are closed shapes within one
trusted schema, not separate authorities or independent event systems.

Quest Emberlines remain the sole future current-state authority for admitted
Quests after an atomic cutover is proven. The current Quest Board retains its
canonical role until that cutover. Events, Feathers, receipts, and generated
projections supply history, evidence, restart context, or proposed deltas; none
can independently advance current Quest state.

## Responsibility chain

Athena authors meaning and acceptance. The lifecycle engine validates exact
state mechanics and prepares deterministic candidates. Thread Engine may later
construct an exact branch-scoped draft-PR transaction from accepted bytes.
Foundry may compile a deterministic carrier without interpreting lifecycle
meaning. Oathbringer performs only separately authorized mechanics. GitHub
preserves exact evidence and readback. Generated projections report the merged
source state and never govern it.

## Receipt-driven transition rule

A merged pull request, generated output, successful schema validation, or
self-consistent submitted bundle is never sufficient evidence of a lifecycle
transition. Every transition must bind an independently controlled trust source
for the expected canonical main SHA, entity revision, trusted schema identity,
acceptance contract, exact accepted evidence SHA, and allowed route authority.

Checkpoint events preserve the active Quest, Campaign, Mission, and Gate. They
keep the Gate `IN_PROGRESS`, create no completion receipt, resolve no blocker,
and request no position advance. Transition events require Athena-authored
acceptance and a trusted receipt reference before a state delta can be planned.

## Concurrency and history

All events bind expected main, entity revision, Quest revision, Gate revision,
source fingerprint, and parent checkpoint where applicable. A state-sensitive
operation rejects stale state, duplicate IDs, replay identifiers, concurrent
advancement from one revision, changed prior state, and mismatched lineage.

History is never deleted or silently rewritten. Supersession, invalidation,
reversal, revocation, and reopening use explicit event links. A failed or
reverted acceptance cannot leave a Gate, Quest, blocker, acceptance journey, or
capability falsely complete.

## Activation and delivery

G4-A defines schema and contracts only. G4-B remains read-only. G4-C writes
temporary candidate output only. G4-D may add narrow Thread Engine construction
profiles only after G4-A through G4-C are accepted; Thread Engine self-change
uses the existing Aegis Break to Oathbringer or Phoenix Blade route. A Foundry
adapter is added only if the generic carrier contract proves insufficient.

No code presence activates GitHub processing, canonical writes, Quest Board
cutover, automatic ready, automatic merge, direct-main writes, or semantic
advancement. G4-F activation requires a separate exact-head acceptance record.
