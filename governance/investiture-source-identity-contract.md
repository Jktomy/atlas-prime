---
title: "Prime Investiture Source Identity Contract"
atlas_id: "prime.governance.investiture-source-identity"
status: "CANONICAL_ACTIVE"
source_type: "PROTOCOL"
authority_class: "CANONICAL_AUTHORED_SOURCE"
owner_project: "Project Codex"
owner_operation: "Operation Source Governance"
protected_level: "CRITICAL"
---

# Prime Investiture source identity contract

This Prime-wide contract fixes model-token origin and identity boundaries.
Found Silverlight owns Investiture Accounting events, ledgers, summaries, and
receipts. This contract does not create a ledger, assert a measurement, or
advance an FS-C01 gate.

## Exact Lights and BEU convention

One trusted provider/runtime-reported model token equals one BEU. The exact
active human-facing Lights are:

| Provider/runtime origin | Accounting Light |
|---|---|
| OpenAI model token | `Spirallight` |
| Google model token | `Chromelight` |
| Atlas-controlled local-model token | `Emberlight` |

- 1 OpenAI model token = 1 BEU of Spirallight.
- 1 Google model token = 1 BEU of Chromelight.
- 1 Atlas-controlled local-model token = 1 BEU of Emberlight.

The convention does not assert equal provider cost, tokenizer behavior,
quality, capability, intelligence, latency, or performance.

Each accounted model token appears in exactly one non-overlapping entry and one
Light. Mixed-provider work uses separate entries. There is no hybrid Light and
no active alias with spaces. A provider/account/product label alone is not
trusted token evidence and cannot select a Light.

Total Investiture BEU is the arithmetic sum of all non-overlapping
Spirallight, Chromelight, and Emberlight entries.

Provider totals, input, output, cached, reasoning, and other subtype fields may
overlap. A record must choose either one trusted authoritative total or a
declared set of disjoint leaf categories. Informational overlapping subtypes
are never added again. Missing or ambiguous category semantics make the
dependent count `UNAVAILABLE`; they are never inferred as zero.

Deterministic non-model work has no Light and consumes exactly zero BEU. Python,
PowerShell, compilation, validation, indexing, fixture reconciliation, and
other deterministic work are not Emberlight unless a separately evidenced
Atlas-controlled local model actually produced reported tokens.

## Identity separation

Every use keeps these identities independent:

- human authorizer and operator;
- provider and model;
- runtime and Atlas runtime-control status;
- AI-assisted work surface;
- delivery route and launcher;
- repository engine and substrate;
- credential principal and token mode;
- exact candidate and permanence authority;
- accounting Light, measurement status, and evidence receipt.

No identity implies another. A Light grants no provider activation, account
access, runtime availability, route, engine, credential, capability, candidate
approval, or permanence authority. Shardplate and Shardblade are operational
concepts, never Lights.

## Stormlight compatibility and retirement

`Stormlight` is retired as the active accounting-system and model-source
identity name. New doctrine, schemas, writers, events, ledgers, and summaries
must use the exact current identities above and must not emit a `stormlight`
field.

Accepted RP-C03 and RP-C04 v1 schemas and evidence retain their literal
`stormlight` field and `CLOUD`, `LOCAL`, `HYBRID`, or `NONE` values as frozen
legacy compatibility formats. That field was a coarse source classifier. It is
not a token count, BEU value, current Light, provider activation, or safe basis
for automatic conversion. Historical records remain readable and are never
rewritten or backfilled.

The RP-C03 Chromelight campaign remains accepted provider/account evidence.
Its proper name and gate lineage do not prove Google token use and do not emit
accounting Chromelight. Only trusted reported Google model tokens do.

The Found Silverlight Quest's older Stormlight wording is superseded for
identity and accounting-name decisions by this contract. Its stable Quest and
FS-C01 lineage is modernized through
`governance/investiture-accounting-contract.md`, with the Quest Board and
Found Silverlight continuity digest updated atomically in the same authored
acceptance transaction.

## Evidence and privacy boundary

Unreported token use is `UNAVAILABLE`. Partial trusted telemetry may expose a
known subtotal only as partial, never as complete Investiture. Raw prompts,
conversations, account records, usage exports, credentials, private runtime
facts, and protected evidence stay outside Prime. Prime may retain only
sanitized identities, digests, category semantics, clean pointers, summaries,
and receipts permitted by the protected-source boundary.
