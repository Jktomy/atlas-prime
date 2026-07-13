---
title: "Repairing Prime RP-C06 Generated Parity Acceptance R01"
atlas_id: "prime.proof.repairing-prime.rp-c06-generated-parity-acceptance-r01"
status: "ACCEPTED_PARTIAL_CAMPAIGN"
source_type: "PROOF"
authority_class: "CANONICAL_AUTHORED_SOURCE"
owner_project: "Project Codex"
owner_operation: "Operation Source Governance"
protected_level: "HIGH"
---

# RP-C06 generated parity and AJ-09 acceptance

AJ-09 is proven from a fresh owner-triggered hosted journey. Run `29225849474`
at exact source and base `2bac4015df36838854fbf23994d9e7d2da094ebe`
produced byte-identical Ubuntu and Windows registers, reproduced the five
approved generated reports in a fresh clone, invoked only the singular Thread
Engine, and created draft PR `#138` at exact head
`5ef0bbe61ee575890c8a07ed79fd6ed7533f5298`.

The route receipt stopped at `DRAFT_PR_READBACK` and its complete PR readback
equaled live GitHub state: one bot-authored commit, exact base, exact immutable
branch, exactly five generated report changes, and no comments, reviews, Quest
promotion, capability promotion, ready transition, merge, setting mutation, or
standing authority. Exact-head validation run `29226002993` passed on Ubuntu and
Windows. Detached Shardblade review independently regenerated all five files
byte-for-byte and returned GREEN.

After human ready/merge, PR `#138` became canonical main
`2a8736c01cc7be00d307db7c8b4163d685405df6`; its carrier branch was absent and
the canonical generator readback was `CURRENT` at source fingerprint
`sha256:a9e108b3f748bf735068fb691bb4575b6f25ef116dd9bd5def5639b9fc57b9d9`.
CAP-019 and CAP-020 are therefore restored and active.

Replay run `29225994125` used the same accepted identity only as a rejection
probe. It stopped at `DUPLICATE_CHECK` with `BRANCH_EXISTS`, recorded
`mutation_observed: NO`, and left PR `#138` at its original one-commit head.
Fresh rejection-only run `29226140111` requested the superseded base
`2bac4015df36838854fbf23994d9e7d2da094ebe`; both read-only parity jobs passed,
but the credentialed publisher job was skipped because workflow/main was
`2a8736c01cc7be00d307db7c8b4163d685405df6`. No branch or PR was created.

RP-C06-M01 through M04, M06, and M07 are proven. RP-C06-M05 is `PARTIAL`: live
stale-base, replay, and branch-collision refusal are conserved, and the unit
contract covers PR collision, but a distinct-identity hosted PR-collision
rejection is still missing. The RP-C06 Campaign and gate remain in progress
until that smallest missing leg is proven in a later authored transaction.

Run `29225548513` is retained only as a superseded startup diagnostic. It did
not create a branch or PR and contributes no acceptance identity, carrier,
receipt, or partial success to this record.
