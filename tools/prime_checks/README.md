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
Workflow, validation-engine, and unclassified changes fail closed to the full
suite, and protected or cross-platform surfaces require the Windows companion.
