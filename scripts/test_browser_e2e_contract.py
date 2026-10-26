"""Guard against silently replacing real browser/WebSocket E2E with a mock-only job."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


# TEST-GATE-06: a real browser and WebSocket job is required, not a file-name check.
class BrowserE2EContractTests(unittest.TestCase):
    def test_TEST_GATE_06_browser_and_ws_job_is_executable(self):
        workflow = (ROOT / ".github/workflows/live-e2e.yml").read_text(encoding="utf-8")
        script = (ROOT / "web/e2e/browser_ws_journey.py").read_text(encoding="utf-8")
        for token in (
            "browser-ws-e2e:",
            "bundle exec rails db:migrate",
            "script/seed_browser_e2e.rb",
            "playwright==1.56.0",
            "python web/e2e/browser_ws_journey.py",
            "bundle exec rails server",
            "npm run dev",
        ):
            self.assertIn(token, workflow)
        for token in (
            "sync_playwright()", "get_by_role(", "new WebSocket(url)",
            "candidate", "revoke_invite", "coverage_update",
        ):
            self.assertIn(token, script)

    def test_e2e_requires_test_database(self):
        script = (ROOT / "api/script/seed_browser_e2e.rb").read_text(encoding="utf-8")
        self.assertIn("Rails.env.test?", script)
        browser = (ROOT / "web/e2e/browser_ws_journey.py").read_text(encoding="utf-8")
        self.assertIn('os.environ.get("RAILS_ENV") != "test"', browser)


if __name__ == "__main__":
    unittest.main()
