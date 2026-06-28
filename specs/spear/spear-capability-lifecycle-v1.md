---
title: Athena's Spear Capability Lifecycle v1
atlas_id: spear.capability-lifecycle.v1
format_version: "1.0"
status: PROPOSED
source_type: SPECIFICATION
authority_class: TOOL_CONTRACT
owner_project: Codex
owner_operation: Athena's Spear
canonical_scope: Defines the permanent lifecycle for proposing, implementing, proving, activating, operating, deprecating, and retiring Athena's Spear capabilities and route profiles, including the Artemis's Bow and Arrow execution handoff and Emberline status relationship, without granting writer authority.
protected_level: CRITICAL
routes_from:
  - athenas-spear.md
  - migration/atlas-codex/atlas-prime-rebuild-program-roadmap-v1.md
  - policies/destination/atlas-prime-destination-policy-v0.2.yaml
routes_to:
  - schemas/spear/spear-packet-v1.schema.json
  - policies/operations/spear/spear-policy-v1.yaml
  - tools/spear/operator-runbook.md
  - tools/spear/recovery-runbook.md
  - migration/atlas-codex/atlas-prime-rebuild-program-roadmap-v1.md
private_boundary: This specification may contain clean capability names, route rules, limits, tests, recovery requirements, and public repository identities only. It must not contain credentials, tokens, secrets, PHI, raw finance or account evidence, private runtime values, network maps, device registers, real environment values, or protected exports.
evidence_boundary: Capability source, implementation, tests, receipts, proof packets, pull requests, Noctua reports, activation records, and runtime observations remain distinct evidence. This specification defines required lifecycle gates but is not evidence that any gate passed.
supersedes: []
cleanup_path: Retain as the initial permanent Spear capability-lifecycle contract. Supersede only through a separately reviewed Spear protocol or engine PR with compatibility, rollback, and migration treatment for every active profile.
last_verified: 2026-06-28
---

# Athena's Spear Capability Lifecycle v1

## 1. Status and non-authority

Status: PROPOSED tool contract.

This specification does not activate S1, authorize a repository write, broaden a route, execute a packet, create a branch or PR, authorize merge, promote Atlas Prime, retire Atlas Codex, or perform cutover.

## 2. Permanent architecture

Athena's Spear is a permanent controlled source-change platform composed of:

1. a stable deny-by-default safety kernel;
2. versioned capabilities;
3. versioned route profiles;
4. exact bounded packets;
5. Artemis's Bow and Arrow as a separately authorized execution handoff when local packaging is selected;
6. independent Noctua and human merge gates.

The migration campaign may end. The platform and its safety obligations continue.

### 2.1 Safety kernel

The kernel owns:

- strict packet parsing and duplicate-key rejection;
- pinned schema, policy, and contract identity;
- target repository, base branch, and base commit verification;
- expected absence or exact current blob verification;
- path normalization and collision rejection;
- protected-content checks and redacted diagnostics;
- deterministic proposed trees and receipts;
- exact changed-file, stage, commit, push, and draft-PR boundaries when writer authority is separately active;
- no direct `main` write, force-push, or automatic merge;
- replay, partial-failure, abandonment, and recovery controls;
- stop-before-merge and merged-main readback requirements.

Kernel changes are protected engine work and must not occur through an ordinary Spear packet.

### 2.2 Capability

A capability is one versioned operation family with explicit input, output, safety, test, and recovery contracts. Examples may include:

- file creation;
- complete file replacement;
- bounded surgical Markdown mutation;
- append beneath a unique semantic anchor;
- multi-file atomic source transaction;
- migration-evidence transaction;
- structured JSON or JSONL register transition;
- deterministic generator execution;
- lifecycle or archive transaction;
- lineage and closure-record generation.

A named capability is not authority to use it.

### 2.3 Route profile

A route profile binds capabilities to a recurring source class and defines:

- profile ID and version;
- repository and allowed path classes;
- authority and source classes;
- allowed operation versions;
- file-count, byte, and complexity limits;
- expected-state rules;
- atomicity and partial-state behavior;
- required tests and fixtures;
- recovery and abandonment rules;
- Noctua acceptance criteria;
- activation state and permitted actor;
- explicit prohibitions.

