# Operation Ciel validator

`tools.ciel.engine` is a read-only validator for the Operation Ciel and Rimuru source boundary.

```bash
python -B -m tools.ciel.engine validate
```

It validates the closed schemas; rejects duplicate record, source, path, and finding identities; rejects unsafe or executable paths; verifies record-file presence and type binding; rejects orphan or undeclared JSON; scans public-clean JSON for protected-value patterns; requires resolved Code Capsule licensing; verifies Harvest registry bindings; verifies every Absorption's internal Harvest locator and exact Harvest-file SHA-256; and checks nonpromotion markers across the Ciel, Gluttony, Rimuru, and Quest contracts.

Rimuru registry revision 2 is the bounded **First Gluttony** inventory. It must contain exactly 21 reviewed Harvest Records and 21 reviewed paired Absorption Records, with zero Code Capsules.

The validator creates no file, branch, Issue, pull request, package installation, runtime action, READY transition, downstream Mission, or permanence action.
