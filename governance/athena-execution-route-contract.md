---
title: "Athena Execution Route Contract"
atlas_id: "prime.governance.athena-execution-routes"
status: "CANONICAL_ACTIVE"
source_type: "PROTOCOL"
authority_class: "CANONICAL_AUTHORED_SOURCE"
owner_project: "Project Codex"
owner_operation: "Operation Source Governance"
protected_level: "CRITICAL"
---

# Athena Execution Route Contract

This contract separates Athena's methods, Jayson/Artemis delegated delivery, repository engines, launchers, substrates, and permanence authority. No route name may be inferred from the work surface or repository substrate alone.

## Canonical route identities

```text
ATHENA_SPEAR
  -> Athena authors one exact Weave
  -> Spear delivers it to the singular Prime Thread Engine
  -> immutable branch + one draft PR + exact readback

JAYSON_ARTEMIS_ARROW_BOW
  -> Jayson authorizes or fires one immutable Arrow
  -> Artemis/Bow validates and delivers the unchanged Weave
  -> the same compiler and singular Prime Thread Engine
  -> immutable branch + one draft PR + exact readback

ATHENA_PHOENIX_BLADE
  -> Athena executes one exact Sword herself
  -> Sword-defined repository transaction
  -> no Thread Engine

JAYSON_OATHBRINGER
  -> Jayson wields one exact Sword through Oathbringer
  -> thin client + Sword-defined repository transaction
  -> no Thread Engine

ATHENA_AEGIS_BREAK
  -> Athena selects or constructs any safe bounded equivalent route
  -> may include direct GitHub-native construction
  -> preserves the approved authority envelope and stop boundary
```

Spear is Athena's direct Thread Engine route. Arrow and Bow belong to Jayson and Artemis delegated delivery and are not Athena's direct route. Phoenix Blade mirrors what Oathbringer is to Jayson: Athena executes a Sword herself, independently of Thread Engine. Aegis Break owns safe alternate-route selection and construction, including direct GitHub-native work when appropriate.

Prime has one normal repository engine: Thread Engine. Spear and Arrow/Bow may converge on the same compiler and Thread Engine while preserving distinct authorizer, operator, and route identities. Phoenix Blade, Oathbringer, and Aegis Break do not become second normal repository engines.

Machine-stable invariants:

```text
THREAD_ENGINE_SELF_CHANGE_ROUTE=AEGIS_BREAK_TO_NON_THREAD_ENGINE_METHOD
NORMAL_STOP_BOUNDARY=DRAFT_PR_READBACK
DIRECT_GITHUB_NATIVE_ROUTE=AEGIS_BREAK
PHOENIX_BLADE_EXECUTES_SWORD=true
PHOENIX_BLADE_USES_THREAD_ENGINE=false
BOW_ARROW_OWNERSHIP=JAYSON_AND_ARTEMIS
ROLLBACK_PRE_MERGE=CLOSE_DRAFT_PR
ROLLBACK_POST_MERGE=REVIEWED_REVERT_PR
```

## Jayson authorization and CAP-015

Jayson's explicit Preview and Execute approval in the active chat is sufficient human authority for the exact bounded task. A separate platform-signed ChatGPT Work origin attestation, external bridge, user-run Python command, or user-run PowerShell command is not required to establish Athena's authority or ability to invoke Spear.

Direct Spear compilation and Thread Engine delivery are already proven and merged through harmless direct Spear PR `#102`. The merged Spear/Arrow/Bow parity proof separately binds compiler and candidate equivalence. On that accepted evidence, `CAP-015` and `AJ-01` are reconciled as active/proven under their corrected meanings:

- `CAP-015`: Athena can reach the singular Thread Engine through Spear from a Jayson-authorized chat task.
- `AJ-01`: Athena's exact direct Spear submission reaches Thread Engine and creates a harmless immutable draft PR.

The former requirement for an independently attested fresh-platform origin was an architectural wrapper, not a missing operating capability. It is superseded and must not block Spear, Phoenix Blade, Aegis Break, or ordinary in-chat Preview-to-Execute work.

## Hosted Arrow/Bow identity

The hosted intake is a thin Jayson/Artemis launcher, never a source author, patch engine, normal repository writer, ready authority, merge authority, or replacement for Thread Engine. It may validate and invoke only.

