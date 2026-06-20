# Athena’s Spear Specification v0.2

Status: Pre-build compiler contract  
Repository target: `Jktomy/atlas-prime` shadow repository  
Owner: Project Codex / Project Artemis  
Authority: Current explicit Jayson direction  
Implementation state: Specification only; no production write authority

---

## 1. Mission

Athena’s Spear (“Spear”) accepts one complete packet prepared by Athena, validates the packet and its requested repository changes, deterministically computes the exact result, and returns a machine-readable plan.

After the read-only compiler is proven and a separate apply phase is approved, Spear may consume an already-validated manifest to create one branch, one commit, and one pull request. Spear stops before merge.

Spear feeds clean continuity memory and approved canonical source changes into the GitHub Spiritual Realm.

```text
Athena interprets.
Spear validates and files.
GitHub exposes.
Athena audits.
Jayson decides permanence.
```

---

## 2. Non-goals

Spear does not:

- interpret the original conversation;
- infer Jayson's intent from raw chat;
- invent decisions;
- choose a Project when ownership is ambiguous;
- invent canonical destinations;
- decide promotion;
- merge;
- write directly to `main`;
- force-push;
- hard-delete in v1;
- modify its own engine or workflow through ordinary packets;
- store prohibited private evidence.

---

## 3. User experience

Normal flow:

1. Athena prepares one complete packet.
2. Jayson pastes the packet into Spear.
3. Spear returns either a clean plan, warnings, or a safe block.
4. Later, after apply mode is separately approved, the same contract creates one PR.
5. Athena audits the PR.
6. Jayson decides whether to merge.
7. Athena verifies merged `main`.

Jayson should not need to provide:

- paths;
- branch names;
- commit messages;
- pull-request titles or bodies;
- patch types;
- file-by-file formatting;
- repository topology;
- GitHub API details.

---

## 4. Supported callers

Future callers may include:

- Athena in ChatGPT;
- Apple Shortcuts;
- n8n;
- Hermes agents;
- approved bots;
- GitHub Actions;
- a future Atlas app.

All callers use the same language-neutral JSON contract.

Caller authentication is separate from packet integrity.

---

## 5. Run intents

Every packet declares exactly one `run_intent`:

- `PLAN_ONLY`
- `CREATE_PR`
- `REPAIR_PR`
- `VERIFY_MERGE`

v0.2 implementation authority:

- `PLAN_ONLY` is the only authorized implementation target.
- `CREATE_PR`, `REPAIR_PR`, and `VERIFY_MERGE` are schema-defined for compatibility but remain disabled until separately approved.

---

## 6. Memory classes

### WORKING_MEMORY

Active chat context. Not a GitHub object by itself.

### CONTINUITY_MEMORY

Durable but non-governing memory:

- Harvest Record;
- Sunset Record;
- Synthesis Record;
- Continuity Record;
- Aegis Lesson;
- research and decision context not yet promoted.

### CANONICAL_MEMORY

Governing Atlas source:

- doctrine;
- policy;
- explicit decision;
- Project or Operation summary;
- runbook;
- active state;
- command behavior;
- recovery standard.

Continuity memory never becomes canonical through storage, age, repetition, or consolidation alone.

---

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

### Compatibility matrix

A child change must use an authority permitted by the packet authority:

| Packet authority | Permitted change authority |
|---|---|
| CONTINUITY_MEMORY | CONTINUITY_MEMORY |
| STATE_UPDATE | STATE_UPDATE, CONTINUITY_MEMORY |
| DECISION_UPDATE | DECISION_UPDATE, CONTINUITY_MEMORY |
| CANONICAL_UPDATE | CANONICAL_UPDATE, STATE_UPDATE, DECISION_UPDATE, CONTINUITY_MEMORY |
| PROMOTION | PROMOTION, CANONICAL_UPDATE, STATE_UPDATE, DECISION_UPDATE, CONTINUITY_MEMORY |
| SUPERSESSION | SUPERSESSION, CONTINUITY_MEMORY |
| ARCHIVE_PROPOSAL | ARCHIVE_PROPOSAL, CONTINUITY_MEMORY |
| AEGIS_EVOLUTION | AEGIS_EVOLUTION, CANONICAL_UPDATE, CONTINUITY_MEMORY |
| REPAIR | REPAIR plus the original packet's authorized classes |

