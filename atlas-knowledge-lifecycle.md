---
title: Atlas Knowledge Lifecycle
atlas_id: atlas-prime.knowledge-lifecycle
format_version: '1.0'
status: PROPOSED
source_type: CORE_DOCTRINE
authority_class: CANONICAL_AUTHORED_SOURCE
owner_project: Codex
owner_operation: Source Governance
canonical_scope: Controlling sequence, semantic authority, provenance states, absorption
  rules, and transitional predecessor safeguards for Sunset, Feathers, Quests, Phoenix
  Flare, Controlled Burn, Golden Wing, Phoenix Burn, Spear, Noctua, and Phoenix Reborn.
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
last_verified: '2026-06-21'
---

# Atlas Knowledge Lifecycle

## Controlling rule

This file is the controlling lifecycle map for Atlas Prime. Specialized doctrine, schemas, policies, and tools MAY add detail, but MUST NOT redefine the sequence, actor boundaries, or reserved Phoenix meanings.

## Lifecycle

```text
Session
→ Athena creates a Sunset Packet
→ Spear validates and deterministically renders one Feather Entry
→ Monthly Atlas Feather Archive
→ Phoenix Flare
→ Controlled Burn when needed
→ Athena validates promotion candidates
→ Golden Wing
→ Phoenix Burn
→ Athena authors complete destination files
→ Spear validates and stages one atomic repository transaction
→ Noctua audits
→ Jayson approves and manually merges
→ merged-main readback
→ Atlas absorbs
→ Phoenix Reborn
```

## Semantic versus mechanical authority

### Athena

Athena performs semantic work:

- session interpretation;
- Sunset authorship;
- Feather meaning;
- Quest creation, update, state, and ranking decisions;
- Controlled Burn;
- recurrence and contradiction analysis;
- Golden Wing validation;
- Phoenix Burn;
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

Sunset closes a session. Athena authors meaning. A normal Sunset does not create a standalone GitHub harvest file by default in the target architecture.

### Monthly Feather Archives

Each Sunset produces one concise entry in the correct monthly archive. Entries are append-oriented, uniquely identified, stale-hash protected, and amendment-based. Closed months reject ordinary appends.

### Quest Registry and Quest Board

Quest Registry is the authoritative current work snapshot. Quest events preserve append-only history. Quest Board is a small deterministic projection, not an independent authority source.

### Phoenix Flare

Phoenix Flare is read-only Athena analysis with exactly these primary dispositions:

- `NO_BURN`
- `CONTROLLED_BURN`
- `PHOENIX_BURN`
- `BLOCKED`

It is not an umbrella family and does not perform repository changes.

### Controlled Burn

Controlled Burn is Athena's semantic compaction, consolidation, contradiction review, and promotion-candidate classification. Recurrence alone never grants promotion.

### Golden Wing

Golden Wing is a validated promotion holding surface, not a general archive. Candidates retain stable identity, Feather provenance, recurrence evidence, intended destination, conflicts, dependencies, status history, and Athena or explicit Jayson validation.

### Phoenix Burn

Phoenix Burn is Athena's Golden Wing -> durable-source promotion analysis. Athena authors complete final destination files. Spear validates and stages mechanics only.

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

Every completed Phoenix Flare creates an eventual recovery obligation after the selected work reaches a stable verified state.

Valid terminal postures are:

- `PHOENIX_REBORN`
- `PHOENIX_REBORN_ALREADY_SATISFIED`
- `BLOCKED_WITH_REBORN_PENDING`

A backup upload alone is not Phoenix Reborn. Full Reborn requires the approved backup, independent storage, integrity verification, isolated restore, repository comparison, and deterministic receipt defined by the Phoenix contract.

## Transitional predecessor rules

### Active Workboard -> Quest

The Active Workboard remains canonical until every row is explicitly inventoried and mapped to a Quest record, Quest event history, historical reference, or approved omission reason. No row may disappear silently.

### Emberline -> Spear and source-update governance

Emberline remains operationally canonical until its safeguards are demonstrably absorbed by:

- Spear packet and plan binding;
- atomic transaction behavior;
- Noctua verification;
- Quest continuity;
- source + routing + readback + cleanup discipline;
- honest skipped, blocked, and manual-item reporting.

Only then may Emberline receive an explicit supersession or retirement disposition.

## Provenance rule

Feathers, Quest events, Burn Reports, Golden Wing candidates, Phoenix Burn assessments, Spear packets, plans, receipts, PR discussions, and recovery receipts preserve provenance. None automatically becomes canonical by age, repetition, storage location, or successful automation.
