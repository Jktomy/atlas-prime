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
        self.recovery = (ROOT / "recovery/elantris-recovery.md").read_text(encoding="utf-8")
        self.covenant = (ROOT / "quests/prime-ascendant-covenant.md").read_text(encoding="utf-8")

    def test_topology_and_ram_arithmetic_are_exact(self) -> None:
        for text in (self.quest, self.infrastructure):
            self.assertIn("Harmony VM — 24 GB", text)
            self.assertIn("Atlas VM — 12 GB", text)
            self.assertIn("Plex LXC — 16 GB", text)
            self.assertIn("Protected Proxmox reserve — 8 GB", text)
            self.assertIn("Flexible headroom — 4 GB", text)
            self.assertIn("Total — 64 GB", text)
        self.assertNotIn("Crucible VM — 28 GB", self.quest)
        self.assertNotIn("Emberdark VM — 10 GB", self.quest)
        self.assertNotIn("Plex LXC — 12 GB", self.quest)
        self.assertNotIn("Nexus LXC —", self.quest)
        self.assertNotIn("Matrix LXC —", self.quest)

    def test_harmony_atlas_and_reserved_crucible_boundaries_are_exact(self) -> None:
        self.assertIn("## Campaign PF-C04 — Establish the Harmony Substrate", self.quest)
        self.assertIn("## Campaign PF-C05 — Establish the Atlas Substrate", self.quest)
        self.assertIn("`Crucible` is reserved", self.quest)
        self.assertIn("Harmony VM", self.artemis)
        self.assertIn("dedicated Atlas VM", self.artemis)
        self.assertIn("Emberdark, Coppermind, and Phoenix", self.artemis)
        self.assertIn("independently bounded", self.artemis)
        self.assertIn("GitHub remains canonical", self.quest)
        self.assertIn("Qdrant is a future option only after measured need is proven", self.artemis)
        self.assertNotIn("Build Crucible as", self.quest)
        self.assertNotIn("dedicated QEMU VM named the Emberdark VM", self.artemis)

    def test_plex_jellyfin_dvr_and_antenna_continuity_are_exact(self) -> None:
        combined = self.quest + self.infrastructure + self.recovery + self.covenant
        for marker in (
            "primary and only final-state Plex server",
            "Jellyfin — local-only continuity",
            "completed DVR",
            "direct antenna",
            "new and in-progress Plex recordings are not guaranteed",
            "shares no Plex application database",
            "no automatic failover",
            "metadata, artwork, cache, and transcode workspace remain on Prometheus local NVMe",
            "media and completed DVR",
            "safe unavailable-mount behavior",
        ):
            self.assertIn(marker, combined)
        self.assertNotIn("Forge Plex — cold standby", combined)
        self.assertNotIn("Jellyfin uses the Plex application database", combined)

    def test_support_sources_preserve_runtime_and_recovery_boundaries(self) -> None:
        self.assertIn("PostgreSQL full-text", self.infrastructure)
        self.assertIn("PostgreSQL base backups", self.recovery)
        self.assertIn("point-in-time recovery direction", self.recovery)
        self.assertIn("These are future proof requirements", self.recovery)
        self.assertIn("does not claim deployment", self.quest)
        self.assertIn("Prime Ascendant remains the application-semantics Quest", self.quest)
        self.assertIn("No Gitea installation", self.quest)
        self.assertIn("no ballooning and no memory overcommit", self.quest)
        self.assertIn("Plex playback and DVR recording outrank", self.infrastructure)

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
        self.assertEqual(bound["last_event_id"], "PF-PA-PROMETHEUS-CORE-TOPOLOGY-REFRACTION-R03")

        self.assertTrue((ROOT / "quests/prime-ascendant.md").exists())
        ascendant = next(item for item in board["entries"] if item["quest_id"] == "QUEST-PRIME-ASCENDANT-20260717")
        self.assertEqual(ascendant["source"], "quests/prime-ascendant.md")


if __name__ == "__main__":
    unittest.main()
