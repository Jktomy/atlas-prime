# RP-C08 AJ-11 clean-clone recovery acceptance R08

AJ-11 is proposed as `PROVEN` from the exact read-only Oathbringer clean-clone
proof `RP-C08-AJ11-FINAL-MAIN-CLEAN-CLONE-PROOF-R02` at canonical main
`af97c00df41be8943ba5d4c942a8ecc2c5aff822`. This authored reconciliation changes only AJ-11's controlling
disposition.

## Accepted evidence

The proof expected and observed the same canonical SHA before clone, in the
isolated clone, and after final remote readback:

```text
af97c00df41be8943ba5d4c942a8ecc2c5aff822
```

The clone used canonical origin `https://github.com/Jktomy/atlas-prime.git`,
default branch `main`, detached exact HEAD, no inherited hooks, no inherited
worktrees, and a clean working tree before and after execution.

All 13 validation commands passed, including the Prime kernel, repository
policy, privacy boundary, 63 lifecycle contracts, 105 Thread Engine tests,
Thread Engine and Sword static checks, 33 generator tests, 245 whole-program
tests, Athena execution routes, source validation, continuity validation, and
the native PowerShell resolver self-test.

Separate-output deterministic regeneration proved all five generated
projections byte-identical to committed generated state:

```text
GENERATED_STATUS=CURRENT
CHANGED_GENERATED_PATHS=NONE
```

The proof classified every `atlas-codex` reference as historical/doctrinal,
test/fixture, or predecessor provenance only. Normal recovery targets
`Jktomy/atlas-prime`; normal `atlas-codex` dependency is false. Source rollback
requires a new reviewed PR. Force push and history rewrite remain forbidden.

## Evidence integrity

```text
receipt self-hash:
5907e446bee11a013e8fa5202e1f712af8e922ea5b72621ae129b936d5ec9b45

final receipt file SHA-256:
1976b29f9a05a93d86a887e63edd960b19f91967ee916e719aff44728f82240c

transcript SHA-256:
c2f595f73c89ef2af2050b53ffbf14aba8d59f5b18d32ce1e6e3063576eba93f

mission SHA-256:
a6b8aa742339c82a68189128e197d4ca7b410ffed330a2a438b8af274ca7f313
```

Detached audit independently verified the receipt self-hash contract, final
receipt sidecar, mission binding, stage sequence, exact generated hashes,
thirteen passing results, absence of exposed credential material, unchanged
canonical main, and absence of a proof-created branch or pull request.

## Preserved boundaries

AJ-12 remains `UNPROVEN`. CAP-027 remains the sole `STILL_MISSING` capability
and now depends only on AJ-12. RP-C08 and Repairing Prime remain `IN_PROGRESS`.
Capability counts do not change. This authored candidate contains no generated
files and grants no standing authority, automatic ready, automatic merge,
direct-main write, force push, cleanup, Quest completion, or reusable account
authority.

After this reconciliation is separately reviewed and merged, generated state
must become current through the normal generated-only checkpoint or a truthful
zero-delta result. AJ-12 then requires the complete Prime validation matrix on
Ubuntu and Windows at one exact final merged-main SHA.
