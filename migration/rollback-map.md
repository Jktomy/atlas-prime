---
title: "Prime Rollback Map"
atlas_id: "prime.migration.rollback"
status: "SHADOW_CONSTRUCTION"
source_type: "PROTOCOL"
authority_class: "CANONICAL_AUTHORED_SOURCE"
owner_project: "Project Phoenix"
owner_operation: "Operation Restore Runbook"
protected_level: "CRITICAL"
---

# Prime Rollback Map

## Before bootstrap merge

Close the draft PR. Active Prime remains unchanged.

## After bootstrap merge

Restore the exact predecessor tree through a new rollback branch and PR sourced from the preserved predecessor tag.

Do not force-reset or rewrite `main`.

## Tool proof failure

Preserve the failed branch, PR, and receipt. Disable the affected adapter. Keep Codex canonical. Repair only through a new Preview.

## Cutover failure

Return source authority to the last independently verified canonical generation and rerun inheritance and recovery tests before resuming.
