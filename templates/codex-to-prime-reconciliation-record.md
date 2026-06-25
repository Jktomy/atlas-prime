---
title: Codex to Prime Reconciliation Record Template
atlas_id: atlas-prime.template.codex-to-prime-reconciliation-record
format_version: "1.0"
status: PROPOSED
source_type: TEMPLATE
authority_class: TOOL_CONTRACT
owner_project: Codex
owner_operation: Source Governance
canonical_scope: Provides the required read-only Athena reconciliation structure that precedes any Atlas Codex to Atlas Prime migration packet or protected source PR.
protected_level: HIGH
routes_from:
  - specs/atlas-prime/codex-to-prime-migration-contract-v1.md
routes_to:
  - migration/atlas-codex/README.md
private_boundary: Completed records must contain clean migration analysis only. Do not paste secrets, credentials, PHI, raw finance or account evidence, private runtime values, IP addresses, network maps, device registers, raw exports, or other protected evidence.
evidence_boundary: A completed reconciliation record summarizes evidence and cites exact source identities. It does not replace Atlas Codex, current Atlas Prime source, original evidence, Spear receipts, Noctua reports, or Git lineage.
supersedes: []
cleanup_path: Keep as the current reconciliation template until replaced by a versioned successor. Completed instances belong in approved migration evidence, not in this template file.
last_verified: 2026-06-25
---

# Codex to Prime Reconciliation Record

> Template status: planning evidence only. Completion does not authorize a packet, write, merge, migration disposition, retirement, promotion, or cutover.

## 1. Record identity

- Reconciliation ID:
- Prepared by:
- Prepared at:
- Project:
- Operation:
- Migration wave:
- Approval basis:
- Current status: `DRAFT / NEEDS_JAYSON / PACKET_READY / BLOCKED`

## 2. Exact source state

### Atlas Codex

- Repository: `Jktomy/atlas-codex`
- Source branch:
- Source commit:
- Source paths:
- Git blob IDs:
- SHA-256 values:
- Complete reads confirmed: `YES / NO`

### Atlas Prime

- Repository: `Jktomy/atlas-prime`
- Base branch: `main`
- Base commit:
- Existing target paths:
- Expected target blob IDs:
- Complete reads confirmed: `YES / NO`

Stop when any required complete read is unavailable.

## 3. Controlling sources

- explicit Jayson instruction:
- Prime doctrine and format:
- Prime lifecycle and source-update standard:
- current Codex source:
- relevant Workboard rows:
- relevant session harvests:
- original evidence systems:
- Athena inference, if any:

## 4. Source meaning inventory

For each predecessor source, identify durable meaning, routing, ownership, safeguards, stale terminology, duplication, contradictions, obsolete structure, protected evidence, generated material, and unresolved meaning.

## 5. Proposed disposition

- Schema disposition: `MIGRATE / MERGE / REMODEL / GENERATED_REBUILD / HISTORICAL_REFERENCE / PRIVATE_POINTER / SUPERSEDE / RETIRE / OMIT_WITH_REASON`
- Content transfer: `FULL / PARTIAL / NONE / POINTER_ONLY / GENERATED_REBUILD`
- Reason:
- Target paths:
- Preserved elements:
- Removed or remodeled elements:
- Dependencies:
- Replacement routing:
- Private pointer:
- Omission reason:
- Approval required:

## 6. Conflict analysis

- Codex meaning:
- Prime meaning:
- Original evidence:
- Conflict:
- Recommendation:
- Safe default:
- Downstream consequences:
- Decision Box required: `YES / NO`
- Jayson decision:

Do not hide unresolved conflict inside a packet.

## 7. Route selection

Choose exactly one primary route:

- ordinary project migration packet;
- protected source PR;
- migration evidence PR;
- structured-register transition;
- generated rebuild;
- private pointer;
- blocked pending new contract.

Why this route is permitted:

Why other routes are rejected:

## 8. Proposed target source

- Create or update:
- Full-file replacement or bounded source change:
- Complete proposed content attached: `YES / NO`
- Source metadata:
- Authority class:
- Source type:
- Owner:
- Inbound route:
- Outbound routes:
- Cleanup or supersession path:

## 9. Full-file replacement controls

- complete current target read:
- expected target Git blob:
- expected target SHA-256:
- proposed SHA-256:
- required headings preserved:
- declared removals:
- removal rationale:
- deletion percentage:
- complete diff available:
- metadata validation:
- route validation:
- protected-boundary review:
- temporary-tree validation:

Any `NO` blocks replacement.

## 10. Packet or source-PR plan

- Packet ID, if applicable:
- Exact operations:
- Current S0 compatibility:
- Current writer authority: `NOT_AUTHORIZED` unless separately proven and approved
- Expected branch:
- Expected commit:
- Expected draft PR:
- Changed-filename boundary:
- Source/generated separation:
- Explicit prohibitions:

## 11. Tests and verification

- syntax:
- schema:
- metadata:
- destination policy:
- protected paths:
- routes:
- privacy screening:
- unit/adversarial tests:
- deterministic reproduction:
- full diff:
- Noctua acceptance criteria:

## 12. Recovery posture

- stale-source response:
- partial-write response:
- push-without-PR response:
- failed-check response:
- abandon/rollback response:
- protected-evidence response:
- connector-block response:

## 13. Closure requirements

- PR:
- merge commit:
- merged-main readback:
- target hashes:
- routes verified:
- inventory entry updated:
- disposition ledger updated:
- Noctua outcome:
- Noctua receipt:
- unresolved loss or conflict:
- final state:
- Phoenix Reborn obligation:

## 14. Final gate

- Result: `READY_FOR_PREVIEW / NEEDS_JAYSON / BLOCKED`
- Exact next approval phrase:
- Scope explicitly not authorized:
