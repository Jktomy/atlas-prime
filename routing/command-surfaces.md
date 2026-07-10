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
| Capability parity and acceptance | `governance/capability-parity-register.json`, `schemas/capability-parity-register.schema.json`, `governance/capability-acceptance-contract.md` |
| Source changes and route selection | `governance/source-lifecycle.md`, `governance/change-routes.md` |
| Projects | `projects/project-registry.md` |
| Operations | `operations/operation-registry.md` |
| Artemis, Hermes, Nexus | `operations/artemis-runtime-and-routing.md` |
| Protocols and delivery methods | `operations/protocol-library.md`, `methods/artemis-bow-and-arrow.md`, `methods/athenas-spear.md`, `methods/atlas-sword.md`, `methods/phoenix-blade.md` |
| Athena direct construction or repair | `methods/phoenix-blade.md`, then the exact live repository or PR state |
| Sword or Oathbringer request | `methods/sword-forge-standard.md`, `methods/sword-lessons.json`, `methods/atlas-sword.md`, `tools/atlas-sword/README.md`, then the exact live repository or PR state |
| Oathbringer Foundry carrier compile | `methods/oathbringer-foundry.md`, `methods/sword-forge-standard.md`, `methods/sword-lessons.json`, `tools/oathbringer-foundry/README.md`, then exact current source and read-only live-state binding |
| Active Quests | `quest-board/quest-board-v1.json`, `quests/` |
| Infrastructure source | `infrastructure/atlas-infrastructure-source.md` |
| Backup, restore, recovery, rollback | `recovery/phoenix-recovery.md`, `migration/rollback-map.md` |
| Knowledge lifecycle | `knowledge/atlas-source-compendium.md` |
| Thread Engine | `tools/thread-engine/README.md`, `tools/thread-engine/PRIME-PORT-STATUS.json` |
| Routing registry | `routing/command-surfaces.md` |
| Reusable templates | `templates/preview-bundle-template.md`, `templates/project-template.md`, `templates/protocol-template.md`, `templates/source-file-template.md`, `templates/support-file-template.md` |
| Proven delivery evidence | `proof/prime-thread-engine-bootstrap-proof.md`, `proof/prime-spear-arrow-bow-parity-r01.md` |
| Generated projections | `tools/build_index.py`, `generated/` |
| Migration and cutover evidence | `migration/codex-cutover.md`, `migration/codex-inheritance-manifest.md`, `migration/predecessor-snapshot.md`, `migration/rollback-map.md`, `migration/source-disposition-summary.json` |

## Automatic method routing

A request for Athena to construct or repair Atlas directly routes to Phoenix Blade without requiring ChatGPT Work / Codex, Thread Engine, or Oathbringer.

A request to build, repair, recover, execute, or otherwise make a Sword automatically routes first through `methods/sword-forge-standard.md` and `methods/sword-lessons.json`, then through current Sword/Oathbringer doctrine and implementation source, and finally through exact live GitHub target state. The user does not need to invoke a separate preflight command or remind Athena to recall earlier lessons.

## Decision box

For every requested action, state: objective, exact scope, source authority, protected boundary, route, proof, stop condition, rollback, and next safe action. If any field is unknown, investigate before mutation.

Prime command surfaces never route normal operation to `Jktomy/atlas-codex`, Google Drive, a chat transcript, or a generated report as source truth.
