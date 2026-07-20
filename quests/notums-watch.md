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
  - infrastructure/atlas-infrastructure-source.md
routes_to:
  - governance/source-lifecycle.md
  - infrastructure/atlas-infrastructure-source.md
  - infrastructure/atlas-infrastructure-source.md
  - infrastructure/atlas-infrastructure-source.md
  - recovery/elantris-recovery.md
  - recovery/elantris-recovery.md
  - quest-board/quest-board-v1.json
  - quests/prometheus-fire.md
  - governance/atlas-strikeforce.md
  - noctua.md
private_boundary: "Store only clean architecture, sanitized readiness steps, non-secret status labels, and safe evidence pointers. Do not store IP addresses, private network maps, device registers, UPS serials, account data, credentials, tokens, MFA or recovery codes, real environment values, raw private runtime logs, PHI, raw finance evidence, or protected household evidence."
evidence_boundary: "This Quest coordinates source decisions and Jayson-executed readiness packages. It is not deployment evidence. Hardware health, installation, runtime telemetry, backup manifests, capacity figures, restore receipts, and private topology details must be verified from approved evidence systems before promotion."
cleanup_path: "Keep active until Notum's Watch has passed its source-readback, interim-vessel, future-vessel, backup-capacity, and lineage disposition gates. Close only through final Noctua/Strikeforce review, Workboard synchronization, and merged-main readback."
last_verified: 2026-07-09
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

Notum's Watch brings forward the small, durable infrastructure role that watches the Gatehouse and Citadel, keeps lightweight status visible, preserves sanitized rescue notes, and helps Jayson understand outages without becoming a router, recovery controller, or broad service host.

The Quest coordinates:

- Gatehouse and Citadel physical/source alignment;
- the interim Notum vessel;
- the future Notum Phoenix vessel;
- the absorbed Nightwatcher lineage;
- bounded observability and diagnostics;
- read-only emergency Codex access;
- backup and restore boundaries;
- capacity proof before any full-Forge-backup claim;
- Prometheus independence and parallel-safe sequencing;
- final source, Workboard, and generated-report closeout in separate transactions.

## 3. Source-readback rule for this Quest

Any answer about Notum's Watch, Notum, Notum Phoenix, Nightwatcher, Gatehouse, Citadel observability, or Notum-related backup capacity must first follow `governance/source-lifecycle.md`.

Minimum readback route:

1. `atlas-index.md`
2. `quests/notums-watch.md`
3. `infrastructure/atlas-infrastructure-source.md`
4. `infrastructure/atlas-infrastructure-source.md`
5. `infrastructure/atlas-infrastructure-source.md`
6. `recovery/elantris-recovery.md`
7. `recovery/elantris-recovery.md` when backup or disk capacity is discussed
8. `quests/prometheus-fire.md` only when Prometheus dependency, sequencing, or observability consumption is discussed
9. approved private evidence only when current hardware, capacity, topology, or runtime facts are needed

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

### Roles and vessels

Notum's Watch = the durable Quest and role family for Gatehouse/Citadel observability, diagnostics, rescue notes, and outage understanding.

Notum = the preferred interim vessel for Notum's Watch, using the 2014 Mac mini only after Jayson verifies hardware health and explicitly proceeds with runtime work.

Notum Phoenix = the future permanent two-bay x86 Gatehouse vessel. It may inherit Notum duties and later become a capacity-proven backup/recovery target, but it is not purchased, deployed, or proven by this source.

Nightwatcher = the superseded separate-role lineage for monitor-only power and continuity observation. Its history is preserved. It is absorbed into Notum's Watch as lineage and evidence vocabulary; it is not deleted merely for cleanliness.

## 5. Interim Notum baseline

The interim Notum baseline is:

- minimal Linux endpoint;
- wired Ethernet;
- Tailscale private access if separately approved;
- restricted SSH;
- Uptime Kuma;
- Homepage;
- network, DNS, gateway, Forge, Prometheus, HAOS, and Plex reachability checks where applicable;
- UPS telemetry only if hardware and cabling are proven;
- outage journal;
- alert relay that does not make recovery depend on Prometheus;
- diagnostics surface;
- read-only emergency Codex clone;
- sanitized runbooks;
- configuration backup and restore notes;
- reboot and power-return proof;
- clear disablement and rollback path.

Optional later additions require separate proof:

- SmokePing;
- Speedtest Tracker;
- Netdata;
- lightweight log viewer;
- additional dashboards.

## 6. What Notum's Watch is not

Notum's Watch is not:

- routing;
- DNS authority;
- DHCP authority;
- identity authority;
- public endpoint authority;
- Helios host;
- Plex host;
- AI compute;
- Home Assistant host;
- HAOS replacement;
- source truth;
- broad backup authority in the interim baseline;
- broad infrastructure control plane;
- plug-cycling controller;
- automatic outage recovery controller.

