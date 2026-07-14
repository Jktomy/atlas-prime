# Consistent PR Delivery Standard R01

`CONSISTENT_PR_DELIVERY_STANDARD_R01` is the canonical human-operated boundary
around Oathbringer Foundry and Oathbringer. It standardizes deterministic
compilation, exact diagnostics, evidence completion, platform applicability,
and the one-ZIP operator handoff without granting a new GitHub writer or
standing merge authority.

## Route

1. Preview a narrow authored-only transaction from the exact canonical base.
2. Keep package-only metadata outside both strict mission objects.
3. Validate the complete Foundry input and compile the sealed carrier before
   beginning the expensive mission-wide test suite; a packaging or source-lock
   defect must fail early.
4. Compile with `Invoke-AtlasDeliveryStandard.ps1`; the wrapper invokes Foundry
   with native argument arrays and preserves stdout and stderr independently.
5. Verify the sealed carrier and the outer delivery evidence using its ZIP,
   sidecar, and an independently supplied expected SHA-256.
6. Run the applicable source and regression validation suite, then reverify that
   the unchanged carrier SHA-256 is still the audited carrier.
7. Generate the Foundry operator handoff only after carrier verification. Deliver
   the unchanged carrier as the single Jayson download plus one fixed-shape
   PowerShell 7 paste command; do not generate a second outer ZIP or a separate
   mission-specific bootstrap script.
8. Run the carrier through interactive Console v2 for BUILD, REPAIR, or EXECUTE.
9. Require exact-head Ubuntu and Windows validation and a detached audit whose
   only head binding is `exact_head`.
10. Ready and merge only under explicit mission authority, then read back main.
11. If generated projections are stale, publish them in a separate transaction.

## Invariants

- `git ls-tree` records are parsed as metadata, one TAB, then the complete path.
- PowerShell uses braced interpolation before `?ref=` while StrictMode is active.
- A REPAIR declares the complete intended final path set and validates each
  source blob against the current pull-request parent tree.
- Strict Foundry and Oathbringer operation objects reject package metadata such
  as `result_blob`.
- A GitHub 404 is the explicit `MISSING` branch state, never a null-property read.
- Foundry diagnostics are retained before JSON parsing.
- Foundry compilation and carrier verification precede expensive mission-wide
  validation; successful validation is followed by an unchanged-carrier digest
  readback.
- The operator handoff command is generated from one canonical template. Only
  the safe carrier filename and lowercase SHA-256 may vary.
- The handoff verifies the complete carrier digest before extraction, uses a
  unique workspace, and stores durable receipt or Deflected Sword evidence under
  `Downloads/Atlas-Oathbringer-Evidence`.
- Console v2 remains the one canonical Oathbringer presentation component under
  `tools/atlas-sword/engine/`; Foundry embeds it without duplicating it.
- A successful stop boundary cannot be reversed by nonessential later probes.
- The outer evidence archive and checksum sidecar finish on success or safe
  rejection and contain only sanitized, public-clean material.
- Evidence verification enforces the trusted receipt identity, exact member and
  path contract, bounded stored bytes and JSON depth, and independent
  expected-digest/sidecar/archive agreement; internal self-consistency alone is
  never proof of authenticity.
- The operator downloads one carrier ZIP. Sidecars and outer evidence remain
  Forge evidence unless separately needed for investigation.
- The operator never persists credentials and never writes directly to main.

## Failure boundary

Any base/head drift, unknown mission field, missing required workflow lane,
non-GREEN audit, evidence-integrity failure, carrier digest drift, unsafe handoff
input, or ambiguous remote state rejects the transaction. Automatic retry,
rollback, ready, and merge remain forbidden.
