# Athena’s Spear Specification v0.2

Status: Pre-build compiler contract  
Repository target: `Jktomy/atlas-prime` shadow repository  
Owner: Project Codex / Project Artemis  
Authority: Current explicit Jayson direction  
Implementation state: Specification only; no production write authority

---

## 1. Mission

Athena’s Spear (“Spear”) accepts one complete packet prepared by Athena, validates the packet and its requested repository changes, deterministically computes the exact result, and returns a machine-readable plan.

After the read-only compiler is proven and a separate apply phase is approved, Spear may consume an already validated manifest to create one branch, one commit, and one pull request. Spear stops before merge.

```text
Athena interprets.
Spear validates and files.
GitHub exposes.
Athena audits.
Jayson decides permanence.
```

## 2. Non-goals

Spear does not:

- interpret the original conversation;
- infer Jayson's intent from raw chat;
- invent decisions or destinations;
- choose a Project when ownership is ambiguous;
- decide promotion;
- write directly to `main`;
- merge or force-push;
- hard-delete in v1;
- modify its own engine or workflows through ordinary packets;
- store prohibited private evidence.

## 3. User experience

1. Athena prepares one complete packet.
2. Jayson pastes the packet into Spear.
3. Spear returns a clean plan, warnings, or a safe block.
4. Later, after apply mode is separately approved, the validated plan may create one PR.
5. Athena audits the PR.
6. Jayson decides whether it merges.
7. Athena verifies merged `main`.

Jayson should not need to provide paths, branch names, commit messages, PR metadata, patch types, or repository internals.

## 4. Supported callers

Future callers may include Athena in ChatGPT, Apple Shortcuts, n8n, Hermes agents, approved bots, GitHub Actions, and a future Atlas app.

All callers use the same language-neutral JSON contract. Caller authentication is separate from packet integrity.

## 5. Run intents

Every packet declares exactly one `run_intent`:

- `PLAN_ONLY`
- `CREATE_PR`
- `REPAIR_PR`
- `VERIFY_MERGE`

For v0.2, only `PLAN_ONLY` is authorized for implementation. The other intents are schema-defined but disabled until separately approved.

## 6. Memory classes

### WORKING_MEMORY

Active chat context. Not a GitHub object by itself.

### CONTINUITY_MEMORY

Durable but non-governing memory, including Harvest, Sunset, Synthesis, Continuity, and Aegis records.

### CANONICAL_MEMORY

Approved doctrine, policy, decisions, Project and Operation summaries, runbooks, active state, command behavior, and recovery standards.

Continuity memory never becomes canonical merely through storage, age, repetition, or consolidation.

## 7. Authority classes

Each packet declares one primary authority class:

- `CONTINUITY_MEMORY`
- `STATE_UPDATE`
- `DECISION_UPDATE`
- `CANONICAL_UPDATE`
- `PROMOTION`
- `SUPERSESSION`
- `ARCHIVE_PROPOSAL`
- `AEGIS_EVOLUTION`
- `REPAIR`

The compiler enforces a strict authority-compatibility matrix. A child change may use only an authority permitted by the packet authority. No continuity-to-canonical escalation is allowed.

## 8. Approval basis

Packets that may affect canonical memory or an existing PR require `approval_basis`.

Allowed sources:

- `EXPLICIT_JAYSON_INSTRUCTION`
- `APPROVED_PREVIEW_EXECUTE`
- `PHOENIX_BURN_DISPOSITION`
- `PR_AUDIT_REPAIR_AUTHORIZATION`
- `NONE_REQUIRED_CONTINUITY_ONLY`

Required fields are `source`, `reference`, and `approved_scope`, with `approved_at` when known.

## 9. Privacy classes

Every packet and change declares:

- `PUBLIC_CLEAN`
- `PRIVATE_CLEAN_SUMMARY`
- `POINTER_ONLY`
- `PROHIBITED`

