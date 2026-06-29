---
title: Spear Transaction and Receipt Contract v1
atlas_id: spear.transaction-receipt-contract.v1
format_version: "1.0"
status: PROPOSED
source_type: SPECIFICATION
authority_class: TOOL_CONTRACT
owner_project: Codex
owner_operation: Athena's Spear
canonical_scope: Defines the Gate 3 runner-neutral transaction, repository subtransaction, stage authority record, Build receipt, Execute receipt, Noctua profile, fixture expectations, and recovery semantics without granting writer or merge authority.
protected_level: CRITICAL
routes_from:
  - specs/spear/spear-execution-convergence-v1.md
  - specs/spear/spear-capability-lifecycle-v1.md
  - tools/spear/operator-runbook.md
  - tools/spear/recovery-runbook.md
routes_to:
  - schemas/spear/spear-transaction-v1.schema.json
  - schemas/spear/spear-build-receipt-v1.schema.json
  - schemas/spear/spear-execute-receipt-v1.schema.json
  - profiles/noctua/spear-transaction-v1.json
private_boundary: This contract may contain clean repository identities, hashes, branch and pull-request metadata, route names, limits, tests, and recovery states only. It must not contain credentials, tokens, PHI, raw finance or account evidence, private runtime values, network maps, device registers, real environment values, unrestricted terminal transcripts, or protected exports.
evidence_boundary: This contract and its fixtures define required semantics. Arrow packages, local receipts, workflow runs, pull requests, commits, Noctua reports, merged-main readback, and recovery observations remain separate evidence.
supersedes: []
cleanup_path: Retain as the Gate 3 contract baseline. Breaking changes require a new major version and separately reviewed compatibility and recovery treatment.
last_verified: 2026-06-29
---

# Spear Transaction and Receipt Contract v1

## 1. Status and non-authority

Status: PROPOSED tool contract.

This source defines data contracts only. It does not activate S1, authorize a branch, commit, push, draft pull request, merge, Arrow firing, Artemis operation, migration, promotion, retirement, deletion, Google Drive action, or cutover.

## 2. Runner-neutral transaction

One immutable transaction describes one mission independently of the selected execution adapter.

It binds:

- one transaction and mission identity;
- one controlling Preview identity and SHA-256;
- one Build-stage authority record;
- one or more exact repository subtransactions;
- exact bases, branches, commit messages, pull-request metadata, paths, payload members, candidate hashes, Git blob identities, and byte counts;
- required tests and Noctua profile;
- cross-repository order and partial-state behavior;
- recovery states and forbidden actions;
- the rule that Execute requires a new authority record, exact audited pull-request heads, and a separately sealed Arrow.

The transaction may not embed caller-selected executable code, credentials, arbitrary commands, hidden policy, or authority-expanding instructions.

## 3. Repository subtransaction

Each repository subtransaction is independently exact and names:

- repository and base branch;
- expected base commit;
- deterministic branch;
- exact commit message;
- exact draft pull-request title and body hash;
- complete ordered operation inventory;
- expected absence or exact current blob identity;
- package payload path, SHA-256, Git blob SHA-1, and byte count;
- stop-before-merge state.

A multi-repository transaction is coordinated but not atomic. Earlier successful repository state is preserved when a later repository blocks.

## 4. Stage authority record

Every Arrow carries one immutable authority record.

### Build authority

Build authority may permit only:

- state verification;
- deterministic branch creation;
- exact candidate writes;
- staging and one bounded commit;
- push without force;
- one draft pull request per repository;
- exact readback and receipt emission.

It must deny merge, auto-merge, direct-main write, force-push, branch deletion, pull-request closure, cleanup, migration, activation, promotion, retirement, deletion, and cutover.

### Execute authority

Execute authority is a new record created only after Build receipt audit and Noctua acceptance. It binds exact pull-request numbers and audited head SHAs.

It may permit only:

- exact-head and current-state verification;
- approved merge in the declared order;
- merged-main readback;
- Execute receipt emission.

It may not repair, rewrite, rebase, force-push, create a replacement pull request, broaden files, activate a profile, migrate content, promote Prime, retire Codex, delete evidence, or cut over.

## 5. Build receipt

A Build receipt records:

- transaction, mission, Arrow, runner, and authority identities;
- package and candidate-set hashes;
- observed repository bases;
- branch, commit, changed-file, pull-request, and head identities when reached;
- result: `PASS`, `BLOCKED`, `PARTIAL`, or `FAILED_WITH_RECEIPT`;
- last completed gate;
- redacted diagnostics;
- explicit confirmation that forbidden actions were not performed.

A `PASS` means every declared draft pull request exists at the exact expected head and shape. It grants no merge authority.

## 6. Execute receipt

An Execute receipt records:

- the same mission and transaction lineage;
- the exact Build receipt and Noctua report hashes;
- the Execute authority identity;
- every approved pull request number and audited head SHA;
- merge commit and final `main` readback when reached;
- result and last completed gate;
- forbidden-action confirmation.

A `PASS` means the approved merges and final readback completed exactly. It does not activate S1, Artemis, migration, promotion, retirement, or cutover.

## 7. Recovery states

At minimum, runners must distinguish:

- `NOT_STARTED`;
- `LOCAL_VALIDATION_COMPLETE`;
- `BRANCH_CREATED`;
- `COMMIT_CREATED`;
- `COMMIT_PUSHED`;
- `BRANCH_PUSHED_PR_MISSING`;
- `PR_STATE_UNCERTAIN`;
- `DRAFT_PR_VERIFIED`;
- `PARTIAL_REPOSITORY_SUCCESS`;
- `MERGED_READBACK_INCOMPLETE`;
- `COMPLETE`.

Reruns may resume only the missing permitted action after exact readback. They must not reset successful state, force-push, delete, close, duplicate, or silently repair.

## 8. Noctua acceptance

The Gate 3 Noctua profile checks:

- source order and controlling Preview;
- schema and fixture validity;
- exact repository, base, branch, path, and candidate identities;
- stage authority separation;
- Build and Execute receipt fidelity;
- pull-request shape and exact-head binding;
- partial-state and recovery semantics;
- protected-boundary compliance;
- absence of hidden execution or expanded authority.

Noctua acceptance authorizes only the next separately approved stage.

## 9. Fixture rule

Gate 3 contains valid and invalid fixtures. Invalid fixtures must fail for the intended reason without weakening the schema or accepting alternate authority.

## 10. Gate boundary

Gate 3 is complete only after:

1. the contract files and fixtures are merged;
2. merged-main readback confirms exact lineage;
3. the separate continuity update records Gate 3 complete and Gate 4 next.

Gate 3 does not itself prove either execution adapter. Those proofs begin at Gates 4 and 5.
