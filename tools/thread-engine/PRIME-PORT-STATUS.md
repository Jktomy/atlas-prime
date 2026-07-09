# Prime Thread Engine Port Status

The source beneath this directory is copied at Build time from the verified Codex Thread Engine source at:

```text
1c43a5c7903a38a684b906e87a6475651a900a39
```

It is a **port candidate**, not an activated production tool.

```text
Implementation:
PORT_CANDIDATE_DISABLED

Production execution:
NOT AUTHORIZED

Proof:
REQUIRED IN PR-C03
```

The Build script replaces exact repository identity strings and installs a production-launcher guard. It does not claim full Prime policy parity.

PR-C03 must audit every remaining Codex-bound assumption, run the complete tests, prove disablement, and produce one harmless mission-scoped draft PR before Prime Thread Engine may be called working.
