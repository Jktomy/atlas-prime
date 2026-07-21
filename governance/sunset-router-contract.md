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
  - lifecycle/schemas/sunset-router-request-v1.schema.json
  - lifecycle/schemas/sunset-router-plan-v1.schema.json
  - lifecycle/schemas/sunset-router-receipt-v1.schema.json
private_boundary: "Router requests, plans, receipts, fixtures, and proof are public-clean. Protected facts remain represented only by sanitized summaries and bounded protected pointers."
evidence_boundary: "Router output is temporary execution evidence. Only exact merged-main lifecycle readback can establish SUNSET COMPLETE."
---

# Sunset Router contract

Sunset Router is one deterministic front door over the existing Preview-first
Atlas lifecycle engine. It does not replace lifecycle semantics, Mission Board
continuity, Operation Phoenix publication, or Jayson-controlled permanence.

## Required flow

```text
public-clean router request
→ canonical Project / Operation / Quest ownership resolution
→ exact route selection
→ lifecycle Sunset Preview
→ Jayson approval bound to the unchanged Preview
→ route-neutral approval carrier
→ exact lifecycle candidate
→ exact publication plan
→ governed draft PR
→ validation and review
→ separately authorized permanence
→ canonical lifecycle readback
→ SUNSET COMPLETE
```

## Route policy

- `ATHENA` defaults to `ATHENA_SPEAR_THREAD_ENGINE`.
- Ordered Athena fallbacks are `ATHENA_PHOENIX_BLADE` then
  `ATHENA_AEGIS_BREAK`.
- `JAYSON` and `DELEGATED_NON_ATHENA` require explicit operator-transfer
  authorization and an exact allowed route.
- `AUTO` never transfers operators.
- A failed route preserves the same Preview, approval, plan, and transaction
  identity as `BLOCKED_RESUMABLE`.

The router validates canonical ownership, current main, protected boundaries,
trusted schemas, exact candidate paths, and route identity. Candidate paths
must remain beneath `lifecycle/`, sorted, traversal-safe, drive-prefix-safe, and
case-fold unique. Every path carries an exact `ADD` or `REPLACE` action and a
payload digest; existing living Emberlines are replacements, while immutable new
records are additions.

The router writes only new system-temporary directories. It grants no source,
READY, merge, Quest, runtime, infrastructure, Gitea, settings, deployment, or
route-retirement authority. A branch, PR, GREEN result, READY state, merge
response, or router receipt cannot claim `SUNSET COMPLETE`. A readback receipt
requires the exact merged commit to equal canonical `main` and every planned
lifecycle path to match its payload digest.
