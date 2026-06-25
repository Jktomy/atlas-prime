---
title: Atlas Prime
atlas_id: atlas-prime.readme
format_version: '1.0'
status: PROPOSED
source_type: BOOTSTRAP
authority_class: CANONICAL_AUTHORED_SOURCE
owner_project: Codex
owner_operation: null
canonical_scope: Repository identity, construction authority, foundation routes, protected
  boundaries, and cutover posture for Atlas Prime.
protected_level: CRITICAL
routes_from: []
routes_to:
- .gitattributes
- .gitignore
- atlas-prime.md
- atlas-aegis.md
- atlas-knowledge-lifecycle.md
- codex/codex-source-update-standard.md
- specs/atlas-prime/repository-format-v1.md
- schemas/atlas-prime/repository-manifest-v1.schema.json
- schemas/source-metadata/source-metadata-v1.schema.json
- schemas/migration/atlas-codex-inventory-v1.schema.json
- specs/atlas-prime/codex-to-prime-migration-contract-v1.md
- migration/atlas-codex/README.md
- templates/codex-to-prime-reconciliation-record.md
- schemas/policies/atlas-prime-destination-policy-v0.2.schema.json
- schemas/policies/protected-paths-v0.2.schema.json
- policies/destination/atlas-prime-destination-policy-v0.2.yaml
- policies/protected-paths/protected-paths-v0.2.yaml
- templates/source-file.md
private_boundary: Do not store secrets, credentials, tokens, MFA or recovery codes,
  private keys, seed phrases, real .env values, PHI, raw finance or account evidence,
  private runtime values, IP addresses, network maps, device registers, protected
  exports, or other raw protected evidence in GitHub.
evidence_boundary: Original evidence systems remain authoritative outside GitHub.
  Atlas Prime stores only clean source, clean summaries, structured clean state, generated
  projections, migration provenance, and clean pointers.
supersedes: []
cleanup_path: Keep as the repository entry point. Change only through Preview -> Execute,
  a full diff, Noctua audit, Jayson manual merge, and post-merge readback.
last_verified: '2026-06-21'
---

# Atlas Prime

Atlas Prime is the shadow successor repository for Atlas clean durable source, structured continuity, governance, contracts, tools, and recovery specifications.

`Jktomy/atlas-codex` remains the canonical clean-text Atlas source until a verified and explicitly approved cutover. A file's presence in this repository does not by itself make that file governing source.

## Current repository state

```text
Repository: Jktomy/atlas-prime
State: SHADOW
Canonical predecessor: Jktomy/atlas-codex
Spear v0.2: merged compatibility contract; PLAN_ONLY authority only
Prime Spear S0: merged compiler and validation foundation; `EXECUTION_NOT_AUTHORIZED`
Phoenix Reborn: designed; real repository proof not yet complete
Cutover: not authorized
```

## Controlling source order during construction

1. Current explicit Jayson instruction.
2. The existing Athena's Spear v0.3 foundation preserved in the June 21, 2026 Sunset package.
3. The June 21 lifecycle audit and locked decisions.
4. Current merged source in `Jktomy/atlas-prime`.
5. Current `Jktomy/atlas-codex` as canonical until cutover and as migration evidence to preserve, remodel, supersede, or retire.
6. Original approved evidence sources.
7. Athena inference, clearly labeled.

Newer explicit decisions control intended v0.3 design. Older Codex terminology remains operationally canonical today but MUST NOT silently overwrite the approved Prime target architecture.

## Authority model

```text
Athena interprets, validates, ranks, and authors complete semantic content.
Spear performs registered deterministic repository mechanics only.
Noctua independently audits and verifies.
Jayson approves execution, accepts residual risk, and manually merges.
```

Preview -> Execute is required before durable source changes, migration, retirement, automation, external-system action, repository-setting changes, writer activation, or source-truth promotion.

## What PR 1A establishes

PR 1A establishes only:

- repository identity and source order;
- Aegis authority and stop conditions;
- the controlling lifecycle skeleton;
- source-update and no-orphan-file rules;
- repository topology and metadata contracts;
- repository-wide line-ending and local-artifact controls;
- zero-silent-loss migration structure;
- destination classification and protected-path policies;
- a reusable authored-source template.

PR 1A does **not**:

- migrate `atlas-codex` content;
- activate Spear writes;
- create Quest, Feather, Golden Wing, or transaction data;
- create n8n or Google Drive automation;
- prove Phoenix Reborn;
- change repository settings;
- retire Active Workboard or Emberline;
- declare Atlas Prime canonical.

## Foundation routes

- Line-ending rules: `.gitattributes`
- Existing local-artifact exclusions: `.gitignore`
- Core doctrine: `atlas-prime.md`
- Safety and authority: `atlas-aegis.md`
- Lifecycle control: `atlas-knowledge-lifecycle.md`
- Source updates: `codex/codex-source-update-standard.md`
- Repository format: `specs/atlas-prime/repository-format-v1.md`
- Repository manifest schema: `schemas/atlas-prime/repository-manifest-v1.schema.json`
- Markdown metadata schema: `schemas/source-metadata/source-metadata-v1.schema.json`
- Codex migration schema: `schemas/migration/atlas-codex-inventory-v1.schema.json`
- Codex-to-Prime migration contract: `specs/atlas-prime/codex-to-prime-migration-contract-v1.md`
- Migration evidence hub: `migration/atlas-codex/README.md`
- Reconciliation record template: `templates/codex-to-prime-reconciliation-record.md`
- Destination classification: `policies/destination/atlas-prime-destination-policy-v0.2.yaml`
- Protected paths: `policies/protected-paths/protected-paths-v0.2.yaml`
- Destination-policy schema: `schemas/policies/atlas-prime-destination-policy-v0.2.schema.json`
- Protected-path schema: `schemas/policies/protected-paths-v0.2.schema.json`
- Authored-source template: `templates/source-file.md`

## Protected boundary

GitHub may hold clean doctrine, protocols, schemas, policies, runbooks, templates, structured clean registers, generated projections, and clean pointers. Raw protected evidence remains in the appropriate original system, private vault, Google Drive/Sheets, Tiller, broker, medical record, account system, or runtime register.

When uncertain, preserve a clean pointer and keep the protected source outside GitHub.

## Cutover requirements

Atlas Prime becomes canonical only after:

1. every tracked `atlas-codex` path has an explicit migration disposition;
2. zero unexplained source loss remains;
3. Active Workboard -> Quest migration is proven record by record;
4. Emberline safeguards are absorbed before retirement;
5. Spear PLAN_ONLY and writer-pilot proofs pass;
6. Noctua verifies the whole repository and generated projections;
7. Phoenix Reborn independently proves backup, restore, and repository integrity;
8. rollback remains possible;
9. startup and source-order documents are updated;
10. Jayson explicitly approves cutover.

Until then, `atlas-prime` is a shadow rebuild and `atlas-codex` remains canonical.
