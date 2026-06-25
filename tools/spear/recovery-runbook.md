---
title: Spear S0 Recovery Runbook
atlas_id: spear.s0.recovery-runbook
format_version: "1.0"
status: PROPOSED
source_type: TOOL_DOCUMENTATION
authority_class: TOOL_CONTRACT
owner_project: Codex
owner_operation: Athena's Spear
canonical_scope: Defines non-mutating recovery guidance for failed Athena's Spear S0 offline compiler validation and review package work.
protected_level: HIGH
routes_from:
  - athenas-spear.md
  - tools/spear/operator-runbook.md
routes_to:
  - tools/spear/cli.py
private_boundary: This recovery runbook must not include credentials, private runtime values, raw account evidence, PHI, or protected exports.
evidence_boundary: Recovery evidence belongs in external review artifacts or separately approved receipts, not inline in this authored source.
supersedes: []
cleanup_path: Update through a separately reviewed Spear engine documentation PR; do not use ordinary S0 packets for Spear self-modification.
last_verified: 2026-06-24
---

# Spear Recovery Runbook S0 v4

S0 has no repository mutation capability.

If validation fails:

- inspect the error category;
- do not infer absence from a Git failure;
- do not substitute policy repositories, policy commits, or source-metadata schemas;
- correct the packet or proposed source through a later reviewed package;
- do not branch, push, retry as execution, delete, or force-push.

Future S1 recovery remains separate. If a future branch push succeeds but draft PR creation fails, Spear must stop, report branch and commit, and require explicit Jayson recovery direction.