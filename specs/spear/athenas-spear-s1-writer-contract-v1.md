---
title: "Athena's Spear S1 Draft-PR Writer Contract v1"
atlas_id: "spear.s1.draft-pr-writer.v1"
format_version: "1.0"
status: "PROPOSED"
source_type: "SPECIFICATION"
authority_class: "TOOL_CONTRACT"
owner_project: "Codex"
owner_operation: "Athena's Spear"
canonical_scope: "Defines the bounded S1 execution contract for converting an already validated and explicitly approved Prime Spear plan into one deterministic branch, one commit, and one draft pull request while preserving manual merge, Noctua, source-order, and protected-boundary controls."
protected_level: "CRITICAL"
routes_from:
  - "atlas-aegis.md"
  - "athenas-spear.md"
  - "migration/atlas-codex/audits/prime-spear-s0-audit-and-freeze-v1.md"
  - "specs/atlas-prime/codex-to-prime-migration-contract-v1.md"
  - "specs/spear/athenas-spear-spec-v0.2.md"
  - "schemas/spear/spear-packet-v1.schema.json"
  - "policies/operations/spear/spear-policy-v1.yaml"
  - "policies/destination/atlas-prime-destination-policy-v0.2.yaml"
routes_to:
  - "tools/spear/operator-runbook.md"
  - "tools/spear/recovery-runbook.md"
  - "tests/spear/test_security.py"
  - "tests/spear/test_final_gates.py"
private_boundary: "This contract may contain clean workflow, permission, repository, branch, hash, test, and recovery semantics only. It must not contain tokens, credentials, private keys, real secret values, PHI, raw finance or account evidence, private runtime values, IP addresses, network maps, device registers, protected exports, or other raw protected evidence."
evidence_boundary: "This specification is authored tool-contract source. GitHub settings, workflow runs, packets, manifests, receipts, artifacts, branches, commits, pull requests, Noctua reports, merge records, rollback tests, and original evidence systems remain distinct evidence and must be verified directly."
supersedes: []
cleanup_path: "Retain as the S1 design contract. Supersede only through a later reviewed Spear writer contract after implementation evidence, Noctua audit, recovery proof, and explicit Jayson approval. Do not interpret this file as writer activation."
last_verified: "2026-06-25"
---

# Athena's Spear S1 Draft-PR Writer Contract v1

## 1. Authority and outcome

```text
Repository: Jktomy/atlas-prime
A2 phase: WRITER CONTRACT AND S1 DESIGN
Design outcome: COMPLETE WHEN MERGED AND READ BACK
Implementation authority: NOT AUTHORIZED
Writer activation: NOT AUTHORIZED
Migration authority: NOT AUTHORIZED
Merge authority: JAYSON MANUAL ONLY
Cutover authority: NOT AUTHORIZED
```

This contract defines the first future write-capable Prime Spear phase.

It does not implement S1, enable a workflow, change repository settings, grant credentials, execute a packet, create a migration branch, modify Atlas Codex, promote Atlas Prime, or authorize cutover.

Atlas Codex remains canonical. Atlas Prime remains `SHADOW`.

## 2. Locked A2 design decision

A2 adopts this execution model:

```text
Trigger: owner-only GitHub Actions workflow_dispatch
Runner: GitHub-hosted runner
Credential: job-scoped repository GITHUB_TOKEN
Write scope: one deterministic branch, one commit, one draft pull request
Merge: prohibited
Direct main write: prohibited
Force push: prohibited
```

The S1 pilot must not require:

- a personal access token;
- a long-lived repository token;
- a GitHub App private key;
- a self-hosted runner;
- an external orchestrator;
- an issue-comment command surface;
- a pull-request-triggered write workflow;
- or packet-provided executable code.

A later contract may replace the credential or gateway model only through a separate Preview -> Execute decision.

## 3. S1 pilot scope

S1 is a draft-PR writer for the already registered ordinary packet route only.

The pilot may execute only packets that satisfy the active S0 contracts at the exact packet base commit:

- target repository exactly `Jktomy/atlas-prime`;
- base branch exactly `main`;
- operations limited to `CREATE_FILE` and `REPLACE_FILE_FULL`;
- at most five operations;
- Markdown targets only;
- ordinary target prefix limited to `projects/`;
- no deletion, move, rename, archive, merge, force-push, or direct-main operation;
- no protected, migration, generated, register, workflow, schema, policy, tool, test, root-governance, or private-evidence surface.

S1 does not expand S0 path or operation authority.

