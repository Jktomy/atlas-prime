---
title: "Atlas Prime Source File Template"
atlas_id: "atlas-prime.template.source-file"
format_version: "1.0"
status: "PROPOSED"
source_type: "TEMPLATE"
authority_class: "TOOL_CONTRACT"
owner_project: "Codex"
owner_operation: "Source Governance"
canonical_scope: "Reusable template for authored Atlas Prime Markdown files governed by the source-metadata v1 contract."
protected_level: "HIGH"
routes_from:
  - "README.md"
  - "specs/atlas-prime/repository-format-v1.md"
routes_to:
  - "schemas/source-metadata/source-metadata-v1.schema.json"
private_boundary: "Use only clean source, clean summaries, redacted examples, or clean pointers. Never place raw protected evidence in an authored source file."
evidence_boundary: "Original evidence remains authoritative in its approved external system. This template provides structure for clean Atlas source."
supersedes: []
superseded_by: []
cleanup_path: "Version this template when the source-metadata contract changes. Existing files migrate through an explicit metadata or content update."
last_verified: "2026-06-21"
---

# Atlas Prime Source File Template

Copy the fenced block into a new authored Markdown file and replace every placeholder. Do not copy placeholder brackets into governing source.

```markdown
---
title: "<human-readable title>"
atlas_id: "<stable.unique.atlas-id>"
format_version: "1.0"
status: "DRAFT"
source_type: "<allowed source type>"
authority_class: "<allowed authority class>"
owner_project: "<Atlas Project>"
owner_operation: null
canonical_scope: "<what this file governs or preserves>"
protected_level: "HIGH"
routes_from:
  - "<repository-relative inbound route>"
routes_to:
  - "<repository-relative outbound route>"
private_boundary: "<what private or protected material must not enter this file>"
evidence_boundary: "<which original evidence source remains authoritative>"
supersedes: []
superseded_by: []
cleanup_path: "<keep, merge, supersede, retire, regenerate, or archive path>"
last_verified: null
---

# <Title>

## Purpose

State why this file exists and the problem it solves.

## Authority and scope

State:

- what this file governs;
- what it does not govern;
- whether it is canonical, continuity, generated, migration, historical, contract, implementation, or pointer material;
- the source order that controls conflicts.

## Required rules

List normative rules in testable language.

## Routes and dependencies

Identify:

- inbound routing surfaces;
- outbound dependencies;
- related Projects and Operations;
- schemas, policies, generators, or evidence sources required.

## Private and evidence boundary

State what must remain outside GitHub and where original evidence remains authoritative.

## Verification

Define:

- syntax or schema checks;
- route checks;
- expected readback;
- Noctua checks;
- any proof needed before status changes.

## Failure and stop conditions

State conditions that block action, require Jayson, or force capture-only treatment.

## Cleanup, supersession, or retirement

State how this file can be merged, superseded, retired, regenerated, or retained historically without silent loss.

## Change log

### YYYY-MM-DD — <change>

- <what changed>
- <what did not change>
- <verification>
```

## Template rules

- `atlas_id` is stable and unique.
- Use repository-relative paths only.
- Root bootstrap files may have an empty `routes_from`; other governing files normally require an inbound route.
- `last_verified` remains `null` until the file and its routes are actually checked.
- `status: ACTIVE` requires a real approval and merge history.
- `status: SUPERSEDED` requires a non-empty `superseded_by` route.
- `status: GENERATED` is reserved for deterministic projections and requires `authority_class: GENERATED_OPERATIONAL_PROJECTION`.
- Do not use the template to bypass a schema, policy, Preview → Execute, migration, automation, protected-source, or merge gate.
