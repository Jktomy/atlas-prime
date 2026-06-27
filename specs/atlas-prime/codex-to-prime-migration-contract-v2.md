---
title: Atlas Codex to Atlas Prime Migration and Reconciliation Contract v2
atlas_id: atlas-prime.migration.codex-to-prime.v2
format_version: "1.0"
status: ACTIVE
source_type: SPECIFICATION
authority_class: TOOL_CONTRACT
owner_project: Codex
owner_operation: Source Governance
canonical_scope: Defines the immutable frozen-baseline and ordered-delta control plane for complete Atlas Codex predecessor accounting, migration reconciliation, collision review, route selection, proof, closure, and cutover preparation in Atlas Prime.
protected_level: CRITICAL
routes_from:
  - specs/atlas-prime/codex-to-prime-migration-contract-v1.md
routes_to:
  - schemas/migration/atlas-codex-inventory-v1.schema.json
  - schemas/migration/atlas-codex-delta-v1.schema.json
  - codex/codex-source-update-standard.md
  - migration/atlas-codex/README.md
  - templates/codex-to-prime-reconciliation-record.md
private_boundary: This contract may contain clean migration doctrine, classifications, schemas, paths, hashes, and examples only. It must not contain secrets, credentials, PHI, raw finance or account evidence, private runtime values, IP addresses, network maps, device registers, raw protected exports, or other prohibited evidence.
evidence_boundary: Atlas Codex source and Git history, the frozen inventory, ordered delta records, current Atlas Prime source, original evidence systems, reconciliation records, Spear receipts, pull requests, Noctua reports, and recovery proofs remain distinct evidence sources. This contract governs their clean reconciliation and does not replace them.
supersedes:
  - specs/atlas-prime/codex-to-prime-migration-contract-v1.md
cleanup_path: Keep v2 as the controlling migration contract while baseline-plus-delta accounting is active. Replace only through a later reviewed versioned contract, preserve predecessor contracts as historical evidence, and never rewrite the frozen baseline to simulate freshness.
last_verified: 2026-06-27
---

# Atlas Codex to Atlas Prime Migration and Reconciliation Contract v2

## 1. Status and purpose

This specification controls the Atlas Codex to Atlas Prime migration evidence architecture after the original source inventory ceased to equal live Codex `main`.

It replaces the single-current-inventory assumption with:

```text
immutable frozen baseline
+ ordered versioned deltas
= effective migration inventory
```

This contract does not migrate content.

It does not create or close a disposition ledger.

It does not dispatch or activate S1.

It does not authorize branch creation, pull requests, source promotion, predecessor retirement, deletion, cutover, automation, or direct modification of Atlas Codex.

During construction:

- `Jktomy/atlas-codex` remains the canonical operational source of truth.
- `Jktomy/atlas-prime` remains the proposed successor in `SHADOW`.
- Current merged Prime doctrine controls intended Prime architecture.
- Current Codex source supplies canonical operational meaning and predecessor evidence.
- Jayson decides unresolved meaning, permanent dispositions, execution, merge, promotion, retirement, and cutover.

## 2. Governing source order

For each migration-control change, reconciliation record, or migration batch, use this order:

1. current explicit Jayson instruction;
2. current merged Atlas Prime doctrine, lifecycle, repository-format, safety, source-update, and Spear contracts;
3. the immutable frozen Codex baseline at its exact pinned commit;
4. every accepted ordered Codex delta after that baseline;
5. current Codex source at the effective delta-chain head;
6. relevant approved Prime decisions and restart-safe continuity evidence;
7. approved original evidence systems when Codex contains only a summary, pointer, or stale representation;
8. Athena inference, clearly labeled and never silently promoted.

The frozen baseline proves historical predecessor coverage.

The ordered delta chain proves later Codex change coverage.

Current Codex remains operationally canonical until explicit cutover.

## 3. Accepted frozen baseline

The accepted baseline for this migration campaign is:

