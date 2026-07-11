# Oathbringer Foundry

`SWORD_FORGE_COMPILER_V1` compiles Athena-authored exact payload bytes into a
deterministic sealed Oathbringer carrier. It is deliberately narrower than
Oathbringer: Foundry validates, binds, packages, and reports; it never performs
GitHub mutation or grants authority.

Canonical doctrine: `methods/oathbringer-foundry.md`
Forge Standard: `methods/sword-forge-standard.md`
Lessons register: `methods/sword-lessons.json`
Delivery Standard: `methods/consistent-pr-delivery-standard.md`

For human-operated BUILD, REPAIR, and EXECUTE preparation, use
`Invoke-AtlasDeliveryStandard.ps1`. It preserves Foundry diagnostics and always
finishes a sanitized outer evidence ZIP plus SHA-256 sidecar, including safe
rejections. The carrier still runs through Oathbringer Console v2 and retains
all existing exact-head, audit, authorization, and stop-boundary gates.

## Compile

```text
python -B tools/oathbringer-foundry/cli.py compile \
  --input-root <mission-input-directory> \
  --source-root . \
  --output-dir <carrier-output-directory>
```

Every production compile obtains the current GitHub lock through read-only `gh
api` requests. The compiler prints only carrier identity, hashes, locks, and
paths; it never prints a credential.

## Output

One compile writes:

- `Oathbringer-Foundry-<mission>-<revision>.zip` and its SHA-256 sidecar;
- `FOUNDRY-REPLAY-LEDGER.json` in the output directory; a recorded mission
  identity is rejected on later production compiles from that durable ledger;
- an immutable `MANIFEST.json` and `SHA256SUMS.txt` inside the carrier;
- canonical mission, authority, source/target locks, operation inventory,
  complete payload bytes, source lessons, transport library, launcher,
  recovery instructions, test contract, and Forge receipt.

Run `verify` against a carrier before delivery:

```text
python -B tools/oathbringer-foundry/cli.py verify --carrier <carrier.zip>
```

The extracted carrier launcher remains current-directory-independent. It starts
the pre-bound Oathbringer mission only; user/operator invocation and every
existing Oathbringer gate remain required.
