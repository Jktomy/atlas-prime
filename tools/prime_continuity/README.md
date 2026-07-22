# Prime continuity engine

This read-only module validates the canonical Mission Board Quest registry
recovery snapshot, the frozen predecessor Quest Board, and the canonical
operational continuity register. It plans exactly one-entry,
replay-ledger-bound continuity updates, renders a deterministic
non-authoritative aggregate Emberline and one human-readable Mission Quest Emberline, and reconstructs bounded Sunset, Sunrise, and
Argus views without chat memory.

Here, `sunset` is the historical command name for a compact continuity
snapshot. It is not a full Atlas Sunset, creates no lifecycle
Feather/Sunset/Sunrise record set, performs no lesson absorption, and cannot
claim closeout. Route the full lifecycle objective through
`governance/lesson-harvest-protocol.md` and `tools.atlas_lifecycle` instead.

The Mission Board is the admitted-Quest registry and primary operational work
surface. `continuity/mission-board-quest-registry-r01.json` is the merged,
portable recovery snapshot of its active Quest parents, so recovery never
requires GitHub availability. Mission Issues coordinate state but cannot
silently advance merged Prime. `quest-board/quest-board-v1.json` is frozen
predecessor evidence and is never edited for future admissions.

Continuity adds unfinished-work detail but cannot advance Quest state. A
planned update writes nothing; durable apply still requires one exact branch,
draft PR, review, and merge. Sunrise must be anchored to the canonical
register; the snapshot's own digest is not authority. Generated Emberlines report and never govern. Each Mission Quest row binds one
stable Emberline ID and the exact `mission/quest` label; the per-Quest renderer
joins that row to canonical continuity and includes readable Markdown for the
parent Issue.

## Commands

Run from the repository root:

```text
python -B -m tools.prime_continuity.cli validate
python -B -m tools.prime_continuity.cli emberline [--output PATH]
python -B -m tools.prime_continuity.cli mission-quest-emberline --quest-id QUEST_ID [--output PATH]
python -B -m tools.prime_continuity.cli argus [--output PATH]
python -B -m tools.prime_continuity.cli sunset --continuity-id ID [--output PATH]
python -B -m tools.prime_continuity.cli sunrise --snapshot PATH [--output PATH]
python -B -m tools.prime_continuity.cli plan-update --continuity-id ID --expected-register-sha256 SHA --expected-entry-revision N --event-id ID --changes-json JSON [--output PATH]
```

`plan-update` emits a candidate and never replaces the canonical register.
Every `--output` must resolve outside the canonical repository and must not
already exist; output commands use no-clobber creation. Durable apply still
requires the reviewed source transaction in the contract.
