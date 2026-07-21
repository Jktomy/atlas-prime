---
title: "Atlas Lifecycle Contract"
atlas_id: "prime.lifecycle.contract"
status: "CANONICAL_ACTIVE"
source_type: "PROTOCOL"
authority_class: "CANONICAL_AUTHORED_SOURCE"
owner_project: "Atlas"
owner_operation: "Source Governance"
protected_level: "CRITICAL"
---

# Atlas Lifecycle Contract

## Storage

| Entity | Canonical source directory | Prefix | Immutability |
|---|---|---|---|
| Feather | `lifecycle/feathers/` | `FTR` | sealed records immutable |
| Feather Archive | `lifecycle/feather-archives/` | `FAR` | immutable event |
| Golden Wing | `lifecycle/golden-wings/` | `GWN` | revision or supersession |
| Quest Emberline | `lifecycle/quest-emberlines/` | `QEM` | one stable living map per admitted Quest |
| Quest checkpoint | `lifecycle/quest-checkpoints/` | `QCP` | immutable checkpoint |
| Sunset | `lifecycle/sunsets/` | `SUN` | immutable plan/checkpoint |
| Sunrise | `lifecycle/sunrises/` | `SRI` | immutable reconstruction |
| Continuity | `lifecycle/continuity/` | `CON` | immutable recovery record |
| Lifecycle receipt | `lifecycle/receipts/` | `LCR` | immutable independent binding |
| Lifecycle event | `lifecycle/events/` | `LEV` | append-only or explicit correction event |

Only schema-valid `.json` files belong in canonical record directories. Except for lifecycle events, filenames are the case-sensitive `record_id` plus `.json`. A lifecycle event is the sole filename exception: its authorized route must declare one exact immutable repository-relative `.json` path beneath `lifecycle/events/` before candidate generation. The event's full canonical payload, including that declared path, remains in `record_id` derivation; only `record_id` itself is omitted. The path is storage location, never identity, and cannot be reused for another event. Readers, projections, relationships, lineage, replay protection, and supersession continue to use `record_id`. Candidate manifests and lifecycle receipts must independently bind both the permanent event ID and exact path. No other lifecycle record type receives this exception. Test fixtures live only under `lifecycle/fixtures/` and declare `authority: NONCANONICAL_FIXTURE`.

## Lifecycle rules

Feather states are `DRAFT`, `SEALED`, `ARCHIVED`, `SUPERSEDED`, and `INVALIDATED`. A sealed Feather is never edited. Archival and supersession are new records that preserve stable readback and lineage.

Golden Wing states are `CANDIDATE`, `GATHERING_EVIDENCE`, `READY_FOR_PHOENIX_BURN`, `ABSORBED`, `REJECTED`, `SUPERSEDED`, and `HISTORICAL`. Advancement requires recurrence across independent contexts or one explicitly justified systemic exception. The engine never creates or promotes a Golden Wing automatically.

Lifecycle events use the one-envelope contract in `lifecycle-event-contract.md`. `CHECKPOINT` events preserve an in-progress position. `TRANSITION` events describe an Athena-authored requested state change and require independently trusted acceptance evidence. An ordinary merge or generated projection cannot create an authoritative transition.

Quest Emberlines use monotonically increasing integer revisions while preserving one stable record ID and one canonical file per admitted Quest. Each revision binds the SHA-256 digest of the previous canonical Emberline file. The living map contains ordered `Main-*`, `Side-*`, `Branched-*`, and `Final-*` entries. Side entries must resolve a departure and return; Branched entries must record the superseded and newly accepted direction. A completed Quest requires a Final entry, no unresolved blockers, and `next_gate: CLOSED`. Candidate Quests use `candidate_quest_ref`; they do not receive a canonical `quest_id`. Non-Quest work leaves both fields absent.

Every completed Sunset is one atomic continuity transaction that creates exactly one new sealed Feather and exactly one immutable Sunset bound to that Feather. This rule applies to admitted-Quest, candidate-Quest, non-Quest, and protected-domain work; non-Quest work never receives an invented Quest identity. The Feather retains the rich authored restart meaning, while the Sunset retains the closeout assessment, unresolved items, next safe action, next approval gate, source locks, and protected pointers.

