---
title: "Quest — Prometheus's Fire"
status: Active
owner: "Project Odyssey / Operation Prometheus Foundation"
supporting_projects:
  - "Project Elantris"
  - "Project Artemis"
  - "Project Helios"
  - "Project Codex"
source_type: Quest
canonical_scope: "Parent Quest for converting Prometheus into a stable, recoverable Proxmox platform with the Harmony VM, Atlas VM, household-critical Plex LXC, and bounded Forge media continuity topology."
protected_level: High
routes_from:
  - atlas-prime.md
  - operations/protocol-library.md
  - infrastructure/atlas-infrastructure-source.md
  - safety/atlas-safety-doctrine.md
routes_to:
  - emberline-sop.md
  - quests/notums-watch.md
  - quests/prime-ascendant.md
  - quest-board/quest-board-v1.json
  - governance/atlas-strikeforce.md
  - proof/prometheus-fire/pf-c01-m01-mission-seal-r01.md
  - recovery/elantris-recovery.md
  - noctua.md
  - sunsetting-protocol.md
private_boundary: "Store only clean architecture, campaign status, gates, sanitized evidence pointers, and completion claims. Do not store IP addresses, private network maps, device registers, credentials, tokens, MFA or recovery codes, real environment values, PHI, raw finance evidence, account data, or unrestricted terminal output."
evidence_boundary: "This Quest coordinates verified source and sanitized operating evidence. Original hardware diagnostics, backup artifacts, restore receipts, screenshots, private runtime values, and protected records remain in their approved evidence systems. Planning acceptance does not prove deployment."
cleanup_path: "Keep active until all required Campaigns and Quest-level gates pass. Close through a final Noctua completion audit, Prime Quest Board and continuity-register synchronization, restart-safe Sunset, and verified merged-main readback."
last_verified: 2026-07-20
---

# Quest — Prometheus's Fire

## 1. Quest identity

**Quest ID:** `QUEST-PROMETHEUS-FIRE-20260701`  
**Parent Project:** Project Odyssey  
**Owning Operation:** Operation Prometheus Foundation  
**Supporting Projects:** Elantris, Artemis, Helios, Codex  
**Current lane:** `UPDATE -> VERIFY`  
**Current route:** `PF-C01 -> PF-C01-M02 Preserve the Old Flame Preview`  
**Current state:** `IN_PROGRESS`

## 2. Purpose

Prometheus's Fire converts Prometheus into Atlas's stable, recoverable, privately administered Proxmox compute and service node without bypassing Citadel readiness, Forge storage boundaries, Elantris restore proof, or Atlas approval gates. This source records architecture and proof requirements only; it does not claim deployment.

The Quest coordinates clean source and future proof for:

- Prometheus hardware and Proxmox foundation;
- private administration and rescue access;
- narrow Forge, Hammer, and Anvil mounts;
- Prometheus-to-Forge backup and destructive Elantris restore proof;
- the Harmony VM and exclusive Intel Arc Pro B50 passthrough;
- the Atlas VM containing logically separate Emberdark, Coppermind, and Phoenix services;
- PF-C06 disposition of Matrix / Element from the active baseline;
- the household-critical Plex LXC and controlled Forge-to-Prometheus cutover;
- Forge-local Jellyfin continuity for stored media and completed DVR recordings;
- direct-antenna live-TV continuity on the Samsung television;
- observability through Notum's Watch;
- final source, recovery, and completion audit.

`Crucible` is reserved for a future bounded transformation or testing system and is not an active Prometheus guest.

The accepted launch envelope is:

```text
Prometheus / Proxmox
├── Harmony VM — 24 GB fixed RAM
├── Atlas VM — 12 GB fixed RAM
└── Plex LXC — 16 GB maximum

Protected Proxmox reserve — 8 GB
Flexible headroom — 4 GB
Total — 64 GB
```

Launch rules are no ballooning and no memory overcommit. The Plex value is a ceiling rather than expected continuous use. Harmony or Atlas may grow only after measured concurrent-load proof. Temporary restore guests require an explicit RAM reallocation or guest-shutdown plan. Sustained swap, an OOM event, recording failure, or Plex playback degradation blocks resource promotion.

