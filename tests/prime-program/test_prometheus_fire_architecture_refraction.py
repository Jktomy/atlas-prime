import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class PrometheusFireArchitectureRefractionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.quest = (ROOT / "quests/prometheus-fire.md").read_text(encoding="utf-8")
        self.infrastructure = (
            ROOT / "infrastructure/atlas-infrastructure-source.md"
        ).read_text(encoding="utf-8")
        self.artemis = (
            ROOT / "operations/artemis-runtime-and-routing.md"
        ).read_text(encoding="utf-8")
        self.recovery = (
            ROOT / "recovery/elantris-recovery.md"
        ).read_text(encoding="utf-8")
        self.covenant = (
            ROOT / "quests/prime-ascendant-covenant.md"
        ).read_text(encoding="utf-8")
        self.odyssey = (
            ROOT / "quests/the-odyssey.md"
        ).read_text(encoding="utf-8")

    def test_topology_and_ram_arithmetic_are_exact_historical_baseline(self) -> None:
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

    def test_harmony_atlas_and_reserved_crucible_boundaries_are_preserved(self) -> None:
        self.assertIn(
            "## Campaign PF-C04 — Establish the Harmony Substrate",
            self.quest,
        )
        self.assertIn(
            "## Campaign PF-C05 — Establish the Atlas Substrate",
            self.quest,
        )
        self.assertIn("`Crucible` is reserved", self.quest)
        self.assertIn("Harmony VM", self.artemis)
        self.assertIn("dedicated Atlas VM", self.artemis)
        self.assertIn("Emberdark, Coppermind, and Phoenix", self.artemis)
        self.assertIn("independently bounded", self.artemis)
        self.assertIn("GitHub remains canonical", self.quest)
        self.assertIn(
            "Qdrant is a future option only after measured need is proven",
            self.artemis,
        )
        self.assertNotIn("Build Crucible as", self.quest)
        self.assertNotIn(
            "dedicated QEMU VM named the Emberdark VM",
            self.artemis,
        )

    def test_plex_jellyfin_dvr_and_antenna_continuity_are_preserved(self) -> None:
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
        self.assertNotIn(
            "Jellyfin uses the Plex application database",
            combined,
        )

    def test_support_sources_preserve_runtime_and_recovery_boundaries(self) -> None:
        self.assertIn("PostgreSQL full-text", self.infrastructure)
        self.assertIn("PostgreSQL base backups", self.recovery)
        self.assertIn("point-in-time recovery direction", self.recovery)
        self.assertIn("These are future proof requirements", self.recovery)
        self.assertIn("does not claim deployment", self.quest)
        self.assertIn(
            "Prime Ascendant remains the application-semantics Quest",
            self.quest,
        )
        self.assertIn("No Gitea installation", self.quest)
        self.assertIn("no ballooning and no memory overcommit", self.quest)
        self.assertIn(
            "Plex playback and DVR recording outrank",
            self.infrastructure,
        )

    def test_prometheus_lineage_is_preserved_but_odyssey_is_active(self) -> None:
        board = json.loads(
            (ROOT / "quest-board/quest-board-v1.json").read_text(
                encoding="utf-8"
            )
        )
        historical = next(
            item
            for item in board["entries"]
            if item["quest_id"] == "QUEST-PROMETHEUS-FIRE-20260701"
        )
        self.assertEqual(historical["source"], "quests/prometheus-fire.md")
        self.assertEqual(historical["state"], "IN_PROGRESS")

        registry = json.loads(
            (
                ROOT
                / "continuity/mission-board-quest-registry-r01.json"
            ).read_text(encoding="utf-8")
        )
        continuity = json.loads(
            (
                ROOT / "continuity/prime-continuity-register-r01.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(
            {item["quest_id"] for item in registry["entries"]},
            {"QUEST-THE-ODYSSEY-20260727"},
        )
        self.assertEqual(
            {item["quest_id"] for item in continuity["entries"]},
            {"QUEST-THE-ODYSSEY-20260727"},
        )
        self.assertIn("quests/prometheus-fire.md", self.odyssey)
        self.assertIn("Prometheus's Fire", self.odyssey)
        self.assertIn("preserved superseded history", self.odyssey)


if __name__ == "__main__":
    unittest.main()