The compiler enforces the matrix. The schema alone is not considered sufficient enforcement.

---

## 8. Approval basis

Packets that may affect canonical memory or an existing PR must contain `approval_basis`.

Allowed approval sources:

- `EXPLICIT_JAYSON_INSTRUCTION`
- `APPROVED_PREVIEW_EXECUTE`
- `PHOENIX_BURN_DISPOSITION`
- `PR_AUDIT_REPAIR_AUTHORIZATION`
- `NONE_REQUIRED_CONTINUITY_ONLY`

Required fields:

- `source`
- `reference`
- `approved_scope`
- `approved_at` when known

Spear validates that an approval basis is present and compatible with the authority class. Spear does not decide whether Athena interpreted the approval correctly; Athena and Jayson remain responsible for meaning.

---

## 9. Privacy classes

Every packet and change declares:

- `PUBLIC_CLEAN`
- `PRIVATE_CLEAN_SUMMARY`
- `POINTER_ONLY`
- `PROHIBITED`

`PROHIBITED` always blocks.

Prohibited GitHub content includes:

- passwords;
- API keys;
- tokens;
- MFA or recovery codes;
- private keys;
- seed phrases;
- real `.env` values;
- raw PHI;
- raw finance or account evidence;
- private runtime registers;
- IP maps;
- device registers;
- protected exports.

Prohibited-content errors must redact detected values from all logs and reports.

Pattern scanning is support, not proof. Athena's review remains required.

---

## 10. Record types

Spear v1 contract supports:

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

---

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

---

## 12. Operation payload requirements

### CREATE_FILE

Requires:

- `expected_absent: true`
- complete `content`

### CREATE_RECORD_IN_BUNDLE

Requires:

- target bundle path;
- `record_key`;
- complete `record`;
- duplicate behavior `BLOCK`, `NOOP_IF_EQUAL`, or `UPDATE_IF_MATCHED`;
- expected blob ID if bundle exists;
- `expected_absent: true` if bundle does not exist.

### CREATE_CROSS_REFERENCE

Requires:

- relationship type;
- source record ID;
- target record ID;
- expected blob ID for the relationship store or source record.

### REPLACE_EXACT

Requires:

- `find`;
- `replace`;
- expected occurrence count;
- expected blob ID.

### APPEND_UNDER_UNIQUE_HEADING

Requires:

- exact heading;
- append block;
- duplicate-content policy;
- expected blob ID.

### UPDATE_STRUCTURED_FIELD

Requires:

- record key;
- field path;
- expected current value when safety-relevant;
- new value;
- expected blob ID.

### UPSERT_STRUCTURED_RECORD

Requires:

- stable record key;
- complete record or bounded field patch;
- duplicate behavior;
- expected blob ID or `expected_absent: true`.

### MARK_CONSOLIDATED / MARK_SUPERSEDED

Requires:

- source record IDs;
- destination or successor record ID;
- exact status transition;
- expected blob IDs.

### ADD_RELATIONSHIP / REMOVE_RELATIONSHIP

Requires:

- relationship type;
- source ID;
- target ID;
- expected blob ID.

### Proposal operations

Require:

- current path;
- proposed destination or disposition;
- reason;
- replacement routing;
- no destructive execution.

### REPAIR_EXISTING_PR

Requires:

- PR number;
- expected PR head object ID;
- audit finding IDs;
- exact corrective changes;
- repair-cycle number.

### REPLACE_UNSAFE_PR

Requires:

