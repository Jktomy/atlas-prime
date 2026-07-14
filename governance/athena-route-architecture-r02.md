---
title: "Athena Route Architecture R02"
atlas_id: "prime.governance.athena-route-architecture-r02"
status: "CANONICAL_ACTIVE"
source_type: "PROTOCOL"
authority_class: "CANONICAL_AUTHORED_SOURCE"
owner_project: "Project Codex"
owner_operation: "Operation Source Governance"
protected_level: "CRITICAL"
supersedes:
  - "prime.governance.athena-fresh-work-origin"
  - "fresh-origin requirements in prime.governance.athena-execution-routes"
routes_from:
  - "routing/command-surfaces.md"
  - "governance/change-routes.md"
routes_to:
  - "methods/athenas-spear.md"
  - "methods/phoenix-blade.md"
  - "methods/artemis-bow-and-arrow.md"
  - "methods/atlas-sword.md"
  - "governance/capability-parity-register.json"
  - "governance/capability-acceptance-contract.md"
---

# Athena Route Architecture R02

## Controlling decision

Jayson's explicit in-chat authorization is the human authority for the exact
Preview or mission presented in that conversation. No external platform-origin
attestation, separate OAuth service, custom gateway, user-run Python command, or
user-run PowerShell command is required to prove that Jayson authorized Athena.

GitHub identity, exact source locks, immutable payload identity, route-specific
receipts, draft-PR containment, applicable CI, independent review, and separate
permanence authority remain required. Authorization truth does not weaken
execution safety.

## Operator and route map

```text
ATHENA
  Spear
    -> Athena authors the exact Weave
    -> Spear delivers it to the singular Prime Thread Engine
    -> immutable branch and draft PR
    -> exact readback
    -> stop

  Sword -> Phoenix Blade
    -> Athena wields the exact Sword
    -> authenticated GitHub transaction or equivalent bound substrate
    -> no Thread Engine dependency
    -> branch and draft PR
    -> exact readback
    -> stop

  Aegis Break
    -> Athena directly uses GitHub-native mechanics or another bounded safe route
    -> preserves the approved goal, authority, risk, operations, stop, and proof
    -> never breaks Aegis or grants new authority

JAYSON / ARTEMIS
  Arrow -> Bow
    -> Jayson authorizes or fires the immutable Arrow
    -> Artemis Bow validates delegated delivery
    -> singular Prime Thread Engine
    -> immutable branch and draft PR
    -> exact readback
    -> stop

JAYSON
  Sword -> Oathbringer
    -> Jayson wields the exact Sword through the thin PowerShell client
    -> GitHub transaction
    -> no Thread Engine dependency
```

Phoenix Blade is Athena's functional counterpart to Oathbringer. Athena and
Jayson each wield an exact Sword without Thread Engine through their
operator-specific method.

Spear is Athena's Thread Engine route.

Arrow/Bow is Jayson and Artemis delegated delivery and is not an Athena route.

Aegis Break is Athena's direct/adaptive safe method and is not merely an alias
for Phoenix Blade.

## One normal engine

Prime Thread Engine remains the only normal repository engine. Spear and
Arrow/Bow may invoke it. Phoenix Blade, Oathbringer, and Aegis Break do not become
standing repository engines. Thread Engine never performs its own self-change.

## Post-merge generated infrastructure

The generated-checkpoint publisher is lifecycle infrastructure, not an Athena,
Jayson, or Artemis method.

```text
non-generated push to main
  -> deterministic Ubuntu/Windows generation
  -> zero delta: successful NOOP
  -> complete five-report delta: singular Thread Engine
  -> generated-only immutable draft PR
  -> exact-head Ubuntu/Windows validation
  -> stop
  -> separate Jayson permanence decision
```

Generated-only merges do not retrigger the publisher. Partial generated deltas
fail closed before writer authority.

## Authority boundaries

Every route preserves:

- exact current-source readback;
- Preview before durable mutation;
- Build and Execute separation;
- immutable base and payload locks;
- branch and draft-PR containment;
- no direct-main write or force push;
- no automatic ready transition or automatic merge;
- fail-closed behavior on replay, drift, ambiguity, privacy risk, or route
  mismatch;
- exact readback and rollback;
- separate Jayson permanence authority.

Athena may author meaning and payloads. Authoring does not imply merge authority.
Jayson controls permanence.

## Accepted evidence

### Phoenix Blade — RP-C01-M02

PR #50, `Prime: admit Found Silverlight Quest`, records an approved Phoenix
Blade Build by Athena under a Sword-equivalent exact control envelope, exact
base `9d0725fa0bce9461239cab10b4608ff3831d31fa`, head
`d26927cb0663afe71775dbfd35df2b3fc49ad21b`, Ubuntu and Windows validation
run `29070149639`, and merge
`c919b491d7dcf406fff9f1996ebe210e524cfc71`.

That accepted transaction proves Phoenix Blade as Athena-native Sword execution
independent of Thread Engine and reconciles `RP-C01-M02` as `PROVEN`.

### Spear — CAP-015 and AJ-01

PR #39, `Prime: prove Spear and Arrow/Bow delivery parity`, records Athena
authoring one exact Weave and direct Spear delivering the compiled mission into
the mission-scoped Prime Thread Engine. The engine created draft PR #39 at exact
head `1f60f0496eca94fe97071217a04b8bdf70004b64`, performed exact readback,
and stopped. Ubuntu and Windows validation run `29056870868` was GREEN, and the
proof merged as `7c8a533175da5c4fc9e8e0bb9de8bd37eba33dc5`.

PR #102 independently repeated direct Spear at exact head
`fa20c23c532f3c684862a028720fe9debd7db855`, passed complete Ubuntu and
Windows validation run `29215320609`, and merged as
`2ed53467a83569afea1d6c07e06d1d2ab52c75ff`.

These accepted transactions prove that Athena can reach Thread Engine through
Spear. They reconcile `CAP-015` as `RESTORED / ACTIVE` and `AJ-01` as `PROVEN`.
They do not prove or promote the separate Jayson/Artemis Arrow/Bow rejection
matrix.

## SUPERSEDED_HISTORICAL_ONLY origin experiment

The former fresh Work/Athena origin experiment is retired as a false
prerequisite. Its platform-attestation premise is not part of current route
authority. Its construction-only files remain in current source only as inert
historical security evidence. They are non-governing, have no dispatch
authority, and may not gate CAP-015, AJ-01, RP-C01-M02, ordinary in-chat
authorization, or any current route.

This retirement does not weaken GitHub actor verification, workflow identity,
replay protection, privacy screening, draft-only stops, exact-head CI,
independent review, rollback, or separate permanence authority.

## Non-promotion boundary

This architecture reconciliation does not promote AJ-03, AJ-11, AJ-12,
CAP-027, the RP-C01 gate, the RP-C08 gate, or Repairing Prime completion.
