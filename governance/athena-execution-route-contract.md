---
title: "Spear and Arrow/Bow Delivery Contract"
atlas_id: "prime.governance.athena-execution-routes"
status: "CANONICAL_ACTIVE"
source_type: "PROTOCOL"
authority_class: "CANONICAL_AUTHORED_SOURCE"
owner_project: "Project Codex"
owner_operation: "Operation Source Governance"
protected_level: "CRITICAL"
routes_from:
  - "governance/athena-route-architecture-r01.md"
---

# Spear and Arrow/Bow Delivery Contract

This contract governs the two delivery routes into the same singular Prime
Thread Engine while preserving operator identity.

```text
SPEAR_DIRECT
  -> Jayson-authorized Athena task
  -> exact Spear Weave and carrier audit
  -> existing Spear compiler
  -> singular Prime Thread Engine production adapter
  -> immutable branch and one draft PR
  -> exact readback
  -> stop

ARROW_BOW_HOSTED
  -> Jayson-authorized immutable Arrow
  -> Artemis Bow hosted identity, replay, and carrier validation
  -> the same Spear compiler
  -> the same singular Prime Thread Engine production adapter
  -> immutable branch and one draft PR
  -> exact readback
  -> stop
```

Spear belongs to Athena. Arrow/Bow belongs to Jayson and Artemis. Byte-equivalent
mission output never merges those operator or route identities.

Jayson's explicit in-chat authorization is sufficient human authority for the
exact Preview or mission. No platform-origin attestation or external bridge is
required. Hosted Arrow/Bow must still obtain actor, triggering actor, workflow,
workflow-source SHA, run, attempt, credential principal, and token-mode identity
from GitHub and must reject inconsistent identity before mutation.

Machine-stable invariants:

```text
THREAD_ENGINE_SELF_CHANGE_ROUTE=AEGIS_BREAK_TO_INDEPENDENT_METHOD
NORMAL_STOP_BOUNDARY=DRAFT_PR_READBACK
COMPONENT_EVIDENCE_CANNOT_ASSERT_ROUTE_GATE
ROLLBACK_PRE_MERGE=CLOSE_DRAFT_PR
ROLLBACK_POST_MERGE=REVIEWED_REVERT_PR
```

The hosted request and receipt schemas remain closed. `SUCCESS` requires compiler
and adapter receipts plus a new immutable branch, draft PR, and exact head.
`REJECTED` and `BLOCKED` require no mutation. `PARTIAL` preserves every observed
remote identity, stops retry, and requires preserve-and-review.

Replay, stale base, edited input, malformed carrier, unsafe paths, protected
route mismatch, generated/source mixing, duplicate branch or PR, private
material, or any request for direct main, force push, ready, merge, cleanup,
settings, standing authority, or a second writer rejects before write authority.

Only a locally pre-screened, public-clean, size-bounded carrier may cross into a
hosted event. Logs, summaries, comments, artifacts, and receipts never echo
carrier bytes or protected content.

The owner-guided free-form and Preview/Execute components remain bounded
Arrow/Bow preparation and recovery tools. The carrier travels to the hosted
workflow as JSON on standard input, not as a command-line argument. Their
construction does not self-promote CAP-009, CAP-010, CAP-011, or a Quest gate;
accepted live evidence and separate reconciliation remain controlling.

Direct Spear and hosted Arrow/Bow both preserve the draft-PR stop, exact readback,
no-retry partial-state rules, one normal engine, and separate Jayson permanence
authority.
