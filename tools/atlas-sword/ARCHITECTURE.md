# Atlas Sword Framework Architecture

## Route and profile

- **Sword** is the direct local fallback, recovery, and self-change route.
- **Oathbringer** is the Sword change method.
- The checked-in framework remains `PILOT_DISABLED` and `AUDIT_ONLY`.

## Components

### PowerShell launcher

PowerShell owns:

- parser and encoding initialization;
- explicit native argument-array construction;
- Python resolution;
- invocation of the Python Oathbringer contract;
- streaming contract output to the host;
- nonzero result propagation without automatic host exit.

### Python Oathbringer contract

Python owns:

- schema `1.2` validation;
- `change_method = OATHBRINGER`;
- `execution_environment = POWERSHELL`;
- package manifest verification when present;
- exact path normalization;
- workflow path-filter matching;
- exact workflow name, `pull_request` event, and head SHA filtering;
- `REQUIRED` and `NOT_APPLICABLE` classification;
- same-run refresh and newer-run precedence;
- separate bounded appearance and completion waits;
- exact untracked `ADD` audit planning;
- stage-ledger truth;
- failure and interrupt receipt classification;
- receipt-contract validation;
- atomic JSON receipt and SHA-256 sidecar writes;
- parseable JSON mode and persistent terminal final display.

### Mission manifest

A mission contains only mission-specific facts:

- immutable identity and lane;
- change method and execution environment;
- repository, base, branch, pull request, and expected head;
- declared file operations and hashes;
- hash-bound workflow rules and path filters;
- required CI;
- receipt contract;
- expected automation effects;
- recovery state;
- stop boundary;
- forbidden actions.

### Payload

Payload bytes remain outside the checkout until the complete declared output set
has been validated.

## Future production state machine

```text
PACKAGE_AUDIT
-> PARSER_PREFLIGHT
-> MISSION_SCHEMA
-> READ_ONLY_LIVE_LOCKS
-> FRESH_CLONE
-> LOCAL_CANDIDATE_VALIDATION
-> EXACT_UNTRACKED_ADD_AUDIT
-> COMPLETE_DIFF_AUDIT
-> DECLARED_MUTATION
-> INDEPENDENT_REMOTE_READBACK
-> PATH_APPLICABLE_WORKFLOW_GATE
-> RECEIPT
-> STOP
```

Each transition is entered in the ledger before its operation begins. Recovery
resumes from recorded state without replaying a completed mutation.

## Workflow gate

For each hash-bound workflow definition:

```text
read exact changed paths
-> evaluate pull_request path filters
-> classify REQUIRED or NOT_APPLICABLE
-> allow a bounded appearance grace for REQUIRED workflows
-> allow a separate bounded completion wait after appearance
-> fail closed on missing, failed, cancelled, or timed-out required workflows
-> write a structured receipt on failure or interruption
```

A workflow excluded by its own path filters is never polled forever.

Workflow observations are accepted only when the observed run matches the exact
workflow name, `pull_request` event, and expected head SHA. A refreshed status for
the same run replaces stale observations, and a newer matching run takes
precedence over older matching runs.

## Required lane behavior

### BUILD

- fresh clone from the exact verified base;
- install only the complete declared output set;
- enumerate and assert exact untracked `ADD` paths;
- apply intent-to-add only to approved new paths;
- run `git diff --check`;
- verify the complete changed-file boundary;
- one deterministic branch and single-parent commit;
- non-force push;
- draft pull request;
- independent readback;
- wait only for applicable CI;
- stop before merge.

### REPAIR

- diagnose before retry;
- reproduce the defect in a disposable fixture when possible;
- add a regression test;
- fresh clone;
- exact current pull-request head;
- explicit non-overlapping-drift proof when main moved;
- one child commit;
- fast-forward-only branch update;
- independent amended-head readback;
- wait only for applicable CI;
- stop before merge.

### EXECUTE

- fresh clone for exact verification;
- exact audited base, head, file set, blobs, reviews, and applicable CI;
- disclosed automation effects;
- sealed merge method and expected head;
- merged-main topology and tree readback;
- preserve the source branch unless deletion has separate authority;
- observe automation without inheriting authority;
- stop at the declared boundary.

## Failure posture

Automatic retry, rollback, cleanup, force push, merge, and branch deletion are
absent. Local receipt replacement is the only retry surface, bounded to
transient Windows rename/replace locks. A normal failure writes a fail-closed
receipt. An operator interruption writes a preserved-state receipt and exits
with code `130`.
