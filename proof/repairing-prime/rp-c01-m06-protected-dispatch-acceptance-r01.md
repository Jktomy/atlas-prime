---
title: "Repairing Prime RP-C01-M06 Protected Dispatch Acceptance R01"
atlas_id: "prime.proof.repairing-prime.rp-c01-m06-protected-dispatch-acceptance-r01"
status: "ACCEPTED_MISSION_PROOF"
source_type: "PROOF"
authority_class: "CANONICAL_AUTHORED_SOURCE"
owner_project: "Project Codex"
owner_operation: "Operation Source Governance"
protected_level: "CRITICAL"
---

# RP-C01-M06 protected dispatch acceptance

`RP-C01-M06` is PROVEN from one live protected-path transaction through
`AEGIS_BREAK_PROTECTED_PATH_V1`.

## Live transaction

Jayson authorized mission `RP-C01-M06-PROTECTED-DISPATCH-LIVE-R01`. The
mission-scoped production adapter independently observed authenticated GitHub
operator `Jktomy`, locked canonical base
`eef4e211d3e4bf6068f1b27cef0dc884a46e2791`, fresh-cloned Prime, and added
exactly one public-clean protected payload:

`governance/proof-fixtures/rp-c01-m06-protected-dispatch-marker-r01.md`.

The adapter created draft PR #187 at exact head
`fa383b816f26160067372fb107120a8a3c4fb2bd`, verified one commit, one changed
path, zero comments, zero reviews, zero review threads, and stopped at
`DRAFT_PR_READBACK`.

## Immutable evidence

- mission SHA-256:
  `29a96ea23975f6165961db639f8fb4d31244e02cfc4cebd12c4b7c1f3db11816`;
- uploaded adapter receipt SHA-256:
  `0edaf1e7b7f788ca60ba3cbd6a00228cb7adbf2852a1716107b9fa6e8c7a03aa`;
- operation-set SHA-256:
  `e0dcb1d29bbef7a765938b04c9974417f71da6d595590682745053272f74e7ba`;
- candidate-tree SHA-256:
  `e67babe6da7905da0dacef568320234533a9cce6f4fc54541a2222048cfe50e3`;
- final-pathset SHA-256:
  `7571d338ab6b7a27e1b631e7cb49822f31b3bb3adb8658d5be972b606af2538d`;
- protected payload SHA-256:
  `4e61f25575013aefb429d4f50873037eb488ad20ab6a24ba5c9f7670c4e5c0bc`;
- commit tree:
  `745b553e5c738f56575b80417d0f52eb90ec2de3`.

The receipt reports `SUCCESS`, mission-scoped authority, expected and observed
operator `Jktomy`, all 24 execution checkpoints through exact readback,
human-required merge, no standing authority, and every forbidden action false
or `NO`.

## Validation and permanence

Read-only validation run `29333971422` passed the exact PR head on Windows job
`87088522381` and Ubuntu job `87088522424`. Detached Strikeforce review was
GREEN. Jayson separately approved permanence, and the reviewed head merged as
`c20644641d947485a5d9fad26b6d07ef064dba9b`.

Canonical readback reproduced the marker as Git blob
`7cad2c8a8bddaa8db171dbf56f6785c8dd98b4e3` with exact SHA-256
`4e61f25575013aefb429d4f50873037eb488ad20ab6a24ba5c9f7670c4e5c0bc`.

Post-merge generated checkpoint PR #188 completed deterministic hosted
Ubuntu/Windows parity and exact-head validation, then merged as
`aee1f837c18dbabf871396ffedf7d9c53e3d8297`.

## Acceptance boundary

This authored reconciliation moves only `RP-C01-M06` from PARTIAL to PROVEN.
It grants no standing authority and does not complete RP-C01. M07 and AJ-03
still require a genuine non-owner rejection. CAP-027, AJ-11, AJ-12, RP-C08,
and the Repairing Prime Quest remain open. No capability or acceptance-journey
promotion is authorized by this mission-level proof.
