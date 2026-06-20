# Athena’s Spear Real Packet Corpus v0.2

Status: Read-only compiler fixture plan  
Purpose: Define the real Atlas cases and hostile variants that must pass before Spear gains write authority.

## Required positive fixtures

1. Daily Sunset continuity memory
2. External URL Harvest with clean pointer
3. Chat Harvest preserving reasoning
4. Explicit Jayson decision
5. Active Work state update
6. Controlled Burn Synthesis Record
7. Emberline Continuity Record
8. Phoenix Burn multi-file promotion
9. Aegis lesson candidate
10. Existing PR repair
11. Orphan-branch recovery state
12. Post-merge verification
13. Hermes candidate packet
14. Apple Shortcut submission
15. n8n submission
16. Daily Sunset duplicate no-op
17. Advisory duplicate memory
18. Multi-file cross-reference creation

## Required hostile fixtures

1. Ambiguous cross-Project ownership
2. Stale base object
3. Stale target blob object
4. Duplicate packet ID with identical hash
5. Packet-ID collision with different hash
6. Prohibited secret
7. Raw PHI
8. Raw finance/account evidence
9. Path traversal
10. Encoded path traversal
11. Workflow targeting
12. Spear self-modification
13. Missing end marker
14. Duplicate JSON key
15. Invalid packet hash
16. Change-count mismatch
17. Conflicting operations on one path
18. Continuity-to-canonical authority escalation
19. Missing approval basis
20. Hermes packet requesting promotion
21. Unsupported hard deletion
22. Oversized packet
23. Oversized one-change payload
24. Excessive changed-file count
25. Diff-size limit exceeded
26. Destination-policy version mismatch
27. Plan expiration
28. Manifest-hash mismatch
29. Caller replay
30. Caller exceeds maximum authority
31. Repair head moved
32. Repair cycle exceeds limit
33. Generated-view direct edit
34. Promotion omits continuity source link
35. Consolidation attempts to delete source memory
36. Create target already exists
37. Bundle upsert missing stable record key
38. Exact replacement has multiple occurrences
39. Heading append heading not unique
40. Prohibited-content error leaks matched value

## Result expectations

Each fixture declares exactly one expected primary result:

- PLAN_CLEAN
- PLAN_CLEAN_WITH_WARNINGS
- BLOCKED
- DUPLICATE_NOOP
- STALE_SOURCE
- REPAIR_REQUIRED
- MANUAL_JAYSON_DECISION_REQUIRED
- VERIFICATION_CLEAN
- VERIFICATION_FAILED

## Acceptance rule

The first compiler release is not eligible for a write phase until:

- all hostile fixtures block or route exactly as expected;
- all positive fixtures create deterministic normalized manifests;
- repeated runs produce byte-identical manifests and diffs;
- no redacted protected value appears in logs;
- and the test suite runs locally and in read-only GitHub Actions.
