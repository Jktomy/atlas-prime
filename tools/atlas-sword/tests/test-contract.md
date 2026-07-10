# Atlas Oathbringer Framework Test Contract

The reusable framework is production-active because the required source tests and live AJ-04 through AJ-06 acceptance journeys passed on their stated platforms. Future changes must preserve these controls and re-prove any altered boundary.

## Source-adoption tests

These remain mandatory for every source candidate that changes the Oathbringer framework:

| Test | Windows PowerShell 7 | Linux PowerShell 7 | Python 3 |
|---|---:|---:|---:|
| PowerShell AST parser preflight | Required | Required | N/A |
| Audit-only runner, valid Build example | Required | Required | N/A |
| Audit-only runner, valid Execute example | Required | Required | N/A |
| Audit-only runner, valid Recovery example | Required | Required | N/A |
| Production launcher resolves audit and production adapters | Required | Required | N/A |
| Production mission v2 validation | N/A | N/A | Required |
| Mocked GitHub-native BUILD | N/A | N/A | Required |
| Mocked GitHub-native REPAIR | N/A | N/A | Required |
| Mocked GitHub-native EXECUTE | N/A | N/A | Required |
| Exact final path-set verification | N/A | N/A | Required |
| Unsafe payload traversal rejection | N/A | N/A | Required |
| Audit/head mismatch rejection | N/A | N/A | Required |
| UTF-8 payload round trip | Required | Required | Required |
| Native argument-array preservation | Required | Required | N/A |
| Static source checks | N/A | N/A | Required |
| Runtime byproduct exclusion | N/A | N/A | Required |

## Audit-contract fixtures

The schema `1.2` audit contract must continue to prove:

- root and recursive GitHub path-filter semantics;
- exact workflow source-blob declarations;
- `REQUIRED` versus `NOT_APPLICABLE`;
- applicable workflow success and failure;
- bounded missing-workflow appearance failure;
- bounded incomplete-workflow timeout;
- duplicate workflow-rule rejection;
- exact workflow name, `pull_request` event, and head SHA filtering;
- same-run refresh and newer-run precedence;
- exact untracked `ADD` enumeration for clone compatibility;
- complete candidate path-set audit planning;
- stage entry before an operation begins;
- stage-aware normal failure and operator-interrupt receipt classification;
- atomic JSON receipt write and SHA-256 sidecar creation;
- bounded local retry for transient Windows receipt replacement locks only;
- parseable JSON mode;
- persistent interactive final display without automatic exit or second confirmation;
- explicit completion flags;
- no automatic retry or rollback.

## Production-adapter source fixtures

The schema `2.0` GitHub-native adapter must prove without live mutation:

- exact live base, branch, pull-request, and source-blob lock validation;
- branch and pull-request absence checks for BUILD;
- safe package-relative payload resolution;
- complete payload SHA-256 verification;
- GitHub blob construction;
- complete candidate-tree construction;
- exact final changed-path equality;
- one single-parent candidate commit;
- BUILD branch creation and draft pull request;
- REPAIR fast-forward-only ref update with no force;
- exact remote branch, commit, PR, and path readback;
- path-applicable exact-head workflow polling;
- success, failure, interruption, and partial-state receipts;
- EXECUTE independent GREEN audit binding;
- ready transition without head movement;
- exact-head merge;
- merged pull-request and canonical branch readback;
- no token persistence, direct-main write, force push, blind retry, rollback, or branch deletion.

## Live production acceptance

Wave 3 proved:

### AJ-04 — BUILD

- one harmless sealed multi-file Sword;
- one PowerShell invocation;
- truthful stage and plan-position percentage display;
- authenticated GitHub-native transaction;
- one exact single-parent commit;
- one new branch;
- one draft pull request;
- exact remote path and payload readback;
- applicable CI;
- durable receipt and SHA-256 sidecar.

### AJ-05 — REPAIR

- exact current harmless PR head;
- one repaired complete candidate;
- one child commit;
- fast-forward-only branch update;
- exact amended-head readback;
- applicable CI;
- durable receipt.

### AJ-06 — EXECUTE

- separate explicit Execute authorization;
- independently audited exact head;
- applicable CI green;
- exact-head ready and squash merge;
- merged-main readback;
- durable receipt.

All three live journeys passed and were independently reconciled. CAP-017 is `REPLACED` and `ACTIVE`; the durable evidence record is `proof/oathbringer-production-acceptance-r01.md`.

## Acceptance record

Every result must identify:

- exact framework commit;
- platform and version;
- test command;
- pass/fail result;
- sanitized output;
- exact source, branch, PR, and head when applicable;
- receipt and sidecar SHA-256;
- absence of undeclared source or GitHub mutation.
