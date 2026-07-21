# Atlas Lifecycle Engine

`tools.atlas_lifecycle` is the Prime-native deterministic lifecycle package.
Its classification is `SCRIPT ASSIST — LEVEL 1`. It exposes Level 1A read-only
mechanics and the explicit Level 1B temporary Preview, approval-carrier, and
candidate commands:

```text
python -m tools.atlas_lifecycle validate
python -m tools.atlas_lifecycle verify
python -m tools.atlas_lifecycle context [--quest-id ID]
python -m tools.atlas_lifecycle index build
python -m tools.atlas_lifecycle pilot [--repetitions N]
python -m tools.atlas_lifecycle event plan --event EVENT --trust-root TRUST --expected-trust-root-digest SHA256 --state STATE --expected-state-digest SHA256
python -m tools.atlas_lifecycle event candidate --event EVENT --trust-root TRUST --expected-trust-root-digest SHA256 --state STATE --expected-state-digest SHA256 --output-dir NEW_SYSTEM_TEMP_DIR
python -m tools.atlas_lifecycle sunset preview --request REQUEST_V2 --selected-route ROUTE --fallback-route ROUTE [--fallback-route ROUTE ...] --output-dir NEW_SYSTEM_TEMP_DIR
python -m tools.atlas_lifecycle sunset approve --preview-dir PREVIEW_DIR --approval-mode STANDARD|GODDESS_MODE|GODDESS_MODE_SHARDBLADE --output-dir NEW_SYSTEM_TEMP_DIR
python -m tools.atlas_lifecycle sunset candidate --request APPROVAL_DIR/sunset-request-v3.json --preview-dir PREVIEW_DIR --approval-dir APPROVAL_DIR --output-dir NEW_SYSTEM_TEMP_DIR
python -m tools.atlas_lifecycle sunset verify --candidate-dir SYSTEM_TEMP_DIR
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
`verify` adds parent-Feather and Quest revision checks. A canonical record's
`expected_main_sha` is immutable historical transaction-input evidence, not a
lease that expires whenever `main` advances. The `sunset preview` and approved
`sunset candidate` commands reject a stale transaction base before output.
Optional archive verification requires a ZIP, independent sidecar, receipt,
and a repository-controlled external trust root.

G4-A adds one trusted `atlas.lifecycle.event` envelope for `CHECKPOINT` and
`TRANSITION` fixtures plus a separate closed external event trust-root schema.
This is contract validation only: it does not plan a delta, generate a
candidate, write a canonical event, invoke Thread Engine or Foundry, or process
GitHub activity.

The engine does not call a model, author meaning, infer completion, mutate
canonical source, invoke GitHub, create a branch or PR, advance a Quest,
promote a Golden Wing, or run as a service. Level 1A executes only the fixed
`git rev-parse HEAD` readback needed for stale-state verification. The explicit
Level 1B commands have only the temporary write boundary described below.

## Full Sunset front door

`Sunset this chat` semantically routes to `sunset preview`. Preview writes only
one new system-temporary directory containing `sunset-preview.json` and
`sunset-preview-receipt.json`. It binds the exact source lock, lifecycle scope,
semantic payload, Lesson Harvest, expected record inventory, selected route,
fallback routes, and permitted approval modes. At least one `--fallback-route`
is required; the option may be repeated. Preview creates no lifecycle candidate
and cannot be bypassed by Goddess Mode or Shardblade.

`sunset approve` verifies the exact Preview and emits
`sunset-approval.json`, `sunset-carrier.json`, `sunset-request-v3.json`, and
`sunset-approval-receipt.json`. The carrier starts at
`APPROVED_PENDING_COMPILATION` and is route-neutral temporary execution
evidence. It is not canonical source and cannot claim Sunset completion.

`sunset candidate` requires all three exact inputs: the v3 request, Preview
directory, and approval directory. It rejects missing inputs, noncanonical
bytes, changed scope, changed Lesson Harvest, changed permanence mode, tampered
digests, stale base, unsafe output, or any other binding mismatch before output.
It reuses the existing v2 record compiler behind this mandatory approval gate,
then independently validates the approved record set.

Level 1B event candidate writes exactly `event.json`,
`candidate-manifest.json`, and `candidate-receipt.json` into one new directory
beneath the system temporary root. Approved Sunset candidate writes exactly
`candidate-bundle.json` and `candidate-receipt.json`; the bundle contains one
Feather/Sunset/Sunrise pair and, for admitted-Quest scope only, one replacement
payload for the stable living Emberline plus one new Quest checkpoint. The
replacement increments the Quest revision, binds the prior file digest, and
appends one Main-Gate journey entry without creating a second Emberline ID.
Sunrise links only resolving Golden Wing IDs already present in the approved
Lesson Harvest. New candidate and absorption-required dispositions remain
explicit follow-up obligations and do not self-promote.

Both event and Sunset routes bind exact transaction input and read back every
temporary byte. Existing output, repository output, path reuse, case-fold
collisions, stale transaction bases, and malformed bindings fail closed.
`sunset verify` is read-only and accepts later repository HEADs because the
bound base is historical transaction evidence.

Level 1B does not write canonical source, invoke GitHub, advance a Quest, mark a
pull request ready, or merge. Branch-scoped publication remains a separately
authorized Level 1C route such as Oathbringer.

A route failure after approval preserves the same carrier as resumable evidence.
Athena, Harmony, or Jayson PowerShell may resume only after exact read-only
reconciliation. A temporary artifact, branch, draft PR, GREEN result, READY
state, or merge API response cannot claim `SUNSET COMPLETE`; canonical
merged-main readback is required.

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
File-byte or tokenizer estimates may be reported only as labeled proxies.

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

## Living Quest Emberline

Quest Emberline schema v2 preserves one stable identity and canonical path per
admitted Quest. Its ordered journey uses Main, Side, Branched, and Final entry
types. `validate` enforces entry ordering, branch and return relationships,
revision-parent binding, and terminal completion rules. Other lifecycle records
remain immutable and continue to reference the stable Emberline ID.
