---
title: "Lifecycle Architecture Decision R01"
atlas_id: "prime.lifecycle.architecture.r01"
status: "SUPERSEDED"
superseded_by: "prime.lifecycle.architecture.r02"
source_type: "ARCHITECTURE_DECISION"
authority_class: "CANONICAL_AUTHORED_SOURCE"
owner_project: "Atlas"
owner_operation: "Source Governance"
protected_level: "CRITICAL"
---

# Lifecycle Architecture Decision R01

This decision is preserved as the G3 foundation. Lifecycle Architecture
Decision R02 supersedes it for the shared receipt-driven event model without
erasing this history.

## Decision

Atlas lifecycle source uses strict UTF-8 JSON records and JSON Schema Draft
2020-12. This combination supports closed schemas, stable identifiers,
deterministic indexes, explicit relationships, revision locks, and future
website rendering without scraping prose or depending on repository folders.

The implementation is one modular Python package at `tools/atlas_lifecycle/`.
It is classified `SCRIPT ASSIST — LEVEL 1`; it contains no hidden model call and
does not author meaning, infer completion, advance a Quest, promote a Golden
Wing, write directly to `main`, run as a service, or hold standing GitHub
authority.

## Authority

1. Quest identity and admission remain explicit authored decisions.
2. After the atomic lifecycle authority cutover is proven, a current Quest
   Emberline is the sole current-state record for an admitted Quest.
3. Feathers and Quest checkpoints are immutable checkpoints, not competing
   state authorities.
4. Feather Archive and supersession records preserve the permanent Feather ID.
5. Golden Wings remain candidates linked many-to-many to Feathers, Quests,
   Projects, and Operations.
6. Sunset supports admitted-Quest, candidate-Quest, protected-domain, and
   non-Quest scopes without inventing identity.
7. Quest Board and website indexes become generated projections only after the
   Quest Emberline cutover is proven; no authority gap is permitted.
8. GitHub stores clean summaries and `protected://` pointers only.

## Stable identity and serialization

Canonical JSON is UTF-8, NFC normalized, sorted by Unicode code point, compact
(`,` and `:` separators), and terminated by one LF. Schema-declared integers are
allowed; floating-point numbers, duplicate object keys, NaN, and infinity are
forbidden in lifecycle records.

Each record ID is `<type-prefix>-<digest>`, where `digest` is the first 26
unpadded RFC 4648 Base32 characters of SHA-256 over the canonical record with
`record_id` omitted. Prefixes are `FTR`, `FAR`, `GWN`, `QEM`, `QCP`, `SUN`,
`SRI`, `CON`, and `LCR`. Corrections create a revision or supersession record;
a sealed record is never silently mutated.

## Concurrency and integrity

Every state-sensitive operation binds expected canonical `main`, expected
parent Feather, expected Quest revision, and declared source fingerprint where
applicable. Case-fold collisions, stale parents, stale revisions, duplicate
IDs, duplicate payloads, and receipt replay are rejected.

Evidence verification is bounded by trusted schema identity, input byte size,
member count, safe relative paths, parsing depth, and explicit contract.
Archives reject traversal, absolute paths, links, and special files. A receipt
must independently bind the sidecar digest and the verified subject digest;
self-consistent evidence alone is insufficient.

## Activation sequence

- Level 1A: read-only `validate`, `context`, `verify`, stale detection, and
  check-only index build.
- Level 1B: temporary candidate generation for Feathers, Sunset, Sunrise, and
  Golden Wings.
- Level 1C: branch-scoped apply only after 1A and 1B acceptance; exact mission,
  base, allowed paths, and approved route are mandatory; draft PR is the stop.

Code presence never activates a higher level. Activation requires a separate,
durable acceptance record and exact-head proof.

## Current doctrine reconciliation

Notum's Watch remains candidate-only for new lifecycle fixtures because no
current valid admission handoff is available in this mission. Existing lineage
is preserved for later schema-driven reconciliation. The current Quest Board
temporarily retains its present authority until Quest Emberlines and projection
generation are proven together. Generic Emberline remains an immutable preview
and decision package; a Quest Emberline is a non-executing structured subtype
whose authority is limited to current admitted-Quest state.

The future website is out of scope here. Only deterministic, read-only,
schema-validated projections are authorized.