```text
Source repository:
Jktomy/atlas-codex

Frozen source commit:
3e4f06ed4abf8fbd44bd04ec1ad8997ffae7eda4

Inventory path:
migration/atlas-codex/source-inventory.json

Inventory Git blob:
f95c3fab4ce296c11f4f277c8e4675071cc92091

Inventory entries:
349

Unique source paths:
349

Stored canonical inventory digest:
03fa76c0991e06350cb112d1b33b1dbf00fe6296cabb08199cb92808956dd4fa
```

The baseline inventory and its v1 preflight are immutable historical migration evidence.

They must not be edited to:

- replace the pinned source commit with a newer commit;
- replace historical blobs or SHA-256 values;
- add post-baseline paths;
- remove predecessor paths;
- rewrite a historical freshness result;
- change provisional dispositions to simulate later reconciliation;
- or make the baseline appear current.

If baseline bytes or the accepted canonical digest fail verification, stop. Do not create or accept a delta until the discrepancy is resolved.

## 4. Ordered delta chain

Every tracked Codex change after the frozen baseline must be represented by one ordered delta conforming to:

`schemas/migration/atlas-codex-delta-v1.schema.json`

Each delta must:

- have a monotonically increasing sequence;
- start at the preceding accepted chain head;
- end at one exact later Codex commit;
- be contiguous and zero commits behind its starting point;
- enumerate every added, modified, removed, or renamed path in the comparison range;
- preserve old and new object identities where applicable;
- record migration-classification and collision effects;
- bind target observations to one exact Prime commit;
- state that execution authority is `NONE`;
- and carry a deterministic canonical digest.

Sequence `0001` begins at the frozen baseline commit.

Each later delta identifies the immediately preceding delta and its canonical digest.

A delta may not skip an intermediate accepted Codex change range unless the complete combined comparison still enumerates every changed path and preserves contiguous lineage.

## 5. Delta change semantics

Allowed change types are:

### `ADDED`

A path is present at the delta end and absent at the delta start.

The record must contain the new path, blob, SHA-256, classification, disposition, transfer class, targets, dependencies, and collision effects.

### `MODIFIED`

The same path exists at both ends with changed bytes or changed Git object identity.

The record must preserve both old and new blobs and SHA-256 values.

Any changed classification, disposition, transfer class, target, dependency, privacy boundary, or collision treatment must be explicit.

### `REMOVED`

A path exists at the delta start and is absent at the delta end.

Removal from live Codex does not erase migration lineage.

The delta retains the old path, blob, SHA-256, prior migration treatment, removal reason, and required retention, omission, supersession, retirement, or historical-review state.

A removed path remains part of accounted lineage even when it no longer contributes to the live-path count.

### `RENAMED`

A path changes identity between the delta start and end and Git evidence supports the rename interpretation.

The record preserves both paths, both object identities, both SHA-256 values, and any semantic changes.

When rename evidence is uncertain, represent the change as one `REMOVED` record plus one `ADDED` record rather than asserting a rename.

## 6. Zero-silent-loss effective inventory

The effective migration inventory is computed by applying accepted deltas in sequence to the frozen baseline.

The computation must track separately:

- live unique Codex paths at the chain head;
- all accounted lineage paths, including removed-path tombstones;
- normalized or case-only path collisions;
- unresolved delta records;
- and collision-group membership.

The following are migration failures:

- a live Codex path absent from the effective inventory;
- an unexplained delta path;
- two effective live records for one exact path;
- a normalized or case-only live-path collision;
- a modified path without its predecessor identity;
- a removed path that disappears from lineage;
- a renamed path without complete old-to-new accounting;
- a delta range that does not start at the preceding chain head;
- or a digest that cannot be reproduced.

## 7. Delta record contents

Each delta records at minimum:

- schema version and delta identity;
- sequence and status;
- source and target repositories;
- frozen-baseline identity;
- previous-delta identity or `null` for sequence `0001`;
- exact comparison start and end commits;
- comparison counts and contiguity;
- exact Prime observation commit and repository state;
- added, modified, removed, renamed, and total changed-path counts;
- resulting live and accounted-lineage counts;
- normalized collision count;
- one record per changed path;
- collision-group impacts;
- preparation identity and timestamp;
- execution authority;
- canonical delta digest;
- and clean notes.

Each changed-path record preserves applicable before and after values for:

- path;
- Git blob;
- SHA-256;
- source class;
- privacy class;
- migration disposition;
- content-transfer class;
- target paths;
- dependencies;
- preserved meaning;
- removed or remodeled meaning;
- collision effects;
- review state;
- and rationale.

## 8. Canonical delta digest

The canonical delta digest is the lowercase SHA-256 of a deterministic UTF-8 JSON serialization.

To compute it:

1. parse the complete delta JSON object;
2. remove the top-level `delta_sha256` member;
3. serialize the remaining object with keys sorted lexicographically;
4. preserve array order;
5. emit no insignificant whitespace;
6. emit Unicode directly rather than ASCII escape substitution;
7. encode the result as UTF-8 without a byte-order mark;
8. compute SHA-256;
9. store the lowercase hexadecimal result in `delta_sha256`.

The required serialization is equivalent to:

```python
json.dumps(
    delta_without_digest,
    ensure_ascii=False,
    sort_keys=True,
    separators=(",", ":"),
).encode("utf-8")
```

Changing array order, path order, or any semantic field changes the digest.

A delta is not accepted when its stored digest does not match independent recomputation.

## 9. Collision-group reconciliation

Every delta must evaluate its changed paths against the current migration collision register.

For each affected collision group, record:

- group ID;
- target path;
- baseline member count;
- resulting provisional member count;
- affected source paths;
- and one or more effects.

Allowed effects are:

- `ADD_MEMBER`;
- `REMOVE_MEMBER`;
- `UPDATE_MEMBER_IDENTITY`;
- `SEMANTIC_DEPENDENCY`;
- `NO_DIRECT_IMPACT`.

A changed source blob within a collision group requires later reconciliation to use the new blob.

A new path provisionally targeting a collision target increases the provisional member count unless later reconciliation selects another route.

A semantic dependency does not change member count by itself.

M0-D records collision impact only. It does not resolve a collision group or authorize target creation.

## 10. Prime target observation

Every delta binds its target observations to one exact `Jktomy/atlas-prime` commit.

For each directly affected proposed target, record:

- target path;
- whether it is present or absent;
- current Git blob when present;
- and clean notes.

Target observation is evidence, not authority.

If Prime `main` changes before a later reconciliation or execution gate, reread the target and bind the new work to the new exact Prime commit.

Do not carry a historical planning base forward as though it were current.

## 11. Migration route selection

Use the route required by current Prime protected-path and source-update controls.

### 11.1 Protected format-contract route

Use a separate format-contract update for:

- migration contracts;
- migration schemas;
- repository-format dependencies;
- and compatible validation fixtures or tests.

### 11.2 Migration-evidence route

Use a migration Preview -> Execute route for:

- baseline manifests;
- ordered delta artifacts;
- migration maps;
- migration audits;
- and clean predecessor-to-successor provenance.

Migration evidence does not become governing doctrine merely because it is complete.

### 11.3 Structured-register route

Active Workboard, Quest Registry, Quest events, Golden Wing, and similar registers require versioned transition contracts and record-level accounting.

### 11.4 Generated rebuild route

Generated projections must be recreated from declared authoritative inputs.

Do not copy stale generated bytes as authored source.

Ordinary generated refresh remains separate from source or migration-evidence pull requests.

### 11.5 Spear-engine route

Spear specifications, policies, tools, tests, fixtures, and workflows remain separate protected engine work.

A migration delta must not activate the writer or broaden operation authority.

## 12. Source and generated separation

A PR governed by this contract must not mix:

- format contracts and migration evidence;
- authored source and ordinary generated output;
- migration evidence and Spear-engine changes;
- private evidence and public clean source;
- source promotion and migration planning;
- or unrelated Project work.

Generated reports may reflect a later source change only through their approved generator route.

A generated-file diff caused solely by a volatile date or equivalent non-semantic field is not sufficient reason to create durable churn.

## 13. M0-D baseline drift reconciliation

M0-D closes only when:

- both repository heads are reverified;
- frozen inventory bytes and the accepted canonical digest independently match;
- the delta schema is merged and read back;
- delta `0001` validates against that merged schema;
- the complete baseline-to-current comparison is reproduced;
- every changed path is represented exactly once;
- effective path and collision counts are reproducible;
- affected target observations are bound to current Prime `main`;
- source and generated consequences are resolved;
- exact changed filenames and full diffs are audited;
- Noctua audits the pinned pull-request heads;
- Jayson manually merges;
- and merged `main` is read back.

