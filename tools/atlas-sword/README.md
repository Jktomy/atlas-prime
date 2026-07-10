# Atlas Sword Framework

**Implementation state:** `PILOT_DISABLED`
**Runtime mode:** `AUDIT_ONLY`
**Change method:** `OATHBRINGER`
**Operator interface:** `POWERSHELL`
**Preferred repository transaction:** `GITHUB_NATIVE`
**Production mutation adapters:** absent
**Canonical doctrine:** `methods/atlas-sword.md`
**Forge standard:** `methods/sword-forge-standard.md`
**Lessons register:** `methods/sword-lessons.json`

This directory contains the reusable, versioned audit scaffold for Atlas Sword.

```text
Sword route
+ Oathbringer change method
+ Sword Forge Standard
+ verified Sword lessons
+ one mission manifest
+ exact payload files
= one mission-specific Oathbringer
```

The checked-in framework validates mission structure and execution contracts. It
does not clone, branch, commit, push, create or edit pull requests, mark a pull
request ready, merge, dispatch workflows, alter repository settings, or write to
Google Drive.

The runner requires `-AuditOnly`. Production mutation adapters remain separately
proof-gated.

## Mandatory forge inputs

Before any mission-specific carrier is built, Athena must read the current Forge Standard, lessons register, Sword doctrine, this implementation source, and exact live GitHub target state. The operator does not need to invoke a separate preflight command.

Every sealed carrier must identify:

- `SWORD_FORGE_STANDARD_V1`;
- the `prime-sword-lessons-v1` register and its exact source identity;
- all controlling lesson IDs classified as `APPLIED` or `NOT_APPLICABLE` with reasons;
- complete multi-file operations and candidate bytes;
- exact repository, base, branch or pull request, and head locks;
- package, payload, receipt, workflow, recovery, and stop contracts.

The framework remains audit-only until Wave 2 adds and separately proves GitHub-native BUILD, REPAIR, and EXECUTE adapters.

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

For parseable machine output:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File .\engine\Invoke-AtlasSword.ps1 `
  -MissionPath .\examples\build.example.json `
  -AuditOnly `
  -Json
```

For a durable local receipt:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File .\engine\Invoke-AtlasSword.ps1 `
  -MissionPath .\examples\build.example.json `
  -AuditOnly `
  -ReceiptPath .\oathbringer.receipt.json
```

## Authority

Code never grants authority. Every future Oathbringer still requires:

- a new immutable identity and carrier SHA-256;
- an approved Preview;
- Strikeforce-to-Green;
- one exact current-directory-independent command;
- explicit authorization when Jayson presses Enter;
- exact mission locks and stop boundaries;
- independent Noctua review;
- a separate Execute decision.

PowerShell is the thin launcher and human-facing host. Python or another packaged deterministic library may own mission validation, stage ledger state, GitHub transport, workflow filtering, timers, receipt classification, receipt writing, and structured output. It never authors or reinterprets Atlas payload bytes.

## Source and package manifest behavior

A checked-in source checkout does not require a package manifest. When the
framework is embedded in a sealed carrier, the audit runner verifies
`MANIFEST.json` when present and reports whether package-manifest verification
occurred.
