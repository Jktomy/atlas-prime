---
title: "Prime"
atlas_id: "prime.repository"
status: "CANONICAL_ACTIVE"
source_type: "BOOT"
authority_class: "CANONICAL_AUTHORED_SOURCE"
owner_project: "Project Codex"
owner_operation: "Operation Source Governance"
protected_level: "CRITICAL"
---

# Prime

`Jktomy/atlas-prime` is the sole canonical clean-source repository for Atlas.

```text
Prime: CANONICAL / ACTIVE
Thread Engine: ACTIVE / MISSION_SCOPED / DRAFT_PR_ONLY
Codex repository: FROZEN PREDECESSOR / ROLLBACK EVIDENCE
```

Start with `bootstrap.md`, then `routing/command-surfaces.md`.

Current operator and route architecture is documented in
`governance/athena-route-architecture-r01.md`.

```text
ATHENA
  Spear -> Thread Engine
  Sword -> Phoenix Blade -> GitHub transaction, no Thread Engine
  Aegis Break -> direct GitHub-native or other bounded safe route

JAYSON / ARTEMIS
  Arrow -> Bow -> Thread Engine

JAYSON
  Sword -> Oathbringer -> GitHub transaction, no Thread Engine
```

The generated-checkpoint publisher is post-merge infrastructure, not an operator
method. A non-generated push to `main` starts deterministic regeneration. Zero
delta is a successful no-op; a complete five-report delta invokes the singular
Thread Engine to create a generated-only draft PR and run exact-head Ubuntu and
Windows validation.

Prime contains current authored identity, governance, routing, Projects,
Operations, Quests, safety doctrine, recovery, infrastructure source,
generators, working command surfaces, and bounded generated projections.
Generated projections do not govern. Runtime packages do not prove deployment.
Private or regulated evidence remains in its approved system.

All durable source changes use exact source locks, a reviewed branch, and a draft
PR. Jayson's explicit in-chat authorization controls the exact approved Preview
or mission; separate permanence authority controls ready and merge. No external
origin bridge or platform attestation is required.
