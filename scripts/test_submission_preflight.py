"""Only synthetic fixtures; not representations of real GitHub submissions."""
import json
import tempfile
import unittest
from pathlib import Path
from submission_preflight import REQUIRED, _github_html_url, _local_md_links, run_preflight


class Phase8PreflightTests(unittest.TestCase):
    def test_url_parser_rejects_fake_or_external_urls(self):
        self.assertFalse(_github_html_url('http://github.com/a/b', 'repo'))
        self.assertFalse(_github_html_url('https://github.com.evil.test/a/b', 'repo'))
        self.assertFalse(_github_html_url('https://github.com/a/b/pull/not-a-number', 'pr'))
        self.assertFalse(_github_html_url('https://github.com/a/b/actions/runs/x', 'run'))
        self.assertFalse(_github_html_url('https://github.com/example/b', 'repo'))

    def test_url_parser_accepts_plausible_shapes_only(self):
        self.assertTrue(_github_html_url('https://github.com/synthetic-user/synthetic-repo', 'repo'))
        self.assertTrue(_github_html_url('https://github.com/synthetic-user/synthetic-repo/pull/17', 'pr'))
        self.assertTrue(_github_html_url('https://github.com/synthetic-user/synthetic-repo/actions/runs/456', 'run'))

    def test_broken_local_markdown_link_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = Path(tmp)
            (r / 'README.md').write_text('[missing](missing.txt)\n')
            bad = _local_md_links(r)
            self.assertEqual(len(bad), 1)

    def test_good_relative_markdown_link_is_accepted(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = Path(tmp)
            (r / 'README.md').write_text('[doc](assessment/test.md)\n')
            (r / 'assessment').mkdir()
            (r / 'assessment/test.md').write_text('test')
            self.assertEqual(_local_md_links(r), [])

    def test_missing_external_evidence_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name in REQUIRED:
                p = root / name
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text('document')
            (root / 'assessment/release-readiness.json').write_text(json.dumps({
                'p1_findings': [{'id': 'FIND-X', 'state': 'OPEN'}],
                'mandatory_verifications': {'api_db_integration': {'status': 'BLOCKED'}}
            }))
            report = run_preflight(root, root / 'assessment/submission-evidence.json')
            self.assertEqual(report['status'], 'BLOCKED')
            self.assertIn('FIND-X', report['unresolved_p1_ids'])
            self.assertFalse(report['checks']['tag_specific_remote_ci_verified'])

    def test_self_declared_remote_evidence_cannot_bypass_local_tag(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name in REQUIRED:
                p = root / name
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text('document')
            (root / 'assessment/release-readiness.json').write_text(json.dumps({
                'candidate_tag': 'v9.9.9', 'p1_findings': [{'id':'FIND-X','state':'VERIFIED_FIXED'}],
                'mandatory_verifications': {k:{'status':'VERIFIED'} for k in
                    ('api_db_integration','frontend_build','component_regression','browser_api_db_journey',
                     'traceability_complete','spec_acceptance_approved','publication_clearance',
                     'two_real_pr_demonstrations','release_approval')}
            }))
            fake = root / 'assessment/submission-evidence.json'
            fake.write_text(json.dumps({
                'public_independent_repo': {'url':'https://github.com/synthetic-user/synthetic-repo',
                    'independent_not_fork':True,'owner_verified':True},
                'tag_commit':{'name':'v9.9.9','sha':'a'*40},
                'tag_ci_run':{'url':'https://github.com/synthetic-user/synthetic-repo/actions/runs/456',
                    'tag':'v9.9.9','sha':'a'*40,'verified_by_human':True,'outcome':'BLOCKED'},
                'publication_clearance':True
            }))
            report = run_preflight(root,fake)
            self.assertFalse(report['checks']['tag_commit_bound'])
            self.assertEqual(report['status'],'BLOCKED')


if __name__ == '__main__':
    unittest.main()
