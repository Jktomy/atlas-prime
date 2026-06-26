---
title: "Athena's Spear A3-G0 Golden Transaction Suite v1"
atlas_id: "spear.a3-g0.golden-transactions.v1"
format_version: "1.0"
status: "PROPOSED"
source_type: "SPECIFICATION"
authority_class: "TOOL_CONTRACT"
owner_project: "Codex"
owner_operation: "Atlas Prime Rebuild Quest / Spear Campaign"
canonical_scope: "Defines the representative positive, hostile, recovery, and platform transactions that lead A3a and A3b implementation without granting writer activation or packet-execution authority."
protected_level: "CRITICAL"
routes_from:
  - "specs/spear/athenas-spear-s1-writer-contract-v1.md"
  - "migration/atlas-codex/atlas-prime-rebuild-quest-roadmap-v1.md"
routes_to:
  - "tests/fixtures/spear/golden-transactions-v1.json"
  - "tests/spear/test_golden_transactions.py"
  - "tools/spear/s1_contracts.py"
private_boundary: "Clean transaction requirements, failure codes, hashes, repository identities, and audit expectations only. No credentials, tokens, PHI, raw finance evidence, private runtime values, network maps, or protected exports."
evidence_boundary: "This specification and its fixture define acceptance requirements. Workflow runs, packet bytes, receipts, Git objects, pull requests, Noctua reports, merge records, and Phoenix proofs remain separate evidence."
supersedes: []
cleanup_path: "Retain as the A3-G0 requirements baseline. Supersede only through a reviewed Spear contract revision that preserves complete vector lineage and states why each changed vector remains safe."
last_verified: "2026-06-25"
---

# Athena's Spear A3-G0 Golden Transaction Suite v1

## Authority

```text
A3a source implementation: REQUIRES SEPARATE PREVIEW AND EXECUTE
A3b writer implementation: NOT AUTHORIZED BY THIS SPECIFICATION
S1 writer activation: NOT AUTHORIZED
Packet execution: NOT AUTHORIZED
Migration / merge / promotion / cutover: NOT AUTHORIZED
```

## Design sequence

```text
Atlas outcome
-> representative packet
-> exact expected transaction
-> required receipt and Noctua evidence
-> minimum safe implementation
-> harmless proof
-> separate activation
```

The exact machine-readable suite is `tests/fixtures/spear/golden-transactions-v1.json`. It contains 43 vectors and maps every A2 contract section from §5 through §23.

## Implementation split

- `A3A_CONTRACT_TEST` covers schemas, dual activation, path-before-Git hardening, redaction boundaries, and static no-writer controls.
- `A3B_WRITER_TEST` covers remote-main freshness, transaction identity, Git lineage, draft-PR fidelity, failure receipts, and recovery.
- `A4_PROOF` covers the harmless end-to-end proof and independent rollback planning.

## Vector catalog

