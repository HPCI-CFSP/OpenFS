from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from validate_workflows import validate  # noqa: E402


class WorkflowValidationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        (self.root / ".github/workflows").mkdir(parents=True)

    def tearDown(self):
        self.temporary.cleanup()

    def write(self, text):
        (self.root / ".github/workflows/test.yml").write_text(
            text, encoding="utf-8"
        )

    def test_accepts_minimal_workflow(self):
        self.write(
            "name: Test\non:\n  push:\njobs:\n  test:\n    runs-on: ubuntu-latest\n    steps: []\n"
        )
        self.assertEqual([], validate(self.root))

    def test_rejects_plain_scalar_colon_and_duplicate_keys(self):
        self.write(
            "name: Test\non:\n  push:\njobs:\n  test:\n    runs-on: ubuntu-latest\n"
            "    steps:\n      - run: command --option=:all: value\n"
        )
        self.assertTrue(any("YAML parse failed" in error for error in validate(self.root)))

        self.write(
            "name: Test\non:\n  push:\njobs:\n  test:\n    runs-on: ubuntu-latest\n"
            "    runs-on: macos-latest\n    steps: []\n"
        )
        self.assertTrue(any("duplicate mapping key" in error for error in validate(self.root)))


if __name__ == "__main__":
    unittest.main()
