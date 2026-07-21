---
title: "Atlas Mission Board Contract"
atlas_id: "prime.governance.mission-board"
status: "CANONICAL_ACTIVE"
source_type: "PROTOCOL"
authority_class: "CANONICAL_AUTHORED_SOURCE"
owner_project: "Project Codex"
owner_operation: "Operation Source Governance"
protected_level: "CRITICAL"
routes_from:
  - routing/command-surfaces.md
  - operations/operation-registry.md
routes_to:
  - schemas/mission-v1.schema.json
  - tools/mission_board/README.md
  - recovery/elantris-recovery.md
  - governance/repository-process-contract.md
  - lifecycle/lifecycle-contract.md
  - quest-board/quest-board-v1.json
private_boundary: "Mission Issues, comments, templates, fixtures, receipts, and archive packages are public-clean. Protected facts remain in approved private evidence systems and are represented only by sanitized summaries and bounded protected pointers."
evidence_boundary: "Issue state coordinates work. Only merged canonical source and exact readback establish accepted doctrine or source completion; package presence does not prove Coppermind runtime archival."
---

# Atlas Mission Board contract

## Identity and purpose

The **Mission Board** is the GitHub Issues system in `Jktomy/atlas-prime` and,
after a separately proven migration, the corresponding Gitea Issues system.
`Mission #N` means Issue `#N` in the explicitly resolved repository. A pull
request, Project item, Quest Board row, chat, file, database record, or custom
service is not a Mission Issue.

The Mission Board is the durable public-clean intake, continuity, assignment,
sequencing, restart, progress, and execution-record surface for unfinished Atlas
work. It allows Jayson to state an objective without choosing a publisher. The
assigned worker resolves the safe internal route from current source and live
state.

## Authority separation

| Surface | Authority |
|---|---|
| Mission Board | Visible intake, assignment, discussion, sequencing, queue state, restart context, and linked evidence |
| Merged Prime `main` | Canonical doctrine and accepted repository source |
| Quest Board and continuity register | Current admitted-Quest registry and unfinished Quest continuity until a separately proven atomic cutover |
| Operation Phoenix | Governed branch/PR publication and canonical-source maintenance; future Gitea work remains pre-cutover |
| Operation Coppermind | Structured operational history, retrieval context, and archival records after applicable gates |
| Operation Harmony / Emberdark | Governed execution, private integration mediation, event processing, mission-state plumbing, idempotency, retry, quarantine, reconciliation, audit receipts, and controlled exports |

An Issue can describe intended, pending, blocked, or completed work, but it never
silently outranks merged Prime. Issue closure does not imply `CANONICAL`,
`COPPERMIND_ARCHIVED`, Quest completion, or `SUNSET COMPLETE`.

## Closed Mission model

Every Mission uses `schemas/mission-v1.schema.json` and records repository,
Issue number, stable Mission ID, type, state, timestamps, objective, rationale,
ownership, Quest/Campaign/Gate relationships, assigned worker, separate execution
identity, dependencies, public-clean boundary, acceptance criteria, next safe
action, effort class, queue behavior, canonical-source state, branch/PR/head/path
bindings, validation and review, Coppermind disposition, completion proof,
rollback, and replay-resistant attempt identity.

### Types

```text
mission/sunset
mission/quest
mission/campaign
mission/gate
mission/controlled-burn
mission/phoenix-burn
mission/repair
mission/research
mission/migration
mission/generated-refresh
```

The vocabulary is deliberately small and portable. A new type requires a
reviewed schema and contract change; labels cannot extend the semantic model.

### Mission states

```text
CAPTURED
→ TRIAGED
→ READY
→ IN_PROGRESS
→ PR_OPEN
→ VALIDATING
→ READY_FOR_PERMANENCE
→ CANONICAL
→ COPPERMIND_ARCHIVED
→ CLOSED
```

`BLOCKED_RESUMABLE` is reachable from active pre-canonical states and may return
only through an explicit resumed transition. Validation repair may move
`VALIDATING → PR_OPEN`; changed candidate bytes require renewed validation,
review, Strikeforce, READY, and readback. `CLOSED` is terminal.

No-source-change Missions may move `IN_PROGRESS → CANONICAL` while keeping the
separate canonical-source status `NO_SOURCE_CHANGE_REQUIRED`. They still require
completion proof and an archival disposition before `CLOSED`.

