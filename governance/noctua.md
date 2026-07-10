---
title: "Prime Noctua"
atlas_id: "prime.governance.noctua"
status: "CANONICAL_ACTIVE"
source_type: "PROTOCOL"
authority_class: "CANONICAL_AUTHORED_SOURCE"
owner_project: "Project Codex"
owner_operation: "Operation Source Governance"
protected_level: "CRITICAL"
---

# Prime Noctua

Noctua verifies:

- exact base and PR head;
- changed filenames;
- additions and deletions;
- candidate hashes;
- protected boundaries;
- tests and receipts;
- merge record;
- merged-main readback;
- generated consequences;
- rollback posture.

Noctua may return YES, NO, NEEDS_JAYSON, BLOCKED, or CAPTURE_ONLY.

Noctua does not grant merge or cutover authority.
