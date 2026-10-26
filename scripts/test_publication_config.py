"""Configuration drift checks for the engineering gate.

These are narrow checks. They do not certify confidentiality or production readiness.
"""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ConfigurationContractTests(unittest.TestCase):
    def test_TEST_GATE_06_database_name_agrees_with_ci(self):
        database = (ROOT / "api/config/database.yml").read_text(encoding="utf-8")
        workflow = (ROOT / ".github/workflows/quality.yml").read_text(encoding="utf-8")
        self.assertIn("database: quality_net_test", database)
        self.assertIn("POSTGRES_DB: quality_net_test", workflow)
        self.assertIn("DB_NAME: quality_net_test", workflow)

    def test_release_notes_identify_actual_tag_and_blocked_outcome(self):
        notes = (ROOT / "RELEASE_NOTES.md").read_text(encoding="utf-8")
        self.assertIn("v1.0.0", notes)
        self.assertIn("40277694610", notes)
        self.assertIn("DO NOT SHIP", notes)
        self.assertNotIn("No remote Git tag", notes)

    def test_current_status_does_not_claim_release_approval(self):
        status = (ROOT / "assessment/09-current-status.md").read_text(encoding="utf-8")
        self.assertIn("BLOCKED / DO NOT SHIP", status)
        self.assertIn("FIND-011", status)
        self.assertIn("historical", status.lower())


if __name__ == "__main__":
    unittest.main()
