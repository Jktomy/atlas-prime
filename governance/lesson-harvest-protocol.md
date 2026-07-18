---
title: "Atlas Lesson Harvest Protocol"
atlas_id: "prime.governance.lesson-harvest"
status: "CANONICAL_ACTIVE"
source_type: "PROTOCOL"
authority_class: "CANONICAL_AUTHORED_SOURCE"
owner_project: "Atlas"
owner_operation: "Source Governance"
protected_level: "HIGH"
---

# Atlas Lesson Harvest Protocol

Lesson Harvest preserves the user's semantic objective and turns verified,
reusable experience into enforced assurance without allowing evidence to
promote itself.

## Terms and singular roles

- A **full Atlas Sunset** is the lifecycle closeout transaction. It locks final
  known state, classifies source and inference, creates exactly one new sealed
  Feather, exactly one immutable Sunset bound to it, and exactly one Sunrise
  bound to the same pair, evaluates reusable lessons, and records recovery.
- A **continuity snapshot** is a compact read-only continuity view. The
  `tools.prime_continuity` command historically named `sunset` produces only
  that view; it is not a full Atlas Sunset and cannot claim lifecycle closeout.
- A **Feather** is exact-context evidence. It preserves the rich restart
  position and never becomes doctrine or current-state authority by itself.
- A **Golden Wing** is the sole reusable-lesson candidate. An observation,
  chat note, Feather, check result, or generated report is not a substitute.
- An **assurance control** is an ACTIVE or SUPERSEDED controlling rule in
  `governance/assurance-controls.json` with a real enforcement source and test.

## Harvest and absorption route

```text
Observation
→ exact Feather evidence
→ Golden Wing candidate when recurrence or a justified systemic exception exists
→ Noctua verification
→ Ares adversarial attack
→ human-controlled reviewed absorption
→ ACTIVE Aegis/Strikeforce assurance control
→ applicability disposition before Build
→ Strikeforce exact-head verification
```

Lessons never self-promote. Creating or advancing a Golden Wing, passing CI,
or receiving GREEN cannot add doctrine, alter an assurance control, authorize
Build, or authorize permanence. A lesson is absorbed only when a reviewed
source transaction creates or revises a real control whose enforcement and
regression proof are both present.

## Applicability before Build

Before Build, preserve the user's semantic objective and compare it to every
ACTIVE control's `applies_when` rule. Record exactly one disposition for every
matching active control:

- `APPLIED`, with the exact enforcement and evidence used; or
- `NOT_APPLICABLE`, with an exact objective-specific reason.

Missing controls, omitted matching controls, an unknown semantic objective,
unknown applicability, or a blank/generic `NOT_APPLICABLE` reason fails closed.
SUPERSEDED controls never compete with their named successor. Applicability
review creates no authority; it is an Aegis prerequisite for the separately
authorized Build route.

## Semantic route reconciliation

Route from meaning, not a shared command name:

| Semantic objective | Exact route | Prohibited substitution |
|---|---|---|
| Complete the full Atlas lifecycle closeout | `lifecycle/lifecycle-contract.md` and `python -B -m tools.atlas_lifecycle sunset candidate` | continuity snapshot |
| Render compact unfinished-work continuity | `python -B -m tools.prime_continuity.cli sunset --continuity-id ID` | claim of lifecycle Sunset completion |
| Preserve exact restart context | sealed Feather under the lifecycle contract | Golden Wing or generated summary |
| Propose a reusable lesson | Golden Wing candidate | direct doctrine/control edit without reviewed absorption |

When wording and apparent command names conflict, stop and reconcile the user's
semantic objective before mutation. Passing checks cannot cure a misleading
name, event ID, route, or claim.

## Strikeforce verification

Strikeforce rereads the exact candidate and verifies objective-to-route
alignment, applicable-control dispositions, enforcement-source presence,
Feather/Sunset/Sunrise cardinality when ASC-001 applies, non-promotion under
ASC-002, dependent canonical sources, exact-head checks, and truthful claims.
Any mismatch is YELLOW or RED; it is never waived by CI success.

Historical lifecycle v1 schemas and records remain unchanged. This protocol
adds assurance around their use and does not reinterpret or rewrite them.
