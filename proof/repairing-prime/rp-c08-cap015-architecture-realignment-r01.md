---
title: "Repairing Prime CAP-015 Architecture Realignment R01"
atlas_id: "prime.proof.repairing-prime.rp-c08-cap015-architecture-realignment-r01"
status: "ACCEPTED_EVIDENCE_RECONCILIATION"
source_type: "PROOF"
authority_class: "CANONICAL_AUTHORED_SOURCE"
owner_project: "Project Codex"
owner_operation: "Operation Source Governance"
protected_level: "CRITICAL"
---

# RP-C08 CAP-015 Architecture Realignment

## Decision

CAP-015 was blocked by a false premise: that Jayson's in-chat authorization
required a separate platform-origin attestation before Athena could reach Prime
Thread Engine. That premise is retired.

Jayson's explicit in-chat authorization is the human authority for the exact
Preview or mission. Route-specific source locks, GitHub identities, immutable
payloads, receipts, draft-PR containment, CI, review, rollback, and separate
permanence authority remain mandatory.

## Controlling route map

```text
ATHENA
  Spear -> Prime Thread Engine
  Sword -> Phoenix Blade -> GitHub transaction, no Thread Engine
  Aegis Break -> direct GitHub-native or other bounded safe route

JAYSON / ARTEMIS
  Arrow -> Bow -> Prime Thread Engine

JAYSON
  Sword -> Oathbringer -> GitHub transaction, no Thread Engine
```

Phoenix Blade is Athena's functional counterpart to Oathbringer: Athena wields
the Sword through Phoenix Blade, while Jayson wields it through Oathbringer.
Spear is Athena's Thread Engine route. Arrow/Bow belongs to Jayson and Artemis.
Aegis Break is Athena's adaptive direct/safe route and is not Phoenix Blade.

## RP-C01-M02 — Phoenix Blade

PR #50 is accepted Phoenix Blade evidence.

| Identity | Value |
|---|---|
| PR | `50` |
| Exact base | `9d0725fa0bce9461239cab10b4608ff3831d31fa` |
| Exact head | `d26927cb0663afe71775dbfd35df2b3fc49ad21b` |
| Validation run | `29070149639` |
| Ubuntu | `GREEN` |
| Windows | `GREEN` |
| Merge | `c919b491d7dcf406fff9f1996ebe210e524cfc71` |
| Thread Engine dependency | `NO` |

The PR body records Athena Phoenix Blade mirroring Oathbringer controls. The
transaction used a Sword-equivalent exact control envelope, branch and draft PR,
passed both hosted platforms, and merged only after Jayson's separate decision.

`RP-C01-M02` is therefore `PROVEN`.

## CAP-015 and AJ-01 — Spear

PR #39 is accepted direct Spear evidence.

| Identity | Value |
|---|---|
| PR | `39` |
| Exact base | `49eaf46bd971b4359e9ef89cb551c97e83dec85e` |
| Exact head | `1f60f0496eca94fe97071217a04b8bdf70004b64` |
| Validation run | `29056870868` |
| Ubuntu | `GREEN` |
| Windows | `GREEN` |
| Merge | `7c8a533175da5c4fc9e8e0bb9de8bd37eba33dc5` |
| Thread Engine dependency | `YES` |

Athena authored one exact Weave. Direct Spear delivered the compiled mission into
the mission-scoped Prime Thread Engine. The engine created the immutable draft
PR, performed exact readback, emitted its receipt, and stopped.

PR #102 independently corroborates the route at exact head
`fa20c23c532f3c684862a028720fe9debd7db855`, complete Ubuntu and Windows
validation run `29215320609`, and merge
`2ed53467a83569afea1d6c07e06d1d2ab52c75ff`.

`CAP-015` is therefore `RESTORED / ACTIVE`. AJ-01 is the actual Athena journey—
Jayson-authorized Athena Spear submission—and is `PROVEN`.

The parity transaction also proved byte equivalence with Arrow/Bow, but it did
not transfer Arrow/Bow ownership to Athena.

## Post-merge generated route

The generated-checkpoint publisher is infrastructure, not an operator method.
After a non-generated source merge, it starts automatically. Zero delta is a
successful no-op; a complete five-report delta invokes Thread Engine to create a
generated-only draft PR and validate its exact head on Ubuntu and Windows;
partial delta fails closed. It never auto-merges.

## Retired experiment

The following construction-only platform-origin experiment is removed from
current source and retained through Git history:

```text
governance/athena-fresh-work-origin-contract.md
schemas/athena-fresh-work-origin-receipt-v1.schema.json
schemas/athena-fresh-work-journey-receipt-v1.schema.json
tools/athena_routes/fresh_work_bridge.py
tests/athena-routes/test_fresh_work_bridge.py
```

It is not an active route, capability gate, blocker, or required user action.

## Counts after reconciliation

```text
PRESERVED:              4
IMPROVED:               7
RESTORED:              14
REPLACED:               1
INTENTIONALLY_RETIRED:  1
BLOCKED:                0
STILL_MISSING:          1
TOTAL:                  28
```

CAP-027 is the sole still-missing capability.

## Boundaries preserved

This reconciliation does not promote AJ-03, AJ-11, AJ-12, CAP-027, the RP-C01
gate, the RP-C08 gate, or Repairing Prime completion. It grants no automatic
merge, ready transition, branch cleanup, standing authority, protected external
action, infrastructure action, finance/account action, or unrelated source-truth
promotion.
