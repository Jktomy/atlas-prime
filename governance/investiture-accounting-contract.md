---
title: "Found Silverlight Investiture Accounting Contract"
atlas_id: "prime.governance.investiture-accounting"
status: "CANONICAL_ACTIVE"
source_type: "PROTOCOL"
authority_class: "CANONICAL_AUTHORED_SOURCE"
owner_project: "Project Codex"
owner_operation: "Operation Source Governance"
owning_quest: "QUEST-FOUND-SILVERLIGHT-R01"
protected_level: "CRITICAL"
---

# Found Silverlight Investiture Accounting contract

Found Silverlight owns Investiture Accounting events, private ledgers,
sanitized summaries, and receipts. Prime-wide provider/runtime-to-Light
identity remains governed by
`governance/investiture-source-identity-contract.md`.

This contract defines accounting semantics only. It does not choose a private
storage location, activate a provider or runtime, assert token use, grant a
credential, select a work surface, authorize repository mutation, or confer
permanence.

## Canonical identities

One trusted provider/runtime-reported model token equals one BEU:

- OpenAI model tokens are `Spirallight`.
- Google model tokens are `Chromelight`.
- Atlas-controlled local-model tokens are `Emberlight`.

Total Investiture BEU is the arithmetic sum of non-overlapping entries in those
three Lights. The convention does not assert equal provider cost, tokenizer
behavior, quality, capability, intelligence, latency, or performance.

Provider, model, runtime, Atlas runtime-control status, work surface, route,
engine, credential principal, accounting Light, and permanence authority are
independent identities. A task using Codex, ChatGPT, Shardplate, Sword,
Oathbringer, or another surface cannot infer its provider, model, Light, or BEU.

## Measurement states

Every usage scope has exactly one current measurement state:

| State | Meaning | Countable |
|---|---|---|
| `MEASURED` | Trusted provider/runtime evidence completely covers the declared usage scope. | Yes |
| `PARTIAL` | Trusted evidence covers only a known subtotal of the declared usage scope. | Known subtotal only |
| `UNAVAILABLE` | No trusted evidence or authoritative category semantics are available. | No |
| `ZERO_MODEL` | The work is deterministically proven to have used no model. | Exactly zero |

`OBSERVED` may describe non-counting evidence but never emits BEU. `ESTIMATED`
is not an accepted accounting state and may not be converted into BEU.
Unreported or ambiguous token use is `UNAVAILABLE`, never inferred as zero.

Deterministic Python, PowerShell, compilation, validation, indexing, fixture
reconciliation, and other non-model work has no Light and consumes exactly zero
BEU. It is not Emberlight unless a separately evidenced Atlas-controlled local
model reports tokens.

## Exact non-overlap rule

Each countable provider usage scope chooses exactly one basis:

1. `AUTHORITATIVE_TOTAL` counts one trusted authoritative total. Input,
   output, cached, reasoning, and other subtypes are informational only.
2. `DISJOINT_LEAVES` counts one or more trusted categories whose evidence
   explicitly states they are mutually disjoint. Any parent total or
   overlapping subtype is informational only.

The same provider usage-scope identity, source receipt, event identity, replay
identity, category, or token may not be counted twice. A counted ancestor and a
counted descendant cannot coexist. Cached and reasoning categories are never
automatically added to input or output. Ambiguous overlap semantics make the
dependent value `UNAVAILABLE`.

Mixed-provider work uses separate usage entries and separate Lights. There is
no hybrid Light. A partial entry exposes only `known_beu_subtotal`; a complete
`total_investiture_beu` is unavailable whenever any included usage scope is
partial or unavailable.

## Event and lifecycle boundary

Only an exact `USAGE_REPORTED` event may contribute BEU. Task start, pause,
cooldown, resume, completion, Athena checkpoint, Gemstone, Arrow, Spear
readback, Phoenix Flare, and Sunset events may bind a usage receipt but never
recount it.

Every countable usage entry independently binds:

- provider and model identity, or an explicit unavailable state;
- runtime identity and Atlas runtime-control status;
- exact Light;
- unique provider usage-scope identity;
- private source-receipt SHA-256;
- category-semantics receipt SHA-256;
- the selected counting basis and computed BEU.

## Append-only ledger and replay boundary

The authoritative ledger is private and outside Prime. It uses an immutable
initialization manifest, one immutable hash-chained record per accepted event,
append-only operation receipts, and sanitized quarantine receipts. It has no
mutable authoritative total or index.

Every record binds its sequence, prior-record SHA-256, canonical event SHA-256,
unique event identity, unique request/replay identity, computed measurement,
and record SHA-256. Stale expected heads, duplicate events, duplicate usage
scopes, duplicate receipts, replay, malformed fields, and chain drift fail
closed. An exact replay after interruption is classified as already committed;
it is never appended again.

Malformed input quarantine records only a stable error code, byte count, and
input digest. Raw malformed input, prompts, responses, conversations, provider
exports, account records, credentials, and private paths never enter Prime or a
sanitized receipt.

## Storage, recovery, and rollback

The ledger implementation must require an explicit Jayson-selected external
store root. Prime supplies no default, does not invent its placement, rejects
repository-contained or escaping roots, and never emits the absolute path in a
receipt.

Recovery verifies the immutable chain and creates a new explicit ledger
generation from the last valid record. It references the prior generation and
last valid digest without truncating, deleting, or rewriting history. Rollback
repoints the external owner-managed selection to a prior verified immutable
generation. Backup placement, restore execution, and destructive canaries
remain separately authorized protected actions.

## Clean-source evidence

Prime may retain only public-clean schemas, code, fixtures, sanitized status,
opaque identifiers, SHA-256 digests, category semantics, booleans, permitted
clean pointers, and acceptance receipts. It must never retain raw usage
exports, conversations, prompts, account data, private storage locations,
credentials, tokens, private runtime facts, or protected evidence.

RP-C03 Chromelight provider/account evidence does not prove Google model-token
use and does not create accounting Chromelight. Its frozen legacy `stormlight`
field is historical compatibility data and is never rewritten or converted.

## Gates

The stable Found Silverlight lineage uses these gates:

- FS-C01-M01: `INVESTITURE_ACCOUNTING_DOCTRINE_ACCEPTED`;
- FS-C01-M02: `APPEND_ONLY_INVESTITURE_LEDGER_CONSTRUCTION_PROVEN`;
- FS-C01-M03: `INVESTITURE_RECEIPT_AND_LIFECYCLE_BINDING_PROVEN`;
- FS-C01-M04: `INVESTITURE_ACCOUNTING_LIVE_ACCEPTANCE_PROVEN`;
- FS-C01 Campaign: `INVESTITURE_ACCOUNTING_INDEPENDENTLY_PROVEN`.

Doctrine, schemas, deterministic tests, zero-model handling, honest unavailable
behavior, and partial-telemetry behavior cannot by themselves close the live
acceptance gate. That gate additionally requires a protected external store
selected by Jayson and one bounded real model task with trusted
provider/runtime usage and category-semantics evidence, followed by exact
append/readback and a sanitized summary receipt.

Google or local-model activation is not required merely to prove honest
`UNAVAILABLE` behavior.
