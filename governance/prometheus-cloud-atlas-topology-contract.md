---
title: "Prometheus Cloud Atlas Topology Contract"
atlas_id: "prime.governance.prometheus-cloud-atlas-topology-r01"
status: "CANONICAL_SOURCE_ARCHITECTURE"
source_type: "PROTOCOL"
authority_class: "CANONICAL_AUTHORED_SOURCE"
owner_project: "Project Odyssey"
owner_operation: "Operation Prometheus Foundation"
protected_level: "HIGH"
---

# Prometheus Cloud Atlas topology contract

This contract selects a recovery-aware public-clean topology direction from
canonical planning envelopes. It does not claim measured deployment capacity,
create a guest, change storage/networking, activate backup, move Plex/DVR, or
activate Cloud Atlas, Phoenix, PostgreSQL, `pgvector`, or Gitea.

| Service | Identity and trust boundary | Resource/storage direction | Persistence, recovery, health, and failure |
|---|---|---|---|
| Harmony VM | Separate intelligence vessel; exclusive planned B50; no source, SQL, infrastructure, or permanence authority | 24 GB fixed RAM; about 350 GB expandable local NVMe | Independent VM backup/restore and accelerator-detachment proof; private health; fail closed without collapsing Atlas VM |
| Atlas VM | Operational-soul substrate, not Atlas; co-located Emberdark, Coppermind, Phoenix remain separate | 12 GB fixed RAM; about 180–200 GB expandable NVMe; separate OS/app, Coppermind, Phoenix, Emberdark areas | Complete VM plus selective service restore; PostgreSQL base/WAL/PITR and Phoenix repo/Gitea consistency; service-specific health and rollback |
| Plex LXC | Household-critical media server; iGPU Quick Sync; no Atlas dependency | 16 GB maximum; about 150 GB local NVMe for application state | Metadata/config restore, playback/DVR/reboot/mount-loss proof; failure falls back only to stored-media Jellyfin and direct antenna, not seamless recording |
| Proxmox host | Substrate and rescue boundary | 8 GB protected reserve, 4 GB flexible headroom, about 64 GB ISO/template area | Administration remains independent of B50/iGPU; restore guests require explicit reallocation/shutdown plan |
| Forge | Storage backbone and encrypted backup destination, not protected primary runtime | Media, completed DVR, persistent Helios, backups | Narrow mounts, safe mount loss, independent recovery copy; local-only Jellyfin continuity |
| Notum/Sentinel | Independent monitoring authority | No workload capacity allocation here | Observes bounded health; never required for startup, control, failover, or recovery |
| Glass Codex on Apollo | Client-independent API consumer; GUI only | No Prometheus authoritative state | Apollo/VS Code loss removes GUI only; Cloud Atlas, monitoring, and Prime recovery continue |

The 64 GB planning ceiling is Harmony 24 + Atlas 12 + Plex maximum 16 +
protected host reserve 8 + flexible headroom 4. No ballooning or overcommit is
allowed at launch. Resource promotion stops on sustained swap, OOM, playback or
recording degradation, or unmeasured disk headroom. Plex playback, DVR
recording, and persistent Forge services outrank discretionary Harmony/Atlas
work and unproven backup activity.

Startup order is substrate/rescue → narrow storage mounts → household-critical
Plex → bounded Atlas services → Harmony intelligence → clients. Shutdown is
reverse, preserving database/WAL, workflow receipts, Phoenix repository state,
and recordings. A failed dependency produces explicit unavailable/degraded
state; no service receives another's credential, mount, database role, backup,
restore, monitoring, or permanence authority.

GitHub remains canonical. Phoenix/Gitea remains a shadow direction until PA-C06
separately proves parity, independent mirror, backup, selective restore,
interruption, access, and cutover rollback. PF-C01-M02 and every deployment,
capacity, migration, storage, network, backup, restore, and cutover gate remain
unchanged.
