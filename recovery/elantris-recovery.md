---
title: "Prime Elantris Recovery"
atlas_id: "prime.recovery.elantris"
status: "ACTIVE"
source_type: "RUNBOOK"
authority_class: "CANONICAL_AUTHORED_SOURCE"
owner_project: "Project Elantris"
owner_operation: "Operation Restore Runbook"
protected_level: "CRITICAL"
---

# Prime Elantris Recovery

Prime recovery begins from a clean clone of `Jktomy/atlas-prime`, a verified main head, and the exact Receipt Gemstone. Normal restoration must not require `Jktomy/atlas-codex`, Athena, Harmony, Coppermind, an active transaction store, or the normal repository publisher.

## Recovery sequence

1. Verify repository identity, remote, default branch, expected head, and receipt hashes.
2. Clone without inherited worktrees, hooks, generated output, caches, or local configuration.
3. Run kernel, repository-policy, privacy, Thread Engine, generator, and whole-program checks.
4. Regenerate projections into a separate output directory and compare deterministically.
5. Verify Thread Engine state and its isolated disablement path.
6. Verify Sword/Oathbringer can classify the recovery point without blind replay.
7. Reconcile any unfinished repository transaction from exact branch, PR, head, tree, paths, receipts, and remote state before resuming; never create a duplicate mission because one operator surface is unavailable.
8. Reconcile any unfinished Sunset from its exact Preview, approval, carrier, semantic digest, scope, and current state before compiling or publishing.
9. Restore only declared external runtime configuration from its approved backup system; never infer private values from source.
10. Perform a destructive canary restore only with explicit Jayson-side authority and a protected evidence plan.
11. Read back recovered source and runtime evidence before declaring success.

## Repository-process recovery boundary

Every source transaction records or permits reconstruction of:

- transaction and objective identity;
- canonical base, branch, PR, head, tree, and complete changed paths;
- candidate generation and payload hashes;
- requesting surface, operator, selected route, and authorized fallback routes;
- validation plan, exact-head results, review dispositions, and generated-state classification;
- Strikeforce verdict, permanence mode, merge receipt, canonical readback, and rollback classification.

Before Coppermind is separately proven, route-neutral sanitized manifests and append-only receipts may preserve this state outside canonical source. They are recovery evidence, not authority. Loss of that compatibility layer must not prevent clean-clone recovery of merged Prime.

A blocked Thread Engine route may fall back to exact Sword/Oathbringer only after read-only reconciliation proves the existing transaction state. The alternate route resumes the same transaction; it does not create a second branch or PR.

For explicit Shardblade action, the expected head SHA must be atomically bound to the merge request. An interruption or ambiguous result enters readback-only reconciliation. Never blindly retry a merge. If the exact candidate is already merged, verify canonical main and close the transaction. If it is not merged and authority remains valid, re-establish exact evidence before any new attempt.

## Sunset recovery boundary

A Sunset is recoverable from:

- exact Preview and Preview digest;
- exact Jayson approval and permanence mode;
- approved route-neutral carrier and semantic payload digest;
- Project, Operation, Quest scope, protected boundary, and record plan;
- proposed Feather meaning, decisions, open items, blockers, next gates, and Lesson Harvest;
- selected route, fallback routes, current carrier state, and any existing branch or PR.

A missing publisher, local clone, connector, or network path changes the carrier to `BLOCKED_RESUMABLE`; it does not terminate or replace the save point. Athena, Harmony, and Jayson PowerShell may resume the same carrier after read-only reconciliation. Any semantic change requires a new Preview and explicitly supersedes the old carrier.

No recovery route may manufacture a lifecycle source fingerprint, recreate an approval from chat memory, substitute a narrative summary, or report `SUNSET COMPLETE` before canonical merged-main readback.

## Prometheus's Fire recovery boundary

The Prometheus architecture requires narrow Forge mounts with safe unavailable-mount behavior, Prometheus guest backups, a destructive canary restore, and an independent recovery copy not confined to Forge.

Harmony recovery must include the Harmony VM, accelerator detachment and reattachment safety, model/runtime configuration, backup, restoration, thermal and soak evidence, and rollback without making host administration depend on the accelerator.

These are future proof requirements. This runbook does not claim that any backup, restore, deployment, migration, Gitea activation, cutover, or runtime action has occurred. Recovery receipts must be sanitized and must not contain secrets, private runtime values, or protected records.

## Rollback

- Every source transaction records base, head, tree, paths, payload hashes, PR, merge, and recovery classification.
- A source rollback uses a new reviewed PR; no force push or history rewrite is required.
- Thread Engine emergency disablement changes the reviewed activation state through Aegis Break → Oathbringer.
- Historical lifecycle records are not rewritten; a changed Sunset plan requires a new Preview and supersession.
- The frozen Codex predecessor remains audit evidence only and is never the normal rollback target after cutover.

RAID, snapshots, a green backup job, an undeleted predecessor, or a merge API success response are not restore proof. Recovery is proven only by exact restoration and readback.
