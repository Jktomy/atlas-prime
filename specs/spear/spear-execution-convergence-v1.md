---
title: Spear Execution Convergence v1
atlas_id: spear.execution-convergence.v1
format_version: "1.0"
status: PROPOSED
source_type: SPECIFICATION
authority_class: TOOL_CONTRACT
owner_project: Codex
owner_operation: Athena's Spear
canonical_scope: Defines the runner-neutral Spear transaction, GitHub-native and Artemis Bow execution adapters, Athena-Artemis-Jayson escalation, CLI-primary Gates 1-8 campaign posture, separate Build and Execute Arrows, common receipts, and recovery requirements without granting writer authority.
protected_level: CRITICAL
routes_from:
  - athenas-spear.md
  - specs/spear/spear-capability-lifecycle-v1.md
  - tools/spear/operator-runbook.md
  - tools/spear/recovery-runbook.md
routes_to:
  - schemas/spear/spear-packet-v1.schema.json
  - policies/operations/spear/spear-policy-v1.yaml
  - migration/atlas-codex/atlas-prime-rebuild-program-roadmap-v1.md
  - quest-board/quest-board-shadow-v1.json
private_boundary: This specification may contain clean contracts, repository identities, route names, limits, tests, and recovery rules only. It must not contain secrets, credentials, PHI, raw finance or account evidence, private runtime values, network maps, device registers, real environment values, or protected exports.
evidence_boundary: This specification defines intended behavior. Implementation, workflow runs, Arrow packages, receipts, PRs, Noctua reports, activation records, and recovery proof remain separate evidence.
supersedes: []
cleanup_path: Retain through the Spear/Bow convergence and capability-proof campaign. Supersede only through a separately reviewed protected source transaction with compatibility and recovery treatment.
last_verified: 2026-06-29
---

# Spear Execution Convergence v1

## Status and controlling scope

Status: PROPOSED tool contract. It grants no writer authority.

For execution-adapter, Arrow-artifact, and Athena-Artemis-Jayson escalation semantics, this later-verified specification controls conflicting older Prime wording until those sources are reconciled through reviewed transactions.

## Operating hierarchy

```text
Jayson states intent and grants bounded authority
-> Athena reads current durable source and prepares one exact runner-neutral Spear transaction
-> the approved execution adapter performs the transaction
-> Artemis Local Operator is the local fallback operator
-> Jayson is the final manual fallback and remains the ultimate authority
-> Noctua verifies durable results
```

Execution escalation is Athena -> Artemis -> Jayson. Authority remains with Jayson throughout.

## Runner-neutral transaction

One Spear transaction binds exact candidate bytes, repository subtransactions, bases, expected blobs, allowed paths, hashes, route and capability versions, protected boundaries, tests, PR expectations, recovery rules, Noctua criteria, and forbidden actions.

The transaction must not contain caller-selected executable code, hidden policy, or authority-expanding instructions.

## Execution adapters

### GitHub-native Spear adapter

The intended long-term normal runner after capability proof and activation. It creates deterministic branches, commits, draft PRs, readback, and receipts, then stops before merge.

### Artemis Bow adapter

The local runner. It consumes the same transaction through a thin launcher and exact package. It must not perform semantic authoring or reconstruct source changes.

## Gates 1-8 campaign posture

For Atlas Prime Rebuild Gates 1-8, Bow and Arrow CLI is the approved primary repository-mutation route.

- GitHub connectors remain readback and audit surfaces.
- Prime S1 remains disabled except for a separately approved proof.
- Jayson operates the Bow until Artemis Local Operator is implemented, proven, and activated.
- Bow-primary campaign execution does not change the long-term GitHub-native Spear destination.

## One mission, separate Arrows

A mission may produce:

1. a Build Arrow that creates and verifies draft PRs and stops;
2. an Execute Arrow created only after Noctua audit and Jayson exact-head approval.

They share mission lineage but have separate IDs, manifests, hashes, receipts, and approval records. Build success never grants Execute authority.

## Final-byte rule

Execution adapters receive complete final candidate bytes whenever practical. Source reasoning and compilation occur before execution. PowerShell and workflow runners verify and perform repository mechanics only.

## Common receipts

Both adapters must emit equivalent receipts recording transaction, mission, runner, Arrow, bases, candidate and manifest hashes, changed files, branches, commits, PR heads, merges when applicable, result, last completed gate, authority used, and forbidden-action confirmation.

## Idempotency and recovery

Active adapters must detect exact replay, branch-created, commit-pushed, branch-pushed/PR-missing, PR-state-uncertain, draft-PR-verified, partial repository success, merge/readback incomplete, and complete states.

A rerun resumes only a missing permitted action. It must not reset successful work, force-push, delete, close, create duplicates, or broaden scope.

## Current implementation posture

- Codex remains canonical.
- Prime remains SHADOW.
- Prime S0 is read-only compiler support.
- Prime S1 remains hard-disabled and dependency-blocked.
- Artemis Local Operator is not implemented or activated.
- Gates 1-8 repository mutations use Jayson-fired CLI Arrows.

## Proof sequence

```text
continuity and doctrine convergence
-> runner-neutral transaction and receipt contracts
-> harmless GitHub-native Build proof
-> equivalent local Bow Build proof
-> recovery and exact replay proof
-> separately approved Execute proof
-> multi-file and linked multi-repository proof
-> Artemis read-only validation and later bounded local operation
-> bounded migration use
```

## Authority boundary

This specification does not activate S1, authorize repository mutation, fire an Arrow, grant Artemis authority, authorize merge, migrate content, promote Prime, retire Codex, delete evidence, modify Google Drive, or perform cutover.
