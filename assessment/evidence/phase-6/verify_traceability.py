#!/usr/bin/env python3
"""Compare Phase 3 planned test IDs with source files and actually executed local layers.

A source-token match is presence evidence, NOT proof that the scenario is covered.
"""
from __future__ import annotations
import json
from pathlib import Path

root = Path(__file__).resolve().parents[3]
catalog = json.loads((root/'assessment/design/phase-3-test-catalog.json').read_text())
suites = (list((root/'api/spec').rglob('*.rb'))+
          list((root/'web/tests').glob('*.mjs'))+
          list((root/'scripts').glob('test_*.py')))
records=[]
for finding in catalog['findings']:
 for t in finding['tests']:
  sid=t['id']; appearances=[]
  for f in suites:
   s=f.read_text(encoding='utf-8')
   if sid in s or sid.replace('-','_') in s:
    appearances.append(str(f.relative_to(root)))
  executed=[f for f in appearances if f.startswith('api/spec/regression/') or f.startswith('web/tests/') or f.startswith('scripts/test_')]
  unexecuted=[f for f in appearances if f.startswith('api/spec/') and not f.startswith('api/spec/regression/')]
  # scripts/test_validate_pr_inputs mentions SESSION-01 as fixture metadata,
  # but a policy fixture is NOT evidence of application session testing.
  if not sid.startswith(('TEST-GATE','DOR-','RELEASE-GATE')):
   executed=[f for f in executed if not f.startswith('scripts/')]
  if executed:
   status='PARTIAL_EXECUTED_LOCAL'
  elif unexecuted:
   status='AUTHORED_NOT_RUN'
  else:
   status='MISSING'
  records.append({'finding':finding['finding'],'requirement':finding['requirement'],
                  'acceptance':finding['acceptance'],'test_id':sid,
                  'planned_path':t.get('path') or t.get('test_path') or '',
                  'found_paths':appearances, 'executed_local_layer':executed,
                  'authored_not_run':unexecuted,'status':status})
stats={state:sum(r['status']==state for r in records) for state in ['PARTIAL_EXECUTED_LOCAL','AUTHORED_NOT_RUN','MISSING']}
assert len(records)==len({r['test_id'] for r in records}) and len(records)==41
out={'total_planned':len(records),'total_findings':len(catalog['findings']),
     'status_counts':stats,'disclaimer':'Token presence is not full assertion coverage; no Rails/DB/WS/browser proof.',
     'tests':records}
(root/'assessment/evidence/phase-6/traceability-verification.json').write_text(json.dumps(out,indent=2)+'\n')
rows=['# Phase 6 — Independent Traceability Verification','',
      '> This supersedes stale Phase 3 **follow-through** placeholders without rewriting its historical design catalog. Presence of a test ID is only a weak indicator of coverage; inspect assertions and run integration tests before claiming scenario completeness.',
      '',f'- Planned test IDs: **{len(records)}** across **{len(catalog["findings"])}** findings.',
      f'- Executed local contract/policy test ID references: **{stats["PARTIAL_EXECUTED_LOCAL"]}** (partial contract only).',
      f'- Authored Rails/DB spec references not executed: **{stats["AUTHORED_NOT_RUN"]}**.',
      f'- No matching implemented test references: **{stats["MISSING"]}**.',
      '- **No test in this report is certified against production or a running Rails HTTP/DB/WS stack.**',
      '', '| Finding | Planned ID | Current evidence | Actual test file(s) |',
      '|---|---|---|---|']
for r in records:
 paths=', '.join('`'+p+'`' for p in r['found_paths']) or '—'
 rows.append(f"| {r['finding']} | `{r['test_id']}` | {r['status']} | {paths} |")
rows += ['', '## Unresolved verification gaps',
 '- No authenticated request/response + persisted database parity was executed.',
 '- Rails integration specs are syntax-checked but not executable in current environment.',
 '- Existing `INVITE-03` Node check validates URL configuration only; it does **not** prove rendered/copy-link behavior promised by the original catalog.',
 '- Existing `AUTH-TENANT-01/02` Minitest harness uses doubles; it does **not** validate actual tenant-scoped SQL or authorization end-to-end.',
 '- A later PR should cite actual test cases, validated assertions, reviewer acceptance, and CI links; these are not yet available.',
 '- `FIND-011` tenant membership acceptance rules remain unspecified and security-relevant; keep P1 OPEN.',
 '']
(root/'assessment/06-traceability-verification.md').write_text('\n'.join(rows))
print(json.dumps(stats,sort_keys=True))
