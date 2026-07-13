---
title: "Shared Agentic Warrant Contract"
atlas_id: "prime.governance.agentic-warrant-contract"
status: "CANONICAL_ACTIVE"
source_type: "PROTOCOL"
authority_class: "CANONICAL_AUTHORED_SOURCE"
owner_project: "Project Codex"
owner_operation: "Operation Source Governance"
protected_level: "CRITICAL"
---

# Shared agentic warrant contract

An agent may act only through an exact capability warrant. A role name, model,
provider, conversation, work surface, tool connection, earlier success, or
parent warrant never grants authority by itself. The warrant is a bounded
authorization record, not a credential and not a standing repository writer.

## Identity and authority separation

Every warrant independently binds stable warrant and agent IDs, role,
implementation, provider, model, work surface, human authorizer, credential
principal, token mode, repository, exact base SHA, allowed actions and paths,
route, protected posture, stop boundary, Preview digest, required checks,
candidate-tree evidence, expiry, lifecycle state, delegation, approvals,
rollback, and forbidden actions.

The semantic agent, credential principal, authorizer, launcher, route, engine,
and work surface are different identities. None may impersonate another. A
model or provider change does not preserve authority unless a new or updated
warrant binds the new identity explicitly.

## Lifecycle

```text
DRAFT -> ACTIVE
ACTIVE -> SUSPENDED -> ACTIVE
ACTIVE|SUSPENDED -> REVOKED|EXPIRED|REPLACED
REVOKED|EXPIRED|REPLACED -> terminal
```

Activation requires a separate approval record that binds the exact warrant
body and scope, is accepted by a trusted authorizer verifier, and expires no
more than 24 hours after issue. A name or self-authored signature string is not
authorization. Suspension blocks new action without erasing evidence.
Revocation is immediate and terminal. Expiry is terminal. Replacement creates
a new warrant with its own scope and evidence, and both records cross-link the
replacement; authority is never inherited silently.

## Delegation

Delegation is denied unless the parent explicitly allows it. A child has a new
warrant and agent identity, names exactly one parent, has depth one, uses only a
subset of the parent's actions and paths, keeps the same repository and base,
and cannot relax protected, stop, approval, rollback, or forbidden controls.
It carries its own authorizer, principal, expiry, Preview, evidence, and receipt.
No transitive, wildcard, role-based, conversational, provider-derived, or
standing delegation exists. A suspended, revoked, expired, or replaced parent
invalidates every child immediately; a child never outlives its active parent.

## Human approval and routes

Build authority never implies Execute, ready, merge, settings, provider/account
activation, private-data ingress, or permanence. Ready, merge, settings,
provider activation, protected execution, and destructive action each require
an explicit human approval record at the exact action boundary. That record
binds the attempted request digest and cannot authorize a different request.
Prime routes remain governed by `governance/change-routes.md`; a warrant cannot
invent a writer or bypass Aegis. The route/action matrix is closed. Any mutating
path classified by `policies/protected-paths.json` requires the
`AEGIS_BREAK_PROTECTED` route and protected-action approval. Private-data
ingress is forbidden in v1 (`private_data_allowed` is always `false`).

In the machine warrant, a `human_approval` value of `true` means approval is
required, not that approval has already been granted. The receipt supplies the
separate approval-record digest when a required action is actually attempted.

## Receipts and fail-closed behavior

Every attempt produces a receipt conforming to
`schemas/agentic-warrant-receipt-v1.schema.json`. It binds the canonical warrant
SHA-256, observed agent and principal, base/head, route, action/path inventory,
approval records, exact request digest, Preview and candidate-tree evidence,
completed checks, result, stop, rollback, and forbidden confirmation. Request
digest plus receipt, attempt, and nonce identity is consumed by a required
replay guard; repeated request or receipt identity is rejected before the
receipt can be accepted.

Reject before mutation on missing, malformed, inactive, suspended, revoked,
expired, replaced, mismatched, stale, over-broad, transitive, or unsigned
authority; principal or agent mismatch; unapproved protected or permanence
action; route drift; evidence failure; replay; or action outside the warrant.
Rejection never edits the warrant, retries partial state, or broadens scope.
A `REJECTED` or `BLOCKED` receipt for an invalid or inactive warrant is valid
only when its error code matches the validator's fail-closed reason, records no
head or approval, preserves the exact attempted scope, and passes replay
consumption.

The machine contracts are
`schemas/agentic-capability-warrant-v1.schema.json`,
`schemas/agentic-approval-record-v1.schema.json`, and
`schemas/agentic-warrant-receipt-v1.schema.json`. Fixtures and whole-program
tests prove structural closure and lifecycle semantics. This contract grants
no capability or journey promotion by itself.
