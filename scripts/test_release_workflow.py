"""Static workflow contract. Does not represent a GitHub Actions execution."""
import unittest
from pathlib import Path


WORKFLOW = Path(__file__).resolve().parents[1] / '.github/workflows/quality.yml'


class ReleaseWorkflowContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workflow = WORKFLOW.read_text(encoding='utf-8')

    def test_version_tags_trigger_workflow(self):
        self.assertIn("tags: ['v*']", self.workflow)

    def test_release_decision_fails_when_upstream_skipped_or_failed(self):
        s = self.workflow.split('  release-decision:', 1)[1]
        self.assertIn('if: always()', s)
        for check in ('policy-unit', 'api-contract', 'api-critical', 'web-quality', 'quality-summary'):
            self.assertIn(check, s)

    def test_exact_tag_commit_binding_is_verified(self):
        s = self.workflow.split('  release-decision:', 1)[1]
        self.assertIn('TAG_COMMIT=$(git rev-parse', s)
        self.assertIn('"$TAG_COMMIT" == "$GITHUB_SHA"', s)
        self.assertIn('RELEASE_TAG_BINDING: ${{ steps.tag-binding.outputs.match }}', s)

    def test_release_verdict_fails_job_and_uploads_blocked_evidence(self):
        s = self.workflow.split('  release-decision:', 1)[1]
        self.assertIn('python scripts/release_gate.py', s)
        self.assertIn('Upload evidence even when release is blocked', s)
        self.assertNotIn('continue-on-error:', s)
        self.assertIn('if: always()', s)

    def test_release_job_uses_read_only_permissions(self):
        s = self.workflow.split('  release-decision:', 1)[1]
        self.assertIn('contents: read', s)
        self.assertIn('persist-credentials: false', s)


if __name__ == '__main__':
    unittest.main()
