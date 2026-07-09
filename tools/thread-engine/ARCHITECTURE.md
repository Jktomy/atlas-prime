# Thread Engine Fixture Architecture

Gate 7B separates doctrine, disabled implementation, proof, and activation:

- `thread-engine.md` defines the durable workflow doctrine.
- `tools/thread-engine/` contains only the pilot-disabled fixture implementation.
- Gate 7C-E remain responsible for proof harnesses, parity proof, replay, recovery, and remote evidence.
- Gate 7F is the earliest route for disabled production adapter implementation and proof.
- Gate 7G is the earliest route for activation decisions.

## State Machine

```text
PACKAGE_AUDIT
-> PARSER_PREFLIGHT
-> WEAVE_SCHEMA
-> FIXTURE_BOUNDARY
-> BASE_TREE_VERIFY
-> THREAD_SET_VERIFY
-> CANDIDATE_STAGE
-> CANDIDATE_TREE_VERIFY
-> RECEIPT
-> STOP
```

Every checkpoint is journaled before transition. A requested resume point must match the next uncompleted checkpoint; otherwise the engine stops with a classified rejection receipt.

## Fixture Adapter

The only adapter in Gate 7B is a fixture adapter. It copies a checked-in fixture base into a unique temporary sandbox, applies declared Threads there, and reports deterministic receipts. It refuses absolute paths, traversal, backslashes, empty segments, symlinks, undeclared paths, duplicate paths, and case-fold collisions.

The fixture adapter never mutates the source checkout and never calls Git, GitHub, workflow APIs, network APIs, or caller-provided commands.

## Mission-Scoped Production Adapter

The Gate 7F production adapter is separate from the fixture adapter. Gate 7G activates it only as `THREAD_ENGINE_ACTIVE_MISSION_SCOPED` and `DRAFT_PR_ONLY`.

The adapter can operate only when a mission-specific authority declares the exact repository, remote, base SHA, branch, changed path set, source blobs, payload hashes, candidate tree hash, final path-set hash, network allowlist, receipt name, stop point, and mission SHA-256. It uses Fresh Clone First, prepares candidate files outside the checkout, installs only the complete validated candidate set, verifies exact bytes and `git diff --check`, verifies the staged diff, creates one deterministic branch and one single-parent commit, pushes without force, creates one draft PR, reads the PR back, emits a deterministic receipt, and stops before ready transition or merge.

The production adapter denies direct-main write, force push, automatic merge, ready transition, workflow dispatch, repository-setting mutation, generated-output mutation, Workboard mutation, standing authority, arbitrary command execution, shell evaluation, undeclared paths, symlinks, path traversal, absolute paths, backslashes, duplicate paths, case-fold collisions, stale bases, existing mission branches, duplicate PRs, and mismatched receipts.

Disablement route: restore the Gate 7F disabled posture through one narrow source PR that changes the mission schema, authority constants, launcher intent, examples, tests, and status text back to disabled-proof mode. Preserve evidence, open draft PRs, and branches; do not delete proof or harmless state as part of disablement.

## Rejection Codes

Bounded rejection receipts use these error codes:

- `INTENT_REQUIRED`
- `RUNTIME_BYPRODUCT`
- `INVALID_JSON`
- `WEAVE_SCHEMA`
- `RESUME_MISMATCH`
- `PATH_REJECTED`
- `BOUNDARY_REJECTED`
- `SYMLINK_REJECTED`
- `TREE_HASH_MISMATCH`
- `THREAD_SET_REJECTED`
- `SOURCE_HASH_MISMATCH`
- `PAYLOAD_HASH_MISMATCH`
- `OUTPUT_HASH_MISMATCH`
- `DELETE_AUTHORITY_REQUIRED`
- `CANDIDATE_TREE_MISMATCH`
- `REGULAR_FILE_REQUIRED`
