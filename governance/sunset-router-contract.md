---
title: "Sunset Router Contract"
atlas_id: "prime.governance.sunset-router"
status: "CANDIDATE"
source_type: "PROTOCOL"
authority_class: "CANONICAL_AUTHORED_SOURCE"
owner_project: "Project Codex"
owner_operation: "Operation Source Governance"
protected_level: "CRITICAL"
routes_from:
  - governance/mission-board-contract.md
  - lifecycle/lifecycle-contract.md
  - routing/command-surfaces.md
routes_to:
  - tools/sunset_router/README.md
  - tools/sunset_router/issue_preview_ingress.py
  - lifecycle/schemas/sunset-router-request-v1.schema.json
  - lifecycle/schemas/sunset-router-plan-v1.schema.json
  - lifecycle/schemas/sunset-router-receipt-v1.schema.json
  - lifecycle/schemas/sunset-router-preview-intake-v1.schema.json
private_boundary: "Router requests, plans, receipts, fixtures, and proof are public-clean. Protected facts remain sanitized summaries and bounded pointers."
evidence_boundary: "Router output is temporary execution evidence. Only exact merged-main lifecycle readback can establish SUNSET COMPLETE."
---

# Sunset Router contract

Sunset Router is one deterministic front door over the existing Preview-first
Atlas lifecycle engine. It does not replace lifecycle semantics, Mission Board
continuity, Operation Phoenix publication, or Jayson-controlled permanence.

## Required flow

```text
public-clean router request
-> canonical Project / Operation / Quest ownership resolution
-> exact route selection
-> lifecycle Sunset Preview
-> Jayson approval bound to the unchanged Preview
-> route-neutral approval carrier
-> exact lifecycle candidate
-> exact publication plan
-> governed draft PR
-> validation and review
-> separately authorized permanence
-> canonical lifecycle readback
-> SUNSET COMPLETE
```

## Current GitHub route policy

- `ATHENA` with `AUTO` selects `ATHENA_AEGIS_BREAK`.
- Its automatic same-operator fallback is `ATHENA_PHOENIX_BLADE`.
- `ATHENA_SPEAR_THREAD_ENGINE` remains schema-readable for historical records but
  a new current-GitHub request selecting it rejects before mutation with
  `CURRENT_GITHUB_SPEAR_RETIRED`.
- Explicit Aegis Break or Phoenix Blade selection retains route identity and the
  other current Athena method as its fallback.
- `JAYSON` and `DELEGATED_NON_ATHENA` require explicit operator-transfer
  authorization and an exact allowed route.
- `AUTO` never transfers operators.
- A failed route preserves the same Preview, approval, plan, candidate bytes,
  and transaction identity.

Aegis Break is the primary method, not the lifecycle-byte author or a standing
publisher. The lifecycle engine owns deterministic lifecycle bytes. The exact
selected substrate must preserve Candidate Seal, base, paths, tree, draft-PR
stop, validation, review, rollback, and readback.

The router validates canonical ownership, current main, protected boundaries,
trusted schemas, exact candidate paths, and route identity. Candidate paths
remain beneath `lifecycle/`, sorted, traversal-safe, drive-prefix-safe, and
case-fold unique. Every path carries exact `ADD` or `REPLACE` action and payload
digest.

## Retired Mission-comment Preview ingress

The owner-only hosted Preview ingress was campaign-scoped acceptance for Mission
#257. Mission #257 is complete and
`.github/workflows/sunset-router-preview-intake.yml` remains absent so unrelated
Issue comments do not create no-job workflow failures.

The closed intake schema and `tools.sunset_router.issue_preview_ingress` adapter
remain frozen historical evidence and local regression fixtures only. They
establish no active hosted route, accept no new authority, and do not make Athena
callable. Restoring hosted ingress requires a separately authorized transport
contract whose trigger avoids repository-wide no-job runs.

## Completion boundary

The router writes only new system-temporary directories. It grants no source,
READY, merge, Quest, runtime, infrastructure, Gitea, settings, deployment, or
route-retirement authority. A branch, PR, GREEN result, READY state, merge
response, or router receipt cannot claim `SUNSET COMPLETE`. A readback receipt
requires the exact merged commit to equal canonical `main` and every planned
lifecycle path to match its payload digest.
