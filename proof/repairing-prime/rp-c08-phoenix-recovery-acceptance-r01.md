---
title: "Repairing Prime Phoenix Recovery Acceptance R01"
atlas_id: "prime.proof.repairing-prime.rp-c08-phoenix-recovery-acceptance-r01"
status: "ACCEPTED_RECOVERY_GATE"
source_type: "PROOF"
authority_class: "CANONICAL_AUTHORED_SOURCE"
owner_project: "Project Phoenix"
owner_operation: "Operation Restore Runbook"
protected_level: "CRITICAL"
---

# RP-C08 Phoenix recovery acceptance R01

## Exact acceptance base

```text
canonical main:
797fb2a1add829ccc304086a56f6d223d130d90d
```

This reconciliation accepts the final source-only Phoenix recovery gate. It does
not complete RP-C08 or Repairing Prime, create a Sunset, change a capability or
acceptance-journey disposition, embed private evidence, ready or merge a pull
request, clean frozen candidates, or grant standing recovery authority.

## Bound evidence

```text
recovery mission:
RP-C08-PHOENIX-RECOVERY-FINAL-MAIN-CLEAN-CLONE-PROOF-R01

Oathbringer carrier SHA-256:
a1083ca9c5123b1bfa552602b008a45314cab847c50e143cc58d80275ed8fa75

Receipt Gemstone SHA-256:
9dc2726e30f6b3ff8748804e991feb1441a03dcd715212d9cf391203dbfc22e7

original private evidence ZIP SHA-256:
b4049ff69a9347ad7ca7ee2fd0712966c8a45888faba86df1d656127fc156103

sanitized detached audit envelope SHA-256:
a920e86fa22a548521e619bd1d77d267b39b617b221ee36c63d53b4dcc832617

mission SHA-256:
3dc5d82aa0bccf8f6bde2b897913ad5072fc823e88d2c58c6d78de2f4a8efb98

receipt self-hash:
7fc50f501ae4599081c62abcd7f126163247568c4140604c342f80f8b0d36b02

receipt file SHA-256:
1705807d142c361d61b039b5cca6f7eeebe3ba893e398c1d5a0e78ea8701fbab

receipt sidecar file SHA-256:
00667cdda52ec0012225326d3d9f4f31ac4215472c927d12d56b016db7fa79f7

original transcript SHA-256:
9f575cf72279097117c77a44197a99eab2eb5697537f65706d8c0837a49323f3

sanitized transcript SHA-256:
50c3209b71d8bbb7c5e59f57fa8b615e0d74f38a364e8e989fc9e90422740477
```

The original recovery ZIP remains protected external evidence. The sanitized
envelope is not embedded. Prime records only clean identities and accepted
findings.

## Accepted recovery result

The separately authorized Oathbringer recovery proof:

- verified the exact repository, remote, default branch, Receipt Gemstone, and
  canonical SHA;
- created one isolated, detached, symlink-free clean clone;
- inherited no hooks or worktrees;
- passed all 13 validation commands;
- regenerated all five projections byte-identically as `CURRENT/NONE`;
- verified Thread Engine as active, mission-scoped, non-standing, and
  self-change isolated;
- proved normal `Jktomy/atlas-codex` dependency false;
- preserved source rollback as a new reviewed Prime pull request;
- recorded every mutation field false; and
- read back unchanged remote main before and after execution.

The sanitized detached envelope then passed 22 independent integrity, binding,
privacy, parity, mutation, and limitation-preservation checks. Repeated live
readback resolved `main` to `797fb2a1add829ccc304086a56f6d223d130d90d` with zero canonical delta.

## Preserved evidence limitation

The original receipt was written with:

```text
current stage:
EVIDENCE_SEAL

last completed stage:
FINAL_READBACK

transcript endpoint:
STAGE_ENTER EVIDENCE_SEAL
```

The original ZIP does not self-contain `STAGE_COMPLETE EVIDENCE_SEAL` or the
later `STOP_BOUNDARY` stage. This record preserves that limitation. It does not
rewrite the receipt or invent transcript lines. Acceptance rests on the proven
recovery substance, the GREEN sanitized detached audit, the observed
Oathbringer stop result, and repeated unchanged canonical-main readback.

## Transition

```text
PHOENIX RECOVERY:
PENDING -> PROVEN / ACCEPTED

RP-C08:
IN_PROGRESS -> IN_PROGRESS

Repairing Prime:
IN_PROGRESS -> IN_PROGRESS

next gate:
RESTART-SAFE SUNSET
```

AJ-01 through AJ-12 remain PROVEN. CAP-027 remains RESTORED/ACTIVE. Capability
counts remain 4 PRESERVED, 7 IMPROVED, 15 RESTORED, 1 REPLACED,
1 INTENTIONALLY_RETIRED, 0 BLOCKED, and 0 STILL_MISSING.

## Stop boundary

This acceptance grants no recovery rerun, private-runtime restoration,
destructive canary, branch cleanup, ready transition, merge, Sunset, Quest
completion, or reusable execution authority.

The next safe gate is a separately authorized restart-safe Sunset.
