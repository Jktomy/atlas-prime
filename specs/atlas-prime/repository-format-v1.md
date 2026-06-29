---
title: Atlas Prime Repository Format v1
atlas_id: atlas-prime.repository-format.v1
format_version: '1.0'
status: PROPOSED
source_type: SPECIFICATION
authority_class: TOOL_CONTRACT
owner_project: Codex
owner_operation: Source Governance
canonical_scope: Normative repository topology, authority classes, metadata, source
  and generated separation, lifecycle reservations, migration proof, validation relationships,
  and cutover requirements for Atlas Prime.
protected_level: CRITICAL
routes_from:
- README.md
routes_to:
- .gitattributes
- .gitignore
- schemas/atlas-prime/repository-manifest-v1.schema.json
- schemas/source-metadata/source-metadata-v1.schema.json
- schemas/migration/atlas-codex-inventory-v1.schema.json
- schemas/policies/atlas-prime-destination-policy-v0.2.schema.json
- schemas/policies/protected-paths-v0.2.schema.json
- policies/destination/atlas-prime-destination-policy-v0.2.yaml
- policies/protected-paths/protected-paths-v0.2.yaml
- templates/source-file.md
- codex/codex-source-update-standard.md
private_boundary: This specification defines clean repository structure only. It must
  not contain raw protected evidence, private runtime values, credentials, account
  data, PHI, raw finance evidence, network maps, device registers, or secret material.
evidence_boundary: Original evidence systems remain authoritative. Atlas Prime stores
  clean source, structured clean state, generated projections, migration provenance,
  and clean pointers.
supersedes: []
cleanup_path: Version through a new repository-format specification. Do not silently
  rewrite v1 after implementation depends on it.
last_verified: '2026-06-29'
---

# Atlas Prime Repository Format v1

## 1. Status and purpose

This specification defines the complete target format of `Jktomy/atlas-prime`.

It is a format contract, not a declaration that all target files already exist. The repository format and the already-existing Spear v0.3 foundation are co-designed and mutually validated. They are committed in narrow dependency-ordered PRs, then substantive Atlas content is rebuilt through audited Spear packets and manually merged pull requests after writer activation receives a separate approval.

`Jktomy/atlas-codex` remains canonical until verified cutover.

## 2. Normative language

The words **MUST**, **MUST NOT**, **REQUIRED**, **SHOULD**, **SHOULD NOT**, and **MAY** are normative.

When this specification conflicts with a current explicit Jayson instruction, the explicit instruction controls and the conflict MUST be recorded for the next versioned update.


## 2A. Controlling source order during reconciliation

1. Current explicit Jayson instruction.
2. Existing Spear v0.3 foundation preserved in the June 21, 2026 Sunset package.
3. June 21 Spear lifecycle audit and locked decisions.
4. Current merged `Jktomy/atlas-prime` source.
5. Current `Jktomy/atlas-codex` as canonical operational source until cutover and as legacy migration evidence.
6. Original approved evidence sources.
7. Athena inference, explicitly labeled.

Conflicting predecessor meanings MUST be reconciled through an explicit Reforge Preview and, when migration lineage is affected, an explicit migration disposition. Codex remains canonical until verified cutover.

## 3. Core principles

1. **No silent authority.** Storage, repetition, age, generation, or successful automation does not make content canonical.
2. **No silent loss.** Every tracked predecessor path receives an explicit migration disposition.
3. **No orphan source.** Every durable behavior source has an owner, routing hooks, verification path, and cleanup or supersession path.
4. **Private evidence stays private.** GitHub receives clean source and pointers, not raw protected evidence.
5. **Authored source and generated projections are distinct.**
6. **Athena authors meaning; Spear executes deterministic mechanics; Noctua audits; Jayson decides permanence.**
7. **Preview → Execute precedes durable action.**
8. **Phoenix Reborn is independent of Spear.**
9. **Prime does not use a normal direct-main fast path.**
10. **A migration is complete only after merged-main readback and migration-ledger closure.**

## 4. Repository states

The repository state is one of:

- `SHADOW` — construction and testing; predecessor remains canonical.
- `CUTOVER_CANDIDATE` — migration coverage and proofs are complete; explicit cutover approval remains.
- `CANONICAL` — Jayson explicitly approved cutover and source-order files were updated.
- `FROZEN` — temporarily read-only for audit, cutover, incident response, or retirement.
- `RETIRED` — no longer active; retained only according to an approved retention decision.

