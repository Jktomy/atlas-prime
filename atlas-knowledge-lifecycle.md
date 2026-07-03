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
last_verified: '2026-07-03'
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

CONTROLLED BURN
-> Athena distills one bounded context cluster
-> one Burn Report preserves focused provenance
-> Burn Report remains active provenance until later Sunset or Phoenix Burn review
-> Controlled Burn never creates a Feather directly

SUNSET
-> Athena reviews relevant Burn Reports and authors one exact Sunset Packet Preview
-> Jayson approves COMPLETE SUNSET [Archive ID]
-> Spear validates and deterministically renders one Feather entry in the correct Monthly Feather Archive
-> Noctua verifies the durable archive and continuity readback
-> the session becomes archive-ready

LEARNED-KNOWLEDGE PROMOTION — NORMAL, NOT MANDATORY
Feather corpus
-> Standard or Full Phoenix Burn reconciles memory, active work, direction, source alignment, and Atlas Soul
-> Phoenix Burn validates a Golden Wing candidate when recurrence and corroboration justify promotion
-> Reforge authors the exact doctrine-reconciliation Preview
-> exact separately approved source transaction
-> Noctua audit
-> Jayson-controlled merge
-> merged-main readback
-> Atlas absorbs

DIRECT CORRECTION EXCEPTION
confirmed doctrine contradiction or explicit Jayson instruction
-> Reforge Preview without waiting for recurrence or Golden Wing promotion
-> the same approval, audit, merge, and readback controls
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

Sunset is the sole session-closeout route that renders selected continuity as a Feather. It may incorporate or cite a Controlled Burn Report, but the Burn Report itself never becomes a Feather automatically.

### Monthly Feather Archives

Prime's durable Essential Sunset Archive representation is one concise, verified, stable-ID Feather entry in the correct Monthly Atlas Feather Archive unless a separately approved exception exists.

A Feather is the individual continuity record. The Monthly Feather Archive is its append-oriented container, not a higher promotion tier.

Entries are stale-hash protected and amendment-based. Closed months reject ordinary appends. Feathers are continuity provenance, not governing doctrine.

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

It produces one Burn Report that preserves focused provenance, classifies findings, and routes doctrine contradictions to Reforge. A Burn Report is not a Feather and does not close a session.

During active work, a durable Burn Report remains available for later Sunset or Phoenix Burn review. During chat closeout, Controlled Burn returns to Sunset, which selects only the continuity that belongs in the Feather.

Recurrence alone never grants promotion.

### Golden Wing

Golden Wing is a validated promotion holding surface, not a general archive. Candidates retain stable identity, Feather provenance, recurrence evidence, intended destination, conflicts, dependencies, status history, and Athena or explicit Jayson validation.

The normal learned-knowledge route creates or validates Golden Wing candidates through Phoenix Burn. A Golden Wing is promotion-ready meaning, not doctrine; Reforge must still author the exact doctrine change.

### Phoenix Burn

Phoenix Burn is Athena's broad documentary-memory consolidation and Atlas reconciliation process, not only Golden Wing promotion analysis.

It clears and reconciles the documentary mind by comparing what happened, what Atlas is doing, where Atlas is going, and whether memory and direction remain aligned with active source and Atlas Soul.

A **Standard Phoenix Burn** reviews every Essential Sunset Archive or Feather created since the last verified Burn, unresolved earlier findings and Golden Wings, active control surfaces, routing, Quest/Workboard state, open decisions, and every source changed or materially implicated since the previous Burn.

A **Full Phoenix Burn** reviews every tracked clean Atlas document and generated projection in the verified documentary inventory regardless of lifecycle class; the complete Burn Report / archive / Feather corpus; retired, superseded, and historical material for correct classification, routing, provenance, and non-governing posture; all Golden Wings and unresolved prior findings; active doctrine, routing, registries, Quest/Workboard state, Codex / Prime alignment, Atlas Soul identity surfaces, and successor architecture.

Phoenix Burn classifies what is aligned and absorbed, stale or drifting, historical only, a Quest/Workboard continuity need, a Golden Wing candidate, a Reforge candidate, protected external evidence, or an unresolved conflict. A restart-safe verdict requires either no source changes or merged-main readback of every required approved change.

Atlas Soul defines constitutional identity. Phoenix Burn protects Soul integrity by reconciling the documentary mind against that standard; it does not replace Atlas Soul, Codex source order, or Reforge authority.

### Reforge

Reforge is the independent direct doctrine-reconciliation route.

`REFORGE — [topic]` produces an exact Preview candidate. Reforge does not itself write, merge, migrate, promote, delete, retire, activate, cut over, or expand actor authority.

### Absorption

Material is not `ABSORBED` merely because it appears in a packet, plan, branch, PR, commit, or merged diff.

`ABSORBED` requires:

1. Jayson-approved merge;
2. merged-main commit identification;
3. Noctua readback of the intended destination state;
4. provenance closure from the source Feather and Golden Wing candidate when the learned-knowledge promotion route applies, or from the direct contradiction / explicit instruction and its approved Reforge rationale when the direct-correction exception applies;
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
