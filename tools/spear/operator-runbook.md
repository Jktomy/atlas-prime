---
title: Spear S0/S1 Operator Runbook
atlas_id: spear.s0-s1.operator-runbook
format_version: "1.0"
status: PROPOSED
source_type: TOOL_DOCUMENTATION
authority_class: TOOL_CONTRACT
owner_project: Codex
owner_operation: Athena's Spear
canonical_scope: Provides operator guidance for the Atlas Prime Spear S0 offline compiler and the source-hard-disabled A3b S1 draft-PR writer implementation without authorizing workflow activation, packet execution, migration, promotion, merge, or cutover.
protected_level: HIGH
routes_from:
  - athenas-spear.md
routes_to:
  - tools/spear/cli.py
  - tools/spear/s1_cli.py
  - tools/spear/s1_writer.py
  - tools/spear/s1_receipts.py
  - tools/spear/dependencies-v1.toml
  - tools/spear/recovery-runbook.md
  - .github/workflows/spear-s1-draft-pr-writer.yml
private_boundary: This runbook may describe clean operational procedure only and must not include credentials, tokens, private runtime facts, raw account evidence, PHI, or protected exports.
evidence_boundary: Test receipts, generated compiler outputs, package manifests, and migration evidence remain external review evidence and are not authored source in this runbook.
supersedes: []
cleanup_path: Update through a separately reviewed Spear engine documentation PR; ordinary S0 packets must not modify Spear tooling documentation.
last_verified: 2026-06-26
---

# Spear Operator Runbook S0/S1 v4

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

## A3b S1 implementation posture

A3b adds a bounded draft-PR writer implementation and regression suite, but it does not activate repository mutation.

Current safety state:

- `S1_APPLY_HARD_DISABLED` remains enforced in source;
- the workflow APPLY job remains `if: ${{ false }}`;
- the hosted workflow PLAN job emits a bounded blocked receipt because the dependency route is not authorized;
- the S1 activation policy remains `PROPOSED`, `DISABLED`, and write authority remains false;
- no packet execution, branch creation, push, draft PR, merge, migration, promotion, retirement, or cutover is authorized.

A future activation requires a separate exact Preview -> Execute decision, successful Noctua review, harmless proof, recovery proof, and explicit Jayson authorization.

### S1 planning inputs

The disabled S1 CLI additionally requires an injected authenticated observation timestamp. It binds the exact packet bytes, Preview hash, manifest hash, base commit, actor, workflow commit, run identity, controlling contracts, target state, deterministic branch, deterministic commit metadata, and exact draft-PR metadata before returning a disabled receipt.

Do not treat a successful A3b test or plan as activation.

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

## A3b disabled S1 writer preview route

A3b introduces a disabled writer implementation candidate for review. It does not activate S1.

The disabled route may validate an S1 execution envelope, construct a logical plan, emit a bounded receipt, and prove fake-backed transaction behavior in tests. It must not be used as live migration or write authority.

Operator boundaries:

- APPLY is source-level hard-disabled.
- The workflow remains dependency-blocked pending a separately reviewed dependency route.
- The activation policy remains disabled.
- The destination policy grants no repository write authority.
- Atlas Codex remains canonical.
- Atlas Prime remains SHADOW until explicit promotion and cutover.
- No packet may select commands, branches, credentials, workflows, or runner behavior.

The disabled writer candidate must preserve:

- repository plus packet ID as the concurrency and idempotency identity;
- exact branch derivation from target repository plus packet ID;
- exact packet ID agreement between workflow input, envelope, and decoded packet;
- remote-main recheck before branch creation, before commit/ref write, and before PR creation;
- exactly one parent commit with exact full commit message;
- `github-actions[bot] <41898282+github-actions[bot]@users.noreply.github.com>` as author and committer;
- exact PR title, complete body, base, head, draft state, and head SHA readback;
- one schema-valid redacted receipt for every failed or successful attempt.

No operator may treat a disabled A3b Preview as permission to create a live branch, push, open a pull request, bypass Noctua, merge, migrate, promote, retire Atlas Codex, or perform cutover.
