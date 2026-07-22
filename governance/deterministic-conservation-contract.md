---
title: "Deterministic Projection Diagnostics Contract"
atlas_id: "prime.governance.deterministic-conservation-contract"
status: "CANONICAL_ACTIVE"
source_type: "PROTOCOL"
authority_class: "CANONICAL_AUTHORED_SOURCE"
owner_project: "Project Codex"
owner_operation: "Operation Source Governance"
protected_level: "CRITICAL"
---

# Deterministic projection diagnostics

Prime's five Markdown inventory functions are deterministic, nonauthoritative
diagnostics. Ordinary validation builds them twice from canonical authored
Markdown, evaluates them in temporary storage, verifies byte-identical readback,
and emits one machine-readable receipt containing the source fingerprint and
the ordered path, size, and SHA-256 of every diagnostic. A clean clone needs no
committed projection files to reproduce this proof.

The active tree does not retain the five reports. Their former `generated/`
paths do not govern, are not recovery inputs, and must not be introduced by an
authored candidate. Routine authored merges therefore need no generated-only
follow-up branch, pull request, READY transition, or merge.

The ordinary `prime/integrity` validation path runs the diagnostic on every
candidate. A malformed source, invalid UTF-8 input, output-set drift, repeated
build mismatch, or temporary readback mismatch returns a nonzero result and a
machine-readable `atlas.generated-projection-diagnostics.v1` failure receipt.
Applicable candidate changes still receive conditional Windows validation under
the normal changed-path planner; the diagnostic itself creates no standing
cross-platform publication cycle.

The former hosted `GENERATED_CHECKPOINT_V1` workflow and its owner-dispatch
publication route are retired from active operation. Historical proof, receipts,
lifecycle records, migration ledgers, Git history, and dormant compatibility
implementation remain unchanged and nonauthoritative. They prove what the old
route did; they do not authorize dispatch, publication, runtime deployment, or
restoration of routine generated-file permanence.

Explicit materialization remains a local noncanonical inspection facility and
must target a declared output directory. It cannot write `main`, create a branch
or pull request, change settings, advance a Quest, promote a capability, or
become a repository writer. Coppermind and Glass Codex may later consume
exact-commit-bound, stale-aware, replaceable projections, but this contract
deploys neither service and grants neither system canonical authority.
