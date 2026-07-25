from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]


class WorldhopperRelayContractTests(unittest.TestCase):
    def test_contract_routes_from_startup_and_recovery(self) -> None:
        contract = (ROOT / "governance/worldhopper-relay-contract.md").read_text(encoding="utf-8")
        routing = (ROOT / "routing/command-surfaces.md").read_text(encoding="utf-8")
        recovery = (ROOT / "recovery/elantris-recovery.md").read_text(encoding="utf-8")
        self.assertIn("atlas.mission-checkpoint.v1", contract)
        self.assertIn("WORKING_DRAFT", contract)
        self.assertIn("BLOCKED_RESUMABLE` is invalid", contract)
        self.assertIn("GitHub-native blob, tree, commit, ref, file", contract)
        self.assertIn("governance/worldhopper-relay-contract.md", routing)
        self.assertIn("digest-chained", recovery)

    def test_runner_remains_orchestration_over_two_publishers(self) -> None:
        contract = (ROOT / "governance/worldhopper-relay-contract.md").read_text(encoding="utf-8")
        runner = (ROOT / "tools/mission_runner/README.md").read_text(encoding="utf-8")
        self.assertIn("never becomes a third publisher", contract)
        self.assertIn("Thread Engine remains the normal publisher", contract)
        self.assertIn("Sword/Oathbringer remains the", contract)
        self.assertIn("independent recovery publisher", contract)
        self.assertIn("not a publisher", runner)


if __name__ == "__main__":
    unittest.main()
