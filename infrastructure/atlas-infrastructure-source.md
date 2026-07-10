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
- **Nexus** — deterministic routing and mission-state service; no broad infrastructure or source authority.
- **Matrix** — private command-room transport; no public registration or federation without a separate approved design.
- **Citadel/Gatehouse** — physical infrastructure, WAN edge, power, cooling, wiring, observability, and rescue boundary.
- **Notum's Watch** — observability and diagnostics that must not become routing, identity, DNS, DHCP, public endpoint, source truth, or automatic recovery authority.
- **Beacon/HAOS** — home automation boundary with safe manual fallback.
- **Helios/Relay** — media and OTA service boundary; cutover requires restore, playback, recording, acceleration, reboot, and rollback proof.

## Infrastructure rules

- Foundation and recovery precede broad migration.
- Major applications do not run directly on the Proxmox host.
- Public exposure, automatic power action, destructive restore, storage reclassification, and credential changes require separate protected authority.
- A planned topology is not an active runtime fact.
- All configuration committed to Prime is sanitized and reproducible; protected values come from external secret/evidence systems at runtime.
- Failure of observability, Nexus, Hermes, or generated projections must not block Prime source recovery.

Active execution campaigns live in `quests/prometheus-fire.md` and `quests/notums-watch.md`.
