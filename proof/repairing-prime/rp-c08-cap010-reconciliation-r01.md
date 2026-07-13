# RP-C08 CAP-010 reconciliation R01

CAP-010 is `RESTORED / ACTIVE`. Repairing Prime, RP-C01, and RP-C08 remain
`IN_PROGRESS`.

## Accepted guided journey

The guided publisher construction landed through PR `#150` at merge
`f30c682e711cd3b92ffb5252734a48813fd5b493`. Its exact head
`b343e92a6919c66bc7a258056037ae0bb1e0ac2b` passed CI run `29231674388`
on Windows job `86757074617` and Ubuntu job `86757074621`, plus detached GREEN
review. The accepted 32-test Athena route suite covers exact Preview
confirmation and drift, stale base, deterministic branch and replay checks,
owner and privacy gates, decoded mission-lock binding, new durable receipt-sink
reservation, ambiguous dispatch/readback, and preserved no-retry intent when
atomic receipt finalization fails. These executable rejections are component
evidence, not the missing live AJ-03 matrix.

Fresh mission `RP-C01-CAP010-GUIDED-LIVE-R01` then ran from exact canonical
base `f30c682e711cd3b92ffb5252734a48813fd5b493` with immutable carrier SHA-256
`86963fc061946a2dc074a765524277ddd25e26cd9da4888c49605fb1d124d350`.
Read-only Preview receipt
`d84fcf8c9e3633cceab56503a60f36e228519a4178276504f3526b8d98346084`
bound canonical mission digest
`09964cdbd06a5d6c4823fd0926a5f8082dd42fdc0a66875f6ef40e0dafdc5a30`
and decoded mission/base lock
`e7d5254f49cfd5790fc1b1de3566a2d16d96e9703f587da0879aa429d23aed5e`.
Execute receipt
`943118dccdf005354ed49855fbbff18a42318f9c222fff302a2b2a0f8e9fd97b`
recorded exact owner dispatch without branch, PR, adapter, ready, or merge
authority in the local publisher.

Hosted run `29231950571` passed read-only preflight job `86757943098` and
singular Thread Engine invocation job `86757981074`. Route artifact
`8271869325` has GitHub SHA-256
`8805942fbafa03df4ea9eb2c1fac91901f05cc260378b87b927f1d3bfcfa217a`;
its request and SUCCESS/DRAFT_PR_READBACK receipt hash to
`d07221a8266b89f5e6c3e230ce62970c916b45139eab9267f1cd937dfc7861aa`
and `e77a17196ec81068d82639c8877a44b474f8ca999cc3a6039f39b81a784a0a7c`.
The route itself created draft PR `#151` on deterministic branch
`source/athena-bow-e7d5254f49cfd5790fc1` at exact head
`337d86615594b6c8b07cd474b8d23ddc032b2c42` and stopped at exact readback.

PR `#151` contained one commit, exact base parent, and exactly one ordinary
authored path. The 519-byte GitHub blob rehashed to
`5c43f21878d192e76a57485495a135c4b14bf2e2e2424b235d2072c3ee39cc0c`,
identical to the carrier payload. Exact-head CI run `29232042665` passed Ubuntu
job `86758220665` and Windows job `86758220673`; detached review was GREEN.
The proof merged as `93f19b44b830c05bf9ec57356da66af4ac4a444c`, canonical readback was
exact, and the hosted branch is absent.

## Boundary

This proof restores only the human-friendly guided Spear intake capability.
It does not establish fresh Work/Athena origin, the remaining live AJ-03
rejections, protected execution, final-main recovery or validation, Quest
completion, permanence, standing authority, or any second repository writer.

The current 28-record counts are 13 RESTORED, 7 IMPROVED, 4 PRESERVED,
1 REPLACED, 1 INTENTIONALLY_RETIRED, 0 BLOCKED, and 2 STILL_MISSING:
CAP-015 and CAP-027.
