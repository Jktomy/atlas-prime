---
title: "Prime Ascendant Covenant — PA-C01 Context"
status: Active
owner: "Project Artemis / Operation Harmony"
source_type: Covenant
authority_class: "CANONICAL_AUTHORED_SOURCE"
parent_quest: "quests/prime-ascendant.md"
protected_level: High
routes_from:
  - quests/prime-ascendant.md
  - governance/atlas-aegis.md
  - governance/atlas-strikeforce.md
  - governance/shard-doctrine.md
  - governance/change-routes.md
  - operations/artemis-runtime-and-routing.md
  - quests/prime-reborn.md
  - quests/prometheus-fire.md
routes_to:
  - quest-board/quest-board-v1.json
  - continuity/prime-continuity-register-r01.json
  - governance/source-lifecycle.md
  - governance/quest-engine-continuity-contract.md
  - recovery/elantris-recovery.md
private_boundary: "This Covenant contains clean architecture, rationale, unresolved decisions, provenance, and sanitized restart guidance only. Private runtime facts, network maps, device registers, account data, PHI, raw finance evidence, credentials, tokens, keys, MFA/recovery codes, seed phrases, and real environment values remain outside Prime."
evidence_boundary: "Statements below are accepted source direction or explicit future evidence requirements. They do not claim deployment, recovery, parity, model use, Gitea shadow, private-site security, or lifecycle activation."
last_verified: 2026-07-20
---

# Prime Ascendant Covenant

## 1. Covenant purpose

This is the single detailed companion for **Prime Ascendant — The Dawnshard Covenant**. It consolidates the meaningful founding context needed to restart PA-C01 without a chat transcript, duplicated context map, or separate decision register. The parent Quest remains concise and authoritative for identity, state, roadmap, boundaries, and next gate.

Prime Ascendant is the controlled self-hosted Prime chapter. It is phased rather than a wholesale replacement event. It exists to reduce dependence on constrained or expensive external execution, create durable living memory, preserve one authoritative source, give Athena restart-safe context, enable bounded local orchestration and intelligence, preserve reversible migration and recovery, and retain proven workflows until replacements are proven.

The terminal PA-C01 gate is:

```text
COVENANT ACCEPTED
ARCHITECTURE BOUNDARIES EXPLICIT
NO RUNTIME AUTHORIZED
```

This Covenant does not complete PA-C01, activate lifecycle doctrine, or authorize runtime, infrastructure, migration, cutover, deletion, or route retirement.

## 2. Accepted architecture

### 2.1 Prime source and live memory

```text
Prime Git repository:
durable accepted source and doctrine

Operation Coppermind:
live operational state

Operation Harmony / Emberdark:
governed transit, application writer, and validation boundary

Dawnshard:
restart-safe context projection from Coppermind for Athena

PostgreSQL full-text search + pgvector:
initial retrieval stack

Qdrant:
deferred until demonstrated need.
```

Coppermind does not replace durable doctrine. Dawnshard is not a second source of truth. AI models, browser clients, and arbitrary workflows do not receive unrestricted direct SQL authority. Exact schemas, APIs, retention, event model, and retrieval thresholds remain unresolved decisions below.

### 2.2 Dawnshard conceptual target

The future restart-safe projection may contain:

```text
generated/dawnshard/latest/
├── 00-START-HERE.md
├── 01-OVERNIGHT-DELTA.md
├── 02-LIVE-VS-DURABLE-DRIFT.md
├── 03-ACTIVE-QUEST-BOARD.md
├── 04-RECENT-JAYSON-DECISIONS.md
├── 05-AWAITING-JAYSON.md
├── 06-CONTROLLED-BURN-QUEUE.md
├── 07-PHOENIX-BURN-QUEUE.md
├── 08-FEATHERS-AND-GOLDEN-WINGS.md
├── 09-RECENT-RECEIPTS.md
├── 10-NEXT-SAFE-GATES.md
├── manifest.json
└── SHA256SUMS.txt
```

It must eventually use an event sequence or watermark, fail closed, retain last-known-good output, visibly mark stale output, exclude secrets and protected raw evidence, support a portable approved backup twin, and avoid repeated large ZIP commits. This is a conceptual target, not an implementation claim.

### 2.3 Operation Harmony and Emberdark

Project Artemis is the durable owning domain, not a model identity. Operation Harmony is the durable workflow and resource boundary. Harmony and Sazed name the same resident intelligence in ordinary Atlas language; no separate Artemis-model identity exists or is created by this Covenant.

Harmony/Sazed provides frictionless RAG and bounded context assembly, OCR and intake normalization, capability awareness, delegation, worker coordination, result reconciliation, and lightweight intent interpretation when the active surface does not provide a stronger conversational lead. Routine retrieval, intake, and route selection should require no new user-facing command or approval. Harmony should perform small work directly when delegation would add complexity or latency without improving the result.

The interaction model is surface-dependent:

```text
ChatGPT:
Jayson → Athena intent/reasoning lead → Harmony context/intake/delegation → workers/tools → Athena response

VS Code or another approved surface without Athena:
Jayson → Harmony intent/orchestration lead → workers/tools → Harmony response
```

In ChatGPT, Harmony must not create a second planning ceremony or independently reinterpret an already-closed Athena mission. It may surface missing context, capability limits, or a real protected boundary. In VS Code and other approved surfaces without Athena, Harmony may interpret ordinary intent, gather repository and Coppermind context, select the appropriate model, Kandra, tool, or route, and reconcile the result. An immutable mission is executed or delegated without reopening intent unnecessarily.

