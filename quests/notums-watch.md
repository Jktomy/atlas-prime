---
title: "Quest - Notum's Watch"
status: Active
owner: "Project Odyssey / Operation Citadel / Gatehouse Infrastructure"
supporting_projects:
  - "Project Elantris"
  - "Project Beacon"
  - "Project Codex"
source_type: Quest
canonical_scope: "Parent Quest for bringing Notum's Watch forward as Gatehouse/Citadel observability and rescue infrastructure, including the interim Notum vessel, future Notum Phoenix vessel, Nightwatcher lineage, and backup-capacity boundaries."
protected_level: High
routes_from:
  - atlas-prime.md
  - atlas-start-here.md
  - atlas-index.md
  - operations/protocol-library.md
  - infrastructure/atlas-infrastructure-source.md
routes_to:
  - governance/source-lifecycle.md
  - infrastructure/atlas-infrastructure-source.md
  - recovery/elantris-recovery.md
  - quest-board/quest-board-v1.json
  - quests/prometheus-fire.md
  - governance/atlas-strikeforce.md
  - noctua.md
private_boundary: "Store only clean architecture, sanitized readiness steps, non-secret status labels, and safe evidence pointers. Do not store IP addresses, private network maps, device registers, UPS serials, account data, credentials, tokens, MFA or recovery codes, real environment values, raw private runtime logs, PHI, raw finance evidence, or protected household evidence."
evidence_boundary: "This Quest coordinates source decisions and Jayson-executed readiness packages. It is not deployment evidence. Hardware health, installation, runtime telemetry, backup manifests, capacity figures, restore receipts, and private topology details must be verified from approved evidence systems before promotion."
cleanup_path: "Keep active until Notum's Watch has passed its source-readback, interim-vessel, future-vessel, backup-capacity, and lineage disposition gates. Close only through final Noctua/Strikeforce review, Workboard synchronization, and merged-main readback."
last_verified: 2026-07-23
---

# Quest - Notum's Watch

## 1. Quest identity

**Quest ID:** `quest.notums-watch`
**Parent Project:** Project Odyssey
**Owning Operation:** Operation Citadel / Gatehouse Infrastructure
**Supporting Projects:** Elantris, Beacon, Codex
**Current lane:** `PLAN -> VERIFY`
**Current route:** `Official Quest source -> infrastructure readback -> Jayson-executed readiness package`
**Current state:** `READY_FOR_JAYSON_EXECUTION_PACKAGE`

## 2. Purpose

Notum's Watch brings forward the small, durable infrastructure role that watches Olympus from the Citadel, keeps lightweight status visible, preserves sanitized rescue notes, and helps Jayson understand outages without becoming a router, recovery authority, source authority, AI host, or broad service host.

The Quest coordinates:

- Citadel physical/source alignment;
- the interim Notum vessel;
- the future Notum Phoenix vessel;
- the absorbed Nightwatcher lineage;
- bounded network, power, service-availability, and self-health observation;
- independent outage alerts that do not depend on Prometheus, Grafana, Harmony, Coppermind, or Gitea;
- read-only emergency Codex access;
- backup and restore boundaries;
- capacity proof before any full-Forge-backup claim;
- Prometheus independence and parallel-safe sequencing;
- final source, Workboard, and generated-report closeout in separate transactions.

## 3. Source-readback rule for this Quest

Any answer about Notum's Watch, Notum, Notum Phoenix, Nightwatcher, Citadel observability, UPS monitoring, or Notum-related backup capacity must first follow `governance/source-lifecycle.md`.

Minimum readback route:

1. `atlas-index.md`
2. `quests/notums-watch.md`
3. `infrastructure/atlas-infrastructure-source.md`
4. `recovery/elantris-recovery.md`
5. `quests/prometheus-fire.md` only when Prometheus dependency, sequencing, or observability consumption is discussed
6. approved private evidence only when current hardware, capacity, topology, UPS identity, cabling, or runtime facts are needed

Use evidence labels:

- `SOURCE_ACCEPTED`
- `PLANNED_NOT_DEPLOYED`
- `READY_FOR_JAYSON_EXECUTION`
- `PENDING_PRIVATE_EVIDENCE`
- `RUNTIME_UNVERIFIED`
- `HISTORICAL_SUPERSEDED_LINEAGE`

Memory-only answers about current Notum runtime state are not allowed.

## 4. Canonical architecture

### Zones

Gatehouse = the master-bedroom-closet WAN-edge zone where Emberdark reaches Olympus.

Citadel = the office infrastructure zone for core rack, compute, power, cabling, console, and physical maintenance.

Olympus = the household environment observed by Notum; it is not the name of a router or firewall.

### Roles and vessels

Notum's Watch = the durable Quest and role family for Citadel/Olympus observability, diagnostics, rescue notes, and outage understanding.

