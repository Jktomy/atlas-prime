from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.atlas_lifecycle.pilot import run_context_pilot


class LifecyclePilotTests(unittest.TestCase):
    def test_pilot_proves_compact_usage_reduction_without_unmeasured_claims(self) -> None:
        report = run_context_pilot(ROOT, repetitions=20)
        self.assertEqual(report["authority"], "NONCANONICAL_MEASUREMENT_EVIDENCE")
        self.assertEqual(report["operation"], "CLEAN_CONTEXT_RECONSTRUCTION")
        self.assertEqual(report["manual_baseline"]["model_visible_files"], 3)
        self.assertEqual(report["script_assisted"]["model_visible_files"], 1)
        self.assertLess(
            report["script_assisted"]["model_visible_bytes"],
            report["manual_baseline"]["model_visible_bytes"],
        )
        self.assertGreater(
            report["comparison"]["model_visible_byte_reduction_percent"], 50
        )
        self.assertEqual(report["comparison"]["reconstruction_accuracy_percent"], 100.0)
        self.assertEqual(report["comparison"]["reconstruction_fields_exact"], 8)
        self.assertEqual(report["comparison"]["reconstruction_fields_total"], 8)
        self.assertTrue(report["comparison"]["usage_saving_supported"])
        self.assertEqual(report["manual_baseline"]["retries"], 0)
        self.assertEqual(report["script_assisted"]["retries"], 0)
        self.assertEqual(report["script_assisted"]["protected_boundary_trials"], 1)
        self.assertEqual(report["script_assisted"]["protected_boundary_rejections"], 1)
        boundaries = report["measurement_boundaries"]
        for field in (
            "beu",
            "model_usage",
            "elapsed_agent_work",
            "real_workflow_human_interventions",
            "manual_semantic_privacy_review",
        ):
            self.assertEqual(boundaries[field], "NOT_MEASURED")
        self.assertFalse(boundaries["hidden_model_calls"])
        self.assertTrue(boundaries["machine_execution_is_not_agent_elapsed_work"])

    def test_pilot_semantic_evidence_is_repeatable(self) -> None:
        first = run_context_pilot(ROOT, repetitions=10)
        second = run_context_pilot(ROOT, repetitions=10)
        for report in (first, second):
            report["manual_baseline"].pop("machine_execution_median_ns")
            report["script_assisted"].pop("machine_execution_median_ns")
        self.assertEqual(first, second)
        self.assertEqual(
            first["script_assisted"]["context_sha256"],
            "sha256:85eb3eabcbde94ca5229daf394905c12c2ecdf6c046744af842eecabc1a06e9b",
        )

    def test_pilot_cli_is_read_only(self) -> None:
        before = subprocess.run(
            ["git", "status", "--porcelain"], cwd=ROOT, check=True, capture_output=True, text=True
        ).stdout
        result = subprocess.run(
            [
                sys.executable,
                "-B",
                "-m",
                "tools.atlas_lifecycle",
                "pilot",
                "--repetitions",
                "10",
            ],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        report = json.loads(result.stdout)
        self.assertEqual(report["pilot_id"], "G3-D-COMPACT-CONTEXT-R01")
        after = subprocess.run(
            ["git", "status", "--porcelain"], cwd=ROOT, check=True, capture_output=True, text=True
        ).stdout
        self.assertEqual(after, before)

    def test_committed_pilot_receipt_matches_reproducible_semantics(self) -> None:
        path = ROOT / "proof/lifecycle/g3-d-beu-reduction-pilot-r01.json"
        if not path.exists():
            self.skipTest("pilot receipt is added after the first measured run")
        receipt = json.loads(path.read_text(encoding="utf-8"))
        observed = run_context_pilot(ROOT, repetitions=10)
        for report in (receipt, observed):
            report["manual_baseline"].pop("machine_execution_median_ns")
            report["script_assisted"].pop("machine_execution_median_ns")
        self.assertEqual(receipt, observed)


if __name__ == "__main__":
    unittest.main()
