# Atlas Lifecycle Engine

`tools.atlas_lifecycle` is the Prime-native deterministic lifecycle package.
Its classification is `SCRIPT ASSIST — LEVEL 1`. This G3-B transaction exposes
only Level 1A read-only mechanics:

```text
python -m tools.atlas_lifecycle validate
python -m tools.atlas_lifecycle verify
```

`validate` checks the trusted local schema catalog, bounded JSON, closed record
shapes, stable IDs, protected-data rules, canonical bytes, duplicate identities,
and replay identifiers. `verify` adds exact-HEAD, parent-Feather, and Quest
revision checks. Its optional archive mode requires a ZIP, independent sidecar,
receipt, and a repository-controlled external trust root.

The engine does not call a model, author meaning, infer completion, mutate a
record, write a file, invoke GitHub, create a branch or PR, advance a Quest,
promote a Golden Wing, or run as a service. It executes only the fixed
`git rev-parse HEAD` readback needed for stale-state verification.

Code presence does not activate Level 1B or Level 1C. Candidate generation,
context/index mechanics, branch-scoped apply, Thread Engine profiles, Foundry
integration, and GitHub automation are outside G3-B.

## Evidence trust

Evidence verification never extracts an archive. It bounds input bytes, member
count, member bytes, aggregate expansion, compression ratio, JSON depth, and
JSON nodes. It rejects traversal, absolute paths, backslashes, encrypted
members, case-fold collisions, links, and special files.

The submitted archive, sidecar, and receipt cannot supply their own trust root.
The trust root must be a regular file below canonical
`lifecycle/trust-roots/`, and it independently binds the subject digest, local
receipt schema digest, and lifecycle contract digest. Diagnostics expose a
specific failure code without echoing submitted values or private paths.