Notum = the preferred interim vessel for Notum's Watch, using the 2014 Mac mini only after Jayson verifies hardware health and explicitly proceeds with runtime work. Its clean current posture is returning to the Citadel and awaiting a separately authorized minimal-Linux conversion; no installation or runtime proof is claimed.

Notum Phoenix = the future permanent two-bay x86 Gatehouse vessel. It may inherit Notum duties and later become a capacity-proven backup/recovery target, but it is not purchased, deployed, or proven by this source.

Nightwatcher = the superseded separate-role lineage for monitor-only power and continuity observation. Its history is preserved. It is absorbed into Notum's Watch as lineage and evidence vocabulary; it is not deleted merely for cleanliness.

## 5. Interim Notum baseline

The interim Notum baseline is:

- minimal Linux endpoint;
- ordinary wired Ethernet; 1 Gb is sufficient for the bounded baseline unless a later monitoring role proves otherwise;
- Tailscale private access if separately approved;
- restricted SSH;
- Uptime Kuma as the lightweight availability and incident surface;
- Network UPS Tools only after exact UPS model, communications port, USB detection, supported variables, and safe cabling are proven;
- independent checks for local interface state, gateway reachability, external IP reachability, DNS resolution, and a small external HTTPS response so “connected” is not confused with “internet usable”;
- Forge, Prometheus, Apollo, HAOS, Grafana/Prometheus monitoring, and later Gitea, Glass Codex, Coppermind API, and Emberdark reachability checks where applicable;
- outage journal;
- direct alert relay to Zeus that does not depend on Prometheus or Grafana and may use HAOS only as a secondary route;
- diagnostics surface;
- read-only emergency Codex clone;
- sanitized runbooks;
- configuration backup and restore notes;
- reboot and power-return proof;
- clear disablement and rollback path.

`Homepage` is optional rather than required. Grafana is the future richer analytical dashboard on the Prometheus substrate; Glass Codex may later present only the minimized Notum health projection. Notum does not host Prometheus/Grafana, Loki, AI models, databases, Gitea, Coppermind, Emberdark, or HAOS.

Optional later additions require separate proof:

- SmokePing;
- Speedtest Tracker;
- Netdata;
- lightweight log viewer;
- additional dashboards;
- a separately governed continuity-action lane.

## 6. Observation model

Notum reports observations rather than making semantic or recovery decisions. It distinguishes at least:

| Utility | Gateway | Internet | Meaning |
|---|---|---|---|
| online | reachable | usable | normal |
| on battery | reachable | usable | household power outage with a remote-action window |
| online | reachable | unusable | ISP, WAN, DNS, or external-connectivity failure |
| online | unreachable | unusable | local gateway or network failure |
| on battery | reachable | unusable | power outage plus lost external communication |
| unknown | any | any | monitoring evidence unavailable or stale |

A future synthesized Olympus health view may combine these observations with critical-service states, but it must preserve `CURRENT`, `STALE`, `OFFLINE`, `UNKNOWN`, and `LAST_KNOWN_GOOD` distinctions.

## 7. What Notum's Watch is not

Notum's Watch is not:

- routing;
- DNS authority;
- DHCP authority;
- identity authority;
- public endpoint authority;
- packet-surveillance or household-traffic analysis;
- Helios host;
- Plex host;
- AI compute;
- Home Assistant host;
- HAOS replacement;
- source truth;
- broad backup authority in the interim baseline;
- broad infrastructure control plane;
- plug-cycling controller;
- automatic outage recovery controller;
- automatic shutdown or power-restoration controller in the initial baseline.

HAOS remains within the Beacon/Home Olympus boundary unless separately revisited.

Failure of Notum's Watch must not stop core Atlas systems.

## 8. Future continuity-action lane

A later bounded Notum continuity-action contract may evaluate graceful SSH shutdown, Proxmox API shutdown sequencing, Wake-on-LAN, or preapproved load shedding. That later lane requires exact dependencies, secret isolation, dry-run proof, graceful shutdown and ambiguous-result proof, manual override, recovery/rollback, and separate Jayson authority.

Until that proof exists, Notum observes, alerts, recommends, and preserves the remote-action opportunity. It does not autonomously shut down, start, power-cycle, or restore Prometheus, Forge, Apollo, HAOS, networking, or another system.

## 9. Notum Phoenix and backup capacity truth

Notum Phoenix is a future permanent Gatehouse vessel, not current deployment proof.

The future Notum Phoenix may become a full-Forge-backup or recovery target only after a protected capacity audit covers:

- current Forge dataset size;
- retained backup classes;
- retention depth;
- snapshot or versioning overhead;
- filesystem overhead;
- growth headroom;
- excluded replaceable data;
- restore target and restore workflow;
- off-device or off-Forge copy.

No source may claim that a proposed first disk can hold a full Forge backup until that audit is complete and safe evidence exists.

