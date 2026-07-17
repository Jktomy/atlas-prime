---
title: "Atlas Infrastructure Source"
atlas_id: "prime.infrastructure.source"
status: "ACTIVE"
source_type: "ARCHITECTURE"
authority_class: "CANONICAL_AUTHORED_SOURCE"
owner_project: "Project Odyssey"
owner_operation: "Operation Prometheus Foundation"
protected_level: "HIGH"
---

# Atlas Infrastructure Source

This source records clean architecture and recovery boundaries. It contains no addresses, credentials, account values, private capacity data, device secrets, or claim of deployment.

## Durable roles

- **Prometheus** — Proxmox compute and service foundation; minimal host services, private administration, independent rescue, narrow storage mounts, backup, and restore proof precede service migration.
- **Forge** — storage backbone. **Hammer** is staging/processing; **Anvil** is durable archive. Mounts and write paths remain least-privilege.
- **Crucible** — Artemis local-intelligence VM; model runtime and accelerator use require isolation, backup, restore, thermal, soak, and rollback proof.
- **Nexus** — dedicated Living Memory QEMU VM substrate for deterministic routing and mission state; no broad infrastructure or source authority.
- **Matrix / Synapse / Element** — removed from the active Prometheus baseline; PF-C06 preserves lineage without claiming deployment or retirement.
- **Citadel/Gatehouse** — physical infrastructure, WAN edge, power, cooling, wiring, observability, and rescue boundary.
- **Notum's Watch** — observability and diagnostics that must not become routing, identity, DNS, DHCP, public endpoint, source truth, or automatic recovery authority.
- **Beacon/HAOS** — home automation boundary with safe manual fallback.
- **Helios/Relay** — media and OTA service boundary; cutover requires restore, playback, recording, acceleration, reboot, and rollback proof.

## Human-operated Atlas endpoints

| Name | Accepted device assignment | Clean role |
|---|---|---|
| **Apollo** | Lenovo M720q | Fixed Windows orchestration endpoint, Windows-specific Atlas and Codex work surface, and interactive Helios Control Deck |
| **Hermes** | MacBook Pro | Portable primary Atlas command endpoint, independent administration surface, and future Seon macOS bridge vessel |
| **Iris** | iPad Pro | Nonblocking dashboard, communication, viewing, and human-approval companion |

These assignments are clean source decisions, not proof that operating-system names, hostnames, Tailscale records, account records, or private device registers have changed. Apollo, Hermes, and Iris are human-operated endpoints. None is source truth, storage authority, routing authority, identity authority, persistent automation authority, or an indispensable Atlas server.

Loss or shutdown of Apollo, Hermes, or Iris must not stop persistent Forge automation, qBittorrent, Audiobookshelf, current Plex, access to finalized Anvil media, Prime source recovery, or administration through another approved route.

## Helios placement boundary

Forge retains the persistent Helios backend:

- Gluetun;
- qBittorrent;
- Prowlarr;
- Sonarr and Radarr;
- optional Readarr;
- automated watchers and import workflows;
- storage-adjacent processing;
- Audiobookshelf;
- current Plex until controlled cutover.

Apollo may host the on-demand, human-interactive Helios Control Deck:

- Libation;
- FileBot GUI;
- MediaInfo;
- MKVToolNix GUI;
- Subtitle Edit;
- optional bounded HandBrake or FFmpeg work;
- dashboards;
- manual inspection, naming, and approval.

Hermes may access Helios administration and dashboards remotely. Iris may display status and support human review or approval. Neither Hermes nor Iris is a persistent Helios backend.

## Prometheus launch planning envelope

The accepted source planning envelope is:

```text
Crucible VM — 28 GB RAM
Nexus Living Memory VM — 10 GB RAM
Plex LXC — 12 GB RAM
Protected Proxmox reserve — 8 GB
Flexible headroom — 6 GB
Total — 64 GB
```

Launch uses no memory ballooning or overcommit. Crucible may grow only after
measured concurrent-load proof, and temporary restore guests require explicit
RAM reallocation or guest shutdown. The plan is not deployment evidence.

The thin-provisioned local-NVMe plan is approximately 64 GB for host
ISOs/templates, 350 GB for Crucible, 120 GB for Nexus, and 150 GB for Plex.
Remaining usable capacity is reserved for pool/filesystem overhead,
snapshots, temporary restore needs, and growth; exact remaining capacity is
unknown until storage formatting and pool creation are measured.

## Infrastructure rules

- Foundation and recovery precede broad migration.
- Major applications do not run directly on the Proxmox host.
- Plex application database, metadata, artwork, cache, and transcode workspace
  remain on Prometheus local NVMe; Forge/Anvil holds media, completed DVR
  media, application backups, and recovery copies through narrow paths.
- Nexus Phase 1 retrieval uses PostgreSQL relational state, PostgreSQL full-text
  search, and `pgvector`; Qdrant is deferred until measured need is proven.
- Public exposure, automatic power action, destructive restore, storage reclassification, and credential changes require separate protected authority.
- A planned topology is not an active runtime fact.
- All configuration committed to Prime is sanitized and reproducible; protected values come from external secret/evidence systems at runtime.
- Failure of observability, Nexus, Kandra, or generated projections must not block Prime source recovery.

Active execution campaigns live in `quests/prometheus-fire.md` and `quests/notums-watch.md`.
