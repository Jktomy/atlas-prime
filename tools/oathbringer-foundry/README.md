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

Evidence verification requires three independent inputs: the ZIP, its sidecar,
and the expected SHA-256 copied from the controlling receipt or handoff. The
verifier rejects unknown receipt fields, untrusted identities, missing authority
invariants, unexpected members, noncanonical paths, compression, special files,
oversized archives or members, excessive JSON nesting, and any disagreement
between the independent digest, sidecar, archive, manifest, and receipt binding.

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

## Lifecycle carrier binding

G4-D2 permits one optional shared lifecycle construction profile in BUILD mode.
It accepts exactly one route-declared `ADD` under `lifecycle/events/` and
preserves the complete G4-C `event.json`, `candidate-manifest.json`, and
`candidate-receipt.json` set under `payload/lifecycle-candidate/`. The compiler
validates the profile and candidate against Prime's fixed coinstalled lifecycle
schemas, binds the event ID, immutable repository path, exact base and revision
locks, trust/state/candidate digests, and records a non-writer, no-GitHub-authority
Forge receipt. Sealed-carrier verification repeats the independent candidate
readback.

This binding only packages deterministic bytes. It cannot author meaning,
accept a transition, advance a Quest, open or ready a pull request, merge, or
write canonical source.
