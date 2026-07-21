---
title: "Prime Command and Routing Surfaces"
atlas_id: "prime.routing.command-surfaces"
status: "ACTIVE"
source_type: "REGISTER"
authority_class: "CANONICAL_AUTHORED_SOURCE"
owner_project: "Atlas"
owner_operation: "Source Governance"
protected_level: "HIGH"
---

# Prime Command and Routing Surfaces

Start with `README.md`, then `bootstrap.md`, then `atlas-start-here.md`, then this surface.

| Need | Canonical route |
|---|---|
| Atlas identity and canonical authority | `atlas-prime.md`, `governance/source-hierarchy.md` |
| Safety and execution boundaries | `safety/atlas-safety-doctrine.md`, `governance/noctua.md`, `governance/atlas-aegis.md`, `governance/atlas-strikeforce.md`, `governance/protected-source-boundary.md`, `governance/cutover-boundary.md` |
| Repository process, complete candidate, fallback, Goddess Mode, review, validation, Shardblade, and readback | `governance/repository-process-contract.md`, `governance/change-routes.md`, `governance/shard-doctrine.md` |
| Capability parity and acceptance | `governance/capability-parity-register.json`, `schemas/capability-parity-register.schema.json`, `governance/capability-acceptance-contract.md` |
| Athena execution routes and hosted identity | `governance/athena-execution-route-contract.md`, `methods/athenas-spear.md`, `methods/phoenix-blade.md`, `schemas/athena-hosted-route-request-v1.schema.json`, `schemas/athena-hosted-route-receipt-v1.schema.json`, `tools/athena_routes/README.md` |
| Default one-request route | One direct Jayson instruction grants bounded build-through-ready authority under `governance/repository-process-contract.md`; without explicit Shardblade authority, Athena reports `Prime PR #___ is ready to merge.` and Jayson merges manually |
| Explicit Goddess Mode | `with Goddess Mode` authorizes bounded autonomous completion only inside the exact approved transaction or campaign and all existing stops |
| Explicit Shardblade | `with Shardblade` or an unambiguous equivalent authorizes one exact-head compare-and-swap merge after required status, review reconciliation, Strikeforce GREEN, replay reservation, rollback, and fresh readback |
| Projects | `projects/project-registry.md` |
| Operations | `operations/operation-registry.md` |
| Artemis, Harmony, Emberdark, Cognitive Shadows, Kandra, and Sazed | `operations/artemis-runtime-and-routing.md` |
| Active Quests | `quest-board/quest-board-v1.json`, `quests/` (Prime Ascendant: `quests/prime-ascendant.md`) |
| Quest identities and unfinished-work continuity | `governance/quest-engine-continuity-contract.md`, `continuity/quest-engine-identities-r01.json`, `continuity/prime-continuity-register-r01.json`, `tools/prime_continuity/README.md` |
| Preview one bounded continuity update | `python -B -m tools.prime_continuity.cli plan-update ...`; candidate only, then reviewed draft-PR route |
| Full Atlas Sunset or continuity snapshot | Full lifecycle closeout starts with `python -B -m tools.atlas_lifecycle sunset preview`, then exact `sunset approve`, then exact `sunset candidate`; compact continuity snapshot only: `python -B -m tools.prime_continuity.cli sunset --continuity-id ID`; never substitute one for the other |
| Lesson Harvest and active assurance controls | `governance/lesson-harvest-protocol.md`, `governance/assurance-controls.json`, `schemas/assurance-controls-v1.schema.json` |
| Lifecycle records and read-only mechanics | `lifecycle/README.md`, `lifecycle/lifecycle-contract.md`, `lifecycle/schemas/`, `tools/atlas_lifecycle/README.md` |
| Clean-clone recovery, protected runtime restoration, and recovery proof | `recovery/elantris-recovery.md` |
| Prime-native source rollback and reviewed revert | `migration/rollback-map.md` |
| Thread Engine | `tools/thread-engine/README.md`, `tools/thread-engine/PRIME-PORT-STATUS.json` |
| Reusable templates | `templates/preview-bundle-template.md`, `templates/project-template.md`, `templates/protocol-template.md`, `templates/source-file-template.md`, `templates/support-file-template.md` |
| Generated projections | `tools/build_index.py`, `generated/` |

## Automatic method routing

A request for Athena to deliver through Thread Engine routes to Spear.

A request for Athena to execute an exact Sword herself routes to Phoenix Blade. Phoenix Blade mirrors Jayson wielding the same Sword through Oathbringer and does not use Thread Engine.

A request for Athena to construct, repair, or otherwise accomplish a bounded Atlas task directly routes through Aegis Break, which selects or constructs the safest exact route available. Direct GitHub-native construction is an Aegis Break route, not a synonym for Phoenix Blade.

Bow and Arrow belong to Jayson and Artemis delegated delivery. They are never selected as Athena's direct route.

A direct request to change, repair, update, or add to Prime routes one bounded transaction through merge-ready without a second user command. Preview-only and draft-only requests remain narrower.

A request to `Sunset this chat` is the mandatory exception: it always returns one exact user-visible Sunset Preview and stops. After Jayson approves that exact Preview, the same transaction seals its approval carrier and may continue through candidate, draft PR, validation, Strikeforce, permanence, and canonical readback according to the approved mode.

`with Goddess Mode` cannot bypass or change the Sunset Preview. `with Shardblade` is bound only through the exact Sunset approval mode. A blocked route resumes the same approved carrier and cannot claim completion before canonical readback.

## Decision box

For every requested action, state: objective, exact scope, source authority, protected boundary, route, proof, stop condition, rollback, and next safe action. If any field is unknown, investigate before mutation.

Prime command surfaces never route normal operation to `Jktomy/atlas-codex`, Google Drive, a chat transcript, or a generated report as source truth.
