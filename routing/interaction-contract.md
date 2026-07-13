---
title: "Prime Interaction and Decision Contract"
atlas_id: "prime.routing.interaction-contract"
status: "CANONICAL_ACTIVE"
source_type: "PROTOCOL"
authority_class: "CANONICAL_AUTHORED_SOURCE"
owner_project: "Atlas"
owner_operation: "Source Governance"
protected_level: "HIGH"
---

# Prime interaction and decision contract

Every action reports objective, exact scope, current source authority, Preview,
route and method, authorizer and operator, protected boundary, expected proof,
stop point, rollback, observed result, and next safe action.

`Preview`, `Build`, `Execute`, `Ready`, and `Merge` are distinct decisions.
Preview never executes. Build never implies Execute. Execute never implies Ready
or Merge. A route name never grants authority. Unknown fields trigger read-only
investigation. Blocked work is surfaced through Prime continuity and Argus,
never inferred from chat memory or a generated projection.