`PROHIBITED` always blocks. Prohibited content includes secrets, credentials, tokens, MFA or recovery codes, private keys, seed phrases, real `.env` values, raw PHI, raw finance or account evidence, private runtime registers, IP maps, device registers, and protected exports.

Detected values must be redacted from logs and reports.

## 10. Record types

Spear v1 supports:

- `HARVEST_RECORD`
- `SUNSET_RECORD`
- `SYNTHESIS_RECORD`
- `CONTINUITY_RECORD`
- `AEGIS_LESSON`
- `ACTIVE_WORK_ITEM`
- `DECISION_RECORD`
- `PROJECT_UPDATE`
- `OPERATION_UPDATE`
- `RUNBOOK_UPDATE`
- `POLICY_UPDATE`
- `PHOENIX_BURN_PROMOTION`
- `ARCHIVE_OR_RETIREMENT_PROPOSAL`
- `BOUNDED_SOURCE_UPDATE`
- `PR_REPAIR`

## 11. Operations

### Create

- `CREATE_FILE`
- `CREATE_RECORD_IN_BUNDLE`
- `CREATE_CROSS_REFERENCE`

### Update

- `REPLACE_EXACT`
- `APPEND_UNDER_UNIQUE_HEADING`
- `UPDATE_STRUCTURED_FIELD`
- `UPSERT_STRUCTURED_RECORD`
- `MARK_CONSOLIDATED`
- `MARK_SUPERSEDED`
- `ADD_RELATIONSHIP`
- `REMOVE_RELATIONSHIP`

### Proposal-only

- `PROPOSE_ARCHIVE`
- `PROPOSE_RETIREMENT`
- `PROPOSE_PROMOTION`
- `PROPOSE_MOVE_OR_RENAME`

### Repair

- `REPAIR_EXISTING_PR`
- `REPLACE_UNSAFE_PR`

Hard deletion is not supported in v1.

## 12. Operation payload requirements

Every operation has a specific required payload. Creates require complete content and absence checks. Existing-file changes require expected Git object IDs. Exact replacement requires unique match counts. Heading append requires a unique heading and duplicate-content rule. Structured updates require stable record keys and deterministic transition rules. Consolidation and supersession preserve source memory and add successor relationships. Proposal operations never perform destructive execution. Repair operations identify the exact PR head and audit findings.

## 13. Packet envelope

Required fields:

- `schema_version`
- `packet_id`
- `created_at`
- `prepared_by`
- `caller`
- `run_intent`
- `intent`
- `approval_basis`
- `authority_class`
- `privacy_class`
- `repository`
- `base_ref`
- `expected_base_object`
- `destination_policy_version`
- `primary_project`
- `affected_projects`
- `changes`
- `verification`
- `non_promotions`
- `resource_limits`
- `packet_hash`
- `human_summary`

Optional fields include `repair_context` and `merge_verification_context`.

Copy/paste transport should use explicit begin and end markers around the authoritative JSON object.

## 14. Git object identifiers

Do not assume SHA-1 forever. Git objects are represented as an algorithm and value pair. Initially supported algorithms are `sha1` and `sha256`, with length validation by algorithm.

## 15. Canonical packet hashing

1. Parse JSON with duplicate-key rejection.
2. Remove the top-level `packet_hash` field.
3. Normalize embedded text newlines to LF.
4. Serialize with deterministic key ordering, no insignificant whitespace, stable scalar encoding, and preserved array order.
5. Hash canonical UTF-8 bytes with SHA-256.
6. Store the lowercase hexadecimal digest in `packet_hash`.

The compiler recomputes and verifies the hash rather than trusting the submitted value.

## 16. Destination policy

Every plan uses a versioned destination policy. The policy defines permitted repositories and base refs, canonical and continuity path classes, generated-view denial, workflow and engine denial, Project ownership, file types, and operation-specific destination rules.

The manifest records the policy version and hash. A future apply must reject a plan if the policy changed after planning.