M0-D does not create migration targets, resolve the 18 collision groups, create the disposition ledger, or move content.

## 14. Criterion for reopening M1-A

M1-A may receive a new read-only Preview only when:

- the frozen baseline remains intact;
- every required ordered delta through current Codex `main` is accepted;
- the effective inventory has zero unexplained gaps or path collisions;
- collision impacts are incorporated into the current migration map;
- current Prime target observations are verified;
- the Workboard records M0-D completion;
- generated consequences are closed;
- no M0-D `NEEDS_JAYSON` item remains;
- and Jayson separately approves the M1-A Preview.

M1-A reopening does not authorize migration, target replacement, a disposition ledger, S1, promotion, retirement, or cutover.

## 15. Reconciliation and migration closure

Before any migration packet or protected source PR, Athena must complete the applicable reconciliation record using:

`templates/codex-to-prime-reconciliation-record.md`

The record must bind:

- frozen baseline and accepted delta-chain head;
- complete current source reads;
- exact Prime target reads;
- source meaning to preserve;
- contradictions, stale meaning, and privacy boundaries;
- proposed target state;
- selected route;
- tests and recovery;
- unresolved Decision Boxes;
- Noctua requirements;
- and merged-main closure.

A merged target file is not migration closure.

Closure additionally requires inventory and delta lineage, final target readback, disposition-ledger state when that ledger is later authorized, and no unresolved loss.

## 16. Failure behavior

Stop and preserve source when:

- Codex or Prime head changed unexpectedly;
- baseline bytes or digest do not match;
- the delta chain is discontinuous;
- a changed path is missing, duplicated, or ambiguously renamed;
- a normalized or case-only collision appears;
- a target has no safe route;
- a selected route does not permit the target;
- protected evidence is detected;
- complete-file readback or a complete diff is unavailable;
- schema validation fails;
- one member of an atomic set fails;
- migration meaning is unresolved;
- or the proposal includes silent omission, deletion, retirement, supersession, promotion, activation, or cutover.

Do not repair stale evidence by changing only a commit SHA.

Reread, reconcile, regenerate, and present a new Preview.

## 17. Noctua, merge, and recovery

Noctua verifies:

- source order;
- exact repository heads;
- baseline and delta digests;
- effective path coverage;
- collision effects;
- metadata and schema validity;
- private boundaries;
- exact changed filenames;
- complete diffs;
- source and generated separation;
- route compliance;
- tests and reproducibility;
- pull-request lineage;
- manual merge;
- and merged-main readback.

A Noctua `YES` does not authorize execution or merge by itself.

Before merge, recovery is closing the unmerged pull request.

After merge, recovery is a separately reviewed narrow revert that preserves the frozen baseline and predecessor contracts.

## 18. S1, promotion, and cutover boundaries

This contract does not activate S1.

The presence of disabled writer implementation, passing tests, a valid delta, or a complete migration map does not grant repository-write authority.

Prime may become `CUTOVER_CANDIDATE` only after complete effective Codex accounting, zero unexplained gaps, closed or explicitly blocked dispositions, proven Workboard continuity, source and generated verification, writer pilots, repository-wide Noctua audit, Phoenix Reborn backup and isolated restore, rollback proof, and updated startup and source-order files.

Prime becomes `CANONICAL` only through explicit Jayson approval.

## 19. Acceptance criteria

This contract is acceptable when it:

- preserves the frozen 349-entry baseline without modification;
- defines ordered versioned delta accounting;
- preserves zero-silent-loss lineage for additions, modifications, removals, and renames;
- defines deterministic delta digests;
- requires effective path and collision accounting;
- separates format, migration evidence, Spear-engine, structured-register, and generated routes;
- keeps Atlas Codex canonical and Atlas Prime `SHADOW`;
- grants no writer, migration, promotion, retirement, or cutover authority;
- and blocks M1-A until M0-D is fully merged, audited, and read back.
