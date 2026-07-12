---
title: "Athena Execution Route Contract"
atlas_id: "prime.governance.athena-execution-routes"
status: "CONTRACT_DEFINED_NOT_ACTIVATED"
source_type: "PROTOCOL"
authority_class: "CANONICAL_AUTHORED_SOURCE"
owner_project: "Project Codex"
owner_operation: "Operation Source Governance"
protected_level: "CRITICAL"
---

# Athena Execution Route Contract

This contract defines RP-C01 execution-route parity before any hosted intake is
activated. Contract source, schemas, tests, component existence, and local
execution do not prove hosted availability or fresh Work/Athena reachability.

## One engine, two delivery routes

```text
SPEAR_DIRECT
  -> exact Spear carrier audit
  -> existing Spear compiler
  -> singular Prime Thread Engine production adapter
  -> immutable branch + one draft PR + exact readback

ARROW_BOW_HOSTED
  -> owner-only hosted event snapshot
  -> immutable Arrow carrier audit
  -> Bow identity and replay validation
  -> the same existing Spear compiler
  -> the same singular Prime Thread Engine production adapter
  -> immutable branch + one draft PR + exact readback
```

The hosted intake is a thin launcher, never a source author, patch engine,
normal repository writer, ready authority, merge authority, or replacement for
Thread Engine. It may validate and invoke only. Direct Spear and hosted
Arrow/Bow must produce the same compiled mission, payload bytes, candidate tree,
and normalized compiler receipt for the same carrier.

Machine-stable invariants:

```text
THREAD_ENGINE_SELF_CHANGE_ROUTE=AEGIS_BREAK_TO_OATHBRINGER
NORMAL_STOP_BOUNDARY=DRAFT_PR_READBACK
COMPONENT_EVIDENCE_CANNOT_ASSERT_ROUTE_GATE
ROLLBACK_PRE_MERGE=CLOSE_DRAFT_PR
ROLLBACK_POST_MERGE=REVIEWED_REVERT_PR
```

## Trusted request identity

Every hosted request validates against
`schemas/athena-hosted-route-request-v1.schema.json` and binds:

- Jayson as authorizer;
- repository, exact base SHA, route, mission identity, and carrier SHA-256;
- event name, action, immutable event node or delivery identity, creation and
  update timestamps, event payload digest, event actor, and triggering actor;
- workflow ref and exact workflow source SHA;
- run ID, run attempt, credential principal, and token mode;
- a replay key derived from repository, event identity, carrier digest, mission
  identity, and base SHA;
- exact protected-path classification and the draft-PR stop boundary.

The hosted request schema accepts only `ARROW_BOW_HOSTED`, an ephemeral
`GITHUB_TOKEN`, and `ORDINARY` path classification. Direct Spear uses the
existing local compiler and adapter mission contracts. Protected, generated,
self-change, and unresolved inputs stop before an executable hosted request is
formed and receive only a sanitized rejection or handoff receipt.

The submitted request cannot select its trusted workflow SHA, credential
principal, event actor, triggering actor, run identity, or repository owner.
Those values come from the hosted platform and are read back independently.

## Receipt and replay contract

Every accepted, rejected, or successful invocation validates against
`schemas/athena-hosted-route-receipt-v1.schema.json`. The receipt separates the
authorizer, semantic operator, requesting surface, event actor, triggering
actor, workflow identity/source SHA, credential principal, token mode, mission,
run, and attempt. It binds the input carrier, compiler receipt, adapter receipt,
branch, draft PR, and exact remote head when those stages exist.

Receipt conditionals make the result coherent: `SUCCESS` requires compiler and
adapter receipts plus a new branch, draft PR, and exact head at
`DRAFT_PR_READBACK`; `REJECTED` and `BLOCKED` require no mutation, null remote
identities, an error code, and a pre-mutation rejection or route handoff. Every
receipt binds rollback: close the draft PR before merge, use a new reviewed
revert PR after merge, and never force-update or rewrite history. A no-mutation
result records that no rollback is required.

