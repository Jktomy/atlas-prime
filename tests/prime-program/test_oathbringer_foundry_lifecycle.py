from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FOUNDRY_ROOT = ROOT / "tools/oathbringer-foundry"
THREAD_TESTS = ROOT / "tools/thread-engine/tests"
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(FOUNDRY_ROOT))
sys.path.insert(0, str(THREAD_TESTS))

import foundry as foundry_module
from foundry import FoundryError, compile_carrier, verify_carrier
from test_lifecycle_profile import build_lifecycle_mission
import test_oathbringer_foundry as base_foundry


class OathbringerFoundryLifecycleTests(unittest.TestCase):
    def setUp(self) -> None:
        base_foundry.OathbringerFoundryTests.setUp(self)

    def tearDown(self) -> None:
        base_foundry.OathbringerFoundryTests.tearDown(self)

    def _mission(self, mode: str = "BUILD") -> dict:
        return base_foundry.OathbringerFoundryTests._mission(self, mode)

    def _live(self, mission: dict) -> dict:
        return base_foundry.OathbringerFoundryTests._live(self, mission)

    def _lifecycle_mission(self) -> tuple[dict, dict]:
        fixture_root = self.root / "lifecycle-fixture"
        fixture_root.mkdir()
        _, thread_mission, candidate_root = build_lifecycle_mission(fixture_root)
        destination = self.input_root / "payload/lifecycle-candidate"
        shutil.copytree(candidate_root, destination)
        profile = thread_mission["lifecycle_profile"]
        mission = self._mission("BUILD")
        operation = {
            "path": profile["repository_path"],
            "operation": "ADD",
            "payload_path": "payload/lifecycle-candidate/event.json",
            "payload_sha256": base_foundry.digest(destination / "event.json"),
        }
        mission["operations"] = [operation]
        mission["oathbringer_mission"]["declared_paths"] = [dict(operation)]
        mission["source_lock"]["expected_base"] = profile["expected_main_sha"]
        mission["oathbringer_mission"]["expected_base"] = profile["expected_main_sha"]
        mission["lifecycle_profile"] = profile
        live = self._live(mission)
        live["base_sha"] = profile["expected_main_sha"]
        return mission, live

    def _compile_lifecycle(self, mission: dict, live: dict, name: str = "lifecycle"):
        return compile_carrier(
            mission,
            input_root=self.input_root,
            source_root=ROOT,
            output_dir=self.root / name,
            live_state=live,
        )

    def test_lifecycle_carrier_preserves_exact_candidate_set_and_receipt_binding(self) -> None:
        mission, live = self._lifecycle_mission()
        first = self._compile_lifecycle(mission, live, "first")
        second = self._compile_lifecycle(mission, live, "second")
        self.assertEqual(first.carrier_path.read_bytes(), second.carrier_path.read_bytes())
        self.assertEqual(verify_carrier(first.carrier_path)["status"], "PASS")
        with zipfile.ZipFile(first.carrier_path) as archive:
            names = set(archive.namelist())
            self.assertTrue({
                "payload/lifecycle-candidate/event.json",
                "payload/lifecycle-candidate/candidate-manifest.json",
                "payload/lifecycle-candidate/candidate-receipt.json",
            } <= names)
            receipt = json.loads(archive.read("FORGE-RECEIPT.json"))
            binding = receipt["lifecycle_carrier"]
            self.assertEqual(binding["event_record_id"], mission["lifecycle_profile"]["event_record_id"])
            self.assertEqual(binding["candidate_set_digest"], mission["lifecycle_profile"]["candidate_set_digest"])
            self.assertFalse(binding["compiler_is_writer"])
            self.assertFalse(binding["github_authority"])

    def test_lifecycle_carrier_rejects_candidate_profile_and_authority_drift(self) -> None:
        mission, live = self._lifecycle_mission()
        receipt = self.input_root / "payload/lifecycle-candidate/candidate-receipt.json"
        receipt.write_bytes(receipt.read_bytes() + b" ")
        with self.assertRaisesRegex(FoundryError, "trusted contract|digest mismatch"):
            self._compile_lifecycle(mission, live, "tampered")

        self.tearDown()
        self.setUp()
        mission, live = self._lifecycle_mission()
        mission["mode"] = "REPAIR"
        with self.assertRaisesRegex(FoundryError, "BUILD-only"):
            foundry_module._validate_lifecycle_binding(mission, ROOT)

        mission["mode"] = "BUILD"
        mission["lifecycle_profile"]["write_boundary"]["automatic_merge"] = True
        with self.assertRaisesRegex(FoundryError, "trusted contract"):
            self._compile_lifecycle(mission, live, "authority")

    def test_lifecycle_carrier_rejects_operation_widening(self) -> None:
        mission, live = self._lifecycle_mission()
        mission["operations"].append(dict(mission["operations"][0], path="lifecycle/events/second.json"))
        mission["oathbringer_mission"]["declared_paths"] = [dict(item) for item in mission["operations"]]
        with self.assertRaisesRegex(FoundryError, "one operation"):
            self._compile_lifecycle(mission, live, "widened")

    def test_lifecycle_bearing_json_is_bounded_and_float_free(self) -> None:
        nested: dict = {"leaf": "value"}
        for _ in range(70):
            nested = {"nested": nested}
        with self.assertRaisesRegex(FoundryError, "parsing bounds"):
            foundry_module._loads_json(json.dumps(nested).encode(), "deep fixture")
        with self.assertRaisesRegex(FoundryError, "floating-point"):
            foundry_module._loads_json(b'{"value":1.5}\n', "float fixture")


if __name__ == "__main__":
    unittest.main()
