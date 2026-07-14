---
title: "Quest — Found Silverlight"
status: Active
owner: "Project Codex / Operation Source Governance"
supporting_projects:
  - "Project Artemis"
  - "Project Odyssey"
  - "Project Phoenix"
source_type: Quest
canonical_scope: "Parent Quest for establishing Atlas's private cognitive interface through Investiture Accounting, the seven-pillar Glass Codex, and the Seon Apple Reminders integration."
protected_level: High
routes_from:
  - atlas-prime.md
  - routing/command-surfaces.md
  - operations/protocol-library.md
  - operations/artemis-runtime-and-routing.md
  - infrastructure/atlas-infrastructure-source.md
  - knowledge/context-pack-contract.md
  - safety/atlas-safety-doctrine.md
routes_to:
  - quest-board/quest-board-v1.json
  - governance/change-routes.md
  - governance/atlas-aegis.md
  - governance/atlas-strikeforce.md
  - recovery/phoenix-recovery.md
private_boundary: "Store only clean doctrine, schemas, sanitized status, non-secret architecture, safe evidence pointers, and completion claims. Do not store raw conversations, reminder contents, personal task history, IP addresses, device registers, private network maps, credentials, tokens, MFA or recovery codes, real environment values, PHI, raw finance evidence, account data, or private runtime values."
evidence_boundary: "This Quest coordinates canonical source and sanitized proof. Only trusted provider/runtime-reported model tokens may emit BEU; partial or unavailable telemetry remains explicit and deterministic non-model work is zero BEU. Raw usage, conversations, account data, private locations, credentials, and protected evidence remain outside Prime. Apple Reminders remains authoritative for Seon. Planning or package readiness does not prove deployment."
cleanup_path: "Keep active until all three Campaigns and Quest-level gates pass. Close through final Noctua, Ares, Athena reconciliation, whole-Quest Strikeforce, Quest Board and generated refresh, Phoenix recovery proof, and restart-safe Sunset."
last_verified: 2026-07-14
---

# Quest — Found Silverlight

## 1. Quest identity

**Quest ID:** `QUEST-FOUND-SILVERLIGHT-R01`  
**Parent Project:** Project Codex  
**Owning Operation:** Operation Source Governance  
**Supporting Projects:** Artemis, Odyssey, Phoenix  
**Current lane:** `EXECUTE -> VERIFY`
**Current route:** `Canonical Investiture identity -> Found Silverlight accounting doctrine -> append-only ledger construction`
**Current state:** `IN_PROGRESS`

## 2. Purpose

Found Silverlight establishes Atlas's private cognitive interface by:

1. accounting for trusted model-token Investiture through Found Silverlight's Investiture Accounting system;
2. rendering canonical Atlas knowledge through Glass Codex;
3. carrying personal commitments through Seon while Apple Reminders remains authoritative.

## 3. Naming contract

```text
Found Silverlight = unified Quest
Investiture Accounting = active BEU accounting system and Glass Codex Pillar VII
Spirallight = trusted reported OpenAI model tokens
Chromelight = trusted reported Google model tokens
Emberlight = trusted reported Atlas-controlled local-model tokens
Stormlight = retired historical accounting name; never emitted by new writers
Glass Codex = private Atlas website
Seon = Apple Reminders integration
Spanreed = printer
```

## 4. Work hierarchy

```text
Quest
├── Campaign
│   ├── Mission
│   │   ├── entry gate
│   │   ├── bounded execution
│   │   └── exit gate
│   └── Campaign completion gate
└── Quest completion gates
```

Gates govern entry, exit, promotion, Campaign completion, and Quest completion. A Gate is a checkpoint, not a mandatory fourth nested object beneath every Mission.

## 5. Authority and runtime boundaries

- Prime remains the sole canonical clean-source repository.
- Glass Codex is a generated read-only projection of canonical source.
- Investiture Accounting reports measurement state, evidence basis, category semantics, age, and staleness.
- Seon is a Live Integration, not Pillar VIII.
- Apple Reminders remains authoritative for reminder state.
- Completing a reminder does not complete or advance an Atlas Quest, Campaign, Mission, Gate, PR, purchase, account action, or infrastructure action.
- Live Investiture Accounting and Seon data remain outside Prime, Git history, static search, and immutable Glass Codex releases.
- No public endpoint, Funnel, standing writer, automatic merge, or direct-main write is authorized.
- Runtime deployment requires separate Preview, Jayson approval, evidence, recovery, and rollback.

# Campaigns

## Campaign FS-C01 — Infuse the Gemstone

**Owner:** Codex / Source Governance  
**Support:** Artemis / AI Governance; Phoenix  
**Status:** `IN_PROGRESS`
**Depends on:** Found Silverlight source admission

