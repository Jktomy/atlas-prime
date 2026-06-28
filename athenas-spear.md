---
title: Athena's Spear S0 Prime Migration Compiler Proposal
atlas_id: spear.s0.offline-compiler
format_version: "1.0"
status: PROPOSED
source_type: PROTOCOL
authority_class: CANONICAL_AUTHORED_SOURCE
owner_project: Codex
owner_operation: Athena's Spear
canonical_scope: Defines the probationary S0 compiler, Athena/Jayson conversation-to-source operating model, permanent Spear safety architecture, Artemis's Bow and Arrow handoff, Emberline relationship, capability evolution, migration role, and post-cutover maintenance boundary while Atlas Codex remains canonical until verified cutover.
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
  - specs/spear/spear-capability-lifecycle-v1.md
  - specs/atlas-prime/codex-to-prime-migration-contract-v2.md
  - migration/atlas-codex/atlas-prime-rebuild-program-roadmap-v1.md
  - migration/atlas-codex/README.md
  - templates/codex-to-prime-reconciliation-record.md
private_boundary: This source must contain only clean protocol text and must not include secrets, private runtime values, raw account evidence, PHI, or protected exports.
evidence_boundary: This file is authored source; generated receipts, test logs, package manifests, migration evidence, and original protected evidence remain outside this source unless separately approved.
supersedes: []
cleanup_path: Update through a separately reviewed Spear engine or protocol PR; do not alter Spear governance or implementation through an ordinary Spear packet.
last_verified: 2026-06-28
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

The Athena's Spear implementation being built in Atlas Prime is intended to become Athena's permanent controlled source-change instrument for the Atlas Prime rebuilding campaign and for normal Atlas evolution after cutover.

It is designed primarily for Athena operating inside an active ChatGPT conversation with Jayson. Its long-term purpose is to convert Jayson-approved intent into structured, auditable, recoverable source-change packets without depending on fragile direct-write connectors.

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

## Permanent platform and controlled evolution

The Spear Campaign builds and proves the machine. The campaign may close after the required migration routes are proven, but Athena's Spear itself remains a permanent Atlas Prime source-change platform.

Spear evolves through four separable layers:

1. **Safety kernel** — packet parsing, contract binding, repository and expected-state validation, path safety, protected-content checks, deterministic planning, receipts, branch and commit controls, stop-before-merge, and recovery behavior. The kernel is deny-by-default and changes rarely.
2. **Capabilities** — versioned operations such as create, replace, bounded surgical mutation, append, structured-register transition, generator execution, lifecycle handling, and lineage generation.
3. **Route profiles** — versioned combinations of path classes, operations, limits, atomicity, tests, recovery, Noctua criteria, and activation state for recurring change families.
4. **Packets** — exact bounded instances that invoke only already-defined and appropriately activated capabilities and route profiles.

Flexibility belongs in reusable versioned capabilities and route profiles, not in packet-specific weakening of safeguards. A recurring legitimate need discovered by Evolving Prime may justify a new Spear capability. One difficult packet does not justify bypassing or globally relaxing policy.

Implementation and authority remain separate. Code, schemas, or route profiles may exist while operational activation remains `NO`. No capability becomes executable merely because it compiles, tests, or merges.

The normative capability states, promotion gates, compatibility rules, deactivation rules, and post-cutover maintenance process are defined in:

`specs/spear/spear-capability-lifecycle-v1.md`


## Jayson-Athena operating relationship

The controlling relationship is:

```text
Jayson defines the goal, boundaries, and approval
-> Athena reads current source and reasons about the safest exact change
-> Athena's Spear validates and packages only that approved intent
-> Artemis's Bow fires an exact Arrow when package-based local execution is selected
-> Noctua independently audits the result
-> Jayson retains final activation, merge, migration, promotion, retirement, and cutover authority
```

Spear is optimized for conversation-to-durable-source work. It may support adding, augmenting, reconciling, reorganizing, and retiring Atlas source only through versioned routes whose authority has been separately proven and activated.

Technical capability never implies authorization. Chat discussion may propose change, but only an exact source-backed Preview and explicit Jayson approval may authorize the next bounded gate.

## Artemis's Bow and Arrow handoff

Artemis's Bow and Arrow is the user-facing local execution model for exact package-based Spear work.

- **The Bow** is the stable thin Command Prompt or PowerShell launch surface Jayson uses.
- **An Arrow** is one exact immutable ZIP payload plus its exact firing command or launcher.
- **Stage 1 — Build and Verify** may create and read back only the approved draft-PR state, then stops for Noctua.
- **Stage 3 — Merge and Readback** may be prepared and fired only after complete Stage 1 receipts, Noctua on the exact PR head, and a separate Jayson approval.

The Bow may be reusable. Every Arrow is mission-specific, hash-bound, and disposable. Stage 1 never authorizes Stage 3.

The current Codex-side user contract is `Jktomy/atlas-codex/codex/artemis-bow-and-arrow.md`. Prime operator and recovery guidance must remain compatible until cutover and later source-order reconciliation.

