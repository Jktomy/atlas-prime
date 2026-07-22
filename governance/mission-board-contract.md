---
title: "Mission Board Contract"
atlas_id: "prime.governance.mission-board"
status: "CANONICAL_ACTIVE"
source_type: "PROTOCOL"
authority_class: "CANONICAL_AUTHORED_SOURCE"
owner_project: "Project Codex"
owner_operation: "Operation Source Governance"
protected_level: "CRITICAL"
routes_from:
  - .github/ISSUE_TEMPLATE/mission.md
  - schemas/mission-v1.schema.json
  - continuity/mission-board-quest-registry-r01.json
routes_to:
  - tools/mission_board/README.md
  - governance/repository-process-contract.md
  - governance/quest-engine-continuity-contract.md
  - recovery/elantris-recovery.md
private_boundary: "Mission Board stores only public-clean mission identity, sanitized operational context, source bindings, checks, receipts, and protected:// pointers."
---

# Mission Board contract

## 1. Purpose

Mission Board is Atlas's primary public-clean operational work surface and its
admitted-Quest registry interface. In GitHub, one Mission is one Issue in
`Jktomy/atlas-prime`. The Issue body and append-only comments preserve intake,
assignment, decisions, dependencies, exact transaction identity, status,
evidence, and restart instructions.

Mission Board does not replace merged Prime. It cannot grant protected access,
advance a canonical Quest or Campaign by Issue state alone, merge a pull
request, deploy a runtime, or turn an architectural statement into execution
proof.

## 2. Authority layers

Authority is deliberately separated:

1. **Merged Prime** owns canonical doctrine, schemas, protocols, Quest sources,
   portable registry snapshots, continuity, recovery, and route rules.
2. **Mission Board Issues** are the primary live coordination and restart
   surface.
3. **`continuity/mission-board-quest-registry-r01.json`** is the merged portable
   admitted-Quest registry and offline recovery snapshot.
4. **`continuity/prime-continuity-register-r01.json`** owns exact unfinished-work
   detail bound to the active Quest registry.
5. **`quest-board/quest-board-v1.json`** is frozen predecessor evidence after
   Mission #278 and has no admission or operational authority.
6. **Phoenix** owns governed source publication; **Shardblade/Jayson** owns
   permanence; protected systems retain protected facts and runtime authority.

A Mission Issue may describe an intended source change but cannot make it
canonical before exact merged-main readback. A merged registry snapshot may
bind a parent Issue but does not give that Issue source or permanence authority.

## 3. Mission identity

A valid Mission uses one `atlas.mission.v1` manifest and binds:

- repository and Issue number;
- Mission ID and attempt ID;
- Mission type and state;
- objective, rationale, owner, Quest/Campaign/Gate relationships;
- assigned worker and execution identity;
- dependency edges;
- public-clean boundary;
- acceptance criteria and next safe action;
- effort and queue behavior;
- canonical source status and exact source binding;
- validation, review, Strikeforce, and receipt references;
- Coppermind archival disposition;
- completion proof and rollback; and
- Sunset fields only for `mission/sunset`.

The Issue template begins with an unbound `atlas-mission-draft-v1` block and
`issue_number: 0`. After creation, the adapter must bind the real repository and
Issue number in exactly one valid `atlas-mission-v1` body or comment before the
Issue becomes an admitted Mission.

## 4. Mission types

The closed Mission type vocabulary is:

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

`mission/quest` is the stable parent identity for an admitted active Quest.
Campaigns, gates, migrations, repairs, and research are child or related
Missions and cannot substitute for the parent.

## 5. State machine

The closed Mission state sequence is:

```text
CAPTURED
TRIAGED
READY
IN_PROGRESS
BLOCKED_RESUMABLE
PR_OPEN
VALIDATING
READY_FOR_PERMANENCE
CANONICAL
COPPERMIND_ARCHIVED
CLOSED
```

Only transitions accepted by `tools.mission_board.core` are valid. Each later
manifest must keep the same Mission ID and attempt ID, use a non-decreasing
`updated_at`, preserve repository and Issue identity, and follow the exact state
and canonical-source transition graphs. Historical malformed candidates may be
superseded only by a later valid append-only update; the latest manifest-shaped
update must validate or reconciliation fails closed.

