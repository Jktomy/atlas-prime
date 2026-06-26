---
title: "Atlas Prime Rebuild Quest — Dual-Campaign Roadmap v1"
atlas_id: "atlas-prime.quest.rebuild-roadmap.v1"
format_version: "1.0"
status: "PROPOSED"
source_type: "MIGRATION_RECORD"
authority_class: "MIGRATION_EVIDENCE"
owner_project: "Codex"
owner_operation: "Source Governance"
canonical_scope: "Coordinates the Spear Campaign and Evolving Prime campaign from verified construction planning through packet-driven rebuilding, migration closure, recovery proof, and explicit Atlas Prime cutover without granting execution authority."
protected_level: "CRITICAL"
routes_from:
  - "atlas-prime.md"
  - "atlas-aegis.md"
  - "athenas-spear.md"
  - "noctua.md"
  - "migration/atlas-codex/audits/prime-spear-s0-audit-and-freeze-v1.md"
  - "specs/spear/athenas-spear-s1-writer-contract-v1.md"
  - "specs/atlas-prime/codex-to-prime-migration-contract-v1.md"
  - "migration/atlas-codex/README.md"
  - "migration/atlas-codex/migration-map.md"
routes_to:
  - "athenas-spear.md"
  - "tools/spear/operator-runbook.md"
  - "tools/spear/recovery-runbook.md"
  - "specs/spear/athenas-spear-s1-writer-contract-v1.md"
  - "specs/atlas-prime/codex-to-prime-migration-contract-v1.md"
  - "migration/atlas-codex/README.md"
  - "migration/atlas-codex/migration-map.md"
  - "noctua.md"
private_boundary: "This roadmap may contain clean quest plans, public repository identities, clean migration counts, route names, statuses, dependencies, findings, and decision gates only. It must not contain secrets, credentials, tokens, PHI, raw finance or account evidence, private runtime values, IP addresses, network maps, device registers, protected exports, or raw private records."
evidence_boundary: "This roadmap coordinates work but does not replace Atlas Codex, Atlas Prime source, Git history, reconciliation records, original evidence systems, Spear packets or receipts, Noctua reports, pull requests, merge records, generated reports, hostile-test logs, or Phoenix recovery proofs. A Google Docs copy is a readable mirror only and is not durable source truth."
supersedes: []
cleanup_path: "Retain throughout the Atlas Prime Rebuild Quest. Update through versioned roadmap revisions after this first durable version. After explicit cutover and quest closeout, supersede with the final migration receipt and cutover record while retaining this version as historical migration evidence."
last_verified: "2026-06-25"
---

# Atlas Prime Rebuild Quest

## 1. Authority and current state

```text
Quest: Atlas Prime Rebuild
Campaign A: Spear Campaign
Campaign B: Evolving Prime Campaign

Canonical operational source: Jktomy/atlas-codex
Verified Codex main: 9b1811180104ac9020e8bfaffc5a3ee6df692ab1

Successor construction repository: Jktomy/atlas-prime
Verified Prime main: 3ad3d796aaf17f9fa396ac3dbfc099e477d524a8
Prime state: SHADOW

A0: VERIFIED_COMPLETE
A1: VERIFIED_COMPLETE
A2: VERIFIED_COMPLETE
A3: PLAN_REPAIR_REQUIRED
S1 writer activation: NOT AUTHORIZED
Migration execution: NOT AUTHORIZED
Prime promotion: NOT AUTHORIZED
Cutover: NOT AUTHORIZED
```

This roadmap is quest-planning evidence.

### Quest Board hierarchy

```text
Parent Quest: Atlas Prime Rebuild
Child Campaign A: Spear
Child Campaign B: Evolving Prime
Campaign milestones and gates: A0-A7 and B0-B10
```

For Quest Board purposes:

- **Atlas Prime Rebuild** is one parent Quest with one shared completion rule.
- **Spear** and **Evolving Prime** are child Campaigns within that Quest.
- They are not separate top-level Quests and should not be represented as independent Programs.
- The A-series and B-series entries are Campaign milestones, phases, or gates—not additional Quests.
- Tasks, packets, pull requests, audits, decisions, and proofs remain bounded work items beneath the appropriate Campaign.
- The Quest Board should roll Campaign state upward without erasing each Campaign's separate blockers, evidence, or next gate.
- Completing one Campaign does not complete the parent Quest while the other Campaign or any shared cutover obligation remains open.

This roadmap defines the intended Quest Board hierarchy but does not create or mutate a Quest Board record. Durable Quest Board registration remains blocked until the Workboard-to-Quest transition contract and its approved route exist.

