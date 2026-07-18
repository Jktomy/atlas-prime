---
title: "Prime Shardplate and Shardblade Doctrine"
atlas_id: "prime.governance.shard-doctrine"
status: "CANONICAL_ACTIVE"
activation_state: "CONTRACT_ONLY_NOT_ACTIVATED"
source_type: "PROTOCOL"
authority_class: "CANONICAL_AUTHORED_SOURCE"
owner_project: "Project Codex"
owner_operation: "Operation Source Governance"
protected_level: "CRITICAL"
---

# Prime Shardplate and Shardblade doctrine

## Shardplate

Shardplate is the AI-assisted work surface. It may help read, reason, draft,
test, or prepare a candidate only through a separately authorized construction
route. Shardplate grants no mutation, credential, route, launcher, engine,
candidate, approval, provider, Light, or permanence authority. A provider,
model, account, tool connection, or earlier success cannot turn Shardplate into
an authorizer or writer.

## Shardblade

Shardblade is the bounded permanence executor for an exact Jayson-approved
candidate or campaign warrant. It is not an agent, model, provider, Light, work
surface, construction route, repository writer, or standing authority.

Both `READY` and `MERGE` are Shardblade actions, but they are distinct and
non-substitutable:

- `READY` changes one exact draft PR to the reviewable ready state without
  changing its base, head, tree, or path inventory.
- `MERGE` makes that same exact ready candidate canonical only after a fresh
  readback and a new Jayson approval.

READY authority never implies MERGE authority. Strikeforce GREEN establishes
readiness; Shardblade is the separate authority that permits merging the
reviewed exact head. A successful READY receipt is evidence, not approval. Each action has a different request ID and digest,
approval ID and nonce, attempt and receipt identity, stop point, and readback.
Delegation, standing approval, combined READY+MERGE, automatic retry, and
approval reuse are forbidden.

## Campaign Shardblade

One exact Jayson-approved campaign warrant may prospectively authorize separate
READY and MERGE operations for predetermined stages. Every operation still
requires a stage child request binding the current canonical base, campaign
digest, PR, branch, head, tree, complete changed-path inventory, Preview,
construction receipt, exact-head checks, Noctua, Ares, Athena, Strikeforce,
Copilot dispositions, rollback, and protected-path posture. After READY,
Campaign Shardblade requires a fresh unchanged-candidate readback and a new
MERGE request. Each operation has its own nonce, replay reservation, and
immutable receipt.

Campaign Shardblade receives authority from the campaign warrant, not from
GREEN. It cannot author, repair, widen, substitute, self-renew, retry ambiguity,
or merge a different head. It stops and expires with the campaign. The existing
single-candidate route remains valid and separate.

Shardblade may not author, modify, repair, widen, substitute, bypass checks,
change the candidate head, select an undeclared merge method, or conceal a
partial result. Build or Execute authority never implies either Shardblade
action.

## Exact candidate and evidence

Every action request binds the repository, current `main` SHA, PR and source
branch, PR state, exact head and tree, sorted complete path inventory, Preview,
construction receipt, exact protected-path subset and construction approval,
pull-request readback, exact-head Ubuntu and Windows run identities, workflow
source, and detached GREEN review. Protected paths must already have their
applicable construction authority; Shardblade cannot create it after the fact.

A MERGE request additionally binds the SHA-256 of one successful READY receipt,
the unchanged candidate and evidence, a new `OPEN_READY` readback taken after
READY, and the declared merge method. Its direct Jayson approval is issued only
after that fresh readback.

Immediately before mutation, the invoking adapter must compare-and-swap the
exact PR head and re-read base, tree, paths, CI, and review. After mutation, the
receipt records unchanged candidate identity, final PR state, merge SHA, and
canonical-main/tree readback. Pre-merge rollback is closing the PR; post-merge
rollback is a separately reviewed revert PR. History rewrite is never allowed.

## Replay, interruption, and recovery

The caller must durably and atomically reserve the request digest, request and
approval identities before mutation, then consume the receipt identity. A
replay, duplicate nonce, ambiguous mutation result, interruption, or delayed
readback stops automatic action. Recovery is readback-only reconciliation;
never a blind retry.

The machine contracts are
`schemas/shardblade-permanence-request-v1.schema.json`,
`schemas/shardblade-permanence-approval-v1.schema.json`, and
`schemas/shardblade-permanence-receipt-v1.schema.json`, validated by
`tools/agentic_warrants/permanence.py`. Validation proves only that supplied
objects satisfy this contract. It does not perform GitHub mutation, prove that
the supplied readbacks came from GitHub, or grant permanence by itself.

The bounded campaign contracts are
`schemas/shardblade-campaign-warrant-v1.schema.json`,
`schemas/shardblade-campaign-stage-request-v1.schema.json`, and
`schemas/shardblade-campaign-stage-receipt-v1.schema.json`, validated by
`tools/agentic_warrants/campaign.py`. They enforce stage, expiry, exact path,
review, READY-chain, readback, replay, receipt, and rollback bindings without
turning a campaign warrant into a credential or standing authority.

The single-candidate source layer is `CONTRACT_ONLY_NOT_ACTIVATED`. No
production Shardblade route is accepted yet. Activation still requires a
trusted GitHub adapter that
proves the construction and protected-path approvals, canonical-base policy,
PR readback, workflow source and exact run identities, detached-review origin,
atomic request reservation, mutation compare-and-swap, and final readback, plus
a live direct-Jayson READY journey and a separately approved MERGE journey.
Digest-shaped fixture values, passing unit tests, or this contract's presence
are not that evidence and may not promote the route.

The accepted RP-C02 v1 agentic-warrant evidence remains historical structural
proof. Its generic validator is not a production permanence executor and now
rejects v1 READY, MERGE, and `SHARDBLADE_PERMANENCE` authority in favor of this
dedicated boundary. Current Oathbringer EXECUTE compatibility remains subject
to the separate Sword-route reliability transaction; this doctrine does not
self-certify that journey.
