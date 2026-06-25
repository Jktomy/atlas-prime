---
title: Spear S0 Operator Runbook
atlas_id: spear.s0.operator-runbook
format_version: "1.0"
status: PROPOSED
source_type: TOOL_DOCUMENTATION
authority_class: TOOL_CONTRACT
owner_project: Codex
owner_operation: Athena's Spear
canonical_scope: Provides operator guidance for the proposed Atlas Prime Spear S0 offline migration compiler without authorizing repository writes, workflow activation, migration, or cutover.
protected_level: HIGH
routes_from:
  - athenas-spear.md
routes_to:
  - tools/spear/cli.py
  - tools/spear/dependencies-v1.toml
  - tools/spear/recovery-runbook.md
private_boundary: This runbook may describe clean operational procedure only and must not include credentials, tokens, private runtime facts, raw account evidence, PHI, or protected exports.
evidence_boundary: Test receipts, generated compiler outputs, package manifests, and migration evidence remain external review evidence and are not authored source in this runbook.
supersedes: []
cleanup_path: Update through a separately reviewed Spear engine documentation PR; ordinary S0 packets must not modify Spear tooling documentation.
last_verified: 2026-06-25
---

# Spear Operator Runbook S0 v4

S0 is a dry-run compiler and validator only.

Atlas Codex remains canonical. Atlas Prime is the next-generation target under construction. S0 does not perform migration, repository mutation, source promotion, or cutover.

## Before preparing a packet

Athena must complete a read-only reconciliation pass:

1. read the relevant current source from `atlas-codex/main`;
2. read the complete current target files from `atlas-prime`;
3. review relevant harvests, approved decisions, chat context, Noctua findings, migration maps, rejected approaches, Workboard items, and unresolved Decision Boxes;
4. classify content as preserve, reorganize, update, replace, add, retire, retain as history, defer, or exclude;
5. resolve or surface conflicts between current canonical Codex and proposed Prime source;
6. choose full-file replacement or a bounded surgical operation based on safety and clarity;
7. prepare an exact packet and Preview.

Do not create a packet from memory alone, an old summary, a stale SHA, or an earlier package.

## Full-file replacement preparation

For a proposed `REPLACE_FILE_FULL` operation:

- read the complete current target file;
- compute and record its exact Git blob SHA;
- prepare the complete replacement text;
- deliberately preserve or explicitly supersede valid current material;
- produce and review the complete old-to-new diff;
- verify source metadata and protected boundaries;
- fail closed if the current file is incomplete, stale, private, protected, ambiguous, or not safely reviewable.

S0 validates and plans the replacement but does not apply it.

## Required CLI inputs

- packet JSON file or Base64 packet;
- exact decoded-packet transport SHA-256;
- target Atlas Prime repository;
- optional Atlas Codex repository path used only to protect that checkout from output-root placement;
- base ref `main`;
- absent or empty external output root.

The packet schema and Spear overlay policy are not caller-selected inputs.

S0 loads these fixed paths from the target Atlas Prime repository at the packet's exact `base_commit`:

- `schemas/spear/spear-packet-v1.schema.json`
- `policies/operations/spear/spear-policy-v1.yaml`

S0 also loads the destination policy, protected-path policy, and source-metadata schema from that same repository and commit.

## Invocation shape

From the Atlas Prime repository root:

```text
python -m tools.spear.cli \
  --packet <packet.json> \
  --packet-sha256 <decoded-packet-sha256> \
  --repository <atlas-prime-checkout> \
  --atlas-codex-repository <atlas-codex-checkout> \
  --base-ref main \
  --output-root <absent-or-empty-external-directory>
```

Use `--packet-b64` instead of `--packet` only when the packet is supplied as Base64. Provide exactly one packet transport.

Do not install or update dependencies as part of an S0 run. Dependencies are declared in `tools/spear/dependencies-v1.toml`; that file is a contract, not an installer, and grants no network authority.

## Validation sequence

The compiler:

1. verifies the target checkout is a Git repository;
2. verifies the output root is outside protected repositories;
3. parses the exact packet bytes and verifies the transport SHA-256;
4. requires base ref `main`;
5. resolves `main` and requires it to equal packet `base_commit`;
6. loads the pinned packet schema, overlay, destination policy, protected-path policy, and source-metadata schema from that commit;
7. validates packet structure, authority claims, limits, actions, paths, metadata, content, protected boundaries, and source-type consistency;
8. reads real Git base state for every operation;
9. requires real target absence for `CREATE_FILE`;
10. requires exact expected blob identity for `REPLACE_FILE_FULL`;
11. emits deterministic review artifacts only.

## Output artifacts

A successful S0 run writes:

- `normalized-packet.json`
- `operation-manifest.json`
- `validation-receipt.json`
- `proposed-tree/`

The output root must be external, absent or empty, and outside Atlas Prime and Atlas Codex checkouts.

Review artifacts do not become source truth automatically.

Every S0 receipt must state:

```text
EXECUTION_NOT_AUTHORIZED
```

## Review gate

Before any future execution phase may apply an S0 plan, Athena must present an exact Preview containing:

- target files;
- old and new hashes;
- complete replacement text or bounded operation;
- complete diff;
- additions and deletions;
- source-truth implications;
- metadata and protected-boundary findings;
- tests;
- expected branch, commit, and draft-PR shape;
- recovery instructions;
- and unresolved decisions.

Jayson must explicitly approve that exact Preview.

S0 itself cannot stage, commit, push, open a PR, merge, migrate, promote source, or activate writer authority.
