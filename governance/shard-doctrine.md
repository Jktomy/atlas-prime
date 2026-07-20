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

Shardplate is the AI-assisted work surface. It may help read, reason, draft, test, or prepare a candidate only through a separately authorized construction route. Shardplate grants no mutation, credential, route, launcher, engine, candidate, approval, provider, Light, or permanence authority. A provider, model, account, tool connection, or earlier success cannot turn Shardplate into an authorizer or writer.

## Shardblade

Shardblade is the bounded permanence actuator for one exact Jayson-authorized candidate. It is not an agent, model, provider, Light, work surface, construction route, source author, repair worker, repository-settings manager, or standing authority.

`governance/repository-process-contract.md` controls ordinary use.

### Default and explicit permanence modes

The default normal Prime route stops at one unchanged merge-ready pull request. Athena reports `Prime PR #___ is ready to merge.` and Jayson performs the normal manual merge.

A current explicit Jayson instruction containing `with Shardblade` or an unambiguous equivalent grants one transaction-scoped machine permanence action for the exact unchanged candidate. This authority:

- belongs only to the named transaction;
- is not inferred from Build, Execute, READY, GREEN, route identity, tool access, prior approval, or prior success;
- is consumed by one successful merge or one terminal safe rejection;
- cannot be reused for changed bytes, another head, another PR, another repository, or a later transaction.

Goddess Mode may carry the same bounded transaction through construction, validation, review repair, and final evidence collection, but it never creates Shardblade authority by itself.

### Exact merge gate

Before mutation, the invoking adapter must freshly verify:

- repository, base branch, current base SHA, PR, source branch, and open state;
- exact expected head SHA and candidate tree;
- sorted complete changed-path inventory and its digest;
- protected-path construction authority;
- final required status results for that exact head;
- review reconciliation with no blocking finding;
- exact-head Strikeforce GREEN;
- declared merge method;
- replay reservation, interruption posture, rollback, and transaction identity.

The merge request must bind the expected head SHA through repository compare-and-swap or an equivalent atomic condition. A moved head, changed tree, changed path set, missing status, pending or blocking review, stale authority, duplicate reservation, or unreadable evidence rejects without mutation.

Shardblade may not author, modify, repair, widen, substitute, bypass checks, select another head, alter settings, force-push, write directly to main, conceal partial state, or blind-retry an ambiguous result.

### Readback and recovery

Immediately after mutation, the actuator records:

- unchanged transaction, PR, head, tree, and path identity;
- merge result and merge SHA;
- final PR state;
- canonical-main SHA and tree readback;
- receipt identity and authority consumption;
- rollback classification.

An interruption or ambiguous mutation result stops automatic action. Recovery is readback-only reconciliation against the exact transaction and remote state, never a blind retry. Pre-merge rollback is closing the PR. Post-merge rollback is a separately reviewed repair-forward or revert PR. History rewrite is forbidden.

## Legacy dedicated warrant contracts

The front-matter value `CONTRACT_ONLY_NOT_ACTIVATED` applies specifically to the older dedicated READY/MERGE warrant implementation in:

- `schemas/shardblade-permanence-request-v1.schema.json`;
- `schemas/shardblade-permanence-approval-v1.schema.json`;
- `schemas/shardblade-permanence-receipt-v1.schema.json`;
- `tools/agentic_warrants/permanence.py`.

Those contracts preserve valuable exact-candidate, replay, approval, receipt, and rollback semantics. Their presence and passing fixture tests do not establish a standing production service, credential, scheduler, campaign bot, or generic machine authority.

The ordinary transaction-scoped meaning above does not activate standing warrants. It allows one exact merge only when the current Jayson instruction explicitly invokes Shardblade and the available adapter proves the required exact-head, compare-and-swap, status, review, Strikeforce, replay, and canonical-readback conditions.

The legacy dedicated contract keeps READY and MERGE distinct and non-substitutable:

- `READY` changes one exact draft PR to open ready state without changing its candidate;
- `MERGE` makes that same exact ready candidate canonical only through a separately bound action.

A legacy successful READY receipt is evidence, not reusable approval. Combined READY+MERGE, automatic retry, approval reuse, candidate substitution, and standing delegation remain forbidden.

## Campaign compatibility

An exact bounded campaign warrant may define predetermined stages, but each stage remains exact, expiring, replay-resistant, and limited to its declared candidate and action. Campaign GREEN creates no authority. Campaign Goddess Mode cannot self-renew or convert campaign construction authority into permanence.

When a campaign invokes Shardblade, the current stage must carry exact transaction-scoped permanence authority, fresh exact-head evidence, and one-use reservation. Changed candidate bytes invalidate the prior stage evidence and require a new exact current action.

## Implementation boundary

Existing Oathbringer EXECUTE mechanics and exact GitHub adapters may provide proven transport and compare-and-swap primitives. Reuse of those primitives does not grant standing authority or permit a different candidate.

Future Coppermind, Emberdark, Phoenix, Gitea, or dedicated Shardblade services must preserve these semantics. Architecture source or schema presence does not prove deployment, credentials, runtime activation, settings configuration, or cutover.
