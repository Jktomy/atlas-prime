---
title: "Sunset Router"
atlas_id: "prime.tools.sunset-router"
status: "CANDIDATE"
source_type: "TOOL_CONTRACT"
authority_class: "CANONICAL_AUTHORED_SOURCE"
owner_project: "Project Codex"
owner_operation: "Operation Source Governance"
protected_level: "CRITICAL"
---

# Sunset Router

`tools.sunset_router` is the deterministic front door for full Atlas Sunset. It
resolves Project, Operation, and admitted-Quest ownership from canonical Prime,
selects the permitted route from declared actor identity, and delegates Preview,
approval, candidate construction, and candidate verification to the existing
`tools.atlas_lifecycle` engine.

```text
python -B -m tools.sunset_router preview --request ROUTER_REQUEST.json --output-dir NEW_TEMP_DIR
python -B -m tools.sunset_router approve --router-dir PREVIEW_DIR --approval-mode STANDARD|GODDESS_MODE|GODDESS_MODE_SHARDBLADE --output-dir NEW_TEMP_DIR
python -B -m tools.sunset_router candidate --router-dir PREVIEW_DIR --approval-dir APPROVAL_DIR --output-dir NEW_TEMP_DIR
python -B -m tools.sunset_router verify --router-dir PREVIEW_DIR --approval-dir APPROVAL_DIR --candidate-dir CANDIDATE_DIR
python -B -m tools.sunset_router receipt --router-dir PREVIEW_DIR --approval-dir APPROVAL_DIR --candidate-dir CANDIDATE_DIR --state READBACK_COMPLETE --expected-head HEAD --pull-request PR --merged-commit MERGE
```

Athena defaults to Spear with Phoenix Blade and Aegis Break as ordered
fallbacks. Jayson and delegated non-Athena routes require explicit operator
transfer and an exact route; `AUTO` never transfers operators.

## Owner-only Mission Preview ingress

After `.github/workflows/sunset-router-preview-intake.yml` is canonical, Jayson
may request one exact Mission #257 Preview by posting only this closed block:

````text
```atlas-sunset-router-preview-intake-v1
{CANONICAL_SINGLE_LINE_JSON}
```
````

The JSON must validate as
`atlas.sunset-router.preview-intake` version `1.0.0`, bind the exact current
`main`, declare `ATHENA_SPEAR_THREAD_ENGINE`, forbid operator transfer, include a
fresh replay nonce and `PUBLIC_CLEAN_CONFIRMED`, and contain the complete closed
Router request. The comment is limited to 32 KiB.

`tools.sunset_router.issue_preview_ingress admit` validates the GitHub event,
owner, repository, Issue, canonical bytes, schema, public-clean boundary, base,
route, request digest, and replay identity. The workflow then invokes only
`tools.sunset_router preview` in system temporary storage.
`tools.sunset_router.issue_preview_ingress render` returns the exact lifecycle
Preview, exact Router receipt, their digests, the replay binding, and one explicit
Jayson approval command to Mission #257.

The ingress is Preview-only. It cannot approve the Preview, compile a candidate,
create a branch or PR, write source, mark READY, merge, change settings, operate
runtime, advance a Quest, transfer an operator, or claim `SUNSET COMPLETE`.

All output is temporary, public-clean, canonical JSON. The router never writes
canonical source, creates a branch or PR, marks READY, merges, advances a Quest,
retires a route, or reports `SUNSET COMPLETE`. The publication plan binds the
verified lifecycle candidate record paths, exact `ADD` or `REPLACE` operations,
and payload digests. It preserves `BLOCKED_RESUMABLE` through the same plan
identity and emits `READBACK_COMPLETE` only when canonical `main` contains the
exact planned bytes.
