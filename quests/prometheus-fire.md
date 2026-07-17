---
title: "Quest — Prometheus's Fire"
status: Active
owner: "Project Odyssey / Operation Prometheus Foundation"
supporting_projects:
  - "Project Phoenix"
  - "Project Artemis"
  - "Project Helios"
  - "Project Codex"
source_type: Quest
canonical_scope: "Parent Quest for converting Prometheus into a stable, recoverable Proxmox compute platform with the approved Crucible VM, Nexus Living Memory VM, and future Plex LXC topology."
protected_level: High
routes_from:
  - atlas-prime.md
  - operations/protocol-library.md
  - infrastructure/atlas-infrastructure-source.md
  - infrastructure/atlas-infrastructure-source.md
  - safety/atlas-safety-doctrine.md
routes_to:
  - emberline-sop.md
  - quests/notums-watch.md
  - quest-board/quest-board-v1.json
  - governance/atlas-strikeforce.md
  - proof/prometheus-fire/pf-c01-m01-mission-seal-r01.md
  - noctua.md
  - sunsetting-protocol.md
private_boundary: "Store only clean architecture, campaign status, gates, sanitized evidence pointers, and completion claims. Do not store IP addresses, private network maps, device registers, credentials, tokens, MFA or recovery codes, real environment values, PHI, raw finance evidence, account data, or unrestricted terminal output."
evidence_boundary: "This Quest coordinates verified source and sanitized operating evidence. Original hardware diagnostics, backup artifacts, restore receipts, screenshots, private runtime values, and protected records remain in their approved evidence systems. Planning acceptance does not prove deployment."
cleanup_path: "Keep active until all required Campaigns and Quest-level gates pass. Close through a final Noctua completion audit, Prime Quest Board and continuity-register synchronization, restart-safe Sunset, and verified merged-main readback."
last_verified: 2026-07-17
---

# Quest — Prometheus's Fire

## 1. Quest identity

**Quest ID:** `QUEST-PROMETHEUS-FIRE-20260701`
**Parent Project:** Project Odyssey
**Owning Operation:** Operation Prometheus Foundation
**Supporting Projects:** Phoenix, Artemis, Helios, Codex
**Current lane:** `UPDATE -> VERIFY`
**Current route:** `PF-C01 -> PF-C01-M02 Preserve the Old Flame Preview`
**Current state:** `IN_PROGRESS`

## 2. Purpose

Prometheus's Fire converts Prometheus into Atlas's stable, recoverable, privately administered Proxmox compute and service node without bypassing Citadel readiness, Forge storage boundaries, Phoenix restore proof, or Atlas approval gates. This source records architecture and proof requirements only; it does not claim deployment.

The Quest coordinates clean source and future proof for:

- Prometheus hardware and Proxmox foundation;
- private administration and rescue access;
- narrow Forge, Hammer, and Anvil mounts;
- Prometheus-to-Forge backup and destructive Phoenix restore proof;
- Crucible and exclusive Intel Arc Pro B50 passthrough;
- a dedicated Nexus Living Memory VM with deterministic routing and mission state;
- PF-C06 disposition of Matrix / Element from the active baseline;
- future Plex LXC and controlled Forge-to-Prometheus cutover;
- observability through Notum's Watch;
- final source, recovery, and completion audit.

The accepted launch envelope is:

```text
Prometheus / Proxmox
├── Crucible VM — 28 GB RAM
├── Nexus Living Memory VM — 10 GB RAM
└── Plex LXC — 12 GB RAM

Protected Proxmox reserve — 8 GB
Flexible headroom — 6 GB
Total — 64 GB
```

Launch rules are no ballooning and no memory overcommit. Crucible may grow
only after measured concurrent-load proof. Temporary restore guests require an
explicit RAM reallocation or guest-shutdown plan.

The thin-provisioned NVMe planning envelope is approximately 64 GB for host
ISOs/templates, 350 GB for Crucible, 120 GB for Nexus, and 150 GB for Plex;
the remaining usable capacity is reserved for pool/filesystem overhead,
snapshots, temporary restore needs, and growth. Exact remaining capacity is
unknown until storage is formatted and measured.

## 3. Approved topology baseline

