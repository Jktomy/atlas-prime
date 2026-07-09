# Atlas Oathbringer Framework Test Contract

The reusable framework is not production-eligible until all required tests pass on
their stated platforms.

## Source-adoption tests

These must pass before the source candidate is eligible for Noctua:

| Test | Windows PowerShell 7 | Linux PowerShell 7 | Python 3 |
|---|---:|---:|---:|
| PowerShell AST parser preflight | Required | Required | N/A |
| Audit-only runner, valid Build example | Required | Required | N/A |
| Audit-only runner, valid Execute example | Required | Required | N/A |
| Audit-only runner, valid Recovery example | Required | Required | N/A |
| Invalid mission rejected by JSON Schema | Required | Required | N/A |
| UTF-8 payload round trip | Required | Required | Required |
| Native argument-array preservation | Required | Required | N/A |
| Static source checks | N/A | N/A | Required |
| Deterministic package rebuild | N/A | N/A | Required |
| Runtime byproduct exclusion | N/A | N/A | Required |

## Oathbringer contract fixtures

The audit contract must prove:

- root and recursive GitHub path-filter semantics;
- exact workflow source-blob declarations;
- `REQUIRED` versus `NOT_APPLICABLE`;
- applicable workflow success;
- applicable workflow failure;
- bounded missing-workflow appearance failure;
- bounded incomplete-workflow timeout;
- duplicate workflow-rule rejection;
- exact workflow name, `pull_request` event, and head SHA filtering;
- same-run refresh and newer-run precedence;
- exact untracked `ADD` enumeration;
- intent-to-add only after exact untracked-set proof;
- complete candidate path-set audit;
- stage entry before an operation begins;
- stage-aware normal failure receipt classification;
- stage-aware operator-interrupt receipt classification and exit code `130`;
- atomic JSON receipt write and SHA-256 sidecar creation;
- bounded local retry for transient Windows rename/replace locks only;
- parseable JSON mode;
- persistent interactive final display without automatic exit or second confirmation;
- explicit completion flags;
- no automatic retry or rollback.

## Future production-adapter fixtures

These remain proof-gated and are not implemented by the audit-only framework:

- exact live main and source-blob locks;
- branch and pull-request absence queries;
- current-directory-independent launch;
- fresh clone with command-scoped Windows Git settings;
- stale-base safe stop;
- `git diff --check` blocks commit;
- single-parent candidate commit;
- non-force push;
- draft pull request;
- exact remote readback;
- path-applicable workflow polling;
- stopped receipt and successful receipt;
- partial-state recovery without blind replay;
- exact-head merge;
- ordered merge-parent and merged-main proof;
- separately authorized branch deletion.

## Acceptance

A result must identify:

- exact framework commit;
- platform and version;
- test command;
- pass/fail result;
- sanitized output;
- absence of undeclared source or GitHub mutation.
