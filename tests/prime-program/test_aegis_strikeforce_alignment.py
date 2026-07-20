from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class AegisStrikeforceAlignmentTests(unittest.TestCase):
    def test_aegis_is_athenas_shield_and_interface_improvement_layer(self) -> None:
        aegis = (ROOT / "governance/atlas-aegis.md").read_text(encoding="utf-8")
        self.assertIn("Aegis is Athena's shield", aegis)
        self.assertIn("improves Athena's interface with Jayson", aegis)
        self.assertIn("accepted lessons", aegis)
        self.assertIn("A lesson affects Aegis only after reviewed absorption", aegis)
        self.assertIn("Aegis is one of the three read-only Strikeforce disciplines", aegis)
        self.assertIn("Aegis cannot cure a false claim", aegis)

    def test_strikeforce_is_noctua_ares_and_aegis(self) -> None:
        strikeforce = (ROOT / "governance/atlas-strikeforce.md").read_text(encoding="utf-8")
        covenant = (ROOT / "quests/prime-ascendant-covenant.md").read_text(encoding="utf-8")
        self.assertIn("Strikeforce consists of Noctua, Ares, and Aegis", strikeforce)
        self.assertIn("Noctua verifies source, identity, evidence, paths, bytes, and claims", strikeforce)
        self.assertIn("Ares red-teams assumptions", strikeforce)
        self.assertIn("Aegis audits alignment", strikeforce)
        self.assertIn("Aegis is Athena's shield within Strikeforce", strikeforce)
        self.assertNotIn("→ Athena reconciles", strikeforce)
        self.assertIn("GREEN does not merge", strikeforce)
        self.assertIn("Strikeforce consists of Noctua, Ares, and Aegis", covenant)
        self.assertIn("→ Aegis audits and improves Athena's interface with Jayson", covenant)
        self.assertNotIn("Athena improves\n→ Noctua verifies", covenant)
        self.assertNotIn("Qdrant remains deferred until demonstrated need", covenant)

    def test_safety_and_core_sources_match_the_composition(self) -> None:
        safety = (ROOT / "safety/atlas-safety-doctrine.md").read_text(encoding="utf-8")
        core = (ROOT / "atlas-prime.md").read_text(encoding="utf-8")
        self.assertIn('owner_project: "Project Codex"', safety)
        self.assertIn('owner_operation: "Operation Source Governance"', safety)
        self.assertIn("Aegis is Athena's continuous shield", safety)
        self.assertIn("Strikeforce combines three cumulative read-only disciplines", safety)
        self.assertIn("Noctua, Ares, and Aegis", safety)
        self.assertIn("Aegis is Athena's shield", core)
        self.assertIn("Together Noctua, Ares, and Aegis form Strikeforce", core)
        self.assertIn("Jayson decides permanence", core)


if __name__ == "__main__":
    unittest.main()