Emberdark remains the governed transit, validated-intake, authorization, idempotency, reconciliation, workflow-execution, retry, mission-state, quarantine, audit-receipt, mediated-integration, failure-behavior, and controlled-export System. Harmony may request and supervise work through Emberdark, but the resident intelligence does not become the workflow engine or permanent state store. Perpendicularity is the approved Google Drive crossing. Dynamic retrieves and preserves Gemstone provenance; Navigator prepares and routes it; TenSoon verifies intake before Coppermind absorption and verifies the exact Phoenix draft before Athena audit. n8n may act through governed interfaces; it does not inherit broad database authority. Exact API shape, versioning, authorization model, write contracts, reconciliation algorithm, retry behavior, and audit format remain unresolved.

Harmony is not canonical source, permanent memory, infrastructure control, recovery authority, monitoring, a dashboard, a scheduler, a notification platform, or automatic permanence authority. Prime retains doctrine; Coppermind retains operational memory; Odyssey retains infrastructure; Elantris retains backup, restore, rollback, and recovery; Notum's Watch and Sentinel retain monitoring; and each human-facing interface retains its own presentation role.

### 2.4 Private Atlas control surface

The future Operation Glass Codex website/API is a private control surface for Jayson with local/mobile access, approvals, Quest views, Dawnshard views, health, receipts, and bounded actions. Tailscale or another separately approved private route is an accepted direction. No public endpoint is approved. Framework, authentication, authorization, session handling, and approval UX remain unresolved.

### 2.5 Gitea direction

Gitea may become future canonical Prime source only after shadow parity, backup, restore, rollback, mirror, mobile access, Athena access, and exact source identity are proven. GitHub Prime remains canonical until an explicit Preview → Execute and Jayson-approved cutover. Gitea host placement, database placement, mirror direction/cadence, branch/tag/PR parity, and rollback criteria remain unresolved.

### 2.6 Harmony/Sazed and local intelligence

Harmony/Sazed is the resident intelligence inside Operation Harmony. It may retrieve, summarize, classify, embed, rerank, perform OCR and intake, propose, coordinate bounded workers, and route to permitted local or external models. In ChatGPT, Athena remains the primary intent, reasoning, and conversational lead. On approved surfaces where Athena is absent, Harmony may lead ordinary interpretation and delegation.

Models, Kandra, and tools serving Harmony do not gain source authority, merge authority by inference, infrastructure authority, unrestricted database writes, or silent action authority. Model selection, routing implementation, resource allocation, evaluation, read boundaries, tool permissions, and delegation criteria remain future work. A future larger local model may serve Harmony, but its identity, hardware, and runtime are not decided here and it is not automatically named Artemis.

### 2.7 Node boundaries

| Node | Accepted role | Boundary |
|---|---|---|
| Prometheus | Proxmox host, Crucible, Emberdark, Plex, future runtime substrate | Host and recovery substrate; no application deployment is claimed here. |
| Forge | Storage backbone, Hammer/Anvil, persistent services, backup destination, possible future Gitea placement | Storage and protected backup boundary; no cutover is authorized. |
| Apollo | Human-operated workstation, VS Code, Codex, Git, PowerShell, interactive tools, administration | Not a persistent-service dependency. |
| Notum | Parallel-safe monitoring | No source, routing, automatic recovery, or blocking authority. |

### 2.8 Future Gitea/Phoenix pull-request validation augmentation

The future PA-C06 validation route is:

```text
Gitea pull-request event
→ Prime Integrity Cognitive Shadow under Artemis / Operation Harmony
→ immutable exact-base/exact-head validation carrier
→ bounded Kandra integrity executor
→ conditional Windows executor only when classification requires it
→ TenSoon exact-head verification
→ Operation Phoenix publishes or reports the draft candidate/status
→ Athena audit
→ Jayson-controlled permanence
```

The Prime Integrity Cognitive Shadow receives and validates one event, rejects
replay, moved heads, malformed repository/base/head identity, protected-data
ingress, and undeclared paths, and prepares an immutable mission carrier. It does
not judge permanence, mark READY, or merge. One bounded Kandra executes only the
mission-bound carrier and receives no standing repository authority. TenSoon
independently verifies the exact candidate head, changed-path inventory, checks,
and receipts and may report `VERIFIED_FOR_ATHENA_AUDIT`; it has no READY or MERGE
authority. Operation Phoenix owns canonical-source maintenance and future Gitea
branch, draft-PR, or commit-status publication. Phoenix does not own backup or
restore, which remains Elantris, and it never merges automatically.

The future Gitea model uses three logical contexts:

- `prime/integrity` — required repository/source policy, protected-data, JSON,
  schema, Project, Operation, Quest Board, continuity, routing, metadata,
  deterministic generated-current comparison, changed-path tests, and exact
  base/head/path identity.
- `prime/windows-compatibility` — conditional for PowerShell, Atlas Sword,
  Oathbringer, Windows launcher or resolution behavior, Thread Engine,
  Athena-route execution, validation/workflow, and unknown paths that fail closed.
- `prime/generated-current` — required for generated-only refresh candidates or
  wherever accepted source/generated parity applies.

