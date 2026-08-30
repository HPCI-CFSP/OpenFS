from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from build_pages_site import build  # noqa: E402


class FeedbackPageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.scripts = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "a":
            self.links.append(attributes)
        if tag == "script":
            self.scripts.append(attributes.get("src", ""))


class PublicFeedbackTests(unittest.TestCase):
    def test_forms_are_public_feedback_not_directives(self):
        for name in ("correction-report", "research-request", "improvement-proposal"):
            with self.subTest(name=name):
                form = yaml.safe_load((ROOT / ".github/ISSUE_TEMPLATE" / f"{name}.yml").read_text())
                self.assertEqual(["public-feedback", name], form["labels"])
                fields = {item["id"]: item for item in form["body"] if "id" in item}
                self.assertTrue(fields["description"]["validations"]["required"])
                self.assertTrue(fields["boundary"]["attributes"]["options"][0]["required"])
                for key in ("target", "page_url", "source_commit", "language", "sources"):
                    self.assertIn(key, fields)
                    self.assertFalse(fields[key].get("validations", {}).get("required", False))
                warning = form["body"][0]["attributes"]["value"]
                self.assertIn("投稿内容は公開", warning)
                self.assertIn("Submissions are public", warning)

    def test_every_generated_page_links_feedback_before_search(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "site"
            data = build(ROOT, output)
            self.assertTrue((output / "feedback/index.html").is_file())
            self.assertTrue((output / "feedback.js").is_file())
            for page in output.rglob("*.html"):
                with self.subTest(page=str(page.relative_to(output))):
                    parser = FeedbackPageParser()
                    text = page.read_text()
                    parser.feed(text)
                    links = [link for link in parser.links if "data-feedback-nav" in link]
                    self.assertEqual(1, len(links))
                    target = (page.parent / urlsplit(links[0]["href"]).path / "index.html").resolve()
                    self.assertEqual((output / "feedback/index.html").resolve(), target)
                    nav = text.split('<nav class="tabs"', 1)[1].split("</nav>", 1)[0]
                    self.assertLess(nav.index("data-feedback-nav"), nav.index('data-i18n="navSearch"'))
                    feedback_script = next(index for index, src in enumerate(parser.scripts) if "feedback.js?" in src)
                    self.assertGreater(feedback_script, 0)
                    self.assertIn("openfs-public.js?", parser.scripts[feedback_script - 1])
                    self.assertIn(data["site"]["commit_sha"], parser.scripts[feedback_script])
                    self.assertNotIn("{{", text)

    def test_url_contract_in_node(self):
        node = os.environ.get("OPENFS_NODE") or shutil.which("node")
        if not node:
            self.skipTest("Node.js is required for the feedback URL contract tests")
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "site"
            build(ROOT, output)
            environment = {**os.environ, "OPENFS_FEEDBACK_DATA": str(output / "data/openfs-public.js")}
            result = subprocess.run(
                [node, "--test", "tests/feedback_urls.test.cjs", "tests/feedback_ui.test.cjs"],
                cwd=ROOT, env=environment, text=True, capture_output=True,
            )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
