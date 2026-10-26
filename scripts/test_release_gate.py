"""Independent, synthetic unit tests for fail-closed release policy."""
import json
import tempfile
import unittest
from pathlib import Path

from release_gate import EVIDENCE_KEYS, REQUIRED_JOBS, audit_p1_states, evaluate


TAG = 'refs/tags/v0.1.0-rc1'
SHA = 'a' * 40
JOBS = {**{name: 'success' for name in REQUIRED_JOBS}, 'pr-inputs': 'skipped'}


class ReleaseGateTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        (self.root / 'assessment').mkdir()
        (self.root / 'assessment/evidence').mkdir()
        (self.root / 'assessment/evidence/verified.txt').write_text('Synthetic test artifact, not a real CI run.')
        self.audit = self.root / 'assessment/01-audit.md'
        self.audit.write_text('| Rank / ID | Severity | Description | Classification | Evidence | State | Release |\n'
                              '|---|---|---|---|---|---|---|\n'
                              '| 1 · FIND-001 | **P1** | test | any | SRC | VERIFIED_FIXED | CLEAR |\n')
        self.controls = {
            'schema_version': 1,
            'candidate_tag': 'v0.1.0-rc1',
            'p1_findings': [{'id': 'FIND-001', 'state': 'VERIFIED_FIXED',
                             'evidence_paths': ['assessment/evidence/verified.txt']}],
            'mandatory_verifications': {key: {'status': 'VERIFIED', 'evidence_paths':
                                        ['assessment/evidence/verified.txt']} for key in EVIDENCE_KEYS},
        }
        self.save()

    def save(self):
        (self.root / 'assessment/release-readiness.json').write_text(json.dumps(self.controls))

    def evaluate(self, ref=TAG, sha=SHA, jobs=None, tag_binding='verified'):
        return evaluate(self.root, ref, sha, JOBS if jobs is None else jobs, tag_binding)

    def blocked(self, phrase):
        result = self.evaluate()
        self.assertEqual('BLOCKED', result['release_status'])
        self.assertIn(phrase, '\n'.join(result['blockers']))

    def test_synthetic_all_verified_controls_can_be_releasable(self):
        result = self.evaluate()
        self.assertEqual('RELEASABLE', result['release_status'])
        self.assertEqual([], result['blockers'])

    def test_fails_without_tag_or_sha(self):
        result = self.evaluate('', '', {})
        self.assertEqual('BLOCKED', result['release_status'])
        self.assertTrue(any('tag not verified' in b for b in result['blockers']))

    def test_missing_tag_binding_blocks_even_when_everything_else_passes(self):
        self.assertEqual('BLOCKED', self.evaluate(tag_binding='unverified')['release_status'])

    def test_prevent_unrelated_main_run_substitution(self):
        self.assertEqual('BLOCKED', self.evaluate('refs/heads/main')['release_status'])

    def test_missing_or_failed_critical_job_blocks(self):
        for name in REQUIRED_JOBS:
            with self.subTest(job=name):
                self.assertEqual('BLOCKED', self.evaluate(jobs={**JOBS, name: 'failure'})['release_status'])

    def test_non_pr_job_must_be_skipped(self):
        self.assertEqual('BLOCKED', self.evaluate(jobs={**JOBS, 'pr-inputs': 'missing'})['release_status'])

    def test_unresolved_p1_blocks_even_when_all_ci_green(self):
        self.audit.write_text(self.audit.read_text().replace('VERIFIED_FIXED', 'OPEN'))
        self.controls['p1_findings'][0]['state'] = 'OPEN'
        self.save()
        self.blocked('FIND-001: P1 not closed')

    def test_code_fix_without_integration_verification_blocks(self):
        self.audit.write_text(self.audit.read_text().replace('VERIFIED_FIXED', 'CODE_FIXED_UNVERIFIED'))
        self.controls['p1_findings'][0]['state'] = 'CODE_FIXED_UNVERIFIED'
        self.save()
        self.blocked('CODE_FIXED_UNVERIFIED')

    def test_missing_or_renamed_finding_blocks(self):
        self.controls['p1_findings'].clear()
        self.save()
        self.blocked('register/audit disagreement')

    def test_register_and_audit_disagreement_blocks(self):
        self.controls['p1_findings'][0]['state'] = 'OPEN'
        self.save()
        self.blocked('differs from audit index')

    def test_missing_mandatory_evidence_blocks(self):
        self.controls['mandatory_verifications']['frontend_build'] = {'status': 'BLOCKED', 'evidence_paths': []}
        self.save()
        self.blocked('frontend_build')

    def test_nonexistent_local_evidence_does_not_clear_gate(self):
        self.controls['p1_findings'][0]['evidence_paths'] = ['assessment/evidence/missing.log']
        self.save()
        self.blocked('no valid repository-local evidence')

    def test_traversal_and_remote_link_not_accepted_as_executed_evidence(self):
        for path in ('../../etc/hosts', 'https://example.com/test-log'):
            with self.subTest(path=path):
                self.controls['mandatory_verifications']['api_db_integration']['evidence_paths'] = [path]
                self.save()
                self.blocked('api_db_integration')

    def test_missing_audit_blocks(self):
        self.audit.unlink()
        self.blocked('Unable to verify severity-ranked audit')

    def test_missing_readiness_blocks(self):
        (self.root / 'assessment/release-readiness.json').unlink()
        self.blocked('Unable to verify release readiness')

    def test_mismatched_candidate_tag_blocks(self):
        self.controls['candidate_tag'] = 'v2.0.0'
        self.save()
        self.blocked('does not match')

    def test_risk_acceptance_requires_real_owner_and_document(self):
        self.audit.write_text(self.audit.read_text().replace('VERIFIED_FIXED', 'ACCEPTED_RISK'))
        self.controls['p1_findings'][0]['state'] = 'ACCEPTED_RISK'
        self.controls['p1_findings'][0]['risk_acceptance'] = {'owner': 'TBD'}
        self.save()
        self.blocked('incomplete named risk acceptance')

    def test_audit_index_must_not_be_missing(self):
        self.audit.write_text('# Empty index\n')
        self.blocked('no P1 finding index')

    def test_repeated_finding_id_blocks(self):
        self.controls['p1_findings'].append(dict(self.controls['p1_findings'][0]))
        self.save()
        self.blocked('Duplicate P1 IDs')

    def test_audit_parser_detects_real_markdown_p1_state(self):
        self.assertEqual({'FIND-001': 'VERIFIED_FIXED'}, audit_p1_states(self.audit.read_text()))


if __name__ == '__main__':
    unittest.main()