It does not:

- activate Prime Spear;
- authorize a workflow run or repository mutation;
- authorize a Spear packet;
- authorize the rejected A3 Preview;
- close M1;
- select an M2 pilot;
- create the disposition ledger;
- modify Workboard, Quest, Golden Wing, Atlas Index, Feather, or another register or generator;
- authorize migration, merge, source promotion, Codex retirement, or cutover.

Atlas Codex remains canonical until an explicit cutover is approved after complete proof.

Atlas Prime remains the proposed successor architecture under construction.

Any Google Docs copy of this roadmap is a readable convenience copy only. The approved GitHub source and its verified lineage control.

## 2. Quest hierarchy and design model

The Spear Campaign builds and proves the machine.

The Evolving Prime Campaign determines and prepares what the machine will build.

Approved Spear packets connect the two Campaigns and advance the parent Quest.

The design hierarchy is:

```text
Atlas goal
-> concrete intended outcome
-> representative packet
-> exact expected transaction evidence
-> minimum safe Spear capability
-> hostile tests
-> harmless proof
-> bounded activation
-> migration batches
```

Packets lead the **what**.

Spear leads the **how safely**.

Atlas goals, source order, protected boundaries, Noctua, Phoenix, and Jayson approval govern both.

Terminology rule:

```text
Quest = the complete strategic objective and final completion condition
Campaign = a major coordinated line of effort within the Quest
Milestone / phase / gate = a bounded stage within one Campaign
Task / packet / PR / audit / proof = an executable or reviewable work item
```

Use “sub-quest” only in informal discussion when needed for readability. Durable source and Quest Board records should use **Campaign** for Spear and Evolving Prime so the hierarchy remains unambiguous.

The Quest must not:

- build a generalized writer without representative transaction requirements;
- design an unlimited packet language and force Spear to support it;
- let implementation convenience redefine Atlas goals;
- treat a valid packet as execution authority;
- treat a merged PR as migration closure;
- treat a Google Doc, chat conclusion, local artifact, or generated projection as canonical source by existence alone.

## 3. Shared final goal

Build a clean, coherent, recoverable, auditable, and restart-safe Atlas Prime that:

- preserves valid Atlas Codex meaning;
- deliberately supersedes obsolete, duplicated, or conflicting meaning;
- eliminates silent duplication, fragmentation, and accidental authority competition;
- keeps original protected evidence authoritative outside GitHub;
- stores only clean source, clean summaries, structured clean state, generated projections, migration evidence, and clean pointers;
- can be reconstructed from durable source without depending on chat memory;
- can be changed through bounded deterministic packets;
- proves packet-to-tree, packet-to-commit, packet-to-PR, and merged-main fidelity;
- can be independently audited by Noctua;
- can be restored and rolled back through Phoenix proof;
- preserves complete predecessor disposition and successor lineage;
- replaces Atlas Codex only after every migration obligation closes and Jayson explicitly approves cutover.

## 4. Governing principles

### 4.1 Source order

Use:

1. current explicit Jayson instruction;
2. current merged Atlas Prime construction doctrine and contracts;
3. current Atlas Codex source for canonical operational meaning;
4. approved migration evidence and reconciliation records;
5. approved original evidence systems;
6. Athena inference, clearly labeled.

Atlas Codex governs current operation until cutover.

Atlas Prime governs the intended successor architecture.

Conflict requires reconciliation, not blind copying.

### 4.2 Evidence classification

Every Quest claim must be classified as one of:

- `VERIFIED_DURABLE_SOURCE`
- `VERIFIED_GIT_HISTORY`
- `VERIFIED_MERGED_MAIN_READBACK`
- `VERIFIED_LOCAL_ARTIFACT`
- `VERIFIED_CHAT_REVIEW`
- `PROPOSED`
- `BLOCKED_PENDING_CONTRACT`
- `NEEDS_JAYSON`
- `UNVERIFIED`

Chat and local evidence may drive planning but do not become durable truth until reviewed and written through an approved route.

### 4.3 Preview before execution

Preview -> Execute is required before:

- source writes;
- workflow or writer activation;
- migration packet execution;
- contract, policy, schema, tool, workflow, or test changes;
- register or generator activation;
- deletion, retirement, move, rename, archive, omission closure, or supersession execution;
- Google Drive creation, replacement, movement, export, or deletion;
- promotion;
- cutover;
- any other durable or external-system action.

### 4.4 Stop before merge

Spear may create a draft pull request only through a proven and approved route.

Spear stops before merge.

Noctua audits.

Jayson decides merge.

Merged-main readback is required before phase closure.

### 4.5 Zero silent loss

