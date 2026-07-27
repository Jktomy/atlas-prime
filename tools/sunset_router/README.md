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
selects the permitted route from actor identity, and delegates Preview, approval,
candidate construction, and verification to `tools.atlas_lifecycle`.

```text
python -B -m tools.sunset_router preview --request ROUTER_REQUEST.json --output-dir NEW_TEMP_DIR
python -B -m tools.sunset_router approve --router-dir PREVIEW_DIR --approval-mode STANDARD|GODDESS_MODE|GODDESS_MODE_SHARDBLADE --output-dir NEW_TEMP_DIR
python -B -m tools.sunset_router candidate --router-dir PREVIEW_DIR --approval-dir APPROVAL_DIR --output-dir NEW_TEMP_DIR
python -B -m tools.sunset_router verify --router-dir PREVIEW_DIR --approval-dir APPROVAL_DIR --candidate-dir CANDIDATE_DIR
python -B -m tools.sunset_router receipt --router-dir PREVIEW_DIR --approval-dir APPROVAL_DIR --candidate-dir CANDIDATE_DIR --state READBACK_COMPLETE --expected-head HEAD --pull-request PR --merged-commit MERGE
```

For Athena, `AUTO` selects Aegis Break with Phoenix Blade as the automatic
same-operator fallback. Explicit current-GitHub Spear selection rejects before
mutation as `CURRENT_GITHUB_SPEAR_RETIRED`. The historical route token remains
schema-readable. Jayson and delegated routes require explicit operator transfer;
`AUTO` never transfers operators.

Aegis Break selects and governs the publication route; the lifecycle engine owns
the exact lifecycle bytes. The router itself never writes canonical source,
creates a branch or PR, marks READY, merges, advances a Quest, or changes
settings.

## Retired Mission #257 Preview ingress

The campaign-specific hosted comment ingress is retired.
`.github/workflows/sunset-router-preview-intake.yml` is intentionally absent so
unrelated Issue comments do not create no-job workflow runs or notifications.
The closed schema and adapter remain historical evidence and local fixtures only.

Use the deterministic CLI for current operation. Restoring hosted ingress
requires a separately authorized transport contract whose trigger does not run
for unrelated comments.

All output is temporary, public-clean, canonical JSON. The publication plan
binds exact record paths, `ADD` or `REPLACE` operations, and payload digests.
`READBACK_COMPLETE` requires exact canonical main and exact planned bytes. No
router artifact alone can claim `SUNSET COMPLETE`.