The thin-provisioned NVMe planning envelope is approximately 64 GB for host ISOs/templates, 350 GB for Harmony, 180–200 GB for Atlas, and 150 GB for Plex. The remaining usable capacity is reserved for pool/filesystem overhead, snapshots, temporary restore needs, and growth. Exact remaining capacity is unknown until storage is formatted and measured.

## 3. Approved topology baseline

The cross-service resource, trust, recovery, health, dependency, startup,
shutdown, and rollback selection is governed by
`governance/prometheus-cloud-atlas-topology-contract.md`. It consolidates this
Quest's existing public-clean planning envelopes without claiming measurement
or advancing PF-C01-M02.

```text
Prometheus / Proxmox
├── Harmony VM — intelligence and B50
├── Atlas VM — Emberdark, Coppermind, and Phoenix
└── Plex LXC — primary and only final-state Plex server

Forge
├── media and completed DVR recordings
├── persistent Helios backend
├── backup destination
└── Jellyfin — local-only continuity player

Samsung television
└── direct antenna — live-TV continuity
```

### Resource envelope

| Guest or reserve | RAM |
|---|---:|
| Harmony VM | 24 GB fixed |
| Atlas VM | 12 GB fixed |
| Plex LXC | 16 GB maximum |
| Permanent planned maximum | 52 GB |
| Protected Proxmox reserve | 8 GB |
| Flexible headroom | 4 GB |
| **Total** | **64 GB** |

Rules:

- Prometheus remains a 64 GB baseline.
- Ballooning and memory overcommit are disabled at launch.
- The B50 is planned for exclusive passthrough to Harmony and is not shared with Forge or another guest.
- The iGPU is planned for Plex Quick Sync; host administration and rescue remain independent of that mapping.
- The protected 8 GB Proxmox reserve is not reassigned for routine workloads.
- Temporary restore guests require an explicit RAM reallocation or guest-shutdown plan.
- Plex playback and DVR recording outrank discretionary Harmony/Atlas batch work, Jellyfin scans, and unproven backup activity.

### NVMe planning envelope

This is a thin-provisioned, expandable plan rather than a measured capacity claim:

| Planned area | Approximate capacity |
|---|---:|
| Proxmox host, ISO, and templates | 64 GB |
| Harmony VM | 350 GB |
| Atlas VM | 180–200 GB |
| Plex LXC | 150 GB |

Remaining usable capacity is reserved for pool and filesystem overhead, snapshots, temporary restore needs, and future growth. Exact remaining capacity must be measured after storage formatting and pool creation.

### Atlas VM internal boundary

The Atlas VM is one recovery substrate with separately bounded services and data areas:

```text
Atlas VM
├── OS and application binaries
├── Coppermind PostgreSQL data
├── Phoenix repositories and Gitea state
└── Emberdark workflow, quarantine, and temporary state
```

Emberdark, Coppermind, and Phoenix retain distinct service identities, private interfaces, database roles, credentials, health checks, logs, backup units, and restore procedures. Co-location does not grant unrestricted SQL, canonical-source, infrastructure, recovery, READY, or merge authority.

The Atlas VM is the selected future Phoenix/Gitea shadow substrate direction. GitHub remains canonical. No Gitea installation, database activation, parity claim, repository-setting change, or cutover is authorized by this source architecture.

## 4. Desired end state

Prometheus's Fire is complete only when:

