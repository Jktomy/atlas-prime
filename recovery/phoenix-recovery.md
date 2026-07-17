---
title: "Prime Phoenix Recovery"
atlas_id: "prime.recovery.phoenix"
status: "ACTIVE"
source_type: "RUNBOOK"
authority_class: "CANONICAL_AUTHORED_SOURCE"
owner_project: "Project Phoenix"
owner_operation: "Operation Restore Runbook"
protected_level: "CRITICAL"
---

# Prime Phoenix Recovery

Prime recovery begins from a clean clone of `Jktomy/atlas-prime`, a verified main head, and the exact Receipt Gemstone. Normal restoration must not require `Jktomy/atlas-codex`.

## Recovery sequence

1. Verify repository identity, remote, default branch, expected head, and receipt hashes.
2. Clone without inherited worktrees, hooks, generated output, caches, or local configuration.
3. Run kernel, repository-policy, privacy, Thread Engine, generator, and whole-program checks.
4. Regenerate projections into a separate output directory and compare deterministically.
5. Verify Thread Engine active state and its isolated disablement path.
6. Verify Sword/Oathbringer can classify the recovery point without blind replay.
7. Restore only declared external runtime configuration from its approved backup system; never infer private values from source.
8. Perform a destructive canary restore only with explicit Jayson-side authority and a protected evidence plan.
9. Read back recovered source and runtime evidence before declaring success.

## Prometheus's Fire recovery boundary

The Prometheus architecture requires narrow Forge mounts with safe unavailable-
mount behavior, Prometheus guest backups, a destructive canary restore, and an
independent recovery copy not confined to Forge. Nexus recovery must include
the dedicated Nexus VM, PostgreSQL base backups, WAL protection, and a
point-in-time recovery direction. Plex recovery must include its local-NVMe
database, metadata, configuration, cache, and transcode state; media and
completed DVR media remain on Forge/Anvil through narrow paths. Temporary
restore guests require an explicit RAM reallocation or guest-shutdown plan.

These are future proof requirements. This runbook and the Prometheus Quest do
not claim that any backup, restore, deployment, or runtime cutover has
occurred. Recovery receipts must be sanitized and must not contain secrets,
private runtime values, or protected records.

## Rollback

- Every source transaction records base, head, tree, paths, payload hashes, PR, merge, and recovery classification.
- A source rollback uses a new reviewed PR; no force push or history rewrite is required.
- Thread Engine emergency disablement changes the reviewed activation state through Aegis Break → Oathbringer and must reject at `ACTIVATION_GATE` before mission parsing.
- The original Prime shadow head remains preserved by the locked archive branch and annotated tag.
- The frozen Codex predecessor remains audit evidence only and is never the normal rollback target after cutover.

RAID, snapshots, a green backup job, or an undeleted predecessor are not restore proof. Recovery is proven only by exact restoration and readback.
