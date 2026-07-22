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

Prime recovery begins from a clean clone of `Jktomy/atlas-prime`, a verified main head, and the exact Receipt Gemstone. Normal restoration must not require `Jktomy/atlas-codex`, Athena, Harmony, Coppermind, an active transaction store, the live GitHub Issue service, or the normal repository publisher.

## Recovery sequence

1. Verify repository identity, remote, default branch, expected head, and receipt hashes.
2. Clone without inherited worktrees, hooks, generated output, caches, or local configuration.
3. Run kernel, repository-policy, privacy, Thread Engine, generator, Mission Board Quest registry, frozen Quest Board, continuity, and whole-program checks.
4. Regenerate projections into a separate output directory and compare deterministically.
5. Verify Thread Engine state and its isolated disablement path.
6. Verify Sword/Oathbringer can classify the recovery point without blind replay.
7. Reconcile any unfinished repository transaction from exact branch, PR, head, tree, paths, receipts, and remote state before resuming; never create a duplicate mission because one operator surface is unavailable.
8. Reconcile any unfinished full Sunset from its exact Preview, approval, carrier, semantic digest, scope, and current state before compiling or publishing.
9. Restore only declared external runtime configuration from its approved backup system; never infer private values from source.
10. Perform a destructive canary restore only with explicit Jayson-side authority and a protected evidence plan.
11. Read back recovered source and runtime evidence before declaring success.

## Mission Board and admitted-Quest recovery boundary

Mission Board recovery does not depend on chat memory, Coppermind runtime,
Emberdark runtime, GitHub Projects, an available normal publisher, or live
GitHub Issues for Quest-level orientation.

First read and validate:

1. `continuity/mission-board-quest-registry-r01.json`;
2. `continuity/prime-continuity-register-r01.json`;
3. the exact active Quest sources; and
4. `quest-board/quest-board-v1.json` only as frozen predecessor evidence.

The merged registry recovers the exact active Quest IDs, owners, states, next
gates, readiness bases, and parent Issues #307–#309. Live Issue availability is
not required for that recovery. Issue state alone cannot override the merged
registry or continuity.

For `Continue Mission #N`:

1. resolve the exact repository and confirm object `#N` is an Issue, not a pull request;
2. export and read the Issue plus every comment;
3. fresh-read canonical `main` and this contract's routed sources;
4. reconcile linked branch, PR, head, tree, changed paths, checks, reviews, receipts, and attempt identity;
5. reject stale or contradictory Mission claims;
6. search before creating any Mission, branch, PR, Sunset, child, receipt, or archive;
7. resume the same attempt from its last proven state; and
8. append a sanitized result and exact next safe action.

If the Issue service is unavailable, Quest-level work may be oriented from the
merged registry and continuity, but a particular child Mission remains blocked
until its exact public-clean Issue/comment/PR/receipt export or authenticated
readback is available. That export is evidence rather than source authority. It
cannot authorize a blind retry or claim canonical completion.

GitHub-to-Gitea recovery preserves `atlas.mission.v1` semantics and maps only the
platform API; cutover remains separately gated.

## Quest portfolio recovery boundary

Read `governance/atlas-quest-portfolio-contract.md` after the Mission Board Quest
registry and continuity register. Atlas remains an umbrella ecosystem, never a
recovery super-Quest. Resolve each unfinished responsibility to exactly one
active registry row, parent Mission identity, durable Quest, and Operation
before resuming it.

