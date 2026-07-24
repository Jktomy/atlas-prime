---
title: "Mission Control and Decision Box Interaction Contract"
atlas_id: "prime.governance.mission-control-interaction-r01"
status: "CANDIDATE"
source_type: "PROTOCOL"
authority_class: "CANONICAL_AUTHORED_SOURCE"
owner_project: "Project Artemis"
owner_operation: "Operation Harmony"
protected_level: "HIGH"
---

# Mission Control and Decision Box interaction contract

Mission Control is the truthful, mobile-first live operations surface for substantial Atlas work. It reports only actual actions, confirmed results, current blocks, and exact approval gates. It never exposes private chain-of-thought, secrets, protected evidence, raw private logs, or unperformed steps.

## Mission Control stream

Use Mission Control for Mission work, repository operations, infrastructure changes, Sunset, recovery, validation, and other substantial tasks. Ordinary conversation and quick factual answers remain conversational.

Each stream identifies the Mission or bounded transaction, mode, Project or Operation lane, selected route, current phase, and current Strikeforce pass when applicable. Standard states are reading, analyzing, writing, testing, verifying, blocked, deferred, waiting on Jayson, and complete.

Planned actions must be labeled as plans. A write is not complete until readback confirms it. A blocked connector, ambiguous mutation result, stale identity, or unreadable evidence stops truthfully; simulated progress is forbidden.

Every substantial operation ends with:

- **Current Position**;
- **Next Safe Action**;
- **Waiting On**.

## Decision Boxes

A Decision Box is used only when an unresolved consequential choice remains. It appears at the absolute bottom of the user-facing message and nothing follows it.

A Decision Box has at most four numbered options. Option 1 is always Athena's or Harmony's recommendation. Every option states its lane and exact action, for example Preview Lane, Audit Lane, Verify Lane, Build Lane, Execute Lane, Sunset Lane, Defer Lane, or another precise bounded lane. Each option has its own copy-paste command. Jayson may reply with only the option number when the box is unambiguous.

Do not manufacture alternatives. When only one valid authorization exists, present one exact copy-paste command rather than false choices. A genuine do-nothing, defer, narrow-scope, change-task, or Sunset option may appear when useful.

A Decision Box is required when two or more viable paths have meaningful downstream consequences, when the choice changes architecture, cost, privacy, authority, recovery, permanence, or scope, or when Athena cannot safely infer Jayson's intent. It is not required for obvious safe next steps within an already approved bounded goal.

## Preview before consequential execution

Consequential durable or runtime work requires a user-visible Preview before Build or Execute. The Preview states the objective, exact scope, source authority, protected boundary, route, proof, stop condition, rollback, and next safe action. Preview, Build, Execute, READY, and permanence remain distinct.

For a source-changing Mission, the complete restart-safe Preview is appended to the Mission Board before branch or pull-request construction. Preview acceptance stores and confirms the plan only; it grants no Build authority. Build begins only after a later explicit Build Lane authorization. Before construction or reuse of an earlier candidate, the worker fresh-reads current Prime and live transaction state, checks for duplicates, and reconciles the stored Preview. Canonical drift, missing evidence, or changed scope returns to Preview rather than being silently inferred. This separation preserves a resumable plan across context, resource, connector, or session interruption.

Risk-scaled Strikeforce applies:

- consequential or complex work receives a full Preview Strikeforce and a full exact-head Build Strikeforce;
- ordinary low-risk reversible work receives a lighter Preview review and one full Build Strikeforce;
- immutable execution may use a fresh execution gate instead of repeating a full design review when bytes, digests, authority, and scope are unchanged.

## Strikeforce reporting

Every full Strikeforce cycle is reported as `Pass N of 5` and runs Noctua, then Ares, then Aegis against one exact object. Candidate changes invalidate prior exact-head Build Strikeforce results. After five non-GREEN passes, stop `BLOCKED_RESUMABLE` and ask Jayson for more information, narrowed scope, a changed approach, or abandonment. Five attempts never convert a defective plan into GREEN.

## Goddess Mode and Shardblade

Goddess Mode means continue through recoverable failures inside the exact approved goal: diagnose, repair candidate-caused failures, use safe authorized alternate routes, preserve valid partial results, and continue until success, a true decision gate, a safety stop, or a terminal fifth Strikeforce pass.

Shardblade means Jayson grants one exact candidate merge authority. It remains subject to exact-head checks, required status, review reconciliation, Strikeforce GREEN, replay protection, rollback, compare-and-swap, and canonical readback. Shardblade is not construction authority and cannot repair or substitute a candidate.

## Sunset learning

Every full Sunset Lesson Harvest includes an Aegis and Strikeforce improvement review: what Noctua missed, whether Ares attacked the right failure modes, whether Aegis solved or exposed every finding, whether the Decision Box and Mission Control interface were clear on mobile, how many Strikeforce passes were required, which pass became GREEN, and whether a regression or reviewed assurance-control improvement is required. Lessons never self-promote.
