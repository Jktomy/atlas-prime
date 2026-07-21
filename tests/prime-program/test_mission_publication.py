from __future__ import annotations

import unittest

from tools.mission_publisher.core import PublicationError, build_plan, build_receipt

BASE = "6ef7f2fd03b5b31fa2a7fe8cfcf80f6f50fa6b8e"
MISSION = {
    "repository": "Jktomy/atlas-prime",
    "issue_number": 257,
    "mission_id": "CAMPAIGN-CODEX-OPEN-PATHWAYS-SUNSET-R01",
    "attempt_id": "CAMPAIGN-CODEX-OPEN-PATHWAYS-SUNSET-ATTEMPT-02",
    "objective": "Build the minimum reliable Mission-native publisher.",
}
SEALED = ["tools/mission_publisher/core.py", "tests/prime-program/test_mission_publication.py"]

class MissionPublicationTests(unittest.TestCase):
    def test_plan_is_deterministic_and_bounded(self):
        first = build_plan(MISSION, BASE, list(reversed(SEALED)), SEALED)
        second = build_plan(MISSION, BASE, SEALED, SEALED)
        self.assertEqual(first, second)
        self.assertEqual(first["branch"], "mission/257-campaign-codex-open-pathways-sunset-r01")

    def test_outside_path_fails_closed(self):
        with self.assertRaisesRegex(PublicationError, "PATH_OUTSIDE_ENVELOPE"):
            build_plan(MISSION, BASE, ["README.md"], SEALED)

    def test_duplicate_path_fails_closed(self):
        with self.assertRaisesRegex(PublicationError, "DUPLICATE_PATH"):
            build_plan(MISSION, BASE, [SEALED[0], SEALED[0].upper()], SEALED)

    def test_protected_content_fails_closed(self):
        unsafe = dict(MISSION, objective="password='supersecretvalue'")
        with self.assertRaisesRegex(PublicationError, "PROTECTED_BOUNDARY_FAILURE"):
            build_plan(unsafe, BASE, [SEALED[0]], SEALED)

    def test_pr_open_receipt_requires_exact_bindings(self):
        plan = build_plan(MISSION, BASE, [SEALED[0]], SEALED)
        with self.assertRaisesRegex(PublicationError, "INCOMPLETE_RECEIPT"):
            build_receipt(plan, status="PR_OPEN", next_safe_action="stop")

if __name__ == "__main__":
    unittest.main()