1. Prometheus runs Proxmox VE stably with verified 64 GB memory.
2. Primary private administration and an independent rescue route are proven.
3. Forge mounts are narrow, persistent, and fail safely.
4. Prometheus backs up to Forge / Anvil and Elantris proves an independent recovery copy.
5. A destructive canary restore succeeds.
6. Harmony passes B50 passthrough, model-runtime, retrieval, intake, backup, restore, thermal, soak, and rollback proof without durable-action authority.
7. Atlas passes complete-VM and selective service restoration, independent storage-boundary, Emberdark, Coppermind PostgreSQL/WAL/PITR, Phoenix repository/Gitea-state consistency, and rollback proof.
8. PF-C06 records that Matrix / Synapse / Element are not part of the active Prometheus baseline and preserves lineage without claiming deployment or retirement.
9. Plex passes metadata restore, Quick Sync, playback, transcoding, recording, concurrency, reboot, mount-loss, rollback, and controlled cutover proof before leaving Forge; its application database, configuration, metadata, artwork, cache, and transcode workspace remain on Prometheus local NVMe.
10. Jellyfin on Forge proves local-only playback of stored media and completed DVR recordings with a separate application database and no Plex-standby or automatic-failover claim.
11. The Samsung television's direct antenna input is verified as the live-TV continuity route independent of Prometheus, Plex, Jellyfin, and HDHomeRun streaming.
12. The accepted degraded mode is explicit: stored media and completed DVR playback remain available through Jellyfin during a Prometheus outage, but new or in-progress Plex recordings are not guaranteed.
13. Notum's Watch improves observability without becoming a mandatory control dependency or Prometheus prerequisite.
14. Noctua verifies the final topology and exact evidence.
15. The Prime Quest Board and continuity register remain synchronized, with generated projections refreshed separately.
16. Required Windows-specific work and Codex continuity are safely evacuated from the current Prometheus Windows installation before destructive action.
17. Forge retains the persistent Helios backend while Apollo provides the separately bounded interactive Helios Control Deck.
18. Prime Ascendant remains the application-semantics Quest; this mission does not implement it or authorize runtime.

## 5. Explicit exclusions

The baseline does not include:

- a generic Docker VM;
- a Disposable Browser VM;
- a Helios VM or full Helios migration to Prometheus;
- a separate n8n guest;
- HAOS on Prometheus;
- Paperless on Prometheus;
- Jellyfin on Prometheus;
- a permanent Forge Plex standby after final disposition;
- Plex/Jellyfin database sharing;
- Jellyfin public exposure or automatic failover;
- Jellyfin HDHomeRun/DVR ownership in the continuity role;
- Immich;
- Nextcloud;
- Kavita;
- Komga;
- Calibre / ebook-convert;
- m4b-tool;
- Matrix, Synapse, and Element as active Prometheus workloads;
- public Harmony, Atlas, Emberdark, n8n, Plex administration, or Proxmox endpoints;
- Qdrant as a Phase 1 requirement;
- Proxmox Backup Server as an immediate requirement;
- acting Kandra workers before governance and tool gates pass;
- automatic UPS shutdown or ONT / Eero recovery without a separate Elantris / Beacon Preview and proof;
- Coppermind application activation, Dawnshard activation, Gitea cutover, or a private Glass Codex website.

Forge retains HAOS, Paperless-ngx, Dozzle, Diun, and the persistent Helios backend: Gluetun, qBittorrent, Prowlarr, Sonarr, Radarr, optional Readarr, automated watchers and import workflows, storage-adjacent processing, Audiobookshelf, media, completed DVR recordings, and current Plex until separately proven cutover. Jellyfin is a separately deployed local-only continuity application, not part of the Prometheus guest baseline.

Apollo may host the on-demand interactive Helios Control Deck: Libation, FileBot GUI, MediaInfo, MKVToolNix GUI, Subtitle Edit, optional bounded HandBrake or FFmpeg work, dashboards, and manual inspection or approval. Hermes and Iris are Helios clients only. Prometheus hosts neither persistent Helios-backend role nor the interactive Control Deck.

# Campaigns

## Campaign PF-C01 — Forge the Vessel

**Owner:** Odyssey / Prometheus Foundation  
**Support:** Elantris / Keystone  
**Status:** `IN_PROGRESS`  
**Depends on:** none

Prove physical, firmware, memory, storage, power, cooling, cabling, recovery-console, and operator-continuity readiness before replacing the current operating system.

### Mission PF-C01-M01 — Mission Seal

**State:** `PROVEN_WITH_CARRY_FORWARD`

**Acceptance record:** `proof/prometheus-fire/pf-c01-m01-mission-seal-r01.md`

Accepted clean evidence:

