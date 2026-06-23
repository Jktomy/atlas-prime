---
title: "Atlas Prime Core Doctrine"
atlas_id: "atlas-prime.core"
format_version: "1.0"
status: "PROPOSED"
source_type: "CORE_DOCTRINE"
authority_class: "CANONICAL_AUTHORED_SOURCE"
owner_project: "Codex"
owner_operation: "Source Governance"
canonical_scope: "Atlas identity, Project model, source hierarchy, realm shorthand, node and layer roles, construction posture, cutover boundary, and recovery-before-migration doctrine."
protected_level: "CRITICAL"
routes_from:
  - "README.md"
routes_to:
  - "atlas-aegis.md"
  - "atlas-knowledge-lifecycle.md"
  - "codex/codex-source-update-standard.md"
  - "specs/atlas-prime/repository-format-v1.md"
private_boundary: "Do not store secrets, credentials, tokens, MFA or recovery codes, private keys, seed phrases, real .env values, PHI, raw finance or account evidence, private runtime values, IP addresses, network maps, device registers, protected exports, or other raw protected evidence in GitHub."
evidence_boundary: "Original evidence systems remain authoritative outside GitHub. Atlas Prime stores only clean source, clean summaries, structured clean state, generated projections, migration provenance, and clean pointers."
supersedes: []
cleanup_path: "Keep as compact core doctrine. Move detailed Project, Operation, protocol, and implementation material to routed child files rather than allowing this file to become a second archive."
last_verified: "2026-06-21"
---

# Atlas Prime Core Doctrine

## Prime rule

Atlas is the umbrella ecosystem and governance layer. Atlas is not one of the Projects.

`Jktomy/atlas-prime` is the intended successor clean-source repository, but `Jktomy/atlas-codex` remains canonical until verified cutover.

```text
Atlas governs.
Athena advises and authors.
Codex remembers.
Artemis coordinates.
Phoenix protects and proves recovery.
Spear performs bounded deterministic repository mechanics.
Noctua watches and verifies.
Jayson decides permanence.
```

## Construction source hierarchy

1. Current explicit Jayson instruction.
2. Existing Spear v0.3 foundation preserved in the June 21 Sunset package.
3. June 21 lifecycle audit and locked decisions.
4. Current `atlas-prime` merged source.
5. Current `atlas-codex` as canonical until cutover and as migration evidence.
6. Approved original evidence sources.
7. Athena inference, explicitly labeled.

This construction hierarchy governs the intended Prime design. It does not prematurely revoke the current operational authority of `atlas-codex`.

## Atlas Project model

Atlas uses twelve Projects:

| # | Project | Durable ownership |
|---:|---|---|
| 1 | Odyssey | Infrastructure, Prometheus, Forge, network, Citadel |
| 2 | Codex | Source truth, documents, protocols, templates |
| 3 | Artemis | AI coordination, Nexus, Hermes, future intelligence |
| 4 | Phoenix | Backup, restore, recovery, power resilience |
| 5 | Beacon | Smart home and household automation |
| 6 | Helios | Media lifecycle, Sun Maker, Sun Eater |
| 7 | Midas | Finance, investing, household planning |
| 8 | Chiron | Professional optometry and PHI-free clinic reasoning |
| 9 | Raphael | Personal health and wellness tracking |
| 10 | Genesis | Family, children, education, cooking, meal planning |
| 11 | Pegasus | Travel, itineraries, packing, trip documents |
| 12 | Arcanum | Hobbies, fandom, lore, personal research |

Critical classifications:

- Vulcan is a future AI compute Node under Artemis.
- Crucible is the future local AI services stack on Vulcan or another approved Artemis compute surface.
- Nexus is an Operation under Artemis.
- Sun Maker and Sun Eater are Operations under Helios.
- Kindling and Grazing Ember remain protected sub-Operations under Helios.
- Morningstar belongs under Beacon.
- Pulse belongs under Raphael.
- Genesis is a Project.

## Realm shorthand

Realm names are informal cross-Project shorthand only:

- **Physical Realm** — where Atlas exists materially.
- **Cognitive Realm** — where Atlas thinks and coordinates.
- **Spiritual Realm** — where Atlas preserves clean source and continuity.

Realm names do not create Projects, Operations, folders, vaults, or evidence sources.

## Node and layer doctrine

- Prometheus runs approved compute and services after foundation gates.
- Forge stores and serves durable data.
- Hammer is the staging layer.
- Anvil is the archive layer.
- Citadel houses the core.
- Gatehouse receives the network.
- Shadesmar provides private connectivity.
- Sentinel displays only.
- Apollo commands.
- Iris controls.

Detailed runtime values, IP addresses, device registers, network maps, credentials, and private infrastructure paths remain outside GitHub.

## Command and authority doctrine

Use the lanes:

- PLAN
- BUILD
- VERIFY
- AUDIT
- UPDATE

Use Route Lines for substantial Atlas work. Use Decision Boxes only for unresolved choices with downstream consequences.

Preview -> Execute is required before:

- durable source changes;
- migration or cutover;
- deletion, move, rename, archive, retirement, or supersession execution;
- automation or external-system actions;
- infrastructure-impacting changes;
- finance, account, legal, insurance, mortgage, estate, or medical-record actions;
- repository-setting changes;
- Spear writer activation;
- source-truth promotion.

Atlas Prime has no normal Direct-Main Fast Path. Source changes use narrow branches and pull requests, stop before merge, receive Noctua audit, and are manually merged by Jayson.

## Recovery-before-migration rule

For Prometheus and comparable major operational transitions:

1. Citadel readiness first.
2. Foundation second.
3. Storage mounts third.
4. Phoenix restore proof fourth.
5. Broad services later.

Do not migrate broad services or declare source cutover before backup paths and a real restore test exist.

## Clean-source and evidence rule

GitHub stores clean source, not raw evidence. Original evidence systems remain authoritative.

- Midas uses Tiller, brokers, statements, Gmail confirmations, and original records.
- Chiron excludes PHI and raw EHR material.
- Raphael keeps private medical records outside GitHub.
- Infrastructure private runtime truth stays in approved private sources.
- Passwords and secrets remain in the password manager.

## Cutover boundary

Prime may be promoted from `SHADOW` only when the repository-format, migration, Spear, Noctua, generated-view, and Phoenix Reborn gates are satisfied and Jayson explicitly approves the canonical switch.

Until then, new Prime files are proposed target architecture and `atlas-codex` remains governing operational source.