The replay key is checked before write authority. Any matching current or
historical branch, open/closed/merged PR, accepted receipt, or completed mission
rejects without mutation. A retry never force-updates, reuses a mutable branch,
or edits an earlier PR.

## Pre-mutation route detection

Route selection occurs before compiler or adapter mutation:

| Declared path class | Required result |
|---|---|
| ordinary authored source | Spear or hosted Arrow/Bow may invoke Thread Engine |
| generated projection mixed with authored source | reject `GENERATED_SOURCE_MIXING` |
| protected non-self-change without exact Aegis authority | reject `PROTECTED_ROUTE_AUTHORITY_REQUIRED` |
| protected non-self-change with exact Aegis authority | existing Aegis Break protected Thread Engine route |
| `tools/thread-engine/**` self-change | hand off to Aegis Break → Oathbringer; Thread Engine must not execute |
| ambiguous, unknown, or policy-drifted path | reject `ROUTE_UNRESOLVED` |

Phoenix Blade remains the Athena-native direct control route and may perform a
separately authorized bounded construction. Oathbringer remains manual
recovery/compatibility and the mandatory Thread Engine self-change route.
Neither becomes a second normal repository writer.

## Hosted permissions and separation

A future hosted workflow must separate read-only intake validation from the
mission-scoped execution job. The execution job may receive only ephemeral
`GITHUB_TOKEN` access with `contents: write` and `pull-requests: write`. It must
not use `pull_request_target`, unpinned reusable workflows, arbitrary URLs,
caller-provided commands, shell evaluation, repository-setting authority,
workflow dispatch authority, ready authority, merge authority, or persistent
credentials.

Write authority is acquired only after owner identity, immutable event snapshot,
workflow source, carrier, base, mission, replay, path, and privacy checks pass.

## Fail-closed rejection set

Reject without mutation on non-owner or unauthorized delegation; edited input;
stale base; replay; malformed or oversized carrier; duplicate JSON keys;
unexpected, missing, nested, encrypted, symlink, or nonregular archive entries;
hash mismatch; unsafe or duplicate paths; branch or PR collision; ambiguous
credential principal; workflow-source drift; protected-path mismatch; generated
mixing; private material; or any request for direct main, force push, ready,
merge, cleanup, settings, standing authority, or a second writer.

## Pre-ingress privacy boundary

Only a locally pre-screened, public-clean, size-bounded carrier may cross into a
GitHub event or workflow input. Secrets, credentials, tokens, MFA or recovery
data, private keys, real environment values, PHI, finance/account evidence, IP
addresses, network maps, device registers, private runtime values, and raw
private exports must remain outside GitHub; hosted rejection is defense in
depth, not permission to submit them.

Event bodies, logs, step summaries, comments, artifacts, receipts, and failure
diagnostics never echo carrier bytes, payload text, private-looking matches, or
unrestricted command output. They expose only bounded identities, hashes,
paths already classified as public-clean, stage names, and sanitized error
codes.

## Evidence boundary

GitHub can prove workflow identity, source SHA, actor fields, run/attempt,
credential-principal readback, compiler and adapter receipts, rejection runs,
branch/PR/head identity, CI, and exact changed paths. It cannot prove that a
fresh Work/Athena context originated the request unless a separate external
Work receipt binds that context to the event, carrier, run, mission, and PR.

Therefore:

- this contract does not promote CAP-009, CAP-010, CAP-011, or CAP-015;
- a hosted GitHub pilot may prove hosted mechanics but not fresh Work origin;
- AJ-01, AJ-02, and AJ-03 remain unproven until their complete exact journeys
  and genuinely detached reconciliation exist;
- `ATHENA_NATIVE_EXECUTION_ROUTES_PROVEN` cannot be asserted from contract or
  component evidence alone.

## Transaction order

1. Land this contract, closed schemas, and tests.
2. Land the thin hosted intake separately without changing Thread Engine.
3. Run one harmless hosted pilot to a new unprotected proof path.
4. Run live rejection trials without mutation.
5. Reconcile method, capability, journey, and Quest source only from accepted
   evidence.
6. Refresh generated projections in a separate generated-only transaction.
