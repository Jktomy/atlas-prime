# Atlas Thread Engine

Prime carries a fixture engine and a separately bounded production adapter. The fixture engine remains disabled and fixture-only. The production adapter is proven and active only for exact mission-scoped draft-PR transactions. Its harmless pilot, replay rejection, rollback/disablement, direct Spear, and immutable Arrow/Bow proofs are merged.

Runtime posture:

```text
fixture_implementation_state: PILOT_DISABLED
fixture_runtime_mode: FIXTURE_ONLY
persistent_writer: ABSENT
production_adapter: THREAD_ENGINE_ACTIVE_MISSION_SCOPED
direct_spear_repository_path_scope: ALL_SAFE_DECLARED_PATHS
github_mutation: DISABLED
network_access: DISABLED
repository_checkout_mutation: DISABLED
workflow_authority: ABSENT
standing_authority: NO
```

The engine applies declared ADD and REPLACE fixture Threads inside a unique temporary sandbox. It validates removal contracts, but a successful fixture removal requires separate runtime authority and is not part of default Gate 7B tests.

The production adapter under `production_adapter/` is activated only as mission-scoped, draft-PR-only Thread Engine authority. PowerShell, CLI, and direct Python execution all read `PRIME-PORT-STATUS.json` and fail closed if the state is disabled, malformed, or violates a permanent invariant. The fixture core remains fixture-only.

The active adapter requires an exact mission authority, mission SHA-256 binding, explicit mission-scoped draft-PR intent, Fresh Clone First, declared paths, source locks, payload hashes, candidate-tree verification, final path-set verification, `git diff --check`, staged diff verification, a pre-push canonical-main recheck, one deterministic branch, one single-parent commit, one draft PR, and independent readback. It never activates persistent writer authority, standing automation, ready transition, merge, workflow dispatch, unprofiled generated-output mutation, repository-setting authority, cleanup, or production configuration.

## Universal direct-Spear repository paths

Direct Spear may author any safe repository-relative path in Prime. Governance, lifecycle, schemas, workflows, generated source, Quest source, recovery source, and `tools/thread-engine/**` are all valid declared targets in an exact Jayson-authorized Weave.

The Spear compiler validates safe syntax, uniqueness, source existence, payload identity, source blobs, and exact final state. The production adapter recognizes the compiler-bound mission shape and permits its declared path set without a separate path-class authority object.

This does not make repository location irrelevant to validation. Changes to Thread Engine, workflows, schemas, validation planning, policy, lifecycle, or generated contracts receive their applicable trusted-base and platform profiles. A candidate cannot reduce or select away the validation that applies to itself.

A Thread Engine self-change is constructed by the current canonical engine as one immutable draft candidate. The running engine is not altered. Review, exact-head CI, Strikeforce, separately authorized permanence, and merged-main readback remain outside the engine.

The protected-data boundary is unchanged. Secrets, credentials, private keys, real environment values, PHI, raw finance or legal evidence, IP addresses, private runtime state, and unredacted logs remain prohibited regardless of target path.

## Path-policy compatibility

`policies/protected-paths.json` and Aegis Break protected-route evidence remain historical and compatibility inputs for older raw missions and hosted launchers. They no longer define a repository-file authorship restriction for direct Spear.

Raw production missions that were not produced by the exact Spear compiler may continue to require their legacy route profile. Hosted Arrow/Bow launchers may retain narrower admission until separately reconciled. Neither compatibility boundary limits Athena's direct Spear path scope.

## Lifecycle Construction Profiles

G4-D1 adds the closed `LIFECYCLE_CHECKPOINT_V1` and `LIFECYCLE_TRANSITION_V1` profiles for exact lifecycle-event construction. A profile binds the semantic event ID, route-declared immutable path, target entity and revision locks, source fingerprint, candidate event/manifest/receipt/set digests, independent trust and state digests, replay key, lineage, protected-data class, and rollback and reversal contracts. Transition profiles additionally require an independent accepted-receipt digest.

The adapter accepts one lifecycle event below `lifecycle/events/`, verifies the exact three-file G4-C candidate set under `payload/lifecycle-candidate/`, rejects record-ID/replay-key reuse, missing parents, and a concurrently claimed entity revision, and then uses the existing one-branch, one-commit, draft-PR-only route. The physical event path never replaces `record_id` as identity.

The profile performs no semantic authorship, Quest advancement, acceptance decision, automatic ready, automatic merge, or direct-main write.

## Generated Checkpoint Profile

`GENERATED_CHECKPOINT_V1` is a separate closed profile for the exact five non-governing generated reports. It is mutually exclusive with lifecycle profiles. A read-only preparer builds canonical registers; hosted Ubuntu and Windows must produce byte-identical register artifacts; and the publish job reproduces those bytes from the exact workflow/base source.

The profile binds fresh mission and replay identities, its deterministic branch, source blobs, candidate and final path-set digests, source fingerprint, parity and reconciliation digests, workflow ref/source/blob, run and attempt, owner actors, repository token principal, and public-clean confirmation. The adapter re-reproduces the outputs from its fresh clone, rechecks canonical `main` immediately before push, permits only five ordered replacement operations, creates one draft PR, performs exact readback, emits sanitized evidence, and stops.

It cannot advance a Quest or capability, ready or merge a PR, retry automatically, change settings, or become a second writer.

## Historical Aegis Break protected route

The Aegis Break protected route remains accepted historical evidence and a compatibility profile for older exact missions. It is no longer required merely because a direct Spear Weave names governance, lifecycle, workflow, generated, Quest, or Thread Engine source.

When explicitly used by a legacy mission, the route still requires its exact authority ID, authenticated operator readback, declared path set, source blob map, operation-set SHA-256, candidate-tree SHA-256, final-pathset SHA-256, and draft-PR stop. It grants no direct-main, force-push, automatic ready, automatic merge, workflow dispatch, cleanup, or standing authority.

Codex's `WORKBOARD_ROW_UPDATE_V1` route is not inherited. Its CLI flags, mission schema, implementation, receipt fields, examples, and positive tests are absent in Prime. Prime Quest Board changes remain exact reviewed source work; direct Spear may author them but cannot promote a Quest by path access alone.

## Launcher

PowerShell 7 fixture audit:

```powershell
./Invoke-AtlasThreadEngine.ps1 -WeavePath ./examples/add-replace.example.json -FixtureOnly -AuditOnly
```

Python 3 fixture audit:

```text
python -B -m engine.thread_engine --weave examples/add-replace.example.json --fixture-only --audit-only
```

Both fixture routes fail closed unless fixture-only and audit-only intent are explicit.

Mission-scoped production adapter:

```powershell
./Invoke-AtlasThreadEngineProductionAdapter.ps1 -MissionPath ./mission.json -MissionSha256 <sha256> -MissionScopedDraftPr -ExecuteDraftPr
```

The production-adapter launcher fails closed unless mission-scoped and draft-PR-only intent are explicit.

Historical Aegis Break compatibility mission:

```powershell
./Invoke-AtlasThreadEngineProductionAdapter.ps1 -MissionPath ./mission.json -MissionSha256 <sha256> -MissionScopedDraftPr -ExecuteDraftPr -AegisBreakProtectedRoute -AegisBreakAuthorityId <authority-id>
```

The compatibility launcher fails closed unless the protected-route switch and exact authority ID are both supplied. Direct Spear does not require this switch for repository path access.
