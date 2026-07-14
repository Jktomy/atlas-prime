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

Start with `README.md`, then `bootstrap.md`, then `atlas-start-here.md`, then this
surface.

| Need | Canonical route |
|---|---|
| Atlas identity and canonical authority | `atlas-prime.md`, `governance/source-hierarchy.md` |
| Safety and execution boundaries | `safety/atlas-safety-doctrine.md`, `governance/noctua.md`, `governance/atlas-aegis.md`, `governance/atlas-strikeforce.md`, `governance/protected-source-boundary.md`, `governance/cutover-boundary.md` |
| Operator and route architecture | `governance/athena-route-architecture-r01.md`, `governance/change-routes.md` |
| Capability parity and acceptance | `governance/capability-parity-register.json`, `schemas/capability-parity-register.schema.json`, `governance/capability-acceptance-contract.md` |
| Athena delivers through Thread Engine | `methods/athenas-spear.md`; use Spear |
| Athena wields a sealed Sword | `methods/phoenix-blade.md`, `methods/atlas-sword.md`; use Phoenix Blade without Thread Engine |
| Athena needs a direct or alternate safe route | `governance/atlas-aegis.md`, `methods/phoenix-blade.md`; use Aegis Break to perform a direct GitHub-native transaction or select/construct another bounded safe route |
| Jayson and Artemis delegated delivery | `methods/artemis-bow-and-arrow.md`, `governance/athena-execution-route-contract.md`; Arrow/Bow invokes Thread Engine and is not an Athena route |
| Jayson wields a Sword | `methods/atlas-sword.md`, `methods/oathbringer-foundry.md`, `methods/sword-forge-standard.md`; use Oathbringer |
| Hosted Arrow/Bow identity and safety | `schemas/athena-hosted-route-request-v1.schema.json`, `schemas/athena-hosted-route-receipt-v1.schema.json`, `tools/athena_routes/README.md` |
| Agent identity and capability warrants | `governance/agentic-warrant-contract.md`, `schemas/agentic-capability-warrant-v1.schema.json`, `schemas/agentic-approval-record-v1.schema.json`, `schemas/agentic-warrant-receipt-v1.schema.json` |
| Deterministic conservation and generated-checkpoint route | `governance/deterministic-conservation-contract.md`, `.github/workflows/generated-checkpoint-publisher.yml`, `tools/generated_checkpoint/README.md` |
| Source changes and route selection | `governance/source-lifecycle.md`, `governance/change-routes.md` |
| Projects | `projects/project-registry.md` |
| Operations | `operations/operation-registry.md` |
| Artemis, Hermes, Nexus | `operations/artemis-runtime-and-routing.md` |
| Active Quests | `quest-board/quest-board-v1.json`, `quests/` |
| Quest continuity | `governance/quest-engine-continuity-contract.md`, `continuity/quest-engine-identities-r01.json`, `continuity/prime-continuity-register-r01.json`, `tools/prime_continuity/README.md` |
| Emberline, Sunset, or Sunrise | `tools.prime_continuity.cli emberline|sunset|sunrise`; projections and evidence never govern |
| Lifecycle records | `lifecycle/README.md`, `lifecycle/lifecycle-contract.md`, `lifecycle/schemas/`, `tools/atlas_lifecycle/README.md` |
| Backup, restore, recovery, rollback | `recovery/phoenix-recovery.md`, `migration/rollback-map.md` |
| Thread Engine | `tools/thread-engine/README.md`, `tools/thread-engine/PRIME-PORT-STATUS.json` |
| Generated projections | `tools/build_index.py`, `generated/` |
| Migration and cutover evidence | `migration/codex-cutover.md`, `migration/codex-inheritance-manifest.md`, `migration/predecessor-snapshot.md`, `migration/rollback-map.md`, `migration/source-disposition-summary.json` |

## Automatic method routing

- A request for Athena to use Thread Engine routes to **Spear**.
- A request for Athena to wield or execute an exact Sword routes to **Phoenix Blade**.
- A request for Athena to work directly through GitHub-native mechanics, recover
  from an obstructed path, or use any other safe route routes to **Aegis Break**.
- A delegated Jayson/Artemis delivery routes to **Arrow/Bow**.
- A request for Jayson to wield a Sword routes to **Oathbringer**.

The user does not need to invoke a separate preflight command or restate this
method taxonomy. Direct Athena work does not require ChatGPT Work / Codex,
Thread Engine, Oathbringer, user-run Python, or user-run PowerShell unless the
selected method explicitly requires that component.

## Generated checkpoint lifecycle

After an exact source merge, a non-generated push to `main` automatically starts
the generated publisher. Zero delta ends as a successful no-op. A complete
five-report delta invokes the singular Thread Engine, creates a generated-only
draft PR, validates its immutable head on Ubuntu and Windows, and stops for a
separate Jayson decision. Generated-only changes do not create a loop.

## Decision box

For every requested action, state objective, exact scope, source authority,
protected boundary, route, proof, stop condition, rollback, and next safe action.
If any field is unknown, investigate before mutation.

Prime command surfaces never route normal operation to `Jktomy/atlas-codex`,
Google Drive, a chat transcript, or a generated report as source truth.
