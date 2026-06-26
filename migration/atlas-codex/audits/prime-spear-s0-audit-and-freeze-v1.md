---
title: "Prime Spear S0 Audit and Specification Freeze v1"
atlas_id: "atlas-prime.spear.s0.audit-freeze.v1"
format_version: "1.0"
status: "PROPOSED"
source_type: "MIGRATION_RECORD"
authority_class: "MIGRATION_EVIDENCE"
owner_project: "Codex"
owner_operation: "Athena's Spear"
canonical_scope: "Records the verified implementation boundary, controlling contract identities, test evidence, known limitations, deferred hardening notes, and non-writing freeze state of Atlas Prime Spear S0 before any S1 writer design."
protected_level: "CRITICAL"
routes_from:
  - "athenas-spear.md"
  - "atlas-aegis.md"
  - "specs/atlas-prime/codex-to-prime-migration-contract-v1.md"
  - "policies/destination/atlas-prime-destination-policy-v0.2.yaml"
  - "policies/protected-paths/protected-paths-v0.2.yaml"
  - "policies/operations/spear/spear-policy-v1.yaml"
  - "schemas/spear/spear-packet-v1.schema.json"
routes_to:
  - "tools/spear/operator-runbook.md"
  - "tools/spear/recovery-runbook.md"
  - "migration/atlas-codex/README.md"
private_boundary: "This audit may contain clean repository paths, public commit and blob identities, contract versions, test descriptions, and bounded implementation findings only. It must not contain secrets, credentials, tokens, PHI, raw finance or account evidence, private runtime values, IP addresses, network maps, device registers, protected exports, or raw private records."
evidence_boundary: "This audit records a source and implementation review. Git history, pull requests, exact repository files, test logs, compiler receipts, generated artifacts, Noctua reports, and recovery evidence remain distinct evidence sources."
supersedes: []
cleanup_path: "Retain as the S0 freeze record. Supersede only through a later reviewed Spear audit when the compiler contract changes or S1 is approved. Do not treat this record as writer activation, migration authority, source promotion, or cutover."
last_verified: "2026-06-25"
---

# Prime Spear S0 Audit and Specification Freeze v1

## 1. Authority and outcome

```text
Repository: Jktomy/atlas-prime
Verified main: f408a2551d4a169a045405b3d0000605e432c23f
S0 merge commit: d2a8a6d68e24456b1a20925429f1d445260e1109
S0 PR head: 92036dac6456cc7afcc635cd5073409ab8f6c109
S0 PR: #3
Implementation classification: PROBATIONARY OFFLINE COMPILER
Writer authority: NOT AUTHORIZED
Migration authority: NOT AUTHORIZED
Cutover authority: NOT AUTHORIZED
Freeze outcome: SAFE TO FREEZE AS S0
Activation outcome: NOT SAFE OR AUTHORIZED TO ACTIVATE AS A WRITER
```

Atlas Codex remains canonical. Atlas Prime remains `SHADOW`.

This audit freezes what S0 currently is. It does not expand S0, activate S1, approve a packet, create a writer, authorize migration, or promote Atlas Prime.

## 2. Verified source boundary

S0 entered Prime through PR #3 as exactly 29 files:

1. `athenas-spear.md`
2. `policies/operations/spear/spear-policy-v1.yaml`
3. `schemas/spear/spear-packet-v1.schema.json`
4. `tests/__init__.py`
5. `tests/fixtures/spear/invalid/invalid-packet-id.json`
6. `tests/fixtures/spear/invalid/protected-path.json`
7. `tests/fixtures/spear/valid-create.json`
8. `tests/fixtures/spear/valid-multi.json`
9. `tests/fixtures/spear/valid-update.json`
10. `tests/spear/__init__.py`
11. `tests/spear/helpers.py`
12. `tests/spear/test_compile.py`
13. `tests/spear/test_final_gates.py`
14. `tests/spear/test_policy.py`
15. `tests/spear/test_policy_provenance.py`
16. `tests/spear/test_reproducibility.py`
17. `tests/spear/test_schema.py`
18. `tests/spear/test_security.py`
19. `tests/spear/test_source_metadata.py`
20. `tools/spear/__init__.py`
21. `tools/spear/cli.py`
22. `tools/spear/compile.py`
23. `tools/spear/dependencies-v1.toml`
24. `tools/spear/git_adapter.py`
25. `tools/spear/models.py`
26. `tools/spear/operator-runbook.md`
27. `tools/spear/policy.py`
28. `tools/spear/recovery-runbook.md`
29. `tools/spear/validate.py`

