---
title: "Prime Candidate Seal"
atlas_id: "prime.tools.candidate-seal"
status: "ACTIVE"
source_type: "TOOL_CONTRACT"
authority_class: "CANONICAL_AUTHORED_SOURCE"
owner_project: "Project Codex"
owner_operation: "Operation Source Governance"
protected_level: "HIGH"
---

# Prime Candidate Seal

`tools.candidate_seal` is a deterministic read-only compiler, verifier, remote-state reconciler, and repair-batch planner. It creates no branch, commit, pull request, READY transition, merge, workflow dispatch, setting change, or standing authority.

## Seal boundary

Before the first supported remote mutation, the operator constructs the complete candidate locally, runs every applicable local or read-only prepublication check, creates the exact local commit when the route supports it, and emits one `atlas.candidate-seal.v1` record. The seal binds:

- repository, Mission issue/ID, attempt, and objective digest;
- canonical base, deterministic branch intent, authorizer, operator, route, and generated-state classification;
- sorted case-fold-unique paths and their digest;
- every candidate byte through size, SHA-256, Git blob identity, and a route-neutral candidate-content digest;
- expected Git tree and optional exact commit head;
- deterministic PASS-evidence bindings for the applicable prepublication checks;
- invalidation, forbidden-action, and rollback contracts.

The compiler is not a publisher. Thread Engine remains the singular normal repository engine. Sword/Oathbringer, Phoenix Blade, or direct GitHub-native Aegis Break remains an exact mission-scoped alternate route and gains no normal or standing writer authority.

## Invalidation

Any change to the canonical base, branch, path inventory, bytes, tree, head, check evidence, Mission scope, attempt, or seal invalidates the seal and all validation, review, Strikeforce, READY, and MERGE evidence derived from it. A consumed seal ID rejects as replay.

## Interrupted publication

Remote-state reconciliation is read-only and fail-closed:

- no branch and no PR: publish the exact sealed candidate once;
- exact sealed branch and no PR: resume only draft-PR creation without repush;
- one exact sealed draft PR: readback, validation, and review only;
- stale main, moved branch, mismatched PR, duplicate PR, replay, malformed input, or unknown state: stop without mutation.

No interrupted state authorizes blind retry, duplicate work, force push, cleanup, READY, or merge.

## Batched candidate repair

Collect all readable findings before repair. Normalize each as `ACTIONABLE`, `INCORRECT`, `DUPLICATE`, `ALREADY_RESOLVED`, `INFORMATIONAL`, `UNAVAILABLE`, `DECISION_REQUIRED`, or `UNKNOWN`. One repair batch may contain every readable candidate-caused `ACTIONABLE` finding. Decision-required, unknown, malformed, duplicate, unreadable-misclassified, or actionable non-candidate-caused evidence fails closed.

The repair batch invalidates the source seal and all dependent evidence, preserves truthful partial state, permits one consolidated local repair, and requires one newly created and independently verified replacement seal before one repair publication. It never authorizes piecemeal pushes or automatic retry.

## Shared roles

- **Jayson / authorizer** controls objective, scope, protected boundary, READY, and MERGE.
- **Codex or Athena / semantic operator** discovers the complete candidate and reconciles findings.
- **Candidate Seal / read-only control** binds and verifies exact evidence but performs no mutation.
- **Thread Engine / normal publisher** may publish the exact verified seal once and stops after draft readback.
- **Approved alternate publisher** applies the same seal and partial-state rules inside one explicit mission; it does not become a second normal engine.
- **Strikeforce** audits the unchanged published head; GREEN grants no permanence authority.

## CLI

Create and verify use exact candidate files plus PASS-evidence digests:

```text
python -B -m tools.candidate_seal create mission.json \
  --candidate-root . --path path/to/file \
  --canonical-base <sha> --branch <branch> \
  --expected-tree <sha> --expected-head <sha> \
  --check full-validation=<sha256> \
  --authorizer Jayson --operator Codex \
  --route DIRECT_GITHUB_NATIVE_AEGIS_BREAK \
  --generated-state STALE_ALLOWED
```

`verify`, `reconcile`, and `repair-batch` are likewise read-only and emit JSON to standard output. Any rejected input returns `BLOCKED_RESUMABLE` and a stable error code.
