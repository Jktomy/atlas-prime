# Prime Thread Engine Port Status

The source beneath this directory is copied at Build time from the verified Codex Thread Engine source at:

```text
1c43a5c7903a38a684b906e87a6475651a900a39
```

It is a **Prime-native, mission-scoped production adapter** activated through the protected Aegis Break → Oathbringer source route. The fixture engine remains disabled and fixture-only.

```text
Implementation:
THREAD_ENGINE_ACTIVE_MISSION_SCOPED

Production execution:
AUTHORIZED FOR EXACT MISSION-SCOPED DRAFT PRS ONLY

Proof:
ACTIVATION SOURCE PROVEN; HARMLESS PILOT PENDING
```

The adapter enforces this state inside Python, the CLI, and the PowerShell launcher. Active receipts report `THREAD_ENGINE_ACTIVE_MISSION_SCOPED`, `thread_engine_active: true`, `production_execution_authorized: true`, and `authority_scope: MISSION_SCOPED`. They also preserve `standing_authority: NO`, require human merge, and confirm that the engine cannot mark ready or merge.

Live protected-path enforcement loads `policies/protected-paths.json`. The Codex Workboard route is absent from Prime's CLI, schema, implementation, receipts, examples, and positive tests.

Disabled-state rejection remains continuously tested through an isolated status source. Thread Engine self-change remains blocked. Prime Thread Engine may be called working only after the separate harmless mission opens a draft PR, passes exact readback and Strikeforce, merges, and is proven recoverable and disableable.
