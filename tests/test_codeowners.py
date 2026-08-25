from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from validate_repository import validate_codeowners  # noqa: E402


class CodeownersTests(unittest.TestCase):
    def test_missing_sensitive_pattern_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / ".github/CODEOWNERS"
            path.parent.mkdir(parents=True)
            path.write_text("/AGENTS.md @owner\n", encoding="utf-8")
            errors = validate_codeowners(root)
            self.assertTrue(any("lacks protected" in error for error in errors))

    def test_repository_codeowners_contract_passes(self):
        self.assertEqual([], validate_codeowners(ROOT))


if __name__ == "__main__":
    unittest.main()
