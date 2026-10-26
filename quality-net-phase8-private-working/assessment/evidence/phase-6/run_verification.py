#!/usr/bin/env python3
"""Repeat independent, available local checks and record exact exit codes.

No networks, production DB, external environments or remote repositories are touched.
"""
from __future__ import annotations
import json
import os
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = ROOT/'assessment/evidence/phase-6'
EVIDENCE.mkdir(exist_ok=True,parents=True)
checks=[]

def run(label, args, cwd=ROOT, env=None, timeout=35, expected=None):
    try:
        p=subprocess.run(args,cwd=cwd,env=env,capture_output=True,text=True,timeout=timeout)
        ret=p.returncode;output=f'$ {" ".join(args)}\n[exit_code] {ret}\n\n[stdout]\n{p.stdout}\n[stderr]\n{p.stderr}'
    except (OSError,subprocess.TimeoutExpired) as exc:
        ret=124;output=f'$ {" ".join(args)}\n[exit_code] {ret}\n{type(exc).__name__}: {exc}\n'
    (EVIDENCE/f'{label}.log').write_text(output)
    checks.append({'id':label,'command':args,'exit_code':ret,'expected_exit_code':expected,
                   'status':('PASS' if ret==expected else ('BLOCKED_OR_FAILED' if expected==0 else 'OBSERVED'))})
    return ret

for i in range(3):
    run(f'repeat-{i+1}-ruby',['ruby','api/spec/regression/critical_contract_test.rb','--seed',str(11+i*413)],expected=0)
    run(f'repeat-{i+1}-policy',['python3','-m','unittest','discover','-s','scripts','-p','test_*.py','-q'],expected=0)
    run(f'repeat-{i+1}-web',['node','--test','web/tests/api_config.test.mjs'],expected=0)

run('final-mutation',['python3','assessment/evidence/phase-6/run_mutation_probes.py'],expected=0)
run('final-traceability',['python3','assessment/evidence/phase-6/verify_traceability.py'],expected=0)
run('web-typecheck',['tsc','--noEmit','--project','web/tsconfig.json'],expected=0)
run('web-build',['npm','run','build'],cwd=ROOT/'web',expected=0)
run('web-offline-install',['npm','ci','--offline','--ignore-scripts','--no-audit','--no-fund'],cwd=ROOT/'web',expected=0)
run('rails-bundle-check',['ruby','-rbundler','-e',"puts 'Bundler: ' + Bundler::VERSION; abort 'Rails gem unavailable' unless Gem::Specification.find_all_by_name('rails').any?"],cwd=ROOT/'api',expected=0)
run('rails-rspec-attempt',['ruby','-e',"require 'rspec/core'"],cwd=ROOT/'api',expected=0)
# inspect Ruby parse without external dependencies
rbs=sorted((ROOT/'api').rglob('*.rb'))
syntax_errors=[]
for f in rbs:
 p=subprocess.run(['ruby','-c',str(f)],capture_output=True,text=True)
 if p.returncode: syntax_errors.append({'file':str(f.relative_to(ROOT)),'message':p.stderr[-400:]})
(EVIDENCE/'all-ruby-syntax.json').write_text(json.dumps({'total_checked':len(rbs),'errors':syntax_errors,'result':'PASS' if not syntax_errors else 'FAIL'},indent=2)+'\n')
checks.append({'id':'all-ruby-syntax','command':['ruby','-c','api/**/*.rb'],'exit_code':0 if not syntax_errors else 1,'expected_exit_code':0,'status':'PASS' if not syntax_errors else 'BLOCKED_OR_FAILED'})
# Parse Github YAML but don't execute Actions.
try:
 import yaml
 wf=yaml.safe_load((ROOT/'.github/workflows/quality.yml').read_text())
 assert isinstance(wf.get('jobs'),dict) and len(wf['jobs'])==6
 val={'result':'PARSED','jobs':sorted(wf['jobs']), 'note':'Parser check is not a GitHub-hosted execution'}
except Exception as e:
 val={'result':'FAIL','error':str(e)}
(EVIDENCE/'workflow-yaml-parse.json').write_text(json.dumps(val,indent=2)+'\n')
checks.append({'id':'workflow-yaml-parse','exit_code':0 if val['result']=='PARSED' else 1,'expected_exit_code':0,'status':'PASS' if val['result']=='PARSED' else 'BLOCKED_OR_FAILED'})
# Check JS files using Node builtin syntax checker; TS/TSX require dependencies.
jsfiles=sorted([*ROOT.glob('web/*.js'), *ROOT.glob('web/src/**/*.js'), *ROOT.glob('web/public/*.js'), *ROOT.glob('web/tests/*.mjs')])
node_errors=[]
for f in jsfiles:
 p=subprocess.run(['node','--check',str(f)],capture_output=True,text=True)
 if p.returncode: node_errors.append({'file':str(f.relative_to(ROOT)),'message':p.stderr[-400:]})
(EVIDENCE/'node-js-syntax.json').write_text(json.dumps({'total_checked':len(jsfiles),'errors':node_errors},indent=2)+'\n')
checks.append({'id':'node-js-syntax','exit_code':0 if not node_errors else 1,'expected_exit_code':0,'status':'PASS' if not node_errors else 'BLOCKED_OR_FAILED'})
# Hard block on functional runtime, regardless of local source contracts.
result={'phase':'6','scope':'LOCAL_INDEPENDENT_VERIFICATION', 'checks':checks,
        'runtime_integration_executed':False,'github_pull_requests_executed':False,'release_status':'BLOCKED',
        'note':'Failed/blocked mandatory commands remain nonzero and are never reported as passing.'}
(EVIDENCE/'phase-6-checks.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'successful_checks':[x['id'] for x in checks if x['status']=='PASS'],
                  'blocked_or_failed':[x['id'] for x in checks if x['status']!='PASS'],
                  'ruby_syntax_files':len(rbs),'js_syntax_files':len(jsfiles)},indent=2))