Build and prove Investiture Accounting independently before Glass Codex
depends on it. The Found Silverlight-owned accounting contract is
`governance/investiture-accounting-contract.md`; Prime-wide Light identity is
`governance/investiture-source-identity-contract.md`.

### Mission FS-C01-M01 — Define Investiture

Establish:

- the exact one trusted reported model token equals one BEU convention;
- `Spirallight`, `Chromelight`, and `Emberlight` accounting Light identities
  derived only from trusted provider/runtime evidence;
- independent provider, model, runtime-control, work-surface, route, engine,
  credential, Light, and permanence identities;
- `MEASURED`, `PARTIAL`, `UNAVAILABLE`, and `ZERO_MODEL` states;
- authoritative-total versus disjoint-leaf counting and exact non-overlap;
- Stormlight retirement without rewriting historical evidence;
- Found Silverlight ownership of events, ledgers, summaries, and receipts.

**State:** `PROVEN` from the accepted Prime identity contract, this
Found Silverlight-owned accounting contract, exact source tests, and canonical
readback.

**Exit gate:** `INVESTITURE_ACCOUNTING_DOCTRINE_ACCEPTED`.

### Mission FS-C01-M02 — Forge the Ledger

Build:

- append-only event, record, and ledger-manifest schemas;
- deterministic validator;
- duplicate, replay, stale-head, and category-overlap rejection;
- private storage contract;
- sanitized summary generator;
- malformed-event quarantine;
- immutable-generation recovery and rollback.

**State:** `PROVEN` from authored construction PR `#171`, exact-head Ubuntu
and Windows validation, detached review, canonical synthetic exercise, and
accepted record
`proof/found-silverlight/fs-c01-m02-m03-construction-acceptance-r01.json`.

**Exit gate:** `APPEND_ONLY_INVESTITURE_LEDGER_CONSTRUCTION_PROVEN`.

### Mission FS-C01-M03 — Bind the Receipts

Define events for:

- exact `USAGE_REPORTED` entries that alone may contribute BEU;
- Athena checkpoints;
- Gemstones and Arrows;
- Spear result readback;
- Phoenix Flare and Sunset;
- Codex task start, pause, cooldown, resume, completion, and receipt;
- deterministic zero-model work.

Lifecycle events bind usage receipts without recounting usage.

**State:** `PROVEN` from the same exact construction lineage and canonical
synthetic lifecycle-binding exercise. Only `USAGE_REPORTED` entries changed
BEU; the lifecycle event bound prior usage without recounting it.

**Exit gate:** `INVESTITURE_RECEIPT_AND_LIFECYCLE_BINDING_PROVEN`.

### Mission FS-C01-M04 — Prove the Light

Record real events and prove:

- summary accuracy;
- honest unavailable and partial telemetry;
- zero-model deterministic evidence;
- restoration from private ledger data;
- safe loss of telemetry without loss of canonical source;
- one bounded real model task backed by trusted provider/runtime usage and
  category-semantics evidence in a Jayson-selected protected external store.

**Exit gate:** `INVESTITURE_ACCOUNTING_LIVE_ACCEPTANCE_PROVEN`.

**Campaign completion gate:** `INVESTITURE_ACCOUNTING_INDEPENDENTLY_PROVEN`.

## Campaign FS-C02 — Raise the Glass Codex

**Owner:** Codex / Source Governance  
**Support:** Odyssey / Forge Storage; Phoenix; Artemis  
**Status:** `BLOCKED_BY_FS-C01`  
**Depends on:** FS-C01

Build the private Atlas website and consume the proven sanitized Investiture
Accounting summary as Pillar VII.

### Mission FS-C02-M01 — Define the Reflection

Define authority, stable IDs, visibility classes, schemas, provenance, release contracts, and lifecycle feature gates.

### Mission FS-C02-M02 — Shape the Glass

Approve the responsive visual system and exact navigation:

1. Atlas Home;
2. Quest Board;
3. Quest Dossiers & Emberlines;
4. Atlas Registry;
5. Phoenix Memory;
6. Decisions, Proof & History;
7. Investiture Accounting.

### Mission FS-C02-M03 — Compile the Codex

Build deterministic normalization, schema validation, static generation, local search, provenance, and immutable releases.

### Mission FS-C02-M04 — Seal the Glass

Prove privacy filtering, local assets, Content Security Policy, accessibility, failed-build quarantine, atomic publication, rollback, and clean rebuild.

### Mission FS-C02-M05 — Raise It on Forge

Deploy one manual Tailnet-only release after applicable Phoenix restore proof.

### Mission FS-C02-M06 — Awaken the Living View

Add changed-commit checks, isolated builds, locking, atomic publication, release notification, and stale states.

### Mission FS-C02-M07 — Bind Investiture Accounting to Pillar VII

Display the sanitized Investiture Accounting summary without giving the browser
or website ledger-write authority.

