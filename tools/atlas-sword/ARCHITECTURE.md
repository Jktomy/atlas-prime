# Atlas Sword Framework Architecture

## Route and profile

- **Sword** is Athena's sealed mission-specific repository payload.
- **Oathbringer** is Jayson's PowerShell-operated GitHub change method.
- The checked-in framework state is `PILOT_READY_PROOF_PENDING`.
- Audit schema `1.2` remains available; production schema `2.0` is present but awaits Wave 3 live proof.

## Components

### Thin PowerShell client

PowerShell owns only:

- parser and UTF-8 initialization;
- Python resolution;
- process-scoped GitHub authentication through `OATHBRINGER_GITHUB_TOKEN`, `GH_TOKEN`, `GITHUB_TOKEN`, or `gh auth token`;
- explicit native argument-array construction;
- invocation of the selected audit or production contract;
- streaming stage and percentage output to the host;
- restoration of the prior process environment;
- nonzero result propagation without automatic host exit.

PowerShell does not author, patch, transform, or locally compose Atlas source. It never writes the GitHub token to disk or terminal output.

### Python audit contract

The schema `1.2` audit contract owns historical audit-only validation, workflow fixtures, stage-ledger behavior, and receipt tests. It performs no GitHub mutation.

### Python GitHub-native production adapter

The production adapter owns:

- schema `2.0` validation;
- Forge Standard and lessons-register binding;
- authorizer and operator authority checks;
- exact repository, base, branch, pull-request, and head locks;
- payload path and SHA-256 validation;
- GitHub blob, tree, commit, ref, pull-request, ready, and merge operations;
- complete candidate-tree and final changed-path verification;
- exact-head workflow applicability and bounded waits;
- success, failure, interruption, and partial-state receipts;
- atomic receipt and SHA-256 sidecar writes;
- parseable JSON output and interactive terminal stages.

The adapter receives already-authored complete payload bytes. It never invents or reinterprets source content.

### Mission manifest

A production mission contains mission-specific facts:

- immutable identity and one lane: BUILD, REPAIR, or EXECUTE;
- `SWORD_FORGE_STANDARD_V1`;
- exact lessons-register SHA-256 and lesson applicability;
- Jayson as authorizer and operator;
- approved Preview and explicit execution authorization;
- repository, base branch, exact base, branch, pull request, and expected head;
- complete final file operations and payload hashes;
- hash-bound workflow rules and path filters;
- receipt contract;
- independent audit receipt for EXECUTE;
- stop boundary and forbidden actions.

### Payload

Complete candidate bytes remain in the sealed package until hashes, paths, authority, and live GitHub locks are validated. GitHub blobs are created from those exact bytes.

## Production state machine

### BUILD

```text
PACKAGE_INTEGRITY
-> MISSION_CONTRACT
-> LIVE_IDENTITY
-> TREE_READBACK
-> PAYLOAD_AND_BLOBS
-> CANDIDATE_TREE
-> COMMIT
-> BRANCH_AND_PR
-> REMOTE_READBACK
-> WORKFLOW_GATE
-> RECEIPT
-> STOP_AT_DRAFT_PR
```

### REPAIR

```text
PACKAGE_INTEGRITY
-> MISSION_CONTRACT
-> EXACT_PR_HEAD
-> BASE_AND_HEAD_TREE_READBACK
-> PAYLOAD_AND_BLOBS
-> COMPLETE_FINAL_CANDIDATE_TREE
-> SINGLE_PARENT_CHILD_COMMIT
-> FAST_FORWARD_REF_UPDATE
-> AMENDED_HEAD_READBACK
-> WORKFLOW_GATE
-> RECEIPT
-> STOP_AT_DRAFT_PR
```

### EXECUTE

```text
PACKAGE_INTEGRITY
-> MISSION_CONTRACT
-> EXACT_PR_HEAD_AND_PATH_SET
-> WORKFLOW_GATE
-> INDEPENDENT_GREEN_AUDIT
-> READY_TRANSITION_IF_NEEDED
-> EXACT_HEAD_MERGE
-> MERGED_MAIN_READBACK
-> RECEIPT
-> STOP
```

Each stage is entered and displayed before its operation begins.

## GitHub transaction rules

### BUILD

- current base branch must equal `expected_base`;
- mission branch and matching open pull request must not already exist;
- complete payload blobs are created through GitHub;
- the candidate tree is compared with the exact base tree;
- the complete changed path set must equal the declared final operation inventory;
- one single-parent commit is created;
- one new branch is created;
- one draft pull request is opened;
- branch, commit, pull request, path set, and applicable CI are read back;
- stop before merge.

### REPAIR

- base branch, pull request, branch, and exact current head must match the mission;
- the final operation inventory remains relative to the exact pull-request base;
- the repaired tree is built on the exact current PR head;
- one single-parent child commit is created;
- the branch is updated fast-forward only with `force = false`;
- the amended PR head and complete final changed path set are read back;
- applicable CI is observed;
- stop before merge.

### EXECUTE

- pull request identity, base, branch, exact head, and changed path set must match;
- applicable exact-head CI must pass;
- a separately created GREEN audit receipt must bind the exact head;
- a draft PR may be marked ready without changing its head;
- GitHub merge receives the exact expected head and sealed merge method;
- merged PR and canonical base branch are read back;
- branch deletion is not performed.

## Workflow gate

For each hash-bound workflow definition:

```text
read exact changed paths
-> evaluate pull_request path filters
-> classify REQUIRED or NOT_APPLICABLE
-> allow bounded appearance time for REQUIRED workflows
-> allow separate bounded completion time after appearance
-> fail closed on missing, failed, cancelled, or timed-out required workflows
-> write a structured receipt on failure or interruption
```

A workflow excluded by its own path filters is never polled indefinitely. Workflow observations are accepted only for the exact workflow name, `pull_request` event, and expected head SHA.

## Authentication boundary

The PowerShell client resolves the token and places it only in the child process environment as `OATHBRINGER_GITHUB_TOKEN`. The adapter sends it only in GitHub API authorization headers. The prior environment is restored after the child exits.

The framework forbids:

- token persistence;
- token printing;
- direct-main ref writes;
- force pushes;
- silent scope expansion;
- automatic rollback;
- blind retry;
- Thread Engine dependency.

## Failure posture

A failure or operator interruption preserves the known remote state in a durable receipt. No automatic retry, rollback, cleanup, branch deletion, or force push occurs. Recovery begins from exact GitHub readback rather than replaying an assumed prior stage.

## Proof boundary

Wave 2 establishes source and deterministic mocked-transport proof. It does not promote production capability. Wave 3 must complete harmless live BUILD, REPAIR, and EXECUTE journeys before Prime may describe Oathbringer production as restored or active.
