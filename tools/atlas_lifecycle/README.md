# Atlas Lifecycle Engine

`tools.atlas_lifecycle` is the Prime-native deterministic lifecycle package.
Its classification is `SCRIPT ASSIST — LEVEL 1`. This G3-B transaction exposes
only Level 1A read-only mechanics:

```text
python -m tools.atlas_lifecycle validate
python -m tools.atlas_lifecycle verify
python -m tools.atlas_lifecycle context [--quest-id ID]
python -m tools.atlas_lifecycle index build
python -m tools.atlas_lifecycle pilot [--repetitions N]
python -m tools.atlas_lifecycle event plan --event EVENT --trust-root TRUST --expected-trust-root-digest SHA256 --state STATE --expected-state-digest SHA256
```

`validate` checks the trusted local schema catalog, bounded JSON, closed record
shapes, stable IDs, protected-data rules, canonical bytes, duplicate identities,
and replay identifiers. Its source fingerprint binds the lifecycle contract,
the lifecycle-event contract, every lifecycle schema, canonical trust-root
doctrine and expectations, record paths, and canonical record payloads.
Canonical lifecycle events use the one exact immutable path declared in their
authorized route. That event-only path exception is content-addressed, bound to
the physical file, and case-fold collision checked; every other lifecycle
record retains the `<record_id>.json` rule. Event identity remains `record_id`.
`verify` adds exact-HEAD, parent-Feather, and Quest revision checks. Its optional
archive mode requires a ZIP, independent sidecar, receipt, and a
repository-controlled external trust root.

G4-A adds one trusted `atlas.lifecycle.event` envelope for `CHECKPOINT` and
`TRANSITION` fixtures plus a separate closed external event trust-root schema.
This is contract validation only: it does not plan a delta, generate a
candidate, write a canonical event, invoke Thread Engine or Foundry, or process
GitHub activity.

The engine does not call a model, author meaning, infer completion, mutate a
record, write a file, invoke GitHub, create a branch or PR, advance a Quest,
promote a Golden Wing, or run as a service. It executes only the fixed
`git rev-parse HEAD` readback needed for stale-state verification.

Code presence does not activate Level 1B or Level 1C. Candidate generation,
branch-scoped apply, Thread Engine profiles, Foundry integration, and GitHub
automation remain unactivated and outside G4-B.

`event plan` is the G4-B read-only planner. It validates the event, external
trust root, and closed current-state snapshot; resolves exact prior state;
rejects stale, replayed, concurrent, unauthorized, missing-target, and
incomplete-acceptance inputs; and prints deterministic proposed deltas. It
does not create candidate bytes, write any file, or invoke GitHub.
The trust-root file must come from `lifecycle/trust-roots/` and match an
independently supplied SHA-256 expectation from the controlling handoff.
The current-state snapshot likewise requires an independently supplied digest,
so replacing an event, trust root, and state snapshot together cannot pass.

`context` emits only current Quest position, latest valid Feather, unresolved
blockers, next gate, related Golden Wings, exact source references, source
fingerprint, and stale-projection warnings. With no canonical Quest Emberline it
returns the same bounded shape with null position values. If several admitted
Quests exist, an exact `--quest-id` is required.

`index build` is check-only. It computes the complete website index in memory,
validates it against website-index v2, and compares it to
`generated/lifecycle/website-index-v2.json` without creating or changing that
file. Source revision is the exact `HEAD:lifecycle` Git tree object. The
timestamp is deterministically derived from that tree identity, never a wall
clock, so shallow checkouts and unrelated commits do not create false drift.

`pilot` performs the G3-D reproducible measurement against three harmless
noncanonical fixtures. It compares the files, bytes, and explicit process steps
that a model-visible manual reconstruction would require with the one compact
context result. It also measures local machine execution, exact field
reconstruction, retries, errors, and a protected-boundary rejection. It makes
no model call. BEU, model usage, agent elapsed work, and real-workflow human
interventions remain `NOT_MEASURED` unless supplied by a trusted native meter.

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
