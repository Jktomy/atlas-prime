---
title: Spear S0/S1 Recovery Runbook
atlas_id: spear.s0-s1.recovery-runbook
format_version: "1.0"
status: PROPOSED
source_type: TOOL_DOCUMENTATION
authority_class: TOOL_CONTRACT
owner_project: Codex
owner_operation: Athena's Spear
canonical_scope: Defines non-mutating recovery guidance for failed Atlas Prime Spear S0 validation and source-hard-disabled A3b S1 planning, replay, receipt, branch, commit, and draft-PR verification paths.
protected_level: HIGH
routes_from:
  - athenas-spear.md
  - tools/spear/operator-runbook.md
routes_to:
  - tools/spear/cli.py
  - tools/spear/s1_cli.py
  - tools/spear/s1_writer.py
  - tools/spear/s1_receipts.py
  - .github/workflows/spear-s1-draft-pr-writer.yml
private_boundary: This recovery runbook must not include credentials, private runtime values, raw account evidence, PHI, or protected exports.
evidence_boundary: Recovery evidence belongs in external review artifacts or separately approved receipts, not inline in this authored source.
supersedes: []
cleanup_path: Update through a separately reviewed Spear engine documentation PR; do not use ordinary S0 packets for Spear self-modification.
last_verified: 2026-06-26
---

# Spear Recovery Runbook S0/S1 v4

S0 has no repository mutation capability.

Atlas Codex remains canonical while Atlas Prime is being built. A failed S0 run must not be treated as migration authority or as permission to bypass the current source order.

## General failure rule

When validation or compilation fails:

- inspect and preserve the exact error category;
- make no repository change;
- do not infer target absence from a Git read failure;
- do not substitute repositories, base commits, schemas, policies, or source-metadata contracts;
- do not weaken protected-path or metadata rules;
- do not retry through a different write route in the same run after a connector or safety block;
- correct the packet, proposed source, or reconciliation plan through a later reviewed Preview;
- do not branch, stage, commit, push, create a PR, delete, reset, or force-push.

## Stale source or base

If `main` no longer equals packet `base_commit`, stop.

Athena must:

1. reread current `atlas-codex/main` source relevant to the migration;
2. reread current Atlas Prime target files;
3. rebuild the reconciliation map;
4. recompute expected blob SHAs and replacement content;
5. present a new Preview.

Do not reuse a packet merely by replacing its base SHA.

## Missing or changed controlling contract

If a pinned schema, overlay, destination policy, protected-path policy, or source-metadata schema is missing, malformed, incompatible, or changed:

- stop;
- report the exact Git path, commit, and failure;
- do not substitute an external file;
- do not select an older contract;
- require a separately reviewed contract repair or a newly prepared packet against current source.

## Full-file replacement failure

For a failed `REPLACE_FILE_FULL` plan:

- preserve the current file and exact blob SHA;
- verify that the complete current file was read;
- compare the proposed replacement against current source again;
- confirm that no valid content would be removed silently;
- confirm the target contains no private or protected evidence inappropriate for GitHub;
- resolve competing authority before preparing another replacement;
- prefer a bounded surgical change when full replacement cannot be reviewed safely.

Never bypass an expected-blob mismatch.

## Output-root failure

If the output root exists with content, is a symlink, escapes its expected path, or lies inside a protected repository:

- do not clean or delete it automatically;
- choose a new absent or empty external directory;
- rerun only after the packet and repository state are still verified.

## Forbidden-content or protected-path finding

If content scanning, metadata validation, destination classification, or protected-path policy blocks an operation:

- treat the block as authoritative for that run;
- do not reword, encode, split, or relocate content merely to evade the block;
- determine whether the content belongs in a private evidence source, a clean pointer, a different source class, or a separately approved migration route;
- prepare a new Preview only after the correct destination and authority are established.

## A3b S1 disabled-writer recovery

The A3b implementation remains source-hard-disabled and dependency-blocked. A failed S1 plan or simulated transaction must produce a bounded receipt and stop.

Recovery rules:

- expired or not-yet-valid plan: prepare a fresh exact Preview and envelope; never rewrite timestamps in place;
- packet, manifest, or Preview hash mismatch: stop and rebuild the approved package from exact bytes;
- target-state mismatch: reread the target at current `main`, rebuild the packet and Preview, and do not reuse the prior approval;
- packet-ID replay collision: preserve the existing branch/PR evidence and prepare a new packet identity only through a new approved Preview;
- existing PR metadata mismatch: do not repair the PR in place; stop for Noctua and a separately approved recovery route;
- uncertain PR creation: perform readback only; do not issue a duplicate create request;
- blocked dependency route: preserve the uploaded blocked receipt and do not install dependencies or enable APPLY in the same run.

No recovery step authorizes branch deletion, force-push, PR mutation, merge, migration, promotion, retirement, or cutover.

## Future execution-phase recovery

S1 activation and later execution phases remain separate and are not authorized by this runbook.

Any future execution implementation must define and test recovery for:

- working-tree mutation before staging;
- partial staging;
- commit creation;
- successful push followed by PR-creation failure;
- stale remote branch;
- failed checks;
- and rollback or abandon decisions.

At minimum, if a future branch push succeeds but draft PR creation fails, Spear must stop, report the exact branch and commit, preserve recovery evidence, avoid force-push or deletion, and require explicit Jayson direction.

No future recovery path may merge automatically, write directly to `main`, silently promote Atlas Prime, or modify Atlas Codex without separate approval.

## A3b disabled S1 recovery states

A3b adds recovery planning for a disabled draft-PR writer candidate. These states are review and test obligations only. They do not activate S1.

### Exact replay

An existing transaction may be treated as replay only when all of these match exactly:

- repository;
- packet ID;
- packet hash;
- manifest hash;
- Preview hash;
- base commit;
- deterministic branch;
- commit SHA;
- tree SHA;
- exact commit metadata;
- exact PR metadata.

Any alternate branch is `BRANCH_COLLISION`.

### Branch pushed, PR missing

`BRANCH_PUSHED_PR_MISSING` means the deterministic branch and exact commit exist, but the draft PR is absent.

Permitted recovery is limited to creating the single missing draft PR after exact branch, commit, tree, metadata, and remote-main readback. Do not delete the branch, force-push, create an alternate branch, repair the commit, or create a duplicate PR.

### PR state uncertain

`PR_STATE_UNCERTAIN` means a draft-PR create request may have reached the server but exact readback cannot prove success or absence.

Stop. Preserve the receipt. Do not send another create request until readback establishes definite absence.

### Collision and cleanup boundary

For `BRANCH_COLLISION`, changed hashes under a reused packet ID, altered commit metadata, altered PR metadata, or unexpected branch state:

- do not clean up automatically;
- do not force-push;
- do not close or repair a PR;
- do not create another PR;
- preserve branch, commit, PR, and receipt evidence;
- require Noctua review and explicit Jayson direction.

### Activation boundary

A3b recovery evidence grants no activation authority. S1 activation, harmless proof, rollback proof, migration, promotion, Atlas Codex retirement, and cutover remain later gates.
