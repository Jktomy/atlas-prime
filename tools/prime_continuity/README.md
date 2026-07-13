# Prime continuity engine

This read-only module validates the schema-driven Quest Board and canonical
operational continuity register. It plans exactly one-entry, replay-ledger-bound
continuity updates, renders a deterministic non-authoritative Emberline, and
reconstructs bounded Sunset, Sunrise, and Argus views without chat memory.

The Quest Board remains the canonical Quest registry. Continuity adds
unfinished-work detail but cannot advance Quest state. A planned update writes
nothing; durable apply still requires one exact branch, draft PR, review, and
merge. Sunrise must be anchored to the canonical register; the snapshot's own
digest is not authority. Generated Emberlines report and never govern.

## Commands

Run from the repository root:

```text
python -B -m tools.prime_continuity.cli validate
python -B -m tools.prime_continuity.cli emberline [--output PATH]
python -B -m tools.prime_continuity.cli argus [--output PATH]
python -B -m tools.prime_continuity.cli sunset --continuity-id ID [--output PATH]
python -B -m tools.prime_continuity.cli sunrise --snapshot PATH [--output PATH]
python -B -m tools.prime_continuity.cli plan-update --continuity-id ID --expected-register-sha256 SHA --expected-entry-revision N --event-id ID --changes-json JSON [--output PATH]
```

`plan-update` emits a candidate and never replaces the canonical register.
Durable apply still requires the reviewed source transaction in the contract.
