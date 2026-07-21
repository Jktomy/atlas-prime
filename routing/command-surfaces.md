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
| Ordinary free-form mission fields to immutable carrier | `python -B -m tools.athena_routes.free_form_intake --fields <fields.json> --output-dir <new-directory>`; closed inputs/receipt use `schemas/athena-free-form-mission-fields-v1.schema.json` and `schemas/athena-free-form-intake-receipt-v1.schema.json`; constructor is local, read-only, and non-promoting |
| Guided hosted Preview and Execute | `python -B -m tools.athena_routes.guided_publisher preview|execute`; this is the Jayson/Artemis Arrow/Bow hosted route, not Athena's Spear identity; Execute retains durable no-retry intent and exact hosted mission/base locks |
| Historical fresh-origin construction | `governance/athena-fresh-work-origin-contract.md`, `tools.athena_routes.fresh_work_bridge`; retained only as inert historical construction evidence and never required for Jayson-authorized Spear, Phoenix Blade, or Aegis Break work |
| RP-C01-M05 same-carrier parity evidence | `tools.athena_routes.m05_parity`, `schemas/rp-c01-m05-parity-evidence-v1.schema.json`; verifies exact direct-Spear and hosted Arrow/Bow compiler/adapter joins and cannot self-promote M05 |
| Agent identity and capability warrants | `governance/agentic-warrant-contract.md`, `schemas/agentic-capability-warrant-v1.schema.json`, `schemas/agentic-approval-record-v1.schema.json`, `schemas/agentic-warrant-receipt-v1.schema.json` |
| Legacy dedicated Shardblade warrant contracts | `governance/shard-doctrine.md`, `schemas/shardblade-permanence-request-v1.schema.json`, `schemas/shardblade-permanence-approval-v1.schema.json`, `schemas/shardblade-permanence-receipt-v1.schema.json`, `tools/agentic_warrants/permanence.py`; the dedicated standing service remains `CONTRACT_ONLY_NOT_ACTIVATED` while explicit one-transaction Shardblade is governed by the repository-process contract |
| Bounded Campaign Goddess Mode and Campaign Shardblade | `governance/atlas-aegis.md`, `governance/shard-doctrine.md`, `schemas/shardblade-campaign-warrant-v1.schema.json`, `schemas/shardblade-campaign-stage-request-v1.schema.json`, `schemas/shardblade-campaign-stage-receipt-v1.schema.json`, `tools/agentic_warrants/campaign.py` |
| Investiture source identity and Light-name migration | `governance/investiture-source-identity-contract.md` |
| Found Silverlight Investiture Accounting doctrine, ledger, summaries, and receipts | `governance/investiture-accounting-contract.md`, `quests/found-silverlight.md` |
| Deterministic conservation and generated-checkpoint route | `governance/deterministic-conservation-contract.md`, `.github/workflows/generated-checkpoint-publisher.yml`, `tools/generated_checkpoint/README.md`; explicit owner dispatch invokes the singular Thread Engine generated-draft route, while local generation remains available without hosted minutes |
| Prime Integrity and conditional Windows validation | `tools/prime_checks/README.md`, `tools/prime_checks/targeted_validation.py`, `.github/workflows/prime-readonly-validation.yml`; preserve legacy required contexts until a separately authorized ruleset transition |
| Chromelight provider evidence and account boundary | `governance/chromelight-provider-boundary.md`, `schemas/chromelight-evidence-register-v1.schema.json`, `proof/repairing-prime/rp-c03-chromelight-evidence-r01.json` |
| Resonance independent finding reconciliation | `governance/resonance-reconciliation-contract.md`, `schemas/resonance-finding-v1.schema.json`, `schemas/aberration-register-v1.schema.json`, `tools/resonance/README.md`, `proof/repairing-prime/rp-c04-aberration-register-r01.json` |
| Source changes and route selection | `governance/source-lifecycle.md`, `governance/change-routes.md` |
| Default one-request route | One direct Jayson instruction grants bounded build-through-ready authority under `governance/repository-process-contract.md`; without explicit Shardblade authority, Athena reports `Prime PR #___ is ready to merge.` and Jayson merges manually |
| Explicit Goddess Mode | `with Goddess Mode` authorizes bounded autonomous completion only inside the exact approved transaction or campaign and all existing stops |
| Explicit Shardblade | `with Shardblade` or an unambiguous equivalent authorizes one exact-head compare-and-swap merge after required status, review reconciliation, Strikeforce GREEN, replay reservation, rollback, and fresh readback |
| Projects | `projects/project-registry.md` |
| Operations | `operations/operation-registry.md` |
| Artemis, Harmony, Emberdark, Cognitive Shadows, Kandra, and Sazed | `operations/artemis-runtime-and-routing.md` |
| Apollo, Hermes, Iris, and Zeus operator endpoints | `infrastructure/atlas-infrastructure-source.md` |
| Protocols and delivery methods | `operations/protocol-library.md`, `methods/artemis-bow-and-arrow.md`, `methods/athenas-spear.md`, `methods/atlas-sword.md`, `methods/phoenix-blade.md` |
| Athena through Thread Engine | `methods/athenas-spear.md`, then the exact Weave, base, Thread Engine state, and draft-PR stop boundary |
| Athena direct safe construction or repair | `methods/phoenix-blade.md` for Aegis Break route selection, then the exact live repository or PR state |
| Athena executes a Sword | `methods/phoenix-blade.md`, `methods/sword-forge-standard.md`, `methods/sword-lessons.json`, `methods/atlas-sword.md`, then the exact Sword and live target state |
| Jayson Sword or Oathbringer request | `methods/sword-forge-standard.md`, `methods/sword-lessons.json`, `methods/atlas-sword.md`, `tools/atlas-sword/README.md`, then the exact live repository or PR state |
| Oathbringer Foundry carrier compile | `methods/oathbringer-foundry.md`, `methods/sword-forge-standard.md`, `methods/sword-lessons.json`, `tools/oathbringer-foundry/README.md`, then exact current source and read-only live-state binding |
| Active Quests | `quest-board/quest-board-v1.json`, `quests/` (Prime Ascendant: `quests/prime-ascendant.md`) |
| Mission Board intake, assignment, search, sequencing, and restart | GitHub Issues in `Jktomy/atlas-prime`, `governance/mission-board-contract.md`, `.github/ISSUE_TEMPLATE/mission.md`, `schemas/mission-v1.schema.json`, `tools/mission_board/README.md`; Issues coordinate work but never replace merged source or the canonical Quest Board |
| Continue one Mission | `Continue Mission #N` requires exact repository/Issue resolution, all comments, current canonical source, linked branch/PR/check/review/receipt readback, duplicate search, and one next safe action; pull-request objects and chat-only claims fail closed |
| Complete an ordered Mission list | Read and reconcile each exact Mission in the requested order; number order creates no dependency, and a `BLOCKED_RESUMABLE` item permits continuation only through its explicit queue behavior and dependency edges |
| Quest identities and unfinished-work continuity | `governance/quest-engine-continuity-contract.md`, `continuity/quest-engine-identities-r01.json`, `continuity/prime-continuity-register-r01.json`, `tools/prime_continuity/README.md` |
| Validate continuity or surface Argus | `python -B -m tools.prime_continuity.cli validate`, `python -B -m tools.prime_continuity.cli argus` |
| Preview one bounded continuity update | `python -B -m tools.prime_continuity.cli plan-update ...`; candidate only, then reviewed draft-PR route |
| Full Atlas Sunset or continuity snapshot | Full lifecycle closeout: `governance/lesson-harvest-protocol.md`, `lifecycle/lifecycle-contract.md`, then `python -B -m tools.atlas_lifecycle sunset preview`, exact `sunset approve`, and exact `sunset candidate`; compact continuity snapshot only: `python -B -m tools.prime_continuity.cli sunset --continuity-id ID`; never substitute one for the other |
| Sunset Router deterministic front door | `governance/sunset-router-contract.md`, `tools/sunset_router/README.md`, then `python -B -m tools.sunset_router preview`, `python -B -m tools.sunset_router approve`, `python -B -m tools.sunset_router candidate`, `python -B -m tools.sunset_router verify`, or `python -B -m tools.sunset_router receipt`; it resolves canonical ownership, selects Athena-first routes without automatic operator transfer, delegates lifecycle semantics to `tools.atlas_lifecycle`, and requires exact merged-byte readback for `SUNSET COMPLETE` |
| Lesson Harvest and active assurance controls | `governance/lesson-harvest-protocol.md`, `governance/assurance-controls.json`, `schemas/assurance-controls-v1.schema.json` |
| Lifecycle records and read-only mechanics | `lifecycle/README.md`, `lifecycle/lifecycle-contract.md`, `lifecycle/schemas/`, `tools/atlas_lifecycle/README.md` |
| Infrastructure source | `infrastructure/atlas-infrastructure-source.md` |
| Clean-clone recovery, protected runtime restoration, and recovery proof | `recovery/elantris-recovery.md` |
| Prime-native source rollback and reviewed revert | `migration/rollback-map.md` |
| Knowledge lifecycle | `knowledge/atlas-source-compendium.md` |
| Thread Engine | `tools/thread-engine/README.md`, `tools/thread-engine/PRIME-PORT-STATUS.json` |
| Reusable templates | `templates/preview-bundle-template.md`, `templates/project-template.md`, `templates/protocol-template.md`, `templates/source-file-template.md`, `templates/support-file-template.md` |
| Proven delivery evidence | `proof/prime-thread-engine-bootstrap-proof.md`, `proof/prime-spear-arrow-bow-parity-r01.md`, `proof/repairing-prime/rp-c08-cap015-architecture-realignment-r02.md` |
| Generated projections | `tools/build_index.py`, `generated/` |
| Migration and cutover evidence | `migration/codex-cutover.md`, `migration/codex-inheritance-manifest.md`, `migration/predecessor-snapshot.md`, `migration/rollback-map.md`, `migration/source-disposition-summary.json` |

