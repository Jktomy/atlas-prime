---
title: "RP-C08 CAP-015 Architecture Realignment R02"
atlas_id: "prime.proof.repairing-prime.cap015-architecture-realignment-r02"
status: "CANDIDATE_ACCEPTANCE_EVIDENCE"
source_type: "PROOF"
authority_class: "CANONICAL_AUTHORED_SOURCE"
owner_project: "Project Codex"
owner_operation: "Operation Source Governance"
protected_level: "HIGH"
---

# RP-C08 CAP-015 Architecture Realignment R02

## Mission

`RP-C08-CAP015-ARCHITECTURE-REALIGNMENT-R02`

Exact base: `f4af6cf91028883be6b842d8849e960c0e4664a0`

## Finding

CAP-015 was held missing by an incorrect architectural premise: that Athena required an independently attested fresh ChatGPT Work origin before she could invoke Thread Engine.

The accepted Atlas architecture does not require that wrapper. Jayson authorizes the bounded task through Preview and Execute in the active chat, and Athena reaches the singular Thread Engine through Spear.

The read-only fresh-origin construction is therefore retained as superseded historical evidence, not activated, deleted, or promoted into a route.

## Correct route identities

```text
Athena -> Spear -> Thread Engine
Athena -> exact Sword -> Phoenix Blade -> no Thread Engine
Athena -> Aegis Break -> any safe bounded equivalent route
Jayson / Artemis -> Arrow -> Bow -> Thread Engine
Jayson -> exact Sword -> Oathbringer -> no Thread Engine
```

- Spear is Athena's direct Thread Engine route.
- Phoenix Blade is Athena executing a Sword herself and mirrors what Oathbringer is to Jayson.
- Aegis Break owns safe route selection or construction, including direct GitHub-native work when appropriate.
- Bow and Arrow belong to Jayson and Artemis delegated delivery, not Athena.

## Accepted evidence

### Athena Spear

Harmless PR `#102` proves direct Spear delivery through the singular Prime Thread Engine at exact head `fa20c23c532f3c684862a028720fe9debd7db855`. Canonical readback after merge is `2ed53467a83569afea1d6c07e06d1d2ab52c75ff`.

`proof/prime-spear-arrow-bow-parity-r01.md` separately proves compiler and candidate equivalence between direct Spear and delegated Arrow/Bow without conflating route ownership.

### Phoenix Blade counterpart

`proof/oathbringer-production-acceptance-r01.md` proves the exact Sword BUILD, REPAIR, and EXECUTE operation set. The corrected Phoenix Blade identity applies that Sword contract when Athena is the executor; it does not convert direct repository work into Phoenix Blade and does not invoke Thread Engine.

### Generated post-merge Thread Engine route

Source PRs `#181` and `#182` prove that an authorized non-generated main push automatically invokes the generated-checkpoint publisher, validates the exact generated draft head on Ubuntu and Windows, treats zero delta as a successful read-only `NOOP`, fails partial delta closed, and never automatically readies or merges.

This generated lifecycle is separate from Athena's route ownership.

## Accepted transitions

```text
CAP-015
STILL_MISSING / MISSING
-> RESTORED / ACTIVE

AJ-01
UNPROVEN
-> PROVEN

RP-C01-M02
UNPROVEN
-> PROVEN
```

Corrected meanings:

- `CAP-015`: Athena can reach the singular Thread Engine through Spear from a Jayson-authorized chat task.
- `AJ-01`: Athena's direct Spear submission reaches Thread Engine and creates one harmless immutable draft PR.
- `RP-C01-M02`: Phoenix Blade is Athena executing an exact Sword herself, mirroring Jayson wielding Oathbringer, without Thread Engine.

## Counts

```text
PRESERVED                 4
IMPROVED                  7
RESTORED                 14
REPLACED                  1
INTENTIONALLY_RETIRED     1
BLOCKED                   0
STILL_MISSING             1
TOTAL                     28
```

The only still-missing capability is CAP-027.

## Preserved open boundaries

This reconciliation does not promote or complete:

- RP-C01-M06 protected execution;
- RP-C01-M07 or AJ-03 genuine non-owner rejection;
- CAP-027 complete acceptance layer;
- AJ-11 clean-clone recovery;
- AJ-12 exact-final-main Ubuntu/Windows validation;
- RP-C01;
- RP-C08;
- Repairing Prime.

It adds no external bridge, platform-attestation requirement, user-run Python or PowerShell prerequisite, second repository writer, automatic ready, automatic merge, standing authority, or permanence grant.

## Rollback

Before merge, close the draft PR. After merge, use a new reviewed revert PR. Never rewrite history or force-update the accepted candidate.

## Stop

Audited draft source PR with exact-head Ubuntu and Windows GREEN. No merge is included.
