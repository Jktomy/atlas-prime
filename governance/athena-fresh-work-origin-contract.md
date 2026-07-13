---
title: "Athena Fresh Work Origin Bridge Contract"
atlas_id: "prime.governance.athena-fresh-work-origin"
status: "CONSTRUCTION_ONLY_NOT_ACTIVATED"
source_type: "PROTOCOL"
authority_class: "CANONICAL_AUTHORED_SOURCE"
owner_project: "Project Codex"
owner_operation: "Operation Source Governance"
protected_level: "CRITICAL"
routes_from:
  - "governance/athena-execution-route-contract.md"
  - "routing/command-surfaces.md"
routes_to:
  - "schemas/athena-fresh-work-origin-receipt-v1.schema.json"
  - "schemas/athena-fresh-work-journey-receipt-v1.schema.json"
  - "tools/athena_routes/fresh_work_bridge.py"
---

# Athena Fresh Work Origin Bridge Contract

This contract defines the missing fresh ChatGPT Work/Athena origin boundary for
the already accepted owner-guided route. It does not replace the hosted Bow
workflow, Spear compiler, singular existing Thread Engine, or any accepted v1
receipt.

Construction, schemas, local tests, a read-only origin plan, and a draft pull
request do not prove `CAP-015`, `AJ-01`, `RP-C01-M02`, or the
`ATHENA_NATIVE_EXECUTION_ROUTES_PROVEN` gate. Those identities remain unproven
until a genuinely fresh Jayson-started Work/Athena task completes the live
journey and a separate reviewed authored reconciliation accepts the evidence.

## Construction boundary

The current construction has no dispatch-capable implementation. It may:

1. validate a closed public-safe origin receipt;
2. re-hash and bind the exact carrier and guided Preview;
3. consume an independently obtained full-binding platform readback;
4. produce only a read-only, non-executable dispatch plan; or
5. record the truthful `TRUSTED_ORIGIN_VERIFIER_UNAVAILABLE` blocked state.

It may not invoke guided Execute, dispatch a workflow, call the adapter, create
or update a branch or pull request, mark ready, merge, change settings, clean
up remote state, load a verifier dynamically, accept trust through command-line
or environment strings, or become a second writer.

The intended future route remains:

```text
fresh Work/Athena origin receipt
  -> trusted platform-origin readback
  -> exact read-only binding plan
  -> separately authorized protected integration
  -> existing guided Execute
  -> existing athena-bow-hosted workflow
  -> existing Spear compiler
  -> singular existing Thread Engine
  -> one immutable branch
  -> one draft pull request
  -> exact readback
```

The arrow between the read-only plan and guided Execute is deliberately absent
from this construction. Adding it requires a later protected Preview and
separate Jayson authorization after an actual platform trust anchor exists.

## Identity separation

The origin boundary keeps these identities distinct:

- human authorizer: `Jayson`;
- semantic invoker: `Athena`;
- originating surface: `CHATGPT_WORK`;
- privacy-safe task identity SHA-256;
- origin nonce SHA-256;
- canonical mission, base, carrier, Preview, and workflow-blob identities;
- GitHub actor and triggering actor from a later hosted workflow;
- hosted workflow source, run, and attempt;
- ephemeral GitHub Actions credential principal;
- singular Thread Engine identity and receipts.

The existing hosted v1 receipt retains its historical owner-guided labels. A
future fresh Work journey receipt will be a separate outer receipt that binds a
verified external origin to the exact guided Execute receipt and hosted run. It
must never rewrite or reinterpret accepted historical evidence.

## Trusted platform readback

A caller-authored JSON statement, callable, prompt, screenshot, transcript,
repository file, command argument, or environment value that claims `Athena` or
`ChatGPT Work` is not origin proof.

The read-only planner accepts a readback interface only as a construction seam
for platform integration tests. Its output is always
`READ_ONLY_CANDIDATE_NOT_EXECUTABLE`, carries
`remote_dispatch_authority=false`, and cannot invoke the guided publisher.
Consequently, even a false test double cannot cause a remote mutation.

