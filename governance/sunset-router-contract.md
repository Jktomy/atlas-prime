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

## Retired Mission-comment Preview ingress

The owner-only hosted Preview ingress was a campaign-scoped acceptance surface
for Mission #257. Mission #257 is complete, and its repository-wide
`issue_comment` trigger produced workflow records for unrelated comments even
though the only job was ineligible. The active workflow is therefore retired,
and `.github/workflows/sunset-router-preview-intake.yml` must remain absent.

No replacement runner guard is permitted. Starting a hosted job for every
unrelated comment would hide the notification symptom while reintroducing
unnecessary Actions use. The closed intake schema and
`tools/sunset_router/issue_preview_ingress.py` remain frozen historical evidence
and local regression fixtures only. They establish no active hosted route,
accept no new authority, and do not make Athena callable.

Current Sunset Router operation remains the deterministic local CLI documented
in `tools/sunset_router/README.md`. Any future hosted ingress requires a new,
separately authorized transport contract whose trigger does not create
repository-wide no-job runs.

The router writes only new system-temporary directories. It grants no source,
READY, merge, Quest, runtime, infrastructure, Gitea, settings, deployment, or
route-retirement authority. A branch, PR, GREEN result, READY state, merge
response, or router receipt cannot claim `SUNSET COMPLETE`. A readback receipt
requires the exact merged commit to equal canonical `main` and every planned
lifecycle path to match its payload digest.
