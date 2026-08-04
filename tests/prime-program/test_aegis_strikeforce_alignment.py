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

    def test_open_sky_is_complete_mandatory_and_blocks_green_on_material_violation(self) -> None:
        doctrine = (ROOT / "governance/open-sky-doctrine.md").read_text(encoding="utf-8")
        aegis = (ROOT / "governance/atlas-aegis.md").read_text(encoding="utf-8")
        strikeforce = (ROOT / "governance/atlas-strikeforce.md").read_text(encoding="utf-8")
        safety = (ROOT / "safety/atlas-safety-doctrine.md").read_text(encoding="utf-8")
        autonomy = (ROOT / "governance/atlas-autonomy-and-adaptation-contract.md").read_text(encoding="utf-8")
        mission_control = (ROOT / "governance/mission-control-interaction-contract.md").read_text(encoding="utf-8")
        process = (ROOT / "governance/repository-process-contract.md").read_text(encoding="utf-8")
        aegis_break = (ROOT / "governance/aegis-break-primary-route-contract.md").read_text(encoding="utf-8")
        commands = (ROOT / "routing/command-surfaces.md").read_text(encoding="utf-8")
        preview = (ROOT / "templates/preview-bundle-template.md").read_text(encoding="utf-8")

        self.assertIn("# The Open Sky Doctrine", doctrine)
        self.assertIn("> **Build the runway, not the cage.**", doctrine)
        normalized_doctrine = " ".join(doctrine.split())
        for principle in (
            "Freedom by default",
            "Proportional safety",
            "Infrastructure before restriction",
            "Simplicity and efficiency",
            "Consistency compounds",
        ):
            self.assertIn(principle, doctrine)
        self.assertIn("The Open Sky Doctrine is not optional advice", doctrine)
        self.assertIn("applied during every full Strikeforce pass", doctrine)
        self.assertIn("must not be GREEN while a material Open Sky violation remains unresolved", normalized_doctrine)
        self.assertIn("Unnecessary complexity, unnecessary restriction, duplicated safety", doctrine)
        for basis in (
            "a current canonical invariant",
            "a defined consequence gate",
            "a protected-data boundary",
            "a credible identified failure mode",
            "an evidence-backed recovery or rollback requirement",
            "an exact authority boundary",
            "a concrete risk specific to the reviewed object",
        ):
            self.assertIn(basis, doctrine)

        for dependent in (aegis, strikeforce, safety, autonomy, mission_control, process, aegis_break, commands):
            self.assertIn("governance/open-sky-doctrine.md", dependent)
        self.assertIn("mandatory Open Sky review", aegis)
        self.assertIn("Every full Strikeforce pass includes the mandatory Open Sky evaluation", strikeforce)
        self.assertIn("A material unresolved Open Sky violation prevents GREEN", strikeforce)
        self.assertIn("Open Sky: RUNWAY", mission_control)
        self.assertIn("Open Sky: CAGE", mission_control)
        self.assertIn("Open Sky: [RUNWAY / CAGE finding", preview)

    def test_open_sky_preserves_genuine_boundaries_without_new_enforcement_machinery(self) -> None:
        doctrine = (ROOT / "governance/open-sky-doctrine.md").read_text(encoding="utf-8")
        process = (ROOT / "governance/repository-process-contract.md").read_text(encoding="utf-8")
        self.assertIn("does not authorize Aegis to rewrite an object during Strikeforce", doctrine)
        self.assertIn("convert missing evidence into GREEN", doctrine)
        self.assertIn("Jayson-controlled permanence", doctrine)
        self.assertIn("More steps never become safer merely by existing", process)


if __name__ == "__main__":
    unittest.main()