One difficult packet must not silently broaden a global profile.

### 2.4 Packet

A packet is an exact instance of an already-defined route. It must not carry executable policy, select arbitrary code, weaken safeguards, invent capabilities, or grant itself authority.


### 2.5 Artemis's Bow and Arrow execution handoff

The Bow and Arrow model is not a capability state and does not grant authority. It is the user-facing handoff for firing one exact approved package.

- The Bow is a stable thin launcher.
- Stage 1 is an immutable Build and Verify payload that stops before merge.
- Stage 3 is a separately approved Merge and Readback payload bound to the exact audited Stage 1 result.
- Stage 1 and Stage 3 must have different Arrow IDs, manifests, hashes, receipts, and approval records.
- A capability may be implemented without being eligible for either Arrow stage.
- Stage 3 must never be generated merely because Stage 1 succeeded.

Every capability record used by an Arrow must declare which stages, if any, are permitted and what recovery evidence each stage requires.

### 2.6 Emberline status relationship

Emberline reports the complete Quest/Campaign road and current gate. It may identify a capability need or route dependency, but it does not promote a capability or activate a profile.

An Emberline completion estimate must distinguish compiler support, fixture proof, operational activation, migration use, recovery proof, and closeout instead of treating implementation as completion.

## 3. Capability lifecycle states

Use these capability states:

```text
PROPOSED
-> READ_ONLY_COMPILER_SUPPORT
-> TESTED_IN_FIXTURES
-> PROOF_PACKET_ONLY
-> LIMITED_OPERATIONAL
-> FULLY_OPERATIONAL
-> DEPRECATED
-> RETIRED
```

### PROPOSED

The need, operation semantics, risks, route ownership, and recovery design are documented. No implementation or authority is implied.

### READ_ONLY_COMPILER_SUPPORT

The compiler can validate and deterministically plan the capability, but it cannot apply repository mutations.

### TESTED_IN_FIXTURES

Positive, negative, adversarial, stale-state, protected-boundary, replay, and recovery fixtures pass against the pinned implementation and contracts.

### PROOF_PACKET_ONLY

One exact harmless or bounded proof may execute after a separate Preview -> Execute approval. Authority is limited to that proof.

### LIMITED_OPERATIONAL

The capability may run only through named route profiles, path classes, limits, and actors supported by proof evidence.

### FULLY_OPERATIONAL

The capability is supported for every explicitly activated profile in its version. It remains deny-by-default outside those profiles.

### DEPRECATED

No new packets should use the capability except separately approved migration or recovery work. A replacement and compatibility path must be identified.

### RETIRED

Execution is denied. Historical contracts, receipts, and lineage are retained as required.

## 4. Capability record

Every capability version must declare:

- capability ID and semantic version;
- lifecycle state;
- owning Project and Operation;
- operation semantics and deterministic output;
- allowed and denied source types;
- packet schema fields;
- implementation and contract paths;
- positive, negative, adversarial, and recovery tests;
- expected-state and stale-state behavior;
- idempotency and replay rules;
- partial-failure and cleanup behavior;
- compatible route profiles;
- Noctua criteria;
- activation and emergency-disable records;
- predecessor, successor, deprecation, and retirement treatment.

## 5. Promotion gates

Promotion requires evidence for the next state only; later authority must not be inferred.

### Proposal to compiler support

Require complete semantics, schema treatment, policy treatment, deterministic output definition, protected-boundary review, and no hidden mutation.

### Compiler support to fixture-tested

Require implementation-to-contract fidelity and complete test coverage for malformed input, stale bases, target mismatch, unauthorized paths, prohibited content, path collisions, duplicate replay, partial failure, and recovery.

### Fixture-tested to proof-only

Require a harmless or tightly bounded target, exact Preview, explicit approval, one Stage 1 or equivalent bounded route, one branch, one commit unless otherwise approved, one draft PR, stop-before-merge, and packet-to-PR fidelity evidence. Any Stage 3 merge proof remains a separate gate.

