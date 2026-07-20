from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from tools.prime_continuity.engine import ContinuityError, plan_one_entry_update, sha256


ROOT = Path(__file__).resolve().parents[2]


class PrimeAscendantCovenantReconciliationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.register = json.loads((ROOT / "continuity/prime-continuity-register-r01.json").read_text(encoding="utf-8"))
        self.board = json.loads((ROOT / "quest-board/quest-board-v1.json").read_text(encoding="utf-8"))
        self.identities = json.loads((ROOT / "continuity/quest-engine-identities-r01.json").read_text(encoding="utf-8"))
        self.entry = next(item for item in self.register["entries"] if item["continuity_id"] == "CONT-PRIME-ASCENDANT-R01")

    def test_historical_provenance_and_post_237_truth_are_explicit(self) -> None:
        covenant = (ROOT / "quests/prime-ascendant-covenant.md").read_text(encoding="utf-8")
        for marker in (
            "historical founding lineage",
            "Main immediately after the founding generated transaction",
            "PR #236 — minimize hosted Actions",
            "a02e048209ec3e5f9f329c8772440bc4f728e652",
            "PR #237 — targeted hosted-Actions continuity proof",
            "e95e13f8e7185bb50e773b2033d06f172d928f58",
            "did not execute the full Atlas Sunset for this chat",
            "created no lifecycle Feather",
            "Generated projections remain stale",
            "Runtime is not started",
        ):
            self.assertIn(marker, covenant)
        self.assertNotIn("| Current verified main |", covenant)

    def test_continuity_advances_one_entry_without_quest_promotion(self) -> None:
        self.assertEqual(self.register["register_revision"], 40)
        self.assertEqual(self.entry["revision"], 5)
        self.assertEqual(self.entry["quest_state"], "IN_PROGRESS")
        self.assertEqual(self.entry["campaign_id"], "PA-C01")
        self.assertIsNone(self.entry["mission_id"])
        self.assertEqual(self.entry["gate_id"], "PA-C01-COVENANT-REFINEMENT")
        self.assertIn("Operation Harmony", self.entry["current_position"])
        self.assertIn("Operation Coppermind", self.entry["current_position"])
        self.assertIn("Project Elantris", self.entry["current_position"])
        self.assertIn("Runtime is not started", self.entry["current_position"])
        self.assertEqual(self.entry["last_event_id"], "PA-C01-GITEA-PHOENIX-VALIDATION-AUGMENTATION-R01")
        self.assertLess(
            self.register["event_ids"].index("PA-C01-POST-237-RECONCILIATION-R01"),
            self.register["event_ids"].index("PA-C01-GITEA-PHOENIX-VALIDATION-AUGMENTATION-R01"),
        )
        for prohibited in ("change repository visibility", "awaits merge", "merge pr #237"):
            self.assertNotIn(prohibited, self.entry["next_action"].lower())

        replay = copy.deepcopy(self.register)
        with self.assertRaisesRegex(ContinuityError, "EVENT_REPLAY"):
            plan_one_entry_update(
                replay, self.board, self.identities,
                continuity_id=self.entry["continuity_id"],
                expected_register_sha256=sha256(replay),
                expected_entry_revision=self.entry["revision"],
                event_id="PA-C01-ATLAS-NAMING-REFRACTION-R01",
                changes={"next_action": "replay rejected"},
            )

    def test_runtime_cutover_retirement_topology_and_settings_stay_closed(self) -> None:
        covenant = (ROOT / "quests/prime-ascendant-covenant.md").read_text(encoding="utf-8")
        for marker in (
            "PostgreSQL full-text search + pgvector",
            "Qdrant:\ndeferred until demonstrated need.",
            "Current routes remain until parity and recovery are proven",
            "repository-settings changes remain unauthorized",
            "Gitea cutover",
            "route retirement",
        ):
            self.assertIn(marker, covenant)
        self.assertEqual(covenant.count("Qdrant:\ndeferred until demonstrated need."), 1)
        self.assertIn("Runtime is not started", covenant)

    def test_future_gitea_phoenix_validation_roles_are_bounded(self) -> None:
        quest = (ROOT / "quests/prime-ascendant.md").read_text(encoding="utf-8")
        covenant = (ROOT / "quests/prime-ascendant-covenant.md").read_text(encoding="utf-8")
        artemis = (ROOT / "operations/artemis-runtime-and-routing.md").read_text(encoding="utf-8")
        for marker in (
            "Gitea pull-request event",
            "Prime Integrity Cognitive Shadow",
            "immutable exact-base/exact-head validation carrier",
            "bounded Kandra integrity executor",
            "TenSoon exact-head verification",
            "Jayson-controlled permanence",
            "prime/integrity",
            "prime/windows-compatibility",
            "prime/generated-current",
        ):
            self.assertIn(marker, quest + covenant)
        for marker in (
            "It cannot judge",
            "receives no general or",
            "VERIFIED_FOR_ATHENA_AUDIT",
        ):
            self.assertIn(marker, artemis)
        for prohibited_claim in (
            "Gitea deployment is complete",
            "Gitea cutover is authorized",
            "PA-C01 is complete",
        ):
            self.assertNotIn(prohibited_claim, quest + covenant + artemis)


if __name__ == "__main__":
    unittest.main()
