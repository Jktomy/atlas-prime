# Operation Ciel validator

`tools.ciel.engine` is a read-only validator for the Operation Ciel and Rimuru source boundary.

```bash
python -B -m tools.ciel.engine validate
```

It validates the closed schemas, rejects duplicate record and source identities, rejects unsafe or executable paths, verifies record-file presence and type binding, scans public-clean JSON for protected-value patterns, requires resolved Code Capsule licensing, and checks nonpromotion markers across the Ciel, Gluttony, Rimuru, and Quest contracts.

The validator creates no file, branch, Issue, pull request, package installation, runtime action, READY transition, or permanence action.