Four later Prime commits advanced migration planning. Compared with the S0 merge commit, only `athenas-spear.md` changed inside the original 29-file S0 boundary. The implementation, packet schema, Spear overlay, tests, fixtures, dependency contract, and runbooks remain unchanged from the merged S0 baseline.

The later `athenas-spear.md` change adds routing to the Codex-to-Prime migration contract, migration hub, and reconciliation template. It does not grant writer authority.

## 3. Controlling identities at the verified Prime head

| Contract or implementation surface | Current Git blob SHA |
|---|---|
| `athenas-spear.md` | `8a8c84f16e0001e712defdd7f1227a4b6f31ca19` |
| `policies/operations/spear/spear-policy-v1.yaml` | `f010ed6dc123bef0eaf8d086bc6c730e0f4b58ec` |
| `schemas/spear/spear-packet-v1.schema.json` | `6f123374587f1dabaff821422db39c271d072dda` |
| `policies/destination/atlas-prime-destination-policy-v0.2.yaml` | `6103b5a06298d63919545ca9b1be07578b9b9c91` |
| `policies/protected-paths/protected-paths-v0.2.yaml` | `6443447d8fa88f5b1ca039469bc2019d93e9d201` |
| `schemas/source-metadata/source-metadata-v1.schema.json` | `d1d499e8a6f58cf2a0559ffac4940ecd79ac772a` |
| `tools/spear/__init__.py` | `41bc320405b5b749c7c57133f4d26a383d25ec20` |
| `tools/spear/cli.py` | `9c560f6f0882fe60934ed20dd841f8fdd0068c97` |
| `tools/spear/compile.py` | `59cdf14eb9649174e57b0a52bab743ec5a0ce222` |
| `tools/spear/git_adapter.py` | `33f2238ec7f8eec9c4e84ee350a68fce40669ce4` |
| `tools/spear/models.py` | `b3a550b101575bd7ed34021786df866c3cb4fac4` |
| `tools/spear/policy.py` | `59482eafb82a29c0c6a85b0ec9f4a98692bf6968` |
| `tools/spear/validate.py` | `5d610c4c107fef26660752ef4c6a462927897bb3` |
| `tools/spear/dependencies-v1.toml` | `0b999a733f5cf48e22c31e60d1f6e08f3a323763` |
| `tools/spear/operator-runbook.md` | `31c239eb9ca228f96ac071472ce381914cabbcb1` |
| `tools/spear/recovery-runbook.md` | `857229ceeba48982b603ed60e43be8a8128436b6` |

The compiler version is `4.0.0-s0`.

The dependency contract supports Python `>=3.13,<3.14` and pins the complete declared closure for `jsonschema` and `PyYAML`.

## 4. Frozen implementation contract