The current state is `SHADOW`.

## 5. Target topology

```text
atlas-prime/
├── .gitattributes
├── .gitignore
├── README.md
├── bootstrap.md
├── atlas-start-here.md
├── atlas-prime.md
├── atlas-index.md
├── atlas-command-surface.md
├── atlas-command-surface-dashboard.md
├── atlas-protocol-registry.md
├── atlas-knowledge-lifecycle.md
├── atlas-aegis.md
├── athenas-spear.md
├── noctua.md
├── sunsetting-protocol.md
├── controlled-burn-protocol.md
├── phoenix-flare.md
├── phoenix-burn-protocol.md
├── phoenix-reborn.md
├── codex/
│   ├── codex-source-update-standard.md
│   ├── governance/
│   │   ├── source-hierarchy.md
│   │   ├── source-metadata-standard.md
│   │   ├── protected-source-boundary.md
│   │   ├── generated-view-standard.md
│   │   ├── versioning-and-supersession.md
│   │   └── cutover-standard.md
│   ├── quests/
│   │   ├── quest-registry.json
│   │   └── events/YYYY/YYYY-MM.jsonl
│   ├── quest-registry.md
│   ├── atlas-quest-board.md
│   ├── golden-wing/
│   │   ├── candidates.json
│   │   └── events/YYYY/YYYY-MM.jsonl
│   ├── golden-wing.md
│   └── atlas-feather-archives.md
├── atlas-feather-archives/YYYY/YYYY-MM.md
├── projects/<project-slug>/
│   ├── project.md
│   └── operations/<operation-slug>/
│       ├── operation.md
│       ├── runbooks/
│       ├── protocols/
│       └── templates/
├── specs/
│   ├── atlas-prime/
│   ├── spear/
│   ├── noctua/
│   └── phoenix/
├── schemas/
│   ├── atlas-prime/
│   ├── source-metadata/
│   ├── spear/
│   ├── migration/
│   ├── quests/
│   ├── feathers/
│   ├── golden-wing/
│   └── phoenix/
├── policies/
│   ├── destination/
│   ├── operations/
│   ├── protected-paths/
│   └── privacy/
├── tools/
│   ├── spear/
│   └── phoenix/
├── tests/
│   ├── format/
│   ├── spear/
│   ├── phoenix/
│   └── fixtures/
├── templates/
├── generated/
├── migration/atlas-codex/
│   ├── source-inventory.json
│   ├── disposition-ledger.json
│   ├── migration-map.md
│   └── audits/
└── .github/workflows/
```

A target path MAY be absent until its implementation wave. Absence MUST be represented as `PLANNED` or `CONDITIONAL` in the future repository manifest, not mistaken for completion.


## 5A. PR 1A foundation subset

The first format-and-authority PR establishes repository line-ending controls, preserves and binds the existing `.gitignore`, and establishes the repository entry point, core doctrine, Aegis, the controlling lifecycle skeleton, the source-update standard, format schemas, destination classification, protected paths, and the authored-source template.

It MUST NOT migrate predecessor content, activate Spear writes, create operational registers, generate dashboards, run automation, or claim Phoenix Reborn.

## 6. Path and naming rules

- Repository paths use UTF-8, forward slashes, and LF line endings. `.gitattributes` is the repository-level enforcement surface for supported text types.
- `.gitignore` is preserved as a protected repository-hygiene control. Changes require exact current readback and a complete replacement diff.
- Authored path segments use lowercase kebab-case unless an external format requires otherwise.
- No absolute paths, backslashes, traversal components, percent-encoded traversal, Unicode-confusable separators, control characters, trailing spaces, or case-colliding paths.
- Markdown uses `.md`; JSON uses `.json`; append-only event ledgers use `.jsonl`; YAML policy files use `.yaml`.
- Root Markdown is reserved for approved restart, command, governance, lifecycle, and protocol surfaces.
- Project and Operation slugs MUST be stable. Renaming is a separately approved migration, not an ordinary source edit.
- Binary content is denied unless a later versioned policy explicitly creates a narrow approved class.
- Symlinks, submodules, nested archives, and executable payloads are denied by default.

## 7. Authority classes

Every repository file belongs to exactly one primary authority class.