### Proof-only to limited operational

Require separately approved Stage 3 or equivalent merge proof, successful merged-main readback, recovery evidence, documented limits, a versioned route profile, and explicit activation approval.

### Limited to fully operational

Require repeated clean use within the same profile family, no unresolved safety or recovery defects, current runbooks, and a separate activation decision.

### Deprecation and retirement

Require impact inventory, replacement or no-replacement rationale, active-packet handling, compatibility treatment, rollback plan, routing updates, and retained historical lineage.

## 6. Implementation is not activation

The following states must remain separately recorded:

```text
contract present
implementation present
fixtures passing
proof permitted
profile activated
operational authority active
```

A merge may advance implementation without advancing authority. Activation must identify the exact capability version, route profile version, repositories, path classes, actor, and limits.

## 7. Migration feedback loop

Evolving Prime may reveal recurring legitimate change patterns. The safe loop is:

```text
read-only reconciliation identifies a recurring need
-> capability and route proposal
-> compiler support
-> fixtures and adversarial tests
-> bounded proof
-> narrow activation
-> migration packet use
-> evidence-driven revision, broadening, deprecation, or retirement
```

Do not broaden Spear merely to make one unfit packet pass. Redesign the packet, split the source, or create a narrowly reusable route when that is safer.

## 8. Post-cutover maintenance

After Atlas Prime becomes canonical:

- Spear becomes the normal controlled source-change engine for Prime;
- the safety kernel remains protected and deny-by-default;
- ordinary source, structured systems, generators, and protected doctrine continue through different profiles;
- Noctua and Jayson remain separate merge gates;
- merged-main readback and retained lineage remain required;
- capability evolution continues through this lifecycle;
- Emberline remains the roadmap/status surface for substantial Spear campaigns;
- Bow/Arrow remains separately authorized whenever package-based local execution is used;
- no post-cutover status grants autonomous merge or unrestricted repository authority.

The Spear Campaign closes into maintenance only after required migration routes are proven, active profiles and denials are explicit, runbooks and recovery are current, and restart-safe closeout is durable.

## 9. Self-modification boundary

An ordinary packet must not modify Spear doctrine, schemas, policies, implementation, tests, workflows, authentication, activation records, or its own route profile.

Spear changes require:

1. complete current-source reads;
2. exact protected Preview;
3. a separate engine or protocol branch and PR;
4. implementation and fixture audit;
5. Noctua review;
6. Jayson merge decision;
7. merged-main readback;
8. proof and activation as separate later gates when authority changes.

## 10. Compatibility and versioning

- Packet, capability, and route-profile versions are explicit.
- A packet must bind to compatible versions at the verified base commit.
- Breaking semantics require a new major version.
- Existing active packets must not silently reinterpret under a newer contract.
- Deprecated versions remain readable for lineage and recovery until retirement criteria are met.
- Emergency disable may reduce authority immediately through an approved protected route; reactivation requires fresh evidence.

## 11. Noctua acceptance

Noctua verifies, at minimum:

- source order and approval basis;
- exact capability and route versions;
- contract-to-code fidelity;
- changed filenames and full diff;
- current repository and base state;
- protected boundaries and redacted diagnostics;
- test and proof evidence;
- packet-to-tree, tree-to-commit, and commit-to-PR fidelity;
- activation state and absence of hidden authority expansion;
- recovery, deprecation, and retirement completeness;
- Stage 1/Stage 3 separation and receipt fidelity when Bow/Arrow is used;
- merged-main readback when a merge occurs.

A Noctua `YES` means the reviewed gate may proceed through its required approval. It does not itself execute, merge, activate, promote, or cut over.

## One-Arrow lifecycle rule

A route profile may define multiple sealed stages inside one immutable Arrow. A stage cannot broaden authority, and later-stage permission is never inherited from an earlier-stage receipt.

The reusable Bow and engine are platform capabilities. The Arrow is a mission-bound package. Ordinary Arrows may not modify Bow, engine, policy, schema, or authority.
