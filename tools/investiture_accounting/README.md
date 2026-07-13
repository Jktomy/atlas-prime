# Found Silverlight Investiture Accounting construction

This package is the deterministic construction substrate for FS-C01-M02 and
FS-C01-M03. It validates public-clean event shapes, maintains one immutable
hash-chained ledger generation in an explicitly supplied external store,
emits sanitized receipts and summaries, binds lifecycle events to prior usage
events without recounting them, and supports explicit interruption,
generation-recovery, and rollback planning.

It does not select a private store, activate a provider, acquire credentials,
assert real usage, promote an FS-C01 gate, or confer permanence. M02 and M03
remain unproven until a separate authored acceptance transaction binds the
merged construction head, canonical exercise, exact-head CI, and detached
review.

## Safety boundary

- Every store command requires an explicit absolute root; there is no default
  or environment fallback.
- Initialization requires a new external directory. Repository-contained,
  repository-containing, symlink, junction, mount-point, reparse-point, and
  hard-linked ledger paths fail closed.
- Mutations hold stable operating-system directory handles for the store and
  every ledger child. Linux writes are resolved through descriptor-backed
  paths; Windows handles deny rename/delete sharing. Root and child identities
  are rechecked before release. POSIX file and directory metadata is flushed;
  Windows file buffers are flushed and no-clobber publications use a
  write-through move.
- Receipts and errors contain stable identifiers, digests, counts, booleans,
  and state only. Absolute paths and raw malformed input are never emitted.
- `USAGE_REPORTED` is the only event that may contribute BEU. Lifecycle events
  may bind earlier usage-event IDs and never bind provider receipts directly.
- Append requires an exact expected head. Replay, stale head, duplicated event,
  request, provider usage scope, or source receipt does not append.
- Interruption intent is explicit. Windows holds the persistent one-byte lock
  without delete sharing; POSIX locks the already-held stable root-directory
  inode, so replacing the `append.lock` pathname cannot split serialization.
  The operating system releases either lock when its process exits; recovery never
  guesses, clears lock state, or repeats a confirmed record. Immutable intents
  and receipts use flushed no-clobber staging, remain available for exact
  recovery and audit, and cannot expose a partially written final filename.
- Generation recovery creates a new external generation linked to the last
  verified record and leaves the source bytes untouched. Rollback planning is
  read-only and leaves owner-managed selection to the external authority.

## Commands

```text
python -B -m tools.investiture_accounting validate-event --event FILE
python -B -m tools.investiture_accounting init --store-root NEW_ROOT --ledger-id ID --generation-id ID --created-at UTC --request-id ID
python -B -m tools.investiture_accounting append --store-root ROOT --expected-head SHA256 --request-id ID --event FILE
python -B -m tools.investiture_accounting verify --store-root ROOT
python -B -m tools.investiture_accounting summarize --store-root ROOT --scope-id GENERATION_ID
python -B -m tools.investiture_accounting recover-interrupted --store-root ROOT --request-id ID --expected-head SHA256
python -B -m tools.investiture_accounting recover-generation --source-root ROOT --destination-root NEW_ROOT --expected-valid-head SHA256 --new-generation-id ID --created-at UTC --request-id ID
python -B -m tools.investiture_accounting rollback-plan --current-root ROOT --target-root ROOT --expected-current-head SHA256 --expected-target-head SHA256
```

`ZERO_MODEL` proves exactly zero with no provider, model, runtime, Light,
receipt, usage scope, or category. `UNAVAILABLE` never becomes zero. `PARTIAL`
exposes only a known subtotal. Countable usage chooses exactly one authoritative
total or explicitly disjoint counted leaves; overlapping categories remain
informational.
