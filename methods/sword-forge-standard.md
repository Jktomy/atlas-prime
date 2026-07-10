---
title: "Sword Forge Standard — Prime"
atlas_id: "prime.method.sword-forge-standard"
status: "CANONICAL_ACTIVE"
source_type: "PROTOCOL"
authority_class: "CANONICAL_AUTHORED_SOURCE"
owner_project: "Project Codex"
owner_operation: "Operation Source Governance"
protected_level: "CRITICAL"
---

# Sword Forge Standard — Prime

**Standard identity:** `SWORD_FORGE_STANDARD_V1`

This is the mandatory construction contract for every Build, Repair, Recovery, or Execute Sword. A user request for a Sword routes here automatically; no separate preflight phrase or command is required.

## Power and containment

A Sword may carry arbitrary authorized multi-file `ADD`, `REPLACE`, `DELETE`, `RENAME`, and `MOVE` operations across any clean-text Atlas path. File count, directory count, protected-path classification, and cross-subsystem scope are not construction vetoes.

The containment boundary is the exact branch and pull request. Protected paths raise audit attention and proof requirements; they do not prevent reversible candidate construction. There is no standing Sword authority, direct-main write, force push, silent scope expansion, or automatic merge.

## Required read set

Before forging, Athena must read and bind:

1. the current canonical Prime source and exact live repository state;
2. `methods/atlas-sword.md`;
3. `tools/atlas-sword/README.md`;
4. `methods/sword-lessons.json`;
5. the exact target repository, base, branch, pull request, and current head when applicable;
6. the mission-specific authority, payload source, tests, workflow contract, stop boundary, and rollback.

Chat memory, predecessor doctrine, generated reports, and old Sword packages may supply evidence but never replace current Prime source or live GitHub readback.

## Forge sequence

1. **Classify the Sword.** Select exactly one primary mode: `BUILD`, `REPAIR`, `RECOVERY`, or `EXECUTE`.
2. **Bind authority and identity.** Record authorizer, operator, repository, base, target branch or pull request, expected head, allowed operation classes, protected boundary, proof, stop condition, rollback, and next safe action.
3. **Resolve the complete operation inventory.** Every final path and operation must be declared. The Sword carries complete candidate bytes for additions and replacements rather than relying on Athena to reinterpret intent during execution.
4. **Apply the lessons register.** Every controlling lesson whose trigger matches the mission is recorded as `APPLIED`. A lesson may be `NOT_APPLICABLE` only with a mission-specific reason. `UNKNOWN`, missing classification, or an applicable noncontrolling lesson blocks the forge until resolved.
5. **Construct the sealed carrier.** The carrier contains the mission manifest, authority capsule, source and target locks, complete payload, operation inventory, hashes, thin PowerShell launcher, deterministic engine or transport library, test contract, workflow applicability map, recovery contract, receipt schema, and `SHA256SUMS.txt`.
6. **Preserve the Oathbringer experience.** PowerShell is the thin interactive client. It displays mission identity, stage, plan-position percentage, current GitHub operation, workflow applicability, failure or interruption state, stop boundary, and receipt location. It does not author or locally compose Atlas source.
7. **Validate before delivery.** Verify carrier integrity, internal hashes, source locks, complete path set, operation legality, launcher parsing, package-relative path resolution, structured-output parsing, receipt hashing, workflow classification, and stop behavior.
8. **Strikeforce the forged candidate.** Review the carrier against current doctrine, applicable lessons, live target state, and its declared stop boundary. Findings are repaired in the carrier before delivery.
9. **Deliver one bounded operator experience.** Provide one immutable ZIP, its carrier SHA-256, and one exact current-directory-independent PowerShell command. Package delivery grants no authority beyond the approved mission.

## GitHub-native baseline

The preferred production transaction is GitHub-native blob, tree, commit, ref, and pull-request construction. The Sword already contains Athena's complete intended bytes. Oathbringer transports those sealed operations, reads back GitHub truth, monitors applicable checks, and writes receipts.

Fresh Clone First remains an emergency or compatibility substrate. When used, clone-specific lessons and controls become applicable; clone use does not change the mission authority or permit local reinterpretation of the payload.

## Required carrier records

Every forged Sword records at minimum:

- `forge_standard = SWORD_FORGE_STANDARD_V1`;
- the lessons-register schema version and source blob identity;
- all `APPLIED` lesson IDs;
- every `NOT_APPLICABLE` lesson ID with its reason;
- repository, base, branch or pull request, and exact head locks;
- the complete final operation inventory;
- payload and carrier hashes;
- test and workflow applicability contracts;
- Build/Repair/Recovery/Execute stop boundary;
- failure, interruption, recovery, and final receipt behavior.

## Learning loop

Strikeforce findings do not silently rewrite this standard or promote themselves into controlling lessons.

The lesson lifecycle is:

```text
OBSERVED -> CORROBORATED -> VERIFIED -> ABSORBED
                                  \-> SUPERSEDED
```

Only `VERIFIED` and `ABSORBED` lessons control future forging. A reusable mechanical lesson belongs in `methods/sword-lessons.json`. A fundamental process change requires a bounded source pull request updating this standard. One-off mission findings remain in the mission receipt or evidence.

## Stop rules

The forge does not stop merely because the mission is large, multi-file, cross-directory, or touches protected clean-text source. It stops only when the exact mission cannot be proven or safely contained, including unresolved authority, secret or protected-private material, irreconcilable live-state drift, unknown applicable lessons, corrupt payload or hashes, unavailable required GitHub capability, or inability to prove the resulting candidate.

The Forge Standard constructs the Sword. It does not itself execute, mark ready, or merge the resulting mission.