GitHub remains canonical during this planning chapter. Its current main ruleset
still requires `validate (ubuntu-latest)` and `validate (windows-latest)`, so a
source-side migration must preserve those legacy contexts until the new contexts
are observed at exact heads and Jayson separately changes the ruleset. Proof
before removal requires one Windows-required candidate, one Windows-skipped
ordinary source candidate, successful new and legacy contexts, strict-base
readback, and a reviewed rollback. Rollback is a reviewed workflow revert that
restores the former job topology while the legacy contexts remain required.

No Gitea deployment, webhook activation, database activation, canonical cutover,
GitHub retirement, credential detail, private-network value, or route retirement
is authorized by this augmentation.

## 3. Separation of existing Quests

### Prime Reborn

Prime Reborn owns repository reconstruction, parity, source recovery, validation, cutover readiness, and recovery proof for Prime source. Prime Ascendant owns future Operation Coppermind, Operation Harmony and Emberdark, Dawnshard, Operation Glass Codex, Operation Phoenix source maintenance, future Gitea authority migration, local model coordination, and workflow refraction. Prime Ascendant must not erase or reinterpret Prime Reborn history.

### Prometheus's Fire

Prometheus's Fire owns host preparation, Proxmox, VMs/LXCs, storage, networking, backup, restore, host-level security, hardware, and recovery substrate. Prime Ascendant owns application semantics, schemas, state transitions, API contracts, Dawnshard, website behavior, source/memory reconciliation, future cutover semantics, and lifecycle/workflow evolution. Prometheus's Fire may complete infrastructure readiness without all Prime Ascendant features; Prime Ascendant runtime work depends on appropriate Prometheus gates.

## 4. Rationale and alternatives

### One Covenant instead of documentation sprawl

One companion is chosen because all material remains PA-C01 context, one source is easier to retrieve and maintain, and duplicate authority is avoided. Separate decision, context-map, founding-history, transcript, and per-Campaign files are deferred until a proven independent lifecycle or maintenance need exists.

### PostgreSQL full-text and pgvector before Qdrant

The relational-first direction keeps operational state, retrieval, backup, and recovery close with fewer moving parts. Qdrant remains a valid later specialization after measured retrieval or scale need; it is deferred, not rejected forever.

### Emberdark VM rather than LXC

The VM direction provides a clearer recovery unit, stronger application isolation, and a cleaner Coppermind/Emberdark operational boundary. The substrate belongs primarily to Prometheus's Fire; this Covenant records only the dependency and rationale, not deployment.

### Matrix/Element removed from the Prometheus baseline

Apollo/VS Code and the future private website meet the immediate interaction need with less operational complexity. Matrix may return only through a separately justified need and source transaction.

### GitHub remains canonical before Gitea proof

GitHub source and workflows are proven today, while Gitea parity, backup, recovery, mirror, mobile access, and rollback are not. Keeping GitHub canonical preserves reversibility and avoids a premature source-truth migration.

### Legacy routes remain active

Replacement capability and recovery are not yet proven. Existing routes remain available until parity, rollback, and explicit Preview → Execute retirement approval are complete.

### Dawnshard remains a projection

Durable doctrine and live operational state need a clear separation; projections can stale and must fail closed. Making Dawnshard authoritative would create competing truth and weaken recovery.

### Direct SQL access for AI and browsers is rejected

Unrestricted direct SQL bypasses validation, expands authority, weakens auditability, and complicates rollback. Emberdark remains the future governed transit and application boundary around Coppermind writes.

### Frictionless hybrid surfaces

The hybrid surface model keeps one conversational lead and avoids duplicate planning. Athena leads in ChatGPT because that paid hosted intelligence already performs intent and primary reasoning. Harmony leads in VS Code and other approved surfaces where Athena is absent. RAG, OCR/intake, context assembly, capability awareness, and routine delegation should happen automatically. Existing approval gates remain only where the underlying action already requires them; this role definition creates no new gate, service, dashboard, scheduler, notification platform, or manual model picker.

## 5. Internal unresolved-decision register

All entries below remain open by design. No entry is silently resolved by this harvest.

### PA-C01-DEC-001 — PostgreSQL schema boundaries

**Campaign:** PA-C02 · **Status:** OPEN — UNRESOLVED · **Direction:** Separate durable doctrine references from operational objects, events, audit, and protected-data pointers.  
**Alternatives:** One broad schema; domain schemas; event-only storage. **Reasoning:** Domain separation improves authority and recovery boundaries. **Why unresolved:** Object ownership and retention are not proven.  
**Evidence needed:** Schema proposal, migration/recovery rehearsal, access matrix. **Downstream:** PA-C02/03/08. **Gate/owner:** PA-C02 design gate / Codex-Coppermind with Artemis-Harmony. **Last verified:** 2026-07-17. **Pointers:** Covenant §§2.1, 6.

### PA-C01-DEC-002 — Event sourcing versus conventional audit/event tables

**Campaign:** PA-C02 · **Status:** OPEN — UNRESOLVED · **Direction:** Preserve an append-only, auditable transition record without choosing the implementation prematurely.  
**Alternatives:** Full event sourcing; conventional state plus audit tables; hybrid. **Reasoning:** A hybrid may balance replay and operational simplicity. **Why unresolved:** Replay, correction, and retention costs need proof.  
**Evidence needed:** Failure/replay/restore exercise and write-contract comparison. **Downstream:** PA-C02/03/04/10. **Gate/owner:** PA-C02 event contract / Codex-Coppermind with Artemis-Harmony. **Last verified:** 2026-07-17. **Pointers:** Covenant §§2.1, 2.2.