The following remain outside S1:

- migration evidence transactions;
- the twenty-file collision-evidence package;
- root doctrine or bootstrap changes;
- Spear, Noctua, or Phoenix self-modification;
- schemas, policies, tools, tests, fixtures, or workflows;
- generated reports;
- Quest, Golden Wing, Feather, or other structured-register writes;
- repair of an existing pull request;
- merge verification;
- rollback execution;
- Atlas Codex writes;
- source promotion or cutover.

Those surfaces require later versioned contracts and separately approved routes.

## 4. Actor and trigger boundary

The future S1 workflow must:

1. use `workflow_dispatch` only;
2. exist on the default branch before it may run;
3. verify `github.repository == "Jktomy/atlas-prime"`;
4. verify the triggering actor against an explicit owner allowlist containing `Jktomy`;
5. reject scheduled, push, pull-request, issue, comment, workflow-run, repository-dispatch, and external webhook execution;
6. reject reusable-workflow callers unless a later contract explicitly permits them;
7. reject execution when the checked-out workflow commit is not reachable from current `main`;
8. record the actor, workflow commit, run ID, run attempt, and event type in the execution receipt.

No packet field may select or override the actor, event, repository, workflow, runner, permission set, or credential.

## 5. Runner and action boundary

The S1 pilot must use a fresh GitHub-hosted runner.

It must not use a self-hosted runner because S1 has not yet proven:

- workspace isolation;
- credential cleanup;
- persistence boundaries;
- runner image integrity;
- concurrent-job separation;
- or post-failure residue handling.

Every external GitHub Action must be pinned to an exact full commit SHA.

The workflow must not:

- execute code from the packet;
- evaluate packet text as shell;
- source packet-controlled environment files;
- use `eval`;
- interpolate packet content into shell command structure;
- check out an untrusted pull-request head;
- use `pull_request_target`;
- download or execute undeclared artifacts;
- or invoke network destinations not explicitly required for GitHub repository operations.

## 6. Credential and permission contract

The workflow-level default must be read-only.

The plan job may receive only the minimum read permissions required to:

- check out the exact Prime base;
- read repository contents;
- inspect current pull-request state when idempotency requires it;
- and upload non-secret review artifacts.

The apply job may receive only:

```text
contents: write
pull-requests: write
```

All other permissions must be absent or explicitly `none`, including:

- actions write;
- checks write;
- deployments write;
- discussions write;
- id-token write;
- issues write;
- packages write;
- pages write;
- repository-projects write;
- security-events write;
- statuses write;
- workflow administration.

The workflow must:

- use the job-scoped `GITHUB_TOKEN`;
- avoid `persist-credentials: true` after the write step is complete;
- never print, persist, upload, or echo the token;
- never copy the token into an artifact;
- never expose the token to packet-selected commands;
- and let the token expire with the job.

S1 does not rely on protected-environment required-reviewer features. Those controls may be unavailable depending on repository visibility and account plan. Where available, they may be added later as defense in depth through a separately approved repository-settings change.

## 7. Packet and execution-envelope separation

The existing `spear-packet-v1` remains the semantic change request.

S1 introduces a separate execution envelope. The envelope does not alter packet meaning and must contain:

- exact packet bytes or a transport-safe exact representation;
- packet transport SHA-256;
- expected Prime base commit;
- approved normalized-manifest SHA-256;
- approved Preview SHA-256;
- approval source;
- approval reference;
- exact approved scope;
- execution mode fixed to `CREATE_DRAFT_PR_ONLY`;
- plan creation time;
- plan expiration time;
- and an explicit confirmation value fixed by contract.

The packet remains subject to the current packet size limit.

The total `workflow_dispatch` payload must remain below the current GitHub input-payload limit with adequate margin for envelope fields. A3 must enforce both decoded byte limits and platform payload limits before compilation.

No execution envelope may:

- add operations;
- change content;
- change target paths;
- change authority;
- change privacy classification;
- change the expected base;
- change policy identities;
- or reinterpret an approved Preview.

## 8. Preview and approval binding

S1 may execute only when the execution envelope binds to an exact approved Preview.

The approved Preview must identify:

- the exact Prime base commit;
- exact packet SHA-256;
- exact normalized-manifest SHA-256;
- exact changed filenames;
- complete proposed content or complete diff;
- old and new file hashes;
- protected-boundary outcome;
- validation requirements;
- expected branch and pull-request behavior;
- rollback posture;
- explicit prohibitions;
- and the Noctua stop gate.

The apply job must reject:

