"""TEST-GATE-06: prevent common fail-open pipeline misconfigurations.

Static guard, not a replacement for actual GitHub checks or branch rules.
"""
import re
import unittest
from pathlib import Path

PATH = Path(__file__).resolve().parents[1] / '.github/workflows/quality.yml'
REQUIRED = {'policy-unit', 'pr-inputs', 'api-contract', 'api-critical', 'web-quality', 'quality-summary'}


def check_workflow(content):
    jobs = set(re.findall(r'^  ([a-z][a-z-]+):\s*$', content, flags=re.M))
    missing = REQUIRED - jobs
    if missing:
        raise ValueError('Required CI jobs missing: ' + ', '.join(sorted(missing)))
    if re.search(r'\bcontinue-on-error\s*:', content) or re.search(r'\|\|\s*(?:true|:)(?:\s|$)', content):
        raise ValueError('Fail-open command or continue-on-error not allowed')
    if re.search(r'^\s*pull_request_target\s*:', content, re.M):
        raise ValueError('Do not run untrusted changes in pull_request_target')
    if not all(x in content for x in ('pull_request:', 'push:', 'permissions:', 'contents: read')):
        raise ValueError('Expected least privilege and PR/push triggers')
    block = content.split('  quality-summary:', 1)[-1]
    if 'needs: [policy-unit, pr-inputs, api-contract, api-critical, web-quality]' not in block or 'if: always()' not in block:
        raise ValueError('Summary must require ALL checks and run regardless of failure')
    if '[[ "$INPUTS" == skipped ]]' not in block or '[[ "$INPUTS" == success ]]' not in block:
        raise ValueError('Only non-PR may skip pr-inputs')
    if 'web/package-lock.json' not in content or 'npm ci' not in content or 'bundle exec rspec' not in content:
        raise ValueError('Required reproducibility/build checks missing')
    # The PR can edit its own scripts; do not run the gate implementation from PR HEAD.
    if not re.search(r'(?m)^\s*ref: \$\{\{ github\.event\.pull_request\.base\.sha \}\}\s*$', content):
        raise ValueError('PR validator must be checked out from the target base SHA')
    if not re.search(r'(?m)^\s*path: \.trusted-policy\s*$', content):
        raise ValueError('Trusted baseline checkout path missing')
    if 'python .trusted-policy/scripts/validate_pr_inputs.py --repo . --event "$GITHUB_EVENT_PATH"' not in content:
        raise ValueError('PR validator must execute the trusted base script')
    if re.search(r'(?m)^\s*run: python scripts/validate_pr_inputs\.py ', content):
        raise ValueError('Do not execute PR HEAD validator')
    return True


class WorkflowContractTests(unittest.TestCase):
    def setUp(self):
        self.workflow = PATH.read_text(encoding='utf8')

    def test_valid_workflow(self):
        self.assertTrue(check_workflow(self.workflow))

    def test_no_silent_skip_of_web(self):
        with self.assertRaises(ValueError):
            check_workflow(self.workflow.replace('  web-quality:\n', '  web-quality-disabled:\n'))

    def test_no_fail_open(self):
        with self.assertRaises(ValueError):
            check_workflow(self.workflow+'\n      continue-on-error: true\n')

    def test_no_pull_request_target(self):
        with self.assertRaises(ValueError):
            check_workflow(self.workflow.replace('  pull_request:', '  pull_request_target:'))

    def test_no_missing_rspects(self):
        with self.assertRaises(ValueError):
            check_workflow(self.workflow.replace('bundle exec rspec', 'echo rspec'))

    def test_pr_validator_cannot_run_from_untrusted_head(self):
        with self.assertRaises(ValueError):
            check_workflow(self.workflow.replace('.trusted-policy/scripts/validate_pr_inputs.py',
                                                 'scripts/validate_pr_inputs.py'))

    def test_pr_validator_requires_trusted_base_sha(self):
        with self.assertRaises(ValueError):
            check_workflow(self.workflow.replace('github.event.pull_request.base.sha',
                                                 'github.event.pull_request.head.sha'))

    def test_no_unrequired_summary(self):
        with self.assertRaises(ValueError):
            check_workflow(self.workflow.replace('if: always()', 'if: success()'))


if __name__ == '__main__':
    unittest.main()