- original PR number;
- reason repair is unsafe;
- expected original head object ID;
- complete replacement packet linkage.

---

## 13. Packet envelope

Required packet fields:

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

Optional:

- `repair_context`
- `merge_verification_context`

Recommended text markers for copy/paste transport:

```text
-----BEGIN ATHENAS_SPEAR_PACKET-----
{ JSON packet }
-----END ATHENAS_SPEAR_PACKET-----
```

The JSON object is authoritative. Markers are transport guards.

---

## 14. Git object identifiers

Do not assume SHA-1 forever.

Represent Git object identifiers as:

```json
{
  "algorithm": "sha1",
  "value": "40-or-64-character-lowercase-hex"
}
```

Initially supported:

- `sha1`
- `sha256`

The compiler validates length by algorithm.

---

## 15. Canonical packet hashing

Packet hash rules:

1. Parse JSON with duplicate-key rejection.
2. Remove the top-level `packet_hash` field.
3. Serialize using UTF-8 JSON Canonicalization Scheme-compatible ordering:
   - lexicographically sorted object keys;
   - no insignificant whitespace;
   - stable JSON scalar encoding;
   - array order preserved.
4. Embedded text content is hashed exactly as represented after JSON decoding.
5. Newlines inside embedded content are normalized to LF before canonical serialization.
6. Hash canonical bytes with SHA-256.
7. Store lowercase hexadecimal digest in `packet_hash`.

The compiler returns the canonical representation hash and never trusts an unverified supplied hash.

---

## 16. Destination policy

Every plan uses a versioned destination policy, for example:

```text
atlas-prime-destination-policy/0.1
```

The policy defines:

- permitted repositories;
- allowed base refs;
- canonical path classes;
- continuity-memory path classes;
- generated-view denial;
- workflow and engine denial;
- Project ownership;
- file extensions;
- per-operation allowed destinations.

The normalized manifest records the policy version and hash.

Apply must reject a manifest if the current policy version or hash differs from the plan.

---

## 17. Destination rules

Athena chooses destinations. Spear validates.

Spear verifies:

- continuity memory targets a permitted memory surface;
- canonical updates target permitted canonical surfaces;
- generated views are not edited directly;
- workflow and Spear engine files are denied to ordinary packets;
- each record has one primary owner;
- affected Projects are explicit;
- the path is normalized and inside the repository;
- no path traversal or encoded traversal exists.

Spear blocks rather than inventing a destination.

---

## 18. Caller authentication boundary

Packet integrity does not authenticate the submitter.

Future gateways must provide:

- authenticated caller identity;
- least-privilege credentials;
- replay protection;
- request timestamp;
- request nonce;
- rate limits;
- audit logging;
- caller-to-authority restrictions.

Examples:

- Apple Shortcuts: device-specific revocable gateway credential; no GitHub token in the Shortcut.
- n8n: service credential limited to approved endpoints and caller class.
- Hermes: agent identity and candidate-only authority by default.
- GitHub Actions manual run: authenticated repository actor.

Authentication is an adapter/gateway responsibility. Spear still validates caller identity and permitted maximum authority from trusted gateway metadata.

---

## 19. Resource limits

Default v0.2 limits:

- packet JSON: 1 MiB;
- one change content payload: 256 KiB;
- changes per packet: 50;
- changed files: 50;
- total proposed diff: 2 MiB;
- one resulting file: 1 MiB unless destination policy grants an exception;
- nested JSON depth: 50;
- string field length: 1 MiB;
- planning timeout: 120 seconds.

Limits are policy-controlled and reported in the plan.

Exceeding a hard limit blocks before worktree application.

---

## 20. Deterministic ordering

- Changes are processed in packet array order.
- Duplicate `change_id` values block.
- Manifest files are sorted lexicographically by normalized path.
- Within each file, applied changes retain packet order.
- Conflicting operations on the same target block unless an operation-specific composition rule explicitly permits them.
- PR body tables use manifest file order.
- Warning and blocker codes are sorted by severity, then code, then target path.

