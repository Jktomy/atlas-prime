import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class MissionControlInteractionTests(unittest.TestCase):
    def test_mission_control_contract_is_mobile_first_and_truthful(self) -> None:
        text = (ROOT / "governance" / "mission-control-interaction-contract.md").read_text(encoding="utf-8")
        self.assertIn("absolute bottom", text)
        self.assertIn("at most four numbered options", text)
        self.assertIn("Option 1 is always", text)
        self.assertIn("own copy-paste command", text)
        self.assertIn("Planned actions must be labeled as plans", text)
        self.assertIn("Current Position", text)
        self.assertIn("Next Safe Action", text)
        self.assertIn("Waiting On", text)

    def test_risk_scaled_strikeforce_and_pass_ceiling_are_bound(self) -> None:
        interaction = (ROOT / "governance" / "mission-control-interaction-contract.md").read_text(encoding="utf-8")
        strikeforce = (ROOT / "governance" / "atlas-strikeforce.md").read_text(encoding="utf-8")
        for text in (interaction, strikeforce):
            self.assertIn("Pass N of 5", text)
            self.assertIn("BLOCKED_RESUMABLE", text)
            self.assertIn("Preview Strikeforce", text)
            self.assertIn("Build Strikeforce", text)
        self.assertIn("Five attempts never", strikeforce)

    def test_ares_is_first_class_and_adversarial(self) -> None:
        text = (ROOT / "governance" / "ares.md").read_text(encoding="utf-8")
        self.assertIn("devil's advocate", text)
        self.assertIn("duplication", text)
        self.assertIn("why the plan may be", text)
        self.assertIn("grants no authority", text)

    def test_glass_codex_registers_new_surfaces(self) -> None:
        record = json.loads((ROOT / "governance" / "glass-codex-client-v1.json").read_text(encoding="utf-8"))
        for surface in ("MISSION_CONTROL", "DECISION_BOXES", "PREVIEWS"):
            self.assertIn(surface, record["surfaces"])
        contract = (ROOT / "governance" / "glass-codex-client-contract.md").read_text(encoding="utf-8")
        self.assertIn("Mission Control", contract)
        self.assertIn("Decision Boxes", contract)
        self.assertIn("governance/mission-control-interaction-contract.md", contract)


if __name__ == "__main__":
    unittest.main()