### PA-C01-DEC-003 — Identity and object model

**Campaign:** PA-C02 · **Status:** OPEN — UNRESOLVED · **Direction:** Bind source identity, live objects, Quest identity, and receipts without duplicate authority.  
**Alternatives:** Quest-centric; object-centric; event-sourced identity registry. **Reasoning:** Identity must survive restart, mirror, and rollback. **Why unresolved:** Live-state relationship to the Quest Board is not yet contracted.  
**Evidence needed:** Identity invariants, collision tests, clean-clone and restore proof. **Downstream:** PA-C02/04/06/08. **Gate/owner:** PA-C02 identity gate / Codex-Artemis. **Last verified:** 2026-07-17. **Pointers:** Quest source; `continuity/quest-engine-continuity-contract.md`.

### PA-C01-DEC-004 — Retention and archival

**Campaign:** PA-C02 · **Status:** OPEN — UNRESOLVED · **Direction:** Retain enough live history for audit, rollback, and restart while keeping protected data outside Prime.  
**Alternatives:** Time-based retention; event-class retention; immutable archive plus compact live state. **Reasoning:** Retention must follow evidence and recovery need, not convenience. **Why unresolved:** Data classes and volume are unknown.  
**Evidence needed:** Classification matrix, cost model, restore test. **Downstream:** PA-C02/04/10. **Gate/owner:** PA-C02 retention decision / Coppermind-Elantris-Harmony. **Last verified:** 2026-07-17. **Pointers:** Covenant §§2.1, 8.

### PA-C01-DEC-005 — WAL, PITR, backup, and restore design

**Campaign:** PA-C02 · **Status:** OPEN — UNRESOLVED · **Direction:** Preserve recoverable operational state with independent backup and point-in-time recovery.  
**Alternatives:** Base backups plus WAL; managed backup; snapshot-only. **Reasoning:** Base plus WAL supports bounded PITR and explicit restore proof. **Why unresolved:** Placement, cadence, and protected-storage route await Prometheus gates.  
**Evidence needed:** Backup/restore/PITR rehearsal, integrity hashes, rollback receipt. **Downstream:** PA-C02/06/10. **Gate/owner:** Elantris recovery gate / Elantris-Odyssey. **Last verified:** 2026-07-17. **Pointers:** `quests/prometheus-fire.md`; `recovery/elantris-recovery.md`.

### PA-C01-DEC-006 — Export format and protected-data classification

**Campaign:** PA-C02 · **Status:** OPEN — UNRESOLVED · **Direction:** Export only clean schemas, pointers, and sanitized summaries.  
**Alternatives:** Full database export; class-filtered export; pointer-only export. **Reasoning:** Pointer-only or classified export reduces leakage and keeps doctrine clean. **Why unresolved:** Protected-data categories and consumer contracts need review.  
**Evidence needed:** Classification table, redaction tests, export/import exercise. **Downstream:** PA-C02/04/05/07. **Gate/owner:** PA-C02 protected-boundary gate / Codex. **Last verified:** 2026-07-17. **Pointers:** Covenant §8; `governance/protected-source-boundary.md`.

### PA-C01-DEC-007 — pgvector indexing strategy

**Campaign:** PA-C02 · **Status:** OPEN — UNRESOLVED · **Direction:** Start with PostgreSQL full-text search plus pgvector.  
**Alternatives:** Full-text only; pgvector hybrid; external vector store first. **Reasoning:** Hybrid retrieval remains close to state and backup. **Why unresolved:** Corpus size, embedding model, index type, and quality thresholds are unmeasured.  
**Evidence needed:** Retrieval benchmark, resource profile, stale/rebuild behavior. **Downstream:** PA-C02/07/08. **Gate/owner:** PA-C02 retrieval gate / Artemis. **Last verified:** 2026-07-17. **Pointers:** Covenant §2.1.

### PA-C01-DEC-008 — Qdrant trigger criteria

**Campaign:** PA-C07 · **Status:** DEFERRED — UNRESOLVED · **Direction:** Do not add Qdrant until demonstrated need.  
**Alternatives:** Adopt now; PostgreSQL only; threshold-triggered specialization. **Reasoning:** Deferral reduces moving parts and recovery surface. **Why unresolved:** No measured need exists.  
**Evidence needed:** Retrieval quality/latency/resource threshold and rollback plan. **Downstream:** PA-C02/07/10. **Gate/owner:** PA-C07 evidence gate / Artemis. **Last verified:** 2026-07-17. **Pointers:** Covenant §2.1.

### PA-C01-DEC-009 — Emberdark API and versioning

**Campaign:** PA-C03 · **Status:** OPEN — UNRESOLVED · **Direction:** Govern every durable write through validated, versioned application contracts.  
**Alternatives:** REST; typed command API; workflow-native interface; hybrid. **Reasoning:** Explicit contracts support authorization, receipts, and rollback. **Why unresolved:** Domain objects and error model are not final.  
**Evidence needed:** API proposal, schema validation, compatibility and failure tests. **Downstream:** PA-C03/05/08. **Gate/owner:** PA-C03 contract gate / Artemis-Harmony. **Last verified:** 2026-07-17. **Pointers:** Covenant §2.3.

### PA-C01-DEC-010 — Emberdark authorization model

