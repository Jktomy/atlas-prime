import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def compact(text: str) -> str:
    return " ".join(text.split())


class MissionControlInteractionTests(unittest.TestCase):
    def test_mission_control_contract_is_mobile_first_and_truthful(self) -> None:
        text = compact((ROOT / "governance" / "mission-control-interaction-contract.md").read_text(encoding="utf-8"))
        self.assertIn("absolute bottom", text)
        self.assertIn("at most four numbered options", text)
        self.assertIn("Option 1 is always", text)
        self.assertIn("own copy-paste command", text)
        self.assertIn("Planned actions must be labeled as plans", text)
        self.assertIn("Current Position", text)
        self.assertIn("Next Safe Action", text)
        self.assertIn("Waiting On", text)

    def test_startup_trigger_prime_authority_and_memory_boundary(self) -> None:
        text = compact((ROOT / "governance" / "mission-control-interaction-contract.md").read_text(encoding="utf-8"))
        self.assertIn("Project instructions as the automatic trigger", text)
        self.assertIn("fresh read of current merged `Jktomy/atlas-prime`", text)
        self.assertIn("Merged Prime defines the exact interaction doctrine", text)
        self.assertIn("Saved memory is reminder-only", text)
        self.assertIn("If current Prime cannot be", text)
        self.assertIn("stop before consequential work", text)

    def test_decision_boxes_are_consequential_choice_only(self) -> None:
        text = compact((ROOT / "governance" / "mission-control-interaction-contract.md").read_text(encoding="utf-8"))
        self.assertIn("used only when an unresolved consequential choice remains", text)
        self.assertIn("two or more viable paths have meaningful downstream consequences", text)
        self.assertIn("not required for obvious safe next steps", text)

    def test_single_action_and_no_action_cases_do_not_manufacture_choices(self) -> None:
        text = compact((ROOT / "governance" / "mission-control-interaction-contract.md").read_text(encoding="utf-8"))
        self.assertIn("When only one valid authorization exists", text)
        self.assertIn("one exact copy-paste command at the absolute bottom", text)
        self.assertIn("rather than false choices", text)
        self.assertIn("When no user authorization is required", text)
        self.assertIn("do not manufacture a Decision Box or copy-paste action", text)
        self.assertIn("status fields appear before any final Decision Box or single copy-paste command", text)

    def test_preview_is_restart_safe_and_build_is_separately_authorized(self) -> None:
        text = compact((ROOT / "governance" / "mission-control-interaction-contract.md").read_text(encoding="utf-8"))
        self.assertIn("complete restart-safe Preview is appended to the Mission Board", text)
        self.assertIn("Preview acceptance stores and confirms the plan only", text)
        self.assertIn("later explicit Build Lane authorization", text)
        self.assertIn("fresh-reads current Prime and live transaction state", text)
        self.assertIn("returns to Preview rather than being silently inferred", text)

    def test_risk_scaled_strikeforce_and_pass_ceiling_are_bound(self) -> None:
        interaction = compact((ROOT / "governance" / "mission-control-interaction-contract.md").read_text(encoding="utf-8"))
        strikeforce = compact((ROOT / "governance" / "atlas-strikeforce.md").read_text(encoding="utf-8"))
        for text in (interaction, strikeforce):
            self.assertIn("Pass N of 5", text)
            self.assertIn("BLOCKED_RESUMABLE", text)
            self.assertIn("Preview Strikeforce", text)
            self.assertIn("Build Strikeforce", text)
        self.assertIn("Five attempts never", strikeforce)

    def test_ares_is_first_class_and_adversarial(self) -> None:
        text = compact((ROOT / "governance" / "ares.md").read_text(encoding="utf-8"))
        self.assertIn("devil's advocate", text)
        self.assertIn("duplication", text)
        self.assertIn("why the plan may be", text)
        self.assertIn("grants no authority", text)

    def test_glass_codex_registers_surfaces_but_is_not_a_dependency(self) -> None:
        record = json.loads((ROOT / "governance" / "glass-codex-client-v1.json").read_text(encoding="utf-8"))
        for surface in ("MISSION_CONTROL", "DECISION_BOXES", "PREVIEWS"):
            self.assertIn(surface, record["surfaces"])
        contract = compact((ROOT / "governance" / "glass-codex-client-contract.md").read_text(encoding="utf-8"))
        self.assertIn("Mission Control", contract)
        self.assertIn("Decision Boxes", contract)
        self.assertIn("governance/mission-control-interaction-contract.md", contract)
        interaction = compact((ROOT / "governance" / "mission-control-interaction-contract.md").read_text(encoding="utf-8"))
        self.assertIn("optional presentation clients", interaction)
        self.assertIn("do not own, activate, or enforce this contract", interaction)
        self.assertIn("their absence does not disable it", interaction)


if __name__ == "__main__":
    unittest.main()
