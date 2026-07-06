---
title: Atlas Prime Source Update Standard
atlas_id: atlas-prime.codex.source-update-standard
format_version: '1.0'
status: PROPOSED
source_type: STANDARD
authority_class: CANONICAL_AUTHORED_SOURCE
owner_project: Codex
owner_operation: Source Governance
canonical_scope: Durable source-update procedure for routing, metadata, complete readback,
  protected-file reconstruction, source/generated separation, migration lineage, pull-request
  verification, cleanup, retention, supersession, and post-merge readback.
protected_level: CRITICAL
routes_from:
- README.md
- atlas-prime.md
- atlas-aegis.md
- specs/atlas-prime/repository-format-v1.md
routes_to:
- schemas/source-metadata/source-metadata-v1.schema.json
- policies/destination/atlas-prime-destination-policy-v0.2.yaml
- policies/protected-paths/protected-paths-v0.2.yaml
private_boundary: Do not store secrets, credentials, tokens, MFA or recovery codes,
  private keys, seed phrases, real .env values, PHI, raw finance or account evidence,
  private runtime values, IP addresses, network maps, device registers, protected
  exports, or other raw protected evidence in GitHub.
evidence_boundary: Original evidence systems remain authoritative outside GitHub.
  Atlas Prime stores only clean source, clean summaries, structured clean state, generated
  projections, migration provenance, and clean pointers.
supersedes: []
cleanup_path: Keep as the durable source-update standard. Version explicitly when
  repository format or approved change-path semantics change; do not fork competing update
  standards.
last_verified: '2026-07-06'
---

# Atlas Prime Source Update Standard

## Core rule

```text
No orphan source.
Every durable behavior change needs:
source + ownership + routing hook + verification readback + cleanup or supersession path.
```

This standard preserves the strongest controls from canonical Codex source-update governance while aligning them to Atlas Prime as a proposed shadow repository. Emberline remains the independent Quest/Campaign status model; Reforge is the direct Preview route for doctrine reconciliation.

Codex remains canonical until a separately approved cutover. Prime remains `PROPOSED / SHADOW`. This standard may define source-update safety for Prime candidates, but it does not promote Prime, retire Codex, migrate source, activate a writer, or grant merge authority.

## Emberline and Reforge boundary

Emberline reports the unified Quest/Campaign roadmap, current state, completed and unfinished gates, blockers, dependencies, protected boundaries, provenance, and next safe action.

Emberline may identify stale status or source drift. It is not a generic multi-file source-update engine and does not itself write, merge, migrate, promote, delete, retire, activate, or cut over.

Reforge is the independent direct doctrine-reconciliation route. `REFORGE — [topic]` produces an exact Preview candidate for conflicting or stale doctrine. Reforge does not itself execute the resulting source transaction or expand actor authority.

## Authority boundary

Interface, workflow, implementation, proof, maturity, registry presence, command status, successful tests, or clean Noctua result is not source, execution, merge, migration, retirement, promotion, deletion, cleanup, or cutover authority.

Build never grants Execute. Noctua `YES` means the audited candidate satisfies its stated criteria; it does not authorize mutation, merge, retirement, cutover, or permanence. Jayson retains final merge and permanence authority.

Naming Spear, Arrow, Bow, Thread Engine, Sword, workflow, connector, script, adapter, or another construction mechanism does not activate that mechanism or select it for a transaction. Each construction route needs its own current approved change-path contract, exact base, declared path set, transaction authority, proof, and stop boundary.

This standard creates no standing writer, background service, automatic ready transition, automatic merge, automatic cleanup, repository setting change, migration authority, deletion authority, retirement authority, or cutover authority.

## Classification before change

Every created or modified path MUST be classified as one of:

- bootstrap or restart source;
- canonical doctrine or protocol;
- standard, specification, policy, or schema;
- Project or Operation source;
- structured authoritative register;
- generated operational projection;
- continuity or historical provenance;
- migration evidence;
- tool implementation or test;
- support, pilot, transitional, compatibility, or predecessor source;
- private pointer.

The classification determines metadata, route requirements, write lane, generator rules, protected-path controls, retention treatment, and migration treatment.

## Required source-update sequence