- expected Prometheus hardware identity matched;
- 64 GB memory detected;
- Intel Arc Pro B50 and integrated graphics detected;
- the 1 TB NVMe reported a healthy operational state;
- the active wired link negotiated at 10 GbE;
- Secure Boot is enabled;
- TPM is present and ready;
- the Windows system volume is not BitLocker-encrypted;
- optional Windows hypervisor features are disabled;
- no important or irreplaceable data was reported as existing only on Prometheus;
- no open repair, return, warranty, overheating, fan-noise, or freezing concern was reported.

Carry-forwards:

- extended memory testing;
- bounded follow-up for one corrected PCIe WHEA warning;
- a stability baseline after a prior unexpected shutdown;
- Windows recovery-media and complete system-image disposition;
- manufacturer-driver preservation;
- operator-workstation and Codex evacuation.

Mission Seal authorizes no runtime action, Windows removal, Proxmox installation, migration, or deployment.

### Mission PF-C01-M02 — Preserve the Old Flame

**State:** `READY_FOR_PREVIEW`

The public-clean endpoint, dependency, startup/shutdown, source continuity,
package, reinstall, degraded-mode, and recovery proof plan is defined by
`governance/apollo-remote-operator-continuity-contract.md`. It does not satisfy
the protected proof below: Apollo commissioning, native workflow execution,
private route access, Hermes independent administration, Windows recovery, and
PF-C01-M02 exit remain unproven until separately authorized execution evidence
is read back.

Required proof:

1. Apollo is commissioned as the fixed Windows orchestration endpoint.
2. Required Windows applications and Windows-specific Codex workflows operate on Apollo.
3. Hermes can independently access Prime, GitHub, Element, and approved private administration surfaces.
4. Iris remains a nonblocking companion and is not treated as the sole source, approval, administration, or recovery route.
5. Zeus is recorded as Jayson's nonblocking iPhone endpoint and is not treated as the sole source, approval, administration, or recovery route.
6. Every relevant Prometheus repository and working directory is identified.
7. Dirty worktrees, uncommitted changes, unpushed commits, local branches, and local-only artifacts are reconciled.
8. Required Prime source and branches are visible in GitHub or preserved through another approved route.
9. Active Codex work is completed, safely stopped, or transferred.
10. A representative Windows-specific workflow resumes on Apollo.
11. A representative portable command and administration workflow succeeds from Hermes.
12. Windows recovery media, system-image disposition, manufacturer drivers, and rollback expectations are preserved.
13. No credential, recovery key, token, private key, or secret enters Prime or ordinary migration artifacts.
14. A later exact Execute gate authorizes Windows removal or Proxmox installation.

The continuity proof must also record matching-memory and extended-memory testing, NVMe health, WHEA/PCIe/USB/KVM/thermal stability, firmware and BIOS state, virtualization/IOMMU/ReBAR/iGPU/B50 state, and Citadel power, cooling, cabling, console, and recovery readiness. These are proof requirements, not claims that any device or software has been changed.

**Exit gate:** Apollo and Hermes continuity is proven, Windows recovery posture is preserved, and a separately approved destructive-action Preview may be prepared. Until then, Windows removal and Proxmox installation remain blocked.

## Campaign PF-C02 — Light the First Flame

**Owner:** Odyssey / Prometheus Foundation  
**Support:** Sentinel / Shadesmar Access  
**Status:** `BLOCKED_BY_PF-C01`  
**Depends on:** PF-C01

Install and prove the minimal Proxmox foundation.

Required proof:

- Proxmox VE installation and stable reboot;
- hostname, time, DNS, updates, notifications, and private management;
- 10 GbE primary path and independent rescue path;
- minimal host services only;
- local storage health and thin-pool thresholds;
- Proxmox firewall baseline and guest network segmentation;
- private management and an independent rescue path;
- host configuration backup and recovery notes.

## Campaign PF-C03 — Prove Elantris Recovery

**Owner:** Elantris / Restore Runbook and Recovery Drill  
**Support:** Odyssey / Forge Storage  
**Status:** `BLOCKED_BY_PF-C02`  
**Depends on:** PF-C02

Prove narrow Forge mounts, Prometheus backup destination, and destructive restore before deploying services.

Required proof:

