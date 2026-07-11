---
title: "G3-D Compact Context Usage-Reduction Pilot R01"
atlas_id: "prime.proof.lifecycle.g3-d-context-pilot-r01"
status: "VERIFIED_LOCAL_CANDIDATE"
source_type: "PROOF"
authority_class: "EVIDENCE_ONLY"
owner_project: "Atlas"
owner_operation: "Source Governance"
protected_level: "MEDIUM"
---

# G3-D Compact Context Usage-Reduction Pilot R01

The reproducible pilot compares one clean-context reconstruction performed from
three harmless lifecycle fixture files with the compact deterministic context
returned by `tools.atlas_lifecycle`.

## Measured result

| Measure | Manual baseline | Script-assisted | Change |
|---|---:|---:|---:|
| Model-visible files | 3 | 1 | 66.67% fewer |
| Model-visible bytes | 4,368 | 622 | 85.76% fewer |
| Explicit reconstruction steps | 6 | 1 | 83.33% fewer |
| Reconstruction fields exact | 8 / 8 | 8 / 8 | 100% accuracy |
| Retries | 0 | 0 | no increase |
| Errors | 0 | 0 | no increase |

The compact result SHA-256 is
`85eb3eabcbde94ca5229daf394905c12c2ecdf6c046744af842eecabc1a06e9b`.
One protected-value trial was attempted and rejected.

Local machine execution medians across 500 repetitions were 4,600 ns for the
direct in-memory baseline and 10,400 ns for the compact resolver. These numbers
measure local function execution only; they are not agent elapsed work and do
not establish runtime speed improvement. The supported claim is reduced
model-visible input and fewer reconstruction steps with exact output.

## Truthful limits

BEU, model usage, elapsed agent work, real-workflow human interventions, and
manual semantic privacy review were not available from a trusted native meter
and are recorded as `NOT_MEASURED`. The Python package made no hidden model
call. Structural protected-data rejection is defense in depth, not proof of
semantic privacy interpretation.

The machine-readable receipt is
`proof/lifecycle/g3-d-beu-reduction-pilot-r01.json`. CI reruns the semantic
comparison on Linux and Windows while excluding only variable machine timing
from byte-for-byte evidence comparison.