A real future platform integration must independently bind all of:

- origin receipt SHA-256;
- verification method;
- verification evidence SHA-256;
- task identity SHA-256;
- origin nonce SHA-256;
- mission identity;
- canonical base SHA;
- carrier SHA-256;
- Preview SHA-256;
- hosted workflow blob SHA.

The only contract-eligible verification methods are:

```text
PLATFORM_SIGNED_ATTESTATION
INDEPENDENT_PLATFORM_READBACK
```

If no trusted platform readback exists, the command-line boundary records
`TRUSTED_ORIGIN_VERIFIER_UNAVAILABLE`, reports no remote dispatch possibility,
and leaves `CAP-015` missing.

## Closed origin receipt

`schemas/athena-fresh-work-origin-receipt-v1.schema.json` is closed and accepts
only public-safe hashes and bounded timestamps. It binds issuer, verification
method, authorizer, semantic invoker, originating surface, task and nonce
hashes, mission, base, carrier, Preview, workflow blob, and verification
evidence digest.

It also requires explicit confirmation that raw task or conversation
identifiers, transcripts, prompts, account email, credentials, local paths,
network values, and private data are absent. The receipt lifetime is at most
fifteen minutes. It must be canonical UTF-8 JSON, a regular file, size-bounded,
outside canonical Prime source, and valid at the moment of readback.

## Exact binding and privacy boundary

Before producing a read-only plan, the construction independently re-hashes the
carrier and Preview and requires exact equality with the origin receipt for:

- Preview SHA-256;
- carrier SHA-256;
- mission identity;
- canonical-main SHA;
- hosted workflow blob SHA.

Origin, Preview, carrier, blocked journey receipt, and any future guided receipt
remain outside canonical Prime source. Raw task identifiers, conversations,
prompts, transcripts, account identifiers, local paths, credentials, private
runtime values, network values, PHI, finance/account material, and private
exports never enter GitHub through this boundary.

## Blocked and future journey receipts

The current command-line surface can emit only a closed `BLOCKED` journey
receipt with:

```text
PRE_DISPATCH_BLOCKED
NO_REMOTE_MUTATION
remote_dispatch_possible=false
```

`schemas/athena-fresh-work-journey-receipt-v1.schema.json` also reserves
`DISPATCHED` and `PARTIAL` states for a later protected platform integration.
Their presence in the schema is not current implementation or authority.
Current source tests prohibit imports or calls to guided Execute and prohibit
workflow-dispatch or repository-writer implementations.

A future integration that can dispatch must first add durable no-retry intent,
exact guided receipt binding, and truthful partial-state conservation through a
separate protected transaction. Ambiguous dispatch must remain
`PARTIAL_STATE_PRESERVED` with `PRESERVE_AND_REVIEW_NO_RETRY`.

## Construction and live acceptance boundaries

This transaction may add only the contract, schemas, read-only bridge library,
tests, routing, and documentation. It must not change the hosted workflow,
guided publisher, Thread Engine, capability register, Repairing Prime Quest,
Quest Board, continuity register, generated projections, or acceptance
evidence.

A later live journey must begin in a genuinely new Jayson-started Work/Athena
task and prove:

1. independently verified fresh origin;
2. exact origin-to-carrier-to-Preview binding;
3. one separately authorized integration into existing guided Execute;
4. one hosted workflow run through the singular Thread Engine;
5. one immutable mission branch and draft pull request;
6. exact remote path, blob, tree, base, branch, head, and draft-state readback;
7. exact-head Ubuntu and Windows validation;
8. detached exact-head review;
9. checksummed public-clean evidence with raw origin material kept outside GitHub;
10. stop at the open unmerged draft pull request.

Only a separate reviewed authored reconciliation may then consider promotion of
`CAP-015`, `AJ-01`, `RP-C01-M02`, or the RP-C01 gate.
