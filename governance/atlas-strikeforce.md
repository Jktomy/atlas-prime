---
title: "Prime Strikeforce"
atlas_id: "prime.governance.strikeforce"
status: "CANONICAL_ACTIVE"
source_type: "PROTOCOL"
authority_class: "CANONICAL_AUTHORED_SOURCE"
owner_project: "Project Codex"
owner_operation: "Operation Source Governance"
protected_level: "CRITICAL"
---

# Prime Strikeforce

Strikeforce consists of Noctua, Ares, and Aegis working cumulatively against one exact Preview, candidate head, execution object, recovery object, or lifecycle transaction.

```text
Noctua verifies source, identity, evidence, paths, bytes, and claims
→ Ares red-teams assumptions, authority, replay, recovery, leakage, and rollback
→ Aegis audits alignment and improves the safety, clarity, and Athena-to-Jayson interface
→ GREEN, YELLOW, or RED
```

Strikeforce is read-only. Its members may report defects, required repairs, clearer decision surfaces, and safer next actions, but they do not alter the exact object during reconciliation.

Noctua also verifies that the object is feasible with the declared route and evidence, is not an accidental duplicate of existing Missions, branches, pull requests, doctrine, capabilities, or services, and preserves Jayson's understood semantic intent.

Ares follows `governance/ares.md`. It acts as the devil's advocate and attacks credible failure modes, hidden assumptions, unnecessary complexity, authority, replay, recovery, leakage, rollback, misuse, and reasons the plan may be a bad direction even when technically possible.

Aegis is Athena's shield within Strikeforce. It confirms that the object and its presentation preserve Jayson's semantic objective, accepted lessons, active safeguards, explicit choices, stop conditions, protected boundaries, selected route, generated-state policy, and permanence mode. Aegis must resolve every solvable Ares finding, improve inefficiency and user friction, and clearly expose unresolved findings. It cannot convert a Noctua or Ares failure into GREEN through wording, confidence, or simplification.

## Risk-scaled gates

Consequential or complex work receives a full Preview Strikeforce before Jayson approval and a full exact-head Build Strikeforce after construction. Ordinary low-risk reversible work receives a lighter Preview review and one full Build Strikeforce. Immutable execution may use a fresh execution gate instead of repeating a full design review when exact bytes, digests, authority, scope, and prior findings remain unchanged.

Preview Strikeforce asks whether the exact plan should be built. Build Strikeforce asks whether the approved plan was built correctly. Passing Preview Strikeforce never substitutes for exact-head Build Strikeforce when candidate bytes were constructed or changed.

## Pass ceiling and reporting

Every full Strikeforce cycle is numbered and reported as `Pass N of 5`. Each pass runs Noctua, then Ares, then Aegis against one exact object. A repair or semantic change invalidates the prior exact-head result and requires another numbered pass.

After five non-GREEN passes, the transaction stops `BLOCKED_RESUMABLE`. Mission Control presents unresolved findings and asks Jayson for more information, narrowed scope, a changed approach, or abandonment. Five attempts never waive evidence or convert YELLOW or RED into GREEN. The final report records how many passes were required and which pass became GREEN.

GREEN means the exact reviewed candidate is ready for the next authorized gate. For non-candidate objects, GREEN means that exact reviewed object is ready for its next authorized gate. GREEN does not merge. It also does not itself READY, activate, promote, deploy, migrate, change settings, or cut over Prime. Shardblade is the separate merge authority for an explicitly authorized exact head; it remains distinct from Strikeforce and must perform its own fresh gate.

For a Prime repository transaction, Strikeforce also reconciles:

- the transaction and objective digests;
- exact canonical base, branch, PR, head, tree, and complete path inventory;
- complete-candidate and dependency-discovery posture;
- requesting surface, operator, selected route, publisher, and any fallback reconciliation;
- required checks and the final exact-head integrity result;
- generated-state classification;
- review findings and dispositions;
- protected-path authority;
- rollback and clean-clone recovery;
- replay reservation and receipt identity;
- whether permanence is manual or explicitly transaction-scoped Shardblade.

For a full Atlas Sunset, Strikeforce additionally verifies:

- the exact Preview ID, Preview digest, and user-visible scope;
- the exact approval and approved permanence mode;
- the route-neutral carrier and semantic payload digest;
- unchanged Project, Operation, Quest classification, Feather meaning, Lesson Harvest, record plan, and protected boundary;
- one Feather, one Sunset, and one Sunrise, plus one Emberline revision and checkpoint when admitted-Quest;
- every lesson disposition and resolving Golden Wing reference;
- explicit pending follow-up for new candidates or absorption-required findings;
- the Aegis and Strikeforce improvement review, including pass count and any required regression or assurance-control follow-up;
- resumable same-transaction state after any route failure;
- rejection of narrative, branch, GREEN, READY, or merge-only claims as completion;
- canonical readback before `SUNSET COMPLETE`.

When the current Jayson instruction explicitly authorizes `with Shardblade`, Strikeforce GREEN confirms evidence readiness only. The separate Shardblade actuation must still freshly compare-and-swap the expected head, re-read required status and review state, consume the one-use authority, and perform post-merge canonical readback. Any head, tree, path, status, review, or authority drift rejects the action.

For a bounded campaign, Strikeforce additionally reconciles the campaign digest, stage child request, Preview and construction receipts, expiry, and applicable stage authority. Campaign GREEN creates no authority and cannot substitute for the exact current stage action.

Strikeforce also reconciles the user's semantic objective, objective-to-route alignment, and the exact `governance/assurance-controls.json` applicability record. It verifies that every matching ACTIVE control is `APPLIED` or carries an exact `NOT_APPLICABLE` reason, that claimed absorption has a real enforcing source and regression proof, and that dependent canonical sources make the same claim. Passing checks cannot cure a misleading name, event ID, route, scope, lesson, or completion claim. Any missing or unknown applicability is YELLOW or RED, never GREEN.