### `CANONICAL_AUTHORED_SOURCE`

Human- or Athena-authored governing doctrine, protocol, standard, Project, Operation, runbook, or approved decision source.

### `STRUCTURED_AUTHORITATIVE_REGISTER`

Machine-readable current state whose schema and transition rules are governing, such as the Quest Registry.

### `GENERATED_OPERATIONAL_PROJECTION`

A reproducible view derived from authoritative sources. It is never independently authoritative.

The Quest Board is a narrow exception to normal source/generated PR separation: it MAY be regenerated and committed atomically with the Quest Registry and Quest Event Ledger when the future Quest operation contract explicitly authorizes that transaction.

### `CONTINUITY_PROVENANCE`

Feathers, Sunset-derived summaries, receipts, reports, and other non-governing continuity or provenance.

### `TOOL_CONTRACT`

Specifications, schemas, policies, and testable contracts governing deterministic tools.

### `TOOL_IMPLEMENTATION`

Source code and implementation documentation.

### `MIGRATION_EVIDENCE`

Inventories, maps, disposition ledgers, migration audits, and predecessor-to-successor proof.

### `HISTORICAL_REFERENCE`

Retained historical material that no longer governs current Atlas behavior.

### `PRIVATE_POINTER`

A clean pointer or non-sensitive summary referring to protected evidence outside GitHub.

No file may claim more than one primary authority class. Relationships to other classes are represented through routes and dependencies.

## 8. Source types

Prime source metadata uses one source type:

- `BOOTSTRAP`
- `CORE_DOCTRINE`
- `PROTOCOL`
- `STANDARD`
- `SPECIFICATION`
- `POLICY`
- `PROJECT`
- `OPERATION`
- `RUNBOOK`
- `TEMPLATE`
- `REFERENCE`
- `REGISTER_VIEW`
- `GENERATED_VIEW`
- `MIGRATION_RECORD`
- `HISTORICAL_RECORD`
- `TOOL_DOCUMENTATION`

Structured registers, event ledgers, schemas, policy files, code, and generated artifacts MAY use format-specific metadata instead of Markdown front matter, but MUST appear in the repository manifest and have a declared schema or generator contract.

## 9. Markdown source metadata

All authored canonical, continuity, migration, historical, template, and tool-documentation Markdown MUST begin with YAML front matter conforming to:

`schemas/source-metadata/source-metadata-v1.schema.json`

Required fields are:

```text
title
atlas_id
format_version
status
source_type
authority_class
owner_project
owner_operation
canonical_scope
protected_level
routes_from
routes_to
private_boundary
evidence_boundary
supersedes
cleanup_path
last_verified
```

Rules:

- `atlas_id` is stable and unique repository-wide.
- `routes_from` and `routes_to` contain repository-relative paths only.
- A governing file MUST have at least one inbound route unless it is an approved root bootstrap source.
- A superseded file MUST identify its successor through `supersedes`, `cleanup_path`, body text, or migration ledger.
- `last_verified` means content and routes were checked, not merely edited.
- Front matter does not itself grant authority; repository state, source order, status, and cutover state also apply.

## 10. Routing and discoverability

Every durable behavior change requires:

```text
source
+ owner
+ routing hook
+ verification readback
+ cleanup or supersession path
```

Acceptable routing surfaces include:

- `bootstrap.md`
- `atlas-start-here.md`
- `atlas-index.md`
- `atlas-protocol-registry.md`
- `atlas-command-surface.md`
- a clearly routed parent Project or Operation file.

A file without a verified routing hook MUST be reported as:

```text
Durable storage present; routing incomplete.
```

Generated indexes may expose routes, but the authored route declarations and authoritative source remain controlling.

## 11. Authored source versus generated projections

### Source PRs

Source PRs contain authored canonical source, contracts, schemas, policies, structured-register changes, continuity records, or migration evidence.

### Generated PRs

Ordinary generated inventories, indexes, dashboards, and reports are refreshed in separate PRs after the source merge.

### Quest Board exception

`codex/atlas-quest-board.md` MAY be part of the same atomic transaction as:

- `codex/quests/quest-registry.json`;
- the applicable monthly Quest Event Ledger;
- a deterministic generation receipt.

This exception does not authorize other generated files to accompany source changes.

### Direct edits

