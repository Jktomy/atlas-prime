---
title: "Worldhopper Isolation and Sanitized Handoff Contract"
atlas_id: "prime.governance.worldhopper-isolation-handoff"
status: "CANONICAL_ACTIVE"
source_type: "PROTOCOL"
authority_class: "CANONICAL_AUTHORED_SOURCE"
owner_project: "Project Artemis"
owner_operation: "Operation Harmony"
protected_level: "CRITICAL"
routes_from:
  - governance/cloud-atlas-protected-realm-contract.md
  - governance/gemstone-evidence-lifecycle-contract.md
routes_to:
  - schemas/worldhopper-workspace-v1.schema.json
private_boundary: "Prime stores only public-clean isolation doctrine, synthetic fixtures, hashes, receipts, and denied-access proofs; no live credentials, network values, protected records, or provider workspaces."
---

# Worldhopper Isolation and Sanitized Handoff Contract

## 1. Purpose and authority

A Worldhopper is a replaceable, mission-bound worker that receives exactly one approved Worldhopper Gemstone and only the minimum tools required for one bounded purpose. Worldhopper status grants no standing Coppermind, Original Vault, private Glass Codex, Phoenix, repository, account, READY, or permanence authority.

A profile name, editor workspace, prompt, or model policy is not a security boundary. Isolation must be enforced independently across identity, credentials, process, extension host, filesystem, temporary storage, clipboard, caches, logs, crash reports, network, repositories, models, tools, and return routes.

## 2. Deny-by-default workspace

Each workspace binds one mission ID, attempt ID, worker identity, approved carrier ID and digest, purpose, creation time, expiry, allowed tools, allowed destinations, and explicit denied resources.

The default policy is no protected reachability and no ambient authority. The workspace receives:

- no Coppermind or Original Vault route;
- no protected pointer resolver;
- no Cloud Atlas database or private API credential;
- no standing Phoenix, Prime, GitHub, Gitea, shell, package-manager, or infrastructure credential;
- no unrestricted network, local-LAN discovery, credential forwarding, shared browser session, clipboard bridge, host filesystem mount, or persistent home directory;
- no access to another mission's files, caches, logs, models, or carriers.

A required exception must be separately authorized, mission-bound, time-limited, receipt-backed, and narrower than the denied baseline.

## 3. Execution and data isolation

Worldhopper execution uses an isolated process and extension/tool host. Temporary files, caches, logs, telemetry, crash reports, downloads, model context, and derived artifacts remain inside the bounded workspace and are destroyed or retained only by an explicit disposition.

Secrets cannot be placed in prompts, environment files, command history, clipboard, source trees, logs, or carriers. Credential identity must be distinct from Jayson, Athena, Harmony, Emberdark, TenSoon, Phoenix, or a protected service principal.

Network egress is destination allowlisted. Inbound connectivity is denied unless a separately authorized return endpoint is required. DNS, proxy, redirect, and download behavior remain bounded to the same allowlist.

## 4. Sanitized delivery

Emberdark validates the approved Worldhopper Gemstone before delivery. Delivery proves exact carrier ID, digest, recipient, purpose, allowed fields, excluded classes, expiry, and sanitization receipt.

The Worldhopper cannot resolve protected pointers or request omitted material. A missing field is not permission to fetch it. Provider-side retention, training, telemetry, and human-review exposure must be visible in the mission record and treated as external disclosure risk.

## 5. Expiry, revocation, and destruction

Workspace authority expires automatically at the earliest of mission completion, carrier expiry, credential expiry, explicit revocation, or the declared workspace deadline.

Revocation disables credentials, network routes, tools, and carrier access before any cleanup claim. Destruction then produces receipts for workspace storage, temporary files, caches, logs, clipboard state, credentials, and provider-side deletion requests where supported. Unsupported provider deletion is recorded as residual risk, not silently treated as destruction.

## 6. Return quarantine and verification

Every result returns only through `EMBERDARK_QUARANTINE_TENSOON_VERIFY`. Direct promotion into Coppermind, the Original Vault, Phoenix, Prime, a repository, or another Worldhopper is forbidden.

Return validation checks mission and attempt identity, carrier lineage, digest, expiry, malware/content policy where applicable, unknown fields, embedded credentials, protected pointers, private network/runtime values, unrestricted logs, replay, and unauthorized destinations. TenSoon independently verifies the sanitized result and exclusion proof before release.

A failed, ambiguous, stale, or unreadable result remains quarantined. It is not retried blindly and cannot inherit prior approval.

## 7. Provider and recovery independence

External providers remain visible, bounded, replaceable, and noncanonical. Provider outage or Worldhopper unavailability cannot block Cloud Atlas, Prime, original recovery, or Mission Board continuity.

Recovery reconstructs the workspace from its public-clean manifest, approved carrier identity, policy digest, tool and destination allowlists, expiry, revocation, destruction receipts, and return disposition. Recovery requires no active chat memory and no particular model or provider.

## 8. Completion proof

Worldhopper isolation is proven only when tests demonstrate denied protected access, closed identity and credential boundaries, filesystem and temporary-data isolation, bounded network egress, exact sanitized delivery, automatic expiry, revocation-before-destruction, receipt-backed cleanup, quarantine-only return, no self-promotion, provider visibility and replaceability, and model-independent recovery.