This completed lifecycle transaction is the **full Atlas Sunset**. It is not a continuity snapshot, and a compact continuity view cannot claim its closeout, cardinality, lesson evaluation, or recovery result. The shared historical word `sunset` on a low-level continuity command does not change this semantic route.

Sunrise resolves one exact Sunset/Feather pair. It must name the same Feather recorded by the Sunset and reconstruct only the bounded compact context. A missing, null, dangling, reused, cross-scope, or mismatched Feather binding fails closed.

## Mandatory Sunset Preview and approval

`Sunset this chat` is a Preview request. It never authorizes immediate lifecycle candidate construction. Every full Atlas Sunset follows this exact semantic sequence:

```text
read current source and continuity
→ produce one user-visible Sunset Preview
→ stop for Jayson approval
→ seal one approval and route-neutral carrier
→ compile the exact lifecycle candidate
→ publish through one reviewed draft PR
→ validate and Strikeforce the exact head
→ perform the separately authorized permanence action
→ read back canonical main
```

The Preview binds the exact base, Project, Operation, Quest classification, proposed Feather meaning, completion assessment, decisions, open items, current position, blockers, next gates, protected-data handling, Lesson Harvest, expected lifecycle record inventory, selected route, fallback routes, and permitted approval modes.

Approval binds the exact Preview digest and one permanence mode. Any changed semantic field, scope, Lesson Harvest, record plan, protected boundary, or permanence mode invalidates approval and requires a new Preview. A prior instruction, campaign authority, Goddess Mode, Shardblade authority, model confidence, or passing check cannot approve a Preview that has not been shown.

## Save-first carrier and resumable states

After exact approval, the engine creates a route-neutral approved Sunset carrier before lifecycle candidate construction. The carrier is temporary execution evidence, not canonical lifecycle source and not Sunset completion. It binds the Preview, approval, semantic payload, source lock, selected route, fallback routes, and current resumable state.

Permitted states are:

- `PREVIEWED`;
- `APPROVED`;
- `APPROVED_PENDING_COMPILATION`;
- `APPROVED_PENDING_PUBLICATION`;
- `APPROVED_PENDING_VALIDATION`;
- `APPROVED_PENDING_PERMANENCE`;
- `BLOCKED_RESUMABLE`;
- `READBACK_COMPLETE`;
- `SUPERSEDED_BY_NEW_PREVIEW`.

A blocked connector, publisher, network path, or operator surface preserves the same carrier and transaction identity. Athena, Harmony, or Jayson PowerShell may resume it only after read-only reconciliation. Route failure never authorizes a replacement Sunset, duplicate branch, duplicate PR, fabricated fingerprint, or narrative completion claim.

Only `READBACK_COMPLETE`, proven from merged canonical source and independent readback, may be reported as `SUNSET COMPLETE`.

### Bounded Sunset invocation

The canonical Level 1 commands are:

```text
python -B -m tools.atlas_lifecycle sunset preview --request REQUEST --selected-route ROUTE --fallback-route ROUTE --output-dir NEW_SYSTEM_TEMP_DIR
python -B -m tools.atlas_lifecycle sunset approve --preview-dir PREVIEW_DIR --approval-mode STANDARD|GODDESS_MODE|GODDESS_MODE_SHARDBLADE --output-dir NEW_SYSTEM_TEMP_DIR
python -B -m tools.atlas_lifecycle sunset candidate --request APPROVAL_DIR/sunset-request-v3.json --preview-dir PREVIEW_DIR --approval-dir APPROVAL_DIR --output-dir NEW_SYSTEM_TEMP_DIR
python -B -m tools.atlas_lifecycle sunset verify --candidate-dir SYSTEM_TEMP_DIR
```

