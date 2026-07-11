---
title: "Lifecycle Evidence Trust Roots"
atlas_id: "prime.lifecycle.trust-roots"
status: "CANONICAL_ACTIVE"
source_type: "PROTOCOL"
authority_class: "CANONICAL_AUTHORED_SOURCE"
owner_project: "Atlas"
owner_operation: "Source Governance"
protected_level: "CRITICAL"
---

# Lifecycle Evidence Trust Roots

This directory is reserved for independently authored expectations used by the
read-only lifecycle evidence verifier. A submitted archive, receipt, sidecar,
or transition bundle cannot create, replace, or select its own trusted facts.

Each trust root is a strict UTF-8 JSON object containing exactly:

- `schema_id`: `atlas.lifecycle.trust-root.v1`;
- `expected_subject_digest`: the independently expected archive SHA-256;
- `trusted_schema_digest`: the expected local receipt-schema SHA-256;
- `trusted_contract_digest`: the expected lifecycle-contract SHA-256.

Trust roots are ordinary canonical authored source: exact-base review, protected
boundary review, branch and draft PR, CI, Aegis, and merge readback apply. The
Level 1A engine never writes this directory. No live trust root is introduced by
G3-B; tests construct harmless temporary fixtures only.
