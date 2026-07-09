# Prime Thread Engine Port Status

The source beneath this directory is copied at Build time from the verified Codex Thread Engine source at:

```text
1c43a5c7903a38a684b906e87a6475651a900a39
```

It is a **Prime-native, disabled port candidate**, not an activated production tool.

```text
Implementation:
PORT_CANDIDATE_DISABLED

Production execution:
NOT AUTHORIZED

Proof:
REQUIRED IN PR-C03
```

The repaired candidate enforces this state inside the Python adapter as well as the CLI and PowerShell launcher. Disabled receipts report `PORT_CANDIDATE_DISABLED`, `thread_engine_active: false`, and `production_execution_authorized: false`.

Live protected-path enforcement loads `policies/protected-paths.json`. The Codex Workboard route is absent from Prime's CLI, schema, implementation, receipts, examples, and positive tests.

PR-C03 must activate the adapter through Aegis Break → Oathbringer, rerun the complete tests, and produce one harmless mission-scoped draft PR before Prime Thread Engine may be called working.
