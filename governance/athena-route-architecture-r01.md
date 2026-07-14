---
title: "Athena Route Architecture R01"
atlas_id: "prime.governance.athena-route-architecture-r01"
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
  - "governance/capability-parity-register.json"
  - "governance/capability-acceptance-contract.md"
---

# Athena Route Architecture R01

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
    -> immutable branch
    -> draft pull request
    -> exact readback
    -> stop

  Phoenix Blade
    -> Athena performs direct GitHub-native repository construction
    -> no Thread Engine dependency
    -> branch
    -> draft pull request
    -> exact readback
    -> stop

  Aegis Break
    -> selects or constructs one bounded safe alternate route
    -> never breaks Aegis
    -> never grants new authority

JAYSON / ARTEMIS
  Arrow -> Bow
    -> Jayson authorizes or fires the immutable Arrow
    -> Artemis Bow validates delegated delivery
    -> singular Prime Thread Engine
    -> immutable branch
    -> draft pull request
    -> exact readback
    -> stop

JAYSON
  Sword -> Oathbringer
    -> Jayson's independent GitHub-native execution route
    -> no Thread Engine dependency
```

Phoenix Blade is Athena's functional counterpart to Oathbringer. Both are
independent of Thread Engine. Spear is Athena's Thread Engine route. Arrow/Bow is
Jayson and Artemis delegated delivery and is not an Athena route.

## One normal engine

Prime Thread Engine remains the only normal repository engine. Spear and
Arrow/Bow may invoke it. Phoenix Blade and Oathbringer perform independent
GitHub-native construction and do not become standing engines. Thread Engine
never performs its own self-change.

## Aegis Break

Aegis Break is Athena's third route option. It selects or constructs an
equivalent safe path when the normal route is obstructed. It may select Phoenix
Blade, Oathbringer, a protected Thread Engine route, or another exact bounded
route when doctrine permits. It is not hardwired to any one method and never
widens scope.

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
Blade Build by Athena, exact base `9d0725fa0bce9461239cab10b4608ff3831d31fa`,
head `d26927cb0663afe71775dbfd35df2b3fc49ad21b`, Ubuntu and Windows
validation run `29070149639`, and merge
`c919b491d7dcf406fff9f1996ebe210e524cfc71`.

That accepted transaction proves Phoenix Blade as Athena-native direct control
independent of Thread Engine and reconciles `RP-C01-M02` as `PROVEN`.

### Spear — CAP-015 and AJ-01

PR #39, `Prime: prove Spear and Arrow/Bow delivery parity`, records Athena
authoring one exact Weave and direct Spear delivering the compiled mission into
the mission-scoped Prime Thread Engine. The engine created draft PR #39 at exact
head `1f60f0496eca94fe97071217a04b8bdf70004b64`, performed exact
readback, and stopped. Ubuntu and Windows validation run `29056870868` was
GREEN, and the proof merged as
`7c8a533175da5c4fc9e8e0bb9de8bd37eba33dc5`.

That accepted transaction proves that Athena can reach Thread Engine through
Spear. It reconciles `CAP-015` as `RESTORED / ACTIVE` and `AJ-01` as `PROVEN`.
It does not prove or promote the separate Jayson/Artemis Arrow/Bow rejection
matrix.

## Retired origin experiment

The former fresh Work/Athena origin experiment is retired as a false
prerequisite. Its platform-attestation premise is not part of current route
authority. Git history preserves the experiment as historical evidence; it is
not an active route, capability gate, or blocker.

## Remaining boundaries

This architecture realignment does not promote:

```text
AJ-03  — genuine non-owner rejection remains unproven
AJ-11  — final clean-clone recovery remains unproven
AJ-12  — final merged-main Ubuntu/Windows validation remains unproven
CAP-027 — full acceptance-layer closure remains missing
RP-C01 — remains in progress
RP-C08 — remains in progress
Repairing Prime — remains in progress
```

It grants no automatic merge, ready transition, branch cleanup, standing
authority, protected external action, infrastructure action, account action, or
Quest completion.