| ID | Class | Gate | Vector | Expected state |
|---|---|---|---|---|
| `GT-P01` | POSITIVE | A3B_WRITER_TEST | Ordinary single-file create | `DRAFT_PR_CREATED` |
| `GT-P02` | POSITIVE | A3B_WRITER_TEST | Exact full-file replacement | `DRAFT_PR_CREATED` |
| `GT-P03` | POSITIVE | A3B_WRITER_TEST | Atomic three-file create | `DRAFT_PR_CREATED` |
| `GT-R01` | RECOVERY | A3B_WRITER_TEST | Exact branch pushed, PR missing recovery | `DRAFT_PR_CREATED_RECOVERED` |
| `GT-R02` | RECOVERY | A3B_WRITER_TEST | Exact completed transaction idempotent replay | `EXISTING_TRANSACTION_RETURNED` |
| `GT-P04` | POSITIVE | A4_PROOF | Harmless end-to-end proof vector | `HARMLESS_PROOF_COMPLETE` |
| `GT-N01` | HOSTILE | A3B_WRITER_TEST | Non-owner actor rejected | `BLOCKED_BEFORE_PLAN` |
| `GT-N02` | HOSTILE | A3B_WRITER_TEST | Wrong event rejected | `BLOCKED_BEFORE_PLAN` |
| `GT-N03` | HOSTILE | A3B_WRITER_TEST | Wrong repository rejected | `BLOCKED_BEFORE_PLAN` |
| `GT-N04` | HOSTILE | A3A_CONTRACT_TEST | Duplicate JSON keys rejected | `BLOCKED_BEFORE_COMPILE` |
| `GT-N05` | HOSTILE | A3A_CONTRACT_TEST | Transport and decompression limits enforced | `BLOCKED_BEFORE_PARSE` |
| `GT-N06` | HOSTILE | A3A_CONTRACT_TEST | Packet transport hash mismatch | `BLOCKED_BEFORE_COMPILE` |
| `GT-N07` | HOSTILE | A3A_CONTRACT_TEST | Manifest hash mismatch | `BLOCKED_IN_PLAN` |
| `GT-N08` | HOSTILE | A3A_CONTRACT_TEST | Preview hash mismatch | `BLOCKED_IN_PLAN` |
| `GT-N09` | HOSTILE | A3A_CONTRACT_TEST | Expired plan or approval rejected | `BLOCKED_BEFORE_WRITE` |
| `GT-N10` | HOSTILE | A3A_CONTRACT_TEST | Approval scope does not authorize draft PR | `BLOCKED_IN_PLAN` |
| `GT-N11` | HOSTILE | A3B_WRITER_TEST | Stale base detected in PLAN | `BLOCKED_IN_PLAN` |
| `GT-N12` | HOSTILE | A3B_WRITER_TEST | Remote main advances before branch creation | `BLOCKED_BEFORE_BRANCH` |
| `GT-N13` | HOSTILE | A3B_WRITER_TEST | Remote main advances before push | `BLOCKED_BEFORE_PUSH` |
| `GT-N14` | HOSTILE | A3B_WRITER_TEST | Remote main advances before PR creation | `BRANCH_PUSHED_PR_MISSING` |
| `GT-N15` | HOSTILE | A3B_WRITER_TEST | Stale replacement target blob | `BLOCKED_BEFORE_BRANCH` |
| `GT-N16` | HOSTILE | A3A_CONTRACT_TEST | Schema or policy blob drift | `BLOCKED_BEFORE_WRITE` |
| `GT-N17` | HOSTILE | A3A_CONTRACT_TEST | Path validation precedes Git lookup | `BLOCKED_BEFORE_GIT_LOOKUP` |
| `GT-N18` | HOSTILE | A3A_CONTRACT_TEST | Protected or denied path rejected | `BLOCKED_BEFORE_GIT_LOOKUP` |
| `GT-N19` | HOSTILE | A3A_CONTRACT_TEST | Symlink target or ancestor rejected | `BLOCKED_BEFORE_WRITE` |
| `GT-N20` | HOSTILE | A3A_CONTRACT_TEST | Submodule target or ancestor rejected | `BLOCKED_BEFORE_WRITE` |
| `GT-N21` | HOSTILE | A3A_CONTRACT_TEST | Case or normalization collision rejected | `BLOCKED_BEFORE_GIT_LOOKUP` |
| `GT-N22` | HOSTILE | A3A_CONTRACT_TEST | Activation policy alone cannot authorize | `BLOCKED_BEFORE_PLAN` |
| `GT-N23` | HOSTILE | A3A_CONTRACT_TEST | Destination policy alone cannot authorize | `BLOCKED_BEFORE_PLAN` |
| `GT-N24` | HOSTILE | A3A_CONTRACT_TEST | Dual activation operation mismatch | `BLOCKED_BEFORE_PLAN` |
| `GT-N25` | HOSTILE | A3B_WRITER_TEST | Same packet ID with changed content | `BLOCKED_AS_COLLISION` |
| `GT-N26` | HOSTILE | A3B_WRITER_TEST | Concurrent duplicate dispatch | `ONE_RUN_SERIALIZED_OTHER_BLOCKED_OR_QUEUED` |
| `GT-N27` | HOSTILE | A3B_WRITER_TEST | Existing branch collision | `BLOCKED_AS_COLLISION` |
| `GT-N28` | HOSTILE | A3B_WRITER_TEST | Multi-parent commit rejected | `BLOCKED_AS_COLLISION` |
| `GT-N29` | HOSTILE | A3B_WRITER_TEST | Modified full commit message rejected | `BLOCKED_AS_COLLISION` |
| `GT-N30` | HOSTILE | A3B_WRITER_TEST | Unexpected author or committer rejected | `BLOCKED_AS_COLLISION` |
| `GT-N31` | HOSTILE | A3B_WRITER_TEST | Server-created PR metadata mutated | `PR_CREATED_METADATA_MISMATCH` |
| `GT-N32` | RECOVERY | A3B_WRITER_TEST | PR API uncertainty after possible creation | `PR_STATE_UNCERTAIN` |
| `GT-N33` | HOSTILE | A3A_CONTRACT_TEST | Receipt emitted for every failed gate | `FAILED_WITH_RECEIPT` |
| `GT-N34` | HOSTILE | A3A_CONTRACT_TEST | Credential and protected-value leakage blocked | `BLOCKED_OR_REDACTED` |
| `GT-N35` | HOSTILE | A3A_CONTRACT_TEST | Forbidden capability static and dynamic denial | `FORBIDDEN_CAPABILITIES_ABSENT` |
| `GT-N36` | PLATFORM | A3B_WRITER_TEST | Expected PR checks require human approval and success | `AWAITING_HUMAN_CHECK_APPROVAL_OR_BLOCKED` |
| `GT-N37` | RECOVERY | A4_PROOF | Rollback and replacement-PR planning | `ROLLBACK_PLAN_VERIFIED` |

## Mandatory red-team closures

A3a and A3b must close, by executable tests, the previously reproduced failures:

1. activation policy alone accepted without destination-policy authority;
2. remote `main` advanced while the writer still pushed;
3. one packet ID derived multiple branches after content changed;
4. a two-parent commit was accepted as an idempotent branch;
5. an approved subject with extra commit body or trailers was accepted;
6. mutated server-created PR title and body were accepted;
7. failed attempts did not always produce durable redacted receipts;
8. exact hosted-runner dependency provisioning remained unresolved.

## Completion rule

A3-G0 is satisfied only when the human specification, JSON fixture, schema, A2 traceability checks, and all vector IDs agree exactly. A3a may then implement read-only contract behavior. A3b remains separately gated.
