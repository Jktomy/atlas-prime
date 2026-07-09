# Atlas Thread Engine

Prime carries a fixture engine and a separately bounded production adapter. The fixture engine remains disabled and fixture-only. The production adapter is active only for exact mission-scoped draft-PR transactions; its harmless Prime-native pilot is the next proof gate.

Runtime posture:

```text
fixture_implementation_state: PILOT_DISABLED
fixture_runtime_mode: FIXTURE_ONLY
persistent_writer: ABSENT
production_adapter: THREAD_ENGINE_ACTIVE_MISSION_SCOPED
github_mutation: DISABLED
network_access: DISABLED
repository_checkout_mutation: DISABLED
workflow_authority: ABSENT
standing_authority: NO
```

The engine applies declared ADD and REPLACE fixture Threads inside a unique temporary sandbox. It validates DELETE contracts, but a successful fixture DELETE requires separate runtime authority and is not part of default Gate 7B tests.

Every rejection receipt is deterministic and classified with `result = REJECTED`, `error_code`, `error_stage`, `stop_point`, checkpoint results, completed Thread results, and forbidden-action confirmation.

The production adapter under `production_adapter/` is activated only as mission-scoped, draft-PR-only Thread Engine authority through Aegis Break → Oathbringer. PowerShell, CLI, and direct Python execution all read `PRIME-PORT-STATUS.json` and fail closed if the state is disabled, malformed, or violates a permanent invariant. The fixture core remains fixture-only. The active adapter requires an exact mission authority, mission SHA-256 binding, explicit mission-scoped draft-PR intent, Fresh Clone First, declared paths, protected-path enforcement, source locks, payload hashes, candidate-tree verification, final path-set verification, `git diff --check`, staged diff verification, one deterministic branch, one single-parent commit, one draft PR, and independent readback. It never activates persistent writer authority, standing automation, ready transition, merge, workflow dispatch, generated-output disposition, repository-setting authority, cleanup, or production configuration.

Live protected-path enforcement loads the reviewed Prime source at `policies/protected-paths.json`; there is no second hard-coded path list. The policy covers Prime authority, governance, schema, migration, Quest Board, generated, workflow, and Thread Engine self-change boundaries.

## Aegis Break Protected Route

Ordinary Spear, Bow/Arrow, fixture Thread Engine, and ordinary production missions reject protected paths. The Aegis Break protected route is a separate production-adapter launch profile for an exact Athena-authored Weave that already carries explicit protected-path authority.

The protected route requires all normal production-adapter controls plus:

- `aegis_break_authority.route_identity = AEGIS_BREAK_PROTECTED_PATH_V1`;
- explicit launcher or CLI intent: `-AegisBreakProtectedRoute -AegisBreakAuthorityId <id>` or `--aegis-break-protected-route --aegis-break-authority-id <id>`;
- launch authority ID matching the mission authority ID;
- authenticated GitHub operator readback through the exact read-only `gh api user --jq .login` command;
- observed GitHub login matching the mission's `github_operator_login`;
- exact protected path set, source blob map, operation-set SHA-256, candidate-tree SHA-256, and final-pathset SHA-256 evidence in the receipt;
- source blob entries for every protected `REPLACE` and `DELETE`;
- draft-PR stop with no direct-main write, force push, automatic ready, automatic merge, workflow dispatch, cleanup, or standing authority.

Thread Engine self-change remains outside this route. The Prime protected policy centrally denies `tools/thread-engine/**` as a self-change target even when Aegis Break authority is present.

Codex's `WORKBOARD_ROW_UPDATE_V1` route is not inherited. Its CLI flags, mission schema, implementation, receipt fields, examples, and positive tests are absent in Prime. Prime Quest Board changes remain protected and require a separately reviewed Prime-native route.

## Launcher

PowerShell 7:

```powershell
./Invoke-AtlasThreadEngine.ps1 -WeavePath ./examples/add-replace.example.json -FixtureOnly -AuditOnly
```

Python 3:

```text
python -B -m engine.thread_engine --weave examples/add-replace.example.json --fixture-only --audit-only
```

Both routes fail closed unless fixture-only and audit-only intent are explicit.

Mission-scoped production adapter:

```powershell
./Invoke-AtlasThreadEngineProductionAdapter.ps1 -MissionPath ./mission.json -MissionSha256 <sha256> -MissionScopedDraftPr -ExecuteDraftPr
```

The production-adapter launcher fails closed unless mission-scoped and draft-PR-only intent are explicit.

Aegis Break protected-route mission:

```powershell
./Invoke-AtlasThreadEngineProductionAdapter.ps1 -MissionPath ./mission.json -MissionSha256 <sha256> -MissionScopedDraftPr -ExecuteDraftPr -AegisBreakProtectedRoute -AegisBreakAuthorityId <authority-id>
```

The protected-route launcher fails closed unless the protected-route switch and exact authority ID are both supplied.