- approved NFS or SMB exports and permissions;
- reboot persistence and safe unavailable-mount behavior;
- temporary canary guest creation with an explicit RAM reallocation or guest-shutdown plan;
- off-host backup;
- original deletion;
- restore under a different ID;
- boot, marker, and network verification;
- sanitized restore receipt;
- independent off-Forge recovery plan;
- Harmony VM backup/restore and accelerator detachment safety;
- Atlas VM complete and selective backup/restore, PostgreSQL base-backup and WAL/PITR direction, and Phoenix repository/Gitea-state consistency;
- Plex metadata/configuration restoration and a recovery copy not confined to Forge.

## Campaign PF-C04 — Establish the Harmony Substrate

**Owner:** Artemis / Operation Harmony and AI Governance  
**Support:** Odyssey / Prometheus Foundation  
**Status:** `BLOCKED_BY_PF-C03`  
**Depends on:** PF-C03

Build Harmony as the Atlas resident-intelligence VM.

Required proof:

- 24 GB fixed RAM launch baseline and approximately 350 GB expandable local-NVMe disk;
- base VM backup and restore before passthrough;
- safe IOMMU grouping without unsupported overrides;
- exclusive B50 passthrough;
- host administration independent of the B50;
- pinned Intel / OpenVINO runtime;
- Harmony/Sazed local generation, retrieval, OCR/intake, embeddings, reranking, and capability-aware delegation;
- bounded Kandra baseline and replacement discipline;
- private model-lab posture;
- read-only and mediated Atlas/Coppermind/Phoenix boundaries;
- Qdrant deferred from Phase 1 until measured need is proven;
- cold-load, reboot, reset, thermal, cancellation, soak, backup, restore, and rollback tests;
- no source, merge, infrastructure, unrestricted SQL, or durable-action authority.

## Campaign PF-C05 — Establish the Atlas Substrate

**Owner:** Odyssey / Prometheus Foundation  
**Support:** Artemis / Harmony; Codex / Coppermind and Phoenix; Elantris  
**Status:** `BLOCKED_BY_PF-C03`  
**Depends on:** PF-C03

Build the Atlas VM as the operational-soul substrate for logically separate Emberdark, Coppermind, and Phoenix services. This Campaign owns substrate proof, not later Prime Ascendant application semantics or Gitea cutover.

Required proof:

- 12 GB fixed RAM planning baseline and approximately 180–200 GB expandable local-NVMe storage;
- independently bounded OS/application, Coppermind, Phoenix, and Emberdark data areas;
- distinct service identities, private interfaces, database roles, health checks, logs, and backup units;
- Emberdark workflow, quarantine, approval-state, retry, timeout, mission-register, and receipt substrate;
- Coppermind PostgreSQL relational state, full-text search, `pgvector`, base backup, WAL, and PITR direction;
- Phoenix repository and Gitea application/database consistency, independent mirror, and selective restoration;
- n8n single-main through governed interfaces rather than unrestricted SQL;
- Python / FastAPI integration surface;
- ClamAV/FreshClam and private health endpoints;
- complete VM restore under a different guest ID;
- selective Emberdark, Coppermind, and Phoenix restoration;
- no broad Proxmox, Forge, GitHub, shell, merge, deletion, cleanup, READY, or automatic permanence authority;
- GitHub remains canonical and Gitea cutover remains separately gated.

PF-C04 and PF-C05 may be built in either order after PF-C03 when their independent prerequisites are met. Integrated Harmony-to-Atlas proof remains later and does not create an unnecessary substrate dependency.

## Campaign PF-C06 — Close the Matrix Gate

**Owner:** Artemis / Operation Harmony  
**Support:** Elantris / AI Governance  
**Status:** `BLOCKED_BY_PF-C05`  
**Depends on:** PF-C03 and PF-C05

Disposition Matrix, Synapse, and Element as removed from the active Prometheus baseline. Preserve the PF-C06 lineage and do not claim that Matrix was deployed and then retired.

Required proof:

- no current Matrix/Element deployment requirement;
- no Matrix dependency for Harmony, Atlas VM, Emberdark, Coppermind, Phoenix, or Plex;
- VS Code/Apollo and the future Glass Codex client with governed APIs replace the immediate interaction need;
- any future communications requirement must justify a separate source decision or Quest.

