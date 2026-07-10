---
title: "Oathbringer Foundry — Prime"
atlas_id: "prime.method.oathbringer-foundry"
status: "IMPLEMENTATION_READY_ACCEPTANCE_PENDING"
source_type: "METHOD"
authority_class: "CANONICAL_AUTHORED_SOURCE"
owner_project: "Project Codex"
owner_operation: "Operation Source Governance"
protected_level: "CRITICAL"
---

# Oathbringer Foundry

**Compiler identity:** `SWORD_FORGE_COMPILER_V1`
**Controlling construction doctrine:** `SWORD_FORGE_STANDARD_V1`

Oathbringer Foundry is Prime's deterministic carrier compiler and read-only
live-state binder. Athena supplies complete, exact mission and payload bytes;
the Foundry validates them, binds the declared current source and GitHub state,
and emits one immutable carrier ZIP plus its SHA-256 sidecar.

It accepts the modes `BUILD`, `REPAIR`, `RECOVERY`, and `EXECUTE`. For the
currently supported Oathbringer production lanes, it embeds a fully bound
GitHub-native production mission and the deterministic transport library. A
`RECOVERY` carrier packages its recovery contract and exact evidence without
claiming that it writes, retries, rolls back, readies, or merges anything.

## Boundary

The Foundry is not a weapon, source author, GitHub writer, repository engine,
Thread Engine replacement, automatic merger, authority service, or standing
credential holder. It has no route to create a branch, commit, pull request,
ready transition, merge, workflow dispatch, retry, rollback, cleanup, or
repository setting. Its live binder invokes only read-only GitHub queries and
never serializes credentials.

## Required binding

Every carrier binds:

- one mode, immutable mission identity, authorizer, operator, stop boundary,
  rollback/recovery contract, and public-clean privacy classification;
- repository, exact base, exact branch and head/PR when applicable;
- complete operation inventory and final payload bytes/hashes;
- source and workflow blob identities;
- the current `prime-sword-lessons-v1` register and a classification for every
  controlling lesson;
- the complete current applicable Oathbringer transport source hashes and a
  carrier manifest;
- a deterministic Forge receipt, Deflected Sword configuration, and test
  contract.

## Determinism and rejection

Carriers use UTF-8 without BOM, LF JSON, Unicode NFC paths, sorted keys and
members, fixed ZIP metadata, stable file modes, and stored ZIP members. A
repeated compile from identical normalized inputs is byte-identical across
platforms.

Current transport source hashes bind the checked source bytes; transport text
is then normalized to UTF-8 without BOM and LF line endings inside the carrier.

The compiler fails closed for moved base/head, missing authority, undeclared or
missing final bytes, malformed JSON, unsafe paths, Unicode/case-fold collisions,
non-regular files, archive-bomb limits, stale source/workflow locks, missing or
unclassified lessons, replayed mission identity, mismatched independent audit,
or token-shaped/protected material.

Production compilation records successful mission identities in a durable
output-directory replay ledger. Payloads and audit evidence are restricted to
their dedicated namespaces and cannot replace compiler-controlled carrier
material.

## Invocation

Use `tools/oathbringer-foundry/Invoke-OathbringerFoundry.ps1` or the Python
CLI. Production compilation requires an input root and a source root, then
obtains a fresh `gh` read-only binding itself. A successful compile is carrier
preparation only; it never grants execution or merge authority.