---

## 21. Validation pipeline

### Stage A — Transport and parse

- markers complete when markers are used;
- payload within size limit;
- duplicate JSON keys rejected;
- supported schema version;
- packet hash verified.

### Stage B — Caller and intent

- authenticated caller metadata present when required;
- caller maximum authority compatible;
- run intent recognized and enabled;
- replay and nonce checks satisfied by gateway.

### Stage C — Approval and authority

- approval basis compatible;
- child authority compatible with packet authority;
- no continuity-to-canonical escalation;
- promotion contains explicit basis;
- repair identifies exact PR and head.

### Stage D — Privacy

- privacy classes valid;
- prohibited patterns scanned;
- prohibited content blocked;
- error output redacted.

### Stage E — Destination

- repository and base allowed;
- destination policy version valid;
- paths normalized;
- denied surfaces blocked;
- primary ownership present.

### Stage F — Source state

- base object matches;
- existing targets match expected object IDs;
- new targets are absent when required;
- repair head matches;
- no change-ID collisions;
- no incompatible target conflicts.

### Stage G — Operation validation

- operation payload schema satisfied;
- all referenced record IDs exist or are created in the same packet;
- status transitions allowed;
- duplicate behavior deterministic.

### Stage H — Temporary worktree

- clean read-only checkout;
- apply changes in order;
- parse resulting Markdown/YAML/JSON as applicable;
- enforce file and diff limits;
- build exact changed-file manifest.

### Stage I — Policy

- no main write plan;
- no merge;
- no force push;
- no hard deletion;
- no self-modification;
- no generated-view mixing unless explicitly policy-approved.

### Stage J — Result

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

---

## 22. Warning policy

Warnings are classified:

### Advisory

May still allow a clean plan:

- semantically similar continuity memory;
- missing optional cross-reference;
- unusually large but within limits;
- noncanonical naming style.

### Consent-required

Plan is produced but apply must not proceed without Jayson:

- destination is permitted but unusual;
- canonical change crosses multiple Projects;
- existing unresolved promotion conflict;
- repair-cycle limit approaching.

### Blocking

No plan eligible for apply:

- ambiguous primary owner;
- missing approval basis;
- stale source;
- prohibited content;
- denied path;
- authority escalation;
- packet collision;
- incomplete transport;
- unsupported operation;
- destination policy mismatch.

---

## 23. Plan/apply binding

The plan output contains:

- packet hash;
- manifest hash;
- destination-policy version and hash;
- base object ID;
- every expected target object ID;
- normalized operation list;
- resulting file hashes;
- resource-limit report;
- warning and blocker report;
- plan expiration timestamp.

Apply must:

1. accept only the normalized manifest artifact;
2. verify packet and manifest hashes;
3. verify plan has not expired;
4. verify destination-policy version and hash;
5. recheck base and target object IDs;
6. recheck caller/apply authorization;
7. apply exactly the manifest;
8. refuse all freeform reinterpretation.

Default plan expiration: 60 minutes.

---

## 24. Concurrency and idempotency

Concurrency key:

```text
repository + packet_id
```

Rules:

- one active plan/apply sequence per packet ID;
- same packet ID + same hash returns existing state;
- same packet ID + different hash blocks as collision;
- same packet and manifest after PR creation returns existing PR;
- branch pushed but PR missing triggers deterministic PR recovery;
- retry never creates a second branch for the same packet;
- stale source after planning blocks apply and requires a new plan.

---

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
- warnings;
- blockers;
- packet hash;
- manifest hash;
- result status.

The compiler must run:

- locally;
- in GitHub Actions;
- behind an API;
- from n8n;
- from Apple Shortcuts;
- for Hermes agent packets.

---

## 26. Future apply separation

### Plan job

Permissions:

- contents: read;
- pull requests: read;
- issues: read only when needed;
- no write permissions.

### Apply job

