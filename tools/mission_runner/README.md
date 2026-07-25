---
title: "Mission Runner and Worldhopper Relay"
atlas_id: "prime.tools.mission-runner"
status: "CANONICAL_ACTIVE"
source_type: "TOOL_CONTRACT"
authority_class: "CANONICAL_AUTHORED_SOURCE"
owner_project: "Project Artemis"
owner_operation: "Operation Harmony"
protected_level: "CRITICAL"
---

# Mission Runner and Worldhopper Relay

`tools.mission_runner` is a provider-neutral, read-only orchestration library for
resuming one exact Mission attempt across workers, providers, connectors,
runtimes, and sessions. It is not a publisher, canonical state store, authority
source, lease service, or replacement for the Mission Board.

The relay reconstructs from the latest valid `atlas.mission.v1` manifest,
append-only `atlas.mission-checkpoint.v1` records, current canonical `main`, and
the one working branch or pull request. Every adapter declares closed stage
capabilities and accepted takeover evidence before it may claim a stage.

Partial source may use one `WORKING_DRAFT` handoff on the deterministic Mission
branch. The handoff binds the public-clean path set and expected branch head.
Updates use compare-and-swap; a sealed candidate is immutable; a working draft
cannot bind a pull request.

Fallback execution is an ordered ledger of `atlas.mission-route-attempt.v1`
records. A capability failure advances only the affected stage to the next
authorized route. `BLOCKED_RESUMABLE` is rejected while any route remains
pending or unevaluated unless the last terminal receipt proves a true safety,
authority, drift, or operator-transfer gate.

The normal publisher remains Thread Engine. Sword/Oathbringer remains the
failure-isolated publisher. Aegis Break may use an exact GitHub-native
blob/tree/commit/ref/file/draft-PR substrate only for already trusted bytes with
proven provenance, expected-head protection, validation, rollback, and
readback. No route may fabricate compiler-owned lifecycle bytes.
