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
Oathbringer, PowerShell, and unclassified changes fail closed to the appropriate
Windows companion; ordinary Markdown, JSON, registry, Quest, continuity, and
generated-only changes do not require Windows unless another changed path does.

The pull-request workflow exposes `prime/integrity` and the conditional
`prime/windows-compatibility` logical contexts. Ruleset `Prime Main Protection`
currently requires the legacy `validate (ubuntu-latest)` and
`validate (windows-latest)` contexts, so the workflow retains bounded bridge
jobs until Jayson separately changes the ruleset after exact-head proof. Remove
the bridges only in a later reviewed source transaction after the new contexts
are required and observed on both Windows-required and Windows-skipped PRs.