- a missing Preview hash;
- a changed Preview hash;
- a missing manifest hash;
- a changed manifest hash;
- an approval reference that does not identify the approved scope;
- an approval older than the allowed plan lifetime;
- or an approval that does not explicitly permit draft-PR creation.

A packet upload, valid compile, Noctua `YES`, or prior related approval does not substitute for the exact Preview binding.

## 9. Plan and apply separation

S1 uses two jobs in one manually triggered workflow:

```text
PLAN
-> bounded artifact handoff
-> APPLY
-> DRAFT PR
-> STOP
```

### 9.1 Plan job

The plan job is read-only.

It must:

1. verify actor, event, repository, workflow commit, and input limits;
2. verify packet transport bytes and SHA-256;
3. resolve current `main`;
4. require current `main` to equal the envelope base commit;
5. load every controlling schema and policy from that exact base commit;
6. normalize and validate every path before any target-object lookup;
7. compile the packet with the S0 compiler;
8. verify the resulting manifest hash equals the approved manifest hash;
9. verify the Preview hash and approval envelope;
10. build the complete proposed tree in a temporary location;
11. run all pre-write validation;
12. emit a bounded plan artifact and receipt;
13. grant no write permission.

The plan artifact must include no credential or prohibited evidence.

### 9.2 Apply job

The apply job must consume only the exact plan artifact produced by the same workflow run.

Before any write it must independently reverify:

- actor and event;
- repository and base branch;
- current `main`;
- packet hash;
- manifest hash;
- Preview hash;
- approval reference and scope;
- plan expiration;
- schema and policy identities;
- all target expected states;
- all resulting content hashes;
- branch absence or valid idempotent recovery state;
- and the complete changed-file list.

The apply job must refuse freeform packet reinterpretation.

## 10. Required A1 hardening

A3 implementation must close both A1 findings before any S1 proof run.

### A1-F01

The synthetic compiler-version fixture must stop using the stale value `3.0.0-s0`.

The corrected test must bind synthetic contract identity to the current package version or explicitly assert the intended version value.

### A1-F02

Every operation path must be normalized and policy-validated before any Git target lookup.

A3 must include an end-to-end test proving malformed, traversal, denied, control-character, backslash, and normalization-collision paths are rejected before the Git adapter receives a target lookup request.

Failure to close either finding blocks S1 proof and activation.

## 11. Pre-write validation gates

Before branch creation, S1 must verify:

- the packet and execution envelope parse strictly;
- duplicate JSON keys are rejected;
- the exact approved packet and manifest hashes match;
- current `main` equals the approved base;
- controlling contract blobs match the plan;
- all paths are normalized, unique, case-safe, and permitted;
- no symlink or submodule target is involved;
- each create target is absent;
- each replacement target has the exact expected Git blob;
- every content SHA-256 matches;
- resulting Markdown and YAML front matter parse;
- source metadata conforms to the pinned schema when required;
- protected-content scanning returns no blocking category;
- no binary or NUL content exists;
- the proposed tree contains exactly the approved changes;
- operation and size limits are respected;
- no source/generated mixing occurs;
- no denied authority or action appears;
- and all required tests pass.

Any warning classified as consent-required must return `NEEDS_JAYSON` before write.

Any stale state, hash mismatch, unexpected path, warning escalation, test failure, or policy drift must block before branch creation.

## 12. Atomic transaction contract

S1 must construct and validate the complete proposed tree before creating any remote branch.

A successful transaction creates:

- one new deterministic branch;
- one commit;
- one draft pull request;
- one execution receipt;
- one bounded evidence artifact set.

All approved file changes must be committed atomically in the same commit.

S1 must not create a partial multi-file commit.

The branch name must be generated by the compiler and conform to the exact active destination-policy branch regex. The packet may not supply a branch name.

The commit must have:

- the approved base as its only parent;
- a deterministic subject derived from the packet title;
- no unrelated authoring trailers;
- and a tree matching the approved manifest exactly.

## 13. Branch and idempotency rules

Before creating a branch, S1 must verify that the deterministic branch does not exist.

If the branch is absent, S1 may create it.

If the branch already exists:

- same packet ID, packet hash, manifest hash, base, commit tree, and open draft PR returns the existing transaction;
- same commit but missing PR permits deterministic PR recovery;
- any other state blocks as a collision;
- no force update is permitted;
- no second branch may be created for the same packet.

The concurrency key is:

```text
Jktomy/atlas-prime + packet_id
```

`cancel-in-progress` must be false.

