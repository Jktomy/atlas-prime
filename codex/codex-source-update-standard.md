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
  verification, cleanup, and post-merge readback.
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
  repository format or Spear transaction semantics change; do not fork competing update
  standards.
last_verified: '2026-06-21'
---

# Atlas Prime Source Update Standard

## Core rule

```text
No orphan source.
Every durable behavior change needs:
source + ownership + routing hook + verification readback + cleanup or supersession path.
```

This standard preserves the strongest controls from the canonical Codex source-update and Emberline workflows while aligning them to Atlas Prime and Spear v0.3.

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
- private pointer.

The classification determines metadata, route requirements, write lane, generator rules, protected-path controls, and migration treatment.

## Required source-update sequence

1. Read the current explicit Jayson instruction.
2. Read the current target from the exact base commit.
3. Read related routes, policies, schemas, and protected boundaries.
4. Classify create, complete replacement, structured operation, generated refresh, migration, or proposal-only work.
5. Prepare a complete Preview.
6. Obtain explicit bounded Execute approval when required.
7. Revalidate the exact base and target hashes.
8. Create one narrow branch from the verified base.
9. Apply only the approved changes.
10. Run syntax, schema, policy, link, route, privacy, and test checks.
11. Audit exact changed filenames and the complete diff.
12. Open one scoped draft PR and stop before merge.
13. Noctua verifies the audited head commit.
14. Jayson manually merges.
15. Read back merged `main` and verify routing and generated consequences.
16. Update migration or transaction lineage when applicable.
17. Report changed, skipped, blocked, failed, and deferred items honestly.

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
- tests and acceptance criteria;
- runtime and external-system impact;
- rollback or recovery posture;
- deferred items;
- exact next approval gate.

## Metadata and routing

Authored Markdown MUST validate against `schemas/source-metadata/source-metadata-v1.schema.json`.

Every durable behavior source needs at least one discoverable inbound route unless it is an approved root bootstrap source. Outbound routes MUST use repository-relative paths and MUST NOT pretend planned files are already active.

If routing is incomplete, the change MUST be reported as:

```text
Durable storage proposed, but routing incomplete.
```

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
- use a versioned Spear complete-file operation only after that operation is independently approved and proven.

## Complete-file replacement controls

`REPLACE_FILE_FULL` requires at least:

- exact current Git object and content hash;
- complete replacement bytes;
- exact replacement hash;
- metadata validation;
- required-heading inventory;
- declared removals and rationale;
- route-link preservation or explicit route change;
- protected-term and private-boundary review;
- deletion-percentage warning;
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

Athena decides semantic deltas. Spear applies only versioned high-level registered operations.

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

## Connector full-file replacement rule

A connector action that replaces an entire file is a complete-file replacement path even when the intended change is small.

If a connector blocks once:

1. stop immediately;
2. do not retry the same risky payload in the same run;
3. preserve existing source;
4. continue only with separable safe work;
5. use a complete local Preview, branch/PR route, or support-file route;
6. report the block honestly.

## Branch and PR controls

- one narrow branch per source PR;
- branch starts from the exact verified base commit;
- no direct `main` write;
- no force push;
- no automated merge;
- no branch reuse for a revised Spear transaction;
- exact changed filenames audited;
- PR head commit pinned for Noctua review;
- source PR separated from ordinary generated refresh;
- manual Jayson merge;
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
- the proposal attempts silent promotion, supersession, or deletion;
- a normal packet targets Spear, Phoenix Reborn, policies, schemas, workflows, or tests outside its approved route.

Diagnostics MUST redact protected matches.

## Cleanup and supersession

Every pilot, support, transitional, or predecessor source needs a declared path:

- keep;
- merge;
- remodel;
- regenerate;
- supersede;
- retire;
- archive as historical;
- replace with a private pointer.

No source is deleted merely because a successor exists. Replacement routing, migration closure, retention needs, and explicit approval come first.