RAID 1 is availability, not backup. A later matching second disk may improve availability, but it does not replace versioning, off-device recovery, or restore proof.

## 10. Relationship to Prometheus's Fire

Notum's Watch is parallel-safe with Prometheus's Fire.

Notum's Watch does not wait for Prometheus's Fire unless a specific implementation step proves a real dependency. The Prometheus substrate may host Prometheus monitoring software and Grafana for deeper metrics, history, and analysis. Notum independently hosts Uptime Kuma, power/network checks, outage journaling, and direct alerts so Prometheus may be shut down during an outage without silencing the watchtower.

Prometheus may consume Notum observations, but Prometheus recovery must not depend solely on Notum's Watch. Notum's Watch owns Citadel/Olympus observation and alert posture; Prometheus's Fire owns the Prometheus Proxmox and monitoring substrate.

## 11. Glass Codex health presentation boundary

Glass Codex may present only the minimized, read-only health projection defined by `governance/notum-glass-codex-health-contract.md`. Notum's Watch and Sentinel retain source identity, collection, evaluation, alerting, and outage-record ownership. `CURRENT`, `STALE`, `OFFLINE`, `UNKNOWN`, and `LAST_KNOWN_GOOD` are explicit and non-interchangeable; expired data cannot appear current.

The view grants no power, restart, network, route, restore, failover, deployment, deletion, alert-acknowledgement, monitoring-configuration, or automated-recovery authority. Glass Codex or Apollo failure removes the view only. Notum failure does not block Cloud Atlas, Prime recovery, Elantris, or household-critical workloads. Mission #284 connects no telemetry and does not advance NW-C01.

## 12. READY_FOR_JAYSON_EXECUTION package

### Package identity

`NW-C01-READY_FOR_JAYSON_EXECUTION`

### Boundary

Codex may prepare and verify source, checklists, and packages. Jayson performs or approves any hardware movement, wipe, install, cable change, account action, network change, service deployment, UPS connection, backup execution, restore test, shutdown control, or startup control.

### Allowed Jayson-side readiness work after source merge

- Confirm the 2014 Mac mini is available for possible Notum use and has returned to the Citadel.
- Inspect physical condition, power behavior, and storage health.
- Preserve any needed existing data before wipe or repurpose.
- Confirm wired Ethernet location and power path.
- Confirm the exact UPS model, communications port, USB cable, and whether NUT-compatible telemetry is physically available.
- Confirm whether minimal Linux installation should proceed.
- If proceeding, install and prove only the bounded interim Notum baseline.
- Prove utility-online, on-battery, low-battery where safely testable, internet-usable, internet-unusable, service-down, alert-delivery, reboot, and power-restored behavior.
- Preserve sanitized evidence pointers and keep protected runtime values outside GitHub.

### Stop conditions

Stop before action if:

- the hardware role is uncertain;
- any existing data preservation is unresolved;
- power or cabling is unsafe;
- network identity would require private values in GitHub;
- the exact UPS model or communications path is unverified;
- a service would become routing, DNS, DHCP, identity, public exposure, broad control, packet surveillance, or automatic recovery authority;
- backup capacity claims are requested without private capacity audit evidence;
- the proposed work becomes Prometheus deployment, HAOS migration, Helios migration, Plex migration, AI compute work, or automatic shutdown/startup work.

## 13. Campaigns

### Campaign NW-C01 - Bring Notum's Watch Forward

**Owner:** Odyssey / Citadel-Gatehouse Infrastructure
**Support:** Codex / Elantris / Beacon
**Status:** `READY_FOR_JAYSON_EXECUTION`
**Depends on:** merged source readback

Create the source-grounded Jayson execution package for interim Notum readiness while stopping before runtime action by Codex.

Exit only after:

- this Quest is routed;
- active runtime and Citadel source agrees;
- Nightwatcher lineage is marked superseded rather than silently deleted;
- capacity and authority limits are explicit;
- Jayson has a safe readiness checklist.

### Campaign NW-C02 - Light the Watch

**Owner:** Odyssey / Citadel-Gatehouse Infrastructure
**Support:** Beacon / Elantris
**Status:** `BLOCKED_BY_NW-C01_AND_JAYSON_EXECUTION`
**Depends on:** NW-C01

Build and prove the interim Notum baseline on the approved vessel.

### Campaign NW-C03 - Raise Notum Phoenix

**Owner:** Odyssey / Phoenix
**Support:** Beacon / Forge Storage
**Status:** `DEFERRED_PENDING_CAPACITY_AND_HARDWARE_PROOF`
**Depends on:** NW-C01, private capacity audit, hardware decision

Define and later prove the future two-bay x86 Gatehouse vessel.

### Campaign NW-C04 - Preserve Nightwatcher Lineage

**Owner:** Codex / Odyssey
**Support:** Elantris / Beacon
**Status:** `SOURCE_LINEAGE_PENDING_WORKBOARD_TRANSACTION`