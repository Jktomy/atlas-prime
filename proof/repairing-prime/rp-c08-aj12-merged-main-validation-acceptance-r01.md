# RP-C08 AJ-12 merged-main validation acceptance R01

AJ-12 is proposed as `PROVEN` from one owner-authorized read-only
`workflow_dispatch` of the complete Prime validation matrix against exact
canonical `main`:

```text
repository: Jktomy/atlas-prime
workflow: .github/workflows/prime-readonly-validation.yml
run: 29455372822
exact SHA: 043648a85cf581d7805355a71cc819fdb83e738b
Ubuntu job: 87487269033 — SUCCESS
Windows job: 87487269036 — SUCCESS
```

This authored reconciliation changes only AJ-12's controlling disposition. It
does not promote CAP-027, complete RP-C08, complete Repairing Prime, change
capability counts, or grant standing authority.

## Accepted evidence

Jayson separately authorized AJ-12 execution after canonical generated state
became current. The workflow was dispatched at `main` and bound to exact merged
main `043648a85cf581d7805355a71cc819fdb83e738b`.

Both operating-system jobs completed successfully. Every substantive matrix
stage passed on both Ubuntu and Windows:

1. Prime kernel checks.
2. Prime repository policy tests.
3. Prime privacy boundary tests.
4. Prime lifecycle contract tests.
5. Full Prime Thread Engine tests.
6. Thread Engine static checks.
7. Atlas Sword static checks.
8. Prime generator tests.
9. Prime whole-program tests.
10. Athena execution route tests.
11. Prime source validation.
12. Active PowerShell launcher resolution.

The workflow carries repository `contents: read` permission only. The run
created no source branch, commit, pull request, ready transition, merge,
settings change, force push, cleanup action, capability promotion, or Quest
completion.

Fresh post-run readback resolved canonical `main` to the same exact SHA:

```text
043648a85cf581d7805355a71cc819fdb83e738b
```

## Evidence identity

```text
workflow run:
https://github.com/Jktomy/atlas-prime/actions/runs/29455372822

Ubuntu job ID:
87487269033

Windows job ID:
87487269036
```

A detached read-only inspection of the completed run verified that both jobs
reported `completed/success`, every listed step reported success, and canonical
main remained the bound merged-main SHA.

## Preserved boundaries

CAP-027 remains the sole `STILL_MISSING` capability pending its own separately
authorized final capability reconciliation. RP-C08 and Repairing Prime remain
`IN_PROGRESS`. Capability counts remain 14 RESTORED, 7 IMPROVED, 4 PRESERVED,
1 REPLACED, 1 INTENTIONALLY_RETIRED, 0 BLOCKED, and 1 STILL_MISSING.

This candidate contains no generated files and grants no automatic ready,
automatic merge, direct-main write, force push, cleanup, Quest completion, or
reusable settings authority. The candidate requires exact-head Ubuntu/Windows
PR validation and a fresh detached review before any permanence authorization.

After separate merge authorization, generated state must become current through
the normal generated-only checkpoint or a truthful zero-delta result. The next
bounded authored transaction is CAP-027 and RP-C08 final capability
reconciliation without self-completing the Quest.