## Automatic method routing

A request for Athena to deliver through Thread Engine routes to Spear.

A request for Athena to execute an exact Sword herself routes to Phoenix Blade. Phoenix Blade mirrors Jayson wielding the same Sword through Oathbringer and does not use Thread Engine.

A request for Athena to construct, repair, or otherwise accomplish a bounded Atlas task directly routes through Aegis Break, which selects or constructs the safest exact route available. Direct GitHub-native construction is an Aegis Break route, not a synonym for Phoenix Blade.

Bow and Arrow belong to Jayson and Artemis delegated delivery. They are never selected as Athena's direct route.

A request to build, repair, recover, execute, or otherwise make a Sword automatically routes first through `methods/sword-forge-standard.md` and `methods/sword-lessons.json`, then through current Sword doctrine and the exact live GitHub target state. The user does not need to invoke a separate preflight command or remind Athena to recall earlier lessons.

A direct request to change, repair, update, or add to Prime routes one bounded transaction through merge-ready without a second user command. Preview-only and draft-only requests remain narrower. The route includes complete-candidate construction, candidate-caused repair, actionable review repair, validation, exact-head Strikeforce, and ready-for-review only while the candidate head remains unchanged.

A request to `Sunset this chat` is the mandatory exception: it always returns one exact user-visible Sunset Preview and stops. After Jayson approves that exact Preview, the same transaction seals its approval carrier and may continue through candidate, draft PR, validation, Strikeforce, permanence, and canonical readback according to the approved mode.

Sunset Router is the deterministic front door for that flow. It resolves canonical ownership and route policy, but it never bypasses the required user-visible Preview or transfers an operator automatically. It delegates lifecycle meaning and candidate compilation to `tools.atlas_lifecycle` and treats only exact merged-byte canonical readback as `SUNSET COMPLETE`.

`with Goddess Mode` keeps the same transaction moving through obvious safe work and candidate-caused repair without widening, but cannot bypass or change a Sunset Preview. `with Shardblade` grants one exact-head permanence action only when the exact approval binds that mode. Without Shardblade, merge remains Jayson's manual action. A blocked Sunset route resumes the same approved carrier and cannot claim completion before canonical readback.

## Decision box

For every requested action, state: objective, exact scope, source authority, protected boundary, route, proof, stop condition, rollback, and next safe action. If any field is unknown, investigate before mutation.

Prime command surfaces never route normal operation to `Jktomy/atlas-codex`, Google Drive, a chat transcript, or a generated report as source truth.
