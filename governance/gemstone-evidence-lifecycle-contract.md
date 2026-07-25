---
title: "Gemstone Evidence Lifecycle Contract"
atlas_id: "prime.governance.gemstone-evidence-lifecycle"
status: "CANONICAL_ACTIVE"
source_type: "PROTOCOL"
authority_class: "CANONICAL_AUTHORED_SOURCE"
owner_project: "Project Artemis"
owner_operation: "Operation Harmony"
protected_level: "CRITICAL"
routes_from:
  - governance/cloud-atlas-protected-realm-contract.md
routes_to:
  - schemas/gemstone-carrier-v1.schema.json
  - recovery/elantris-recovery.md
private_boundary: "Prime stores only public-clean carrier doctrine, manifests, hashes, receipts, sanitization evidence, and protected:// pointers; original or derived protected bytes remain in approved private evidence systems."
---

# Gemstone Evidence Lifecycle Contract

## 1. Purpose and authority

A Gemstone is a bounded evidence carrier with immutable identity, provenance, classification, custody, validation, and recovery metadata. It never grants source, protected-data, runtime, account, READY, or permanence authority.

This contract governs three closed carrier classes:

1. `ORIGINAL` — binds byte-for-byte original evidence.
2. `WORKING` — contains derived extraction, OCR, classification, notes, or analysis while retaining immutable links to every original.
3. `WORLDHOPPER` — contains only recipient-bound sanitized information approved for one mission, worker, purpose, and expiry.

Encryption, key custody, password delivery, and cryptographic product selection remain a separate decision gate. A carrier may declare encryption as required or externally managed, but this contract selects no mechanism and stores no secret.

## 2. Immutable original rule

An Original Gemstone records the original object digest, byte length, media type, acquisition receipt, custody identity, and private evidence pointer. The original bytes are never normalized, rewritten, replaced by OCR, or embedded in Prime or Mission Board.

A byte change creates a new original identity. Derived text, thumbnails, metadata repair, redaction, or format conversion cannot overwrite or masquerade as the original.

## 3. Working Gemstones

A Working Gemstone lists every source original by carrier ID and digest. Every derived artifact records its method, tool identity, timestamp, output digest, confidence or limitation statement, and whether human verification occurred.

Working output is evidence, not canonical truth. Ambiguous extraction remains explicitly uncertain. A model or chat is never required to recover the original-to-derived graph.

## 4. Worldhopper Gemstones

A Worldhopper Gemstone is deny-by-default and binds exactly one mission, recipient identity, purpose, allowed fields, excluded classes, expiry, return route, and sanitization receipt.

It must contain no original bytes, protected pointers resolvable by the recipient, secrets, credentials, private network or runtime values, unrestricted logs, raw regulated records, or standing repository authority. Sanitization is proven by an allowlist plus an explicit excluded-content record; absence of a detector finding alone is insufficient.

Worldhopper output cannot self-promote. It returns through Emberdark quarantine, manifest and digest validation, malware/content checks where applicable, replay and expiry checks, and TenSoon verification before any destination accepts it.

## 5. Identity, provenance, and custody

Every carrier uses:

- schema version, carrier ID, carrier class, mission ID, attempt ID, and creation time;
- producer and credential-principal identities without impersonation;
- classification and approved private pointer semantics;
- SHA-256 content and manifest digests;
- source-carrier links and derivation receipts;
- custody events with append-only timestamps and actors;
- recipient, purpose, expiry, and return binding when applicable;
- validation, quarantine, sanitization, and destruction dispositions.

Carrier identity is immutable. A changed manifest or payload creates a new carrier and attempt; it never reuses prior validation or approval.

## 6. Fail-closed conditions

Reject and quarantine a carrier on duplicate or replay identity, stale base or expiry, digest mismatch, missing original link, unsafe path, contradictory classification, unknown field, tampering, ambiguous custody, unauthorized recipient, absent sanitization receipt, return-route mismatch, or protected-data leakage.

An unavailable validator, unreadable original, unavailable private evidence system, or ambiguous write result blocks the route. Never blindly retry or create a replacement carrier.

## 7. Storage and publication boundaries

Prime and Mission Board may store this doctrine, schemas, public-clean examples, immutable public identifiers, hashes, sanitized receipts, and bounded `protected://` pointers. They must not store original or working protected bytes, decryption material, private exports, or unrestricted logs.

Coppermind and the Original Vault remain separate protected systems. Phoenix receives only separately approved public-clean or sanitized packets. Worldhoppers receive no standing access to any protected system.

## 8. Recovery

Recovery begins from the manifest, payload digest, original private pointer, custody log, sanitization receipt, and return receipt. It must work without active chat memory or a particular model.

Original recovery proves byte digest and length. Working recovery reconstructs the complete derivation graph. Worldhopper recovery proves exact approved fields, exclusions, recipient, expiry, delivery, return quarantine, and final disposition.

## 9. Completion proof

A lifecycle implementation is proven only when tests demonstrate byte-preserving original identity, nonreplacement by OCR, deterministic manifest validation, replay/tamper rejection, sanitization allowlisting and exclusions, bounded Worldhopper return quarantine, public-clean publication, and model-independent recovery.