**Campaign:** PA-C03 · **Status:** OPEN — UNRESOLVED · **Direction:** Separate read, propose, approve, write, and export capabilities.  
**Alternatives:** Role-based; capability-based; human approval per command; hybrid. **Reasoning:** Capability separation limits silent action and SQL reach. **Why unresolved:** Actor and private-site boundaries are not proven.  
**Evidence needed:** Threat model, authorization matrix, denial and replay tests. **Downstream:** PA-C03/05/07/08. **Gate/owner:** PA-C03 authority gate / Artemis-Codex. **Last verified:** 2026-07-17. **Pointers:** `governance/atlas-aegis.md`; Covenant §7.

### PA-C01-DEC-011 — Write idempotency and reconciliation

**Campaign:** PA-C03 · **Status:** OPEN — UNRESOLVED · **Direction:** Make retries, duplicate commands, stale inputs, and reconciliation explicit and fail closed.  
**Alternatives:** Client keys; server receipts; event sequence; hybrid. **Reasoning:** Durable source must not fork under retries or partial failure. **Why unresolved:** Event and object contracts remain open.  
**Evidence needed:** Replay, interruption, stale-base, rollback, and restore tests. **Downstream:** PA-C03/04/06/10. **Gate/owner:** PA-C03 reliability gate / Harmony-Phoenix-Elantris. **Last verified:** 2026-07-17. **Pointers:** Covenant §§2.1, 7.

### PA-C01-DEC-012 — n8n integration boundary

**Campaign:** PA-C03 · **Status:** OPEN — UNRESOLVED · **Direction:** n8n acts through Emberdark and cannot inherit broad database or source authority.
**Alternatives:** n8n as writer; n8n as orchestrator; no n8n. **Reasoning:** Mediated orchestration preserves governance and replacement options. **Why unresolved:** Workflow inventory and latency needs are unknown.  
**Evidence needed:** Typed integration contract, denied-direct-write tests, failure/retry proof. **Downstream:** PA-C03/05/08. **Gate/owner:** PA-C03 integration gate / Harmony-Emberdark. **Last verified:** 2026-07-17. **Pointers:** Covenant §2.3.

### PA-C01-DEC-013 — Audit-receipt model

**Campaign:** PA-C03 · **Status:** OPEN — UNRESOLVED · **Direction:** Every governed write and reconciliation emits a sanitized receipt.  
**Alternatives:** Event-only; receipt-only; event plus receipt. **Reasoning:** Receipts provide operator-facing proof while events preserve state history. **Why unresolved:** Fields, retention, and protected pointers need design.  
**Evidence needed:** Receipt schema, integrity binding, redaction and restart tests. **Downstream:** PA-C03/04/05/10. **Gate/owner:** PA-C03 receipt gate / Codex-Harmony. **Last verified:** 2026-07-17. **Pointers:** Covenant §§2.3, 8.

### PA-C01-DEC-014 — Dawnshard watermark and cadence

**Campaign:** PA-C04 · **Status:** OPEN — UNRESOLVED · **Direction:** Generate from a monotonic event sequence or watermark and fail closed on drift.  
**Alternatives:** Time window; sequence watermark; event cursor plus snapshot. **Reasoning:** Time windows lose events and cannot prove freshness. **Why unresolved:** Event model and generation owner are not settled.  
**Evidence needed:** Gap, restart, stale, last-known-good, and concurrent-generation tests. **Downstream:** PA-C04/08/10. **Gate/owner:** PA-C04 projection gate / Coppermind-Codex-Harmony. **Last verified:** 2026-07-17. **Pointers:** Covenant §2.2.

### PA-C01-DEC-015 — Dawnshard storage and portable twin

**Campaign:** PA-C04 · **Status:** OPEN — UNRESOLVED · **Direction:** Keep a bounded generated view and portable approved backup without repeated large Git commits.  
**Alternatives:** Git history; private storage; object store; approved ZIP twin. **Reasoning:** Source and projection history have different durability and size needs. **Why unresolved:** Backup target and retention are not approved.  
**Evidence needed:** Portable manifest, checksum, restore, stale, and storage-cost proof. **Downstream:** PA-C04/06/10. **Gate/owner:** PA-C04 backup gate / Elantris-Codex. **Last verified:** 2026-07-17. **Pointers:** Covenant §2.2.

### PA-C01-DEC-016 — Dawnshard stale presentation and manifest

**Campaign:** PA-C04 · **Status:** OPEN — UNRESOLVED · **Direction:** Show source watermark, freshness, stale state, last-known-good, and integrity manifest.  
**Alternatives:** Silent refresh; visible stale marker; hard failure with preserved output. **Reasoning:** Operators must not mistake stale context for live truth. **Why unresolved:** Consumer UX and event contract are open.  
**Evidence needed:** Tamper, stale, restart, and consumer fail-closed tests. **Downstream:** PA-C04/05/08. **Gate/owner:** PA-C04 integrity gate / Codex-Coppermind-Harmony. **Last verified:** 2026-07-17. **Pointers:** Covenant §2.2.

### PA-C01-DEC-017 — Quest Board and live-state relationship