```text
Prometheus / Proxmox
├── Crucible VM — 28 GB RAM
├── Nexus Living Memory VM — 10 GB RAM
└── Plex LXC — 12 GB RAM

Protected Proxmox reserve — 8 GB
Flexible headroom — 6 GB
Total launch envelope — 64 GB
```

### Resource envelope

| Guest or reserve | RAM |
|---|---:|
| Crucible VM | 28 GB |
| Nexus Living Memory VM | 10 GB |
| Plex LXC | 12 GB |
| Permanent planned guests | 50 GB |
| Protected Proxmox reserve | 8 GB |
| Flexible headroom | 6 GB |

Rules:

- Prometheus remains a 64 GB baseline.
- Ballooning and memory overcommit are disabled at launch.
- The B50 is planned for exclusive passthrough to Crucible and is not shared with Forge.
- The iGPU remains reserved for Prometheus display/recovery needs and future Plex Quick Sync proof.
- Crucible may grow only after measured concurrent-load proof.
- Temporary restore guests require an explicit RAM reallocation or guest-shutdown plan.

### NVMe planning envelope

This is a thin-provisioned, expandable plan rather than a measured capacity
claim:

| Planned area | Approximate capacity |
|---|---:|
| Proxmox host, ISO, and templates | 64 GB |
| Crucible VM | 350 GB |
| Nexus Living Memory VM | 120 GB |
| Plex LXC | 150 GB |

Remaining usable capacity is reserved for pool and filesystem overhead,
snapshots, temporary restore needs, and future growth. Exact remaining
capacity must be measured after storage formatting and pool creation.

## 4. Desired end state

Prometheus's Fire is complete only when:

1. Prometheus runs Proxmox VE stably with verified 64 GB memory.
2. Primary private administration and an independent rescue route are proven.
3. Forge mounts are narrow, persistent, and fail safely.
4. Prometheus backs up to Forge / Anvil and Phoenix proves an independent recovery copy.
5. A destructive canary restore succeeds.
6. Crucible passes B50 passthrough, model-runtime, backup, restore, and rollback proof.
7. Nexus passes deterministic intake, validation, approval, quarantine, mission-state, and receipt proof on the dedicated VM substrate, with PostgreSQL, full-text search, and `pgvector` as the Phase 1 retrieval direction.
8. PF-C06 records that Matrix / Synapse / Element are not part of the active Prometheus baseline and preserves lineage without claiming deployment or retirement.
9. Plex passes metadata restore, acceleration, recording, playback, concurrency, reboot, rollback, and cutover proof before leaving Forge; its application database, metadata, cache, and transcode workspace remain on Prometheus local NVMe.
10. Notum's Watch improves observability without becoming a mandatory control dependency or Prometheus prerequisite.
11. Noctua verifies the final topology and exact evidence.
12. The Prime Quest Board and continuity register remain synchronized, with generated projections refreshed separately.
13. Required Windows-specific work and Codex continuity are safely evacuated from the current Prometheus Windows installation before destructive action.
14. Forge retains the persistent Helios backend while Apollo provides the separately bounded interactive Helios Control Deck.
15. Prime Ascendant is an official architecture-refinement Quest; this mission does not implement it or authorize runtime.

## 5. Explicit exclusions

The baseline does not include:

- a generic Docker VM;
- a Disposable Browser VM;
- a Helios VM or full Helios migration to Prometheus;
- a separate n8n guest;
- HAOS on Prometheus;
- Paperless on Prometheus;
- Jellyfin;
- Immich;
- Nextcloud;
- Kavita;
- Komga;
- Calibre / ebook-convert;
- m4b-tool;
- Matrix, Synapse, and Element as active Prometheus workloads;
- public model, Nexus, n8n, or Proxmox endpoints;
- Qdrant as a Phase 1 requirement;
- Proxmox Backup Server as an immediate requirement;
- acting Kandra workers before governance and tool gates pass;
- automatic UPS shutdown or ONT / Eero recovery without a separate Phoenix / Beacon Preview and proof;
- Living Memory application semantics, Dawnshard, Gitea cutover, or a private Atlas website.

Forge retains HAOS, Paperless-ngx, Dozzle, Diun, and the persistent Helios backend: Gluetun, qBittorrent, Prowlarr, Sonarr, Radarr, optional Readarr, automated watchers and import workflows, storage-adjacent processing, Audiobookshelf, and current Plex until separately proven cutover.

