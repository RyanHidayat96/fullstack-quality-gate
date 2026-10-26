#!/usr/bin/env python3
"""Phase 3 design integrity checks only, NOT runtime regression tests."""
from pathlib import Path
import json, hashlib, re, sys
root=Path(__file__).resolve().parents[3]
ass=root/'assessment'
manifest=json.loads((ass/'PHASE_0_FILE_INVENTORY.json').read_text())
catalog=json.loads((ass/'design/phase-3-test-catalog.json').read_text())
audit=(ass/'01-audit.md').read_text()
issues=[]
summary={'phase':3,'scope':'design_validation_only','runtime_tests_executed':0,'pr_checks_executed':0,'github_repo_created':False}
orig=[]
for e in manifest['entries']:
    p=root/e['path']
    if not p.exists(): issues.append(f'missing original: {e["path"]}');continue
    if hashlib.sha256(p.read_bytes()).hexdigest()!=e['sha256']:
        issues.append(f'modified original: {e["path"]}')
    orig.append(e['path'])
summary['original_source_expected']=manifest['original_file_count']
summary['original_source_verified']=len(orig)
summary['original_source_modified']=len([e for e in issues if e.startswith('modified original')])
audit_findings=set(re.findall(r'^### (FIND-\d{3}) ',audit,re.M))
cat_findings={f['finding'] for f in catalog['findings']}
summary['audit_findings']=len(audit_findings)
summary['catalog_findings']=len(cat_findings)
summary['p1_findings']=sum(f['severity']=='P1' for f in catalog['findings'])
summary['p2_findings']=sum(f['severity']=='P2' for f in catalog['findings'])
if audit_findings != cat_findings: issues.append(f'finding mismatch: {sorted(audit_findings^cat_findings)}')
if summary['p1_findings']!=8 or summary['p2_findings']!=5: issues.append('severity count mismatch')
all_ids=[]
trace=(ass/'03-traceability.md').read_text()
for f in catalog['findings']:
    if not (root/f['source']).is_file():issues.append('source path missing: '+f['source'])
    if not f['requirement'].startswith('REQ-') or not f['acceptance'].startswith('AC-'):issues.append('invalid requirement identifiers: '+f['finding'])
    if f['finding'] not in trace:issues.append('traceability lacks '+f['finding'])
    if f['severity']=='P1' and not f['tests']:issues.append('P1 has no tests '+f['finding'])
    for t in f['tests']:
        tid=t['id'];all_ids.append(tid)
        if tid not in trace:issues.append('traceability lacks test '+tid)
        if t['status']!='PLANNED_NOT_IMPLEMENTED':issues.append('unjustified execution status '+tid)
        if (root/t['planned_file']).exists():issues.append('test target already exists; verify status '+t['planned_file'])
        if not t['assertion'].strip():issues.append('missing expected assertion '+tid)
summary['planned_test_ids']=len(all_ids)
summary['unique_test_ids']=len(set(all_ids))
if len(set(all_ids))!=len(all_ids): issues.append('duplicate test IDs')
for f in ['03-quality-architecture.md','03-quality-gate-contract.md','03-traceability.md']:
    p=ass/f
    if not p.is_file() or len(p.read_text().splitlines())<75:issues.append('missing or shallow design doc: '+f)
    if re.search('rakamin|ai-interview-platform|ai.interview',p.read_text(),re.I):issues.append('hiring brand or product mention in public-facing designed docs: '+f)
summary['written_design_files']=['assessment/03-quality-architecture.md','assessment/03-quality-gate-contract.md','assessment/03-traceability.md','assessment/design/phase-3-test-catalog.json']
summary['errors']=issues
summary['status']='PASS_DESIGN_VALIDATION' if not issues else 'FAIL_DESIGN_VALIDATION'
(ass/'evidence/phase-3/design-validation.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
sys.exit(0 if not issues else 1)
