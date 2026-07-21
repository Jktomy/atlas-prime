from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tests.lifecycle.test_sunset_candidate import request
from tools.atlas_lifecycle.errors import LifecycleError
from tools.atlas_lifecycle.jsonio import canonical_bytes
from tools.sunset_router.core import generate_router_preview

ROOT = Path(__file__).resolve().parents[2]


class SunsetRouterPrivacyTests(unittest.TestCase):
    def test_nested_protected_looking_content_rejects_before_output(self) -> None:
        token = "github" + "_pat_" + ("a" * 24)
        lifecycle = request("NON_QUEST")
        lifecycle["context_summary"] = token
        wrapper = {
            "schema_id": "atlas.sunset-router.request",
            "schema_version": "1.0.0",
            "authority": "PUBLIC_CLEAN_REQUEST",
            "actor": "ATHENA",
            "requested_route": "AUTO",
            "operator_transfer_authorized": False,
            "lifecycle_request": lifecycle,
        }
        with tempfile.TemporaryDirectory() as temp:
            parent = Path(temp)
            request_path = parent / "request.json"
            request_path.write_bytes(canonical_bytes(wrapper))
            output = parent / "output"
            with self.assertRaises(LifecycleError) as raised:
                generate_router_preview(ROOT, request_path, output)
            self.assertIn(raised.exception.code, {"PROTECTED_VALUE_REJECTED"})
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
