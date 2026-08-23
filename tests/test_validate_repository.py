from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from validate_repository import run  # noqa: E402


class RepositoryValidationTests(unittest.TestCase):
    def test_repository_structure_is_valid(self):
        self.assertEqual([], run(ROOT))


if __name__ == "__main__":
    unittest.main()
