from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

class OdysseyCanonReconciliationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.autonomy = (
            ROOT / "governance/atlas-autonomy-and-adaptation-contract.md"
        ).read_text(encoding="utf-8")
        self.architecture = (
            ROOT / "governance/odyssey-hermes-native-architecture-contract.md"
        ).read_text(encoding="utf-8")

    def test_autonomy_is_broad_but_consequence_gated(self) -> None:
        for marker in (
            "Safety is a fence around consequential boundaries",
            "temporary bounded delegation",
            "sanitized Obsidian notes",
            "Protected",
            "Destructive",
            "Externally binding",
            "Materially costly",
            "Infrastructure",
            "Canonical or permanent",
        ):
            self.assertIn(marker, self.autonomy)
        self.assertIn("A fresh Jayson authorization is required", self.autonomy)
        self.assertIn("policy-matched Harmony sanitization may proceed autonomously", self.autonomy)

    def test_native_hermes_and_knowledge_realms_are_canonical_direction(self) -> None:
        for marker in (
            "Hermes-native-first rule",
            "Hermes Desktop as the primary conversational surface",
            "VS Code + Hermes integration",
            "Coppermind",
            "Harmony",
            "Obsidian",
            "OpenViking",
            "receives no Coppermind credential",
        ):
            self.assertIn(marker, self.architecture)

    def test_stable_node_roles_and_baseline_dispositions_are_recorded(self) -> None:
        for marker in (
            "96 GB target RAM",
            "protected/shared realm VM — 72 GB target",
            "Plex LXC — 8 GB maximum",
            "Apollo",
            "Forge",
            "Notum",
            "| Directus | Remove from baseline |",
            "| Mem0 | Remove from baseline |",
            "| LibreChat | Remove from baseline |",
            "| n8n | Remove from baseline |",
            "| Qdrant | Remove from baseline until measured need |",
            "| Gitea | Optional implementation-code repository only",
        ):
            self.assertIn(marker, self.architecture)

    def test_deferred_decisions_do_not_silently_activate(self) -> None:
        for marker in (
            "current Prime machine-permanence meaning remains unchanged",
            "Mission Board cutover to Hermes Kanban",
            "Prime or GitHub retirement",
            "unresolved Kandra",
            "sole-Forge recovery exception",
            "software, model, database, or operating-system versions",
            "exact runtime configuration",
        ):
            self.assertIn(marker, self.architecture)
        for forbidden in (
            "hermes kanban = sole writable mission authority",
            "github is retired",
            "forge is the sole durable backup",
            "openviking may read coppermind",
            "deployment is complete",
        ):
            self.assertNotIn(forbidden, self.architecture.casefold())

    def test_current_authority_and_no_runtime_claim_are_explicit(self) -> None:
        self.assertIn("Prime on GitHub = canonical", self.architecture)
        self.assertIn("GitHub Issues = active writable Mission Board", self.architecture)
        self.assertIn("source architecture, not implementation proof", self.architecture)
        continuity = json.loads(
            (ROOT / "continuity/prime-continuity-register-r01.json").read_text(encoding="utf-8")
        )
        self.assertIn("Mission #364", continuity["entries"][0]["current_position"])
        start = (ROOT / "atlas-start-here.md").read_text(encoding="utf-8")
        self.assertIn("odyssey-hermes-native-architecture-contract.md", start)

if __name__ == "__main__":
    unittest.main()
