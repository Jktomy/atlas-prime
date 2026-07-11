# Consistent PR Delivery Standard R01

`CONSISTENT_PR_DELIVERY_STANDARD_R01` is the canonical human-operated boundary
around Oathbringer Foundry and Oathbringer. It standardizes deterministic
compilation, exact diagnostics, evidence completion, and platform applicability
without granting a new GitHub writer or standing merge authority.

## Route

1. Preview a narrow authored-only transaction from the exact canonical base.
2. Keep package-only metadata outside both strict mission objects.
3. Compile with `Invoke-AtlasDeliveryStandard.ps1`; the wrapper invokes Foundry
   with native argument arrays and preserves stdout and stderr independently.
4. Verify the sealed carrier and the outer delivery evidence ZIP plus sidecar.
5. Run the carrier through interactive Console v2 for BUILD, REPAIR, or EXECUTE.
6. Require exact-head Ubuntu and Windows validation and a detached audit whose
   only head binding is `exact_head`.
7. Ready and merge only under explicit mission authority, then read back main.
8. If generated projections are stale, publish them in a separate transaction.

## Invariants

- `git ls-tree` records are parsed as metadata, one TAB, then the complete path.
- PowerShell uses braced interpolation before `?ref=` while StrictMode is active.
- A REPAIR declares the complete intended final path set and validates each
  source blob against the current pull-request parent tree.
- Strict Foundry and Oathbringer operation objects reject package metadata such
  as `result_blob`.
- A GitHub 404 is the explicit `MISSING` branch state, never a null-property read.
- Foundry diagnostics are retained before JSON parsing.
- A successful stop boundary cannot be reversed by nonessential later probes.
- The outer evidence archive and checksum sidecar finish on success or safe
  rejection and contain only sanitized, public-clean material.
- The operator never persists credentials and never writes directly to main.

## Failure boundary

Any base/head drift, unknown mission field, missing required workflow lane,
non-GREEN audit, evidence-integrity failure, or ambiguous remote state rejects
the transaction. Automatic retry, rollback, ready, and merge remain forbidden.
