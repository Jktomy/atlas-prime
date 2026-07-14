---
title: "Oathbringer Foundry — Prime"
atlas_id: "prime.method.oathbringer-foundry"
status: "PRODUCTION_ACTIVE"
source_type: "METHOD"
authority_class: "CANONICAL_AUTHORED_SOURCE"
owner_project: "Project Codex"
owner_operation: "Operation Source Governance"
protected_level: "CRITICAL"
---

# Oathbringer Foundry

**Compiler identity:** `SWORD_FORGE_COMPILER_V1`
**Controlling construction doctrine:** `SWORD_FORGE_STANDARD_V1`

Oathbringer Foundry is Prime's deterministic carrier compiler, read-only
live-state binder, and operator-handoff generator. Athena supplies complete,
exact mission and payload bytes; the Foundry validates them, binds the declared
current source and GitHub state, and emits one immutable carrier ZIP plus its
SHA-256 sidecar. After independent carrier verification, Foundry can emit one
fixed-shape PowerShell 7 paste command for that exact ZIP and digest.

It accepts the modes `BUILD`, `REPAIR`, `RECOVERY`, and `EXECUTE`. For the
currently supported Oathbringer production lanes, it embeds a fully bound
GitHub-native production mission and the deterministic transport library. That
transport includes the one canonical Oathbringer Console v2 implementation from
`tools/atlas-sword/engine/`; Foundry version-binds and packages it but does not
duplicate or redefine its runtime behavior. A `RECOVERY` carrier packages its
recovery contract and exact evidence without claiming that it writes, retries,
rolls back, readies, or merges anything.

## Boundary

The Foundry is not a weapon, source author, GitHub writer, repository engine,
Thread Engine replacement, automatic merger, authority service, or standing
credential holder. It has no route to create a branch, commit, pull request,
ready transition, merge, workflow dispatch, retry, rollback, cleanup, or
repository setting. Its live binder invokes only read-only GitHub queries and
never serializes credentials.

The operator handoff verifies, extracts, and launches an already sealed carrier.
It cannot edit the mission, reinterpret payload bytes, broaden authority, or
replace Oathbringer's package-integrity and runtime gates.

## Required binding

Every carrier binds:

- one mode, immutable mission identity, authorizer, operator, stop boundary,
  rollback/recovery contract, and public-clean privacy classification;
- repository, exact base, exact branch and head/PR when applicable;
- complete operation inventory and final payload bytes/hashes;
- source and workflow blob identities;
- the current `prime-sword-lessons-v1` register and a classification for every
  controlling lesson;
- the complete current applicable Oathbringer transport source hashes, including
  Console v2, and a carrier manifest;
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

## Operator delivery

The final artifact delivered to Jayson is the Foundry carrier itself. Foundry
must not wrap it in a second outer ZIP, and a normal handoff must not require a
separately downloaded mission-specific PowerShell file.

The `handoff` command first verifies the completed carrier, rereads its actual
SHA-256, and emits a deterministic handoff record. The paste command has one
canonical template; only the safe carrier filename and lowercase SHA-256 vary.
The normal human experience is therefore:

1. download one `Oathbringer-Foundry-<mission>-<revision>.zip`;
2. paste the one PowerShell 7 command supplied from the verified handoff record;
3. press Enter.

The command verifies the complete ZIP digest before extraction, uses a unique
temporary workspace, places the receipt and Deflected Sword evidence under
`Downloads/Atlas-Oathbringer-Evidence`, invokes the carrier's canonical launcher,
and then yields presentation to Oathbringer Console v2. A successful temporary
workspace is removed; a failed workspace is retained for bounded review.

The SHA-256 sidecar and delivery evidence may remain in Athena's Forge evidence.
They are not a second required Jayson download because the independently reported
expected SHA-256 is embedded in the paste command.

## Invocation

Use `tools/oathbringer-foundry/Invoke-OathbringerFoundry.ps1` or the Python
CLI. Production compilation requires an input root and a source root, then
obtains a fresh `gh` read-only binding itself. A successful compile is carrier
preparation only; it never grants execution or merge authority.

Verify the carrier before handoff:

```text
python -B tools/oathbringer-foundry/cli.py verify --carrier <carrier.zip>
```

Generate the one-download operator handoff only after verification:

```text
python -B tools/oathbringer-foundry/cli.py handoff --carrier <carrier.zip> --json
```

## Live production acceptance

The complete Foundry-to-Oathbringer carrier chain is live-proven and active.

The R04 acceptance transaction established:

- deterministic double compilation for BUILD, REPAIR, and EXECUTE carriers;
- exact source, workflow, mission, payload, and independent-audit binding;
- BUILD creation of draft PR `#66` at `93dc448aa7a2208043ea3fb742576813d8e0a87c`;
- REPAIR fast-forward to direct-child head `ab33dd486e9022d26f793b85034ebfe1f307025f`;
- bounded read-only branch and pull-request head convergence without repeated mutation;
- exact audited-head ready transition and squash merge to canonical `main` at `11d0db1c82c36c2bbdc07b02882da4f156b7b4e8`;
- automatic local evidence ZIP packaging without broadening GitHub authority.

Canonical proof is recorded in `proof/oathbringer-production-acceptance-r01.md`.
The one-download handoff contract does not self-promote a new acceptance journey;
its separate live use and reconciliation remain evidence-gated.

This acceptance does not grant standing authority. Every carrier remains mission-specific, exact-state bound, separately authorized, and subject to its declared stop boundary.
