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
| Athena execution-route parity and hosted identity | `governance/athena-execution-route-contract.md`, `schemas/athena-hosted-route-request-v1.schema.json`, `schemas/athena-hosted-route-receipt-v1.schema.json`, `tools/athena_routes/README.md` |
| Ordinary free-form mission fields to immutable carrier | `python -B -m tools.athena_routes.free_form_intake --fields <fields.json> --output-dir <new-directory>`; closed inputs/receipt use `schemas/athena-free-form-mission-fields-v1.schema.json` and `schemas/athena-free-form-intake-receipt-v1.schema.json`; constructor is local, read-only, non-promoting, and explicitly not fresh Work/Athena origin |
| Guided Spear Preview and Execute | `python -B -m tools.athena_routes.guided_publisher preview|execute`; Execute requires a new durable receipt path, journals no-retry intent before dispatch, and uses the hosted mission/base lock; current closed receipts are defined by `schemas/athena-guided-intake-preview-v2.schema.json` and `schemas/athena-guided-intake-execute-receipt-v1.schema.json`, while Preview v1 remains immutable historical evidence; component presence does not prove CAP-010 |
| RP-C01-M05 same-carrier parity evidence | `tools.athena_routes.m05_parity`, `schemas/rp-c01-m05-parity-evidence-v1.schema.json`; verifies exact Preview/Execute/hosted/compiler/adapter joins from one singular execution and cannot self-promote M05 |
| Agent identity and capability warrants | `governance/agentic-warrant-contract.md`, `schemas/agentic-capability-warrant-v1.schema.json`, `schemas/agentic-approval-record-v1.schema.json`, `schemas/agentic-warrant-receipt-v1.schema.json` |
| Shardplate work-surface and Shardblade permanence contract (`CONTRACT_ONLY_NOT_ACTIVATED`) | `governance/shard-doctrine.md`, `schemas/shardblade-permanence-request-v1.schema.json`, `schemas/shardblade-permanence-approval-v1.schema.json`, `schemas/shardblade-permanence-receipt-v1.schema.json`, `tools/agentic_warrants/permanence.py` |
| Investiture source identity and Light-name migration | `governance/investiture-source-identity-contract.md` |
| Deterministic conservation and generated-checkpoint route | `governance/deterministic-conservation-contract.md`, `.github/workflows/generated-checkpoint-publisher.yml`, `tools/generated_checkpoint/README.md`; AJ-09 acceptance is recorded in `proof/repairing-prime/rp-c06-generated-parity-acceptance-r01.md` |
| Chromelight provider evidence and account boundary | `governance/chromelight-provider-boundary.md`, `schemas/chromelight-evidence-register-v1.schema.json`, `proof/repairing-prime/rp-c03-chromelight-evidence-r01.json` |
| Resonance independent finding reconciliation | `governance/resonance-reconciliation-contract.md`, `schemas/resonance-finding-v1.schema.json`, `schemas/aberration-register-v1.schema.json`, `tools/resonance/README.md`, `proof/repairing-prime/rp-c04-aberration-register-r01.json` |
| Source changes and route selection | `governance/source-lifecycle.md`, `governance/change-routes.md` |
| Projects | `projects/project-registry.md` |
| Operations | `operations/operation-registry.md` |
| Artemis, Hermes, Nexus | `operations/artemis-runtime-and-routing.md` |
| Protocols and delivery methods | `operations/protocol-library.md`, `methods/artemis-bow-and-arrow.md`, `methods/athenas-spear.md`, `methods/atlas-sword.md`, `methods/phoenix-blade.md` |
| Athena direct construction or repair | `methods/phoenix-blade.md`, then the exact live repository or PR state |
| Sword or Oathbringer request | `methods/sword-forge-standard.md`, `methods/sword-lessons.json`, `methods/atlas-sword.md`, `tools/atlas-sword/README.md`, then the exact live repository or PR state |
| Oathbringer Foundry carrier compile | `methods/oathbringer-foundry.md`, `methods/sword-forge-standard.md`, `methods/sword-lessons.json`, `tools/oathbringer-foundry/README.md`, then exact current source and read-only live-state binding |
| Active Quests | `quest-board/quest-board-v1.json`, `quests/` |
| Quest identities and unfinished-work continuity | `governance/quest-engine-continuity-contract.md`, `continuity/quest-engine-identities-r01.json`, `continuity/prime-continuity-register-r01.json`, `tools/prime_continuity/README.md` |
| Validate continuity or surface Argus | `python -B -m tools.prime_continuity.cli validate`, `python -B -m tools.prime_continuity.cli argus` |
| Preview one bounded continuity update | `python -B -m tools.prime_continuity.cli plan-update ...`; candidate only, then reviewed draft-PR route |
| Emberline, Sunset, or Sunrise | `python -B -m tools.prime_continuity.cli emberline|sunset|sunrise ...`; projections/evidence never govern |
| Lifecycle records and read-only mechanics | `lifecycle/README.md`, `lifecycle/lifecycle-contract.md`, `lifecycle/schemas/`, `tools/atlas_lifecycle/README.md` |
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