| Capability | S0 state |
|---|---|
| Strict UTF-8 JSON packet parsing | Implemented |
| Duplicate JSON-key rejection | Implemented |
| Exact transport SHA-256 validation | Implemented |
| JSON Schema Draft 2020-12 validation | Implemented |
| Exact `Jktomy/atlas-prime` target | Enforced |
| Exact `main` base branch | Enforced |
| Exact packet `base_commit` equality with resolved `main` | Enforced |
| Pinned packet schema loaded from packet base commit | Implemented |
| Pinned Spear overlay loaded from packet base commit | Implemented |
| Pinned destination and protected policies loaded from packet base commit | Implemented |
| Pinned source-metadata schema loaded from packet base commit | Implemented |
| Caller-selected external schema or policy | Rejected |
| `CREATE_FILE` planning | Implemented |
| `REPLACE_FILE_FULL` planning | Implemented |
| Target absence check | Implemented |
| Exact expected Git blob check | Implemented |
| Content SHA-256 validation | Implemented |
| Path normalization and collision checks | Implemented |
| Metadata validation and destination-class consistency | Implemented |
| Protected-content category scanning | Implemented |
| Deterministic future branch derivation | Implemented as planning output only |
| Deterministic normalized packet | Implemented |
| Deterministic operation manifest | Implemented |
| Deterministic validation receipt | Implemented |
| Deterministic proposed source tree | Implemented |
| Protected external output root | Implemented |
| Repository working-tree mutation | Not implemented |
| Staging | Not implemented |
| Branch creation or switching | Not implemented |
| Commit | Not implemented |
| Push | Not implemented |
| Pull-request creation or update | Not implemented |
| Merge or auto-merge | Forbidden |
| Direct-main write | Forbidden |
| Force-push | Forbidden |
| Deletion, move, rename, or archive | Forbidden |
| Migration, promotion, or cutover | Not authorized |
| Authentication of execution actor | Not implemented; receipt states `UNVERIFIED_PACKET_CLAIM_ONLY` |

Every successful receipt records:

```text
EXECUTION_NOT_AUTHORIZED
```

## 5. Frozen S0 limits

```text
Maximum operations: 5
Maximum decoded packet bytes: 49,152
Maximum content bytes per operation: 16,384
Maximum path bytes: 500
Allowed packet actions: CREATE_FILE, REPLACE_FILE_FULL
Allowed ordinary extension: .md
Allowed ordinary destination prefix: projects/
Ordinary migration/, generated/, schema, policy, tool, test, workflow,
governance, Quest, Golden Wing, root doctrine, and register paths: denied
Execution-authorized operations: none
```

The broader destination policy registers future route classes. Registration is not execution authority.

## 6. Test and evidence audit

The merged S0 PR records:

- exact 29-file source boundary;
- approved file-hash verification;
- complete unit and adversarial suite passing;
- 73 tests passed;
- one known Windows symlink limitation skipped;
- deterministic real-repository dry-run evidence reviewed.

The current source retains tests for:

- valid create and full replacement planning;
- absent, existing, stale, and invalid targets;
- stale repository base;
- invalid Git object handling;
- deterministic branch derivation;
- transport versus canonical packet hashing;
- contract identities in receipts;
- path traversal and normalized-path collisions;
- official policy precedence over the overlay;
- unknown destination classes and extensions;
- protected-content redaction;
- policy and schema drift;
- cross-repository and external-policy substitution;
- missing pinned contracts;
- newly protected paths;
- malformed, duplicate-key, and unsafe YAML;
- metadata-schema enforcement;
- source-type and authority-class consistency;
- deterministic byte-identical outputs;
- protected output-root behavior;
- absence of network and secret-environment access;
- read-only Git command restriction;
- absence of destructive file operations;
- absence of an S0 workflow;
- explicit `EXECUTION_NOT_AUTHORIZED`.

No GitHub Actions workflow exists in Atlas Prime to rerun this suite automatically. This audit verified the current source and the merged test evidence; it did not independently execute the suite.

## 7. Aegis findings

### Finding A1-F01 — synthetic compiler-version fixture drift

Severity: LOW
State: DEFERRED_TO_S1_HARDENING

`tests/spear/test_compile.py` constructs one synthetic `ContractIdentity` using `compiler_version="3.0.0-s0"` while the current package version is `4.0.0-s0`.