The canonical-source state sequence is:

```text
PHOENIX_PENDING
NO_SOURCE_CHANGE_REQUIRED
PR_OPEN
MERGED_PENDING_READBACK
CANONICAL
```

`READY_FOR_PERMANENCE` is not merge authority. `CANONICAL` requires exact
merged-main readback. `CLOSED` additionally requires completion proof and an
explicit archival disposition.

## 6. Public-clean boundary

Mission Board may contain:

- public-clean doctrine and sanitized summaries;
- repository paths, public commit/branch/PR/Issue identities, checks, review
  state, and receipt references;
- dependency and ownership metadata;
- explicit uncertainty, blockers, and next safe actions; and
- bounded `protected://` pointers with no protected value.

It must not contain secrets, credentials, private keys, MFA or recovery codes,
real environment values, IP addresses, private network maps, PHI, raw finance,
legal, tax, insurance, mortgage, estate, brokerage, account, or runtime
evidence. Detection of protected material fails closed before publication.

## 7. Source binding

A source-changing Mission binds:

- canonical base SHA;
- one branch;
- one pull request;
- exact expected head SHA;
- normalized complete changed paths;
- changed-path digest; and
- merged commit after permanence.

Paths are sorted, case-fold unique, repository-relative, and reject traversal,
absolute paths, drive paths, and backslashes. Source status `PR_OPEN` or later
requires a complete binding. `MERGED_PENDING_READBACK` and `CANONICAL` require a
merged commit. A changed candidate head invalidates prior validation, review,
Strikeforce, and permanence evidence.

## 8. Duplicate and replay prevention

Before mutation, search the exact Mission ID, attempt ID, branch, pull request,
expected head, changed-path digest, and relevant Issue relationships. Reuse the
same valid attempt; never create a duplicate because one surface is unavailable.

The same attempt cannot bind two Issues. A branch or PR cannot be silently
reused by a different Mission. A later Issue comment cannot move time backward,
change identity, skip the state machine, or replay an event. An ambiguous write
result enters readback-only reconciliation; never blindly retry.

## 9. Dependencies and queue behavior

Dependencies are explicit edges, never inferred from Issue number order. Allowed
relations are:

```text
BLOCKS
BLOCKED_BY
PARALLEL_WITH
NONBLOCKING_RELATED
PARENT_OF
CHILD_OF
```

An ordered Mission list preserves the requested order. Processing stops on a
`BLOCKED_RESUMABLE` Mission unless its queue behavior explicitly permits
`CONTINUE_IF_BLOCKED_RESUMABLE`. Dependency closure, not numbering, controls
eligibility.

## 10. Admitted Quest registry

The Mission Board Quest registry has two synchronized forms:

- one live `mission/quest` parent Issue per active Quest; and
- the merged portable snapshot at
  `continuity/mission-board-quest-registry-r01.json`.

The initial Mission #278 cutover binds exactly:

| Quest | Parent Issue | Parent Mission |
|---|---:|---|
| Prime Ascendant | #307 | `MISSION-QUEST-PARENT-PRIME-ASCENDANT-R01` |
| Prometheus's Fire | #308 | `MISSION-QUEST-PARENT-PROMETHEUS-FIRE-R01` |
| Notum's Watch | #309 | `MISSION-QUEST-PARENT-NOTUMS-WATCH-R01` |

The portable snapshot stores the exact Quest ID, source, owner, state, next gate,
readiness basis, parent Issue, parent Mission, parent attempt, parent Mission
state, and parent source status. It is canonical source because it is merged
Prime, not because it copies Issue claims.

Live Issue availability is not required for clean-clone recovery. When Issues
are unavailable, recover Quest orientation and continuity from merged Prime,
then defer Issue mutation until authenticated readback is possible. An Issue
export is evidence and may resume its exact attempt, but it cannot override the
merged registry or manufacture a source advance.

## 11. Quest admission and advancement

A later Quest admission requires one unique parent Issue plus one atomic reviewed
Prime transaction that adds the Quest source, adds one registry row, increments
the registry revision, binds continuity when unfinished, and preserves every
existing row. The schema and validator are identity-agnostic; they do not
hard-code future Quest names.