Apollo may host the on-demand interactive Helios Control Deck: Libation, FileBot GUI, MediaInfo, MKVToolNix GUI, Subtitle Edit, optional bounded HandBrake or FFmpeg work, dashboards, and manual inspection or approval. Hermes and Iris are Helios clients only. Prometheus hosts neither Helios role.

# Campaigns

## Campaign PF-C01 — Forge the Vessel

**Owner:** Odyssey / Prometheus Foundation
**Support:** Phoenix / Keystone
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

Required proof:

1. Apollo is commissioned as the fixed Windows orchestration endpoint.
2. Required Windows applications and Windows-specific Codex workflows operate on Apollo.
3. Hermes can independently access Prime, GitHub, Element, and approved private administration surfaces.
4. Iris remains a nonblocking companion and is not treated as the sole source, approval, administration, or recovery route.
5. Every relevant Prometheus repository and working directory is identified.
6. Dirty worktrees, uncommitted changes, unpushed commits, local branches, and local-only artifacts are reconciled.
7. Required Prime source and branches are visible in GitHub or preserved through another approved route.
8. Active Codex work is completed, safely stopped, or transferred.
9. A representative Windows-specific workflow resumes on Apollo.
10. A representative portable command and administration workflow succeeds from Hermes.
11. Windows recovery media, system-image disposition, manufacturer drivers, and rollback expectations are preserved.
12. No credential, recovery key, token, private key, or secret enters Prime or ordinary migration artifacts.
13. A later exact Execute gate authorizes Windows removal or Proxmox installation.

The continuity proof must also record matching-memory and extended-memory
testing, NVMe health, WHEA/PCIe/USB/KVM/thermal stability, firmware and BIOS
state, virtualization/IOMMU/ReBAR/iGPU/B50 state, and Citadel power, cooling,
cabling, console, and recovery readiness. These are proof requirements, not
claims that any device or software has been changed.

**Exit gate:** Apollo and Hermes continuity is proven, Windows recovery posture is preserved, and a separately approved destructive-action Preview may be prepared. Until then, Windows removal and Proxmox installation remain blocked.

## Campaign PF-C02 — Light the First Flame

**Owner:** Odyssey / Prometheus Foundation
**Support:** Aegis / Shadesmar Access
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

## Campaign PF-C03 — Carry the Phoenix Ember

**Owner:** Phoenix / Restore Runbook and Recovery Drill
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
- Nexus VM backup/restore, PostgreSQL base-backup and WAL/PITR direction,
  Plex metadata/configuration restoration, and a recovery copy not confined to
  Forge.

## Campaign PF-C04 — Ignite the Crucible

**Owner:** Artemis / Operation Kandra and AI Governance
**Support:** Odyssey / Prometheus Foundation
**Status:** `BLOCKED_BY_PF-C03`
**Depends on:** PF-C03

Build Crucible as the Artemis local-intelligence VM.

Required proof:

- base VM backup and restore before passthrough;
- safe IOMMU grouping without unsupported overrides;
- exclusive B50 passthrough;
- host administration independent of the B50;
- pinned Intel / OpenVINO runtime;
- Soulcaster local generation, embeddings, and reranking;
- active Spren baseline and replacement discipline;
- Open WebUI private model-lab posture;
- read-only Atlas mirror, Indexer, and Mnemosyne boundaries;
- Qdrant deferred from Phase 1 until measured need is proven;
- cold-load, reboot, reset, thermal, cancellation, soak, backup, restore, and rollback tests;
- no durable-action authority during probation.

## Campaign PF-C05 — Raise the Nexus Vessel

**Owner:** Artemis / Operation Nexus
**Support:** Codex / AI Governance
**Status:** `BLOCKED_BY_PF-C04`
**Depends on:** PF-C03 and PF-C04

Build Nexus as a dedicated QEMU VM substrate for the deterministic integration
and mission-state service. This Campaign owns substrate proof, not the later
Prime Ascendant application semantics.

Required proof:

