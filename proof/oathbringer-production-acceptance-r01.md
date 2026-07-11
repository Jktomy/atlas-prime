---
title: "Oathbringer Production Acceptance — AJ-04 through AJ-06"
atlas_id: "prime.proof.oathbringer-production-acceptance-r01"
status: "PROOF"
source_type: "PROOF"
authority_class: "AUDIT_EVIDENCE"
owner_project: "Project Codex"
owner_operation: "Operation Source Governance"
protected_level: "STANDARD"
---

# Oathbringer Production Acceptance — AJ-04 through AJ-06

This record binds the harmless live acceptance journeys that replace predecessor clone-first CAP-017 with Prime's GitHub-native Oathbringer route.

The proof does not grant standing authority. Every future Sword remains immutable, mission-specific, exact-head bound, and separately authorized.

## AJ-04 — BUILD — PROVEN

- Pull request: `Jktomy/atlas-prime#54`
- Original exact BUILD commit: `7b56f296f559b371baa3647ce7a8da7139472ccc`
- Base at creation: `44e0d860a73fd9d934d3c5aa748db6913bc7292b`
- Changed path: `proof/oathbringer-wave3-proof.txt`
- Workflow: `Prime read-only validation`
- Workflow run: `29102101778` / run number `59`
- Workflow conclusion: `success`
- Stop boundary: draft pull request; no ready transition or merge
- Independent reconciliation: exact branch, commit, pull request, path, payload, and workflow readback passed

A later branch synchronization commit does not alter the immutable original BUILD commit or its accepted transaction evidence.

## AJ-05 — REPAIR — PROVEN

- Pull request: `Jktomy/atlas-prime#56`
- Prior exact head: `61f79757b7dfe91b335d4c7106521f8a8ebd0e5f`
- Repaired exact head: `48f6b1110582886cb460b6ee65b56ffb9ba198ef`
- Base at PR creation: `187a1699e95634bdb07f2ec13b4c58f3b1694d9a`
- Changed path: `proof/oathbringer-wave3-proof.txt`
- Update: one single-parent child commit and fast-forward-only branch movement
- Workflow: `Prime read-only validation`
- Workflow run: `29103532734` / run number `63`
- Workflow conclusion: `success`
- Stop boundary: draft pull request; no merge
- Independent reconciliation: exact amended head, unchanged one-file scope, and workflow readback passed

The first AJ-05 attempt failed closed before mutation, exposed an incorrect REPAIR source-tree binding, and produced a sanitized Deflected Sword. The canonical repair merged in PR `#55` before the accepted AJ-05 retry.

## AJ-06 — EXECUTE — PROVEN

- Pull request: `Jktomy/atlas-prime#56`
- Independently audited exact head: `48f6b1110582886cb460b6ee65b56ffb9ba198ef`
- Applicable workflow run: `29103532734` / run number `63`
- Ready transition: completed without head movement
- Merge method: `squash`
- Merge commit and merged-main readback: `ed21295da8ddcf1b1790ecf6fb559a3128e0e112`
- Changed path: `proof/oathbringer-wave3-proof.txt`
- Independent reconciliation: merged PR identity, exact audited head, merge result, and canonical `main` readback passed

## Console v2 follow-on proof

Console v2 and sanitized Deflected Sword packaging were subsequently live-proven on draft PR `#58`, validation run `29109809717` / run number `68`, and canonized through PR `#57` at merge commit `f670bf27073563af8beb830fccb916b519c80ac5`.

## Foundry compiler and convergence re-acceptance — R04

A fresh end-to-end acceptance cycle re-proved the complete carrier path after canonical launcher and convergence repairs.

### R04 BUILD

- Pull request: `Jktomy/atlas-prime#66`
- Exact base: `1cc5ca68d1357b6060544626f21cc5ee92d3201c`
- BUILD head: `93dc448aa7a2208043ea3fb742576813d8e0a87c`
- Changed path: `proof/foundry-live-acceptance-r04.txt`
- Generated projection preflight: `CURRENT` / `CHANGED_FILES=NONE`
- Result: `OATHBRINGER_BUILD_PASS`
- Stop boundary: harmless draft PR exact readback

### R04 REPAIR

- Prior BUILD head: `93dc448aa7a2208043ea3fb742576813d8e0a87c`
- REPAIR head: `ab33dd486e9022d26f793b85034ebfe1f307025f`
- Parent relationship: one direct child of the BUILD head
- Repaired blob: `b724a09ec0adfceb338d3bb0ba37090c8866622f`
- Remote convergence: branch and PR projections converged after two read-only attempts
- Mutation count: one fast-forward branch update; no automatic retry or rollback
- Result: `OATHBRINGER_REPAIR_PASS`
- Stop boundary: harmless draft PR exact readback

### R04 EXECUTE

- Independently audited exact head: `ab33dd486e9022d26f793b85034ebfe1f307025f`
- Ready transition: completed without head movement
- Merge method: `squash`
- Merge commit and merged-main readback: `11d0db1c82c36c2bbdc07b02882da4f156b7b4e8`
- Result: `OATHBRINGER_EXECUTE_PASS`
- Stop boundary: `MERGED_MAIN_EXACT_READBACK_COMPLETE`

### Compiler and evidence results

- Compiler identity: `SWORD_FORGE_COMPILER_V1`
- BUILD, REPAIR, and EXECUTE each compiled twice with byte-identical carriers
- Carrier manifests bound the exact mission, payload, lessons, transport source, workflow source, and independent audit
- PowerShell remained the thin operator client
- AutoZIP produced local upload-ready evidence packages without changing repository authority
- No direct-main write, force-push, rebase, automatic retry, automatic rollback, or explicit branch deletion occurred
- Repository-level automatic deletion removed the merged proof branch after EXECUTE

This R04 cycle supplements the earlier AJ-04 through AJ-06 proof; it does not replace or invalidate the immutable earlier evidence.

## Acceptance

```text
AJ-04 BUILD    PROVEN
AJ-05 REPAIR   PROVEN
AJ-06 EXECUTE  PROVEN
CAP-017        REPLACED
ACTIVATION     ACTIVE
```

The predecessor clone-first identity remains historical lineage. Prime's accepted active implementation is the GitHub-native Oathbringer route.
