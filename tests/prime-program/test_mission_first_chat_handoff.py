from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "governance" / "mission-first-chat-handoff-contract.md"
MISSION_CONTROL = ROOT / "governance" / "mission-control-interaction-contract.md"
MISSION_BOARD = ROOT / "governance" / "mission-board-contract.md"
LESSON_HARVEST = ROOT / "governance" / "lesson-harvest-protocol.md"
START_HERE = ROOT / "atlas-start-here.md"


class MissionFirstChatHandoffTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = CONTRACT.read_text(encoding="utf-8")
        cls.words = " ".join(cls.text.split())
        cls.start_here = START_HERE.read_text(encoding="utf-8")

    def test_contract_is_canonical_and_routed_from_startup(self) -> None:
        self.assertIn('status: "CANONICAL_ACTIVE"', self.text)
        self.assertIn("governance/mission-control-interaction-contract.md", self.text)
        self.assertIn("governance/mission-board-contract.md", self.text)
        self.assertIn("governance/lesson-harvest-protocol.md", self.text)
        self.assertIn("governance/mission-first-chat-handoff-contract.md", self.start_here)
        self.assertTrue(MISSION_CONTROL.is_file())
        self.assertTrue(MISSION_BOARD.is_file())
        self.assertTrue(LESSON_HARVEST.is_file())

    def test_substantive_work_is_mission_bound_before_execution(self) -> None:
        required = (
            "Before substantive execution begins",
            "create or resolve exactly one",
            "Mission Board Mission",
            "source mutation",
            "delegation or assignment to Codex",
            "BLOCKED_RESUMABLE",
        )
        for phrase in required:
            self.assertIn(phrase, self.words)

    def test_chat_and_mission_board_roles_remain_distinct(self) -> None:
        self.assertIn("Chat is the discussion", self.words)
        self.assertIn("Mission Board is the required", self.words)
        self.assertIn("Merged Prime remains canonical doctrine", self.words)
        self.assertIn("Mission capture does not itself grant Build", self.words)

    def test_ordinary_conversation_does_not_manufacture_missions(self) -> None:
        self.assertIn("Do not manufacture a Mission for ordinary conversation", self.words)
        self.assertIn("quick factual answers", self.words)
        self.assertIn("writing or rewriting", self.words)
        self.assertIn("nonconsequential one-shot task", self.words)

    def test_public_clean_boundary_is_explicit(self) -> None:
        self.assertIn("Never copy an entire chat", self.words)
        self.assertIn("protected://", self.text)
        for prohibited in (
            "Secrets",
            "credentials",
            "private network",
            "PHI",
            "raw financial",
            "unrestricted logs",
        ):
            self.assertIn(prohibited, self.words)

    def test_sunset_interruption_requires_durable_mission_handoff(self) -> None:
        required = (
            "one `mission/sunset` identity before candidate construction",
            "Preview digest and approval mode",
            "approved canonical base",
            "formal carrier state",
            "does not fabricate a formal lifecycle carrier",
            "`SUNSET COMPLETE`",
        )
        for phrase in required:
            self.assertIn(phrase, self.words)

    def test_worldhopper_resumes_same_attempt_without_new_authority(self) -> None:
        self.assertIn("Assignment makes work discoverable", self.words)
        self.assertIn("grants no new capability", self.words)
        self.assertIn("resumes the same attempt", self.words)
        self.assertIn("READY, and permanence gates", self.words)


if __name__ == "__main__":
    unittest.main()
