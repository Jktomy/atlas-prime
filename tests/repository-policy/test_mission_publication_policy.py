from __future__ import annotations

import unittest

from tools.mission_publisher.core import PublicationError, normalize_paths

class MissionPublicationPolicyTests(unittest.TestCase):
    def test_parent_traversal_rejected(self):
        with self.assertRaisesRegex(PublicationError, "UNSAFE_PATH"):
            normalize_paths(["../main"])

    def test_backslashes_are_normalized(self):
        self.assertEqual(normalize_paths(["tools\\mission_publisher\\core.py"]), ["tools/mission_publisher/core.py"])

if __name__ == "__main__":
    unittest.main()
