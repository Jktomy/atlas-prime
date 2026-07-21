from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tests.lifecycle.test_sunset_candidate import canonical_tree, request
from tools.atlas_lifecycle.errors import LifecycleError
from tools.atlas_lifecycle.jsonio import canonical_bytes
from tools.atlas_lifecycle.sunset_preview import (
    APPROVAL_ARTIFACT,
    BOUND_REQUEST,
    CARRIER_ARTIFACT,
    PREVIEW_ARTIFACT,
    generate_approved_sunset_candidate,
    generate_sunset_approval,
    generate_sunset_preview,
    verify_approved_sunset_candidate,
    verify_sunset_approval,
    verify_sunset_preview,
)


ROOT = Path(__file__).resolve().parents[2]


class SunsetPreviewEnforcementTests(unittest.TestCase):
    def write_json(self, path: Path, value: dict) -> Path:
        path.write_bytes(canonical_bytes(value))
        return path

    def preview(self, parent: Path, value: dict) -> Path:
        preview_dir = parent / "preview"
        generate_sunset_preview(
            ROOT,
            self.write_json(parent / "request-v2.json", value),
            preview_dir,
            selected_route="athena-thread-engine",
            fallback_routes=["harmony-local", "jayson-powershell"],
        )
        return preview_dir

    def pipeline(
        self,
        parent: Path,
        value: dict,
        approval_mode: str = "STANDARD",
    ) -> tuple[Path, Path, Path]:
        preview_dir = self.preview(parent, value)
        approval_dir = parent / "approval"
        generate_sunset_approval(
            ROOT,
            preview_dir,
            approval_dir,
            approval_mode=approval_mode,
        )
        candidate_dir = parent / "candidate"
        generate_approved_sunset_candidate(
            ROOT,
            approval_dir / BOUND_REQUEST,
            preview_dir,
            approval_dir,
            candidate_dir,
        )
        return preview_dir, approval_dir, candidate_dir

    def test_preview_is_required_before_approved_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            parent = Path(temp)
            with self.assertRaises(LifecycleError) as raised:
                generate_approved_sunset_candidate(
                    ROOT,
                    self.write_json(parent / "request.json", request("NON_QUEST")),
                    parent / "missing-preview",
                    parent / "missing-approval",
                    parent / "candidate",
                )
            self.assertIn(
                raised.exception.code,
                {"SUNSET_PREVIEW_DIRECTORY", "SUNSET_REQUEST_VERSION"},
            )
            self.assertFalse((parent / "candidate").exists())

    def test_preview_approval_carrier_and_candidate_are_cross_bound(self) -> None:
        before = canonical_tree()
        with tempfile.TemporaryDirectory() as temp:
            parent = Path(temp)
            preview_dir, approval_dir, candidate_dir = self.pipeline(
                parent,
                request("ADMITTED_QUEST"),
                approval_mode="GODDESS_MODE_SHARDBLADE",
            )
            preview_result = verify_sunset_preview(ROOT, preview_dir)
            approval_result = verify_sunset_approval(ROOT, preview_dir, approval_dir)
            candidate_result = verify_approved_sunset_candidate(ROOT, candidate_dir)
            preview = preview_result["preview"]
            approval = approval_result["approval"]
            carrier = approval_result["carrier"]
            self.assertEqual(approval["approval_mode"], "GODDESS_MODE_SHARDBLADE")
            self.assertEqual(approval["permanence_mode"], "SHARDBLADE")
            self.assertEqual(carrier["state"], "APPROVED_PENDING_COMPILATION")
            self.assertEqual(preview["preview_id"], approval["preview_id"])
            self.assertEqual(approval["approval_id"], carrier["approval_id"])
            self.assertEqual(candidate_result["assertions"]["feathers"], 1)
            self.assertEqual(candidate_result["assertions"]["sunsets"], 1)
            self.assertEqual(candidate_result["assertions"]["sunrises"], 1)
            self.assertEqual(candidate_result["assertions"]["quest_emberlines"], 1)
            self.assertEqual(candidate_result["assertions"]["quest_checkpoints"], 1)
            bundle = json.loads(
                (candidate_dir / "candidate-bundle.json").read_text(encoding="utf-8")
            )
            self.assertEqual(bundle["preview_digest"], preview_result["preview_digest"])
            self.assertEqual(bundle["approval_digest"], approval_result["approval_digest"])
            self.assertEqual(bundle["carrier_digest"], approval_result["carrier_digest"])
            self.assertTrue((preview_dir / PREVIEW_ARTIFACT).is_file())
            self.assertTrue((approval_dir / APPROVAL_ARTIFACT).is_file())
            self.assertTrue((approval_dir / CARRIER_ARTIFACT).is_file())
        self.assertEqual(canonical_tree(), before)

    def test_changed_scope_or_lesson_after_approval_rejects(self) -> None:
        for change in ("scope", "lesson"):
            with self.subTest(change=change), tempfile.TemporaryDirectory() as temp:
                parent = Path(temp)
                preview_dir = self.preview(parent, request("NON_QUEST"))
                approval_dir = parent / "approval"
                generate_sunset_approval(ROOT, preview_dir, approval_dir, approval_mode="STANDARD")
                approved = json.loads(
                    (approval_dir / BOUND_REQUEST).read_text(encoding="utf-8")
                )
                if change == "scope":
                    approved["quest_scope"]["work_scope"] = "Changed after approval."
                else:
                    approved["lesson_harvest"]["observations"][0]["observation"] = (
                        "Changed after approval."
                    )
                changed = self.write_json(parent / "changed.json", approved)
                with self.assertRaises(LifecycleError) as raised:
                    generate_approved_sunset_candidate(
                        ROOT,
                        changed,
                        preview_dir,
                        approval_dir,
                        parent / "candidate",
                    )
                self.assertEqual(raised.exception.code, "SUNSET_APPROVAL_BINDING")
                self.assertFalse((parent / "candidate").exists())

    def test_tampered_preview_or_approval_rejects(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            parent = Path(temp)
            preview_dir = self.preview(parent, request("NON_QUEST"))
            preview = json.loads((preview_dir / PREVIEW_ARTIFACT).read_text(encoding="utf-8"))
            preview["current_position"] = "Tampered after Preview."
            (preview_dir / PREVIEW_ARTIFACT).write_bytes(canonical_bytes(preview))
            with self.assertRaises(LifecycleError) as raised:
                verify_sunset_preview(ROOT, preview_dir)
            self.assertEqual(raised.exception.code, "SUNSET_PREVIEW_BINDING")

        with tempfile.TemporaryDirectory() as temp:
            parent = Path(temp)
            preview_dir = self.preview(parent, request("NON_QUEST"))
            approval_dir = parent / "approval"
            generate_sunset_approval(ROOT, preview_dir, approval_dir, approval_mode="STANDARD")
            approval = json.loads((approval_dir / APPROVAL_ARTIFACT).read_text(encoding="utf-8"))
            approval["approval_mode"] = "GODDESS_MODE"
            (approval_dir / APPROVAL_ARTIFACT).write_bytes(canonical_bytes(approval))
            with self.assertRaises(LifecycleError) as raised:
                verify_sunset_approval(ROOT, preview_dir, approval_dir)
            self.assertIn(
                raised.exception.code,
                {"SUNSET_APPROVAL_IDENTITY", "SUNSET_APPROVAL_BINDING"},
            )

    def test_nonquest_fabricates_no_quest_identity(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            parent = Path(temp)
            _, _, candidate_dir = self.pipeline(parent, request("NON_QUEST"))
            bundle = json.loads(
                (candidate_dir / "candidate-bundle.json").read_text(encoding="utf-8")
            )
            records = json.dumps(bundle["records"], sort_keys=True)
            self.assertNotIn('"quest_id"', records)
            self.assertEqual(bundle["assertions"]["quest_emberlines"], 0)
            self.assertEqual(bundle["assertions"]["quest_checkpoints"], 0)

    def test_preview_and_candidate_are_deterministic(self) -> None:
        outputs = []
        for _ in range(2):
            with tempfile.TemporaryDirectory() as temp:
                parent = Path(temp)
                preview_dir, approval_dir, candidate_dir = self.pipeline(
                    parent,
                    request("NON_QUEST"),
                )
                outputs.append(
                    (
                        (preview_dir / PREVIEW_ARTIFACT).read_bytes(),
                        (approval_dir / APPROVAL_ARTIFACT).read_bytes(),
                        (approval_dir / CARRIER_ARTIFACT).read_bytes(),
                        (candidate_dir / "candidate-bundle.json").read_bytes(),
                    )
                )
        self.assertEqual(outputs[0], outputs[1])


if __name__ == "__main__":
    unittest.main()
