#!/usr/bin/env python3
"""Isolated mutation probes: verifies original regression tests fail when P1 guards regress.

Mutants are written ONLY to temporary directories; app source is never changed.
A successful probe is one expected assertion failure with zero harness errors.
"""
from __future__ import annotations
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RUBY = ROOT / 'api/spec/regression/critical_contract_test.rb'
MUTANTS = [
    {
        'id': 'SESSION-02',
        'path': 'api/app/controllers/api/v1/sessions_controller.rb',
        'needle': 'session.active? && session.ready_to_end_at.present? &&',
        'replacement': 'session.active? &&',
        'test': '/SESSION_02/',
    },
    {
        'id': 'FITGAP-04',
        'path': 'api/app/services/fit_gap/engine.rb',
        'needle': 'comparisons = vacancy_skills.map do |vacancy_skill|',
        'replacement': 'comparisons = vacancy_skills.uniq { |s| s.skill_label }.map do |vacancy_skill|',
        'test': '/FITGAP_04/',
    },
    {
        'id': 'PORTFOLIO-01',
        'path': 'api/app/services/portfolios/generator.rb',
        'needle': "raise ArgumentError, 'AI level must be an integer from 1 to 5' unless value.is_a?(Integer) && (1..5).cover?(value)",
        'replacement': 'return value.to_i.clamp(1, 5)',
        'test': '/PORTFOLIO_01/',
    },
    {
        'id': 'INVITE-01',
        'path': 'api/app/models/session.rb',
        'needle': "ENV.fetch('WEB_APP_BASE_URL', 'http://localhost:5173')",
        'replacement': "ENV.fetch('WEB_APP_BASE_URL', 'http://localhost:3001')",
        'test': '/INVITE_01/',
    },
]

def run():
    out = []
    with tempfile.TemporaryDirectory(prefix='quality-phase6-mut-') as tmp:
        base = Path(tmp)
        shutil.copytree(ROOT / 'api/app', base / 'api/app', symlinks=False)
        (base / 'api/spec/regression').mkdir(parents=True)
        shutil.copy2(RUBY, base / 'api/spec/regression/critical_contract_test.rb')
        runner = base / 'api/spec/regression/critical_contract_test.rb'
        for mutation in MUTANTS:
            target = base / mutation['path']
            original = (ROOT / mutation['path']).read_text(encoding='utf-8')
            assert original.count(mutation['needle']) == 1, mutation['id']
            target.write_text(original.replace(mutation['needle'], mutation['replacement']), encoding='utf-8')
            r = subprocess.run(['ruby', str(runner), '--name', mutation['test']],
                               cwd=base, text=True, capture_output=True, timeout=15)
            target.write_text(original, encoding='utf-8')
            summary = re.search(r'(\d+) runs, (\d+) assertions, (\d+) failures, (\d+) errors, (\d+) skips', r.stdout)
            passed = (r.returncode != 0 and summary is not None and
                      int(summary.group(1)) == 1 and int(summary.group(3)) >= 1 and int(summary.group(4)) == 0)
            out.append({'mutation': mutation['id'], 'expected_assertion_failure': bool(passed),
                        'exit_code': r.returncode, 'test_summary': summary.group(0) if summary else None,
                        'stderr_excerpt': r.stderr[-500:]})
    result = {'result': 'PASS' if all(x['expected_assertion_failure'] for x in out) else 'FAIL',
              'mutants': out, 'original_source_modified': False}
    print(json.dumps(result, indent=2))
    return 0 if result['result'] == 'PASS' else 1

if __name__ == '__main__':
    raise SystemExit(run())
