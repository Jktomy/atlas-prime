from __future__ import annotations

import unittest

from tools.mission_publisher.core import PublicationError, build_plan

class MissionPublicationPrivacyTests(unittest.TestCase):
    def test_token_pattern_is_rejected(self):
        mission = {"repository":"Jktomy/atlas-prime","issue_number":257,"mission_id":"MISSION-257","attempt_id":"ATTEMPT-257","objective":"github_pat_abcdefghijklmnopqrstuvwxyz123456"}
        with self.assertRaisesRegex(PublicationError, "PROTECTED_BOUNDARY_FAILURE"):
            build_plan(mission, "6ef7f2fd03b5b31fa2a7fe8cfcf80f6f50fa6b8e", ["tools/mission_publisher/core.py"], ["tools/mission_publisher/core.py"])

if __name__ == "__main__":
    unittest.main()
