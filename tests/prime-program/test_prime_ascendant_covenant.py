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
        self.assertEqual(self.register["register_revision"], 35)
        self.assertEqual(self.entry["revision"], 3)
        self.assertEqual(self.entry["quest_state"], "IN_PROGRESS")
        self.assertEqual(self.entry["campaign_id"], "PA-C01")
        self.assertIsNone(self.entry["mission_id"])
        self.assertEqual(self.entry["gate_id"], "PA-C01-COVENANT-REFINEMENT")
        self.assertIn("PR #237 merged", self.entry["current_position"])
        self.assertIn("not the complete Atlas Sunset", self.entry["current_position"])
        self.assertIn("generated projections remain STALE", self.entry["current_position"])
        for prohibited in ("change repository visibility", "awaits merge", "merge PR #237"):
            self.assertNotIn(prohibited, self.entry["next_action"].lower())

        prior = copy.deepcopy(self.register)
        prior["register_revision"] = 34
        prior["event_ids"].remove("PA-C01-POST-237-RECONCILIATION-R01")
        prior_entry = next(item for item in prior["entries"] if item["continuity_id"] == self.entry["continuity_id"])
        prior_entry.update({
            "current_position": "Prime Ascendant remains in PA-C01 architecture refinement. PR #236 merged at a02e048209ec3e5f9f329c8772440bc4f728e652, making PR validation fail-closed and path-targeted while removing automatic generated publishing on main pushes. Generated projections remain STALE, the repository remains public, and no runtime, infrastructure, cutover, or route-retirement authority was granted.",
            "blockers": [
                "PA-C01 covenant acceptance remains unproven.",
                "The architecture decisions listed in the Quest source remain unresolved by design.",
                "Private visibility remains a separate Jayson-controlled repository-settings action after this continuity-only validation proof.",
            ],
            "next_action": "Use this one-entry Sunset continuity transaction to prove that an ordinary continuity change runs the mandatory Ubuntu baseline plus Prime program validation while the Windows companion is skipped. After exact-head GREEN and a separately authorized merge, change repository visibility to private and verify it independently.",
            "next_approval": "Jayson must separately authorize merge of the unchanged Sunset candidate, then separately perform the private-visibility settings action; no runtime or infrastructure authority is included.",
            "revision": 2,
            "last_event_id": "PA-C01-HOSTED-ACTIONS-SUNSET-R01",
        })
        changes = {
            key: self.entry[key]
            for key in ("current_position", "blockers", "next_action", "next_approval")
        }
        planned = plan_one_entry_update(
            prior, self.board, self.identities,
            continuity_id=self.entry["continuity_id"],
            expected_register_sha256=sha256(prior),
            expected_entry_revision=2,
            event_id="PA-C01-POST-237-RECONCILIATION-R01",
            changes=changes,
        )
        self.assertEqual(planned, self.register)

        replay = copy.deepcopy(self.register)
        with self.assertRaisesRegex(ContinuityError, "EVENT_REPLAY"):
            plan_one_entry_update(
                replay, self.board, self.identities,
                continuity_id=self.entry["continuity_id"],
                expected_register_sha256=sha256(replay),
                expected_entry_revision=self.entry["revision"],
                event_id="PA-C01-POST-237-RECONCILIATION-R01",
                changes={"next_action": "replay rejected"},
            )

    def test_runtime_cutover_retirement_topology_and_settings_stay_closed(self) -> None:
        covenant = (ROOT / "quests/prime-ascendant-covenant.md").read_text(encoding="utf-8")
        for marker in (
            "PostgreSQL full-text search + pgvector",
            "Qdrant remains deferred",
            "Current routes remain until parity and recovery are proven",
            "repository-settings changes remain unauthorized",
            "Gitea cutover",
            "route retirement",
        ):
            self.assertIn(marker, covenant)
        self.assertIn("Runtime is not started", covenant)


if __name__ == "__main__":
    unittest.main()
