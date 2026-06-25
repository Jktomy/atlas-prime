---
title: Spear S0 Operator Runbook
atlas_id: spear.s0.operator-runbook
format_version: "1.0"
status: PROPOSED
source_type: TOOL_DOCUMENTATION
authority_class: TOOL_CONTRACT
owner_project: Codex
owner_operation: Athena's Spear
canonical_scope: Provides operator guidance for the proposed Athena's Spear S0 offline compiler without authorizing repository writes or workflow activation.
protected_level: HIGH
routes_from:
  - athenas-spear.md
routes_to:
  - tools/spear/cli.py
  - tools/spear/dependencies-v1.toml
private_boundary: This runbook may describe clean operational procedure only and must not include credentials, tokens, private runtime facts, or protected evidence.
evidence_boundary: Test receipts and generated compiler outputs are external review evidence and are not authored source in this runbook.
supersedes: []
cleanup_path: Update through a separately reviewed Spear engine documentation PR; ordinary S0 packets must not modify Spear tooling documentation.
last_verified: 2026-06-24
---

# Spear Operator Runbook S0 v4

S0 is dry-run only.

Required CLI inputs:

- packet JSON file or Base64 packet;
- exact decoded packet transport SHA-256;
- packet schema;
- Spear overlay policy;
- target Atlas Prime repository;
- base ref `main`;
- external output root.

The compiler validates real Git state before producing a plan. It resolves `main`, verifies it equals the packet `base_commit`, then reads controlling Prime policies and the source-metadata schema from that same repository and exact commit. CREATE requires real target absence at the pinned base commit. REPLACE requires the target to be a regular blob whose Git object SHA equals `expected_blob_sha`.

Dependencies are declared in `tools/spear/dependencies-v1.toml`. The dependency contract is not an installer and grants no network authority.

Every S0 receipt states `EXECUTION_NOT_AUTHORIZED`.