Every inventoried Atlas Codex path must receive one final disposition.

A missing row is a migration failure.

An unread file is not an omission.

A private file is not copied merely to make the inventory look complete.

A predecessor is not deleted merely because a successor exists.

A merged PR does not close migration by itself.

### 4.6 Source and generated separation

Authored source and ordinary generated outputs use separate pull requests.

Generated projections report from declared authoritative inputs.

Generated files do not silently become authored authority.

### 4.7 Protected-source boundary

Do not place secrets, credentials, tokens, MFA or recovery codes, private keys, seed phrases, real environment values, PHI, raw finance or account evidence, private runtime values, IP addresses, network maps, device registers, or protected exports into GitHub, Spear packets, review packages, migration records, or readable Google Docs mirrors.

Use clean summaries or clean pointers where appropriate.

## 5. Quest and campaign state vocabulary

Use:

- `NOT_STARTED`
- `READ_ONLY_ANALYSIS`
- `READY_FOR_PREVIEW`
- `PREVIEWED`
- `APPROVED_FOR_EXECUTE`
- `IN_IMPLEMENTATION`
- `IN_PR`
- `AWAITING_AUDIT`
- `MERGED_AWAITING_READBACK`
- `VERIFIED_COMPLETE`
- `PLAN_REPAIR_REQUIRED`
- `REJECTED_FOR_EXECUTION`
- `BLOCKED_PENDING_CONTRACT`
- `BLOCKED_NEEDS_JAYSON`
- `DEFERRED`
- `SUPERSEDED`

A phase is not `VERIFIED_COMPLETE` without durable evidence and every required readback.

# Campaign A — Spear

## 6. Mission

Build, prove, and safely activate the next-generation Athena's Spear in Atlas Prime as a controlled compiler and draft-PR writer for bounded, auditable Atlas changes.

The end-state Spear must:

- receive one exact approved packet and execution envelope;
- authenticate the execution actor, event, repository, workflow source, and approval reference;
- validate the exact repository, branch, remote base, schemas, policies, metadata, paths, target states, and content hashes;
- bind packet, manifest, Preview, approval, branch, commit, PR, and receipt identities;
- construct and validate the entire proposed tree before remote mutation;
- create one deterministic branch and one single-parent commit;
- push without force;
- open exactly one deterministic draft PR;
- verify the server-created PR title, body, base, head, draft state, and lineage;
- preserve a receipt for every success and failure attempt;
- support exact idempotent recovery without permitting collision repair or hidden history rewriting;
- stop before merge;
- never write directly to `main`;
- never self-approve, auto-merge, alter repository settings, broaden packet scope, or promote source truth.

## 7. Completed Spear milestones

### A0 — Codex Spear closeout

State: `VERIFIED_COMPLETE`

Verified outcome:

- generated-report PR #162 passed Atlas Verify after the required human workflow approval;
- PR #162 merged;
- Codex `main` advanced to `9b1811180104ac9020e8bfaffc5a3ee6df692ab1`;
- exactly five files under `generated/` changed;
- merged-main generated-report readback completed;
- no authored governing source changed.

A0 does not prove every Codex Spear route. It closes the identified generated-report residue and preserves the existing guarded route proofs.

### A1 — Prime Spear S0 audit and specification freeze

State: `VERIFIED_COMPLETE`

Verified outcome:

- Prime PR #8 merged;
- merge commit `6e7c61496018d258a9a1b51e98adec2343fc4e1b`;
- exactly one audit/freeze record added;
- S0 remains a non-writing offline compiler;
- writer, migration, promotion, and cutover authority remain denied;
- two low-severity findings were preserved for A3:
  - `A1-F01` synthetic compiler-version fixture drift;
  - `A1-F02` Git target lookup before full path-policy validation.

### A2 — S1 writer contract and design

State: `VERIFIED_COMPLETE`

Verified outcome:

- Prime PR #9 merged;
- merge commit and current Prime `main`:
  `3ad3d796aaf17f9fa396ac3dbfc099e477d524a8`;
- exact merged writer-contract blob:
  `dadf1d83841d3cb6a5a0f6848be6787602ac5a51`;
- owner-only `workflow_dispatch`, GitHub-hosted runner, job-scoped repository `GITHUB_TOKEN`, draft-PR-only behavior, manual merge, Noctua, and recovery gates were specified;
- A1-F01 and A1-F02 were made mandatory implementation closures;
- S1 implementation and activation remained separately gated.

A2 does not authorize implementation, writer activation, packet execution, migration, or cutover.

## 8. A3 disposition after ten-pass red team

### Rejected Preview

