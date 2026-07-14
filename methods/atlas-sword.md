---
title: "Atlas Sword and Oathbringer — Prime"
atlas_id: "prime.method.oathbringer"
status: "PRODUCTION_ACTIVE"
source_type: "METHOD"
authority_class: "CANONICAL_AUTHORED_SOURCE"
owner_project: "Project Codex"
owner_operation: "Operation Source Governance"
protected_level: "CRITICAL"
routes_from:
  - "governance/athena-route-architecture-r02.md"
---

# Atlas Sword and Oathbringer — Prime

Sword is one immutable, hash-bound, mission-specific package containing Athena's
complete exact repository payload, source locks, allowed operations, tests, stop
boundary, and receipt contract.

A Sword has two operator-specific wielding methods:

```text
Athena -> Phoenix Blade -> exact Sword mechanics -> GitHub transaction
Jayson -> Oathbringer -> thin PowerShell client -> GitHub transaction
```

Neither method depends on Thread Engine. The package identity and safety controls
remain the same; operator, launcher, credential principal, and route receipt
remain distinct.

## Phoenix Blade

Phoenix Blade is Athena's Sword method. Athena uses the exact Sword mission and
payload through the authenticated capabilities available in the current surface.
Phoenix Blade does not invoke the Oathbringer PowerShell client. Its complete
method contract is `methods/phoenix-blade.md`.

## Oathbringer

Oathbringer is Jayson's PowerShell-operated Sword method. PowerShell is the thin
interactive client: it verifies the Sword, resolves the authenticated GitHub
operator without persisting credentials, displays truthful stages and
plan-position percentages, invokes the deterministic GitHub-native adapter,
observes workflows, and writes the receipt. It does not author, reinterpret, or
locally compose Atlas source.

A Build Sword may create exact GitHub blobs, construct the candidate tree, create
one single-parent commit and branch, open one draft PR, read back the exact remote
state, monitor applicable CI, and then stop.

A Repair Sword may bind the exact current PR head, construct the complete final
candidate tree, and add one fast-forward child commit with exact amended-head
readback. It never force-pushes or rewrites reviewed history.

A separate exact Execute Sword may mark the independently audited head ready and
merge only that exact head after applicable CI and exact readback. Build or
Repair authority never implies Execute authority.

A Sword may target any authorized clean-text Atlas path and may contain arbitrary
multi-file `ADD`, `REPLACE`, `DELETE`, `RENAME`, and `MOVE` operations. Protected
path classification raises audit attention and proof requirements; it is not by
itself a construction veto inside an isolated branch and draft PR.

There is no standing Sword authority.

Prime contains the reusable audit framework, GitHub-native mission format, exact
candidate-tree and path verification, immutable receipts, failure conservation,
and accepted Oathbringer BUILD, REPAIR, and EXECUTE evidence. AJ-04, AJ-05, and
AJ-06 are proven in `proof/oathbringer-production-acceptance-r01.md`. CAP-017 is
`REPLACED / ACTIVE` because the GitHub-native route replaces the predecessor
clone-first implementation while preserving its functional purpose.

The production Oathbringer route is independent of Thread Engine and ChatGPT
Work / Codex. It never persists the GitHub token and never lets Thread Engine
perform its own self-change.

Every Sword must bind its exact authorizer, operator, approved Preview, repository,
base, branch, operation inventory, payload hashes, applicable workflow sources,
stop boundary, proof, and rollback. Unknown fields, unmanifested payloads,
identity drift, stale source, or unbound audit evidence fail closed.
