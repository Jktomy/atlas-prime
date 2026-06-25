---
title: Athena's Spear S0 Offline Compiler Proposal
atlas_id: spear.s0.offline-compiler
format_version: "1.0"
status: PROPOSED
source_type: PROTOCOL
authority_class: CANONICAL_AUTHORED_SOURCE
owner_project: Codex
owner_operation: Athena's Spear
canonical_scope: Defines the proposed probationary S0 offline compiler contract for Athena's Spear in Atlas Prime without granting writer activation.
protected_level: CRITICAL
routes_from:
  - specs/spear/athenas-spear-spec-v0.2.md
  - schemas/spear/athenas-spear-packet-v0.2.schema.json
  - tests/fixtures/spear/corpus-v0.2.md
routes_to:
  - schemas/spear/spear-packet-v1.schema.json
  - policies/operations/spear/spear-policy-v1.yaml
  - tools/spear/cli.py
private_boundary: This source must contain only clean protocol text and must not include secrets, private runtime values, raw account evidence, PHI, or protected exports.
evidence_boundary: This file is authored source; generated receipts, test logs, and review package manifests remain external review evidence until separately approved.
supersedes: []
cleanup_path: Update through a separately reviewed Spear engine or protocol PR; do not alter through ordinary S0 packets.
last_verified: 2026-06-24
---

# Athena's Spear MVP S0 v4

Status: PROBATIONARY offline compiler proposal.

S0 receives one bounded structured packet, validates it against schema, overlay policy, pinned Atlas Prime destination policy, pinned protected-path policy, pinned source-metadata schema, and real Git base state, then emits review evidence only.

S0 supports only registered Prime operations:

- `CREATE_FILE`
- `REPLACE_FILE_FULL`

S0 derives controlling policy and source-metadata schema only from the same target repository at the already-verified packet base commit. S0 does not execute. Every compiled plan records `EXECUTION_NOT_AUTHORIZED`.

## Predecessor continuity

The merged Spear v0.2 files remain predecessor design and historical/reference evidence:

- `specs/spear/athenas-spear-spec-v0.2.md`
- `schemas/spear/athenas-spear-packet-v0.2.schema.json`
- `tests/fixtures/spear/corpus-v0.2.md`

S0 v4 is the current probationary offline compiler proposal. Neither v0.2 nor S0 v4 grants writer activation. S1 remains separately gated and requires a later explicit Preview -> Execute approval.