1. Read the current explicit Jayson instruction.
2. Read the current target from the exact base commit without truncation.
3. Read related routes, policies, schemas, protected boundaries, predecessor records, and current repository state.
4. Classify create, complete replacement, structured operation, generated refresh, migration, proposal-only work, support or transitional source handling, or a doctrine contradiction requiring a separate Reforge Preview.
5. Prepare a complete Preview.
6. Obtain explicit bounded Execute approval when required.
7. Revalidate the exact base, target Git object, content hash, branch state, PR state, and declared path set.
8. Create one narrow branch from the verified base.
9. Apply only the approved changes.
10. Run syntax, schema, policy, link, route, privacy, source/generated, metadata, diff, and applicable test checks.
11. Audit exact changed filenames, complete current bytes, complete candidate bytes, complete unified diff, declared removals, and replacement hashes.
12. Open one scoped draft PR and stop before merge unless the Execute explicitly authorizes a later ready or merge transaction.
13. Read back exact PR title, body, draft state, base, head branch, head SHA, commit set, file set, comments, reviews, review threads, and checks.
14. Noctua verifies the audited head commit and readback.
15. Jayson controls merge directly or through a separately approved exact Execute Arrow bound to the audited PR head.
16. Read back merged `main` and verify routing, generated consequences, and declared non-source consequences.
17. Update migration or transaction lineage when separately authorized and applicable.
18. Report changed, skipped, blocked, failed, and deferred items honestly.

## Preview requirements

A complete Preview identifies:

- repository and expected base commit;
- exact paths;
- create/update/delete status;
- complete proposed contents or deterministic operation inputs;
- exact before hashes for existing targets;
- expected after hashes;
- full changed-filename list;
- complete unified diff;
- metadata and routing changes;
- protected-boundary impact;
- source/generated impact;
- migration disposition impact;
- support, transitional, predecessor, cleanup, and retention impact;
- tests and acceptance criteria;
- runtime and external-system impact;
- rollback or recovery posture;
- deferred items;
- blockers and uncertainties;
- exact next approval gate.

## Metadata and routing

Authored Markdown MUST validate against `schemas/source-metadata/source-metadata-v1.schema.json`.

Every durable behavior source needs at least one discoverable inbound route unless it is an approved root bootstrap source. Outbound routes MUST use repository-relative paths and MUST NOT pretend planned files are already active.

A support, pilot, transitional, compatibility, or predecessor source MUST identify:

- owner;
- status;
- parent, related, or routed sources;
- routes from and routes to where applicable;
- protected and private boundary;
- evidence boundary;
- successor, cleanup, merge, promotion, retention, or supersession path.

If routing is incomplete, the change MUST be reported as:

```text
Durable storage proposed, but routing incomplete.
```

## Support, transitional, and predecessor source retention

Support, pilot, transitional, compatibility, and predecessor sources remain active or preserved until their successor, routing, evidence, recovery, and explicit disposition have been proven and approved.

A clean pointer, summary, successor, copied meaning, consolidated target, or proposed replacement does not authorize deletion, retirement, supersession execution, archive destruction, evidence destruction, branch deletion, or cleanup.

A predecessor is retirement-ready only after an explicit Preview identifies the predecessor path, preserved content, omitted content, successor route, evidence retention, rollback or restore path, migration lineage, and exact approval gate. The default disposition is retain.

## Large protected file rule

A protected source includes any file that defines source order, command behavior, safety, evidence handling, recovery, migration, automation, finance, health, identity, deletion, archive, retirement, or tool authority.

Do not perform complete-file replacement when any of these are true:

- the complete current target cannot be read;
- the tool output is truncated;
- unrelated guardrails cannot be compared;
- the reconstruction could drop, reorder, or weaken protected doctrine;
- the available path cannot show a reliable full diff;
- source state is stale or ambiguous;
- the change contains undeclared removals.

Safe routes include:

- keep an active routed support file;
- use a local clone or complete local Preview package;
- use a branch/PR workflow with full diff;
- split a large source into approved smaller canonical modules;
- use a versioned complete-file operation only after that operation is independently approved and proven.

## Complete-file replacement controls

`REPLACE_FILE_FULL` requires at least:

- exact current Git object and content hash;
- complete current bytes;
- complete replacement bytes;
- exact replacement Git object and content hash;
- UTF-8 and line-ending validation;
- metadata validation;
- required-heading inventory;
- declared removals and rationale;
- route-link preservation or explicit route change;
- protected-term and private-boundary review;
- deletion-percentage calculation and warning when applicable;
- complete diff;
- temporary-tree validation;
- Noctua audit;
- Jayson manual merge.

A full replacement is a mechanism, not semantic authority.

## Source and generated separation

Ordinary generated reports, inventories, and dashboards MUST be refreshed in a separate generated-output PR after source merge.

The initial exception is `codex/atlas-quest-board.md`, which MAY be regenerated atomically with the exact Quest Registry and Quest Event update that defines it. The generator contract MUST identify authoritative inputs, deterministic output, source commit, and receipt.

Direct manual edits to generated projections are forbidden.

## Structured authoritative registers

Structured registers use stable IDs, schema validation, expected record versions, deterministic serialization, append-only event history where defined, and atomic projection regeneration.

Athena may decide semantic deltas only inside the current authority boundary. A construction mechanism applies only the versioned high-level registered operation it is explicitly authorized to apply.

## Migration updates

Every tracked predecessor path receives exactly one explicit disposition:

- `MIGRATE`
- `MERGE`
- `REMODEL`
- `GENERATED_REBUILD`
- `HISTORICAL_REFERENCE`
- `PRIVATE_POINTER`
- `SUPERSEDE`
- `RETIRE`
- `OMIT_WITH_REASON`

Migration records MUST preserve source path and hashes, target paths, preserved elements, removed or remodeled elements, dependencies, replacement routing, packet/PR/commit lineage, Noctua result, and final state.

`OMIT_WITH_REASON`, `SUPERSEDE`, `RETIRE`, and `PRIVATE_POINTER` require explicit rationale and the applicable approval. Prohibited raw evidence may not be copied merely to achieve inventory completeness.

A migration map, disposition ledger, or semantic reconciliation Preview does not itself execute migration, retirement, deletion, source promotion, generated refresh, or cutover.

## Connector full-file replacement rule

A connector action that replaces an entire file is a complete-file replacement path even when the intended change is small.

Do not use connector full-file replacement for a large protected file while a safer path exists.

If a connector blocks once:

1. stop the blocked action immediately;
2. do not retry the same blocked route with alternate wording in the same run;
3. do not fragment an atomic transaction merely to bypass the block;
4. preserve existing source, partial state, and provenance;
5. continue only with separable safe work;
6. use only a currently approved supported route, such as complete local Preview, branch/PR route, or support-file route;
7. report the block honestly.

An issue, status record, or tracking note may document the block, but it grants no execution, write, merge, retirement, deletion, or cleanup authority.

## Branch and PR controls

- one narrow branch per source PR;
- branch starts from the exact verified base commit;
- no direct `main` write;
- no force push;
- no automated merge;
- no branch reuse for a revised transaction unless explicitly approved;
- exact changed filenames audited;
- PR head commit pinned for Noctua review;
- PR title and body constructed as exact literal UTF-8;
- PR title, body, draft state, base branch, base SHA, head branch, head SHA, commits, changed files, comments, reviews, review threads, requested reviewers, and checks read back exactly;
- metadata-only repair preserves the audited head commit and file set;
- corrupted, ambiguous, or mismatched PR metadata blocks approval;
- source PR separated from ordinary generated refresh;
- Jayson-controlled manual merge or separately approved exact Execute Arrow;
- post-merge `main` readback required.

## Failure behavior

Block when:

- source state changed;
- path or ownership is ambiguous;
- policy version mismatches;
- protected content is detected;
- route validation fails;
- one file in an atomic set is invalid;
- a generated file is edited directly;
- a Preview or Execute attempts to infer authority from maturity, status, interface, proof, or command availability;
- the proposal attempts silent promotion, supersession, retirement, deletion, cleanup, or cutover;
- the proposal treats Emberline as a generic source-update engine or Reforge as execution authority;
- the proposal treats this standard as activation authority for a writer, workflow, connector, Spear, Thread Engine, Sword, Arrow, Bow, migration engine, or cleanup mechanism;
- a normal packet targets protected policies, schemas, workflows, tests, runtime topology, or infrastructure outside its approved route.

Diagnostics MUST redact protected matches.

## Cleanup and supersession

Every pilot, support, transitional, compatibility, or predecessor source needs a declared path:

- keep;
- merge;
- remodel;
- regenerate;
- supersede;
- retire;
- archive as historical;
- replace with a private pointer.

No source is deleted merely because a successor exists. Replacement routing, migration closure, retention needs, recovery needs, evidence preservation, and explicit approval come first.

## C07 predecessor disposition

This C07 candidate preserves selected source-update meaning from the five Codex predecessor members without retiring them:

- `atlas-tool-lifecycle.md`: preserve that maturity, interface, protocol, command, implementation, or registry status is not authority; preserve explicit promotion and retirement gates; do not import the live registry.
- `codex/atlas-ember-line-alignment.md`: preserve that replacement, retention, backup, restore, and retirement gates remain separate; do not import historical naming-output doctrine.
- `codex/codex-source-update-standard.md`: preserve no-orphan source discipline, support-file handling, protected reconstruction, connector block behavior, cleanup accounting, and no blind fragmentation.
- `emberline-sop.md`: keep Emberline independent, read-only, and active; do not absorb the full protocol here.
- `github-pr-workflow.md`: preserve PR metadata as approval-critical evidence and metadata-only repair constraints; do not import direct-main exceptions or stale generated-report implementation detail.

All five predecessors remain retained and are not retirement-ready merely because this candidate exists.

## Exclusions

This standard does not import runtime-placement doctrine or infrastructure topology. It does not define Prometheus, Crucible, Nexus, Matrix, Forge, Plex, Helios, Notum, Nightwatcher, or other runtime deployment responsibilities.

It does not activate, configure, or authorize external systems, Drive, finance, account, health, runtime, automation, infrastructure, or private evidence actions.
