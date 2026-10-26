"""Verify 41-item catalog completeness without claiming execution from comments."""
import tempfile
import unittest
from pathlib import Path

from verify_catalog_coverage import build_report, extract_tests


class ScenarioTraceabilityTests(unittest.TestCase):
    # TEST-GATE-06: full catalog classification cannot be replaced by a raw grep count.
    def test_TEST_GATE_06_all_41_scenarios_have_an_explicit_disposition(self):
        report = build_report()
        self.assertEqual(41, report["total"])
        self.assertEqual(41, len(report["scenarios"]))
        self.assertEqual(41, sum(report["counts"].values()))
        self.assertEqual(41, len({s["id"] for s in report["scenarios"]}))
        self.assertTrue(all(s["status"] in {"EXECUTABLE", "PARTIAL", "MISSING"}
                            for s in report["scenarios"]))

    def test_comments_alone_do_not_count_as_test_assertions(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "fake_spec.rb"
            path.write_text("# it 'AUTH-TENANT-01 must reject' do\n"
                            "it 'AUTH-TENANT-02 is empty' do\n"
                            "  # expect(false)\nend\n", encoding="utf-8")
            tests = extract_tests(path)
            self.assertFalse(any(asserts for _name, asserts in tests))

    def test_true_executable_assertion_is_recognized(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "real_spec.rb"
            path.write_text("it 'AUTH-TENANT-01 denies foreign data' do\n"
                            "  expect(result).to be_nil\nend\n", encoding="utf-8")
            self.assertTrue(extract_tests(path)[0][1])


if __name__ == "__main__":
    unittest.main()
