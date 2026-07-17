---
title: "Artemis Runtime and Routing"
atlas_id: "prime.operations.artemis-runtime-routing"
status: "ACTIVE"
source_type: "RUNBOOK"
authority_class: "CANONICAL_AUTHORED_SOURCE"
owner_project: "Project Artemis"
owner_operation: "Operation Nexus"
protected_level: "HIGH"
---

# Artemis Runtime and Routing

Artemis coordinates bounded intelligence work. It does not grant autonomous durable action.

## Nexus

Nexus is the deterministic intake, validation, routing, approval, mission-state, quarantine, and receipt layer. It verifies packages, preserves identity, refuses ambiguous destinations, and separates planning from execution. Nexus is not source truth and cannot merge, delete, deploy, or recover systems without a separately authorized route.

For the Prometheus source architecture, Nexus is planned as a dedicated QEMU
VM named the Nexus Living Memory VM: 10 GB RAM, 4–6 vCPU planning range, and
approximately 120 GB expandable local-NVMe storage. Its Phase 1 retrieval
direction is PostgreSQL relational state plus PostgreSQL full-text search and
`pgvector`; Qdrant is a future option only after measured need is proven.
The VM substrate, PostgreSQL, WAL protection, ClamAV/FreshClam, private health
endpoints, backup, and restore are proof boundaries for Prometheus's Fire.
Living Memory application semantics, Dawnshard, database-backed Controlled
Burn/Phoenix Burn, the private Atlas website, Gitea authority migration, and
other lifecycle/workflow behavior remain deferred to a future Prime Ascendant
Quest, which is not created here.

Nexus has no Matrix / Synapse / Element dependency. Matrix / Element is
disposed from the active Prometheus baseline by PF-C06, with lineage preserved
without claiming deployment or retirement.

## Kandra

Kandra is the adaptive-agent, Skill, and typed-tool layer. Kandra supersedes Hermes as the active Artemis Operation name; Hermes is reserved for the portable human-operated Atlas command endpoint. Worker roles include default coordination, librarian, archivist, scribe, verifier, and an executor that remains disabled until an exact mission explicitly supplies bounded authority. Results return through typed packets and receipts. The rename grants no new authority.

## Athena

Athena authors the Weave: objective, exact base, paths, operations, bytes, authority, stop point, and expected evidence. Athena does not execute the change merely by authoring it.

## Runtime boundary

- Local or remote model choice does not change authority.
- Read-only retrieval and planning are distinct from mutation.
- Private data is minimized, redacted, or kept in its evidence system.
- Tool calls are allowlisted and mission-scoped.
- Every durable mutation requires Prime source, a reviewed route, exact readback, and rollback.
- Failure or absence of Nexus or Kandra must not destroy Prime source or prevent clean-clone recovery.
