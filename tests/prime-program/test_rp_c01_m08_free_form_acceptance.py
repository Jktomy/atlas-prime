from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class RpC01M08FreeFormAcceptanceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.acceptance = json.loads((ROOT / "proof/repairing-prime/rp-c01-m08-free-form-acceptance-r01.json").read_text(encoding="utf-8"))
        self.route = json.loads((ROOT / "proof/repairing-prime/rp-c01-route-evidence-r01.json").read_text(encoding="utf-8"))

    def test_exact_hosted_journey_is_bound(self) -> None:
        live = self.acceptance["live_evidence"]
        self.assertEqual(live["workflow_run"], 29241109167)
        self.assertEqual(live["workflow_source_sha"], "063dd2334f768494a6d0bf4085f5ccffd9799198")
        self.assertEqual(live["mission_id"], "RP-C01-M08-FREE-FORM-LIVE-R01")
        self.assertEqual(live["pull_request"], 166)
        self.assertEqual(live["head_sha"], "4bc22f8203ab0603025fc63fe0862eaddf58f3ef")
        self.assertEqual(live["merge_sha"], "429ae7d068f9dde943a47b7cf3795073b9d1fc93")
        self.assertEqual(live["canonical_readback"], "EXACT")

    def test_exact_head_ci_and_detached_review_are_green(self) -> None:
        live = self.acceptance["live_evidence"]
        self.assertEqual(
            live["exact_head_ci"],
            {"run": 29261247288, "ubuntu_job": 86854800780, "windows_job": 86854800816, "result": "GREEN"},
        )
        self.assertEqual(live["detached_review"], "GREEN")
        self.assertTrue(live["singular_thread_engine"])
        self.assertEqual(live["checkpoint_count"], 24)
        self.assertEqual(live["forbidden_action_confirmation"], "ALL_FALSE_OR_NO")

    def test_artifact_and_member_digests_are_exact(self) -> None:
        artifacts = self.acceptance["live_evidence"]["artifacts"]
        self.assertEqual(artifacts["preflight"]["archive_sha256"], "ab445544481823c5d67df31ca6850e285bb6d28f8c7e31d30641d7fe4fb01efe")
        self.assertEqual(artifacts["route"]["archive_sha256"], "ed712359390cc1678cd41575eb4e906b5b67cf58a0394ba1b8352f311769452c")
        self.assertEqual(
            artifacts["route"]["members"]["thread-engine-evidence.json"],
            "677878da7774b43c76dd32ab6150c96bad7dcc82a316ae2fe28a74c4b43bfab0",
        )

    def test_m08_does_not_self_promote_and_later_m07_transition_is_separate(self) -> None:
        self.assertEqual(self.acceptance["campaign_gate_state"], "NOT_PROVEN")
        self.assertEqual(self.acceptance["capability_promotion"], "NONE")
        self.assertEqual(self.acceptance["acceptance_journey_promotion"], "NONE")
        self.assertTrue(all(value is False for value in self.acceptance["forbidden_promotions"].values()))
        self.assertEqual(self.route["capability_promotion"], "NONE")
        self.assertEqual(self.route["acceptance_journey_promotion"], "AJ-03_ONLY")
        self.assertEqual(self.route["m07_live_rejection_sequence"]["state"], "PROVEN_COMPLETE_REJECTION_SET")
        self.assertEqual(self.route["m07_live_rejection_sequence"]["missing"], [])


if __name__ == "__main__":
    unittest.main()
