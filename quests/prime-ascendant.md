---
title: "Quest — Prime Ascendant"
status: Active
owner: "Project Artemis / Operation Harmony"
supporting_projects:
  - "Project Codex"
  - "Project Odyssey"
  - "Project Elantris"
  - "Project Helios"
source_type: Quest
canonical_scope: "Parent Quest for the future self-hosted living-memory and orchestration chapter of Prime."
protected_level: High
routes_from:
  - atlas-prime.md
  - routing/command-surfaces.md
  - projects/project-registry.md
  - operations/operation-registry.md
  - operations/artemis-runtime-and-routing.md
  - quests/prime-reborn.md
  - quests/prometheus-fire.md
  - safety/atlas-safety-doctrine.md
routes_to:
  - quests/prime-ascendant-covenant.md
  - quest-board/quest-board-v1.json
  - continuity/prime-continuity-register-r01.json
  - governance/atlas-aegis.md
  - governance/atlas-strikeforce.md
  - governance/shard-doctrine.md
  - operations/artemis-runtime-and-routing.md
  - quests/prime-reborn.md
  - quests/prometheus-fire.md
  - recovery/elantris-recovery.md
private_boundary: "Store only clean doctrine, campaign status, gates, sanitized evidence pointers, and completion claims. Protected runtime facts, credentials, tokens, PHI, raw finance evidence, and private exports remain outside Prime."
evidence_boundary: "This Quest records source and sanitized proof only. Planning and source presence do not prove deployment, recovery, model use, Gitea parity, or private-site security."
cleanup_path: "Keep active until all Campaign and Quest gates pass. Close through integrated proof, recovery, restart-safe Sunset, explicit route-retirement evidence, and merged-main readback."
last_verified: 2026-07-17
---

# Quest — Prime Ascendant — The Dawnshard Covenant

## Identity and posture

**Quest ID:** `QUEST-PRIME-ASCENDANT-20260717`  
**Subtitle:** `The Dawnshard Covenant`  
**Parent Project:** Project Artemis  
**Owning Operation:** Operation Harmony
**Supporting Projects:** Codex, Odyssey, Elantris, Helios
**Current lane:** `PLAN -> UPDATE -> VERIFY`  
**Current route:** `PA-C01 — Write the Covenant`  
**Current state:** `ACTIVE — ARCHITECTURE REFINEMENT`  
**Runtime:** `NOT STARTED`  
**Canonical cutover:** `NOT AUTHORIZED`  
**Legacy route retirement:** `NOT AUTHORIZED`

Prime Ascendant is the controlled, phased self-hosted Prime chapter. The detailed constitutional context is kept in exactly one companion: [`quests/prime-ascendant-covenant.md`](prime-ascendant-covenant.md). The Quest answers where we are, what is next, and which boundaries apply; the Covenant answers why, what remains unresolved, and how to safely restart.

## Major boundaries

- Prime Reborn remains the repository reconstruction, parity, recovery, and cutover-readiness Quest.
- Prometheus's Fire remains the host, Proxmox, VM/LXC, storage, network, backup, restore, hardware, and recovery substrate Quest.
- Prime Ascendant owns future application semantics, Operation Coppermind, Operation Phoenix, Operation Harmony, Emberdark, Dawnshard, the private Glass Codex control surface, local intelligence coordination, workflow refraction, and future Gitea cutover semantics.
- Prime Git remains durable doctrine and accepted source. Coppermind is the future PostgreSQL operational-memory system. Emberdark is Harmony's governed transit, validation, routing, mission-state, quarantine, and receipt System. Dawnshard is the restart-safe projection Coppermind prepares for Athena. PostgreSQL full-text search plus `pgvector` is the initial retrieval direction; Qdrant is deferred until demonstrated need.
- Perpendicularity is the approved Google Drive crossing; Dynamic and Navigator are Cognitive Shadow collections that retrieve, preserve, prepare, and route Gemstones across Emberdark. Kandra are restricted mission-bound workers, and TenSoon verifies both pre-Coppermind intake and exact Phoenix draft candidates without granting permanence.
- Phoenix is Codex's canonical-source maintenance Operation. Elantris owns backup, restore, rollback, and recovery. Controlled Burn and Phoenix Burn retain their current meanings pending a later bounded redefinition.
- Runtime, infrastructure, database, Gitea, website, lifecycle, migration, and route-retirement work require later bounded source and proof transactions. No public endpoint, unrestricted SQL authority, secret, or protected raw evidence is authorized here.