One approved invocation emits one exact, read-back-verified candidate set containing exactly one new sealed Feather, exactly one Sunset bound to that Feather, and exactly one Sunrise bound to the same pair. Admitted-Quest scope additionally emits exactly one replacement payload for the existing living Quest Emberline and one new Quest checkpoint. The Emberline replacement keeps the same stable ID, appends one Main-Gate journey entry, increments the Quest revision, and binds the prior file digest. Non-Quest scope emits neither and must not invent a Quest identity.

The Preview, approval, carrier, and v3 request are canonical JSON temporary artifacts. Their exact digests are cross-bound. Candidate construction rejects before output when any artifact is missing, malformed, noncanonical, tampered, stale, semantically changed, or inconsistent with its approval mode.

The request binds the exact canonical `main` SHA used as transaction input. Once accepted, `expected_main_sha` remains immutable historical evidence. Current integrity remains enforced through parent-Feather resolution, Quest revision, source fingerprint, replay protection, exact relationships, receipts, and the separately authorized merge gate.

All construction commands write only beneath the system temporary directory. They never write canonical source, invoke GitHub, mark a pull request ready, or merge. A separately authorized Level 1C route may publish verified record bytes into one immutable draft source PR.

## Lesson Harvest routing

Every full Sunset includes one explicit Lesson Harvest. Every observation has exactly one disposition:

- `LOCAL_ONLY` remains Feather evidence;
- `REINFORCES_EXISTING` resolves one existing Golden Wing reference;
- `NEW_CANDIDATE` creates a visible pending Golden Wing follow-up;
- `SYSTEMIC_EXCEPTION_CANDIDATE` creates an expedited pending Golden Wing review;
- `ABSORPTION_REQUIRED` creates a pending doctrine or assurance-control repair;
- `REJECTED` remains preserved with rationale.

A Feather, observation, pending action, Golden Wing candidate, passing CI, or Strikeforce GREEN never self-promotes. Golden Wing creation and assurance absorption remain separate reviewed source transactions. Sunrise links only Golden Wing IDs that already resolve in the approved Lesson Harvest; unresolved follow-up obligations remain explicit blockers or open items.

## Plan, route, apply, verify

All operations follow `Plan → Route → Apply → Verify`.

- Plan is read-only and declares expected state and output.
- Route checks the approved Prime change route and protected boundary.
- Apply writes only temporary output unless Level 1C is separately active.
- Verify rereads every output, checks canonical bytes and identity, binds an independent receipt, and reports exact stale or mismatch diagnostics.

Canonical source is never silently mutated. Level 1C may write only to an authorized branch, only within exact allowed paths, and may open only a draft PR. READY and merge remain separate gates.

## Protected source

Lifecycle source rejects secrets, credentials, private keys, seed phrases, real environment values, IP addresses or network topology, private runtime registers, raw financial evidence, account records, PHI, medical records, unrestricted private paths, and raw private exports. A protected source is represented only by a sanitized summary, classification, and bounded `protected://` pointer.

## Projections

`generated/lifecycle/` may contain deterministic website-facing indexes. Each projection declares noncanonical authority, schema and generator versions, source fingerprint, and generated timestamp. The timestamp is derived from the locked lifecycle Git tree revision, never the generator's wall clock, so repeated builds are byte-identical even in a shallow checkout. Consumers use stable IDs and relationships, never physical source paths as identity. Stale fingerprints are an error. The initial website contract is read-only.

Website index v2 carries compact restart and relationship fields while preserving stable IDs as identity. During Level 1A, `index build` computes and validates this projection only in memory and reports `CURRENT`, `STALE`, `MISSING`, or `INVALID`; it never publishes or rewrites generated source.

## Acceptance

No Sunset route is accepted until tests prove Preview-only invocation, exact approval binding, carrier creation before compilation, changed-scope and changed-lesson rejection, exact Feather/Sunset/Sunrise cardinality, admitted Quest Emberline/checkpoint behavior, non-Quest identity safety, route-resume identity, stale concurrency, tamper rejection, lesson follow-up visibility, canonical completion readback, Linux/Windows parity, and clean-context reconstruction.

The BEU pilot records trusted measurements only. BEU or model usage is reported only when a trusted native measurement exists; otherwise it is `NOT_MEASURED`.