- 10 GB RAM planning baseline and approximately 120 GB expandable local-NVMe disk;
- 4–6 vCPU planning range;
- n8n single-main with PostgreSQL;
- Python / FastAPI integration surface;
- ClamAV/FreshClam and private health endpoints;
- Gemstone quarantine, hashing, archive safety, ClamAV, and manifest validation;
- approval state, retries, timeouts, mission register, and Receipt Gemstone creation;
- restricted private Kandra call path;
- no broad Proxmox, Forge, GitHub, shell, merge, deletion, or cleanup authority;
- application-aware backup and restore;
- base-backup and WAL path to Forge with sanitized recovery receipts.

## Campaign PF-C06 — Close the Matrix Gate

**Owner:** Artemis / Operation Nexus
**Support:** Phoenix / AI Governance
**Status:** `BLOCKED_BY_PF-C05`
**Depends on:** PF-C03 and PF-C05

Disposition Matrix, Synapse, and Element as removed from the active Prometheus
baseline. Preserve the PF-C06 lineage and do not claim that Matrix was
deployed and then retired.

Required proof:

- no current Matrix/Element deployment requirement;
- no Matrix dependency for Nexus or Plex;
- VS Code/Apollo and a future private Atlas website replace the immediate
  interaction need;
- any future communications requirement must justify a separate source
  decision or Quest.

## Campaign PF-C07 — Raise Relay

**Owner:** Helios / Operation Relay
**Support:** Odyssey / Phoenix
**Status:** `BLOCKED_BY_PF-C03_AND_RESOURCE_REVIEW`
**Depends on:** PF-C03 and PF-C04/PF-C05 resource review

Build the future Plex LXC and perform a separately approved controlled cutover from Forge.

Required proof:

- unprivileged LXC;
- 12 GB memory and 8 vCPU baseline;
- iGPU / Quick Sync acceleration;
- metadata and transcode on Prometheus NVMe;
- Anvil media read-only;
- narrow DVR write path;
- metadata/configuration restore;
- guide, Live TV, DVR recording, completed playback, concurrent clients, reboot recovery, remote access, and rollback;
- Forge Plex remains intact until final disposition.

## Campaign PF-C08 — Close the Aegis Ring

**Owner:** Odyssey / Aegis and Tempest
**Support:** Phoenix, Artemis, Helios, Beacon
**Status:** `BLOCKED_BY_PF-C04_TO_PF-C07`
**Depends on:** PF-C04, PF-C05, PF-C06, PF-C07

Complete integrated observability, failure testing, source alignment, and Quest closeout.

Required proof:

- Notum's Watch Uptime Kuma, Homepage, watchdog, diagnostics, outage journal, optional proven UPS telemetry, and read-only emergency Prime recovery clone;
- Prometheus, guest, storage, network, thermal, and backup monitoring;
- alert delivery that does not make recovery depend on Prometheus;
- integrated reboot, dependency-loss, backup, restore, and rollback tests;
- no automatic shutdown, plug cycling, or ONT / Eero recovery unless separately approved;
- exact configuration manifests and sanitized runbooks;
- Prime Quest Board and continuity-register reconciliation;
- PF-C06 Matrix disposition and no stale Matrix dependency;
- PostgreSQL/WAL health, backup/restore boundaries, and no public endpoints;
- final Strikeforce and Noctua audit;
- restart-safe Sunset.

Prometheus's Fire may consume Notum's Watch observability when available. It does not own Notum's Watch, does not sequence Notum's Watch behind Prometheus, and must not treat Nightwatcher as a current separate active node. Nightwatcher is superseded lineage preserved under Notum's Watch.

## 6. Current gate

```text
Quest state: IN_PROGRESS
Campaign PF-C01: IN_PROGRESS
PF-C01-M01 Mission Seal: PROVEN_WITH_CARRY_FORWARD
PF-C01-M02 Preserve the Old Flame: READY_FOR_PREVIEW
Apollo commissioning: NOT PROVEN
Hermes independent route: NOT PROVEN
Iris role: SOURCE_ACCEPTED / NONBLOCKING
Windows wipe: BLOCKED
Proxmox installation: BLOCKED
Operational readiness: NOT CLEARED
Runtime deployment: NOT STARTED
```

The next safe action is the exact PF-C01-M02 Preserve the Old Flame Preview. This Quest does not authorize device renames, application migration, Windows removal, Proxmox installation, physical, firmware, network, storage, power, service, or infrastructure execution by itself.