### Canonical-source states

```text
PHOENIX_PENDING
→ PR_OPEN
→ MERGED_PENDING_READBACK
→ CANONICAL
```

`PHOENIX_PENDING → NO_SOURCE_CHANGE_REQUIRED` is the only no-source branch.
General Mission state never substitutes for this source-authority state. A merge
API response can establish only `MERGED_PENDING_READBACK`; exact canonical-main
readback is required for `CANONICAL`.

## Dependencies and ordered queues

Every dependency names one exact relation:

```text
BLOCKS
BLOCKED_BY
PARALLEL_WITH
NONBLOCKING_RELATED
PARENT_OF
CHILD_OF
```

Issue number, numerical order, shared Quest or Campaign, shared worker, label,
creation date, and conversation order create no dependency. An unfinished Quest
Mission does not block an unrelated Sunset Mission.

For `complete Missions 5, 7, and 12 sequentially`, the numbers define processing
order only. The worker fresh-reconciles each Mission, completes or truthfully
blocks it, posts evidence, and then evaluates the next requested item. It may
continue past `BLOCKED_RESUMABLE` only when the blocked Mission declares
`CONTINUE_IF_BLOCKED_RESUMABLE` and no explicit blocking dependency reaches the
remaining queue. Otherwise it stops and reports the exact edge.

Repository objects `#5`, `#7`, and `#12` in current `Jktomy/atlas-prime` history
are pull requests, not Mission Issues. A live instruction naming them as Missions
must fail at `#5` with `IDENTITY_MISMATCH` and leave `#7` and `#12` untouched.
Deterministic fixtures prove the abstract 5→7→12 sequencing contract without
rewriting historical pull requests.

## Continue Mission

`Continue Mission #N` means:

1. resolve the exact repository and reject a pull-request object;
2. read Issue `#N` and every comment;
3. fresh-read canonical `main` and controlling Prime source;
4. read every linked branch, PR, head, check, review, receipt, and attempt;
5. validate the latest manifest and every intervening state transition;
6. reject stale or contradictory Issue claims in favor of live canonical truth;
7. identify the last proven state and one next safe action;
8. search for existing Mission, branch, PR, Sunset, child, and archive state;
9. resume the same exact attempt without blind retry; and
10. append public-clean evidence to the Mission.

Chat memory, generated projections, a stale manifest, or an unavailable operator
surface is insufficient. A missing route preserves `BLOCKED_RESUMABLE`; it does
not create a replacement Mission.

## Duplicate and replay prevention

Before any mutation, bind and search:

- Mission ID, repository, and Issue number;
- canonical base;
- branch, PR, exact head, and candidate tree;
- sorted changed paths and SHA-256 digest;
- attempt or replay identity;
- Sunset, child-Mission, receipt, and archive references.

Case-fold or Unicode path collision, conflicting binding, reused attempt, or
ambiguous mutation fails closed. After interruption, reconciliation is read-only.
Never blind retry branch, PR, READY, merge, Sunset, or archive creation.

## Portable template and adapters

`.github/ISSUE_TEMPLATE/mission.md` is ordinary Markdown plus one explicitly
unbound `atlas-mission-draft-v1` block. An Issue number does not exist until the
platform creates the Issue, so the draft uses `issue_number: 0` and has no
Mission authority. The creating adapter must read back the assigned number and
replace the draft or append one validated `atlas-mission-v1` comment bound to
that Issue before any worker treats it as a Mission. This avoids a fabricated
Issue identity and dependence on GitHub Projects, custom fields, sub-issue
semantics, or an Issue Form feature that lacks a direct Gitea equivalent.
Optional labels are search indexes only and never state authority.

A future Gitea adapter copies the template to
`.gitea/ISSUE_TEMPLATE/mission.md` and maps API pagination, author identity,
comments, pull-request detection, and URLs. It may not change schema semantics,
infer dependencies, hide adapter limitations, or claim cutover. GitHub remains
canonical until PA-C06 parity, access, backup, recovery, rollback, mirror, and
cutover are separately proven.

## Worker identity and route selection

`assigned_worker` is a logical assignment or `UNASSIGNED`. Execution evidence
separately records declared worker, authenticated credential principal, surface,
and publisher. Assignment neither impersonates a worker nor grants source,
protected-action, READY, or merge authority.