```text
Preview SHA-256:
ba64c151eda0f92a3cb42f1265dac4d9862efe7738a1885453f8a61a37c635f3

Source-tree SHA-256:
a046ea09c7de9babd2fc0e5ef2fde60845552f46dcac580e49bd4d46093cb719

Disposition:
REJECTED_FOR_EXECUTION
```

The Preview was never executed.

No rollback, branch cleanup, PR closure, or repository repair is required.

The useful source and design work may be reused only after repair and a new exact Preview.

### Why the Preview was rejected

The ten-pass audit found:

1. **Scope concentration**
   - nineteen files and approximately 4,190 additions combined schemas, activation, hardening, writer code, Git logic, PR logic, workflows, tests, and runbooks before complete Golden Transaction vectors existed.

2. **Incomplete activation authority**
   - the proposed runtime accepted the activation policy alone;
   - it did not require matching destination-policy execution authority;
   - current S0 validation would conflict with a nonempty execution-authorization list unless S0 and S1 validation paths are separated.

3. **Remote-main time-of-check/time-of-use race**
   - the writer checked local `main` but could still push after remote `origin/main` advanced.

4. **Packet identity and concurrency mismatch**
   - workflow concurrency used the compressed-envelope hash rather than repository plus packet ID;
   - one packet ID with changed content could derive multiple branches.

5. **Commit lineage weakness**
   - a crafted two-parent commit with an approved tree and subject but an unapproved body or trailer could be accepted as an idempotent transaction.

6. **PR fidelity weakness**
   - server-created title and body were not verified;
   - the proposed body omitted required evidence fields.

7. **Incomplete failure evidence**
   - a machine-readable receipt was not guaranteed for every PLAN or APPLY failure;
   - upload behavior did not consistently preserve failed-attempt evidence.

8. **Dependency provisioning unresolved**
   - the hosted runner lacked a trusted exact route to provide the pinned dependency closure without introducing a new unapproved supply-chain path.

These findings block the current implementation Preview.

## 9. Revised A3 structure

A3 is now divided into three gates.

### A3-G0 — Golden Transaction Suite

State: `READ_ONLY_ANALYSIS`

Purpose:

Define representative packet-to-transaction vectors before writer implementation controls the design.

This is not a new campaign phase. It is A3's mandatory entry gate.

Required Golden Transactions:

1. one clean ordinary `CREATE_FILE`;
2. one exact `REPLACE_FILE_FULL`;
3. one atomic multi-file transaction;
4. stale local and remote base at every write boundary;
5. stale target blob;
6. same packet ID with changed content;
7. concurrent duplicate dispatch;
8. exact preexisting branch with missing PR;
9. branch collision with changed packet, manifest, Preview, tree, or commit;
10. crafted multi-parent commit;
11. exact subject with modified full commit message or trailer;
12. created PR with mutated title or body;
13. PR API uncertainty after possible server-side creation;
14. protected path, symlink, submodule, malformed path, case collision, and traversal denial;
15. failure receipt at every gate;
16. harmless end-to-end proof vector.

Each vector must define:

- exact packet bytes and SHA-256;
- exact execution envelope;
- exact approved Preview object;
- exact normalized manifest;
- expected branch;
- expected single-parent commit and full commit message;
- expected changed filenames and file hashes;
- expected PR title and complete body;
- expected receipt;
- expected failure code where applicable;
- exact recovery state;
- expected Noctua result.

Exit criteria:

- transaction vectors are complete and reviewable;
- no vector requires unspecified authority;
- every A2 requirement maps to at least one positive or hostile vector;
- packet semantics and engine obligations agree.

### A3a — Contract, hardening, and read-only proof foundation

State: `NOT_STARTED`

Purpose:

Merge the smallest protected-source change needed to make the transaction contract executable as tests without adding write-capable runtime authority.

Expected scope:

- close A1-F01;
- close A1-F02;
- add or repair strict execution-envelope, Preview, and receipt schemas;
- define separate S0 and S1 contract-validation paths;
- define the dual activation contract without activating it;
- add Golden Transaction fixtures and hostile read-only tests;
- add static workflow permission and action-pin tests where useful;
- preserve `EXECUTION_NOT_AUTHORIZED`;
- no writer workflow with usable repository mutation authority.

Required dual activation model:

S1 execution must require all of:

- activation policy enabled;
- activation mode active;
- repository writes authorized;
- exact approved activation reference;
- destination policy independently authorizes the same bounded operations;
- current contract compatibility;
- exact actor, event, repository, workflow, and base;
- all authorities agree without widening one another.

One gate alone must never activate writing.

Exit criteria:

- complete existing and new test suite passes in the target dependency environment;
- S0 remains non-writing;
- every A3-G0 vector compiles or fails exactly as specified;
- no repository mutation route exists;
- PR is manually merged and read back after Noctua.

### A3b — Disabled writer and recovery implementation

State: `NOT_STARTED`

Purpose:

Implement the writer only after A3a transaction vectors and contracts are durable.

Required implementation repairs:

- reverify remote `main` before branch creation, before push, and before PR creation;
- use repository plus packet ID as the concurrency identity;
- prevent a second transaction for a reused packet ID with changed hashes;
- require exactly one commit parent;
- require exact full commit message;
- verify author and committer policy;
- verify exact commit tree and changed paths;
- verify server-created PR title, body, base, head, draft state, and head SHA;
- include every A2-required PR evidence field;
- create a redacted receipt for every attempt;
- upload failure evidence with unconditional failure-safe behavior;
- distinguish definite PR absence from uncertain post-request state;
- provide deterministic idempotent branch-pushed/PR-missing recovery;
- preserve no-force, no-main, no-merge, no-settings-change boundaries;
- remain disabled after merge.

Dependency provisioning must receive its own reviewed solution before the hosted workflow can be treated as runnable.

Exit criteria:

- all A3-G0 positive and hostile transactions pass;
- complete repository suite passes;
- implementation PR changes only the approved protected source;
- activation remains disabled;
- Noctua passes;
- Jayson manually merges;
- merged-main readback proves the disabled state.

## 10. Remaining Spear phases

### A4 — Harmless end-to-end proof

State: `NOT_STARTED`

Purpose:

Use one approved non-governing ordinary `projects/` packet to prove:

- exact Preview binding;
- authenticated manual dispatch;
- PLAN/APPLY separation;
- remote-base freshness;
- one branch;
- one single-parent commit;
- one exact draft PR;
- complete receipt;
- manual check approval;
- Noctua packet-to-PR fidelity;
- Jayson manual merge;
- merged-main readback;
- isolated revert planning and replacement-PR recovery.

The harmless proof grants no migration, protected-source, register, generator, or expanded-operation authority.

### A5 — Route qualification

State: `NOT_STARTED`

Purpose:

Qualify only the route families Evolving Prime actually requires.

Candidate route families:

- ordinary authored-source route;
- migration-evidence route;
- protected-source route;
- structured-register route;
- generator route;
- Feather/lifecycle route.

Each route requires:

- exact operation contract;
- path and size limits;
- Golden Transactions;
- hostile tests;
- proof packet;
- Noctua;
- recovery;
- separate activation.

### A6 — Bounded activation for Evolving Prime

State: `NOT_STARTED`

Purpose:

Activate only proven route classes and operation sets.

Activation must not:

- enable every registered future operation;
- broaden ordinary packet paths;
- activate migration by implication;
- change merge authority;
- bypass Noctua or Phoenix;
- make Atlas Prime canonical.

### A7 — Maintenance handoff

State: `NOT_STARTED`

Purpose:

Close the construction campaign into a maintainable source-change system with:

- documented route ownership;
- versioning and supersession;
- stable dependency provisioning;
- audit and observability;
- failure-receipt retention;
- branch and PR lifecycle policy;
- recovery exercises;
- maintenance Golden Transactions;
- safe deactivation and rollback.

# Campaign B — Evolving Prime

## 11. Mission

Reconcile current valid Atlas Codex meaning with the approved Atlas Prime architecture and construct the successor repository through bounded, reviewable, recoverable transactions.

Evolving Prime must determine:

- what meaning survives;
- what is reorganized;
- what is remodeled;
- what is split or merged;
- what is retained as history;
- what remains private;
- what is omitted with reason;
- what requires a structured register or generator;
- what requires a protected-source route;
- what remains blocked;
- and what needs Jayson.

It does not wait for S1 to perform all read-only reconciliation work.

## 12. Current Evolving Prime state

### Durable control plane

State: `VERIFIED_COMPLETE`

Durable Prime source includes:

- Codex-to-Prime migration contract;
- migration evidence hub;
- exact 349-path source inventory;
- inventory schema and preflight audit;
- migration map with waves M0-M9;
- eighteen preliminary collision groups;
- reconciliation template.

The durable migration map remains planning evidence only.

It does not authorize content movement, final dispositions, packet execution, writer activation, retirement, promotion, or cutover.

### Local and chat-reviewed evidence

State: `VERIFIED_LOCAL_ARTIFACT` plus `VERIFIED_CHAT_REVIEW`

Current supporting evidence records:

