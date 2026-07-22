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
- **Harmony VM** — Artemis resident-intelligence VM; Harmony/Sazed, permitted local models, Kandra, retrieval, intake, embeddings, reranking, and exclusive Intel Arc Pro B50 use require isolation, backup, restore, thermal, soak, and rollback proof.
- **Atlas VM** — operational-soul VM containing the logically separate Emberdark, Coppermind, and Phoenix Systems and Operations. Co-location never grants canonical-source, unrestricted SQL, infrastructure, recovery, READY, or merge authority.
- **Plex LXC** — household-critical primary and only final-state Plex server. Plex application state remains on Prometheus local NVMe while media and completed DVR recordings remain on Forge/Anvil.
- **Jellyfin on Forge** — local-only continuity player for stored media and completed DVR recordings. It is not a Plex standby, shares no Plex application database, and owns no automatic failover or HDHomeRun/DVR authority in this continuity role.
- **Matrix / Synapse / Element** — removed from the active Prometheus baseline; PF-C06 preserves lineage without claiming deployment or retirement.
- **Citadel/Gatehouse** — physical infrastructure, WAN edge, power, cooling, wiring, observability, and rescue boundary.
- **Notum's Watch** — observability and diagnostics that must not become routing, identity, DNS, DHCP, public endpoint, source truth, or automatic recovery authority.
- **Beacon/HAOS** — Home Olympus automation boundary with safe manual fallback. Morningstar is its Jayson/Jocelyn dashboard, and Operation Tempest owns physical Home Olympus maintenance with Odyssey support where infrastructure is involved.
- **Helios/Relay** — media and OTA service boundary; cutover requires restore, playback, recording, acceleration, reboot, degraded-mode, and rollback proof.

`Crucible` is reserved for a future bounded transformation or testing system and is not an active Prometheus guest.

## Human-operated Atlas endpoints

| Name | Accepted device assignment | Clean role |
|---|---|---|
| **Apollo** | Lenovo M720q | Fixed Windows orchestration endpoint, Windows-specific Atlas and Codex work surface, and interactive Helios Control Deck |
| **Hermes** | MacBook Pro | Portable primary Atlas command endpoint, independent administration surface, and future Seon macOS bridge vessel |
| **Iris** | iPad Pro | Nonblocking dashboard, communication, viewing, and human-approval companion |
| **Zeus** | Jayson’s iPhone | Nonblocking mobile communication, viewing, and human-approval endpoint |

These assignments are clean source decisions, not proof that operating-system names, hostnames, Tailscale records, account records, or private device registers have changed. Apollo, Hermes, Iris, and Zeus are human-operated endpoints. None is source truth, storage authority, routing authority, identity authority, persistent automation authority, or an indispensable Atlas server.

Loss or shutdown of Apollo, Hermes, Iris, or Zeus must not stop persistent Forge automation, qBittorrent, Audiobookshelf, finalized Anvil media, household media continuity, Prime source recovery, or administration through another approved route.

Apollo endpoint startup, shutdown, environment isolation, source disposition,
package/reinstall, remote-route, degraded-mode, and recovery proof follow
`governance/apollo-remote-operator-continuity-contract.md`. Apollo is preferred,
but Hermes retains independent administration and Prime recovery; Iris and Zeus
remain nonblocking companions. The contract is a public-clean proof plan, not
evidence that Apollo, native VS Code, Glass Codex, credentials, or private
remote access have been commissioned.

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
- media and completed DVR recordings;
- local-only Jellyfin continuity after its separately authorized deployment;
- current Plex only until controlled cutover and later final disposition.

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

The Samsung television's direct antenna input is the accepted live-TV continuity route. It does not depend on Prometheus, Plex, Jellyfin, or HDHomeRun streaming. During a Plex or Prometheus outage, Jellyfin may provide stored media and completed-DVR playback, but new Plex-scheduled recordings are not guaranteed.

## Prometheus launch planning envelope

The accepted source planning envelope is:

```text
Harmony VM — 24 GB fixed RAM
Atlas VM — 12 GB fixed RAM
Plex LXC — 16 GB maximum
Protected Proxmox reserve — 8 GB
Flexible headroom — 4 GB
Total — 64 GB
```

Launch uses no memory ballooning or overcommit. The Plex value is a ceiling rather than expected continuous use. The protected host reserve remains unavailable for routine reassignment. Harmony or Atlas may grow only after measured concurrent-load proof, and temporary restore guests require explicit RAM reallocation or guest shutdown. Sustained swap, an OOM event, recording failure, or Plex playback degradation blocks resource promotion. The plan is not deployment evidence.

The thin-provisioned local-NVMe plan is approximately 64 GB for host ISOs/templates, 350 GB for Harmony, 180–200 GB for Atlas, and 150 GB for Plex. Remaining usable capacity is reserved for pool/filesystem overhead, snapshots, temporary restore needs, and growth; exact remaining capacity is unknown until storage formatting and pool creation are measured.

## Infrastructure rules

- Foundation and recovery precede broad migration.
- Major applications do not run directly on the Proxmox host.
- Harmony receives exclusive planned B50 passthrough and no infrastructure or permanence authority.
- Plex receives the planned iGPU/Quick Sync path; host administration and rescue must remain independent of that mapping.
- Plex application database, configuration, metadata, artwork, cache, and transcode workspace remain on Prometheus local NVMe; Forge/Anvil holds media, completed DVR media, application backups, and recovery copies through narrow paths.
- Missing Forge mounts must fail safely: Prometheus and Plex remain administratively available, absent media is not silently removed, DVR writes cannot fall back to an unintended local path, and no local filesystem may fill because a remote mount disappeared.
- Plex playback and DVR recording outrank discretionary Harmony/Atlas batch work, Jellyfin scans, and unproven backup activity. Heavy work must be throttleable or deferrable while playback or recording is active.
- The Atlas VM keeps OS/application, Coppermind data, Phoenix/Gitea state, and Emberdark workflow/quarantine data in independently bounded storage areas with separate service identities, database roles, backups, and restore procedures.
- The Atlas VM is the selected future Phoenix/Gitea shadow substrate direction, but GitHub remains canonical and no Gitea installation, database activation, parity claim, or cutover is authorized.
- Coppermind Phase 1 retrieval uses PostgreSQL relational state, PostgreSQL full-text search, and `pgvector`; Qdrant is deferred until measured need is proven.
- Public exposure, automatic power action, destructive restore, storage reclassification, and credential changes require separate protected authority.
- A planned topology is not an active runtime fact.
- All configuration committed to Prime is sanitized and reproducible; protected values come from external secret/evidence systems at runtime.
- Failure of observability, Harmony, Atlas VM, Emberdark, Kandra, Jellyfin, or generated projections must not block Prime source recovery.

Active execution campaigns live in `quests/prometheus-fire.md` and `quests/notums-watch.md`.
