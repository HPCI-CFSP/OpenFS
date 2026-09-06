from __future__ import annotations

import os
import shutil
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class AnalyticsUiTests(unittest.TestCase):
    def test_consent_and_data_minimization_contract(self):
        node = os.environ.get("OPENFS_NODE") or shutil.which("node")
        if not node:
            self.skipTest("Node.js is unavailable")
        result = subprocess.run(
            [node, "--test", "tests/analytics_ui.test.cjs"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
