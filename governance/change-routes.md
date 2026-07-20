---
title: "Prime Change Routes"
atlas_id: "prime.governance.change-routes"
status: "CANONICAL_ACTIVE"
source_type: "PROTOCOL"
authority_class: "CANONICAL_AUTHORED_SOURCE"
owner_project: "Project Codex"
owner_operation: "Operation Source Governance"
protected_level: "CRITICAL"
---

# Prime Change Routes

`governance/repository-process-contract.md` controls the common repository transaction, review, validation, fallback, Goddess Mode, Shardblade, and readback rules across these routes.

| Concept | Meaning |
|---|---|
| Authorizer | Jayson or one exact delegated authority; controls scope and permanence |
| Operator | Athena, Jayson, Artemis, or another named actor performing the bounded action |
| Athena Thread Engine route | Spear: Athena delivers one exact Weave to the singular Prime Thread Engine |
| Jayson/Artemis delegated route | Arrow/Bow: Jayson authorizes or fires the immutable Arrow and Artemis/Bow validates and delivers it unchanged to Thread Engine |
| Jayson Sword route | Sword sealed package wielded by Jayson through Oathbringer |
| Athena Sword route | Phoenix Blade: Athena executes one exact Sword herself; counterpart to Jayson wielding Oathbringer; no Thread Engine |
| Athena safe rerouting | Aegis Break: Athena selects or constructs any safe bounded equivalent route, including direct GitHub-native work when appropriate |
| Hosted or local launcher | Thin intake or client that invokes a method or engine without becoming one |
| Normal repository engine | Prime Thread Engine, singular |
| Independent alternate publisher | Sword/Oathbringer for PowerShell, Thread Engine self-change, emergency bootstrap, or a proven blocked-route recovery |
| Repository substrate | Exact GitHub-native tree transaction or Fresh Clone First |
| AI-assisted work surface | Shardplate |
| Default permanence boundary | An unchanged merge-ready PR; Jayson merges manually when no exact Shardblade authority is present |
| Explicit Shardblade boundary | One transaction-scoped exact-head machine merge only when the current Jayson instruction says `with Shardblade` or an unambiguous equivalent |
| Provider, model, and runtime identity | Bound independently; trusted reported tokens map only to Spirallight, Chromelight, or Emberlight under `governance/investiture-source-identity-contract.md` |

```text
Athena -> Spear -> Thread Engine
Jayson / Artemis -> Arrow -> Bow -> Thread Engine
Jayson -> Sword -> Oathbringer -> thin client -> GitHub transaction
Athena -> Sword -> Phoenix Blade -> Sword-defined repository transaction
Athena -> Aegis Break -> any safe bounded equivalent route
```

Spear is Athena's Thread Engine route. Arrow and Bow are not Athena's direct route; they belong to Jayson's delegated delivery and Artemis coordination. Both routes may converge on the same compiler and singular Thread Engine without sharing operator identity.

Phoenix Blade is Athena executing a Sword and mirrors what Oathbringer is to Jayson. Phoenix Blade does not use Thread Engine. Aegis Break owns direct safe-route selection or construction, including direct GitHub-native work when that is the safest bounded route.

Aegis Break is not hardwired to Phoenix Blade, Spear, Oathbringer, or any one substrate. It does not erase Aegis, widen scope, or convert a one-time route into standing authority.

Every route:

- separates Preview, Build, Execute, READY, and permanence;
- uses exact base, path, payload, and candidate-tree locks;
- contains durable construction in a branch and draft PR for Noctua;
- prohibits direct main, force push, and history rewrite;
- preserves requesting surface, operator, selected route, fallback routes, branch, PR, and exact-head identity;
- rejects duplicate transactions, branches, PRs, replay, ambiguous partial state, and blind retry;
- respects Preview-only and draft-only instructions as narrower than the normal build-through-ready route;
- includes complete-candidate construction, validation, candidate-caused repair, actionable review repair, exact-head Strikeforce, and ready-for-review within one direct Jayson request;
- uses `with Goddess Mode` only for bounded autonomous completion inside the same transaction and safeguards;
- uses `with Shardblade` only for one exact unchanged head after required status, review, Strikeforce, fresh compare-and-swap readback, and rollback proof.

Without explicit Shardblade authority, Athena reports `Prime PR #___ is ready to merge.` and Jayson executes the normal permanence action manually in GitHub. With explicit Shardblade authority, the one machine action is consumed by success or terminal safe rejection and grants no standing approval.

After READY, changed candidate bytes invalidate readiness. Return the PR to draft, validate and review the replacement exact head, repeat Strikeforce, and obtain exact current permanence authority for the unchanged replacement head. Merge authority is never inferred from construction, validation, GREEN, READY, delegation, route identity, prior approval, or prior success.

Prime has one normal repository engine and one independent alternate publisher. Spear and Arrow/Bow invoke Thread Engine. Phoenix Blade and Oathbringer execute Swords independently of Thread Engine. The two publishers may share reviewed contracts and fixtures but must not share one mutation implementation whose failure disables both. Thread Engine never performs its own self-change.