**Campaign:** PA-C04 · **Status:** OPEN — UNRESOLVED · **Direction:** Quest Board remains canonical Quest registry; live memory may supplement but never silently advance it.  
**Alternatives:** Board authoritative; live state authoritative; explicit reconciled projection. **Reasoning:** Existing Prime contract forbids generated or live state from self-promoting a Quest. **Why unresolved:** Future read/write interfaces are not defined.  
**Evidence needed:** Admission, stale, conflict, and readback proof. **Downstream:** PA-C04/08/10. **Gate/owner:** PA-C04/08 boundary gate / Codex-Coppermind-Harmony. **Last verified:** 2026-07-17. **Pointers:** `governance/quest-engine-continuity-contract.md`.

### PA-C01-DEC-018 — Private website framework, authentication, and access

**Campaign:** PA-C05 · **Status:** OPEN — UNRESOLVED · **Direction:** Private, authenticated, approval-aware local/mobile control surface with no public endpoint.  
**Alternatives:** Framework A/B; Tailscale identity; VPN plus application auth; passkey/session hybrid. **Reasoning:** Private reachability and explicit approvals reduce exposure. **Why unresolved:** Framework, identity provider, session model, and threat model need Jayson review.  
**Evidence needed:** Threat model, auth denial, session, audit, health, and bounded-action tests. **Downstream:** PA-C05/08/10. **Gate/owner:** PA-C05 private-gate decision / Artemis-Codex. **Last verified:** 2026-07-17. **Pointers:** Covenant §2.4.

### PA-C01-DEC-019 — Website approval UX and audit logging

**Campaign:** PA-C05 · **Status:** OPEN — UNRESOLVED · **Direction:** Preview → approval → bounded Execute with receipt and rollback visibility.  
**Alternatives:** Per-command approval; campaign approval; staged approval with expiry. **Reasoning:** Exact scope and expiry prevent standing authority. **Why unresolved:** Command taxonomy and Emberdark contracts are open.
**Evidence needed:** User journey, replay/expiry, denial, receipt, and rollback proof. **Downstream:** PA-C05/09/10. **Gate/owner:** PA-C05 approval gate / Jayson-Artemis. **Last verified:** 2026-07-17. **Pointers:** `governance/change-routes.md`; Covenant §7.

### PA-C01-DEC-020 — Gitea host and database placement

**Campaign:** PA-C06 · **Status:** OPEN — UNRESOLVED · **Direction:** Shadow placement must preserve independent backup, recovery, and source identity.  
**Alternatives:** Forge; Prometheus; separate host; future dedicated substrate. **Reasoning:** Placement affects failure domains and cutover rollback. **Why unresolved:** Prometheus/Forge capacity and recovery gates are not complete.  
**Evidence needed:** Capacity, network, backup, restore, parity, and rollback proof. **Downstream:** PA-C06/08/10. **Gate/owner:** PA-C06 placement gate / Odyssey-Phoenix-Elantris-Harmony. **Last verified:** 2026-07-17. **Pointers:** Covenant §2.5; `quests/prometheus-fire.md`.

### PA-C01-DEC-021 — Gitea mirror, parity, cutover, and rollback

**Campaign:** PA-C06 · **Status:** OPEN — UNRESOLVED · **Direction:** Begin shadow; prove one-way or bidirectional mechanics, exact refs, workflow replacement, mobile/Athena access, and reversible cutover before authority changes.  
**Alternatives:** GitHub primary with Gitea shadow; Gitea primary with GitHub mirror; dual-write. **Reasoning:** Shadow-first preserves current proven authority. **Why unresolved:** Operational parity and rollback are unproven.  
**Evidence needed:** Exact ref parity, PR/workflow parity, backup/restore, mirror interruption, and rollback receipt. **Downstream:** PA-C06/09/10. **Gate/owner:** PA-C06 cutover gate / Jayson-Codex. **Last verified:** 2026-07-17. **Pointers:** Covenant §2.5; `governance/cutover-boundary.md`.

### PA-C01-DEC-022 — Harmony capability selection and resource allocation

**Campaign:** PA-C07 · **Status:** OPEN — UNRESOLVED · **Direction:** Harmony routes permitted local or external models, Kandra, and tools through bounded retrieval and typed interfaces without source or merge authority.  
**Alternatives:** One local model; routed specialists; external-first; hybrid. **Reasoning:** Resource cost, quality, privacy, availability, and recovery must be measured while preserving the resident Harmony identity. **Why unresolved:** Corpus, hardware, workload, evaluation set, and future model identity are not proven.  
**Evidence needed:** Quality, resource, privacy, failure, fallback, surface-routing, and authority-boundary tests. **Downstream:** PA-C07/08/10. **Gate/owner:** PA-C07 model gate / Artemis-Harmony. **Last verified:** 2026-07-20. **Pointers:** Covenant §§2.3, 2.6; `quests/found-silverlight.md`.

### PA-C01-DEC-023 — Controlled Burn, Phoenix Burn, Feather, and Golden Wing

**Campaign:** PA-C09 · **Status:** OPEN — UNRESOLVED · **Direction:** Preserve lifecycle concepts as future architecture context only; current lifecycle doctrine remains unchanged and inactive for this harvest.  
**Alternatives:** Activate now; defer all; map concepts to current routes without activation. **Reasoning:** Mapping supports restart while avoiding premature doctrine replacement. **Why unresolved:** Contracts, schemas, and proof are not ready.  
**Evidence needed:** Future schema, state-transition, rollback, evidence, and independent lifecycle proof. **Downstream:** PA-C04/09/10. **Gate/owner:** PA-C09 refraction gate / Codex. **Last verified:** 2026-07-17. **Pointers:** `governance/source-lifecycle.md`; `lifecycle/`.

