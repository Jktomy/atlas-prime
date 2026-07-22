from __future__ import annotations

import csv
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FINAL_STATUSES = {
    "MIGRATED",
    "MERGED_INTO_DESTINATION",
    "REMODELED_IN_PRIME",
    "REGENERATED_IN_PRIME",
    "ARCHIVED_IN_CODEX",
    "EXCLUDED_WITH_PROOF",
}


class PrimeProgramTests(unittest.TestCase):
    def test_disposition_ledger_is_terminal_and_complete(self) -> None:
        with (ROOT / "migration/source-disposition-ledger.csv").open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 525)
        self.assertEqual(len({row["source_path"] for row in rows}), 525)
        self.assertEqual({row["final_status"] for row in rows}, FINAL_STATUSES)
        required = (
            "source_blob_sha1",
            "source_class",
            "current_authority",
            "disposition",
            "prime_target",
            "reason",
            "migration_pr_or_ref",
            "migration_commit",
            "verification",
            "privacy_classification",
            "final_status",
        )
        for field in required:
            self.assertEqual([row["source_path"] for row in rows if not row[field].strip()], [], field)

    def test_prime_native_canonical_quest_board(self) -> None:
        board = json.loads((ROOT / "quest-board/quest-board-v1.json").read_text(encoding="utf-8"))
        self.assertEqual(board["canonical_repository"], "Jktomy/atlas-prime")
        self.assertEqual(board["predecessor_workboard_route"], "HISTORICAL_ONLY")
        self.assertEqual(board["state"], "CANONICAL_ACTIVE")
        self.assertEqual(next(item for item in board["entries"] if item["quest_id"] == "PRIME-REBORN-QUEST-R01")["state"], "COMPLETE")

    def test_repairing_prime_is_complete_without_changing_independent_quests(self) -> None:
        board = json.loads((ROOT / "quest-board/quest-board-v1.json").read_text(encoding="utf-8"))
        repairing_prime = next(item for item in board["entries"] if item["quest_id"] == "QUEST-REPAIRING-PRIME-R01")
        self.assertEqual(repairing_prime["state"], "COMPLETE")
        self.assertEqual(repairing_prime["next_gate"], "CLOSED")
        self.assertIn("Sunset PR #224", repairing_prime["completion_basis"])
        self.assertIn("generated publisher run 29536662886", repairing_prime["completion_basis"])
        repairing_source = (ROOT / "quests/repairing-prime.md").read_text(encoding="utf-8")
        conservation = (ROOT / "governance/deterministic-conservation-contract.md").read_text(encoding="utf-8")
        for mission in (f"RP-C06-M{index:02d}" for index in range(1, 8)):
            self.assertIn(mission, repairing_source)
        self.assertIn("CAP-027: RESTORED / ACTIVE", repairing_source)
        self.assertIn("0 STILL_MISSING", repairing_source)
        self.assertIn("FINAL WHOLE-QUEST STRIKEFORCE: GREEN", repairing_source)
        self.assertIn("PHOENIX RECOVERY: PROVEN / ACCEPTED", repairing_source)
        self.assertIn("NEXT GATE: CLOSED", repairing_source)
        self.assertIn("five Markdown inventory functions", conservation)
        self.assertIn("temporary storage", conservation)
        self.assertIn("Historical proof", conservation)
        self.assertIn("dormant compatibility", conservation)
        self.assertIn("no generated-only", conservation)
        independent = {
            item["quest_id"]: (item["source"], item["state"], item["next_gate"])
            for item in board["entries"]
            if item["quest_id"] != "QUEST-REPAIRING-PRIME-R01"
        }
        expected_preserved = {
            "PRIME-REBORN-QUEST-R01": ("quests/prime-reborn.md", "COMPLETE", "CLOSED"),
            "QUEST-FOUND-SILVERLIGHT-R01": ("quests/found-silverlight.md", "COMPLETE", "CLOSED"),
            "QUEST-PROMETHEUS-FIRE-20260701": ("quests/prometheus-fire.md", "IN_PROGRESS", "PF-C01-M02 Preview — Preserve the Old Flame"),
            "QUEST-NOTUMS-WATCH-20260708": ("quests/notums-watch.md", "READY_FOR_JAYSON_EXECUTION_PACKAGE", "NW-C01 readiness package and Jayson-side proof"),
            "QUEST-PRIME-ASCENDANT-20260717": ("quests/prime-ascendant.md", "IN_PROGRESS", "PA-C01 — Write the Covenant"),
        }
        self.assertEqual({identity: independent[identity] for identity in expected_preserved}, expected_preserved)
        self.assertEqual(independent["QUEST-PRIME-CONTINUITY-PROOF-R01"], ("quests/prime-continuity-proof.md", "READY_FOR_CAMPAIGN_1_PREVIEW", "PCP-C01-PREVIEW"))

    def test_prime_ascendant_is_architecture_refinement_only(self) -> None:
        source = (ROOT / "quests/prime-ascendant.md").read_text(encoding="utf-8")
        covenant = (ROOT / "quests/prime-ascendant-covenant.md").read_text(encoding="utf-8")
        artemis = (ROOT / "operations/artemis-runtime-and-routing.md").read_text(encoding="utf-8")
        board = json.loads((ROOT / "quest-board/quest-board-v1.json").read_text(encoding="utf-8"))
        quest = next(item for item in board["entries"] if item["quest_id"] == "QUEST-PRIME-ASCENDANT-20260717")
        self.assertEqual(quest["source"], "quests/prime-ascendant.md")
        self.assertEqual(quest["state"], "IN_PROGRESS")
        self.assertEqual(quest["next_gate"], "PA-C01 — Write the Covenant")
        for marker in (
            "Prime Ascendant — The Dawnshard Covenant",
            "ACTIVE — ARCHITECTURE REFINEMENT",
            "PA-C01 — Write the Covenant",
            "PA-C02 — Raise the Coppermind",
            "PA-C03 — Establish Emberdark",
            "PA-C04 — Shape the Dawnshard",
            "PA-C05 — Open Glass Codex",
            "PA-C06 — Crown Gitea",
            "PA-C07 — Awaken Harmony",
            "PA-C08 — Bind the Realms",
            "PA-C09 — Temper the Old Blades",
            "PA-C10 — Prove the Dawn",
            "**Runtime:** `NOT STARTED`",
            "**Canonical cutover:** `NOT AUTHORIZED`",
            "Project Artemis is the durable owning domain, not a model identity",
            "Harmony/Sazed's frictionless resident role",
            "In ChatGPT, Athena remains the primary intent, reasoning, and conversational lead",
            "no separate Artemis-model identity",
        ):
            self.assertIn(marker, source)
        self.assertIn("Harmony/Sazed is Atlas's frictionless context", artemis)
        self.assertIn("must not create a second planning ceremony", artemis)
        self.assertIn("No routine RAG, OCR, or capability-selection step creates a new approval gate", artemis)
        self.assertIn("prime-ascendant-covenant.md", source)
        self.assertEqual([path.name for path in ROOT.glob("quests/prime-ascendant-covenant*.md")], ["prime-ascendant-covenant.md"])
        for marker in (
            "Prime Reborn owns",
            "Prometheus's Fire owns",
            "PostgreSQL full-text search + pgvector",
            "Qdrant:\ndeferred until demonstrated need.",
            "PA-C01-DEC-001",
            "PA-C01-DEC-025",
            "Campaign ownership map",
            "Founding context and provenance",
            "Proven workflow lesson",
            "Shardblade is merge authority",
            "Goddess Mode is persistence through safe repair and alternate routes",
            "GREEN means the exact reviewed candidate is ready",
        ):
            self.assertIn(marker, covenant)
        self.assertEqual(covenant.count("Qdrant:\ndeferred until demonstrated need."), 1)

    def test_universal_mode_definitions_are_narrow_and_aligned(self) -> None:
        shardblade = (ROOT / "governance/shard-doctrine.md").read_text(encoding="utf-8")
        aegis = (ROOT / "governance/atlas-aegis.md").read_text(encoding="utf-8")
        strikeforce = (ROOT / "governance/atlas-strikeforce.md").read_text(encoding="utf-8")
        protocols = (ROOT / "operations/protocol-library.md").read_text(encoding="utf-8")
        self.assertIn("Shardblade is the bounded permanence executor", shardblade)
        self.assertIn("Shardblade is the separate authority that permits merging", shardblade)
        self.assertIn("Goddess Mode is bounded autonomous completion", aegis)
        self.assertIn("GREEN means the exact reviewed candidate is ready for the next authorized gate", strikeforce)
        self.assertIn("Shardblade is the\nseparate merge authority", strikeforce)
        self.assertIn("Shardblade** is the bounded permanence executor", protocols)
        self.assertIn("Campaign GREEN creates no authority", strikeforce)
        self.assertNotIn("Goddess Mode grants", aegis)
        for path in (
            "schemas/shardblade-campaign-warrant-v1.schema.json",
            "schemas/shardblade-campaign-stage-request-v1.schema.json",
            "schemas/shardblade-campaign-stage-receipt-v1.schema.json",
            "tools/agentic_warrants/campaign.py",
        ):
            self.assertTrue((ROOT / path).is_file(), path)

    def test_kandra_and_operator_endpoint_reconciliation_is_exact(self) -> None:
        projects = (ROOT / "projects/project-registry.md").read_text(encoding="utf-8")
        operations = (ROOT / "operations/operation-registry.md").read_text(encoding="utf-8")
        artemis = (ROOT / "operations/artemis-runtime-and-routing.md").read_text(encoding="utf-8")
        routes = (ROOT / "routing/command-surfaces.md").read_text(encoding="utf-8")
        infrastructure = (ROOT / "infrastructure/atlas-infrastructure-source.md").read_text(encoding="utf-8")
        prometheus = (ROOT / "quests/prometheus-fire.md").read_text(encoding="utf-8")
        found = (ROOT / "quests/found-silverlight.md").read_text(encoding="utf-8")
        proof = (ROOT / "proof/prometheus-fire/pf-c01-m01-mission-seal-r01.md").read_text(encoding="utf-8")
        continuity = json.loads((ROOT / "continuity/prime-continuity-register-r01.json").read_text(encoding="utf-8"))

        self.assertIn("Operation Harmony, Sazed/Harmony, Emberdark transit", projects)
        self.assertIn("| Artemis | Harmony; AI Governance |", operations)
        self.assertIn("| Codex | Source Governance; Document Pipeline; Protocol Library; Template Library; Archive/Index; Janus; Coppermind; Phoenix; Glass Codex |", operations)
        self.assertIn("| Elantris | Backup Matrix; Restore Runbook; Keystone; External Backup Targets; Recovery Drill/Proof |", operations)
        self.assertNotIn("| Artemis | Nexus;", operations)
        self.assertIn("## Harmony / Sazed resident-intelligence role", artemis)
        self.assertIn("## Kandra", artemis)
        self.assertIn("Project Artemis is the owning durable domain, not a model identity", artemis)
        self.assertIn("Hermes is reserved for the portable human-operated Atlas command endpoint", artemis)
        self.assertIn("Artemis, Harmony, Emberdark, Cognitive Shadows, Kandra, and Sazed", routes)
        self.assertIn("Apollo, Hermes, Iris, and Zeus operator endpoints", routes)
        self.assertIn("| **Apollo** | Lenovo M720q |", infrastructure)
        self.assertIn("| **Hermes** | MacBook Pro |", infrastructure)
        self.assertIn("| **Iris** | iPad Pro |", infrastructure)
        self.assertIn("| **Zeus** | Jayson’s iPhone |", infrastructure)
        self.assertIn("Forge retains the persistent Helios backend", infrastructure)
        self.assertIn("Apollo may host the on-demand, human-interactive Helios Control Deck", infrastructure)
        self.assertIn("Iris role: SOURCE_ACCEPTED / NONBLOCKING", prometheus)
        self.assertIn("Zeus role: SOURCE_ACCEPTED / NONBLOCKING", prometheus)
        self.assertIn("Windows wipe: BLOCKED", prometheus)
        self.assertIn("Proxmox installation: BLOCKED", prometheus)
        self.assertIn("Mission FS-C03-M01 — Prove Hermes", found)
        self.assertNotIn("Mission FS-C03-M01 — Prove Apollo", found)
        self.assertNotIn("PENDING_BUILD_READBACK", proof)
        self.assertIn("Jktomy/atlas-prime#195", proof)
        self.assertIn("93def9d8f9716547de69e101bc44a5f896dad67d", proof)
        self.assertIn("the changing final REPAIR head is intentionally not self-embedded", proof)
        self.assertNotIn("CONT-FOUND-SILVERLIGHT-R01", {entry["continuity_id"] for entry in continuity["entries"]})
        self.assertIn("FS-C03 successor: Prime Ascendant / Operation Harmony", found)
        self.assertIn("Apple Reminders remains authoritative", found)

    def test_prime_is_canonical_and_codex_is_predecessor_only(self) -> None:
        policy = json.loads((ROOT / "policies/repository-policy.json").read_text(encoding="utf-8"))
        self.assertEqual(policy["state"], "CANONICAL_ACTIVE")
        self.assertEqual(policy["canonical_repository"], "Jktomy/atlas-prime")
        self.assertEqual(policy["predecessor_repository"], "Jktomy/atlas-codex")
        self.assertEqual(policy["predecessor_role"], "FROZEN_PREDECESSOR_ROLLBACK_EVIDENCE")

    def test_required_program_surfaces_exist(self) -> None:
        required = (
            "safety/atlas-safety-doctrine.md",
            "governance/source-lifecycle.md",
            "governance/investiture-accounting-contract.md",
            "routing/command-surfaces.md",
            "projects/project-registry.md",
            "operations/operation-registry.md",
            "infrastructure/atlas-infrastructure-source.md",
            "recovery/elantris-recovery.md",
            "quests/repairing-prime.md",
            "quests/prime-ascendant.md",
            "quests/prime-ascendant-covenant.md",
            "proof/repairing-prime/rp-c08-final-whole-quest-strikeforce-reconciliation-r01.md",
            "proof/repairing-prime/rp-c08-phoenix-recovery-acceptance-r01.md",
            "proof/repairing-prime/rp-c08-phoenix-recovery-acceptance-r01.json",
            "proof/repairing-prime/rp-c08-final-repairing-prime-completion-r05.md",
            "tools/atlas-sword/engine/oathbringer_contract.py",
            "tools/build_index.py",
        )
        self.assertEqual([path for path in required if not (ROOT / path).is_file()], [])


if __name__ == "__main__":
    unittest.main()