The ordinary user-facing flow may be:

```text
Mission Board
→ assigned worker
→ bounded implementation
→ pull request when source changes
→ validation and review
→ Jayson-controlled permanence
→ canonical readback
```

Spear, Arrow/Bow, Thread Engine, Sword/Oathbringer, Phoenix Blade, and Aegis
Break remain current internal mechanisms. Mission intake can hide routine route
selection from Jayson, but this foundation retires none of them. PA-C09 must
prove parity, Athena/mobile access, recovery, rollback, and independent failure
domains before later simplification or retirement. Recovery without Mission
Board availability begins from clean-clone Prime plus the exact Issue/PR/receipt
export and can use an independently authorized publisher.

## Sunset Missions

A `mission/sunset` captures public-clean context now without pretending the full
Atlas lifecycle has finished. It preserves conversation summary, decisions,
ownership, relationships, exact unfinished work, blockers, Lesson Harvest,
Golden Wing candidate disposition, canonical-source state, record plan, next
safe action, acceptance criteria, Phoenix-pending flag, and archival state.

Truthful Sunset states are:

```text
SUNSET_CAPTURED
PHOENIX_PENDING
PR_OPEN
MERGED_PENDING_READBACK
CANONICAL_READBACK_COMPLETE
SUNSET COMPLETE
```

Issue creation or closure, a package, branch, PR, validation result, Strikeforce
GREEN, READY, or merge response cannot claim `SUNSET COMPLETE`. Only the exact
applicable lifecycle records read back from merged canonical `main` permit it.

## Mission Board, Emberdark, Phoenix, and Coppermind

Mission Board owns visible nonprotected intake, assignment, discussion, status,
sequencing, restart context, and linked evidence. It can replace most public
Gemstone ZIP and copy/paste handoff burden as the default intake surface, but an
offline/exported immutable carrier remains a recovery and protected-boundary
fallback.

Emberdark remains necessary for workflow execution, private integrations,
idempotency, retries, quarantine, reconciliation, authorization mediation,
events, protected transitions, scheduler/automation behavior, audit receipts,
and controlled exports. An Issue cannot safely replace these responsibilities.

Phoenix owns canonical-source branch/PR publication and current-source readback.
Future Gitea publication requires separate cutover evidence. Coppermind owns
structured operational history, retrieval context, cross-Mission search, and
archive records; it does not replace Prime doctrine.

## Coppermind closeout package

The public-clean package contains:

- Mission identity, repository/Issue, objective, final status, and decisions;
- Quest/Campaign/Gate links;
- assigned worker, declared executor, authenticated principal, surface, and publisher;
- branch, PR, exact merged commit, changed paths, and path digest;
- validation, review, Strikeforce, receipts, and canonical readback;
- Lesson Harvest, unresolved follow-up, rollback, and archive timestamp.

No secret or raw protected evidence may enter the package. `PACKAGE_READY`
means the structure is complete but no Coppermind runtime write is claimed.
`COPPERMIND_ARCHIVED` requires a real archive reference and timestamp.

## Protected-data boundary

Mission bodies, comments, fixtures, source, receipts, and examples are
public-clean even after any future private migration. They exclude passwords,
credentials, tokens, keys, MFA/recovery codes, seed phrases, PHI, raw medical,
financial, tax, legal, insurance, mortgage, brokerage, or account evidence,
network addresses or maps, device inventories, real environment values,
unrestricted logs, and raw private exports. Use a sanitized summary and an
approved bounded `protected://` pointer.

## Validation, stop, and rollback

`tools.mission_board` provides read-only validation, manifest extraction,
transition checks, resume planning, replay binding, and ordered-queue behavior.
Platform mutation remains in existing governed adapters. Candidate validation
must include Mission tests, privacy, repository policy, source validation,
whole-program checks, generated-state classification, hosted checks, review,
and exact-head Strikeforce.

Stop on identity, source, head, tree, path, review, validation, protected-data,
replay, dependency, portability, rollback, or cutover ambiguity. Preserve valid
partial state as `BLOCKED_RESUMABLE` with one exact next action.

Before merge, rollback closes the exact PR and preserves Mission evidence. After
merge, use one reviewed revert or repair-forward PR. Never force-push, rewrite
history, silently edit prior Mission truth, or delete the evidence chain.