The test does not use this value to grant authority and does not assert the older version as current. It is test-fixture drift, not a writer or policy bypass.

Required handling:

- correct during a separately previewed Spear engine or test PR;
- do not reopen S0 writer authority;
- add a test that synthetic contract identity defaults to or explicitly matches the current package version where appropriate.

### Finding A1-F02 — read-only base-state lookup precedes full path-policy validation

Severity: LOW
State: DEFERRED_TO_S1_HARDENING

The CLI builds real Git base state for packet paths before `compile_packet` performs full path normalization and path-policy validation.

The Git operation is read-only, subprocess arguments are not shell-evaluated, invalid or unsafe paths are later blocked, and S0 cannot write. No authority escalation was identified.

Required handling for S1:

- normalize and validate every operation path before any target-object lookup;
- preserve fail-closed behavior;
- add an end-to-end CLI test proving malformed paths are rejected before Git target lookup.

These notes do not invalidate the S0 offline compiler. They must not be silently forgotten when S1 begins.

## 8. Aegis safety disposition

```text
Source order: PASS
Exact repository and base binding: PASS
Schema and policy provenance: PASS
Read-only Git boundary: PASS
No network or credential access: PASS
No hidden workflow: PASS
No working-tree mutation: PASS
No direct-main or merge authority: PASS
No Spear self-modification route: PASS
Deterministic review output: PASS
Protected output-root boundary: PASS
Known limitations recorded: PASS
Writer activation: DENIED
Migration execution: DENIED
S1 entry: ALLOWED ONLY AFTER THIS FREEZE IS WRITTEN, AUDITED, MERGED,
AND READ BACK THROUGH A SEPARATE APPROVED SOURCE OR MIGRATION PR
```

## 9. Freeze declaration

The following S0 contract is frozen for A2 planning:

1. S0 is a non-writing offline compiler.
2. S0 supports planning for `CREATE_FILE` and `REPLACE_FILE_FULL`.
3. S0 may process at most five Markdown operations under the current ordinary `projects/` route.
4. S0 loads all controlling contracts from the exact packet base commit.
5. S0 produces deterministic external review evidence only.
6. S0 does not authenticate an execution actor.
7. S0 does not create branches, commits, pushes, or pull requests.
8. S0 grants no merge, migration, promotion, retirement, deletion, or cutover authority.
9. S1 must be a separately specified, implemented, audited, and activated writer phase.
10. S1 must not reinterpret S0 receipts as execution approval.

## 10. A2 entry gate

A2 writer-contract design may begin only after:

- this freeze record receives an exact Preview;
- its one-file migration or protected-source PR is explicitly approved;
- Noctua audits the complete file and diff;
- Jayson manually merges;
- the merged file is read back from `main`;
- A1-F01 and A1-F02 are carried into the S1 test and hardening plan.

This record does not choose the S1 execution environment.

That remains Decision Box D-A2-01.

## 11. Noctua acceptance criteria

Noctua must verify:

1. the Prime head used by the audit;
2. the exact 29-file S0 boundary;
3. the current controlling contract identities;
4. no implementation file changed after the S0 merge, except the documented `athenas-spear.md` routing update;
5. no hidden workflow or write adapter exists;
6. the Git adapter remains read-only;
7. execution remains unauthorized;
8. the two low-severity findings are visible and do not silently broaden scope;
9. the record makes no migration, writer, merge, promotion, or cutover claim;
10. the eventual PR changes only this audit record;
11. merged-main readback occurs before A1 is marked `VERIFIED_COMPLETE`.

## 12. Final state

```text
A1 technical audit: COMPLETE
A1 specification freeze content: COMPLETE
A1 durable source closeout: READY_FOR_PREVIEW
A1 phase status: NOT YET VERIFIED_COMPLETE
Reason: Preview -> Execute, Noctua, manual merge, and merged-main readback remain
S1 writer authority: NOT AUTHORIZED
```