## Campaign roadmap

| Campaign | Owner | Initial purpose | Current gate |
|---|---|---|---|
| PA-C01 — Write the Covenant | Artemis / Harmony with Codex | Constitutional boundaries, source/memory relationships, protected data, rationale, unresolved decisions, and acceptance criteria. | `ACTIVE — ARCHITECTURE REFINEMENT` |
| PA-C02 — Raise the Coppermind | Codex / Coppermind with Artemis / Harmony and Elantris | PostgreSQL schemas, events, audit, retrieval, export, backup, restore, WAL, PITR, and reconciliation. | Depends on PA-C01 and substrate gates. |
| PA-C03 — Establish Emberdark | Artemis / Harmony | Governed intake, Dynamic and Navigator transport, Perpendicularity, authorization, receipts, idempotency, integrations, failure, and rollback. | Depends on PA-C01 and PA-C02 contracts. |
| PA-C04 — Shape the Dawnshard | Codex / Coppermind with Artemis / Harmony | Watermarked, stale-aware, fail-closed, restart-safe context projection from Coppermind for Athena. | Depends on a stable event contract. |
| PA-C05 — Open Glass Codex | Codex / Glass Codex with Artemis / Harmony | Private website/API, authentication, approvals, health, receipts, read views, and bounded actions. | Depends on Emberdark and Coppermind contracts; no public endpoint. |
| PA-C06 — Crown Gitea | Codex / Phoenix with Elantris | Shadow parity, backup, mirror, recovery, rollback, access, and future cutover evidence. | Cutover remains a separate Jayson gate. |
| PA-C07 — Awaken Harmony | Artemis / Harmony and AI Governance | Sazed, bounded Kandra, Cognitive Shadows, retrieval, embeddings, reranking, OCR, assistance, and resource measurement. | Safe interfaces required. |
| PA-C08 — Bind the Realms | Artemis / Harmony with Odyssey, Elantris, Codex, and Helios | Integrate components, prove boundaries and degraded modes, and keep monitoring nonauthoritative. | Component contracts and substrate gates. |
| PA-C09 — Temper the Old Blades | Codex / Source Governance | Compare current routes, prove parity and rollback, and only then consider simplification or retirement. | No route retires during Quest creation. |
| PA-C10 — Prove the Dawn | All owners through Source Governance | Integrated backup, restore, restart, rollback, reconciliation, stale handling, private access, model boundaries, cutover readiness, and final proof. | Requires applicable Campaign evidence. |

## Dependencies and next safe gate

PA-C01 may proceed as source architecture now. PA-C02 and PA-C03 require appropriate Prometheus's Fire gates before deployment; PA-C04 requires a stable event contract; PA-C05 requires Emberdark authorization plus Coppermind read/write contracts; PA-C06 starts in shadow and cannot authorize cutover; PA-C07 may follow safe interfaces; PA-C08 requires proven boundaries; PA-C09 requires old and new evidence; and PA-C10 requires the complete evidence chain. Notum's Watch may remain parallel-safe and nonauthoritative.

The next safe gate is PA-C01 covenant review ending at `COVENANT ACCEPTED / ARCHITECTURE BOUNDARIES EXPLICIT / NO RUNTIME AUTHORIZED`. PA-C01 is not complete. No Campaign, runtime state, infrastructure state, Gitea authority, lifecycle doctrine, or legacy-route status advances by creating this Quest or its Covenant.
