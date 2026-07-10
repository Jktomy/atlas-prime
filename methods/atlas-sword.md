---
title: "Atlas Sword and Oathbringer — Prime"
atlas_id: "prime.method.oathbringer"
status: "PRODUCTION_ADAPTER_PRESENT_PROOF_PENDING"
source_type: "METHOD"
authority_class: "CANONICAL_AUTHORED_SOURCE"
owner_project: "Project Codex"
owner_operation: "Operation Source Governance"
protected_level: "CRITICAL"
---

# Atlas Sword and Oathbringer — Prime

Sword is one immutable, hash-bound, mission-specific package containing Athena's complete exact repository payload, source locks, allowed operations, tests, stop boundary, and receipt contract.

Oathbringer is Jayson's PowerShell-operated GitHub execution route. PowerShell is the thin interactive client: it verifies the Sword, resolves the authenticated GitHub operator without persisting credentials, displays truthful stages and plan-position percentages, invokes the deterministic GitHub-native adapter, observes workflows, and writes the receipt. It does not author, reinterpret, or locally compose Atlas source.

A Build Sword may create exact GitHub blobs, construct the candidate tree, create one single-parent commit and branch, open one draft PR, read back the exact remote state, monitor applicable CI, and then stop.

A Repair Sword may bind the exact current PR head, construct the complete final candidate tree, and add one fast-forward child commit with exact amended-head readback. It never force-pushes or rewrites reviewed history.

A separate exact Execute Sword may mark the independently audited head ready and merge only that exact head after applicable CI and exact readback. Build or Repair authority never implies Execute authority.

A Sword may target any authorized clean-text Atlas path and may contain arbitrary multi-file ADD, REPLACE, DELETE, RENAME, and MOVE operations. Protected-path classification raises audit attention and proof requirements; it is not by itself a construction veto inside the isolated branch and draft PR.

There is no standing Sword authority.

Prime now contains:

- the reusable schema `1.2` audit framework;
- the GitHub-native production mission format `2.0`;
- the thin PowerShell launcher and authenticated token handoff;
- deterministic BUILD, REPAIR, and EXECUTE adapters;
- exact candidate-tree and final path-set verification;
- workflow applicability and exact-head waits;
- structured success, failure, and interruption receipts.

The production adapter is **present but not yet capability-proven**. Until Wave 3 completes AJ-04 through AJ-06 with harmless live GitHub transactions, CAP-017 remains `STILL_MISSING`, the framework state remains `PILOT_READY_PROOF_PENDING`, and Prime must not describe production Oathbringer as restored or generally active.

The production route is independent of Thread Engine and ChatGPT Work / Codex. It uses GitHub-native blob/tree/commit/ref/PR construction as its durable transaction, keeps PowerShell thin, records stage and percentage truth before each action, preserves failure and interruption ledgers, never persists the GitHub token, and never lets Thread Engine perform its own self-change.

Fresh Clone First remains an emergency or compatibility substrate, not a mandatory Oathbringer construction path.

## Production mission invariants

A production mission must bind:

- `SWORD_FORGE_STANDARD_V1`;
- the exact `prime-sword-lessons-v1` source SHA-256;
- every controlling lesson as `APPLIED` or `NOT_APPLICABLE` with a reason;
- Jayson as authorizer and operator;
- approved Preview and explicit execution authorization;
- exact repository, base branch, base SHA, mission branch, pull request, and head SHA as applicable;
- the complete final operation inventory and payload hashes;
- exact workflow source blobs and applicability;
- separate Build, Repair, or Execute stop boundaries;
- `DIRECT_MAIN`, `FORCE_PUSH`, `SCOPE_WIDENING`, and `TOKEN_PERSISTENCE` as forbidden actions.

## Mandatory forge routing

Every request to build, repair, recover, or execute a Sword automatically routes through:

1. `methods/sword-forge-standard.md`;
2. `methods/sword-lessons.json`;
3. this method source;
4. `tools/atlas-sword/README.md`;
5. the exact live repository, branch, pull request, and head state.

No separate user phrase, preflight command, or memory prompt is required.

A forged carrier must record `SWORD_FORGE_STANDARD_V1`, the lessons-register schema and source identity, every applied controlling lesson, and every not-applicable lesson with its mission-specific reason. Unknown applicability or an unclassified controlling lesson blocks carrier delivery.

Strikeforce findings may repair the current Sword, but they never silently rewrite the Forge Standard or lessons register. Reusable lessons require a separate bounded source transaction with evidence and independent review.
