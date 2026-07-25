---
title: "Worldhopper Mission Relay Contract"
atlas_id: "prime.governance.worldhopper-relay"
status: "CANONICAL_ACTIVE"
source_type: "PROTOCOL"
authority_class: "CANONICAL_AUTHORED_SOURCE"
owner_project: "Project Artemis"
owner_operation: "Operation Harmony"
protected_level: "CRITICAL"
routes_from:
  - governance/mission-first-chat-handoff-contract.md
  - governance/mission-board-contract.md
  - governance/repository-process-contract.md
routes_to:
  - tools/mission_runner/README.md
  - tools/mission_runner/core.py
  - recovery/elantris-recovery.md
---

# Worldhopper Mission Relay Contract

## Purpose and authority

One Mission attempt must survive worker, provider, connector, runtime, BEU, or
session loss without a duplicate Mission, branch, pull request, candidate, or
authority claim. Mission Board is the public-clean baton, merged Prime remains
canonical source, and the linked working branch or pull request preserves the
one source transaction.

The Mission Runner reconstructs and verifies these surfaces. It is stateless for
authority and never becomes a third publisher, transaction authority, lease
service, compiler, lifecycle author, or source of canonical truth.

## Digest-chained checkpoints

Every durable relay checkpoint uses `atlas.mission-checkpoint.v1`. Checkpoints
are append-only operational evidence and bind:

- Mission and attempt;
- sequence, prior checkpoint digest, stable checkpoint identity, and digest;
- worker, stage, observed canonical and branch heads;
- completed work, remaining work, stop reason, and next action; and
- claim identity, lease disposition, and expected prior digest.

A missing predecessor, fork, replay, stale expected digest, simultaneous active
claim, Mission drift, attempt drift, or head drift rejects takeover. A
checkpoint records work; it does not grant Build, READY, permanence, protected
access, or canonical status.

## Worker capabilities and stage matching

Every adapter publishes one closed `atlas.mission-worker-capability.v1`
declaration. Stage assignment requires both the matching capability and an
accepted takeover-evidence reference for that exact stage. Provider or model
identity, an available connector, a role name, or earlier success is not
capability proof.

The closed stages are Mission read, checkpoint, source construction,
compilation, validation, publication, review, READY, exact-head permanence, and
canonical readback. Unsupported workers cannot claim a stage.

## Bounded working-source handoff

Partial source work may exist only as `WORKING_DRAFT` on one deterministic
Mission branch. Each `atlas.mission-working-source-handoff.v1` binds the exact
base, expected branch head, complete public-clean changed paths and digest, prior
handoff digest, and force-push denial.

Every update is expected-head compare-and-swap and independently read back.
`WORKING_DRAFT` cannot bind a pull request, Candidate Seal, review result,
READY evidence, or permanence evidence. After complete prepublication
validation, one immutable `SEALED` handoff may bind the one draft pull request.
Any changed byte invalidates the seal and all head-bound evidence.

## Ordered executable fallback

Every approved route has one ordered `atlas.mission-route-attempt.v1` record per
stage. Its status is exactly:

```text
PENDING
IN_PROGRESS
SUCCEEDED
REJECTED_CAPABILITY
REJECTED_SAFETY
REJECTED_AUTHORITY
REJECTED_DRIFT
TRANSFER_REQUIRED
```

A failed capability advances automatically to the next authorized route for
that stage while preserving valid state. A local checkout failure does not
block GitHub-native publication, review, or readback. Compilation and
publication may use different capable Worldhoppers while preserving the same
Mission, attempt, candidate bytes, branch, and pull request.

Mission-wide `BLOCKED_RESUMABLE` is invalid while any authorized route is
pending, nonterminal, missing, or unevaluated. Early blocking is permitted only
when the last terminal receipt proves a true safety, authority, semantic,
protected-boundary, drift, ambiguity, or operator-transfer gate.

## Publisher isolation and GitHub-native Aegis Break

Thread Engine remains the normal publisher. Sword/Oathbringer remains the
independent recovery publisher. They may share schemas, receipts, validation,
and fixtures but not one mutation implementation whose failure disables both.

Aegis Break must evaluate an exact GitHub-native blob, tree, commit, ref, file,
and draft-PR substrate when that stage can be completed safely. It may publish
only compiler-produced or otherwise deterministically proven bytes with
provenance, complete paths, expected-head compare-and-swap, validation,
rollback, and independent readback. It cannot manually invent lifecycle bytes,
skip source fingerprints, create a standing publisher, or treat contents-API
assembly as the normal route.

## Recovery and completion

Recovery reads current Prime, the complete Mission Issue history, all
checkpoints and route receipts, current canonical main, and the one linked
working branch or pull request before action. Deleted branches, closed or
mismatched pull requests, moved heads, undeclared paths, protected content,
duplicate objects, replay, and ambiguous writes fail closed.

Relay repair is complete only after synthetic takeover and ordered-fallback
tests, full exact-head Prime validation, review reconciliation, Strikeforce
GREEN, authorized permanence, exact merged-main readback, rollback proof, and
Mission closure. A successful route, branch, PR, check, READY state, or merge
response alone is not completion.
