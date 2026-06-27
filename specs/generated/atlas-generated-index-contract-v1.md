---
title: Atlas Prime Generated Index Contract v1
atlas_id: atlas-prime.generated.index-contract-v1
format_version: "1.0"
status: ACTIVE
source_type: CONTRACT
authority_class: SOURCE_GOVERNANCE
owner_project: Codex
owner_operation: Source Governance
canonical_scope: Defines the Prime-native, bounded, deterministic contract for generating repository-support indexes without granting source-governance, migration, deletion, promotion, or cutover authority.
protected_level: CRITICAL
routes_from:
  - migration/atlas-codex/README.md
  - migration/atlas-codex/migration-map.md
  - migration/atlas-codex/audits/atlas-codex-delta-0001-merge-closeout-v1.md
  - Jktomy/atlas-codex:codex/atlas-generated-index-standard.md
  - Jktomy/atlas-codex:tools/build_index.py
routes_to:
  - tools/build_index.py
  - tests/test_build_index.py
  - generated/atlas-file-inventory.md
  - generated/atlas-metadata-inventory.md
  - generated/atlas-routing-inventory.md
  - generated/atlas-orphan-report.md
  - generated/atlas-duplicate-scope-report.md
private_boundary: The generator may inspect clean repository text and emit paths, metadata summaries, routing signals, warning counts, and redacted support information only. It must not emit secrets, credentials, tokens, MFA or recovery codes, PHI, raw finance evidence, account data, private runtime values, IP addresses, network maps, device registers, raw exports, or real .env values.
evidence_boundary: Source files, Git objects, generator code, tests, generated reports, preview receipts, Noctua reports, pull requests, and merge records remain distinct evidence sources. Generated reports never replace the source files they summarize.
supersedes: []
cleanup_path: Retain as the generated-index contract until a separately approved version supersedes it. Never rewrite historical generated-output audit records to reflect a later generator version.
last_verified: 2026-06-27
---

# Atlas Prime Generated Index Contract v1

## 1. Purpose

Atlas Prime generated indexes are deterministic, read-only support projections of the repository.

They accelerate inspection of:

- Markdown file coverage;
- front-matter coverage;
- routing references;
- active orphan candidates;
- duplicate canonical-scope claims;
- file-level sensitive-content review signals.

Generated indexes report. They do not govern.

They may not decide canonical truth, ownership, migration, retirement, deletion, promotion, source replacement, writer activation, or cutover.

## 2. Approved implementation

The approved Prime-native implementation is:

```text
tools/build_index.py
```

Its validation suite is:

```text
tests/test_build_index.py
```

The implementation uses the Python standard library only.

## 3. Exact generated-output allowlist

The generator may write only these files:

```text
generated/atlas-file-inventory.md
generated/atlas-metadata-inventory.md
generated/atlas-routing-inventory.md
generated/atlas-orphan-report.md
generated/atlas-duplicate-scope-report.md
```

A custom `--output-dir` may be used for isolated previews and tests, but the generator must still write only the five allowlisted basenames directly inside that directory.

The generator must never:

- write outside the selected output directory;
- write an unapproved filename;
- edit a source file;
- delete, move, or rename a file;
- invoke Git or GitHub;
- access the network;
- execute a subprocess;
- modify a workflow;
- push or merge;
- clean up branches or evidence.

## 4. Source scan boundary

The generator scans UTF-8 Markdown files under the selected repository root.

It excludes:

```text
.git/
.github/
generated/
__pycache__/
```

Generated reports therefore never recursively inventory themselves.

Non-Markdown files are not included in the initial report set.

## 5. Prime routing surfaces

Routing checks use only existing members of this explicit list:

```text
README.md
bootstrap.md
atlas-start-here.md
atlas-index.md
atlas-protocol-registry.md
atlas-command-surface.md
migration/atlas-codex/README.md
migration/atlas-codex/migration-map.md
specs/atlas-prime/codex-to-prime-migration-contract-v2.md
```

Absence of a listed routing surface is not an error. It contributes no routing text.

Changing this list is a source change and requires Preview → Execute.

## 6. Determinism

Authoritative generated-output runs must bind:

- repository root;
- source revision;
- generated date;
- output directory;
- generator version.

The CLI supports:

```text
--repo-root
--output-dir
--source-revision
--generated-date
--dry-run
--check
```

`--generated-date` accepts an ISO `YYYY-MM-DD` value.

When it is omitted, the implementation may derive the UTC date from `SOURCE_DATE_EPOCH`; only when neither is supplied may it use the current local date.

A generated-output PR must always pass an explicit generated date and source revision.

For the same repository bytes, generated date, source revision, and generator version, repeated runs must produce byte-identical UTF-8/LF output.

## 7. Modes

### Write mode

Write mode creates or replaces only the five allowlisted reports in the selected output directory.

It does not delete unrecognized files from that directory.

### Dry-run mode

`--dry-run` computes all five reports and prints their paths, sizes, and SHA-256 values without writing them.

### Check mode

`--check` computes all five reports and compares them to the selected output directory.

It returns success only when every approved report exists and is byte-identical.

It never writes.

## 8. Metadata parsing

The generator performs bounded, simple YAML-front-matter extraction sufficient for the Prime metadata fields used by the reports.

It is not a general YAML authority.

A missing or malformed front matter block is reported as missing metadata; it does not invalidate the source file.

## 9. Sensitive-content boundary

Generated reports may expose:

- repository-relative paths;
- metadata-presence status;
- clean metadata summaries;
- `none`, `policy-reference`, or `review` sensitive hints;
- redacted warning cells;
- counts and routing signals.

Generated reports must not reproduce a value that matches the implementation’s high-confidence secret patterns.

Such values are rendered as:

```text
[REDACTED]
```

The sensitive hint is a warning signal only. It is not proof of a secret, deletion authority, or a security incident.

## 10. Orphan and duplicate reports

An orphan candidate is not deletion approval.

A duplicate canonical scope is not automatic conflict resolution.

Both reports are queues for human review and later source-governance action.

## 11. Source and generated PR separation

The generator contract, implementation, and tests form a source PR.

The first generated reports form a later generated-output-only PR.

The two classes must not be mixed.

The generated-output PR must contain exactly the five approved files under `generated/`.

## 12. Required source validation

Before the source foundation may merge:

1. `python -m py_compile tools/build_index.py tests/test_build_index.py`
2. `python -m unittest discover -s tests -p test_build_index.py -v`
3. a dry run against an exact Prime commit;
4. two write runs with fixed date and source revision producing identical hashes;
5. a successful check-mode run;
6. an exact three-file source diff audit;
7. a protected-boundary scan;
8. Noctua outcome `YES`.

## 13. Required generated-output validation

Before generated reports may merge:

1. the generator foundation is merged and read back from Prime `main`;
2. the generator and tests match the approved blobs;
3. the build is bound to the exact Prime source commit;
4. output is exactly the five-file allowlist;
5. repeated runs are byte-identical;
6. check mode passes;
7. no high-confidence secret value or private runtime value is present;
8. the generated-only diff is audited;
9. Noctua outcome is `YES`;
10. manual squash merge and main-branch readback complete.

## 14. Authority boundary

This contract grants no authority for:

- source migration;
- collision resolution;
- disposition-ledger creation;
- Workboard modification;
- S1 dispatch or activation;
- generated-output auto-merge;
- source promotion;
- Codex retirement;
- deletion;
- cleanup;
- cutover.

M0-D remains open until the generated-output route, the Active Workboard route, and the final delta `MERGED` → `CLOSED` transition are separately completed.