The frozen Quest Board is not an admission route and must fail with
`QUEST_BOARD_FROZEN`. A parent Issue state change is operational context only.
Canonical Quest state changes require a reviewed source candidate updating the
Quest source, portable registry, continuity, tests, and recovery surfaces as
applicable.

## 12. Atomic Mission #278 cutover

Mission #278 permits no split-brain interval:

- **Before merge:** Issues #307–#309 are prepared non-authoritative candidates;
  the existing Quest Board remains the active registry.
- **In the exact candidate tree:** the Mission Board Quest registry becomes
  canonical, continuity binds its digest, startup/recovery route to it, and the
  old Quest Board receives `registry_role: FROZEN_PREDECESSOR_EVIDENCE`.
- **After exact merged-main readback:** the parent Issues are the primary live
  operational surfaces and the portable snapshot is the recovery authority.
- **Rollback:** one reviewed revert or repair-forward PR restores the prior
  authority set; Issue and Git history are never rewritten.

The frozen Board retains all seven pre-cutover Quest rows and its historical
proof. Its legacy file lifecycle `state` is not registry authority; the explicit
`registry_role` and successor binding control that boundary.

## 13. Continue Mission

`Continue Mission #N` requires the adapter to:

1. resolve the exact repository and prove `#N` is an Issue, not a pull request;
2. read the body and every comment;
3. reconcile exactly one latest valid Mission manifest;
4. fresh-read canonical `main` and routed doctrine;
5. read linked branch, PR, head, tree, paths, checks, reviews, and receipts;
6. search duplicate identities before mutation;
7. use `tools.mission_board` to validate and derive the next safe action; and
8. append one sanitized result to the same Issue.

A blocked connector stops that route. It does not authorize a duplicate attempt,
branch, PR, or Mission.

## 14. Search, assignment, and child Missions

Search may use titles, labels, Mission IDs, Quest relationships, dependencies,
owners, assignees, states, and exact source bindings. Assignment identifies the
worker for the next bounded step but grants no extra capability or protected
authority.

A child Mission names its parent with an explicit `CHILD_OF` edge or exact Quest
relationship. Child completion may produce evidence for the parent but never
silently advances the parent Quest. Cross-Quest work has one owner and explicit
supporting relationships.

## 15. Validation and tools

`schemas/mission-v1.schema.json` and `tools.mission_board.core` are the closed
runtime contract for Mission manifests, transitions, path normalization,
protected-data scanning, duplicate detection, restart plans, and ordered
sequence plans.

`schemas/mission-board-quest-registry-v1.schema.json` and
`tools.prime_continuity.engine` validate the portable Quest registry, frozen
predecessor, continuity binding, future Quest admission, and deterministic
recovery views.

The Mission Board tools are read-only. They do not call GitHub or Gitea, create
or edit an Issue, create a branch or PR, mark ready, merge, archive, deploy, or
grant authority. Platform adapters perform authenticated reads and explicit
writes under the repository-process contract.

## 16. Recovery and portability

A restart-safe export includes the Issue, all comments, linked PR and review
state, receipts, exact canonical head, and the latest valid manifest. GitHub to
Gitea portability preserves `atlas.mission.v1` semantics and changes only the
platform adapter. A future platform cutover remains separately gated.

Quest-level recovery never depends on the live Issue service because merged
Prime contains the parent identity map and continuity. Continuing a particular
Mission still requires its exact export or authenticated Issue readback; absence
of that evidence blocks the Mission rather than creating a replacement.

## 17. Completion and archive

A Mission is not complete because an Issue closed, a PR merged, tests passed, or
an operator said it was done. Completion requires the applicable exact-head
validation, review disposition, Strikeforce result, merged-main readback,
continuity/recovery agreement, completion proof, and archival disposition.

Coppermind archival is separate from canonical source. Before Coppermind is
proven, `PACKAGE_READY` or `NOT_APPLICABLE` may close a Mission when truthful.
Protected archive contents never enter Prime or Mission Board.

## 18. Rollback

Before merge, close or abandon the exact candidate while preserving evidence.
After merge, use a reviewed revert or repair-forward PR. Never force-push,
rewrite Issue history, delete accepted proof, reuse approval for changed bytes,
or let a rollback silently advance a different Mission.