## Campaign PF-C07 — Raise Relay

**Owner:** Helios / Operation Relay  
**Support:** Odyssey / Elantris  
**Status:** `BLOCKED_BY_PF-C03_AND_RESOURCE_REVIEW`  
**Depends on:** PF-C03 and PF-C04/PF-C05 resource review

Build the future Plex LXC and perform a separately approved controlled cutover from Forge. Establish Jellyfin and direct-antenna continuity without creating a second Plex server.

Required proof:

- unprivileged LXC;
- 16 GB memory ceiling and 8 vCPU planning baseline;
- iGPU / Quick Sync acceleration;
- metadata, configuration, artwork, cache, and transcode on Prometheus NVMe;
- Anvil media read-only;
- narrow DVR write path to Forge;
- safe behavior when Forge or the DVR mount is unavailable, including no unintended local writes;
- metadata/configuration restore;
- guide, HDHomeRun DVR recording, completed playback, concurrent clients, reboot recovery, remote access, update rollback, and host-contention tests;
- Plex playback and recording priority over discretionary Harmony/Atlas work, Jellyfin scans, and unproven backups;
- local-only Jellyfin playback of stored media and completed DVR files through a separate application database;
- Samsung direct-antenna live-TV continuity;
- explicit acceptance that new and in-progress recordings are not guaranteed during a Plex/Prometheus outage;
- Forge Plex remains intact through migration proof and is removed only after separately confirmed final disposition.

## Campaign PF-C08 — Close the Sentinel Ring

**Owner:** Odyssey / Sentinel  
**Support:** Beacon / Tempest; Elantris; Artemis; Helios  
**Status:** `BLOCKED_BY_PF-C04_TO_PF-C07`  
**Depends on:** PF-C04, PF-C05, PF-C06, PF-C07

Complete integrated observability, failure testing, source alignment, and Quest closeout.

Required proof:

- Notum's Watch Uptime Kuma, Homepage, watchdog, diagnostics, outage journal, optional proven UPS telemetry, and read-only emergency Prime recovery clone;
- Prometheus, guest, storage, network, thermal, playback, recording, and backup monitoring;
- alert delivery that does not make recovery depend on Prometheus;
- integrated reboot, dependency-loss, mount-loss, backup, restore, degraded-media-continuity, and rollback tests;
- no automatic shutdown, plug cycling, or ONT / Eero recovery unless separately approved;
- exact configuration manifests and sanitized runbooks;
- Prime Quest Board and continuity-register reconciliation;
- PF-C06 Matrix disposition and no stale Matrix dependency;
- Coppermind PostgreSQL/WAL and Phoenix repository/Gitea-state health, backup/restore boundaries, and no public endpoints;
- final Strikeforce and Noctua audit;
- restart-safe Sunset.

Prometheus's Fire may consume Notum's Watch observability when available. It does not own Notum's Watch, does not sequence Notum's Watch behind Prometheus, and must not treat Nightwatcher as a current separate active node. Nightwatcher is superseded lineage preserved under Notum's Watch.

## 6. Current gate

```text
Quest state: IN_PROGRESS
Campaign PF-C01: IN_PROGRESS
PF-C01-M01 Mission Seal: PROVEN_WITH_CARRY_FORWARD
PF-C01-M02 Preserve the Old Flame: READY_FOR_PREVIEW
Apollo continuity architecture: SOURCE_ACCEPTED / RUNTIME_PROOF_PENDING
Apollo commissioning: NOT PROVEN
Hermes independent route: NOT PROVEN
Iris role: SOURCE_ACCEPTED / NONBLOCKING
Zeus role: SOURCE_ACCEPTED / NONBLOCKING
Windows wipe: BLOCKED
Proxmox installation: BLOCKED
Operational readiness: NOT CLEARED
Runtime deployment: NOT STARTED
```

The next safe action is the exact PF-C01-M02 Preserve the Old Flame Preview. This Quest does not authorize device renames, application migration, Windows removal, Proxmox installation, physical, firmware, network, storage, power, service, Jellyfin, Gitea, Plex cutover, or infrastructure execution by itself.
