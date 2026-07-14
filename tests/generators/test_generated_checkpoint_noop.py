from __future__ import annotations

import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
THREAD_ENGINE_ROOT = ROOT / "tools" / "thread-engine"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(THREAD_ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(THREAD_ENGINE_ROOT))

from production_adapter.generated_checkpoint import APPROVED_PATHS
from production_adapter.receipt import stable_json
from tools.build_index import APPROVED_OUTPUTS, build_outputs, output_bytes
from tools.generated_checkpoint.core import (
    NOOP_RECEIPT_SCHEMA,
    PreparationError,
    build_hash_register,
    prepare_package,
    reconcile_registers,
)
from tools.generated_checkpoint.hosted_prepare import main as hosted_prepare_main


BASE = "a" * 40
WORKFLOW_REF = "Jktomy/atlas-prime/.github/workflows/generated-checkpoint-publisher.yml@refs/heads/main"
MISSION_ID = "RP-C08-NO-DELTA-UNIT-001"
NONCE = "rp-c08-no-delta-unit-replay-nonce-001"


class GeneratedCheckpointNoopTests(unittest.TestCase):
    def make_full_delta_repo(self, root: Path) -> None:
        root.mkdir(parents=True)
        (root / "README.md").write_text("# Prime before\n", encoding="utf-8", newline="\n")
        old_outputs, _ = build_outputs(root)
        generated = root / "generated"
        generated.mkdir()
        for name in APPROVED_OUTPUTS:
            (generated / name).write_bytes(output_bytes(old_outputs[name]))
        (root / "README.md").write_text("# Prime after\n", encoding="utf-8", newline="\n")
        workflow = root / ".github" / "workflows" / "generated-checkpoint-publisher.yml"
        workflow.parent.mkdir(parents=True)
        workflow.write_text("name: Generated checkpoint publisher\n", encoding="utf-8", newline="\n")

    def candidate_outputs(self, root: Path) -> dict[str, bytes]:
        _, outputs = build_hash_register(
            root,
            mission_id=MISSION_ID,
            base_sha=BASE,
            replay_nonce=NONCE,
            workflow_ref=WORKFLOW_REF,
            workflow_source_sha=BASE,
            workflow_run_id="123456789",
            workflow_run_attempt="1",
        )
        return outputs

    def write_evidence(self, root: Path) -> tuple[Path, Path]:
        register, _ = build_hash_register(
            root,
            mission_id=MISSION_ID,
            base_sha=BASE,
            replay_nonce=NONCE,
            workflow_ref=WORKFLOW_REF,
            workflow_source_sha=BASE,
            workflow_run_id="123456789",
            workflow_run_attempt="1",
        )
        ubuntu = root.parent / "ubuntu.json"
        windows = root.parent / "windows.json"
        ubuntu.write_text(stable_json(register), encoding="utf-8", newline="\n")
        windows.write_text(stable_json(register), encoding="utf-8", newline="\n")
        reconciliation = reconcile_registers(ubuntu, windows)
        reconciliation_path = root.parent / "reconciliation.json"
        reconciliation_path.write_text(
            stable_json(reconciliation), encoding="utf-8", newline="\n"
        )
        return ubuntu, reconciliation_path

    def synchronize_paths(self, root: Path, paths: tuple[str, ...]) -> None:
        outputs = self.candidate_outputs(root)
        for path in paths:
            root.joinpath(*path.split("/")).write_bytes(outputs[path])

    def test_zero_delta_emits_successful_hosted_noop_receipt(self) -> None:
        with tempfile.TemporaryDirectory(prefix="generated-checkpoint-noop-") as raw:
            root = Path(raw) / "repo"
            self.make_full_delta_repo(root)
            self.synchronize_paths(root, APPROVED_PATHS)
            register_path, reconciliation_path = self.write_evidence(root)
            package = Path(raw) / "package"
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                result = hosted_prepare_main(
                    [
                        "--repo-root", str(root),
                        "--register", str(register_path),
                        "--reconciliation", str(reconciliation_path),
                        "--package-root", str(package),
                        "--replay-nonce", NONCE,
                        "--public-clean-confirmation", "PUBLIC_CLEAN_CONFIRMED",
                        "--event-name", "push",
                    ]
                )
            self.assertEqual(result, 0)
            receipt = json.loads(stdout.getvalue())
            self.assertEqual(receipt["schema_id"], NOOP_RECEIPT_SCHEMA)
            self.assertEqual(receipt["result"], "NOOP")
            self.assertEqual(receipt["event_name"], "push")
            self.assertEqual(receipt["changed_count"], 0)
            self.assertEqual(receipt["changed_paths"], [])
            self.assertEqual(receipt["approved_paths"], list(APPROVED_PATHS))
            self.assertRegex(receipt["receipt_sha256"], r"^[0-9a-f]{64}$")
            self.assertFalse((package / "mission.json").exists())
            stored = json.loads((package / "noop-receipt.json").read_text(encoding="utf-8"))
            self.assertEqual(stored, receipt)

    def test_all_five_deltas_keep_existing_mission_route(self) -> None:
        with tempfile.TemporaryDirectory(prefix="generated-checkpoint-full-") as raw:
            root = Path(raw) / "repo"
            self.make_full_delta_repo(root)
            register_path, reconciliation_path = self.write_evidence(root)
            package = Path(raw) / "package"
            mission = prepare_package(
                root,
                register_path,
                reconciliation_path,
                package,
                replay_nonce=NONCE,
                public_clean_confirmation="PUBLIC_CLEAN_CONFIRMED",
            )
            self.assertNotEqual(mission.get("result"), "NOOP")
            self.assertEqual(len(mission["operations"]), len(APPROVED_PATHS))
            self.assertEqual(mission["declared_paths"], list(APPROVED_PATHS))
            self.assertTrue((package / "mission.json").is_file())
            self.assertFalse((package / "noop-receipt.json").exists())

    def test_partial_delta_fails_closed_before_mission_or_noop(self) -> None:
        with tempfile.TemporaryDirectory(prefix="generated-checkpoint-partial-") as raw:
            root = Path(raw) / "repo"
            self.make_full_delta_repo(root)
            self.synchronize_paths(root, APPROVED_PATHS[1:])
            register_path, reconciliation_path = self.write_evidence(root)
            package = Path(raw) / "package"
            with self.assertRaises(PreparationError) as raised:
                prepare_package(
                    root,
                    register_path,
                    reconciliation_path,
                    package,
                    replay_nonce=NONCE,
                    public_clean_confirmation="PUBLIC_CLEAN_CONFIRMED",
                )
            self.assertEqual(
                raised.exception.code,
                "GENERATED_CHECKPOINT_PARTIAL_DELTA",
            )
            self.assertFalse((package / "mission.json").exists())
            self.assertFalse((package / "noop-receipt.json").exists())

    def test_workflow_keeps_noop_read_only_and_writer_full_delta_only(self) -> None:
        workflow = (
            ROOT / ".github" / "workflows" / "generated-checkpoint-publisher.yml"
        ).read_text(encoding="utf-8")
        prepare_block = workflow.split("\n  prepare:\n", 1)[1].split("\n  publish:\n", 1)[0]
        publish_block = workflow.split("\n  publish:\n", 1)[1].split(
            "\n  validate_exact_head:\n", 1
        )[0]
        self.assertIn("route_result: ${{ steps.prepare_checkpoint.outputs.route_result }}", prepare_block)
        self.assertIn('"route_result=NOOP"', prepare_block)
        self.assertIn("contents: read", prepare_block)
        self.assertNotIn("contents: write", prepare_block)
        self.assertNotIn("pull-requests: write", prepare_block)
        self.assertIn(
            "needs.prepare.outputs.route_result == 'PACKAGE_PREPARED'",
            publish_block,
        )
        self.assertIn("contents: write", publish_block)
        self.assertIn("pull-requests: write", publish_block)
        self.assertIn("generated-checkpoint-preparation-", workflow)
        self.assertNotIn("actions: write", workflow)
        self.assertNotIn("automatic merge", workflow.casefold())
        self.assertNotIn("gh workflow run", workflow)


if __name__ == "__main__":
    unittest.main()
