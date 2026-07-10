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

Start with `README.md`, then `bootstrap.md`, then this surface.

| Need | Canonical route |
|---|---|
| Atlas identity and canonical authority | `atlas-prime.md`, `governance/source-hierarchy.md` |
| Safety and execution boundaries | `safety/atlas-safety-doctrine.md`, `governance/noctua.md`, `governance/atlas-aegis.md` |
| Source changes | `governance/source-lifecycle.md`, `governance/change-routes.md` |
| Projects | `projects/project-registry.md` |
| Operations | `operations/operation-registry.md` |
| Artemis, Hermes, Nexus | `operations/artemis-runtime-and-routing.md` |
| Protocols and delivery methods | `operations/protocol-library.md`, `methods/` |
| Active Quests | `quest-board/quest-board-v1.json`, `quests/` |
| Infrastructure source | `infrastructure/atlas-infrastructure-source.md` |
| Backup, restore, recovery, rollback | `recovery/phoenix-recovery.md`, `migration/rollback-map.md` |
| Knowledge lifecycle | `knowledge/atlas-source-compendium.md` |
| Thread Engine | `tools/thread-engine/README.md`, `tools/thread-engine/PRIME-PORT-STATUS.json` |
| Sword/Oathbringer | `tools/atlas-sword/README.md` |
| Generated projections | `tools/build_index.py`, `generated/` |
| Migration and cutover evidence | `migration/` |

## Decision box

For every requested action, state: objective, exact scope, source authority, protected boundary, route, proof, stop condition, rollback, and next safe action. If any field is unknown, investigate before mutation.

After final cutover, Prime command surfaces never route normal operation to `Jktomy/atlas-codex`, Google Drive, a chat transcript, or a generated report as source truth.