A stale base after planning requires a new plan and new approval. S1 must not rebase or silently transplant the approved changes.

## 14. Draft pull-request contract

S1 may open exactly one draft pull request against `main`.

The PR title and body must be generated deterministically from the packet and receipt.

The PR body must include:

- packet ID;
- packet transport SHA-256;
- normalized-manifest SHA-256;
- approved Preview SHA-256;
- approval basis and reference;
- exact base commit;
- branch and commit SHA;
- controlling contract identities;
- exact changed filenames;
- old and new file identities;
- validation summary;
- warnings;
- protected-boundary outcome;
- rollback posture;
- workflow run identity;
- requested Noctua audit;
- and the statements:

```text
This draft pull request grants no merge, deletion, migration, source-promotion, or cutover authority.
Manual Noctua review and explicit Jayson approval are required before merge.
```

S1 must not:

- mark the PR ready for review automatically;
- approve the PR;
- request auto-merge;
- merge the PR;
- close a competing PR;
- modify branch protection;
- dismiss reviews;
- resolve review threads;
- or alter repository settings.

## 15. GitHub Actions recursion and check behavior

S1 must not depend on a push-triggered workflow running after a `GITHUB_TOKEN` push.

All required pre-write validation must finish inside the S1 workflow before the branch is pushed.

When S1 opens or updates a pull request using `GITHUB_TOKEN`, pull-request workflows may enter an approval-required state.

That state is an expected human gate, not permission to bypass checks.

Jayson must approve those workflows in the GitHub interface before merge consideration.

Noctua must verify the resulting check state and must not treat `action_required`, missing approval, skipped validation, or absent expected jobs as a pass.

A later contract may use a separately provisioned GitHub App token only after secret handling, permission boundaries, workflow-recursion behavior, and recovery are independently reviewed.

## 16. Failure and recovery contract

Failure before remote branch creation leaves no repository mutation.

Failure after branch push but before PR creation must return:

```text
BRANCH_PUSHED_PR_MISSING
```

A retry with the identical packet, manifest, base, and branch may create the missing draft PR.

Failure after PR creation must preserve the branch and PR for audit.

S1 must never:

- delete a branch automatically;
- close a PR automatically;
- force-push a repair;
- rewrite history;
- reset `main`;
- or discard failure evidence.

Recovery must report:

- the last completed gate;
- branch state;
- commit state;
- PR state;
- receipt state;
- exact blocker;
- and the next safe action.

Repair of an existing PR is outside S1 and requires a later repair contract.

## 17. Execution receipt

Every S1 attempt must produce a machine-readable receipt containing:

- contract version;
- compiler version;
- workflow commit;
- workflow run ID and attempt;
- event type;
- authenticated actor;
- repository;
- base branch and commit;
- packet ID and hash;
- manifest hash;
- Preview hash;
- approval reference;
- schema and policy blob identities;
- plan creation and expiration;
- changed filenames;
- expected and resulting file identities;
- deterministic branch;
- commit SHA and tree SHA when created;
- pull-request number and URL when created;
- validation results;
- warning and blocker codes;
- protected-content scan categories without detected values;
- final transaction state;
- and explicit non-authorities.

Receipts must redact prohibited values and must never contain token material.

## 18. Noctua audit gate

S1 stops after draft PR creation.

Noctua must independently verify:

1. the current Prime base and PR base;
2. authenticated actor and workflow event;
3. workflow commit and permission declarations;
4. packet, manifest, Preview, and receipt hashes;
5. controlling contract identities;
6. changed filenames;
7. complete PR diff;
8. target expected states;
9. metadata and routing;
10. protected-content boundaries;
11. A1-F01 and A1-F02 closure;
12. tests and hostile fixtures;
13. branch, commit, and PR lineage;
14. one-commit atomicity;
15. absence of direct-main, force-push, merge, deletion, move, or self-modification;
16. CI approval and check state;
17. recovery evidence;
18. packet-to-PR fidelity;
19. Atlas Codex canonical status;
20. Prime `SHADOW` status.

Noctua `YES` means only that the reviewed draft PR passed the stated audit.

It does not authorize merge or activate writer mode.

## 19. Rollback and Phoenix Reborn obligation

Before writer activation, the harmless S1 proof must demonstrate:

- isolated revert planning for the Spear-created commit;
- a replacement-PR path when revert is unsafe or conflicts;
- merged-main readback after the human merge;
- readback after any rollback proof;
- branch and PR lineage preservation;
- and continuity of receipts and Noctua evidence.

