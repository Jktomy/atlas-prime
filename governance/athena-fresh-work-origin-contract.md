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

This contract adds the missing fresh ChatGPT Work/Athena origin boundary to the
already accepted owner-guided publisher. It does not replace the hosted Bow
workflow, Spear compiler, singular Thread Engine, or any accepted v1 receipt.

Construction, schemas, local tests, and a draft pull request do not prove
`CAP-015`, `AJ-01`, `RP-C01-M02`, or the `ATHENA_NATIVE_EXECUTION_ROUTES_PROVEN`
gate. Those identities remain unproven until one genuinely fresh Jayson-started
Work/Athena task completes the required live journey and a separate authored
reconciliation accepts the evidence.

## Existing route remains singular

```text
fresh Work/Athena origin receipt
  -> trusted external origin verifier
  -> exact existing guided Preview
  -> exact existing guided Execute
  -> existing athena-bow-hosted workflow
  -> existing Spear compiler
  -> singular existing Thread Engine
  -> one immutable branch
  -> one draft pull request
  -> exact readback
```

The bridge wraps the existing guided publisher. It contains no Git tree,
commit, branch, push, pull-request, ready, merge, cleanup, settings, credential,
adapter, or second-writer implementation. The hosted route remains the sole
source of mutation and rollback truth.

## Identity separation

The bridge keeps these identities distinct:

- human authorizer: `Jayson`;
- semantic invoker: `Athena`;
- originating surface: `CHATGPT_WORK`;
- privacy-safe task identity SHA-256;
- origin nonce SHA-256;
- GitHub actor and triggering actor from the hosted workflow;
- hosted workflow source, run, and attempt;
- ephemeral GitHub Actions credential principal;
- singular Thread Engine identity and receipts.

The existing hosted v1 receipt may retain its historical owner-guided route
labels. The fresh Work journey receipt is a separate outer receipt that binds a
verified external origin to the exact guided Execute receipt and hosted run. It
must never rewrite or reinterpret accepted historical evidence.

## Trusted verifier gate

A caller-authored JSON statement, prompt, screenshot, transcript, or string that
claims `Athena` or `ChatGPT Work` is not origin proof.

Before dispatch, the bridge requires an independently trusted verifier supplied
by the platform runtime. The verifier must affirm exactly:

- verification method;
- verification evidence SHA-256;
- task identity SHA-256;
- origin nonce SHA-256.

The only accepted verification methods are:

```text
PLATFORM_SIGNED_ATTESTATION
INDEPENDENT_PLATFORM_READBACK
```

If no trusted verifier is available, the bridge returns
`TRUSTED_ORIGIN_VERIFIER_UNAVAILABLE`, records no remote dispatch, and leaves
`CAP-015` missing. Verification failure or field drift also stops before
dispatch. The command-line entry point deliberately supplies no verifier; a
future platform-runtime integration must inject the trusted verifier through
the library API rather than through caller-controlled command arguments,
environment strings, shell commands, or repository content.

## Closed origin receipt

`schemas/athena-fresh-work-origin-receipt-v1.schema.json` is closed and accepts
only public-safe hashes and bounded timestamps. It binds:

- issuer and verification method;
- authorizer, semantic invoker, and originating surface;
- task identity and origin nonce hashes;
- issued and expiry timestamps;
- mission, canonical base, carrier, Preview, and workflow-blob identities;
- verification-evidence digest;
- explicit confirmation that raw task or conversation identifiers, transcript,
  prompt, account email, credentials, paths, network values, and private data
  are absent.

The origin receipt lifetime is at most fifteen minutes. It must be canonical
UTF-8 JSON, a regular file, size bounded, outside canonical Prime source, and
valid at the moment of verification.

## Exact binding and privacy boundary

Before dispatch, the bridge independently re-hashes the local carrier and
Preview and requires exact equality with the origin receipt for:

- Preview SHA-256;
- carrier SHA-256;
- mission identity;
- canonical-main SHA;
- hosted workflow blob SHA.

Origin, Preview, carrier, guided Execute receipt, and journey receipt remain
outside canonical Prime source. Raw task identifiers, conversations, prompts,
transcripts, account identifiers, local paths, credentials, private runtime
values, network values, PHI, finance/account material, and private exports never
enter GitHub through this bridge.

## Durable intent and partial-state rule

After origin verification and before invoking guided Execute, the bridge
exclusively reserves the journey receipt and records a no-retry intent. Guided
Execute independently retains its existing durable intent and dispatch
readback.

If dispatch is ambiguous, readback fails, or final journey publication fails:

```text
PARTIAL_STATE_PRESERVED
PRESERVE_AND_REVIEW_NO_RETRY
```

Do not retry, reuse the origin nonce, mission, branch, pull request, carrier, or
receipt path. Do not force-update, delete, clean up, or rewrite history. The
preserved bridge intent and hosted-route receipt govern.

## Journey receipt

`schemas/athena-fresh-work-journey-receipt-v1.schema.json` records exactly one of:

- `BLOCKED` before dispatch;
- `DISPATCHED` with exact hosted workflow run readback;
- `PARTIAL` with preserved no-retry state.

The receipt binds the external origin receipt digest, verifier evidence digest,
task and nonce hashes, Preview, carrier, mission, base, workflow blob, guided
Execute receipt digest, and hosted workflow run identity when known. It records
that the bridge itself performed no Git or pull-request mutation and grants no
standing authority.

## Construction and live acceptance boundaries

This construction transaction may add the contract, schemas, bridge library,
tests, routing, and validation only. It must not change the hosted workflow,
Thread Engine, capability register, Repairing Prime Quest state, Quest Board,
continuity register, generated projections, or acceptance evidence.

A later live journey must begin in a genuinely new Jayson-started Work/Athena
task and prove:

1. independently verified fresh origin;
2. exact origin-to-carrier-to-Preview binding;
3. one existing guided publisher dispatch;
4. one hosted workflow run through the singular Thread Engine;
5. one immutable mission branch and draft pull request;
6. exact remote path, blob, tree, base, branch, head, and draft-state readback;
7. exact-head Ubuntu and Windows validation;
8. detached exact-head review;
9. checksummed public-clean evidence with raw origin material kept outside GitHub;
10. stop at the open unmerged draft pull request.

Only a separate reviewed authored reconciliation may then consider promotion of
`CAP-015`, `AJ-01`, `RP-C01-M02`, or the RP-C01 gate.
