---
title: "Mission Publisher"
atlas_id: "prime.tools.mission-publisher"
status: "CANDIDATE"
source_type: "TOOL_CONTRACT"
authority_class: "CANONICAL_AUTHORED_SOURCE"
owner_project: "Project Codex"
owner_operation: "Operation Phoenix"
protected_level: "HIGH"
---

# Mission Publisher

`tools.mission_publisher` is a deterministic read-only compiler. It turns a validated Mission manifest, exact canonical base, proposed changed paths, and the sealed path envelope into a publication plan.

```text
python -B -m tools.mission_publisher MISSION.json \
  --canonical-base EXACT_SHA \
  --changed-path path/to/file \
  --sealed-path path/to/file
```

The compiler never creates repository objects. An authenticated adapter must fresh-read the Issue, all comments, canonical `main`, refs, PRs, attempts, reviews, and receipts before executing the plan. It then creates at most one branch, one commit, and one draft PR, and publishes a sanitized receipt.

On ambiguity or interruption, stop as `BLOCKED_RESUMABLE`; never retry mutation blindly.
