import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class PrometheusFireArchitectureRefractionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.quest = (ROOT / "quests/prometheus-fire.md").read_text(encoding="utf-8")
        self.infrastructure = (ROOT / "infrastructure/atlas-infrastructure-source.md").read_text(encoding="utf-8")
        self.artemis = (ROOT / "operations/artemis-runtime-and-routing.md").read_text(encoding="utf-8")
        self.recovery = (ROOT / "recovery/phoenix-recovery.md").read_text(encoding="utf-8")

    def test_topology_and_ram_arithmetic_are_exact(self) -> None:
        for text in (self.quest, self.infrastructure):
            self.assertIn("Crucible VM — 28 GB", text)
            self.assertIn("Nexus Living Memory VM — 10 GB", text)
            self.assertIn("Plex LXC — 12 GB", text)
            self.assertIn("Protected Proxmox reserve — 8 GB", text)
            self.assertIn("Flexible headroom — 6 GB", text)
            self.assertIn("Total — 64 GB", text)
        self.assertNotIn("Crucible VM — 20 GB", self.quest)
        self.assertNotIn("Nexus LXC —", self.quest)
        self.assertNotIn("Matrix LXC —", self.quest)
        self.assertNotIn("Permanent planned guests | 42 GB", self.quest)
        self.assertNotIn("Unassigned headroom | 14 GB", self.quest)

    def test_nexus_matrix_plex_and_qdrant_boundaries_are_exact(self) -> None:
        self.assertIn("## Campaign PF-C05 — Raise the Nexus Vessel", self.quest)
        self.assertIn("dedicated QEMU VM substrate", self.quest)
        self.assertIn("## Campaign PF-C06 — Close the Matrix Gate", self.quest)
        normalized_quest = " ".join(self.quest.split())
        self.assertIn("as removed from the active Prometheus baseline", normalized_quest)
        self.assertIn("application database, metadata, cache, and transcode workspace remain on Prometheus local NVMe", self.quest)
        self.assertIn("Qdrant deferred from Phase 1", self.quest)
        self.assertNotIn("Build the private Matrix / Element transport LXC", self.quest)
        self.assertIn("Nexus has no Matrix / Synapse / Element dependency", self.artemis)
        self.assertIn("Qdrant is a future option only after measured need is proven", self.artemis)

    def test_support_sources_preserve_runtime_and_recovery_boundaries(self) -> None:
        self.assertIn("Plex application database, metadata, artwork, cache, and transcode workspace", self.infrastructure)
        self.assertIn("PostgreSQL full-text", self.infrastructure)
        self.assertIn("PostgreSQL base backups", self.recovery)
        self.assertIn("point-in-time recovery direction", self.recovery)
        self.assertIn("These are future proof requirements", self.recovery)
        self.assertIn("does not claim deployment", self.quest)
        self.assertIn("Prime Ascendant is an official architecture-refinement Quest", self.quest)

    def test_identity_state_and_continuity_digest_are_preserved(self) -> None:
        board = json.loads((ROOT / "quest-board/quest-board-v1.json").read_text(encoding="utf-8"))
        entry = next(item for item in board["entries"] if item["quest_id"] == "QUEST-PROMETHEUS-FIRE-20260701")
        self.assertEqual(entry["source"], "quests/prometheus-fire.md")
        self.assertEqual(entry["state"], "IN_PROGRESS")
        self.assertEqual(entry["next_gate"], "PF-C01-M02 Preview — Preserve the Old Flame")

        continuity = json.loads((ROOT / "continuity/prime-continuity-register-r01.json").read_text(encoding="utf-8"))
        bound = next(item for item in continuity["entries"] if item["continuity_id"] == "CONT-PROMETHEUS-FIRE-R01")
        expected = hashlib.sha256((ROOT / bound["quest_source"]).read_bytes()).hexdigest()
        self.assertEqual(bound["quest_source_sha256"], expected)
        self.assertEqual(bound["quest_state"], "IN_PROGRESS")
        self.assertEqual(bound["campaign_id"], "PF-C01")
        self.assertEqual(bound["mission_id"], "PF-C01-M02")
        self.assertEqual(bound["gate_id"], "PF-C01-M02-PREVIEW")

        self.assertTrue((ROOT / "quests/prime-ascendant.md").exists())
        ascendant = next(item for item in board["entries"] if item["quest_id"] == "QUEST-PRIME-ASCENDANT-20260717")
        self.assertEqual(ascendant["source"], "quests/prime-ascendant.md")


if __name__ == "__main__":
    unittest.main()