S1 itself does not execute rollback.

Phoenix Reborn must independently verify the recovery claim before S1 can be considered production-ready for migration.

## 20. Required A3 implementation surface

A3 may propose, but does not receive authority from this contract to implement:

- the execution-envelope schema;
- the S1 GitHub Actions workflow;
- the apply adapter or executor;
- receipt schema and serializer;
- idempotency and PR-recovery logic;
- permission and actor guards;
- tests and hostile fixtures;
- operator and recovery runbook updates;
- and a disabled-by-default activation control.

A3 must use a separate protected source PR.

The S1 workflow must remain disabled or fail closed until its implementation PR is merged, audited, and separately activated.

## 21. S1 security acceptance suite

A3 tests must prove at minimum:

- non-owner actor rejection;
- non-`workflow_dispatch` event rejection;
- wrong repository rejection;
- stale base rejection;
- stale target blob rejection;
- packet and manifest hash mismatch rejection;
- Preview hash mismatch rejection;
- expired plan rejection;
- policy or schema drift rejection;
- operation and path-limit enforcement;
- path validation before Git lookup;
- denied-path rejection;
- protected-content redaction;
- no packet-selected command execution;
- no packet-selected branch;
- no direct-main write;
- no force push;
- no merge or auto-merge;
- no workflow self-modification;
- branch collision handling;
- idempotent same-transaction recovery;
- branch-pushed/PR-missing recovery;
- atomic multi-file commit behavior;
- deterministic branch, commit, PR body, and receipt generation;
- and absence of credential material in logs and artifacts.

The suite must run without repository write permission for ordinary unit and hostile-fixture tests.

A separate bounded integration proof may receive temporary S1 permissions only after an exact Preview.

## 22. Activation gates

S1 writer activation requires all of the following:

1. this A2 contract is merged and read back from `main`;
2. A3 implementation receives its own exact Preview and explicit Execute approval;
3. protected implementation, workflow, schema, policy, test, and runbook changes pass Noctua;
4. A1-F01 and A1-F02 are closed by tests;
5. the S1 workflow is disabled by default after merge;
6. one harmless ordinary `projects/` packet receives an exact Preview;
7. the harmless packet creates exactly one branch, one commit, and one draft PR;
8. all expected pull-request checks are manually approved and pass;
9. Noctua verifies packet-to-PR fidelity;
10. Jayson manually merges the harmless PR;
11. merged-main readback proves the exact result;
12. rollback and Phoenix Reborn proof pass;
13. residual GitHub Free risks are restated and accepted;
14. Jayson explicitly activates the bounded S1 route.

No migration packet, protected-source route, or expanded operation becomes authorized through the harmless proof.

## 23. Residual-risk statement

The S1 apply job temporarily holds repository write permissions sufficient to create a branch, commit, and draft PR.

Software controls cannot provide the same guarantee as server-enforced branch protection and independent credential separation.

Compensating controls are therefore mandatory:

- owner-only manual dispatch;
- exact repository and base binding;
- short-lived repository-scoped token;
- job-scoped permissions;
- no stored PAT or App private key;
- protected workflow source;
- packet and Preview hash binding;
- deterministic manifest-only execution;
- no packet-selected code;
- no direct-main code path;
- no force-push code path;
- no merge code path;
- full hostile-fixture tests;
- PR CI approval;
- independent Noctua review;
- manual Jayson merge;
- merged-main readback;
- and Phoenix Reborn recovery proof.

The residual risk is not accepted merely because this specification exists.

Risk acceptance occurs only through the later explicit activation gate.

## 24. A2 acceptance criteria

A2 is complete only when:

- this contract receives an exact one-file Preview;
- the target path is confirmed absent;
- the full content and SHA-256 are recorded;
- source metadata validates;
- the protected boundary is clean;
- Noctua returns `YES`;
- Jayson explicitly approves the exact source write;
- a narrow protected source branch and one-file draft PR are created;
- the PR changes only this specification;
- Jayson manually merges;
- and the merged file is read back from `main`.

A2 completion does not authorize A3 implementation.

## 25. Final state

```text
A2 writer-contract design: COMPLETE
A2 durable source closeout: PENDING PREVIEW -> EXECUTE -> MERGE -> READBACK
A3 S1 implementation: NOT AUTHORIZED
S1 writer activation: NOT AUTHORIZED
Migration execution: NOT AUTHORIZED
Atlas Prime promotion: NOT AUTHORIZED
Atlas Codex retirement: NOT AUTHORIZED
```