Permissions:

- contents: write;
- pull requests: write;
- no merge;
- no workflow administration.

The apply job consumes only a valid manifest and repeats source-state and policy checks immediately before write.

---

## 27. Repair contract

Repair packets contain:

- original packet ID;
- original manifest hash;
- PR number;
- expected PR head object ID;
- audit finding IDs;
- exact corrective changes;
- repair-cycle number;
- same-PR permission.

Flow:

1. Re-read the PR.
2. Verify the head.
3. Validate repair operations.
4. Add one corrective commit without force push when permitted.
5. Persist repair-cycle count.
6. Mark prior audit stale.
7. Require full Athena re-audit.

Default cycle limit: 5.  
Protected/high-risk cycle limit: 2.

Unsafe repair results in a replacement-PR proposal.

---

## 28. Rollback contract

Rollback is not a free-text hint.

Every apply manifest later records:

- base commit;
- created commit;
- changed paths;
- previous object IDs;
- safe revert command model;
- whether the change can be reverted independently;
- dependencies on later commits.

Pilot must prove:

- Git revert of an isolated Spear commit;
- replacement PR when revert conflicts;
- post-rollback readback;
- preservation of continuity records and audit links.

---

## 29. Generated views

Generated Workboard or inventory views are non-authoritative.

Default:

- source PR changes only source;
- generated views refresh after source merge in a separate workflow and PR;
- generated PR is audited separately;
- no generated file is edited directly by Spear.

---

## 30. Adapter boundaries

`POST /v1/harvest` and `POST /v1/sunset` are adapters that produce Spear packets. They are not part of the core compiler.

Core endpoints:

- `POST /v1/spear/plan`
- `POST /v1/spear/apply` — disabled initially
- `POST /v1/spear/repair` — disabled initially
- `GET /v1/spear/status/{packet_id}`
- `POST /v1/spear/verify-merge` — disabled initially

---

## 31. PR contract for later phases

Branch:

```text
spear/<packet-id-short>/<slug>
```

PR body includes:

- packet ID and hash;
- manifest hash;
- plan expiration and apply time;
- approval basis;
- authority and privacy classes;
- destination-policy version and hash;
- primary and affected Projects;
- changed files;
- source objects checked;
- validations;
- resource use;
- warnings;
- non-promotions;
- rollback metadata;
- requested Athena audit.

PRs begin as draft during the pilot.

---

## 32. Acceptance gates

Spear is not eligible for Atlas 4.0 migration until:

1. One pasted packet is sufficient.
2. No manual path, branch, or PR construction is required.
3. The same packet cannot create duplicate work.
4. Ambiguity blocks before write.
5. Existing-file changes check source objects.
6. Multi-file packets validate fully before write.
7. Continuity memory cannot become canonical accidentally.
8. Prohibited paths and content are rejected with redacted errors.
9. Spear cannot write to main.
10. Spear cannot merge.
11. Spear cannot self-modify through ordinary packets.
12. Plan and apply are cryptographically bound.
13. Policy changes invalidate stale plans.
14. Branch/PR failure recovery is deterministic.
15. Repair works without force push.
16. Repair-cycle limits are enforced.
17. Athena can audit from packet, manifest, diff, source, and checks.
18. Post-merge readback proves exact state.
19. Rollback is tested.
20. Apple Shortcuts, n8n, and Hermes use the same contract.
21. Jayson’s workflow is simpler than manual GitHub editing.

---

## 33. Build sequence

1. Merge this specification and schema into the shadow repository.
2. Implement the read-only Python compiler.
3. Add unit and hostile-fixture tests.
4. Add a read-only GitHub Actions planning workflow.
5. Run the real packet corpus.
6. Red-team compiler behavior.
7. Add apply only after explicit approval.
8. Prove repair, recovery, post-merge verification, and rollback.
9. Run shadow-repository pilot.
10. Decide whether Atlas 4.0 migration may begin.

---

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
