from __future__ import annotations

import unittest

from tools.atlas_lifecycle.errors import LifecycleError
from tools.sunset_router.core import normalize_record_paths


class SunsetRouterRepositoryPolicyTests(unittest.TestCase):
    def test_unsafe_paths_fail_closed(self) -> None:
        for value in (
            "../main",
            "C:/tmp",
            "/lifecycle/feathers/a.json",
            "lifecycle/../main",
        ):
            with self.subTest(value=value), self.assertRaises(LifecycleError):
                normalize_record_paths([value])

    def test_casefold_collision_fails_closed(self) -> None:
        with self.assertRaises(LifecycleError) as raised:
            normalize_record_paths(
                ["lifecycle/feathers/FTR-A.json", "lifecycle/feathers/ftr-a.json"]
            )
        self.assertEqual(raised.exception.code, "SUNSET_ROUTER_PATH_COLLISION")

    def test_safe_paths_are_sorted(self) -> None:
        self.assertEqual(
            normalize_record_paths(
                ["lifecycle/sunsets/SUN-B.json", "lifecycle/feathers/FTR-A.json"]
            ),
            ["lifecycle/feathers/FTR-A.json", "lifecycle/sunsets/SUN-B.json"],
        )


if __name__ == "__main__":
    unittest.main()