- 18 collision groups;
- 144 collision memberships;
- 91 unique source paths in collision groups;
- 14 groups reviewed as `RESOLVED_FOR_MAP`;
- 4 groups retained as `BLOCKED_PENDING_CONTRACT`;
- 0 collision-layer `NEEDS_JAYSON`;
- 182 non-collision high-consequence records;
- 4 human-reviewed;
- 178 still unreviewed;
- one proposed twenty-file collision-evidence package;
- a known outbound-route serialization defect in one rendered export.

This evidence is not yet durable Prime source.

The malformed outbound-route rendering must not be copied into durable source.

### Contract blockers

The following remain blocked pending dedicated contracts:

1. Golden Wing candidate register;
2. Golden Wing append-only event register;
3. Atlas Index generator;
4. Workboard-to-Quest transition.

These contracts may be designed and audited before writer activation.

Their eventual writes require the appropriate qualified route.

## 13. Evolving Prime phases

### B0 — Migration control plane

State: `VERIFIED_COMPLETE`

Maintain the inventory, map, hub, schema, audit, and reconciliation template against current heads.

### B1 — Semantic reconciliation

State: `READ_ONLY_ANALYSIS`

Remaining work:

- durably preserve corrected collision evidence through an approved migration-evidence route;
- review the remaining 178 non-collision high-consequence records;
- resolve or explicitly block every high-consequence disposition;
- draft the four missing contracts;
- prevent mechanical inventory classification from becoming semantic closure;
- preserve chat-only conclusions as labeled planning evidence until durable review.

B1 may continue in parallel with A3-G0 and A3a.

B1 does not authorize packet execution or target-source changes.

### B2 — Disposition ledger

State: `NOT_STARTED`

Entry gate:

- B1 semantic decisions sufficiently closed;
- ledger schema and production model approved;
- stable record identity and lineage defined.

Decision D-B2-01 remains open:

- directly authored and schema-validated; or
- deterministically generated from accepted reconciliation records.

Recommended direction:

Generate the ledger deterministically from accepted reconciliation records while preserving stable source-record IDs and generation receipts.

### B3 — Packet architecture

State: `READ_ONLY_ANALYSIS`

Purpose:

Group reconciled source into bounded packet families that match proven route classes.

Packet families must be driven by actual Atlas outcomes and Golden Transactions, not by arbitrary implementation limits.

Packet drafting may proceed before activation.

Execution may not.

### B4 — Collision evidence package

State: `BLOCKED_PENDING_CONTRACT`

The proposed twenty-file evidence package cannot use the current ordinary S0 route because:

- ordinary packets permit at most five operations;
- ordinary paths are limited to Markdown under `projects/`;
- `migration/` is denied;
- execution authority is empty.

Decision D-A5-01 remains open:

- one route-specific twenty-file atomic migration-evidence transaction; or
- a dependency-ordered smaller bundle with explicit intermediate-state and recovery rules.

Recommended direction:

Preserve the ordinary five-operation limit and qualify a dedicated migration-evidence route for the exact twenty-file atomic evidence set.

No execution occurs until A5 proves that route.

### B5 — Low-risk construction

State: `NOT_STARTED`

Begin only after:

- harmless Spear proof;
- ordinary route activation;
- M1 readiness;
- one M2 pilot is selected through a separate Preview;
- exact packet and recovery evidence are approved.

### B6 — Core reconstruction

State: `NOT_STARTED`

Reconcile root doctrine, governance, source order, protocols, and critical authored source through protected-source routes.

No blind overwrite.

### B7 — Registers and generators

State: `NOT_STARTED`

Transition Quest, Workboard, Golden Wing, Atlas Index, Feather, and other structured or generated surfaces only after dedicated contracts and route proof.

### B8 — Complete lineage closure

State: `NOT_STARTED`

Every Codex inventory row must have:

- final disposition;
- target or retention outcome;
- route;
- packet or protected-source identity when executed;
- PR and merge lineage;
- Noctua result;
- final readback and target hash;
- retained predecessor evidence;
- unresolved obligation closed or explicitly accepted.

### B9 — Readiness and cutover

State: `NOT_STARTED`

Requires:

- repository-wide Noctua audit;
- Phoenix isolated restore;
- rollback proof;
- startup and continuity proof;
- source and generated reproducibility;
- no open inventory path;
- no unresolved critical Decision Box;
- Codex retention plan;
- explicit Jayson cutover approval.

### B10 — Quest closeout

State: `NOT_STARTED`

Produce final migration receipt, source-order transition, retention record, maintenance handoff, and archive-safe closeout.

## 14. Cross-campaign dependency map