## Emberline relationship

Emberline is the Quest/Campaign roadmap and status surface. It explains where the campaign is, what is complete, what remains, how much is left, what is blocked, and the next safe gate.

For source work:

```text
Emberline identifies the road and current gate
-> Spear prepares the exact source change
-> Bow and Arrow performs an approved package handoff when selected
-> Noctua and Jayson control the merge gate
```

Emberline status is read-only. Durable source changes use the normal Spear/source-update route under Preview -> Execute. Historical **Ember Line** wording refers to the same unified Emberline system and does not create another protocol.

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
- Bow/Arrow stage and separate-authorization behavior when local package execution is selected;
- explicit prohibitions;
- rollback or recovery instructions;
- and the Noctua stop gate.

Before execution, Athena must present an exact Preview with files, old and new hashes, complete diff or replacement text, additions, deletions, source-truth consequences, protected-boundary findings, tests, expected PR shape, Bow/Arrow stage when applicable, recovery behavior, and unresolved decisions.

No execution occurs until Jayson approves the exact Preview.

Noctua must independently verify source order, changed filenames, complete diff, metadata, protected boundaries, tests, workflows, lineage, packet-to-PR fidelity, current head, evidence separation, and the proposal's relationship to current canonical Atlas Codex.

A technically valid packet does not authorize merge, migration, promotion, or cutover.

## Campaign sequence

The Spear Campaign and Evolving Prime overlap rather than run as a simple handoff:

1. preserve the operational Codex Spear while Prime S0 remains probationary;
2. freeze and audit the stable S0 compiler contract;
3. continue Evolving Prime read-only reconciliation to discover legitimate recurring route needs;
4. design, implement, and prove S1 writer authority without broad activation;
5. add narrowly versioned capabilities and route profiles in response to demonstrated recurring needs;
6. use approved packets to rebuild Atlas Prime in bounded batches;
7. audit every packet, PR, merge, and merged-main state through Noctua and required human gates;
8. preserve Atlas Codex as canonical until Prime is fully reconciled, recoverable, and explicitly approved for cutover;
9. close the Spear build campaign into permanent maintenance after all migration-required routes are proven;
10. continue post-cutover Spear evolution through the capability lifecycle rather than freezing the platform or granting unrestricted authority.

The program-level dependencies, current M0-M9 migration waves, and A0-A7 Spear phases are coordinated in:

`migration/atlas-codex/atlas-prime-rebuild-program-roadmap-v1.md`

## Migration contract

The normative Codex-to-Prime source order, reconciliation method, route selection, packet lifecycle, full-file replacement controls, proof requirements, and closure rules are defined in:

`specs/atlas-prime/codex-to-prime-migration-contract-v2.md`

Migration evidence is routed through:

`migration/atlas-codex/README.md`

Athena prepares the required read-only pre-packet analysis from:

`templates/codex-to-prime-reconciliation-record.md`

Current S0 ordinary packets remain limited by the active overlay and destination policy. They do not authorize protected root, governance, schema, policy, tool, test, workflow, generated, structured-register, or migration-evidence writes.

Those surfaces require their separately approved source, migration, register, generator, or future versioned Spear routes.

## Post-cutover operating model

After explicit Atlas Prime cutover, Spear changes role but not its permanent safeguards. The normal source-update flow becomes:

```text
canonical Prime source
-> read-only analysis and exact Preview
-> approved Spear packet
-> validation and deterministic candidate
-> bounded branch, commit, and draft PR
-> Noctua and Jayson merge decision
-> merged-main readback and retained lineage
```

Post-cutover Spear remains prohibited from direct `main` writes, force-push, automatic merge, silent authority expansion, protected-evidence ingestion, and ordinary self-modification. New capabilities continue through versioned proposal, fixture, proof, limited activation, operational, deprecation, and retirement gates.

Spear governance, implementation, schemas, policies, tests, and workflows must use a separately reviewed engine or protocol route. An ordinary Spear packet must never grant itself broader authority.

## Predecessor continuity

The merged Prime Spear v0.2 files remain predecessor design and historical/reference evidence:

- `specs/spear/athenas-spear-spec-v0.2.md`
- `schemas/spear/athenas-spear-packet-v0.2.schema.json`
- `tests/fixtures/spear/corpus-v0.2.md`

S0 v4 is the current probationary Prime migration-compiler proposal. Neither v0.2 nor S0 v4 grants writer activation, migration authority, source promotion, or cutover. S1 and all later execution phases remain separately gated.

## One Arrow and Quest Board correction

Prime Spear prepares one immutable Arrow package with sealed stages. It does not prepare competing Arrow 1 and Arrow 2 packages.

The Codex Active Workboard and Prime Quest Board are one system across repository generations. Quest is the parent, Campaign is the child/subquest, and Emberline is the complete Quest status model.

Prime Quest Board remains SHADOW until verified cutover.