Every hosted request validates against `schemas/athena-hosted-route-request-v1.schema.json` and binds:

- Jayson as authorizer;
- repository, exact base SHA, route, mission identity, and carrier SHA-256;
- event identity, actor, triggering actor, workflow ref and source SHA;
- run ID, run attempt, credential principal, and token mode;
- replay identity, protected-path classification, and draft-PR stop boundary.

The hosted request schema accepts only `ARROW_BOW_HOSTED`, ephemeral `GITHUB_TOKEN`, and ordinary path classification. The submitted request cannot select trusted workflow SHA, credential principal, event actor, triggering actor, run identity, or repository owner.

## Receipt and replay contract

Every accepted, rejected, partial, or successful hosted invocation validates against `schemas/athena-hosted-route-receipt-v1.schema.json`. The receipt separates authorizer, semantic operator, requesting surface, actors, workflow, credential, mission, run, and attempt. It binds carrier, compiler receipt, adapter receipt, branch, draft PR, and exact remote head when those stages exist.

`SUCCESS` requires compiler and adapter receipts plus a new immutable branch, draft PR, and exact head at `DRAFT_PR_READBACK`. `REJECTED` and `BLOCKED` require no mutation, null remote identities, a bounded error code, and a pre-mutation rejection or route handoff. `PARTIAL` is preserved exactly and blocks retry, cleanup, branch reuse, force update, or result relabeling.

The replay key is checked before write authority. Any matching current or historical branch, open/closed/merged PR, accepted receipt, or completed mission rejects without mutation.

## Pre-mutation route detection

Route selection occurs before compiler or adapter mutation:

| Declared path class | Required result |
|---|---|
| ordinary Athena Thread Engine delivery | Spear |
| ordinary Jayson/Artemis delegated delivery | Arrow/Bow |
| Athena executes an exact Sword | Phoenix Blade |
| bounded direct or alternate safe route | Aegis Break |
| generated projection mixed with authored source | reject `GENERATED_SOURCE_MIXING` |
| protected non-self-change without exact authority | reject `PROTECTED_ROUTE_AUTHORITY_REQUIRED` |
| protected non-self-change with exact authority | Aegis Break selects the approved protected route |
| `tools/thread-engine/**` self-change | Aegis Break to Phoenix Blade, Oathbringer, or another approved non-Thread-Engine route |
| ambiguous, unknown, or policy-drifted path | reject `ROUTE_UNRESOLVED` |

## Hosted permissions and separation

The hosted workflow separates read-only intake validation from mission-scoped execution. The execution job receives only bounded ephemeral write permissions after owner identity, workflow source, carrier, base, mission, replay, path, and privacy checks pass.

It must not use `pull_request_target`, unpinned reusable workflows, arbitrary URLs, caller-provided commands, shell evaluation, repository-setting authority, automatic ready, automatic merge, persistent credentials, or a second repository writer.

## Fail-closed rejection set

Reject without mutation on non-owner or unauthorized delegation; edited input; stale base; replay; malformed or oversized carrier; duplicate JSON keys; unsafe archive members; hash mismatch; unsafe or duplicate paths; branch or PR collision; ambiguous credential principal; workflow-source drift; protected-path mismatch; generated mixing; private material; or any request for direct main, force push, ready, merge, cleanup, settings, standing authority, or a second writer.

`AJ-03` remains UNPROVEN because a genuine non-owner live rejection is still missing. This CAP-015/AJ-01 realignment does not promote AJ-03, AJ-11, AJ-12, CAP-027, RP-C01, RP-C08, or the Repairing Prime Quest.

## Pre-ingress privacy boundary

Only locally pre-screened, public-clean, size-bounded content may cross into a GitHub event or workflow input. Secrets, credentials, tokens, MFA or recovery data, private keys, real environment values, PHI, finance/account evidence, IP addresses, network maps, device registers, private runtime values, and raw private exports remain outside GitHub.

Logs, summaries, comments, artifacts, receipts, and diagnostics expose only bounded identities, hashes, already-classified clean paths, stage names, and sanitized error codes. They never echo carrier bytes, payload text, or unrestricted command output.

## Ordinary free-form mission fields

