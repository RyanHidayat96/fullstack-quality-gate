"""Offline adversarial contract tests for scripts/validate_pr_inputs.py.

Run: python3 -m unittest discover -s scripts -p 'test_*.py' -v
"""
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from validate_pr_inputs import GateError, validate, main


class PolicyGateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        for d in ['assessment/design', 'assessment/requirements', 'assessment/criteria',
                  'assessment/designs', 'api/app', 'api/spec/requests', 'scripts']:
            (self.root / d).mkdir(parents=True, exist_ok=True)
        catalog = {"findings": [{"finding": "FIND-002", "requirement": "REQ-SESSION-001",
                                "acceptance": "AC-SESSION-001", "tests": [{"id": "SESSION-01"}]}]}
        (self.root / 'assessment/design/phase-3-test-catalog.json').write_text(json.dumps(catalog))
        self.spec = 'assessment/requirements/REQ-SESSION-001.md'
        self.ac = 'assessment/criteria/AC-SESSION-001.md'
        self.design = 'assessment/designs/DES-SESSION-001.md'
        self.test = 'api/spec/requests/session_completion_spec.rb'
        self.code = 'api/app/session.rb'
        (self.root / self.spec).write_text('''# Session spec
- Requirement ID: REQ-SESSION-001
- Status: PROPOSED
- Source: Source invariant in audited controller
- Problem / affected actor: candidate session integrity
- Expected behavior / business rule: pending interview cannot finish
- In scope / out of scope: session endpoint / unrelated routes
- Owner: backend engineering reviewer
- Unknowns / assumptions: readiness condition needs approval
''')
        (self.root / self.ac).write_text('''# Session completion
- Acceptance ID: AC-SESSION-001
- Requirement: REQ-SESSION-001
- Test IDs: SESSION-01
- Given: pending candidate interview session
- When: audio complete request is sent
- Then: response denies and stored session remains pending
- Negative/boundary scenario: ended session remains idempotent
''')
        (self.root / self.design).write_text('''# Readiness guard
- Design ID: DES-SESSION-001
- Requirement: REQ-SESSION-001
- Acceptance IDs: AC-SESSION-001
- Planned test IDs: SESSION-01
- Affected layers: API and database
- Proposed solution: require persisted server readiness to complete
- Data migration / backwards compatibility: maintain existing session rows
- Alternatives and trade-offs: async readiness token requires stronger audit
- Failure handling and rollback: reject invalid transitions with no DB write
- Risks and open questions: server handshake needs formal signoff
''')
        (self.root / self.code).write_text('class Session; end\n')
        (self.root / self.test).write_text("RSpec.describe 'SESSION-01' do\n  it('rejects pending completion') do\n    expect(false).to be(false)\n  end\nend\n")
        self.changed = [self.code, self.test, self.spec, self.ac, self.design]
        self.body = f'''## Linked engineering inputs
Spec: {self.spec}
Acceptance: {self.ac}
Design: {self.design}
Findings: FIND-002
Tests: SESSION-01
Risk: high
Affected paths: {self.code}, {self.test}
Exemption: none
Justification: code requires tests
'''

    def assert_blocked(self, body=None, changed=None):
        with self.assertRaises(GateError):
            validate(self.root, self.body if body is None else body, self.changed if changed is None else changed)

    def test_DOR_04_positive_metadata_only(self):
        result = validate(self.root, self.body, self.changed)
        self.assertEqual('METADATA_PASS', result['result'])
        self.assertFalse(result['tests_executed'])

    def test_TEST_GATE_06_positive_metadata_requires_human_review(self):
        result = validate(self.root, self.body, self.changed)
        self.assertTrue(result['human_review_required'])
        self.assertEqual('METADATA_PASS', result['result'])
        self.assertFalse(result['tests_executed'])

    def test_DOR_01_missing_spec(self):
        self.assert_blocked(self.body.replace(f'Spec: {self.spec}', ''))

    def test_DOR_02_bad_acceptance(self):
        self.assert_blocked(self.body.replace(f'Acceptance: {self.ac}', 'Acceptance: TBD'))

    def test_DOR_03_missing_design(self):
        self.assert_blocked(self.body.replace(f'Design: {self.design}', ''))

    def test_TEST_GATE_01_no_new_test(self):
        self.assert_blocked(changed=[self.code, self.spec, self.ac, self.design])

    def test_TEST_GATE_03_traversal(self):
        self.assert_blocked(self.body.replace(self.spec, 'assessment/requirements/../designs/DES-SESSION-001.md'))

    def test_TEST_GATE_03_external_url(self):
        self.assert_blocked(self.body.replace(self.spec, 'https://example.invalid/spec.md'))

    def test_TEST_GATE_03_symlink_escape(self):
        path = self.root / self.spec
        path.unlink()
        path.symlink_to('/etc/hosts')
        self.assert_blocked()

    def test_duplicate_field(self):
        self.assert_blocked(self.body+'\nSpec: '+self.spec+'\n')

    def test_broken_req_reference(self):
        path = self.root / self.ac
        path.write_text(path.read_text().replace('Requirement: REQ-SESSION-001', 'Requirement: REQ-SESSION-999'))
        self.assert_blocked()

    def test_unknown_test_id(self):
        self.assert_blocked(self.body.replace('Tests: SESSION-01', 'Tests: SESSION-77'))

    def test_test_id_must_appear_in_changed_test_file(self):
        path = self.root / self.test
        path.write_text(path.read_text().replace('SESSION-01', 'OTHER-01'))
        self.assert_blocked()

    def test_affected_paths_must_be_changed(self):
        self.assert_blocked(self.body.replace('Affected paths: '+self.code+', '+self.test,
                                               'Affected paths: api/app/other.rb'))

    def test_POLICY_change_requires_policy_tests_and_high_risk(self):
        self.assert_blocked(changed=self.changed + ['.github/workflows/quality.yml'])
        self.assert_blocked(self.body.replace('Risk: high', 'Risk: medium'), changed=self.changed+['.github/workflows/quality.yml'])
        # Fixture itself must be a changed, readable test before policy change can pass.
        policy_path = self.root/'scripts/test_validate_pr_inputs.py'
        policy_path.write_text('# TEST-GATE-01\n# SESSION-01\n')
        changed = self.changed + ['scripts/test_validate_pr_inputs.py', '.github/workflows/quality.yml']
        complete_body = self.body.replace('Affected paths: '+self.code+', '+self.test,
                                         'Affected paths: '+', '.join([self.code, self.test, 'scripts/test_validate_pr_inputs.py', '.github/workflows/quality.yml']))
        self.assertEqual('METADATA_PASS', validate(self.root, complete_body, changed)['result'])

    # TEST-GATE-04: a new executable CI workflow is a policy change too.
    def test_TEST_GATE_04_live_workflow_must_update_trusted_policy_tests(self):
        workflow = '.github/workflows/live-e2e.yml'
        (self.root / '.github/workflows').mkdir(parents=True)
        (self.root / workflow).write_text('name: Live browser E2E\\n')
        self.assert_blocked(changed=self.changed + [workflow])

        fixture = 'scripts/test_validate_pr_inputs.py'
        (self.root / fixture).write_text('# SESSION-01: real policy regression added\\n')
        changed = self.changed + [workflow, fixture]
        full = self.body.replace(
            'Affected paths: ' + self.code + ', ' + self.test,
            'Affected paths: ' + ', '.join([self.code, self.test, workflow, fixture])
        )
        self.assertEqual('METADATA_PASS', validate(self.root, full, changed)['result'])

    def test_gate_rejects_undeclared_changed_code(self):
        # An apparently valid PR must not silently hide additional behavior-changing files.
        extra = 'api/app/more.rb'
        (self.root/extra).write_text('class More; end\n')
        self.assert_blocked(changed=self.changed + [extra])

    def test_gate_rejects_duplicate_affected_path_declarations(self):
        self.assert_blocked(self.body.replace('Affected paths: '+self.code+', '+self.test,
                                              'Affected paths: '+self.code+', '+self.code+', '+self.test))

    def test_gate_accepts_executable_node_mjs_tests(self):
        # The existing frontend test runner uses node:test in .test.mjs files.
        node_test = 'web/tests/session.test.mjs'
        (self.root/'web/tests').mkdir(parents=True, exist_ok=True)
        (self.root/node_test).write_text("import test from 'node:test'; // SESSION-01\n")
        files = [self.code, node_test, self.spec, self.ac, self.design]
        body = self.body.replace(self.test, node_test)
        self.assertEqual('METADATA_PASS', validate(self.root, body, files)['result'])

    def test_DOCS_only_exemption(self):
        body = 'Exemption: DOCS_ONLY\nJustification: only a valid markdown note was modified'
        self.assertEqual('METADATA_PASS', validate(self.root, body, [self.spec])['result'])
        self.assert_blocked(body, [self.code])
        self.assert_blocked('Exemption: DOCS_ONLY\nJustification: TODO', [self.spec])

    def test_DOCS_only_validates_changed_document_content(self):
        (self.root/self.spec).write_text('# Broken\n')
        with self.assertRaises(GateError):
            validate(self.root, 'Exemption: DOCS_ONLY\nJustification: valid changed spec', [self.spec])

    def test_TEST_GATE_02_mere_assertion_does_not_prove_value(self):
        # Metadata cannot prove that expectation is meaningful. Document the honest boundary.
        result = validate(self.root, self.body, self.changed)
        self.assertTrue(result['human_review_required'])
        self.assertFalse(result['tests_executed'])

    def test_valid_real_git_diff_cli_passes_metadata(self):
        def git(*args):
            return subprocess.run(['git', '-C', str(self.root), *args], check=True,
                                  capture_output=True, text=True).stdout.strip()
        git('init', '-q')
        git('config', 'user.name', 'Synthetic Reviewer')
        git('config', 'user.email', 'automation@example.invalid')
        git('add', '.')
        git('commit', '-qm', 'baseline')
        base = git('rev-parse', 'HEAD')
        (self.root/self.code).write_text('class Session; def can_end?; status == "active"; end; end\n')
        (self.root/self.test).write_text('RSpec.describe "SESSION-01" do\n  it("rejects pending") { expect(true).to eq(true) }\nend\n')
        git('add', '.')
        git('commit', '-qm', 'synthetic valid diff')
        head = git('rev-parse', 'HEAD')
        event = {'pull_request': {'body': self.body, 'base': {'sha': base}, 'head': {'sha': head}}}
        path = self.root/'event.json'
        path.write_text(json.dumps(event))
        self.assertEqual(0, main(['--repo', str(self.root), '--event', str(path)]))

    def test_deleted_code_is_in_the_verified_git_diff(self):
        from validate_pr_inputs import changed_files
        def git(*args):
            return subprocess.run(['git', '-C', str(self.root), *args], check=True,
                                  capture_output=True, text=True).stdout.strip()
        git('init', '-q')
        git('config', 'user.name', 'Synthetic Reviewer')
        git('config', 'user.email', 'automation@example.invalid')
        git('add', '.')
        git('commit', '-qm', 'baseline')
        base = git('rev-parse', 'HEAD')
        (self.root / self.code).unlink()
        git('add', '-A')
        git('commit', '-qm', 'delete implementation')
        head = git('rev-parse', 'HEAD')
        self.assertIn(self.code, changed_files(self.root, base, head))

    def test_trusted_base_validator_blocks_self_modified_gate(self):
        """Simulates bypass of an untrusted HEAD validator with a trivial no-op."""
        import sys
        from validate_pr_inputs import changed_files
        original = Path(__file__).with_name('validate_pr_inputs.py').read_text()
        script = self.root / 'scripts/validate_pr_inputs.py'
        script.write_text(original)
        def git(*args):
            return subprocess.run(['git', '-C', str(self.root), *args], check=True,
                                  capture_output=True, text=True).stdout.strip()
        git('init', '-q')
        git('config', 'user.name', 'Synthetic Reviewer')
        git('config', 'user.email', 'automation@example.invalid')
        git('add', '.')
        git('commit', '-qm', 'trusted baseline')
        base = git('rev-parse', 'HEAD')
        (self.root / self.code).write_text('class Session; def bypass?; true; end; end\n')
        script.write_text('raise SystemExit(0)\n') # test fixture only, never production source
        git('add', '.')
        git('commit', '-qm', 'untrusted bypass candidate')
        head = git('rev-parse', 'HEAD')
        event_file = self.root / 'malicious-event.json'
        event_file.write_text(json.dumps({'pull_request': {
            'body': self.body, 'base': {'sha': base}, 'head': {'sha': head}}}))
        compromised = subprocess.run([sys.executable, str(script), '--repo', str(self.root),
                                      '--event', str(event_file)], capture_output=True, text=True)
        self.assertEqual(0, compromised.returncode, 'the attack model must be executable')
        # The trusted policy module is imported from the checker, not PR worktree.
        self.assertEqual(1, main(['--repo', str(self.root), '--event', str(event_file)]))
        self.assertIn('scripts/validate_pr_inputs.py', changed_files(self.root, base, head))

    def test_secure_execution_and_head_validation(self):
        def git(*args):
            return subprocess.run(['git', '-C', str(self.root), *args], check=True,
                                  capture_output=True, text=True).stdout.strip()
        git('init', '-q')
        git('config', 'user.name', 'Automation Test')
        git('config', 'user.email', 'automation@example.invalid')
        git('add', '.')
        git('commit', '-qm', 'initial')
        base = git('rev-parse', 'HEAD')
        (self.root/self.code).write_text('class Session; def active?; true; end; end\n')
        git('add', '.')
        git('commit', '-qm', 'code change')
        head = git('rev-parse', 'HEAD')
        event = {"pull_request": {"body": self.body, "base": {"sha": base}, "head": {"sha": head}}}
        event_file = self.root/'event.json'
        event_file.write_text(json.dumps(event))
        # code change without a changed test on this commit: hard FAIL
        self.assertEqual(1, main(['--repo', str(self.root), '--event', str(event_file)]))


    def test_TEST_GATE_06_ci_contract_enforces_executable_coverage(self):
        from test_ci_contract import check_workflow
        workflow = Path(__file__).resolve().parents[1] / '.github/workflows/quality.yml'
        contents = workflow.read_text(encoding='utf-8')
        self.assertTrue(check_workflow(contents))
        with self.assertRaises(ValueError):
            check_workflow(contents.replace('node --test tests/*.test.mjs', 'echo skipped'))


if __name__ == '__main__':
    unittest.main()
