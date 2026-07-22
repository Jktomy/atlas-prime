---
title: "Cloud Atlas Protected Realm Contract"
atlas_id: "prime.governance.cloud-atlas-protected-realm-r01"
status: "CANONICAL_SOURCE_ARCHITECTURE"
source_type: "PROTOCOL"
authority_class: "CANONICAL_AUTHORED_SOURCE"
owner_project: "Project Artemis"
owner_operation: "Operation Harmony"
protected_level: "CRITICAL"
private_boundary: "Public-clean classes, authority rules, schemas, and sanitized evidence pointers only. No protected content, secrets, private locations, network values, credentials, or runtime facts."
---

# Cloud Atlas protected realm contract

Cloud Atlas is Atlas's protected private realm, not a Project, Quest, database,
host, or deployment claim. Prime Ascendant owns its architecture. The normative
machine-readable authority and denial matrix is
`governance/cloud-atlas-protected-realm-v1.json`, validated by
`schemas/cloud-atlas-protected-realm-v1.schema.json`.

## Data-class and provenance boundary

Every object is classified as exactly one of: protected original, extracted
representation, structured record, sanitized summary, public-clean export,
derived index or embedding, audit receipt, or protected pointer. Originals are
byte-preserved and authoritative. Extracted, structured, indexed, embedded, and
summarized forms are distinct derivatives; none silently becomes the original.
Every derivative binds the original's opaque identity, transform identity,
source version, producing authority, timestamp, integrity digest, and current
classification. Sanitization is an explicit, receipted transform, never an
assumption based on file type or destination.

Prime may contain only public-clean exports, sanitized summaries, audit
receipts, and non-resolving protected pointers permitted by source policy.
Protected pointers carry no credential, private location, or reconstructable
protected content.

## Service authority matrix

| Service | May read/write | Never receives |
|---|---|---|
| Protected Original Vault | Byte-preserved originals through separately approved protected authority | Prime placement, silent normalization, direct VS Code mount, unrestricted model or SQL access |
| Coppermind | Approved extracted/structured records and provenance-bound derived indexes; PostgreSQL, full-text search, and `pgvector` are the initial direction | Canonical doctrine, unrestricted vault access, secret custody, direct client SQL |
| Emberdark | Governed workflow/transit/Mission state, authorization, quarantine, idempotency, retries, reconciliation, controlled exports, and receipts | Canonical-source or automatic-permanence authority |
| Harmony | Bounded retrieved context for synthesis and interpretation | Database, canonical-source, secret-store, or unrestricted-vault identity |
| Phoenix | Public-clean exports and explicitly sanitized packets for reviewed source candidates | Protected originals, secrets, automatic merge, or vault access through host co-location |
| Approved secret system | Scoped secret custody and delivery | Prime, Coppermind records, logs, or model exports |

All access is deny-by-default, least-privilege, identity-bound, time- and
Mission-bounded where applicable, and auditable. A browser, model, VS Code
client, automation, worker, database role, or co-located service receives no
unrestricted SQL, vault, secret, source, infrastructure, recovery, READY, or
merge authority.

## Export and Phoenix separation

An export declares source classification, destination classification,
transform, allowed fields, provenance, integrity digest, expiry when relevant,
and receipt identity. Ambiguous or failed classification is quarantined.
Public-clean output must not reconstruct protected content. Phoenix accepts
only public-clean or explicitly sanitized packets and never follows a protected
pointer. Co-location cannot collapse Phoenix, Coppermind, Emberdark, the vault,
or secret-system identities.

## Backup, restore, and degraded operation

Cloud Atlas requires complete and selective-service backup, complete and
selective restore, integrity validation, provenance validation, and recovery
receipts. These requirements are `REQUIRED_UNPROVEN`; source architecture is
not restore proof. Forge is an approved encrypted recovery destination, not the
primary protected runtime.

- Without Coppermind, use canonical Prime and approved original sources only;
  derived retrieval is unavailable or explicitly stale.
- Without Emberdark, do not execute or replay workflow mutations; preserve one
  resumable request identity for later reconciliation.
- Without Harmony, protected synthesis is unavailable and fails closed.
- Without Phoenix, canonical source remains readable; source mutation waits.
- Without Forge, do not claim backup completeness or recoverability.
- Without the Original Vault, originals are unavailable; derivatives never
  impersonate them.

Recovery restores one service at a time when possible, verifies identity and
provenance before exposure, and proves both selective and complete restoration
before activation. A restore never grants broader access than the pre-failure
service identity.

## Acceptance and stop boundary

Mission #279 establishes architecture only. PostgreSQL, `pgvector`, Cloud
Atlas, Gitea, storage, networks, backups, secrets, and protected imports remain
unactivated. PA-C01 and all later Campaign, runtime, infrastructure, repository
platform, READY, and MERGE gates remain unchanged. Rollback is a reviewed
revert or repair-forward transaction; protected-boundary ambiguity fails closed.
