---
title: "Resonance Provider-Neutral Reconciliation Contract"
atlas_id: "prime.governance.resonance-reconciliation-contract"
status: "CANONICAL_ACTIVE"
source_type: "PROTOCOL"
authority_class: "CANONICAL_AUTHORED_SOURCE"
owner_project: "Project Codex"
owner_operation: "Operation Source Governance"
protected_level: "CRITICAL"
---

# Resonance provider-neutral reconciliation contract

RP-C04 defines Refract, sealed independent findings, the Aberration Register,
and Athena Refraction without activating a provider or claiming local runtime.

## Refract

Refract gives multiple warranted lanes the same content-addressed input. Each
lane has a distinct agent and lane identity and must seal its finding before it
can see another lane's output. Refract does not ask providers to vote, share a
conversation, converge early, or infer authority from a model name.

Every finding binds the exact input, semantic claim key, statement, evidence,
confidence, agent/provider/model/Stormlight identity, warrant, independence
posture, and seal time. A sealed finding is a candidate, never doctrine.

## Aberration Register

The Aberration Register preserves every finding and digest, groups only by the
declared semantic claim key, and records one of:

- `CONSENSUS`: at least two independent lanes have the same normalized statement;
- `CONFLICT`: independent lanes disagree about one claim key;
- `NOVEL`: only one independent lane reported the claim.

Provider count, model identity, confidence, eloquence, and majority do not
decide truth. Conflicts are not averaged away. Missing evidence, input drift,
lane, agent, or warrant reuse, prior-lane visibility, duplicate identity, or
unproved LOCAL or HYBRID model execution fails closed.

## Athena Refraction

Athena Refraction reads only sealed findings and produces a provenance-preserving
recommendation. Athena may recommend review, conflict investigation, or a
second lane. Athena cannot rewrite the sealed statements, create a missing
finding, cast an extra vote, decide the human disposition, activate a provider,
or promote a capability or AJ.

Every record remains `OPEN_HUMAN_REVIEW` with a null human decision. A later
decision requires separately authorized evidence and permanence boundaries.

## Runtime and gate truth

The committed fixtures are provider-neutral test evidence with Stormlight
`NONE`; they are not model output. Local-model work remains
`BLOCKED_RUNTIME_PROOF_ABSENT`, contributes no finding, and cannot be relabeled
as CLOUD or fixture execution.

The committed deterministic projection is
`proof/repairing-prime/rp-c04-aberration-register-r01.json`. It remains an open
human-review register, not an accepted-finding ledger.

`RESONANCE_EVIDENCE_RECONCILED` proves the contract, closed schemas,
deterministic fixture reconciliation, and truthful blocker. It does not prove a
provider run, local runtime, accepted finding, provider superiority, capability
promotion, or AJ advancement.