HAOS remains on Forge unless separately revisited.

Failure of Notum's Watch must not stop core Atlas systems.

## 7. Notum Phoenix and backup capacity truth

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

## 8. Relationship to Prometheus's Fire

Notum's Watch is parallel-safe with Prometheus's Fire.

Notum's Watch does not wait for Prometheus's Fire unless a specific implementation step proves a real dependency. Prometheus may later consume Notum's Watch observability, but Prometheus recovery must not depend solely on Notum's Watch.

Prometheus's Fire owns the Prometheus Proxmox foundation. Notum's Watch owns Gatehouse/Citadel observability and rescue posture.

## 9. READY_FOR_JAYSON_EXECUTION package

### Package identity

`NW-C01-READY_FOR_JAYSON_EXECUTION`

### Boundary

Codex may prepare and verify source, checklists, and packages. Jayson performs or approves any hardware movement, wipe, install, cable change, account action, network change, service deployment, backup execution, or restore test.

### Allowed Jayson-side readiness work after source merge

- Confirm the 2014 Mac mini is available for possible Notum use.
- Inspect physical condition, power behavior, and storage health.
- Preserve any needed existing data before wipe or repurpose.
- Confirm wired Ethernet location and power path.
- Confirm whether UPS telemetry is physically available.
- Confirm whether minimal Linux installation should proceed.
- If proceeding, install and prove only the bounded interim Notum baseline.
- Preserve sanitized evidence pointers and keep protected runtime values outside GitHub.

### Stop conditions

Stop before action if:

- the hardware role is uncertain;
- any existing data preservation is unresolved;
- power or cabling is unsafe;
- network identity would require private values in GitHub;
- a service would become routing, DNS, DHCP, identity, public exposure, broad control, or automatic recovery authority;
- backup capacity claims are requested without private capacity audit evidence;
- the proposed work becomes Prometheus deployment, HAOS migration, Helios migration, Plex migration, or AI compute work.

## 10. Campaigns

### Campaign NW-C01 - Bring Notum's Watch Forward

**Owner:** Odyssey / Citadel-Gatehouse Infrastructure
**Support:** Codex / Elantris / Beacon
**Status:** `READY_FOR_JAYSON_EXECUTION`
**Depends on:** merged source readback

Create the source-grounded Jayson execution package for interim Notum readiness while stopping before runtime action by Codex.

Exit only after:

- this Quest is routed;
- active runtime and Citadel/Gatehouse source agrees;
- Nightwatcher lineage is marked superseded rather than silently deleted;
- capacity limits are explicit;
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
**Depends on:** NW-C01 source merge/readback

Preserve Nightwatcher as superseded separate-role lineage absorbed into Notum's Watch. Do not erase historical references that are explicitly archival.

## 11. Completion gates

Notum's Watch is complete only when:

1. active source routes to this Quest;
2. Gatehouse/Citadel definitions are aligned;
3. interim Notum readiness is either executed and verified or explicitly deferred;
4. Nightwatcher lineage is preserved and not confused with an active separate node;
5. Prometheus remains independent and parallel-safe;
6. backup capacity claims are evidence-based;
7. HAOS remains correctly placed on Forge unless separately changed;
8. Noctua and Strikeforce verify the final source state;
9. Active Workboard and generated support refreshes are synchronized through separate transactions.

## 12. Golden readback fixtures

| Fixture question | Required answer shape |
|---|---|
| Bring Notum's Watch forward | Use this Quest, runtime placement, Citadel/Gatehouse runbook, and Jayson execution package; stop before Codex runtime action. |
| What is Notum Phoenix? | Future permanent two-bay x86 Gatehouse vessel for Notum's Watch; not current deployment proof; backup role requires capacity audit. |
| Where does Nightwatcher live now? | Historical superseded lineage absorbed into Notum's Watch; preserve history, do not keep it as an active separate planned node without new source. |
| Does Notum's Watch wait for Prometheus's Fire? | No. It is parallel-safe unless a specific step proves a real dependency. |
| Can the proposed first disk hold full Forge backup? | Unknown until protected capacity audit proves dataset, retention, overhead, growth, exclusions, and headroom. |
| Where does Home Assistant live? | HAOS remains on Forge unless separately revisited. |

## 13. Current gate

```text
Quest state: READY_FOR_JAYSON_EXECUTION_PACKAGE
Operational readiness: NOT CLEARED
Runtime deployment: NOT STARTED
Backup-capacity proof: NOT CLEARED
Nightwatcher lineage: SOURCE_LINEAGE_PENDING_WORKBOARD_TRANSACTION
```

The next safe action is source merge/readback, then the separate Workboard transactions, then Jayson-side readiness only inside `NW-C01-READY_FOR_JAYSON_EXECUTION`.
