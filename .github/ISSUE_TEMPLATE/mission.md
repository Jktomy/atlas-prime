---
name: Atlas Mission
about: Capture one public-clean Mission for intake, continuity, assignment, and restart
title: "Mission: "
labels: ""
assignees: ""
---

<!--
Mission Board records are public-clean coordination records. Never include secrets,
credentials, private network details, PHI, raw financial/legal/tax/insurance data,
account records, unrestricted logs, private exports, or real environment values.

The draft block cannot know its GitHub/Gitea Issue number before creation. After
creation, replace it or append one validated `atlas-mission-v1` comment bound to
the assigned number. Until that binding exists, the Issue is not an admitted
Mission. A worker must reconcile the Issue, every comment, current canonical
main, and any linked branch or PR before mutation.
-->

## Mission manifest

```atlas-mission-draft-v1
{
  "schema_version": "atlas.mission.v1",
  "repository": "Jktomy/atlas-prime",
  "issue_number": 0,
  "mission_id": "MISSION-REPLACE-ME-R01",
  "mission_type": "mission/research",
  "mission_state": "CAPTURED",
  "created_at": "2026-01-01T00:00:00Z",
  "updated_at": "2026-01-01T00:00:00Z",
  "objective": "Replace with one bounded objective.",
  "rationale_and_decisions": [],
  "owner": {"project": "Project Codex", "operation": "Operation Source Governance"},
  "relationships": {"quest": null, "campaign": null, "gate": null},
  "assigned_worker": "UNASSIGNED",
  "execution_identity": {"declared_worker": "UNASSIGNED", "credential_principal": "UNASSIGNED", "surface": "UNASSIGNED", "publisher": "UNASSIGNED"},
  "dependencies": [],
  "public_clean_boundary": {"classification": "PUBLIC_CLEAN", "sanitized_summary": "No protected material is present.", "protected_pointer": null},
  "acceptance_criteria": ["Replace with one objectively verifiable condition."],
  "next_safe_action": "Triage this Mission against current canonical source.",
  "effort_class": "UNKNOWN",
  "queue_behavior": "TERMINAL_ON_BLOCK",
  "canonical_source_status": "PHOENIX_PENDING",
  "source_binding": {"base_sha": null, "branch": null, "pull_request": null, "expected_head": null, "changed_paths": [], "changed_paths_digest": null, "merged_commit": null},
  "validation_review": {"validation_status": "NOT_STARTED", "review_status": "NOT_STARTED", "strikeforce_status": "NOT_RUN", "receipt_refs": []},
  "coppermind": {"status": "PENDING", "reference": null, "archive_timestamp": null, "archive_package": null},
  "completion_proof": [],
  "rollback": "Before merge, close the exact candidate PR. After merge, use one reviewed revert or repair-forward PR.",
  "attempt_id": "MISSION-REPLACE-ME-ATTEMPT-01"
}
```

## Human-readable context

Add only public-clean context that helps a worker understand the objective,
decisions, blockers, and next safe action. The validated manifest controls Mission
workflow state; merged Prime controls canonical doctrine.
