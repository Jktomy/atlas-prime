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
canonical_scope: "Parent Quest for converting Prometheus into a stable, recoverable Proxmox compute platform with the approved Crucible VM, Nexus LXC, Matrix LXC, and future Plex LXC topology."
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
  - noctua.md
  - sunsetting-protocol.md
private_boundary: "Store only clean architecture, campaign status, gates, sanitized evidence pointers, and completion claims. Do not store IP addresses, private network maps, device registers, credentials, tokens, MFA or recovery codes, real environment values, PHI, raw finance evidence, account data, or unrestricted terminal output."
evidence_boundary: "This Quest coordinates verified source and sanitized operating evidence. Original hardware diagnostics, backup artifacts, restore receipts, screenshots, private runtime values, and protected records remain in their approved evidence systems. Planning acceptance does not prove deployment."
cleanup_path: "Keep active until all required Campaigns and Quest-level gates pass. Close through a final Noctua completion audit, Workboard synchronization, restart-safe Sunset, and verified merged-main readback."
last_verified: 2026-07-09
---

# Quest — Prometheus's Fire

## 1. Quest identity

**Quest ID:** `QUEST-PROMETHEUS-FIRE-20260701`
**Parent Project:** Project Odyssey
**Owning Operation:** Operation Prometheus Foundation
**Supporting Projects:** Phoenix, Artemis, Helios, Codex
**Current lane:** `PLAN -> VERIFY`
**Current route:** `Official Quest source -> Campaign 1 Preview -> staged evidence-based execution`
**Current state:** `READY_FOR_CAMPAIGN_1_PREVIEW`

## 2. Purpose

Prometheus's Fire converts Prometheus into Atlas's stable, recoverable, privately administered Proxmox compute and service node without bypassing Citadel readiness, Forge storage boundaries, Phoenix restore proof, or Atlas approval gates.

The Quest coordinates:

- Prometheus hardware and Proxmox foundation;
- private administration and rescue access;
- narrow Forge, Hammer, and Anvil mounts;
- Prometheus-to-Forge backup and destructive Phoenix restore proof;
- Crucible and exclusive Intel Arc Pro B50 passthrough;
- Nexus deterministic routing and mission state;
- Matrix / Element private command-room transport;
- future Plex LXC and controlled Forge-to-Prometheus cutover;
- observability through Notum's Watch;
- final source, recovery, and completion audit.

## 3. Approved topology baseline

```text
Prometheus / Proxmox
├── Crucible VM — 20 GB
├── Nexus LXC — 6 GB
├── Matrix LXC — 4 GB
└── Plex LXC — 12 GB, future cutover

Temporary proof object:
└── Phoenix restore-test LXC
```

### Resource envelope

| Guest or reserve | RAM |
|---|---:|
| Crucible VM | 20 GB |
| Nexus LXC | 6 GB |
| Matrix LXC | 4 GB |
| Plex LXC | 12 GB |
| Permanent planned guests | 42 GB |
| Protected Proxmox reserve | 8 GB |
| Unassigned headroom | 14 GB |

Rules:

- Prometheus remains a 64 GB baseline.
- Ballooning and memory overcommit are disabled at launch.
- A memory upgrade is not a Quest prerequisite.
- The B50 is planned for exclusive passthrough to Crucible and is not shared with Forge.
- The iGPU remains reserved for Prometheus display/recovery needs and future Plex Quick Sync proof.

## 4. Desired end state

Prometheus's Fire is complete only when:

1. Prometheus runs Proxmox VE stably with verified 64 GB memory.
2. Primary private administration and an independent rescue route are proven.
3. Forge mounts are narrow, persistent, and fail safely.
4. Prometheus backs up to Forge / Anvil and Phoenix proves an independent recovery copy.
5. A destructive canary restore succeeds.
6. Crucible passes B50 passthrough, model-runtime, backup, restore, and rollback proof.
7. Nexus passes deterministic intake, validation, approval, quarantine, mission-state, and receipt proof.
8. Matrix passes private access, encryption, signing, and recovery proof.
9. Plex passes metadata restore, acceleration, recording, playback, concurrency, reboot, rollback, and cutover proof before leaving Forge.
10. Notum's Watch improves observability without becoming a mandatory control dependency or Prometheus prerequisite.
11. Noctua verifies the final topology and exact evidence.
12. The Active Workboard and Sunset closeout are synchronized.

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
- Element Web as a dedicated guest;
- public Matrix registration or federation;
- public model, Nexus, n8n, or Proxmox endpoints;
- Proxmox Backup Server as an immediate requirement;
- acting Hermes agents before governance and tool gates pass;
- automatic UPS shutdown or ONT / Eero recovery without a separate Phoenix / Beacon Preview and proof.

