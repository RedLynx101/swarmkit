from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from verify_repo_basics import REQUIRED_PATHS


class VerifyRepoBasicsTests(unittest.TestCase):
    def test_required_paths_are_relative(self) -> None:
        for path in REQUIRED_PATHS:
            self.assertFalse(Path(path).is_absolute())

    def test_missing_files_detected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            missing = [p for p in REQUIRED_PATHS if not (root / p).exists()]
            self.assertGreater(len(missing), 0)


if __name__ == "__main__":
    unittest.main()