Generated projections MUST NOT be edited directly. The authoritative inputs must change and the projection must be regenerated.

## 12. Structured state and append-only history

A structured authoritative register MUST have:

- a versioned schema;
- stable record IDs;
- optimistic concurrency or expected-version checks;
- declared transition rules;
- an append-only event or receipt trail where required;
- deterministic serialization;
- an owner and routing surface;
- a recovery and reconstruction procedure.

Corrections to append-only ledgers create new correction events. They do not silently rewrite prior events.

## 13. Knowledge lifecycle reservations

The following meanings are reserved for Prime and MUST NOT be redefined by migrated predecessor language.

### Sunset

Sunset is the essential archival closeout for a session.

`SUNSET` is Preview-only. Athena authors one exact Sunset Packet candidate.

`COMPLETE SUNSET [Archive ID]` performs only the exact approved archive transaction. Spear validates and deterministically renders the approved archival section into one stable-ID Monthly Feather entry. The session is not archive-ready until the durable archive and required Quest/Workboard continuity are read back and verified.

### Monthly Atlas Feather Archives

Prime's durable Essential Sunset Archive representation is one concise verified entry in the correct Monthly Atlas Feather Archive unless a separately approved exception exists.

Monthly Feathers are summarized, append-oriented continuity memory. They are not transcripts or governing doctrine. Closed months block normal append; late material uses a dated addendum; corrections use amendments rather than silent rewrites.

### Solar Eclipse

Solar Eclipse is the active-transfer form of Sunset. It transfers a compact active Emberline checkpoint and closes only the old chat after handshake PASS plus durable archive and Quest/Workboard readback.

Solar Eclipse does not complete the Quest, Campaign, milestone, or continuing workstream.

### Phoenix Flare

Phoenix Flare is read-only Athena triage that recommends exactly one disposition:

1. **Controlled Burn**
2. **Phoenix Burn**
3. **Sunset**

Blocked is a workflow state. No Action is not a separate disposition.

Phoenix Flare does not perform source mutation, promotion, archive execution, register mutation, backup upload, merge, migration, deletion, retirement, activation, cutover, or automation execution.

### Controlled Burn

Controlled Burn is focused semantic distillation for one bounded topic, chat, workflow, archive cluster, or repeated context set.

Athena may classify findings as:

- `PROMOTE`
- `MERGE_WITH_EXISTING`
- `RETAIN`
- `DEFER`
- `REJECT`
- `SUPERSEDE`
- `NEEDS_JAYSON`

Controlled Burn preserves history, never silently promotes doctrine, and routes doctrine contradictions to Reforge.

### Golden Wing

Golden Wing holds Athena-validated or explicitly Jayson-directed promotion candidates with stable IDs and Feather provenance. It is not a general archive.

### Phoenix Burn

Phoenix Burn is broad Atlas reconciliation, not only Golden Wing promotion analysis.

A **Standard Phoenix Burn** reviews every Essential Sunset Archive or Feather created since the last verified Burn, unresolved earlier findings, active source, routing, Quest/Workboard state, and open decisions.

A **Full Phoenix Burn** reviews the complete archive and Feather corpus, all unresolved prior findings, active doctrine, and successor architecture.

Phoenix Burn classifies findings as already absorbed, historical only, Quest/Workboard continuity needed, Reforge candidate, protected external evidence, or unresolved conflict. A restart-safe verdict requires either no source changes or merged-main readback of every required approved change.

### Reforge

Reforge is the independent direct doctrine-reconciliation route.

`REFORGE — [topic]` produces an exact Preview candidate. Reforge does not itself write, merge, migrate, promote, delete, retire, activate, cut over, or expand actor authority.

### Emberline

Emberline is the independent unified Quest/Campaign roadmap and status model.

It may identify stale status or source drift, but it is not a generic source-update engine, Phoenix Burn stage, or Phoenix Flare disposition. Durable changes route through Reforge or the normal source-update workflow.

### Noctua

Noctua independently audits packets, changed filenames, hashes, diffs, routes, tests, PR state, merge proof, and merged-main readback. Only verified readback may confirm `ABSORBED`.

### Phoenix Reborn

Phoenix Reborn is independent backup, restore, and repository-integrity proof. It is not a Phoenix Flare disposition, Phoenix Burn stage, Sunset stage, or Reforge stage.