The active portfolio is Prime Ascendant (#307), Prometheus's Fire (#308), and
Notum's Watch (#309). The frozen Quest Board preserves the exact pre-cutover
seven-Quest history and cannot admit, advance, or resume work.

Found Silverlight is historical after Mission #276: resume FS-C01-M04 only
through the bounded Codex / Source Governance Mission family, Glass Codex
through Prime Ascendant / Operation Glass Codex, and Seon through Prime
Ascendant / Operation Harmony. Apple Reminders remains authoritative and Hermes
remains the bridge vessel. Preserve all Found Silverlight proofs and events;
never infer M04, deployment, reminder access, or protected-runtime proof from
Sunset. Prime Continuity Proof is complete through Mission #277; preserve AJ-08
admission evidence and its append-only events as historical proof.

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

A full Sunset is recoverable from:

- exact Preview and Preview digest;
- exact Jayson approval and permanence mode;
- approved route-neutral carrier and semantic payload digest;
- Project, Operation, Quest scope, protected boundary, and record plan;
- proposed Feather meaning, decisions, open items, blockers, next gates, and Lesson Harvest;
- selected route, fallback routes, current carrier state, and any existing branch or PR.

A missing publisher, local clone, connector, or network path changes the carrier to `BLOCKED_RESUMABLE`; it does not terminate or replace the save point. Athena, Harmony, and Jayson PowerShell may resume the same carrier after read-only reconciliation. Any semantic change requires a new Preview and explicitly supersedes the old carrier.

No recovery route may manufacture a lifecycle source fingerprint, recreate an approval from chat memory, substitute a narrative summary, or report `SUNSET COMPLETE` before canonical merged-main readback.

## Cloud Atlas protected-realm recovery boundary

Glass Codex recovery follows `governance/glass-codex-client-contract.md`.
Retain an integrity-verified client package and known-good rollback package,
but keep authoritative state in governed backend services. Apollo or VS Code
loss removes the GUI only and must not block Cloud Atlas services, monitoring,
or Prime clean-clone recovery. Client disable/reinstall never restores or
mutates backend state and no protected cache is silently recovered.

The read-only health view additionally follows
`governance/notum-glass-codex-health-contract.md`. Recovering Glass Codex never
recovers, rewrites, acknowledges, or controls Notum/Sentinel monitoring state.
After client loss, rehydrate only a freshly authenticated minimized projection;
expired evidence remains `STALE`, unavailable evidence remains `UNKNOWN`, and
last-known-good remains historical context. Notum loss does not block Prime or
Cloud Atlas recovery, and Glass loss does not stop monitoring.

Apollo endpoint recovery follows
`governance/apollo-remote-operator-continuity-contract.md`. Preserve an
integrity-verified Glass package and rollback package, Windows recovery-media
and system-image dispositions, and manufacturer-driver sources. Reinstall from
known-good media, recreate isolated environments, obtain fresh bounded
credentials, and restore no protected cache or unique source from ordinary
endpoint backup. Hermes retains independent administration and clean-clone
Prime recovery while Apollo or its remote route is unavailable.

Read `governance/cloud-atlas-protected-realm-contract.md` before any Cloud
Atlas recovery design or claim. Preserve exact separation among the Protected
Original Vault, Coppermind, Emberdark, Harmony, Phoenix, and the approved secret
system. Recovery requires complete and selective-service backup, complete and
selective restore, integrity and provenance validation, and least-privilege
readback. Restore one bounded identity at a time where possible; never let a
restored derivative impersonate an original or let co-location confer vault,
SQL, secret, source, or permanence authority.

Forge is an approved encrypted recovery destination, not the primary protected
runtime. If Forge or the Original Vault is unavailable, recoverability or
original availability is `UNPROVEN`/`UNAVAILABLE` and fails closed. If
Coppermind, Emberdark, Harmony, or Phoenix is unavailable, follow the explicit
degraded mode in the validated protected-realm contract. Mission #279 proves
architecture only; no backup, restore, protected import, secret, database,
storage, network, or runtime action is claimed.

## Prometheus's Fire recovery boundary

The selected service isolation, complete/selective restore, dependency order,
failure behavior, and household priority are summarized by
`governance/prometheus-cloud-atlas-topology-contract.md`. Treat every envelope
as planning until measured capacity and real destructive restore proof exist.

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
- Mission #278 registry rollback restores the prior Quest Board authority and removes the active-registry claim through one reviewed revert or repair-forward PR; the frozen Board, parent Issues, and append-only Issue history are never rewritten.
- Thread Engine emergency disablement changes the reviewed activation state through Aegis Break → Oathbringer and must reject at `ACTIVATION_GATE` before mission parsing.
- Historical lifecycle records are never rewritten; a changed Sunset plan requires a new Preview and explicit supersession.
- The original Prime shadow head remains preserved by the locked archive branch and annotated tag.
- The frozen Codex predecessor remains audit evidence only and is never the normal rollback target after cutover.
- Before final Forge Plex removal, a separately authorized migration rollback may temporarily restore service to Forge Plex. After final removal, stored-media continuity is Jellyfin, live-TV continuity is the direct antenna, and normal Plex service returns through restoration of the Prometheus Plex LXC.

RAID, snapshots, a green backup job, an undeleted predecessor, the presence of Jellyfin, a live Mission Issue, or a merge API success response are not restore proof. Recovery is proven only by exact restoration and readback.