`tools.athena_routes.free_form_intake` may construct one deterministic public-clean carrier and Preview from closed mission fields. It is local, read-only, non-promoting, and cannot dispatch, call the adapter, write a branch or PR, mark ready, merge, or change settings.

That constructor is not an external origin bridge and no longer carries a CAP-015 or AJ-01 proof burden. Its live hosted acceptance remains evidence for RP-C01-M08 and guided usability only.

## Guided hosted publisher

The owner-guided publisher is a Jayson/Artemis Arrow/Bow launcher over the existing hosted workflow. Preview audits canonical main, workflow identity, carrier, privacy, ordinary paths, and compiler output without mutation. Execute requires exact Preview identity, revalidates drift, reserves durable no-retry intent, dispatches only the existing hosted workflow, and reads back the run.

The guided publisher may not call the adapter directly, create or update a branch or PR, retry partial state, mark ready, merge, change settings, or become a second writer. CAP-010 is already accepted from its separate live journey and does not establish or limit Athena's Spear identity.

## Generated post-merge route

Every owner-authorized push to canonical `main`, including a generated-only merge, enters `.github/workflows/generated-checkpoint-publisher.yml`. Before parity work, the read-only queue admission binds the exact repository, owner actor, triggering actor, event, main ref, workflow source, event base, current-main readback, run identity, and ephemeral GitHub credential class. It enumerates at most 1,000 open pull requests through a 1,001-entry sentinel so the accepted queue cannot silently truncate. Its durable sanitized receipt binds the closed query boundary and observed snapshot by SHA-256 and never authorizes mutation.

Exactly one open generated checkpoint may yield successful `DEFERRED_OPEN_CHECKPOINT` only when its readback is an internally consistent publisher-owned draft: GitHub Actions bot author, same Prime repository and owner, `main` base, exact generated title and mission, deterministic branch and replay relation, and canonical publisher body provenance. Its historical base may truthfully precede the newer queue run's current main. An older serialized event may likewise defer against a recorded newer current main because deferral cannot mutate; a `CLEAR` decision with event-base drift fails closed before parity. A malformed, inconsistent, forged, non-draft, or multiple generated identity fails closed. Successful deferral leaves parity, reconciliation, preparation, publication, and exact-head validation skipped, performs no mutation, and is an overall GREEN workflow outcome.

While one valid generated draft is open, later source merges defer read-only and accumulate only as canonical source state. Merging that generated draft moves `main`, re-enters the same publisher, and recomputes all five projections from the then-current source. Current reports return successful `NOOP` with no mission, commit, branch, PR, or self-dispatch. Accumulated source changes produce one later full five-file mission and one fresh deterministic generated-only draft through the singular Thread Engine; a partial delta fails closed.

Closing a generated draft without merge does not move `main` and therefore does not wake the publisher. Recovery is an explicit owner `workflow_dispatch` bound to exact current main, or the next authorized source merge. There is no pull-request-close trigger and no automatic close, replacement, retry, ready, merge, branch deletion, or direct generated write to `main`.

Queue preflight is defense in depth, not a replacement writer. The singular Thread Engine retains its final remote-head, branch-collision, generated-PR-collision, mission replay, nonce replay, stale-base, pre-push, exact path/blob, and draft readback locks. No generated queue component may become a second repository writer.

This post-merge generated route is not Spear, Phoenix Blade, Aegis Break, or Bow/Arrow route ownership. It is the accepted generated lifecycle described by AJ-09 and CAP-019/CAP-020. It never automatically readies or merges the generated PR.

## Evidence and promotion boundary

This realignment uses already merged evidence; it does not manufacture new operating proof:

- direct Spear PR `#102` proves Athena-to-Thread-Engine mechanics;
- merged parity proof preserves direct Spear and Arrow/Bow compiler equivalence;
- Oathbringer production acceptance proves the Sword operation set used by Phoenix Blade's counterpart definition;
- PRs `#181` and `#182` prove the automatic generated post-merge route and zero-delta behavior.

Only `CAP-015`, `AJ-01`, and RP-C01-M02 are reconciled by the corrected architecture and accepted evidence. AJ-03, RP-C01-M06, RP-C01-M07, AJ-11, AJ-12, CAP-027, RP-C01, RP-C08, and Repairing Prime remain open.
