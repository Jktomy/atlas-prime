# Prime validation entrypoint

Run the complete current Prime validation suite locally with:

```text
python -B tools/prime_checks/targeted_validation.py --full
```

Plan or run changed-path validation by supplying exact Git base and head SHAs:

```text
python -B tools/prime_checks/targeted_validation.py --base <base-sha> --head <head-sha>
```

Privacy and repository-policy tests are mandatory in every targeted plan.
Prime Integrity also records the exact base, head, merge base, checkout identity,
changed-path inventory, and deterministic generated-current comparison.
Workflow, validation-engine, Athena route execution, Thread Engine, Atlas Sword,
Oathbringer, PowerShell, generator machinery and tests, schema, and unclassified
changes fail closed to the Windows companion. Ordinary Markdown, JSON, registry,
Quest, continuity, and generated-only changes do not require Windows unless
another changed path does.

Rename and copy evidence classifies both the source and destination paths, so a
risky source cannot disappear behind a safe destination name. Case-only path
pairs and mixed candidates require Windows. Malformed, absolute, traversal-like,
backslash, control-character, surrounding-whitespace, case-mismatched, ambiguous,
and otherwise unknown path evidence fails closed to the complete profile with
Windows required.

The pull-request workflow exposes `prime/integrity` and the conditional
`prime/windows-compatibility` logical contexts. Ruleset `Prime Main Protection`
(`19014636`) requires those exact contexts after the independently verified
Stage 1A settings transition. The retired `validate (ubuntu-latest)` and
`validate (windows-latest)` compatibility jobs are no longer emitted.

Pull-request validation runs when a PR is `opened`, `synchronize`d, or
`reopened`. The unchanged ready-for-review transition does not rerun validation;
READY must rely on the already completed exact-head checks. If candidate bytes
change after READY, return the PR to draft and push the replacement head so the
`synchronize` event validates it before review, Strikeforce, and READY repeat.
