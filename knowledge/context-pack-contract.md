---
title: "Prime Context Pack Contract"
atlas_id: "prime.knowledge.context-pack-contract"
status: "ACTIVE"
source_type: "PROTOCOL"
authority_class: "CANONICAL_AUTHORED_SOURCE"
owner_project: "Project Codex"
owner_operation: "Operation Source Governance"
protected_level: "MEDIUM"
---

# Prime Context Pack Contract

A Context Pack is a read-only navigation aid bound to exact Prime source bytes. It may identify a subject, canonical source, routed dependencies, relevant safety doctrine, tools, lessons, checks, protected boundaries, and missing required source. It cannot replace current canonical readback.

## Required machine contract

A pack is UTF-8 JSON with:

- `format_version` equal to `1.0`;
- a nonempty `subject`;
- a nonempty `sources` list;
- one normalized repository-relative `path` and lowercase SHA-256 for every source.

Paths must be unique under case folding. Absolute paths, backslashes, empty segments, `.` and `..`, paths outside the repository, missing files, non-files, symlinks, malformed hashes, and duplicate JSON keys fail closed.

## Validity and invalidation

Run `python -B tools/context-packs/verify_context_pack.py --repo-root . --pack <pack.json>` from a clean Prime clone.

The pack is `CURRENT` only when every listed file exists as a regular in-repository file and its bytes match the declared SHA-256. Any mismatch or absence makes the entire pack `INVALIDATED`. An invalidated pack routes the caller back to canonical Prime source; it is never partially current and cannot be repaired by generated navigation.

## Authority and privacy

Context Packs are read-only. They never approve, merge, write, delete, deploy, restore, purchase, change networking, change repository settings, or promote an agent or model. They contain clean source paths and hashes only, never protected runtime contents, credentials, PHI, finance evidence, recovery secrets, or private values.

The verifier reports `action_authorized = false` and `canonical_readback_required = true` for both current and invalidated packs.
