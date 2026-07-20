from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from tools.prime_continuity.engine import ContinuityError, plan_one_entry_update, sha256


ROOT = Path(__file__).resolve().parents[2]
EVENT_ID = "PF-PA-PROMETHEUS-CORE-TOPOLOGY-REFRACTION-R03"


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

    def test_continuity_advances_without_quest_promotion(self) -> None:
        self.assertGreaterEqual(self.register["register_revision"], 42)
        self.assertGreaterEqual(self.entry["revision"], 7)
        self.assertEqual(self.entry["quest_state"], "IN_PROGRESS")
        self.assertEqual(self.entry["campaign_id"], "PA-C01")
        self.assertIsNone(self.entry["mission_id"])
        self.assertEqual(self.entry["gate_id"], "PA-C01-COVENANT-REFINEMENT")
        self.assertIn("Operation Harmony", self.entry["current_position"])
        self.assertIn("Harmony VM", self.entry["current_position"])
        self.assertIn("Atlas VM", self.entry["current_position"])
        self.assertIn("Runtime", self.entry["current_position"])
        self.assertEqual(self.entry["last_event_id"], EVENT_ID)
        self.assertIn(EVENT_ID, self.register["event_ids"])
        for prohibited in ("change repository visibility", "awaits merge", "merge pr"):
            self.assertNotIn(prohibited, self.entry["next_action"].lower())

        replay = copy.deepcopy(self.register)
        with self.assertRaisesRegex(ContinuityError, "EVENT_REPLAY"):
            plan_one_entry_update(
                replay, self.board, self.identities,
                continuity_id=self.entry["continuity_id"],
                expected_register_sha256=sha256(replay),
                expected_entry_revision=self.entry["revision"],
                event_id=EVENT_ID,
                changes={"next_action": "replay rejected"},
            )

    def test_harmony_hybrid_role_is_surface_aware_and_frictionless(self) -> None:
        quest = (ROOT / "quests/prime-ascendant.md").read_text(encoding="utf-8")
        artemis = (ROOT / "operations/artemis-runtime-and-routing.md").read_text(encoding="utf-8")
        combined = quest + artemis
        for marker in (
            "Project Artemis is the owning durable domain, not a model identity",
            "Harmony/Sazed is Atlas's frictionless context",
            "governed retrieval-augmented generation",
            "OCR and intake normalization",
            "capability awareness",
            "In ChatGPT, Athena remains the primary intent, reasoning, and conversational lead",
            "In VS Code and other approved surfaces where Athena is absent",
            "must not create a second planning ceremony",
            "No separate Artemis-model identity",
            "No routine RAG, OCR, or capability-selection step creates a new approval gate",
        ):
            self.assertIn(marker, combined)
        for prohibited_claim in (
            "Artemis is the resident intelligence",
            "Harmony grants merge authority",
            "routine RAG requires Jayson approval",
            "PA-C01 is complete",
        ):
            self.assertNotIn(prohibited_claim, combined)

    def test_runtime_cutover_retirement_topology_and_settings_stay_closed(self) -> None:
        covenant = (ROOT / "quests/prime-ascendant-covenant.md").read_text(encoding="utf-8")
        quest = (ROOT / "quests/prime-ascendant.md").read_text(encoding="utf-8")
        for marker in (
            "PostgreSQL full-text search + pgvector",
            "Qdrant:\ndeferred until demonstrated need.",
            "Current routes remain until parity and recovery are proven",
            "repository-settings changes remain unauthorized",
            "Gitea cutover",
            "route retirement",
            "Harmony VM",
            "Atlas VM",
            "Jellyfin",
            "direct antenna",
        ):
            self.assertIn(marker, covenant)
        self.assertEqual(covenant.count("Qdrant:\ndeferred until demonstrated need."), 1)
        self.assertIn("**Runtime:** `NOT STARTED`", quest)
        self.assertIn("No Campaign, runtime state", quest)
        self.assertIn("GitHub remains canonical", covenant)
        self.assertIn("SELECTED SUBSTRATE DIRECTION", covenant)

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

    def test_normal_human_merge_boundary_replaces_ordinary_shardblade(self) -> None:
        covenant = (ROOT / "quests/prime-ascendant-covenant.md").read_text(encoding="utf-8")
        for marker in (
            "Normal human-merge boundary",
            "Jayson alone makes the candidate permanent",
            "Prime PR #___ is ready to merge.",
            "If any candidate byte changes after READY",
            "CONTRACT_ONLY_NOT_ACTIVATED",
        ):
            self.assertIn(marker, covenant)
        self.assertNotIn("Shardblade may mark that exact candidate ready and merge it", covenant)


if __name__ == "__main__":
    unittest.main()
