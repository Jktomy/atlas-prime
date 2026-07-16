from __future__ import annotations

import io
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class Cap027WholeProgramDiagnostic(unittest.TestCase):
    def test_first_whole_program_failure_is_visible(self) -> None:
        suite = unittest.defaultTestLoader.discover(
            str(ROOT / "tests" / "prime-program"),
            pattern="test_*.py",
            top_level_dir=str(ROOT),
        )
        stream = io.StringIO()
        result = unittest.TextTestRunner(
            stream=stream,
            verbosity=0,
            failfast=True,
        ).run(suite)
        self.assertTrue(result.wasSuccessful(), stream.getvalue())


if __name__ == "__main__":
    unittest.main()
