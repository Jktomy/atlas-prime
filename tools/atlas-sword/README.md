# Atlas Sword Framework

**Implementation state:** `PILOT_DISABLED`
**Runtime mode:** `AUDIT_ONLY`
**Change method:** `OATHBRINGER`
**Execution environment:** `POWERSHELL`
**Production mutation adapters:** absent
**Canonical doctrine:** `atlas-sword.md`

This directory contains the reusable, versioned audit scaffold for Atlas Sword.

```text
Sword route
+ Oathbringer change method
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

## Oathbringer audit contract

The audit-only framework validates:

- schema `1.2` mission identity, base, branch, head, and declared paths;
- `change_method = OATHBRINGER`;
- `execution_environment = POWERSHELL`;
- exact `ADD`, `REPLACE`, and separately authorized `DELETE` declarations;
- untracked `ADD` enumeration before intent-to-add;
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

PowerShell is the thin launcher and human-facing host. Python is the sole
deterministic Oathbringer engine for mission validation, stage ledger state,
workflow filtering, timers, receipt classification, receipt writing, and
structured output.

## Source and package manifest behavior

A checked-in source checkout does not require a package manifest. When the
framework is embedded in a sealed carrier, the audit runner verifies
`MANIFEST.json` when present and reports whether package-manifest verification
occurred.
