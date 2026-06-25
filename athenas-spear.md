---
title: Athena's Spear S0 Prime Migration Compiler Proposal
atlas_id: spear.s0.offline-compiler
format_version: "1.0"
status: PROPOSED
source_type: PROTOCOL
authority_class: CANONICAL_AUTHORED_SOURCE
owner_project: Codex
owner_operation: Athena's Spear
canonical_scope: Defines the probationary S0 compiler and validation foundation for the next-generation Athena's Spear in Atlas Prime while Atlas Codex remains the current canonical source of truth.
protected_level: CRITICAL
routes_from:
  - specs/spear/athenas-spear-spec-v0.2.md
  - schemas/spear/athenas-spear-packet-v0.2.schema.json
  - tests/fixtures/spear/corpus-v0.2.md
routes_to:
  - schemas/spear/spear-packet-v1.schema.json
  - policies/operations/spear/spear-policy-v1.yaml
  - tools/spear/cli.py
  - tools/spear/operator-runbook.md
  - tools/spear/recovery-runbook.md
private_boundary: This source must contain only clean protocol text and must not include secrets, private runtime values, raw account evidence, PHI, or protected exports.
evidence_boundary: This file is authored source; generated receipts, test logs, package manifests, migration evidence, and original protected evidence remain outside this source unless separately approved.
supersedes: []
cleanup_path: Update through a separately reviewed Spear engine or protocol PR; do not alter Spear governance or implementation through an ordinary Spear packet.
last_verified: 2026-06-25
---

# Athena's Spear MVP S0 v4

Status: PROBATIONARY Atlas Prime migration-compiler foundation.

## Atlas transition model

Atlas Prime is the next evolution of Atlas.

During construction:

- `Jktomy/atlas-codex` remains the current canonical source of truth.
- `Jktomy/atlas-prime` is the next-generation Atlas architecture being designed, tested, and assembled.
- Nothing in Atlas Prime becomes canonical merely because it exists, compiles, or passes testing.
- Promotion, migration, or cutover from Atlas Codex to Atlas Prime requires separate review, verification, rollback planning, Noctua audit, and explicit Jayson approval.
- The current operational Athena's Spear in Atlas Codex remains the active durability tool until a separately approved transition changes that status.
- The Prime-side Spear does not silently replace, supersede, or compete with the current canonical Spear.

## Purpose of Prime Spear

The Athena's Spear implementation being built in Atlas Prime is intended to become the controlled migration and source-change engine for the Atlas Prime rebuilding campaign.

Its long-term purpose is to let Athena prepare structured, auditable source-change packets without depending on fragile direct-write connectors.

The intended end-state is for Prime Spear to:

1. receive a structured Spear packet prepared by Athena;
2. validate it against the exact repository, base commit, schemas, policies, protected paths, source metadata, and real Git state;
3. generate a deterministic proposed source tree and review evidence;
4. apply only an explicitly approved packet;
5. stage and audit only the approved files;
6. create an approved branch, commit, and draft pull request through a controlled workflow;
7. stop before merge for Noctua audit and Jayson approval;
8. never self-approve, silently promote source truth, bypass protected boundaries, force-push, write directly to `main`, or merge automatically.

The execution capabilities in items 4 through 7 are intended future phases. They are not implemented or authorized by S0.

## Current S0 implementation boundary

PR #3 implements only the probationary S0 offline compiler and validation foundation.

S0 currently:

- receives one bounded structured packet;
- validates it against the pinned packet schema and Spear overlay;
- validates it against the pinned Atlas Prime destination policy, protected-path policy, source-metadata schema, and real Git base state;
- loads all controlling contracts from the target repository at the already-verified packet `base_commit`;
- supports deterministic planning for the registered operations `CREATE_FILE` and `REPLACE_FILE_FULL`;
- verifies target absence or exact expected Git blob state;
- generates a normalized packet, operation manifest, validation receipt, and proposed source tree;
- writes review evidence only to a protected external output root;
- records `EXECUTION_NOT_AUTHORIZED`.

S0 does not:

- modify repository files;
- stage changes;
- create or switch branches;
- create commits;
- push;
- create or update pull requests;
- merge;
- activate migration;
- modify Atlas Codex;
- promote Atlas Prime to canonical;
- or grant S1 writer authority.

Every future execution phase requires its own specification, tests, Preview -> Execute authorization, Noctua review, recovery path, and explicit Jayson approval.

## Atlas Prime rebuilding campaign

Once Prime Spear is proven safe through separately approved phases, Athena will use Spear packets to rebuild a cleaner and stronger Atlas Prime from:

- current valid source truth in Atlas Codex;
- approved Atlas Prime architectural improvements;
- durable session harvests and approved chat decisions;
- known structural problems identified before this campaign;
- obsolete, duplicated, conflicting, or poorly organized source;
- missing protocols, schemas, routing, indexes, and continuity records;
- and lessons learned from connector blocks and fragile direct-edit workflows.

The objective is not to copy Atlas Codex blindly.

The objective is to reconcile valid Codex truth with approved Prime improvements, deliberately preserve or supersede useful material, remove known structural problems, and produce a cleaner next-generation Atlas through bounded, reviewable migrations.

## Athena's required preparation before a Spear packet

Before preparing a packet, Athena must complete a read-only planning and reconciliation pass.

Athena must:

1. read the relevant current files from `atlas-codex/main`;
2. read the complete current Atlas Prime targets;
3. review relevant session harvests, approved decisions, current chat context, repair records, Noctua findings, migration maps, rejected approaches, Active Workboard items, and unresolved Decision Boxes;
4. classify source material as preserve, reorganize, update, replace, add, retire, retain as history, defer, or exclude;
5. identify conflicts between Codex and Prime and present a Decision Box when the resolution has downstream consequences;
6. choose the safest approved change method;
7. prepare an exact packet containing repository, branch, commit, target, expected-state, content, hash, metadata, boundary, test, recovery, and stop-gate information;
8. present an exact Preview before execution.

Chat discussion may inform a packet, but chat-only ideas must not be silently promoted into source truth.

## Full-file replacement policy

Full-file replacement is an intended Prime migration operation because the purpose of Atlas Prime is to rebuild source cleanly rather than accumulate fragile patches indefinitely.

Full-file replacement is acceptable only when:

- Athena has read the complete current file;
- the full proposed replacement is available for review;
- valid source content is deliberately preserved or intentionally superseded;
- the replacement produces a cleaner and more coherent file;
- the packet identifies the exact expected current Git blob SHA;
- the complete old-to-new diff is audited;
- no private or protected material is introduced;
- the target has no unresolved competing authority;
- and Jayson explicitly approves the exact replacement through Preview -> Execute.

Full-file replacement must fail closed when:

- the current file cannot be read completely;
- the expected blob SHA is stale;
- valid information would be removed silently;
- the target contains private or protected evidence inappropriate for GitHub;
- the authority relationship is unresolved;
- or the resulting diff cannot be reviewed safely.

Surgical changes remain appropriate when only a small bounded section needs correction, the file is sensitive or safety-adjacent, untouched text requires strong preservation, or a full replacement would create unnecessary review risk.

The method is chosen by safety and clarity, not by minimizing changed lines.

## Packet, Preview, execution, and audit gates

A future execution-authorized Spear packet must identify:

- target repository;
- exact base branch and commit;
- approval basis and migration purpose;
- exact files and operations;
- expected absence or exact current blob SHA;
- complete replacement content or bounded surgical operation;
- content hashes, source type, and authority class;
- protected-boundary declarations;
- tests and verification requirements;
- expected branch, commit, and draft-PR behavior;
- explicit prohibitions;
- rollback or recovery instructions;
- and the Noctua stop gate.

Before execution, Athena must present an exact Preview with files, old and new hashes, complete diff or replacement text, additions, deletions, source-truth consequences, protected-boundary findings, tests, expected PR shape, and unresolved decisions.

No execution occurs until Jayson approves the exact Preview.

Noctua must independently verify source order, changed filenames, complete diff, metadata, protected boundaries, tests, workflows, lineage, packet-to-PR fidelity, current head, evidence separation, and the proposal's relationship to current canonical Atlas Codex.

A technically valid packet does not authorize merge, migration, promotion, or cutover.

## Campaign sequence

The intended campaign sequence is:

1. build and prove Prime Spear;
2. define Codex-to-Prime reconciliation and migration rules;
3. use Athena-prepared packets to rebuild Atlas Prime in bounded batches;
4. audit every batch through Noctua;
5. preserve Atlas Codex as canonical until Prime is fully reconciled and verified;
6. perform explicit cutover only after restore, rollback, routing, source-order, and continuity proof;
7. retain Atlas Codex as historical or rollback evidence under a separately approved sunsetting plan.

## Predecessor continuity

The merged Prime Spear v0.2 files remain predecessor design and historical/reference evidence:

- `specs/spear/athenas-spear-spec-v0.2.md`
- `schemas/spear/athenas-spear-packet-v0.2.schema.json`
- `tests/fixtures/spear/corpus-v0.2.md`

S0 v4 is the current probationary Prime migration-compiler proposal. Neither v0.2 nor S0 v4 grants writer activation, migration authority, source promotion, or cutover. S1 and all later execution phases remain separately gated.
