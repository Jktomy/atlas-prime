---
title: Spear/Bow Gates 1-2 Execution Convergence Record
atlas_id: atlas-prime.migration.spear-bow-convergence.2026-06-29
format_version: "1.0"
status: COMPLETE
source_type: MIGRATION_RECORD
authority_class: MIGRATION_EVIDENCE
owner_project: Codex
owner_operation: Atlas Prime Rebuild Program
canonical_scope: Records the CLI-primary Gates 1-8 decision, exact Gates 1-2 Build and Execute lineage, verified Codex and Prime merged-main state, canonical Codex continuity closeout, authority boundaries, and the Gate 3 handoff.
protected_level: HIGH
routes_from:
  - specs/spear/spear-execution-convergence-v1.md
  - migration/atlas-codex/atlas-prime-rebuild-program-roadmap-v1.md
routes_to:
  - quest-board/quest-board-shadow-v1.json
  - tools/spear/operator-runbook.md
  - tools/spear/recovery-runbook.md
private_boundary: This record contains clean program continuity only and must not include credentials, PHI, raw finance or account evidence, private runtime values, network maps, device registers, or protected exports.
evidence_boundary: Arrow manifests, receipts, commits, PRs, Noctua reports, merged-main readback, and the canonical Codex closure harvest remain primary execution evidence.
supersedes: []
cleanup_path: Retain as the completed Gates 1-2 migration record and absorb stable semantics into Gate 3 contracts, the roadmap, and runbooks through separately reviewed transactions.
last_verified: 2026-06-29
---

# Spear/Bow Gates 1-2 Execution Convergence Record

## Controlling decision

Bow and Arrow CLI is the primary repository-mutation route for Atlas Prime Rebuild Gates 1-8.

The long-term hierarchy remains:

```text
Athena prepares and attempts supported remote operation
-> Artemis Local Operator performs approved local execution when available
-> Jayson is the final manual fallback
```

Jayson remains the ultimate authority and operates the Bow until Artemis is proven and activated.

## Exact pre-transaction state

```text
Codex main: 091c7e88f6403e93a9016670cb5a872b4c8d0c7d
Prime main: 0d2249b864a90804605b7bfa47ac189e51d3e431
Codex authority: CANONICAL
Prime state: SHADOW
```

## Exact Gates 1-2 convergence lineage

### Codex execution-convergence source

- PR: `Jktomy/atlas-codex#184`
- approved PR head: `43a5a9295604be1d5aa8fb2a9b43675541075cee`
- squash merge / verified Codex `main`: `29e1b156316819f87511589bdca58ad120f787e3`

### Prime execution-convergence source

- PR: `Jktomy/atlas-prime#25`
- approved PR head: `1e5211cd1de00b70188a3a413d845826d898c624`
- squash merge / verified Prime `main`: `525dfe23d130415f6acbba9ffd5e42d1bdee3fd8`

### Canonical Codex continuity closeout

- PR: `Jktomy/atlas-codex#185`
- approved PR head: `1eabc24046a777ccba44d9d8c33bbcc2cf2a5b80`
- squash merge / verified canonical Codex `main`: `30b0f33ff571f8c2a7798224c34051781129b921`
- canonical Workboard: `codex/atlas-active-workboard.md`
- closure harvest: `session-harvests/2026-06-29-gates-1-2-execution-convergence-closure.md`

Independent readback confirmed each listed merge commit was identical to the corresponding repository `main` at its completion gate.

## Execution result

Gates 1-2 established:

1. Athena prepares exact source intent and candidate bytes.
2. Bow and Arrow CLI is the approved primary repository-mutation route for Gates 1-8.
3. Jayson physically operates the Bow until Artemis Local Operator is separately implemented, proven, and activated.
4. Build and Execute Arrows are separately sealed and separately approved.
5. Exact audited PR heads bind Execute authority.
6. Cross-repository work preserves successful partial state and stops on later failure.
7. Merged-main readback and machine-readable receipts are required completion evidence.
8. Codex remains canonical and Prime remains SHADOW.
9. S1 remains disabled and Artemis Local Operator remains inactive.

The canonical Codex closure harvest preserves the detailed failed attempts, recovery lessons, and reusable runner safeguards.

## Current non-authority

This record does not activate S1, grant Artemis execution authority, authorize Gate 3 mutation, begin Gates 4-8 execution, migrate C07 content, promote Prime, retire Codex, delete evidence, modify Google Drive, or perform cutover.

## Gate 3 handoff

```text
verified Gates 1-2 merged-main state
-> canonical Codex continuity closeout
-> Prime SHADOW continuity synchronization
-> Gate 3 runner-neutral transaction and common receipt contracts
-> Gate 4 GitHub-native Spear Build proof
-> Gate 5 equivalent local Bow Build proof
-> Gate 6 Artemis read-only validation
-> Gate 7 recovery and coordinated-transaction proof
-> Gate 8 bounded migration beginning with C07
```

The next safe action is to prepare the exact Gate 3 file inventory, schemas, valid and invalid fixtures, Noctua validation profile, and Build Arrow Preview, then stop before mutation.
