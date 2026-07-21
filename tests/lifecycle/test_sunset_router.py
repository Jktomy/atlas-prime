from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tests.lifecycle.test_sunset_candidate import canonical_tree, request
from tools.atlas_lifecycle.jsonio import canonical_bytes
from tools.sunset_router.core import (
    generate_router_approval,
    generate_router_candidate,
    generate_router_preview,
    verify_router_candidate,
)

ROOT = Path(__file__).resolve().parents[2]


def router_request(scope_type: str) -> dict:
    return {
        "schema_id": "atlas.sunset-router.request",
        "schema_version": "1.0.0",
        "authority": "PUBLIC_CLEAN_REQUEST",
        "actor": "ATHENA",
        "requested_route": "AUTO",
        "operator_transfer_authorized": False,
        "lifecycle_request": request(scope_type),
    }


class SunsetRouterLifecycleTests(unittest.TestCase):
    def write_request(self, parent: Path, value: dict) -> Path:
        path = parent / "router-request.json"
        path.write_bytes(canonical_bytes(value))
        return path

    def pipeline(self, parent: Path, scope_type: str) -> tuple[Path, Path, Path]:
        preview = parent / "router-preview"
        approval = parent / "router-approval"
        candidate = parent / "router-candidate"
        generate_router_preview(
            ROOT, self.write_request(parent, router_request(scope_type)), preview
        )
        generate_router_approval(
            ROOT,
            preview,
            approval,
            approval_mode="GODDESS_MODE_SHARDBLADE",
        )
        generate_router_candidate(ROOT, preview, approval, candidate)
        return preview, approval, candidate

    def test_nonquest_pipeline_is_deterministic_and_add_only(self) -> None:
        before = canonical_tree()
        outputs = []
        for _ in range(2):
            with tempfile.TemporaryDirectory() as temp:
                preview, approval, candidate = self.pipeline(Path(temp), "NON_QUEST")
                verified = verify_router_candidate(ROOT, preview, approval, candidate)
                plan = verified["plan"]
                self.assertEqual(plan["selected_route"], "ATHENA_SPEAR_THREAD_ENGINE")
                self.assertEqual(
                    plan["fallback_routes"],
                    ["ATHENA_PHOENIX_BLADE", "ATHENA_AEGIS_BREAK"],
                )
                self.assertTrue(plan["operations"])
                self.assertTrue(
                    all(item["action"] == "ADD" for item in plan["operations"])
                )
                self.assertEqual(
                    plan["changed_paths"], [item["path"] for item in plan["operations"]]
                )
                outputs.append((candidate / "sunset-router-plan.json").read_bytes())
        self.assertEqual(outputs[0], outputs[1])
        self.assertEqual(canonical_tree(), before)

    def test_admitted_quest_marks_living_emberline_replace(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            preview, approval, candidate = self.pipeline(Path(temp), "ADMITTED_QUEST")
            plan = verify_router_candidate(ROOT, preview, approval, candidate)["plan"]
            replacements = [item for item in plan["operations"] if item["action"] == "REPLACE"]
            self.assertEqual(len(replacements), 1)
            self.assertTrue(replacements[0]["path"].startswith("lifecycle/quest-emberlines/"))
            self.assertTrue(
                all(
                    item["payload_digest"].startswith("sha256:")
                    for item in plan["operations"]
                )
            )


if __name__ == "__main__":
    unittest.main()
