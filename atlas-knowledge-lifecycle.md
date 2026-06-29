---
title: Atlas Knowledge Lifecycle
atlas_id: atlas-prime.knowledge-lifecycle
format_version: '1.0'
status: PROPOSED
source_type: CORE_DOCTRINE
authority_class: CANONICAL_AUTHORED_SOURCE
owner_project: Codex
owner_operation: Source Governance
canonical_scope: Controlling lifecycle relationships, semantic authority, provenance states,
  absorption rules, and transitional safeguards for Sunset, Solar Eclipse, Feathers,
  Quests, Emberline, Phoenix Flare, Controlled Burn, Golden Wing, Phoenix Burn,
  Reforge, Spear, Noctua, and Phoenix Reborn.
protected_level: CRITICAL
routes_from:
- README.md
- atlas-prime.md
- atlas-aegis.md
routes_to: []
private_boundary: Do not store secrets, credentials, tokens, MFA or recovery codes,
  private keys, seed phrases, real .env values, PHI, raw finance or account evidence,
  private runtime values, IP addresses, network maps, device registers, protected
  exports, or other raw protected evidence in GitHub.
evidence_boundary: Original evidence systems remain authoritative outside GitHub.
  Atlas Prime stores only clean source, clean summaries, structured clean state, generated
  projections, migration provenance, and clean pointers.
supersedes: []
cleanup_path: Keep as the single controlling lifecycle map. Specialized files may
  add detail but must not redefine actor authority, Phoenix meanings, or the order
  of promotion and recovery.
last_verified: '2026-06-29'
---

# Atlas Knowledge Lifecycle

## Controlling rule

This file is the controlling lifecycle map for Atlas Prime. Specialized doctrine, schemas, policies, and tools MAY add detail, but MUST NOT redefine the sequence, actor boundaries, or reserved Phoenix meanings.

## Lifecycle

Atlas lifecycle protocols are related but do not form one mandatory linear pipeline.

```text
Session or milestone
├─ Phoenix Flare -> exactly one recommendation:
│  ├─ Controlled Burn
│  ├─ Phoenix Burn
│  └─ Sunset
├─ Emberline -> independent Quest/Campaign roadmap and status
├─ Reforge -> independent doctrine-reconciliation Preview
└─ Phoenix Reborn -> independent recovery and integrity proof

SUNSET
-> Athena authors one exact Sunset Packet Preview
-> Jayson approves COMPLETE SUNSET [Archive ID]
-> Spear validates and deterministically renders one Monthly Feather entry
-> Noctua verifies the durable archive and continuity readback
-> the session becomes archive-ready

Phoenix Burn
-> Standard or Full archive, Feather, Golden Wing, active-source, alignment, and restart-readiness reconciliation
-> Reforge Preview when doctrine correction is needed
-> exact separately approved source transaction
-> Noctua audit
-> Jayson-controlled merge
-> merged-main readback
-> Atlas absorbs
```

## Semantic versus mechanical authority

### Athena

Athena performs semantic work:

- session interpretation;
- Sunset and Solar Eclipse authorship;
- Feather meaning;
- Quest, Campaign, and Emberline status interpretation;
- Controlled Burn;
- Phoenix Flare triage;
- Standard and Full Phoenix Burn reconciliation;
- recurrence and contradiction analysis;
- Golden Wing validation;
- Reforge Preview authorship;
- destination selection;
- complete-file authorship;
- migration meaning and preservation decisions.

### Spear

Spear performs only registered deterministic mechanics:

- parse and schema validation;
- canonicalization and hashing;
- lineage and destination-policy checks;
- current-source-state checks;
- deterministic rendering;
- temporary-tree simulation;
- exact diff and manifest production;
- atomic Git object creation;
- one new transaction branch;
- one draft PR;
- deterministic receipts.

Spear does not interpret raw conversations, invent doctrine, decide promotion, rank Quests, merge, auto-merge, force push, write directly to `main`, hard-delete, or modify its protected implementation surfaces through ordinary packets.

### Noctua

Noctua verifies source order, packet and plan integrity, base state, hashes, changed filenames, full diff, protected boundaries, source/generated separation, tests, atomicity, PR head, merge proof, readback, migration closure, and recovery claims.

### Jayson

Jayson controls unresolved decisions, Preview -> Execute approval, source promotion, residual-risk acceptance, manual merge, migrations, automation activation, retirement, deletion, and final cutover.

## Lifecycle surfaces

### Sunset

Sunset is the essential archival closeout for a session.

`SUNSET` is Preview-only. Athena authors one exact Sunset Packet candidate and reports what is durable, chat-only, uncertain, unfinished, and protected.

`COMPLETE SUNSET [Archive ID]` executes only the exact approved archive transaction. The session is not archive-ready until the durable archive and required Quest/Workboard continuity are read back and verified.

### Monthly Feather Archives

Prime's durable Essential Sunset Archive representation is one concise, verified, stable-ID entry in the correct Monthly Atlas Feather Archive unless a separately approved exception exists.

