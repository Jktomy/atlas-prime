---
title: "Repairing Prime RP-C08 Capability Reconciliation R01"
atlas_id: "prime.proof.repairing-prime.rp-c08-capability-reconciliation-r01"
status: "ACCEPTED_PARTIAL_CLOSEOUT"
source_type: "PROOF"
authority_class: "CANONICAL_AUTHORED_SOURCE"
owner_project: "Project Codex"
owner_operation: "Operation Source Governance"
protected_level: "MEDIUM"
---

# RP-C08 capability reconciliation

All 28 frozen capability identities now have an evidence-driven current
disposition. This transaction accepts nine deferred restorations, preserves two
already accepted generated restorations, and keeps four exact capabilities
missing. It does not close RP-C08 or Repairing Prime.

## Restored from accepted RP-C05 evidence

CAP-002, CAP-003, CAP-004, CAP-005, CAP-006, CAP-008, CAP-022, and CAP-023 are
`RESTORED` and `ACTIVE`. RP-C05 accepted the continuity foundation, bounded
one-entry update, schema-driven later-Quest admission, command/startup surface,
deterministic Emberline and Argus, and fresh-clone Sunset/Sunrise
reconstruction. Its proof explicitly deferred these ledger promotions to this
evidence-driven reconciliation.

The exact accepted transaction anchors are:

- foundation PR `#117`, head `1f516c316ab5eefa8385045caef3a115f084423d`, merge `b39b0f7af1c5b136874739c90690814c4b61f7d4`;
- AJ-07 PR `#120`, head `f9dd9577b6dbc1531b93fd4aeeb627f6920b9147`, merge `7c0ab176aa081a2031d56cfee10a38e873cfd742`;
- AJ-08 PR `#121`, head `bf2e80c111b92bfb226fda785f25b99b57f8802f`, merge `fc549741e41fdb9ae73f1d50dba270a3ae314d04`;
- command/startup PR `#122`, head `4f59df54621f0d1e3f6c3fdd24da9a6d09ea78ea`, merge `de436b2919ae5e191de539c5596ac009a6961340`;
- AJ-10 PR `#124`, head `40ac19e0251487ae578e18d09f4f1b359f490628`, merge `4de60f2a1e9b4069189a80a6bc68bfa2b2b69dd0`.

Every source PR passed exact-head Ubuntu and Windows CI and detached review as
bound by `proof/repairing-prime/rp-c05-continuity-evidence-r01.json`.

## Restored hosted intake

CAP-009 is `RESTORED` and `ACTIVE` from hosted R02 run `29218494916`, draft PR
`#114`, exact head `0b8ad61bfa6ca6986111cbcc7205f352d8077acc`, exact-head CI run
`29218544058`, detached GREEN review, and merge
`ef1d137947227fa84e850d5d37275199bbfc5d96`. This is functional
owner-authorized hosted intake through the singular Thread Engine. It does not
prove a guided issue-form experience or fresh Work/Athena origin; those remain
separate CAP-010 and CAP-015 gaps.

## Exact missing capabilities

- CAP-010 remains `STILL_MISSING`: the live hosted surface accepts raw
  workflow-dispatch carrier inputs, not a human-friendly guided Spear intake.
- CAP-011 remains `STILL_MISSING`: live PR `#114` changed one authored path.
  Plural-path compiler tests cannot promote a live multi-file capability. The
  smallest missing proof is one owner-hosted ordinary carrier with at least two
  authored paths, one immutable draft PR, exact path/blob/head readback,
  exact-head CI, detached review, and canonical readback.
- CAP-015 remains `STILL_MISSING`: one fresh Jayson-started Work/Athena origin
  receipt must bind context, event, carrier, mission, run, and PR.
- CAP-027 remains `STILL_MISSING`: AJ-01, AJ-03, AJ-11, and AJ-12 are still
  `UNPROVEN` under the canonical RP-C07 matrix.

## Final counts and boundary

```text
IMPROVED               7
PRESERVED              4
RESTORED              11
REPLACED               1
INTENTIONALLY_RETIRED  1
BLOCKED                0
STILL_MISSING          4
TOTAL                  28
```

No generated report, local-only test, implementation narration, or this proof
promotes the remaining four capabilities. RP-C08 remains `IN_PROGRESS`; Quest
completion, final-main AJ-11/AJ-12 evidence, permanence, and standing authority
remain unchanged.