### PA-C01-DEC-024 — Legacy-route parity and retirement criteria

**Campaign:** PA-C09 · **Status:** OPEN — UNRESOLVED · **Direction:** Keep Spear, Arrow/Bow, Sword/Oathbringer, Phoenix Blade, Aegis Break, Thread Engine, Codex, and GitHub routes until parity, recovery, rollback, and explicit retirement approval.  
**Alternatives:** Immediate simplification; gradual deprecation; parallel routes with evidence. **Reasoning:** Existing routes are proven or historically required; removing them early reduces resilience. **Why unresolved:** New workflows and recovery evidence do not exist.  
**Evidence needed:** Old/new capability matrix, rollback, operator access, and Jayson Preview → Execute approval. **Downstream:** PA-C06/08/09/10. **Gate/owner:** PA-C09 retirement gate / Codex-Jayson. **Last verified:** 2026-07-17. **Pointers:** `governance/change-routes.md`; Covenant §7.

### PA-C01-DEC-025 — Gemstone, Spiralstone, and BEU relationship

**Campaign:** PA-C01 / PA-C09 · **Status:** OPEN — UNRESOLVED · **Direction:** Gemstones may become user-facing mission objects; Spiralstone/BEU concepts may evolve without becoming authority or protected raw evidence.  
**Alternatives:** Keep separate; unify metadata; event-linked objects. **Reasoning:** Clear identity and provenance support restart and accounting without duplicate source. **Why unresolved:** Object contracts and private evidence boundaries are not final.  
**Evidence needed:** Schema, provenance, privacy, replay, and workflow integration proof. **Downstream:** PA-C01/03/04/09. **Gate/owner:** PA-C01 covenant gate / Codex-Artemis. **Last verified:** 2026-07-17. **Pointers:** `governance/investiture-accounting-contract.md`; `operations/protocol-library.md`.

## 6. Campaign ownership map

| Campaign | Context owned | Required evidence before advancement |
|---|---|---|
| PA-C01 | Constitution, authority, source/memory model, protected boundary, decisions, rationale | Accepted Covenant with explicit boundaries and no runtime authority. |
| PA-C02 | PostgreSQL, schemas, events, retrieval, retention, WAL/PITR, backup/restore | Schema, migration, retrieval, export, backup, restore, and reconciliation proof. |
| PA-C03 | Harmony/Emberdark intake, API, validation, receipts, idempotency, integrations | Authorization, failure, replay, rollback, receipt, and mediated-integration proof. |
| PA-C04 | Coppermind-to-Athena Dawnshard projection, watermark, stale behavior, portable context | Watermark, fail-closed, last-known-good, integrity, restart, and backup proof. |
| PA-C05 | Glass Codex private website, authentication, approvals, access, health, bounded actions | Private-access threat model and denied/public-exposure, approval, audit, and recovery proof. |
| PA-C06 | Gitea shadow, parity, mirror, backup, rollback, cutover readiness | Exact identity/ref parity, recovery, mirror interruption, access, and Jayson gate. |
| PA-C07 | Harmony/Sazed, RAG, OCR/intake, context assembly, capability awareness, surface routing, local/external models, embeddings, reranking, and bounded workers | Quality, resource, privacy, fallback, frictionless-routing, and authority-boundary evidence. |
| PA-C08 | Cross-component integration and degraded modes | Boundary, failure, recovery, monitoring nonauthority, and integration proof. |
| PA-C09 | Old/new route parity, lifecycle refraction, retirement criteria | Comparison, rollback, recovery, operator access, and explicit retirement approval. |
| PA-C10 | Integrated acceptance and final Sunset | Backup/restore/restart/rollback, stale/private/model boundaries, cutover readiness, and final Strikeforce. |

## 7. Lifecycle and route direction (not activated)

These are future architecture labels, not active doctrine changes:

```text
Sunset = session save and closeout
Feather Harvest = extract durable candidates
Controlled Burn = bounded reversible reconciliation
Phoenix Burn = governed major transformation or replacement with rollback
Prime Refraction = constitutional or doctrinal change
Elantris Restore = disaster recovery
Golden Wing = reusable validated lesson candidate
```

A possible future state path is `candidate -> scoped -> harvested -> successor verified -> previewed -> approved -> executed -> verified -> mirrored -> closed`, with `blocked`, `rolled_back`, and `deferred` states. This harvest maps the concepts to PA-C01 and PA-C09 but does not activate or replace current lifecycle doctrine.

Current routes remain until parity and recovery are proven. Gemstones may become normal mission objects; Spiralstone/BEU concepts may evolve. Sword, Oathbringer, Phoenix Blade, Thread Engine, Spear, Arrow/Bow, Aegis Break, and Codex remain active unless separately retired. Capability never implies authority, and retirement requires explicit Preview → Execute.

## 8. Authority, safety, and operating definitions

### Shardblade

Shardblade is merge authority for one exact already-authored and reviewed candidate. After exact-head Strikeforce GREEN, Shardblade may mark that exact candidate ready and merge it using the accepted route, with fresh head/base/readback checks. Shardblade cannot author, repair, widen, substitute, bypass checks, force-push, change settings, access secrets, perform runtime or infrastructure work, authorize cutover, or turn into standing authority. Strikeforce GREEN is readiness; it is not merge authority.

### Goddess Mode