Forge retains HAOS, Paperless-ngx, Audiobookshelf, the complete Helios stack, Dozzle, Diun, and current Plex until separately proven cutover.

# Campaigns

## Campaign PF-C01 — Forge the Vessel

**Owner:** Odyssey / Prometheus Foundation
**Support:** Phoenix / Keystone
**Status:** `READY_FOR_PREVIEW`
**Depends on:** none

Prove physical, firmware, memory, storage, power, cooling, cabling, and recovery-console readiness before replacing the current operating system.

Exit only after:

- matching memory is installed and passes extended testing;
- NVMe health is recorded;
- WHEA, PCIe, USB/KVM, thermal, and stability concerns are resolved or bounded;
- Windows recovery and driver evidence are preserved;
- virtualization, IOMMU, ReBAR, iGPU, and B50 state are documented;
- Citadel power, UPS, cooling, cabling, and console access are acceptable.

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
- temporary canary LXC creation;
- off-host backup;
- original deletion;
- restore under a different ID;
- boot, marker, and network verification;
- sanitized restore receipt;
- independent off-Forge recovery plan.

## Campaign PF-C04 — Ignite the Crucible

**Owner:** Artemis / Operation Hermes and AI Governance
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
- read-only Atlas mirror, Indexer, Qdrant, and Mnemosyne boundaries;
- cold-load, reboot, reset, thermal, cancellation, soak, backup, restore, and rollback tests;
- no durable-action authority during probation.

## Campaign PF-C05 — Raise Nexus

**Owner:** Artemis / Operation Nexus
**Support:** Codex / AI Governance
**Status:** `BLOCKED_BY_PF-C04`
**Depends on:** PF-C03 and PF-C04

Build Nexus as the deterministic integration and mission-state LXC.

Required proof:

- unprivileged LXC;
- n8n single-main with PostgreSQL;
- Python / FastAPI integration surface;
- Gemstone quarantine, hashing, archive safety, ClamAV, and manifest validation;
- approval state, retries, timeouts, mission register, and Receipt Gemstone creation;
- restricted private Hermes call path;
- no broad Proxmox, Forge, GitHub, shell, merge, deletion, or cleanup authority;
- application-aware backup and restore.

## Campaign PF-C06 — Open the Matrix

**Owner:** Artemis / Operation Nexus
**Support:** Phoenix / AI Governance
**Status:** `BLOCKED_BY_PF-C05`
**Depends on:** PF-C03 and PF-C05

Build the private Matrix / Element transport LXC.

Required proof:

- Synapse and dedicated PostgreSQL;
- private registration only;
- no federation;
- restricted Nexus bot identity;
- signing material protection;
- encrypted-room state;
- second-device and recovery-key restoration;
- database and application-state backup and restore;
- Element native-client operation.

## Campaign PF-C07 — Raise Relay

**Owner:** Helios / Operation Relay
**Support:** Odyssey / Phoenix
**Status:** `BLOCKED_BY_PF-C06`
**Depends on:** PF-C03 and PF-C06

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

- Notum's Watch Uptime Kuma, Homepage, watchdog, diagnostics, outage journal, optional proven UPS telemetry, and read-only emergency Codex clone;
- Prometheus, guest, storage, network, thermal, and backup monitoring;
- alert delivery that does not make recovery depend on Prometheus;
- integrated reboot, dependency-loss, backup, restore, and rollback tests;
- no automatic shutdown, plug cycling, or ONT / Eero recovery unless separately approved;
- exact configuration manifests and sanitized runbooks;
- Active Workboard reconciliation;
- final Strikeforce and Noctua audit;
- restart-safe Sunset.

Prometheus's Fire may consume Notum's Watch observability when available. It does not own Notum's Watch, does not sequence Notum's Watch behind Prometheus, and must not treat Nightwatcher as a current separate active node. Nightwatcher is superseded lineage preserved under Notum's Watch.

## 6. Current gate

```text
Quest state: READY_FOR_CAMPAIGN_1_PREVIEW
Operational readiness: NOT CLEARED
Runtime deployment: NOT STARTED
```

The next safe action is the exact PF-C01 Preview. This Quest does not authorize physical, firmware, operating-system, network, storage, power, service, or infrastructure execution by itself.