## 17. Destination rules

Athena chooses destinations; Spear validates them. Spear verifies path normalization, allowlists, memory class, canonical class, ownership, affected Projects, and denied surfaces. It blocks rather than inventing a destination.

## 18. Caller authentication boundary

Packet integrity does not authenticate the submitter. Future gateways must provide authenticated caller identity, least-privilege credentials, replay protection, timestamp, nonce, rate limiting, and audit logging.

- Apple Shortcuts uses a revocable gateway credential and no GitHub token.
- n8n uses a service credential limited to approved endpoints.
- Hermes is candidate-only by default.
- GitHub Actions uses the authenticated repository actor.

## 19. Resource limits

Default v0.2 limits:

- packet JSON: 1 MiB;
- one change payload: 256 KiB;
- changes per packet: 50;
- changed files: 50;
- total proposed diff: 2 MiB;
- one resulting file: 1 MiB unless policy grants an exception;
- nested JSON depth: 50;
- planning timeout: 120 seconds.

Exceeding a hard limit blocks before worktree application.

## 20. Deterministic ordering

Changes are processed in packet order. Duplicate change IDs block. Manifest paths are lexicographically sorted. Conflicting operations on one target block unless an explicit composition rule permits them. Warning and blocker codes are sorted deterministically.

## 21. Validation pipeline

### A. Transport and parse

Validate markers, size, duplicate keys, schema version, and packet hash.

### B. Caller and intent

Validate caller metadata, maximum authority, run intent, replay state, and nonce.

### C. Approval and authority

Validate approval basis, authority compatibility, promotion basis, and repair references.

### D. Privacy

Validate privacy classes, scan prohibited patterns, block unsafe content, and redact errors.

### E. Destination

Validate repository, base, policy version, normalized paths, denied surfaces, and primary ownership.

### F. Source state

Validate base object, existing target objects, target absence, repair head, change-ID uniqueness, and target conflicts.

### G. Operation validation

Validate operation-specific payloads, referenced record IDs, allowed status transitions, and duplicate behavior.

### H. Temporary worktree

Apply changes in a clean temporary checkout, parse resulting Markdown/YAML/JSON, enforce limits, and build the exact manifest.

### I. Policy

Block direct-main plans, merge, force push, hard deletion, self-modification, and generated-view mixing.

### J. Result

Return exactly one primary status:

- `PLAN_CLEAN`
- `PLAN_CLEAN_WITH_WARNINGS`
- `BLOCKED`
- `DUPLICATE_NOOP`
- `STALE_SOURCE`
- `REPAIR_REQUIRED`
- `MANUAL_JAYSON_DECISION_REQUIRED`
- `VERIFICATION_CLEAN`
- `VERIFICATION_FAILED`

## 22. Warning policy

Warnings are advisory, consent-required, or blocking. Advisory findings may permit a clean plan. Consent-required findings produce a plan but prevent apply without Jayson. Blocking findings prevent an apply-eligible plan.

## 23. Plan/apply binding

The plan output contains packet hash, manifest hash, destination-policy version and hash, base and target objects, normalized operations, resulting file hashes, resource usage, warnings, blockers, and expiration.

Apply must accept only the normalized manifest, verify all hashes and policy state, recheck source objects and caller authority, and apply exactly the plan without freeform reinterpretation.

Default plan expiration is 60 minutes.

## 24. Concurrency and idempotency

Concurrency key:

```text
repository + packet_id
```

The same packet ID and hash returns existing state. The same packet ID with a different hash blocks as a collision. Retries may recover a missing PR from an existing branch but must not create duplicate branches or PRs. Stale source after planning requires a new plan.

## 25. Read-only compiler

The first implementation has no GitHub write permission.

Inputs:

- Spear packet;
- trusted caller metadata;
- read-only repository checkout;
- JSON Schema;
- destination policy.

Outputs:

- normalized packet;
- normalized manifest;
- proposed diff;
- changed-file list;
- source-state report;
- resource-limit report;
- warnings and blockers;
- packet and manifest hashes;
- result status.

It must run locally, in read-only GitHub Actions, behind an API, and for n8n, Apple Shortcuts, and Hermes callers.

## 26. Future apply separation

### Plan job

Read-only permissions only.

### Apply job

Contents and pull-request write permissions only, with no merge or workflow-administration authority.

The apply job consumes only a validated manifest and repeats source-state and policy checks immediately before writing.

## 27. Repair contract

Repair packets include original packet and manifest identifiers, PR number, expected head object, audit finding IDs, exact corrective changes, repair-cycle number, and whether same-PR repair is permitted.

Repairs add a corrective commit without force push, invalidate the prior audit, and require full re-audit. Default cycle limit is 5; protected or high-risk work uses 2. Unsafe repair produces a replacement-PR proposal.

## 28. Rollback contract

Every future apply manifest records base commit, created commit, changed paths, previous object IDs, revert model, independent-revert expectations, and later dependencies.

Pilot must prove Git revert, replacement PR when revert conflicts, post-rollback readback, and preservation of continuity and audit links.

## 29. Generated views

Generated Workboard and inventory views are non-authoritative. Source changes and generated refreshes use separate PRs. Spear does not directly edit generated files.

## 30. Adapter boundaries

Harvest and Sunset endpoints are adapters that produce Spear packets; they are not part of the core compiler.

Core interface:

- `POST /v1/spear/plan`
- `POST /v1/spear/apply` — disabled initially
- `POST /v1/spear/repair` — disabled initially
- `GET /v1/spear/status/{packet_id}`
- `POST /v1/spear/verify-merge` — disabled initially

## 31. PR contract for later phases

Future branches use:

```text
spear/<packet-id-short>/<slug>
```

PR bodies include packet and manifest hashes, approval basis, authority and privacy classes, policy version, ownership, changed files, checked source objects, validations, resource use, warnings, non-promotions, rollback metadata, and requested Athena audit. Pilot PRs begin as drafts.

## 32. Acceptance gates

Spear is not eligible for Atlas 4.0 migration until:

1. One pasted packet is sufficient.
2. No manual path, branch, or PR construction is required.
3. Duplicate work is prevented.
4. Ambiguity blocks before write.
5. Existing-file changes check source objects.
6. Multi-file packets validate fully before write.
7. Continuity memory cannot become canonical accidentally.
8. Prohibited paths and content are rejected with redacted errors.
9. Spear cannot write to `main`.
10. Spear cannot merge.
11. Spear cannot self-modify through ordinary packets.
12. Plan and apply are cryptographically bound.
13. Policy changes invalidate stale plans.
14. Branch and PR recovery is deterministic.
15. Repair works without force push.
16. Repair-cycle limits are enforced.
17. Athena can audit from packet, manifest, diff, source, and checks.
18. Post-merge readback proves exact state.
19. Rollback is tested.
20. Apple Shortcuts, n8n, and Hermes use the same contract.
21. Jayson’s workflow is simpler than manual GitHub editing.

## 33. Build sequence

1. Merge this specification and schema into the shadow repository.
2. Implement the read-only Python compiler.
3. Add unit and hostile-fixture tests.
4. Add a read-only GitHub Actions planning workflow.
5. Run the real packet corpus.
6. Red-team compiler behavior.
7. Add apply only after explicit approval.
8. Prove repair, recovery, post-merge verification, and rollback.
9. Run the shadow-repository pilot.
10. Decide whether Atlas 4.0 migration may begin.

## 34. Current gate

Authorized next build:

```text
Read-only Python compiler only.
```

Not authorized:

- production write job;
- repository migration;
- automatic Phoenix Flare;
- n8n write orchestration;
- Apple Shortcut production submission;
- Hermes write submission;
- old repository retirement.
