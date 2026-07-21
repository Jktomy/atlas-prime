# Atlas Lifecycle Engine

`tools.atlas_lifecycle` is the Prime-native deterministic lifecycle package.
Its classification is `SCRIPT ASSIST — LEVEL 1`. It exposes Level 1A read-only
mechanics and Level 1B temporary Preview, approval-carrier, and candidate
construction:

```text
python -m tools.atlas_lifecycle validate
python -m tools.atlas_lifecycle verify
python -m tools.atlas_lifecycle context [--quest-id ID]
python -m tools.atlas_lifecycle index build
python -m tools.atlas_lifecycle pilot [--repetitions N]
python -m tools.atlas_lifecycle event plan --event EVENT --trust-root TRUST --expected-trust-root-digest SHA256 --state STATE --expected-state-digest SHA256
python -m tools.atlas_lifecycle event candidate --event EVENT --trust-root TRUST --expected-trust-root-digest SHA256 --state STATE --expected-state-digest SHA256 --output-dir NEW_SYSTEM_TEMP_DIR
python -m tools.atlas_lifecycle sunset preview --request REQUEST_V2 --selected-route ROUTE [--fallback-route ROUTE ...] --output-dir NEW_SYSTEM_TEMP_DIR
python -m tools.atlas_lifecycle sunset approve --preview-dir PREVIEW_DIR --approval-mode STANDARD|GODDESS_MODE|GODDESS_MODE_SHARDBLADE --output-dir NEW_SYSTEM_TEMP_DIR
python -m tools.atlas_lifecycle sunset candidate --request APPROVAL_DIR/sunset-request-v3.json --preview-dir PREVIEW_DIR --approval-dir APPROVAL_DIR --output-dir NEW_SYSTEM_TEMP_DIR
python -m tools.atlas_lifecycle sunset verify --candidate-dir SYSTEM_TEMP_DIR
```

`validate` checks the trusted local schema catalog, bounded JSON, closed record
shapes, stable IDs, protected-data rules, canonical bytes, duplicate identities,
and replay identifiers. Its source fingerprint binds lifecycle doctrine,
schemas, trust roots, record paths, and canonical record payloads.

## Full Sunset front door

`Sunset this chat` semantically routes to `sunset preview`. Preview is read-only
and writes only a new system-temporary output directory. It emits:

- `sunset-preview.json`;
- `sunset-preview-receipt.json`.

Preview displays the exact lifecycle scope, semantic payload, expected record
inventory, Lesson Harvest, selected and fallback routes, source lock, and the
approval modes Jayson may choose. It creates no lifecycle candidate.

`sunset approve` consumes and verifies the exact Preview and emits:

- `sunset-approval.json`;
- `sunset-carrier.json`;
- `sunset-request-v3.json`;
- `sunset-approval-receipt.json`.

The carrier is route-neutral temporary execution evidence. It is sealed before
candidate construction, starts at `APPROVED_PENDING_COMPILATION`, and binds the
Preview digest, approval mode, semantic digest, source lock, and routes. It is
not canonical source and cannot claim Sunset completion.

`sunset candidate` requires all three exact inputs: the v3 request, Preview
directory, and approval directory. It rejects missing inputs, noncanonical
bytes, changed scope, changed Lesson Harvest, changed permanence mode, tampered
digests, stale base, unsafe output, or any other binding mismatch before output.

The candidate output contains exactly:

- `candidate-bundle.json`;
- `candidate-receipt.json`.

The bundle contains one Feather/Sunset/Sunrise pair and, for admitted-Quest
scope only, one replacement payload for the stable living Emberline plus one
new Quest checkpoint. Sunrise links only resolving Golden Wing IDs present in
the approved Lesson Harvest. New candidates and absorption-required findings
remain explicit follow-up obligations; the engine does not promote them.

## Boundaries

The engine does not call a model, author meaning, infer completion, mutate
canonical source, invoke GitHub, create a branch or PR, advance a Quest, promote
a Golden Wing, or run as a service. All construction writes are confined to
fresh directories beneath the system temporary root. Existing output,
repository output, path reuse, case-fold collisions, stale bases, and malformed
bindings fail closed.

Level 1B does not write canonical source, mark a pull request ready, or merge.
Branch-scoped publication remains a separately authorized Level 1C route.

A route failure after approval preserves the same carrier as resumable evidence.
Another operator may resume only after exact read-only reconciliation. A
temporary artifact, branch, draft PR, GREEN result, READY state, or merge API
response cannot claim `SUNSET COMPLETE`; canonical merged-main readback is
required.

## Evidence and measurements

Evidence verification bounds files, bytes, JSON depth, and protected values.
It rejects traversal, unsafe paths, links, encrypted members, and untrusted
self-supplied roots.

`pilot` measures deterministic local mechanics only. BEU, model usage, agent
elapsed work, and real-workflow human interventions remain `NOT_MEASURED`
unless supplied by a trusted native meter. File bytes or tokenizer estimates
may be reported only as clearly labeled proxies and never as trusted BEU.