Entries are append-oriented, stale-hash protected, and amendment-based. Closed months reject ordinary appends. Feathers are continuity provenance, not governing doctrine.

### Solar Eclipse

Solar Eclipse is the active-transfer form of Sunset. It transfers a compact active Emberline checkpoint to a receiving chat and closes only the old chat after handshake PASS plus durable archive and Quest/Workboard readback.

Solar Eclipse does not complete the Quest, Campaign, milestone, or continuing workstream.

### Quest Registry, Quest Board, and Emberline

Quest Registry is the authoritative current work snapshot after cutover. Quest events preserve append-only history. Quest Board is a small deterministic projection, not an independent authority source.

Emberline is the independent unified Quest/Campaign roadmap and status model. It may identify status or source drift, but it is not a generic source-update engine, Phoenix Burn stage, or Phoenix Flare disposition.

### Phoenix Flare

Phoenix Flare is read-only Athena triage that recommends exactly one disposition:

1. **Controlled Burn**
2. **Phoenix Burn**
3. **Sunset**

Blocked is a workflow state. No Action is not a separate disposition; a clean session that should close routes to Sunset.

Phoenix Flare recommends. It does not write source, create an archive, update a register, merge, migrate, delete, retire, activate, or perform an external action.

### Controlled Burn

Controlled Burn is focused semantic distillation for one bounded topic, chat, workflow, archive cluster, or repeated context set.

It preserves history, classifies findings, and routes doctrine contradictions to Reforge. Recurrence alone never grants promotion.

### Golden Wing

Golden Wing is a validated promotion holding surface, not a general archive. Candidates retain stable identity, Feather provenance, recurrence evidence, intended destination, conflicts, dependencies, status history, and Athena or explicit Jayson validation.

### Phoenix Burn

Phoenix Burn is broad Atlas reconciliation, not only Golden Wing promotion analysis.

A **Standard Phoenix Burn** reviews every Essential Sunset Archive or Feather created since the last verified Burn, unresolved earlier findings, active source, routing, Quest/Workboard state, and open decisions.

A **Full Phoenix Burn** reviews the complete archive and Feather corpus, all unresolved prior findings, active doctrine, and successor architecture.

Phoenix Burn classifies what is already absorbed, historical only, a Quest/Workboard continuity need, a Reforge candidate, protected external evidence, or an unresolved conflict. A restart-safe verdict requires either no source changes or merged-main readback of every required approved change.

### Reforge

Reforge is the independent direct doctrine-reconciliation route.

`REFORGE — [topic]` produces an exact Preview candidate. Reforge does not itself write, merge, migrate, promote, delete, retire, activate, cut over, or expand actor authority.

### Absorption

Material is not `ABSORBED` merely because it appears in a packet, plan, branch, PR, commit, or merged diff.

`ABSORBED` requires:

1. Jayson-approved merge;
2. merged-main commit identification;
3. Noctua readback of the intended destination state;
4. provenance closure from source Feather and Golden Wing candidate;
5. transaction-ledger update;
6. no unresolved loss or conflict affecting the claim.

### Phoenix Reborn

Phoenix Reborn is independent backup, restore, and repository-integrity proof. It is not a Phoenix Flare disposition, Phoenix Burn stage, Sunset stage, or Reforge stage.

A Phoenix Flare or Phoenix Burn may identify a recovery obligation, but only the separate approved Phoenix Reborn contract can satisfy it.

Valid terminal postures are:

- `PHOENIX_REBORN`
- `PHOENIX_REBORN_ALREADY_SATISFIED`
- `BLOCKED_WITH_REBORN_PENDING`

A backup upload alone is not Phoenix Reborn. Full Reborn requires the approved backup, independent storage, integrity verification, isolated restore, repository comparison, and deterministic receipt defined by the Phoenix contract.

## Transitional predecessor rules

### Active Workboard -> Quest

The Active Workboard remains canonical until every row is explicitly inventoried and mapped to a Quest record, Quest event history, historical reference, or approved omission reason. No row may disappear silently.

### Emberline continuity

Emberline is the unified Quest/Campaign roadmap and status model across the Codex Workboard and Prime Quest Board transition.

It preserves current state, completed and unfinished gates, blockers, dependencies, durable versus uncertain context, protected boundaries, source and receipt lineage, next safe action, and the next approval gate.

Emberline identifies source drift. Reforge and the normal source-update workflow prepare any durable correction. Emberline does not silently write, merge, migrate, promote, delete, retire, activate, or cut over.

## Provenance rule

Sunset Packets, Essential Sunset Archive Feather entries, Solar Eclipse handshakes, Quest events, Emberline checkpoints, Burn Reports, Golden Wing candidates, Phoenix Burn assessments, Reforge Previews, Spear packets, plans, receipts, PR discussions, and recovery receipts preserve provenance. None automatically becomes canonical by age, repetition, storage location, or successful automation.
