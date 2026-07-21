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
  -> Athena authors one exact Weave across any safe declared Prime paths
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
SPEAR_REPOSITORY_PATH_SCOPE=ALL_SAFE_DECLARED_PATHS
THREAD_ENGINE_SELF_CHANGE_ROUTE=ATHENA_SPEAR_DRAFT_PR
NORMAL_STOP_BOUNDARY=DRAFT_PR_READBACK
DIRECT_GITHUB_NATIVE_ROUTE=AEGIS_BREAK
PHOENIX_BLADE_EXECUTES_SWORD=true
PHOENIX_BLADE_USES_THREAD_ENGINE=false
BOW_ARROW_OWNERSHIP=JAYSON_AND_ARTEMIS
ROLLBACK_PRE_MERGE=CLOSE_DRAFT_PR
ROLLBACK_POST_MERGE=REVIEWED_REVERT_PR
```

## Universal Spear path scope

Prime has no repository file class that blocks direct Spear authorship. A Jayson-authorized Spear Weave may declare governance, lifecycle, schema, workflow, generated, Quest, recovery, or Thread Engine paths in one exact candidate.

Repository path is classification, not authority. High-impact and self-referential changes receive the validation profile required by their controlling source. A candidate that changes Thread Engine, validation planning, policy, schemas, or workflows cannot reduce the tests selected from trusted canonical `main`.

The current canonical compiler and production adapter create only one branch, one single-parent commit, and one draft PR. They cannot ready, merge, write directly to `main`, modify settings, establish standing authority, or conceal partial state. A Thread Engine self-change becomes authoritative only through ordinary review, exact-head validation, Strikeforce, separately authorized permanence, and merged-main readback.

Repository-path freedom does not weaken the protected-data boundary. Private or prohibited content remains outside Prime and outside all carriers, payloads, logs, receipts, and generated projections.

## Jayson authorization and CAP-015

Jayson's explicit Preview and Execute approval in the active chat is sufficient human authority for the exact bounded task. A separate platform-signed ChatGPT Work origin attestation, external bridge, user-run Python command, or user-run PowerShell command is not required to establish Athena's authority or ability to invoke Spear.

Direct Spear compilation and Thread Engine delivery are already proven and merged through harmless direct Spear PR `#102`. The merged Spear/Arrow/Bow parity proof separately binds compiler and candidate equivalence. On that accepted evidence, `CAP-015` and `AJ-01` are reconciled as active/proven under their corrected meanings:

- `CAP-015`: Athena can reach the singular Thread Engine through Spear from a Jayson-authorized chat task.
- `AJ-01`: Athena's exact direct Spear submission reaches Thread Engine and creates a harmless immutable draft PR.

The former requirement for an independently attested fresh-platform origin was an architectural wrapper, not a missing operating capability. It is superseded and must not block Spear, Phoenix Blade, Aegis Break, or ordinary in-chat Preview-to-Execute work.

## Hosted Arrow/Bow identity

The hosted intake is a thin Jayson/Artemis launcher, never a source author, patch engine, normal repository writer, ready authority, merge authority, or replacement for Thread Engine. It may validate and invoke only.

Every hosted request validates against `schemas/athena-hosted-route-request-v1.schema.json` and binds Jayson as authorizer; repository, exact base SHA, route, mission identity, and carrier SHA-256; event identity and workflow source; run and credential identity; replay identity; hosted path classification; and the draft-PR stop boundary.

The hosted request schema accepts only `ARROW_BOW_HOSTED`, ephemeral `GITHUB_TOKEN`, and its currently supported hosted path classification. That compatibility field does not define a Prime-wide protected-file doctrine and does not limit direct Spear.

## Receipt and replay contract

Every accepted, rejected, partial, or successful hosted invocation validates against `schemas/athena-hosted-route-receipt-v1.schema.json`. The receipt separates authorizer, semantic operator, requesting surface, actors, workflow, credential, mission, run, and attempt. It binds carrier, compiler receipt, adapter receipt, branch, draft PR, and exact remote head when those stages exist.

`SUCCESS` requires compiler and adapter receipts plus a new immutable branch, draft PR, and exact head at `DRAFT_PR_READBACK`. `REJECTED` and `BLOCKED` require no mutation, null remote identities, a bounded error code, and a pre-mutation rejection or route handoff. `PARTIAL` is preserved exactly and blocks retry, cleanup, branch reuse, force update, or result relabeling.

The replay key is checked before write authority. Any matching current or historical branch, open/closed/merged PR, accepted receipt, or completed mission rejects without mutation.

## Pre-mutation route detection

Route selection occurs before compiler or adapter mutation:

