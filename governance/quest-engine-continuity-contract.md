---
title: "Quest Engine and Prime Continuity Contract"
atlas_id: "prime.governance.quest-engine-continuity-contract"
status: "CANONICAL_ACTIVE"
source_type: "PROTOCOL"
authority_class: "CANONICAL_AUTHORED_SOURCE"
owner_project: "Project Codex"
owner_operation: "Operation Source Governance"
protected_level: "CRITICAL"
---

# Quest Engine and Prime continuity contract

The Quest Board remains the canonical Quest registry. Its closed schema admits
a Quest by data: add one schema-valid Quest source and one schema-valid unique
board entry. Validator code does not enumerate Quest paths or identities.

`continuity/quest-engine-identities-r01.json` fixes stable Repairing Prime Quest,
Campaign, Mission, and Gate identities plus closed state transitions. A merge,
generated output, or validation success cannot self-certify a state advance.

`continuity/prime-continuity-register-r01.json` is canonical operational
unfinished-work detail. It binds every non-complete Quest Board row and exact
Quest source digest. Its `source_base_sha` records the canonical main used to
author the register; it is evidence provenance, not a claim that later main
must remain byte-identical. The register supplements but never replaces or
silently advances the Quest Board.

## Bounded update

A continuity update binds the complete register digest, one continuity ID, one
entry revision, and one globally unique event ID retained in the register replay
ledger. Only operational position, blockers, next action, next approval, and
explicit Campaign/Mission/Gate routing fields may change; Quest state cannot be
promoted through this route. The input and candidate both validate against the
canonical Board and stable identity register. Exactly one entry, the register
revision, and the replay ledger advance. Planning is read-only; durable apply
still requires an exact branch, draft PR, exact-head review, merge, and
canonical readback.

## Emberline, Sunset, Sunrise, and Argus

The deterministic Emberline is a non-authoritative projection of the exact
register digest. Sunset seals one entry and its register digest. Sunrise accepts
the snapshot only when its register digest and entry exactly match the supplied
canonical register; a self-contained or recomputed digest is not authority. It
reconstructs only position, blockers, next gate, next action, next approval, and
source. Argus sorts unfinished work from the register without chat memory and
cannot mutate or promote it.

Generated projections report and never govern. Private data, provider state,
runtime placement, deployment, CAP promotion, AJ promotion, ready, and merge
authority are outside this contract.
