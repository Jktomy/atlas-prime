---
title: "Notum / Glass Codex Health Boundary"
atlas_id: "prime.governance.notum-glass-codex-health-r01"
status: "CANONICAL_SOURCE_ARCHITECTURE"
source_type: "PROTOCOL"
authority_class: "CANONICAL_AUTHORED_SOURCE"
owner_project: "Project Odyssey"
owner_operation: "Operation Sentinel / Citadel-Gatehouse Infrastructure"
protected_level: "CRITICAL"
---

# Notum / Glass Codex health boundary

Notum's Watch and Sentinel own monitoring, collection, evaluation, alerting,
and outage records. Glass Codex Health is a read-only presentation surface. It
may consume a minimized, versioned health projection but never becomes the
monitor, source of truth, control plane, or recovery dependency.

The normative interface record is `governance/notum-glass-codex-health-v1.json`,
validated by `schemas/notum-glass-codex-health-v1.schema.json`.

## Projection and source identity

Every presented observation binds a stable public-clean source identity, the
source-reported observation time, the projection receipt time, a freshness
deadline, one explicit health state, a sanitized summary, and an optional
approved evidence pointer. A client must not infer freshness from display time,
rewrite source identity, or merge unrelated sources into one authoritative
status.

The only presentation states are:

- `CURRENT`: a source observation is inside its declared freshness window;
- `STALE`: a previously received observation is outside that window;
- `OFFLINE`: the monitoring authority explicitly reports the bounded target or
  source unavailable;
- `UNKNOWN`: there is no trustworthy state determination;
- `LAST_KNOWN_GOOD`: historical context shown with its original timestamp and
  never styled or sorted as current.

Missing, malformed, future-dated, or unverifiable telemetry renders `UNKNOWN`.
An expired observation renders `STALE`, even when its last value was healthy.
`LAST_KNOWN_GOOD` is context only and cannot suppress `STALE`, `OFFLINE`, or
`UNKNOWN`.

## Data minimization and permissions

The projection may contain service category, coarse state, sanitized summary,
timestamps, freshness policy, and approved evidence pointers. It excludes
credentials, tokens, private network maps, unrestricted logs, device registers,
raw topology, protected household evidence, control endpoints, and secrets.

Glass Codex receives read-only projection access. It has no power, restart,
network, routing, DNS, DHCP, restore, failover, deployment, deletion, alert
acknowledgement, monitoring configuration, or automated-recovery permission.
Links and buttons must not disguise a denied control action as navigation.

## Failure independence and recovery

Glass Codex or Apollo failure removes the view only: Notum's Watch and Sentinel
continue collection, evaluation, alerting, and outage recording. Notum failure
does not block Cloud Atlas operation, Prime clean-clone recovery, Elantris
restore, or household-critical workloads. A stale or unavailable projection
must degrade visibly and must not cause automated recovery or route changes.

Client recovery clears or quarantines cached protected material and rehydrates
only from a freshly authenticated projection. Monitoring recovery is owned by
Notum/Sentinel and never depends on Glass Codex state.

## Stop boundary

Mission #284 defines source architecture only. It reads no telemetry, deploys
no service, connects no monitoring source, changes no alert or control path,
and does not advance `NW-C01`, `PA-C05`, runtime, recovery, READY, or any
infrastructure gate.
