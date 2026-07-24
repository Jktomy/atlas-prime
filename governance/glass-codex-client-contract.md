---
title: "Glass Codex Client Contract"
atlas_id: "prime.governance.glass-codex-client-r03"
status: "CANONICAL_SOURCE_ARCHITECTURE"
source_type: "PROTOCOL"
authority_class: "CANONICAL_AUTHORED_SOURCE"
owner_project: "Project Codex"
owner_operation: "Operation Glass Codex"
protected_level: "CRITICAL"
---

# Glass Codex client contract

Glass Codex is a client-independent governed service under Prime Ascendant.
Governed Cloud Atlas services own authoritative state and expose stable,
versioned, least-privilege APIs. The first graphical client direction is a
first-party VS Code extension running natively on Apollo. VS Code is a cockpit,
not source truth; backend services and reusable UI components remain replaceable
and preserve a future Theia or standalone-client route.

The normative UI and authority record is
`governance/glass-codex-client-v1.json`, validated by
`schemas/glass-codex-client-v1.schema.json`.

## Views and two access lanes

The client presents Harmony, Coppermind search, exact source retrieval,
documents/evidence, Emberdark workflow state, Gemstones/provenance, Mission
Board, Mission Control, Decision Boxes, Previews, Phoenix state, approvals,
receipts, and read-only health.

Mission Control presents truthful live operational progress. Decision Boxes are
the mobile-first consequential-choice surface and remain at the bottom of their
message with at most four numbered, individually copyable options; option 1 is
the agent recommendation. Previews show the exact proposed change before
consequential Build or Execute. These surfaces follow
`governance/mission-control-interaction-contract.md` and grant no authority by
their presentation alone.

Exact lookup and structured search use direct governed APIs. Interpretation and
synthesis use Harmony. Neither lane lets the client bypass Emberdark mediation,
Cloud Atlas classification, source review, or human approval.

## Denied authority and retention

The extension receives no unrestricted SQL, direct vault mount, infrastructure,
recovery, permanence, direct canonical-write, secret, or monitoring authority.
A VS Code profile name is organization, not security isolation. Notum's Watch
and Sentinel retain monitoring authority; the client presents only bounded
read-only health. The source identity, minimized projection, freshness states,
denied actions, and failure independence for that view are governed by
`governance/notum-glass-codex-health-contract.md`; stale or last-known-good data
can never render as current.

Protected evidence never persists in repositories, ordinary logs, unmanaged
caches, or ordinary temporary directories. Any explicitly authorized bounded
client material has declared storage, expiry, revocation, cleanup, crash, and
failure behavior. Failed cleanup quarantines the client state and blocks reuse;
it never silently widens retention.

## Packaging, compatibility, and rollback

The future first-party package requires integrity verification or signing,
semantic versioning, a locally retained installer, staged Windows/Apollo and VS
Code compatibility tests, controlled updates, and a known-good rollback
package. Public Marketplace, Microsoft Remote Tunnels, and paid AI extensions
are not mandatory dependencies.

Apollo or VS Code failure removes the primary GUI only. Cloud Atlas services,
monitoring, and Prime clean-clone recovery continue; authoritative state is
never trapped inside the extension. Rollback disables or reinstalls the client
without reverting backend state.

Apollo commissioning, isolated Private/Engineering/Worldhopper environments,
independent Hermes administration, source continuity, remote-route failure,
Windows recovery, reinstall, and runtime proof follow
`governance/apollo-remote-operator-continuity-contract.md`. That source grants
no install, credential, endpoint, or remote-access authority.

## Ownership and stop boundary

Operation Glass Codex owns the client product. PA-C05 owns governed Cloud Atlas
API and integration architecture. Harmony owns interpretation, not exact lookup
or client authority. Phoenix owns reviewed canonical-source maintenance, not
client state. Mission #282 implements no extension, installs nothing on Apollo,
deploys no backend, and advances no runtime, infrastructure, PA-C05, repository
platform, READY, or MERGE gate.
