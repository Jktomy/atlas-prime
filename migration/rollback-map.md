---
title: "Prime Source Rollback Map"
atlas_id: "prime.migration.rollback"
status: "CANONICAL_ACTIVE"
source_type: "PROTOCOL"
authority_class: "CANONICAL_AUTHORED_SOURCE"
owner_project: "Project Phoenix"
owner_operation: "Operation Restore Runbook"
protected_level: "CRITICAL"
---

# Prime Source Rollback Map

Prime remains the sole active canonical source after cutover.
`Jktomy/atlas-codex` is frozen predecessor and rollback evidence only.
It is never the normal rollback target and never regains active source authority.

## Candidate rollback before merge

Stop the candidate before permanence. Preserve or close its draft PR only
under the applicable authorization. Canonical `main` remains unchanged.

A repair uses the exact approved candidate head or a new reviewed branch and
draft PR. It never uses direct-main mutation, force push, or history rewrite.

## Source rollback after merge

Begin from current verified Prime `main`.

Restore the last independently verified Prime state through a new exact
reviewed revert or restoration PR. Bind the current base, proposed head,
changed paths, validation, rollback classification, and independent readback.

Do not force-reset `main`. Do not restore Codex canonical authority.

After the source rollback merges, use the normal generated-checkpoint route
to refresh the five projections or prove a truthful zero-delta `NOOP`.
Generated files are never repaired directly as governing source.

## Tool or route failure

Preserve the failed branch, PR, receipt, and rejection evidence.

Keep Prime canonical. Disable or repair the affected route through its
reviewed Prime-native activation path. Thread Engine self-change or emergency
disablement uses Aegis Break → Oathbringer and must fail closed at the
activation gate before mission parsing.

## Recovery failure

Follow `recovery/phoenix-recovery.md`.

Recover from a clean clone of exact Prime main, run the complete validation
set, regenerate projections separately, and read back the recovered state.

Protected runtime configuration may be restored only from its approved
private backup system. A destructive canary restore requires separate
Jayson-side authority and protected evidence handling.

## Proof boundary

Every rollback records the exact base, head, tree, paths, payload hashes,
pull request, merge state, validation, and recovery classification.

Rollback is proven only after exact restoration and independent readback.
An undeleted predecessor, snapshot, backup job, or generated report is not
rollback proof.