**Campaign completion gate:** `GLASS_CODEX_SEVEN_PILLARS_OPERATIONAL`.

## Campaign FS-C03 — Awaken Seon

**Owner:** Artemis / Nexus  
**Support:** Codex; Odyssey; Phoenix  
**Status:** `BLOCKED_BY_FS-C02_AND_HERMES_EVIDENCE`  
**Depends on:** FS-C02 and Hermes suitability proof

Add Apple Reminders as a separately bounded live integration.

### Mission FS-C03-M01 — Prove Hermes

Verify Hermes, the MacBook Pro portable Atlas command endpoint and proposed macOS bridge vessel, for supported macOS, boot/login reliability, battery, storage, networking, power, thermals, clamshell behavior, FileVault posture, restart behavior, and recovery. The former planned Apollo bridge name is superseded in active source; historical evidence remains unchanged.

### Mission FS-C03-M02 — Hear the Seon

Use native Swift and EventKit with an invented `Seon Test` list. Begin read-only. Prove permission, revocation, refetch-after-change, reboot, privacy, and no-PHI boundaries.

### Mission FS-C03-M03 — Project Seon

Project minimized reminder state from Hermes to a private Forge gateway and Glass Codex Live Integration with current, stale, offline, revoked, and read-only states.

### Mission FS-C03-M04 — Answer Complete

Complete one non-recurring test reminder with prior-state binding, request identity, idempotency, conflict detection, EventKit write, and Apple readback.

### Mission FS-C03-M05 — Answer Reopen

Reopen one-time reminders. Recurring reminders remain excluded until separately characterized.

### Mission FS-C03-M06 — Create, Update, and Reschedule

Add one action class at a time: create, rename, due date, priority, list move, and later recurrence. Broad requests produce a proposed Seon diff before execution.

### Mission FS-C03-M07 — Athena and Seon

Enable private conversational tools only when the then-current ChatGPT plan, client, and supported private connector route are verified. Read-only precedes writes.

### Mission FS-C03-M08 — Recover and Silence the Seon

Prove restart, permission recovery, reinstall, credential revocation, disablement, Apple independence, and Glass Codex survival when Seon is unavailable.

**Campaign completion gate:** `SEON_BOUNDED_AND_APPLE_CONFIRMED`.

## 6. Stormlight historical migration boundary

`Stormlight` is retired as the active accounting-system name. New doctrine,
schemas, events, writers, ledgers, summaries, and Glass Codex navigation use
Investiture Accounting and the exact Lights `Spirallight`, `Chromelight`, and
`Emberlight`.

Historical Stormlight evidence remains immutable. In particular, accepted
RP-C03 and RP-C04 v1 schemas and proofs keep their literal `stormlight` fields
and legacy source classifications. Those values are not token counts, are not
current Lights, and are never automatically converted or backfilled.

## 7. Explicit exclusions

Found Silverlight admission does not itself authorize:

- Forge deployment;
- Hermes installation or repurposing;
- Apple Reminders access;
- reminder reads or writes;
- public exposure;
- ChatGPT custom-app activation;
- subscription purchase or plan upgrade;
- infrastructure, networking, account, backup, or restore action;
- direct Prime mutation outside a reviewed branch and draft PR;
- generated-source mixing;
- automatic ready transition or merge.

## 8. Quest completion gates

Found Silverlight is complete only when:

1. Investiture Accounting is independently proven.
2. Glass Codex displays Pillars I–VII privately and deterministically.
3. Seon operates within its approved data and action boundary.
4. Prime remains sole canonical clean source.
5. Live data remains outside Prime, Git history, static search, and immutable releases.
6. Phoenix backup, restore, rollback, and disablement are proven.
7. No public endpoint is required.
8. Seon writes are idempotent, conflict-aware, and Apple-confirmed.
9. Reminder completion never changes Atlas source or operational state.
10. Final Noctua, Ares, Athena reconciliation, and whole-Quest Strikeforce are GREEN.
11. Quest Board and generated projections are current.
12. Restart-safe Sunset is complete.

## 9. Current gate

```text
Quest state: IN_PROGRESS
Current Campaign: FS-C01 — Infuse the Gemstone
Accepted Mission: FS-C01-M03 — Bind the Receipts
Next Mission: FS-C01-M04 — Prove the Light
Source-governance substrate: FOUNDRY_OATHBRINGER_R04_ACCEPTED
Construction merge: f88dd11875b7891212a05dd7b66f3e11f128526f
Canonical exercise main: df3de8e555c19cab890f3968dca67f770498b153
Runtime deployment: NOT STARTED
External-system action: NOT AUTHORIZED
```

FS-C01-M02 and FS-C01-M03 are accepted at their construction gates.
FS-C01-M04 live acceptance remains separately gated by a Jayson-selected
protected external store and one bounded trusted provider/runtime usage receipt
with authoritative category-semantics evidence.
