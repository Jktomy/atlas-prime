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

    def test_repairing_prime_is_admitted_without_changing_independent_quests(self) -> None:
        board = json.loads((ROOT / "quest-board/quest-board-v1.json").read_text(encoding="utf-8"))
        repairing_prime = [
            item
            for item in board["entries"]
            if item["quest_id"] == "QUEST-REPAIRING-PRIME-R01"
        ]
        self.assertEqual(
            repairing_prime,
            [
                {
                    "next_gate": "Generated-current readback after AJ-12 acceptance, then CAP-027 and RP-C08 final capability reconciliation",
                    "owner": "Codex / Source Governance",
                    "quest_id": "QUEST-REPAIRING-PRIME-R01",
                    "readiness_basis": (
                        "AJ-01 through AJ-12 are PROVEN. AJ-12 is accepted from owner-authorized read-only "
                        "workflow run 29455372822 at exact merged main "
                        "043648a85cf581d7805355a71cc819fdb83e738b: Ubuntu job 87487269033 and Windows "
                        "job 87487269036 completed successfully with the complete Prime matrix and no repository "
                        "mutation. CAP-027 remains the sole STILL_MISSING capability pending separate final "
                        "capability reconciliation; RP-C08, Phoenix recovery, and Quest closeout remain open."
                    ),
                    "source": "quests/repairing-prime.md",
                    "state": "IN_PROGRESS",
                }
            ],
        )
        repairing_source = (ROOT / "quests/repairing-prime.md").read_text(encoding="utf-8")
        conservation = (ROOT / "governance/deterministic-conservation-contract.md").read_text(encoding="utf-8")
        for mission in (f"RP-C06-M{index:02d}" for index in range(1, 8)):
            self.assertIn(mission, repairing_source)
        self.assertIn("Former G4-E means only the construction layer", conservation)
        self.assertIn("Former G4-F means only the later live", conservation)
        self.assertIn("invokes only the singular Thread Engine", conservation)
        independent = {
            item["quest_id"]: (item["source"], item["state"], item["next_gate"])
            for item in board["entries"]
            if item["quest_id"] != "QUEST-REPAIRING-PRIME-R01"
        }
        expected_preserved = {
                "PRIME-REBORN-QUEST-R01": (
                    "quests/prime-reborn.md",
                    "COMPLETE",
                    "CLOSED",
                ),
                "QUEST-FOUND-SILVERLIGHT-R01": (
                    "quests/found-silverlight.md",
                    "IN_PROGRESS",
                    "FS-C01-M04 — Prove the Light",
                ),
                "QUEST-PROMETHEUS-FIRE-20260701": (
                    "quests/prometheus-fire.md",
                    "IN_PROGRESS",
                    "PF-C01-M02 Preview — Preserve the Old Flame",
                ),
                "QUEST-NOTUMS-WATCH-20260708": (
                    "quests/notums-watch.md",
                    "READY_FOR_JAYSON_EXECUTION_PACKAGE",
                    "NW-C01 readiness package and Jayson-side proof",
                ),
            }
        self.assertEqual(
            {identity: independent[identity] for identity in expected_preserved},
            expected_preserved,
        )
        self.assertEqual(
            independent["QUEST-PRIME-CONTINUITY-PROOF-R01"],
            (
                "quests/prime-continuity-proof.md",
                "READY_FOR_CAMPAIGN_1_PREVIEW",
                "PCP-C01-PREVIEW",
            ),
        )

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
        found_continuity = next(
            entry for entry in continuity["entries"] if entry["continuity_id"] == "CONT-FOUND-SILVERLIGHT-R01"
        )

        self.assertIn("Nexus, Kandra, AI governance", projects)
        self.assertIn("| Artemis | Nexus; Kandra; AI Governance; future Janus |", operations)
        self.assertNotIn("| Artemis | Nexus; Hermes;", operations)
        self.assertIn("## Kandra", artemis)
        self.assertIn("Hermes is reserved for the portable human-operated Atlas command endpoint", artemis)
        self.assertIn("Artemis, Kandra, Nexus", routes)
        self.assertIn("Apollo, Hermes, and Iris operator endpoints", routes)
        self.assertIn("| **Apollo** | Lenovo M720q |", infrastructure)
        self.assertIn("| **Hermes** | MacBook Pro |", infrastructure)
        self.assertIn("| **Iris** | iPad Pro |", infrastructure)
        self.assertIn("Forge retains the persistent Helios backend", infrastructure)
        self.assertIn("Apollo may host the on-demand, human-interactive Helios Control Deck", infrastructure)
        self.assertIn("Iris role: SOURCE_ACCEPTED / NONBLOCKING", prometheus)
        self.assertIn("Windows wipe: BLOCKED", prometheus)
        self.assertIn("Proxmox installation: BLOCKED", prometheus)
        self.assertIn("Mission FS-C03-M01 — Prove Hermes", found)
        self.assertNotIn("Mission FS-C03-M01 — Prove Apollo", found)
        self.assertNotIn("PENDING_BUILD_READBACK", proof)
        self.assertIn("Jktomy/atlas-prime#195", proof)
        self.assertIn("93def9d8f9716547de69e101bc44a5f896dad67d", proof)
        self.assertIn("the changing final REPAIR head is intentionally not self-embedded", proof)
        self.assertIn(
            "The ledger, receipts, lifecycle binding, recovery, rollback planning, exact-head CI, "
            "and canonical synthetic exercise are accepted",
            found_continuity["current_position"],
        )
        self.assertIn(
            "The future FS-C03 Seon macOS bridge vessel is Hermes; Apollo is no longer reserved for that bridge role.",
            found_continuity["current_position"],
        )

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
            "recovery/phoenix-recovery.md",
            "quests/repairing-prime.md",
            "tools/atlas-sword/engine/oathbringer_contract.py",
            "tools/build_index.py",
        )
        self.assertEqual([path for path in required if not (ROOT / path).is_file()], [])


if __name__ == "__main__":
    unittest.main()