| Declared objective | Required result |
|---|---|
| Athena authors any safe declared Prime repository paths through Thread Engine | Spear |
| ordinary Jayson/Artemis delegated hosted delivery | Arrow/Bow |
| Athena executes an exact Sword | Phoenix Blade |
| bounded direct or alternate safe route | Aegis Break |
| generated projection mission requiring its dedicated profile | generated checkpoint route |
| unsafe path syntax, collision, stale base, replay, private material, or policy drift | reject before mutation |

Legacy hosted path classification may still decline a hosted Arrow/Bow carrier before mutation. That is a hosted-launch compatibility boundary, not evidence that direct Spear lacks path authority.

## Hosted permissions and separation

The hosted workflow separates read-only intake validation from mission-scoped execution. The execution job receives only bounded ephemeral write permissions after owner identity, workflow source, carrier, base, mission, replay, path, and privacy checks pass.

It must not use `pull_request_target`, unpinned reusable workflows, arbitrary URLs, caller-provided commands, shell evaluation, repository-setting authority, automatic ready, automatic merge, persistent credentials, or a second repository writer.

## Fail-closed rejection set

Reject without mutation on non-owner or unauthorized delegation; edited input; stale base; replay; malformed or oversized carrier; duplicate JSON keys; unsafe archive members; hash mismatch; unsafe or duplicate path syntax; branch or PR collision; ambiguous credential principal; workflow-source drift; private material; or any request for direct main, force push, ready, merge, cleanup, settings, standing authority, or a second writer.

Path location alone is not a direct-Spear rejection reason.

`AJ-03` is PROVEN by genuine non-owner workflow run `29421543076`. Both actors were `jaysontomyod`; the route returned `OWNER_IDENTITY_REJECTED` at pre-mutation rejection, the Thread Engine job was skipped, and exact sanitized evidence records zero mutation. This acceptance does not promote AJ-11, AJ-12, CAP-027, RP-C08, or the Repairing Prime Quest.

## Pre-ingress privacy boundary

Only locally pre-screened, public-clean, size-bounded content may cross into a GitHub event or workflow input. Secrets, credentials, tokens, MFA or recovery data, private keys, real environment values, PHI, finance/account evidence, IP addresses, network maps, device registers, private runtime values, and raw private exports remain outside GitHub.

Logs, summaries, comments, artifacts, receipts, and diagnostics expose only bounded identities, hashes, already-classified clean paths, stage names, and sanitized error codes. They never echo carrier bytes, payload text, or unrestricted command output.

## Ordinary free-form mission fields

`tools.athena_routes.free_form_intake` may construct one deterministic public-clean carrier and Preview from closed mission fields. It is local, read-only, non-promoting, and cannot dispatch, call the adapter, write a branch or PR, mark ready, merge, or change settings.

That constructor is not an external origin bridge and no longer carries a CAP-015 or AJ-01 proof burden. Its live hosted acceptance remains evidence for RP-C01-M08 and guided usability only.

## Guided hosted publisher

The owner-guided publisher is a Jayson/Artemis Arrow/Bow launcher over the existing hosted workflow. Preview audits canonical main, workflow identity, carrier, privacy, hosted-supported paths, and compiler output without mutation. Execute requires exact Preview identity, revalidates drift, reserves durable no-retry intent, dispatches only the existing hosted workflow, and reads back the run.

The guided publisher may not call the adapter directly, create or update a branch or PR, retry partial state, mark ready, merge, change settings, or become a second writer. CAP-010 is already accepted from its separate live journey and does not establish or limit Athena's Spear identity.

## Generated explicit owner-dispatch route

Canonical `main` pushes do not launch `.github/workflows/generated-checkpoint-publisher.yml`. An explicit owner `workflow_dispatch`, bound to exact current `main`, is the only hosted entrypoint. The read-only queue admission and singular Thread Engine preserve exact identity, parity, replay, path, draft-readback, and no-automatic-permanence boundaries.

Current reports return successful `NOOP` with no mission, commit, branch, PR, or self-dispatch. Accumulated source changes produce one full five-file mission and one fresh deterministic generated-only draft; a partial delta fails closed. Closing a generated draft without merge does not move `main` or automatically restart the publisher.

This explicit generated route is not Spear, Phoenix Blade, Aegis Break, or Bow/Arrow route ownership. It never automatically readies or merges the generated PR.

## Evidence and promotion boundary

This realignment uses already merged evidence and the current implementation regression; it does not manufacture operating proof:

- direct Spear PR `#102` proves Athena-to-Thread-Engine mechanics;
- merged parity proof preserves direct Spear and Arrow/Bow compiler equivalence;
- Oathbringer production acceptance proves the Sword operation set used by Phoenix Blade's counterpart definition;
- protected dispatch PR `#187` remains historical evidence of the former path-gated model.

CAP-015, AJ-01, RP-C01-M02, and RP-C01-M06 remain reconciled by their respective accepted evidence. The universal-path change alters authoring scope, not permanence or capability-promotion authority.
