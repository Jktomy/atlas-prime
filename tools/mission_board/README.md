---
title: "Mission Board Read-only Mechanics"
atlas_id: "prime.tools.mission-board"
status: "CANONICAL_ACTIVE"
source_type: "TOOL_CONTRACT"
authority_class: "CANONICAL_AUTHORED_SOURCE"
owner_project: "Project Codex"
owner_operation: "Operation Source Governance"
protected_level: "HIGH"
---

# Mission Board read-only mechanics

`tools.mission_board` validates portable `atlas.mission.v1` manifests and
derives restart or sequential-processing plans. It is deliberately read-only:
it does not call GitHub or Gitea, create or edit an Issue, create a branch or PR,
READY, merge, archive, deploy, or grant authority.

Platform adapters must export the issue, all comments, current canonical head,
and linked PR state before using these mechanics. The adapter remains responsible
for authenticated readback and for proving that the requested repository object
is an Issue rather than a pull request.

The Markdown template begins with an unbound `atlas-mission-draft-v1` block and
`issue_number: 0` because the platform assigns the real number only after
creation. The adapter must read back that number and publish a validated
`atlas-mission-v1` body or comment before the Issue becomes an admitted Mission.

Implementation paths are `tools/mission_board/__init__.py`,
`tools/mission_board/__main__.py`, `tools/mission_board/core.py`, and
`tools/mission_board/quest_sync.py`. The receipt contract is
`schemas/quest-sync-receipt-v1.schema.json`. The package entry point exposes only
read-only validation and planning commands.

## Commands

```text
python -B -m tools.mission_board validate MISSION.json
python -B -m tools.mission_board resume MISSION.json --canonical-head EXACT_SHA
python -B -m tools.mission_board sequence --mission 5=M5.json --mission 7=M7.json --mission 12=M12.json 5 7 12
```

The `sequence` command preserves the requested order. It continues past
`BLOCKED_RESUMABLE` only when that Mission explicitly declares
`CONTINUE_IF_BLOCKED_RESUMABLE`; number order never invents a dependency.

## Post-merge Quest synchronization gate

Before closing a child Mission, an authenticated platform adapter must invoke
`enforce_quest_sync_closure` with the exact canonical head, the merged portable
Quest registry, and complete parent-Issue snapshots. `affected_parent_quests`
detects impact from a direct Quest relationship, a `CHILD_OF` parent binding, a
changed Quest source, or shared Mission Board and Quest-continuity doctrine.

For every affected active Quest, the adapter must append exactly one compact
`atlas-quest-sync-receipt-v1` block to that Quest's live `mission/quest` parent
Issue. `build_quest_sync_receipt` binds the child Mission and Issue, exact merged
commit, changed-path digest, parent Quest and Mission identities, and
`EXACT_MERGED_MAIN` readback. The receipt summarizes impact and never copies
full Quest doctrine or advances Quest state.

Missing, stale, contradictory, unreadable, or duplicate evidence fails closed.
The closure gate returns `QUEST_SYNC_PENDING` until every required parent receipt
is independently read back. A lifecycle-only non-Quest candidate does not invent
Quest impact merely because it records cross-Quest context.

## Safe adapter sequence

1. Resolve exact repository and Issue number.
2. Reject pull-request objects and repository mismatch.
3. Read the Issue and every comment.
4. Fresh-read canonical `main` and linked PR state.
5. Ignore the unbound draft, extract exactly one manifest per admitted update, and reconcile chronological state transitions. A later valid append-only update may supersede an invalid historical candidate; the latest manifest-shaped update must validate or reconciliation fails closed.
6. Search Mission ID, attempt ID, branch, PR, head, and changed-path digest before mutation.
7. Use the returned next safe action; never blind retry.
8. After merged-main readback, append and independently confirm every required parent-Quest synchronization receipt before child Mission closure.
9. Append sanitized completion evidence to the same Mission.

Merged Prime remains source authority. Mission state and issue closure cannot
self-certify canonical source, Coppermind archival, Quest completion, or
`SUNSET COMPLETE`.