Goddess Mode is persistence through safe repair and alternate routes. It continues through obvious safe next steps, repairs candidate-caused failures, completes separable work, and tries safe alternate routes without widening scope. It does not override Aegis, authorize runtime or infrastructure work, authorize secrets or protected data, repeat a blocked connector indefinitely, or override a true decision gate. When a route is blocked, preserve partial results, stop retrying that route, continue safe separable work, and report the blocker if completion depends on it.

### Strikeforce

Strikeforce consists of Noctua, Ares, and Aegis working cumulatively against one exact candidate head.

```text
Noctua verifies
→ Ares red-teams
→ Aegis audits and improves Athena's interface with Jayson
→ GREEN, YELLOW, or RED
```

Aegis is Athena's shield. It cannot cure a Noctua or Ares failure through wording, confidence, or simplification. GREEN means the exact reviewed candidate is ready for the next authorized gate. It does not itself merge, activate, promote, cut over, or grant permanence authority.

### Protected-source boundary

Git may contain clean doctrine, protocols, schemas, pointers, and non-secret summaries. Private runtime facts, network maps, device registers, raw finance evidence, medical records, account data, and private exports remain in approved private sources. Passwords, tokens, keys, MFA/recovery codes, seed phrases, and real environment values never enter Git, Dawnshard, model context, or Coppermind exports.

## 9. Founding context and provenance

Prime Ascendant was created separately after Prometheus's Fire refraction. Prometheus's Fire was intentionally updated first as the host and recovery substrate; Prime Ascendant was then created as a refinement-first Quest for application semantics and future orchestration. This R02 harvest consolidates the full meaningful context into one Covenant to prevent documentation sprawl.

Independently verified historical founding lineage:

| Historical transaction | Historical verified source |
|---|---|
| Prometheus's Fire authored | PR #229, merge `07d45cd6c6486e968f25521f429b8273b128eaed` |
| Prometheus's Fire generated | PR #230, merge `e87dbf05252fd80829143474b83b7fa180d66fb7` |
| Prime Ascendant authored | PR #232, reviewed head `98a57845082e8f051b913e94e2b56da7d70a0d00`, merge `8f8f36b2c83b19deecff4979f940a8c450aa8444` |
| Prime Ascendant generated | PR #233, reviewed head `39e8080789041541617d61baec1c909b2cdfb190`, merge `7d21616e5e625bf4f3ce0b3d78e73187d82c331f` |
| Main immediately after the founding generated transaction | `7d21616e5e625bf4f3ce0b3d78e73187d82c331f` |

These values are historical GitHub facts, not claims about current `main` and
not local receipt paths. Operator-held private receipts may exist but are not
reproduced or stored here. The Covenant's architecture remains conceptual until
later Campaign evidence proves implementation.

Later validation history is also reconciled without changing that architecture:

| Validation transaction | Verified result |
|---|---|
| PR #236 — minimize hosted Actions while preserving validation | Merged as `a02e048209ec3e5f9f329c8772440bc4f728e652`; validation became fail-closed and path-targeted, and automatic generated publishing on every `main` push was removed. |
| PR #237 — targeted hosted-Actions continuity proof | Merged as `e95e13f8e7185bb50e773b2033d06f172d928f58`; proved the Ubuntu baseline/Prime validation route for a continuity transaction. It did not execute the full Atlas Sunset for this chat and created no lifecycle Feather. |

Generated projections remain stale until the separately governed generated
refresh. Runtime is not started. Gitea cutover, route retirement, repository
visibility changes, and repository-settings changes remain unauthorized.

## 10. Proven workflow lesson

The proven bounded transaction pattern is:

```text
Bounded Gemstone
→ exact-base lock
→ authored-source PR
→ exact-head Strikeforce
→ review-comment repair
→ Shardblade merge
→ merged-main readback
→ separate generated-refresh PR
→ exact-head Strikeforce
→ Shardblade merge
→ final-main verification
```

Authored and generated transactions remain separate. Copilot and other reviewer findings are advisory evidence; Codex owns implementation and must address actionable findings. Threads are resolved only after the issue is fixed or proven obsolete. Strikeforce GREEN establishes readiness; Shardblade authorizes merge. Goddess Mode persists through safe repair and alternate routes without scope expansion. Completion requires merged-main readback and restart-safe proof.

## 11. Restart and next gates

On restart, read the parent Quest, this Covenant, the current Quest Board and continuity register, then active Aegis, Shardblade, Strikeforce, change-route, Prime Reborn, Prometheus's Fire, Artemis, and generated-index sources. Re-lock current `main` before any mutation.

The next safe sequence is:

1. Review and accept PA-C01 boundaries without runtime authorization.
2. Define PA-C02 source contracts and evidence requirements; do not deploy until Prometheus substrate gates are proven.
3. Define PA-C03 Emberdark contracts and mediated authority; do not grant direct SQL access.
4. Define PA-C04 watermark, stale, fail-closed, and portable-output contracts.
5. Prepare PA-C05 private-access threat model before any website implementation.
6. Keep Gitea shadow and all route changes behind explicit parity, recovery, rollback, and Jayson cutover gates.
7. Use PA-C09 to compare old and new routes before proposing simplification or retirement.
8. Require PA-C10 integrated proof; service presence alone is never completion.

Future work must preserve unresolved decisions, update this single Covenant or the concise Quest as appropriate, use exact source transactions, and never require this chat transcript to recover the architecture.