A Flare or Burn may identify a recovery obligation. Only the separately approved Phoenix Reborn contract can satisfy it.

Valid terminal postures are:

- `PHOENIX_REBORN`
- `PHOENIX_REBORN_ALREADY_SATISFIED`
- `BLOCKED_WITH_REBORN_PENDING`

The future n8n and Google Drive workflow is reserved but not authorized by this format contract. Upload success alone MUST NOT be represented as full Phoenix Reborn unless the approved proof level is satisfied.

## 14. Spear boundary

The current merged v0.2 Spear contract remains versioned and unchanged as historical and compatibility source.

The existing v0.3 foundation is preserved and formalized in parallel. Its initial registered operation surface is:

- `CREATE_FILE`
- `REPLACE_FILE_FULL`
- `APPEND_FEATHER_ENTRY`
- `APPLY_QUEST_DELTA`
- `GENERATE_QUEST_BOARD`
- `APPLY_SUNSET_LIFECYCLE`

These names are contract reservations, not write activation. The destination and operation policies set every v0.3 operation to `execution_authorized: false` until the separate writer gate is approved.

Spear MUST NOT:

- interpret raw conversation meaning;
- choose promotion;
- self-approve;
- modify its own engine, contracts, policies, workflows, tests, or fixtures through ordinary packets;
- modify Phoenix Reborn tooling;
- write directly to `main`;
- merge;
- force-push;
- delete, move, rename, or archive in the initial v0.3 release;
- execute arbitrary scripts, shell commands, modules, endpoints, or environment variables selected by a packet;
- store prohibited protected evidence.

## 15. Source-update and pull-request rules

Every durable update follows:

```text
Preview
→ explicit Execute approval
→ verify current main
→ create narrow branch
→ write approved complete files
→ audit changed filenames
→ audit diff and tests
→ open draft PR
→ Noctua audit
→ Jayson-controlled manual merge or separately approved exact Execute Arrow
→ verify merge record and merged-main readback
```

Rules:

- One sensitive file at a time when safety-adjacent unless an approved atomic contract requires a multi-file transaction.
- Source PRs and ordinary generated-report PRs remain separate.
- No direct-main fast path exists in Prime's normal workflow.
- Full-file replacement requires complete current readback, exact expected source hash, exact proposed payload hash, declared removals, preserved required metadata and headings, route validation, and a visible diff.
- A connector block stops the blocked action; it must not be repeatedly retried through unsafe wording changes.
- PR repair requires a new bounded authorization and re-audit.
- Spear stops before merge.

## 16. Protected evidence boundary

The following do not belong raw in GitHub:

- passwords, keys, tokens, MFA or recovery codes, private keys, seed phrases, real `.env` values;
- PHI, medical records, unredacted health evidence;
- raw finance, broker, Tiller, tax, insurance, mortgage, estate, legal, account, or transaction evidence;
- private runtime registers, IP addresses, network maps, device registers, private infrastructure paths;
- raw household, identity, or protected exports.

Allowed forms are:

- clean non-sensitive source;
- clean summaries that do not reproduce protected facts unnecessarily;
- schemas and protocols;
- redacted examples;
- clean pointers to the authoritative external source.

When uncertain, use `PRIVATE_POINTER` and keep the evidence outside GitHub.

## 17. Migration from atlas-codex

The migration inventory conforms to:

`schemas/migration/atlas-codex-inventory-v1.schema.json`

Every tracked predecessor path receives one disposition:

- `MIGRATE`
- `MERGE`
- `REMODEL`
- `GENERATED_REBUILD`
- `HISTORICAL_REFERENCE`
- `PRIVATE_POINTER`
- `SUPERSEDE`
- `RETIRE`
- `OMIT_WITH_REASON`

Each entry records:

- source path and hashes;
- source commit;
- target paths;
- content carried forward;
- content removed or remodeled;
- reason and dependencies;
- packet, PR, commit, and Noctua proof when applicable;
- final migration state.

`OMIT_WITH_REASON` requires explicit rationale and approval. Missing inventory entries are migration failures, not implicit omission.

The Active Workboard must be explicitly mapped into the Quest system record by record. It must not disappear through a dashboard rewrite.

## 18. Repository manifest

A generated repository manifest conforming to:

`schemas/atlas-prime/repository-manifest-v1.schema.json`

will eventually record:

- repository state and base commit;
- present, planned, conditional, generated, migration-only, and retired paths;
- authority class and source type;
- schema or generator contract;
- owner, routes, protection level, and write lane;
- hashes for present files;
- cutover requirements.

The manifest is a generated verification surface. It does not override source metadata, policy, or current explicit instruction.

### Manifest and inventory hashing

For `manifest_sha256` and `inventory_sha256`:

1. parse JSON with duplicate-key rejection;
2. remove the top-level hash field being calculated;
3. serialize canonical UTF-8 JSON with lexicographically sorted object keys, no insignificant whitespace, stable scalar encoding, and preserved array order;
4. normalize embedded text line endings to LF where applicable;
5. calculate SHA-256 and store the lowercase hexadecimal digest.

Validators MUST also reject duplicate repository-manifest paths and duplicate migration `source_path` entries. JSON Schema alone does not enforce those uniqueness rules.

## 19. Validation graph

A conforming Prime validation run checks:

1. JSON and YAML syntax.
2. JSON Schema validity.
3. Markdown front matter against the source-metadata schema.
4. Unique `atlas_id` values.
5. Path normalization, case collisions, and forbidden path forms.
6. Destination-policy classification.
7. Protected-path denial and actor boundaries.
8. Required routing hooks and route target existence or declared planned state.
9. Source/generated separation.
10. Structured-register schemas and transition rules.
11. Generated-view reproducibility.
12. Migration inventory coverage and disposition validity.
13. Prohibited-content screening with redacted diagnostics.
14. Git blob or SHA-256 hashes where required.
15. Changed-filename and complete-diff audit.
16. Noctua acceptance criteria.
17. Post-merge readback.

Pattern screening supports human review; it never proves absence of protected material.

## 20. Noctua acceptance criteria for this foundation

The foundation PR is acceptable only when:

- base is the verified current `main`;
- exactly the approved eight files change;
- the existing v0.2 Spear files are unchanged;
- no workflows, code, generated reports, migration content, or automation are added;
- all three JSON schemas parse and validate as schemas;
- both YAML policy files parse;
- the README and specification front matter validate;
- all proposed paths classify under the destination policy;
- the policy remains `CLASSIFICATION_ONLY`;
- repository writes remain unauthorized;
- Direct-Main is not introduced;
- Phoenix meanings match the current explicit decisions;
- Phoenix Reborn is labeled as the June 21, 2026 new decision and no n8n or Drive action is performed;
- protected-source boundaries are at least as strong as canonical Codex;
- no unexplained doctrine removal is hidden inside the format PR;
- a clean diff and post-merge readback are available;
- Jayson controls merge directly or through a separately approved exact Execute Arrow.

## 21. Cutover gates

Atlas Prime may move from `SHADOW` to `CUTOVER_CANDIDATE` only when:

- the full target format is implemented or explicitly dispositioned;
- the complete migration inventory has zero unexplained gaps;
- all active lifecycle doctrine is aligned;
- v0.3 Spear planning and writer pilots pass adversarial tests;
- Noctua independently verifies source, transactions, and readback;
- Phoenix Reborn proves an independent real backup and isolated restore;
- generated projections are rebuilt and verified;
- rollback and predecessor retention are documented.

It becomes `CANONICAL` only through explicit Jayson approval and verified source-order updates.


## 21A. Contract dependency relationship

The format and Spear v0.3 contracts are co-designed but not necessarily merged in one PR. The safe dependency order is:

```text
Format and lifecycle Preview + Spear v0.3 contract Preview
→ narrow format/lifecycle source PRs
→ independent Phoenix Reborn contract and tooling PR
→ Spear v0.3 schemas, policies, and hostile corpus PR
→ PLAN_ONLY compiler PR
→ complete migration inventory
→ separately approved writer pilot PR
→ Spear-packet-driven rebuild waves
→ cutover proof
```

A later PR may depend on an earlier merged contract, but no stage may reinterpret an already-locked lifecycle meaning.

## 22. Versioning

This specification is immutable in meaning once implementation depends on it.

Changes require:

- a new versioned specification or an explicitly versioned compatible revision;
- impact analysis;
- schema and policy updates;
- migration notes;
- Noctua audit;
- Preview → Execute;
- Jayson-controlled manual merge or separately approved exact Execute Arrow.

No tool may silently reinterpret v1.
