from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from validate_readme_i18n import (  # noqa: E402
    EXPECTED_SECTIONS,
    section_ids,
    validate_changed_paths,
    validate_pair,
)


class ReadmeI18nTests(unittest.TestCase):
    def setUp(self):
        self.english = (ROOT / "README.md").read_text(encoding="utf-8")
        self.japanese = (ROOT / "README.ja.md").read_text(encoding="utf-8")

    def test_repository_readmes_are_synchronized(self):
        self.assertEqual([], validate_pair(self.english, self.japanese))
        self.assertEqual(EXPECTED_SECTIONS, section_ids(self.english))
        self.assertEqual(EXPECTED_SECTIONS, section_ids(self.japanese))

    def test_missing_japanese_section_is_rejected(self):
        changed = self.japanese.replace(
            "<!-- i18n-section: license -->", "<!-- removed-section: license -->"
        )
        self.assertTrue(validate_pair(self.english, changed))

    def test_changed_executable_example_is_rejected(self):
        changed = self.japanese.replace(
            "python3 tools/build_pages_site.py --output _site",
            "python3 tools/build_pages_site.py --output public",
        )
        self.assertIn(
            "README executable examples differ between languages",
            validate_pair(self.english, changed),
        )

    def test_one_language_change_is_rejected(self):
        self.assertTrue(validate_changed_paths({"README.md"}))
        self.assertTrue(validate_changed_paths({"README.ja.md"}))
        self.assertEqual(
            [], validate_changed_paths({"README.md", "README.ja.md"})
        )
        self.assertEqual([], validate_changed_paths({"site/app.js"}))

    def test_validation_workflow_enforces_readme_parity(self):
        workflow = (ROOT / ".github" / "workflows" / "validate.yml").read_text(
            encoding="utf-8"
        )
        self.assertIn("Validate bilingual README", workflow)
        self.assertIn("Require synchronized README changes", workflow)
        self.assertIn(
            'tools/validate_readme_i18n.py --base "$OPENFS_README_BASE_SHA"',
            workflow,
        )


if __name__ == "__main__":
    unittest.main()
