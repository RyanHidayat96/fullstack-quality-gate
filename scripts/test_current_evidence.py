"""Regression checks for the published engineering evidence ledger.

These checks do not grant release or publication approval. They only prevent
known stale claims and inconsistent release risk records from returning.
"""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class CurrentEvidenceTests(unittest.TestCase):
    # TEST-GATE-06: check CI claims using the PDF-required quality report.
    def test_live_checks_are_linked_without_claiming_full_stack_e2e(self):
        status = (ROOT / "assessment/02-quality-system.md").read_text(encoding="utf-8")
        self.assertIn("40301673841", status)
        self.assertIn("40295447111", status)
        self.assertIn("DO NOT SHIP", status)
        self.assertIn("not fully demonstrated", status.lower())

    def test_only_requested_top_level_assessment_reports_remain(self):
        expected = {"01-audit.md", "02-quality-system.md", "03-release-decision.md"}
        actual = {p.name for p in (ROOT / "assessment").glob("*.md")}
        self.assertEqual(expected, actual)
        self.assertFalse((ROOT / "PLAN.md").exists())
        self.assertFalse((ROOT / "assessment/evidence").exists())
        for path in (
            "assessment/design/phase-3-test-catalog.json",
            "assessment/requirements/REQ-QUALITY-001.md",
            "assessment/criteria/AC-QUALITY-001.md",
            "assessment/designs/DES-QUALITY-001.md",
        ):
            self.assertTrue((ROOT / path).is_file(), path)

    def test_readiness_claims_reflect_bounded_success(self):
        data = json.loads((ROOT / "assessment/release-readiness.json").read_text(encoding="utf-8"))
        checks = data["mandatory_verifications"]
        self.assertEqual("VERIFIED", checks["api_db_integration"]["status"])
        self.assertEqual("VERIFIED", checks["frontend_build"]["status"])
        self.assertEqual("VERIFIED", checks["component_regression"]["status"])
        self.assertEqual("BLOCKED", checks["browser_api_db_journey"]["status"])
        self.assertEqual("BLOCKED", checks["release_owner_signoff"]["status"])
        self.assertEqual("BLOCKED", checks["publication_clearance"]["status"])
        self.assertEqual("BLOCKED", checks["spec_acceptance_approved"]["status"])
        self.assertEqual("CODE_FIXED_UNVERIFIED",
                         next(x["state"] for x in data["p1_findings"] if x["id"] == "FIND-011"))

    def test_submission_does_not_assert_publication_clearance(self):
        data = json.loads((ROOT / "assessment/submission-evidence.json").read_text(encoding="utf-8"))
        self.assertFalse(data["publication_clearance"])
        self.assertFalse(data["hiring_platform_submission"]["completed"])


if __name__ == "__main__":
    unittest.main()
