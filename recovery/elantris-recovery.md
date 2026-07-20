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
8. Restore only declared external runtime configuration from its approved backup system; never infer private values from source.
9. Perform a destructive canary restore only with explicit Jayson-side authority and a protected evidence plan.
10. Read back recovered source and runtime evidence before declaring success.

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

## Prometheus's Fire recovery boundary

The Prometheus architecture requires narrow Forge mounts with safe unavailable-mount behavior, Prometheus guest backups, a destructive canary restore, and an independent recovery copy not confined to Forge.

Harmony recovery must include the Harmony VM, Intel Arc Pro B50 detachment and reattachment safety, model/runtime configuration, backup, restoration, thermal and soak evidence, and rollback without making host administration depend on the accelerator.

Atlas recovery must include:

- complete Atlas VM backup and restoration under a different guest ID;
- independently bounded OS/application, Coppermind, Phoenix, and Emberdark storage areas;
- Emberdark application and workflow-state restoration;
- PostgreSQL base backups, WAL protection, and a point-in-time recovery direction;
- Phoenix repository, Gitea application-state, and database consistency restoration;
- selective service restoration as well as full-VM restoration;
- an independent repository mirror and clean-clone Prime recovery that does not depend on the Atlas VM.

Plex recovery must include its local-NVMe database, metadata, configuration, and durable application state. Cache and transcode workspace are disposable and need not be restored as durable evidence. Media and completed DVR media remain on Forge/Anvil through narrow paths. Plex restoration must prove Quick Sync, playback, recording, reboot recovery, safe mount loss, and rollback.

Household media continuity is intentionally degraded rather than seamless high availability:

- local-only Jellyfin on Forge may read stored media and completed DVR recordings through its own database and metadata;
- the Samsung television's direct antenna input remains the live-TV continuity route;
- Jellyfin is not a Plex standby and shares no Plex application database;
- during a Plex or Prometheus outage, new scheduled recordings and in-progress recordings are not guaranteed;
- failure of Forge/Anvil removes stored-media continuity even when Prometheus remains healthy.

Temporary restore guests require an explicit RAM reallocation or guest-shutdown plan. The 8 GB protected Proxmox reserve is not consumed merely to simplify a restoration exercise.

These are future proof requirements. This runbook and the Prometheus Quest do not claim that any backup, restore, deployment, migration, Jellyfin installation, Gitea activation, Plex cutover, or runtime action has occurred. Recovery receipts must be sanitized and must not contain secrets, private runtime values, or protected records.

## Rollback

- Every source transaction records base, head, tree, paths, payload hashes, PR, merge, and recovery classification.
- A source rollback uses a new reviewed PR; no force push or history rewrite is required.
- Thread Engine emergency disablement changes the reviewed activation state through Aegis Break → Oathbringer and must reject at `ACTIVATION_GATE` before mission parsing.
- The original Prime shadow head remains preserved by the locked archive branch and annotated tag.
- The frozen Codex predecessor remains audit evidence only and is never the normal rollback target after cutover.
- Before final Forge Plex removal, a separately authorized migration rollback may temporarily restore service to Forge Plex. After final removal, stored-media continuity is Jellyfin, live-TV continuity is the direct antenna, and normal Plex service returns through restoration of the Prometheus Plex LXC.

RAID, snapshots, a green backup job, an undeleted predecessor, the presence of Jellyfin, or a merge API success response are not restore proof. Recovery is proven only by exact restoration and readback.
