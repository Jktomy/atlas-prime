# Atlas Sword Framework

**Implementation state:** `PILOT_READY_PROOF_PENDING`  
**Runtime modes:** `AUDIT_ONLY`, `PRODUCTION_GITHUB_NATIVE`  
**Change method:** `OATHBRINGER`  
**Operator interface:** `POWERSHELL`  
**Execution environment:** `GITHUB`  
**Preferred repository transaction:** `GITHUB_NATIVE`  
**Production mutation adapter:** present; harmless live proof pending  
**Canonical doctrine:** `methods/atlas-sword.md`  
**Forge standard:** `methods/sword-forge-standard.md`  
**Lessons register:** `methods/sword-lessons.json`

This directory contains the reusable, versioned Atlas Sword framework.

```text
Sword route
+ Oathbringer change method
+ Sword Forge Standard
+ verified Sword lessons
+ one mission manifest
+ exact payload files
+ thin PowerShell client
+ deterministic GitHub-native adapter
= one mission-specific Oathbringer
```

## Current capability truth

The schema `1.2` audit framework remains available through `-AuditOnly`.

Wave 2 adds a production-format `2.0` adapter that can:

- authenticate through process-scoped `OATHBRINGER_GITHUB_TOKEN`, `GH_TOKEN`, `GITHUB_TOKEN`, or `gh auth token`;
- create exact GitHub blobs and a complete candidate tree;
- create one single-parent commit;
- create a new branch and draft pull request for BUILD;
- fast-forward an existing exact pull-request branch for REPAIR;
- mark an independently audited exact head ready and merge it for EXECUTE;
- verify the remote branch, commit, pull request, changed paths, and exact head;
- classify and wait only for applicable GitHub Actions workflows;
- write atomic JSON receipts and SHA-256 sidecars on success, failure, or interruption.

The adapter does not persist or print the GitHub token. It does not clone Atlas, author source, reinterpret payload bytes, force-push, write directly to `main`, broaden scope, or merge without a separate exact Execute mission.

Production source is present, but the capability is not yet restored. Wave 3 must prove AJ-04, AJ-05, and AJ-06 with harmless live GitHub transactions before Prime may move CAP-017 from `STILL_MISSING` to `REPLACED`.

## Mandatory forge inputs

Before any mission-specific carrier is built, Athena must read the current Forge Standard, lessons register, Sword doctrine, this implementation source, and exact live GitHub target state. The operator does not need to invoke a separate preflight command.

Every sealed carrier must identify:

- `SWORD_FORGE_STANDARD_V1`;
- the `prime-sword-lessons-v1` register and its exact source SHA-256;
- all controlling lesson IDs classified as `APPLIED` or `NOT_APPLICABLE` with reasons;
- complete multi-file operations and candidate bytes;
- exact repository, base, branch or pull request, and head locks;
- package, payload, receipt, workflow, recovery, and stop contracts.

## Production mission format

Production missions use:

```text
format_version = 2.0
framework_state = PILOT_READY_PROOF_PENDING
runtime_mode = PRODUCTION_GITHUB_NATIVE
change_method = OATHBRINGER
operator_interface = POWERSHELL
execution_environment = GITHUB
```

The canonical schema is:

```text
tools/atlas-sword/schema/oathbringer-production-mission-v2.schema.json
```

Supported lanes:

- `BUILD`
- `REPAIR`
- `EXECUTE`

Supported source operations:

- `ADD`
- `REPLACE`
- `DELETE`
- `RENAME`
- `MOVE`

## Production invocation

A sealed production Sword is launched with one current-directory-independent command equivalent to:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File .\engine\Invoke-AtlasSword.ps1 `
  -MissionPath .\mission.json `
  -ReceiptPath .\oathbringer.receipt.json
```

PowerShell resolves authentication and passes the token to the deterministic Python adapter only through a temporary process environment variable. It restores the prior process environment after execution.

For parseable machine output:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File .\engine\Invoke-AtlasSword.ps1 `
  -MissionPath .\mission.json `
  -ReceiptPath .\oathbringer.receipt.json `
  -Json
```

There is no second confirmation. Pressing Enter on the exact command is Jayson's invocation authorization for that sealed mission.

## Oathbringer audit contract

The audit-only framework validates:

- schema `1.2` mission identity, base, branch, head, and declared paths;
- `change_method = OATHBRINGER`;
- PowerShell as the thin human-facing operator interface;
- exact `ADD`, `REPLACE`, and separately authorized `DELETE` declarations;
- untracked `ADD` enumeration before intent-to-add when clone fallback is selected;
- workflow applicability from exact changed paths and hash-bound workflow source;
- exact workflow name, `pull_request` event, and head SHA filtering;
- `REQUIRED` versus `NOT_APPLICABLE` workflow classification;
- bounded workflow appearance and separate completion wait contracts;
- same-run refresh and newer-run precedence;
- accurate stage entry before an operation begins;
- structured failure and operator-interrupt receipts;
- atomic JSON receipt writes with SHA-256 sidecars;
- parseable JSON mode;
- no automatic retry or rollback.

## Audit-only invocation

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File .\engine\Invoke-AtlasSword.ps1 `
  -MissionPath .\examples\build.example.json `
  -AuditOnly
```

## Authority

Code never grants authority. Every Oathbringer requires:

- a new immutable identity and carrier SHA-256;
- an approved Preview;
- Strikeforce-to-Green;
- one exact current-directory-independent command;
- explicit authorization when Jayson presses Enter;
- exact mission locks and stop boundaries;
- independent Noctua review;
- a separate Execute decision.

PowerShell is the thin launcher and human-facing host. The packaged deterministic Python adapter owns mission validation, stage ledger state, GitHub transport, workflow filtering, timers, receipt classification, receipt writing, and structured output. It never authors or reinterprets Atlas payload bytes.

## Source and package manifest behavior

A checked-in source checkout does not require a package manifest. When the framework is embedded in a sealed carrier, both audit and production runners verify `MANIFEST.json` when present and report whether package-manifest verification occurred.
