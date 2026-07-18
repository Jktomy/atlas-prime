---
status: Active
source_type: Template
canonical_scope: Template for Atlas Preview Bundles, including preview classification, runtime impact, affected files, verification plan, and execute-ready summary.
protected_level: Medium
---

# Preview Bundle: [Preview ID]

Status: Preview only
Classification: [Tiny Patch / Support File Update / Routing Update / Dashboard Update / Emberline / Runtime-Infrastructure]
Runtime impact: [None / Stated impact]

## Purpose

[What this preview changes.]

## Files affected

Create:
- [File]

Modify:
- [File]

Skip:
- [File]

## Safety review

- Secrets: [No / risk]
- PHI: [No / risk]
- Finance evidence: [No / risk]
- Runtime impact: [No / yes]
- Large protected file impact: [No / yes]
- Deletion / migration: [No / yes]

## Proposed changes

[Exact proposed content or bounded diff summary.]

## Verification anchors

- [File / heading / line concept]

## Semantic objective and assurance controls

- User semantic objective: [Exact meaning, independent of command-name overlap]
- Objective-to-route reconciliation: [Canonical route and rejected substitution]
- Assurance-control applicability:
  - [ASC-ID]: [APPLIED with exact enforcement/evidence | NOT_APPLICABLE with exact objective-specific reason]
- Unknown or omitted applicability: FAIL CLOSED

## Rollback plan

[Revert commit / remove new files / restore previous routing.]

## Changelog impact

[Needed / not needed.]

## Execute command

```text
EXECUTE PREVIEW: [Preview ID]
```