| Evolving Prime activity | May proceed before S1 activation? | Required Spear state |
|---|---:|---|
| Inventory and map audit | Yes | None |
| Collision reconciliation | Yes | None |
| Non-collision semantic review | Yes | None |
| Contract drafting | Yes | None |
| Exact source drafting | Yes | None |
| Golden Transaction design | Yes | S0 and A2 contracts |
| Packet drafting | Yes | S0 compile where supported |
| Ordinary S0 dry-run | Yes | Current S0 |
| Durable roadmap creation | Yes, by separate migration-evidence PR | No ordinary S0 route |
| Twenty-file collision evidence execution | No | Qualified migration-evidence route |
| Ordinary low-risk pilot | No | A4 proof and bounded activation |
| Root doctrine replacement | No | Protected-source route |
| Golden Wing and Quest writes | No | Structured-register route |
| Atlas Index generation | No | Generator route |
| Feather archive creation or append | No | Feather/lifecycle route |
| Cutover | No | Complete Quest proof and explicit approval |

## 15. Updated critical path

```text
A0 Codex Spear closeout — VERIFIED_COMPLETE
        ↓
A1 Prime S0 audit and freeze — VERIFIED_COMPLETE
        ↓
A2 S1 writer contract — VERIFIED_COMPLETE
        ↓
A3-G0 Golden Transaction Suite
        ↓
A3a contract, hardening, and read-only proof foundation
        ↓
A3b disabled writer and recovery implementation
        ↓
A4 harmless end-to-end proof
        ↓
A5 route qualification
        ↓
B4 collision evidence transaction
        ↓
B1 remaining reconciliation and contract closure
        ↓
B2 disposition ledger
        ↓
B3 bounded packet families
        ↓
B5-B7 Prime construction
        ↓
B8 complete lineage closure
        ↓
B9 readiness audit and explicit cutover
        ↓
B10 Quest closeout
```

Parallel read-only path:

```text
inventory and map maintenance
-> collision reconciliation
-> non-collision review
-> blocker-contract design
-> exact source drafting
-> packet drafting
-> S0 compilation where supported
-> Noctua planning review
```

## 16. Decision register

### Resolved

**D-A2-01 — S1 execution environment**

Resolved direction:

- owner-only `workflow_dispatch`;
- GitHub-hosted runner;
- job-scoped repository `GITHUB_TOKEN`;
- draft-PR-only;
- no direct-main, force-push, auto-merge, or merge authority.

Implementation remains unactivated.

**D-A3-01 — A3 implementation shape**

Resolved after red team:

- do not execute the nineteen-file Preview;
- require A3-G0;
- split contract/hardening from disabled writer implementation.

### Open

**D-A3-02 — Exact dual activation contract**

Define the precise relationship between:

- activation policy;
- destination-policy execution authority;
- S0 validation;
- S1 validation;
- contract compatibility;
- activation reference;
- allowed operations.

One authority surface alone must not activate writing.

**D-A3-03 — Trusted dependency provisioning**

Choose a reviewed exact dependency route for GitHub-hosted runners without floating installs, unreviewed network access, or source-stored secrets.

**D-A5-01 — Twenty-file migration-evidence transaction**

Choose the exact atomic route or dependency-ordered bundle after Golden Transaction and recovery proof.

**D-B2-01 — Disposition-ledger production model**

Choose direct authorship or deterministic generation from accepted reconciliation records.

No decision is hidden inside an execution packet.

## 17. Risk and red-team register

