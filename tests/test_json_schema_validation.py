from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HAS_JSONSCHEMA = importlib.util.find_spec("jsonschema") is not None


@unittest.skipUnless(HAS_JSONSCHEMA, "pinned JSON Schema dependencies are not installed")
class JsonSchemaValidationTests(unittest.TestCase):
    def test_all_mapped_contract_artifacts_validate(self):
        sys.path.insert(0, str(ROOT / "tools"))
        from validate_json_schemas import validate

        errors, validated = validate(ROOT)
        self.assertGreater(validated, 1900)
        self.assertEqual([], errors)


if __name__ == "__main__":
    unittest.main()
