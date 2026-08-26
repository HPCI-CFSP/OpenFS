from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from tools.check_research_web_security import evaluate


ROOT = Path(__file__).resolve().parents[1]


def load(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


class ResearchWebSecurityTests(unittest.TestCase):
    def setUp(self):
        self.policy = load("config/research-web-security-policy.json")
        self.profiles = load("config/execution-security-profiles.json")

    def test_repository_policy_is_valid_but_not_production_enforcement(self):
        result = evaluate(self.policy, self.profiles)
        self.assertTrue(result["valid"], result["errors"])
        self.assertEqual([], result["production_profiles"])

    def test_production_mode_fails_without_verified_platform_profile(self):
        result = evaluate(self.policy, self.profiles, require_production=True)
        self.assertFalse(result["valid"])
        self.assertTrue(any("no execution security profile" in item for item in result["errors"]))

    def test_shell_network_or_post_enablement_is_rejected(self):
        changed = copy.deepcopy(self.policy)
        changed["capabilities"]["shell"]["general_internet_access"] = True
        changed["capabilities"]["web_fetch"]["allowed_methods"].append("POST")
        result = evaluate(changed, self.profiles)
        self.assertFalse(result["valid"])
        self.assertTrue(any("methods" in item for item in result["errors"]))
        self.assertTrue(any("general_internet_access" in item for item in result["errors"]))

    def test_production_claim_requires_every_verified_control_and_evidence(self):
        changed = copy.deepcopy(self.profiles)
        changed["profiles"][0]["production_eligible"] = True
        result = evaluate(self.policy, changed)
        self.assertFalse(result["valid"])
        self.assertTrue(any("without verified controls" in item for item in result["errors"]))
        self.assertTrue(any("lacks verification evidence" in item for item in result["errors"]))

    def test_selected_unverified_profile_is_rejected(self):
        result = evaluate(
            self.policy,
            self.profiles,
            required_profile_id="SEC-PROFILE-GITHUB-HOSTED-DEFAULT",
        )
        self.assertFalse(result["valid"])
        self.assertTrue(any("not production eligible" in item for item in result["errors"]))

    def test_scheduled_source_audit_uses_the_fetch_broker(self):
        workflow = (ROOT / ".github/workflows/weekly-review.yml").read_text(encoding="utf-8")
        legacy_entry_point = (ROOT / "tools/audit_roadmap_sources.py").read_text(encoding="utf-8")
        self.assertIn("audit_roadmap_sources_via_fetch_broker.py", workflow)
        self.assertNotIn("python3 tools/audit_roadmap_sources.py", workflow)
        self.assertNotIn("urllib.request", legacy_entry_point)


if __name__ == "__main__":
    unittest.main()