| Risk | Prevention | Detection | Stop condition | Recovery |
|---|---|---|---|---|
| Building writer before transaction requirements | A3-G0 Golden Transactions | Contract-to-vector coverage | Missing expected transaction evidence | Return to A3-G0 |
| Confusing Codex and Prime Spear | Name repository, phase, and contract in every artifact | Source/head audit | Ambiguous Spear claim | Correct artifact and rerun review |
| Calling S0 a writer | Preserve `EXECUTION_NOT_AUTHORIZED` | Receipt and code audit | Write claim without activation | Reclassify and block |
| Single-file activation bypass | Dual policy agreement and separate S1 validation | Hostile one-gate tests | Either gate alone permits write | Disable and repair contract |
| Remote-main race | Verify remote base at every write boundary | Hostile TOCTOU tests | Remote base mismatch | Stop; new Preview required |
| Duplicate packet identity | Repository plus packet-ID concurrency and durable identity check | Concurrent altered-packet tests | Reused packet ID with changed hashes | Block as collision |
| Crafted commit accepted | Exact one-parent and full-message verification | Hostile commit objects | Parent count or message mismatch | Preserve branch; report collision |
| Mutated PR metadata accepted | Server readback of title, body, base, head, draft state | Hostile API mock | Any PR metadata mismatch | Stop; preserve uncertain state |
| Lost failure evidence | Receipt for every attempt and failure-safe upload | Workflow failure tests | Missing receipt | Stop activation |
| Dependency supply-chain drift | Exact reviewed provisioning | Version and source checks | Missing or mismatched dependency | No writer run |
| Mechanical classification treated as closure | Human semantic reconciliation | Ledger/reconciliation comparison | Missing preserved/remodeled meaning | Return item to B1 |
| Premature M2 selection | Keep pilot behind B1 and A4/A5 | Migration-map audit | Named pilot before gate | Remove selection |
| Source/generated mixing | Separate lanes and PRs | Filename audit | Mixed PR | Split before merge |
| Unsafe full replacement | Complete reads and visible diff | Deletion and heading checks | Silent meaning loss possible | Redesign or use bounded update |
| Chat promoted silently | Evidence labels and provenance | Source-origin audit | Chat-only claim presented as durable | Reclassify |
| Protected evidence leakage | Clean-pointer boundary | Automated and human scan | Protected finding | Stop and relocate |
| Merge treated as closure | Mandatory merged-main readback | Lineage audit | Missing final readback | Keep phase open |
| Contractless register activation | Dedicated contract and route | Dependency audit | Missing register/generator contract | Block |
| Packet scope expansion | Exact manifest and Preview | Packet-to-PR comparison | Unexpected path or operation | Abort |
| Premature cutover | Explicit cutover checklist | Repository-wide audit | Open path or failed restore | Keep Codex canonical |

## 18. Current dashboard

### Spear Campaign

**Verified complete**

- A0 Codex Spear closeout
- A1 Prime S0 audit and freeze
- A2 S1 writer contract

**Rejected**

- A3 Preview `ba64c151...` — never execute

**Active planning**

- A3-G0 Golden Transaction Suite
- A3a contract and hardening design
- dual activation repair
- dependency-provisioning decision

**Not authorized**

- S1 writer execution
- packet execution
- migration
- promotion
- cutover

### Evolving Prime

**Durable**

- 349-path inventory and schema
- preflight audit
- migration contract
- migration hub
- migration map
- reconciliation template

**Local/chat-reviewed, not yet durable**

- collision semantic package
- fourteen resolved collision groups
- four contract-blocked groups
- twenty-file evidence package
- four non-collision reviews
- A3 ten-pass red-team evidence

**Remaining**

- 178 non-collision high-consequence reviews
- four blocker contracts
- corrected durable collision evidence
- disposition ledger
- M2 pilot selection
- all migration execution and closure

## 19. Immediate next safe actions

1. Review and durably create this roadmap as one migration-evidence file.
2. After merged-main readback, update the canonical Atlas Active Workboard through a separate Codex source PR.
3. Prepare A3-G0 Golden Transaction Suite as an exact Preview.
4. Prepare A3a only after Golden Transaction requirements are frozen.
5. Continue B1 read-only semantic review and blocker-contract design in parallel.
6. Do not execute the rejected A3 Preview.
7. Do not select M2 or execute the twenty-file collision package.
8. Do not activate S1, migrate source, promote Prime, retire Codex, or cut over.

## 20. Restart-safe continuity

```text
Quest: Atlas Prime Rebuild
Lane: PLAN -> PREVIEW

Codex main:
9b1811180104ac9020e8bfaffc5a3ee6df692ab1

Prime main:
3ad3d796aaf17f9fa396ac3dbfc099e477d524a8

Completed:
A0, A1, A2

Rejected:
A3 Preview ba64c151eda0f92a3cb42f1265dac4d9862efe7738a1885453f8a61a37c635f3

Next:
A3-G0 Golden Transaction Suite

Parallel:
B1 semantic reconciliation and four blocker contracts

Hard stops:
No S1 activation
No packet execution
No migration
No M2 pilot
No disposition ledger
No register or generator activation
No source promotion
No cutover
```

## 21. Completion rule

The Atlas Prime Rebuild Quest is complete only when:

- required Spear routes are proven, bounded, recoverable, and maintainable;
- every Codex path is closed;
- every Prime source has verified lineage;
- all required registers and generators operate under contracts;
- source and generated outputs are reproducible;
- all packet, receipt, PR, merge, and readback lineage is complete;
- Noctua repository-wide audit passes;
- Phoenix restore and rollback pass;
- startup and continuity pass;
- Codex retention is defined;
- Jayson explicitly approves cutover;
- final migration and closeout receipts are durable.
