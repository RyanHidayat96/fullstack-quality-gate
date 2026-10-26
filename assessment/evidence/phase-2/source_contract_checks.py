#!/usr/bin/env python3
"""Read-only audit checks against inspected source snapshot; no app startup or network."""
from pathlib import Path
import json, hashlib, datetime
root=Path(__file__).resolve().parents[3]

def src(path): return (root/path).read_text()

def token_present(path, *tokens):
    data=src(path)
    return all(t in data for t in tokens)
checks=[]
def add(id, description, observed, implication, detail):
    checks.append({'finding':id,'contract':description,'observed':bool(observed),'risk_detected':bool(observed), 'implication':implication,'static_evidence':detail})
add('FIND-001','portfolio reads are not tenant constrained',
    token_present('api/app/controllers/api/v1/portfolios_controller.rb','Portfolio.find(params[:id])') and 'include TenantScoped' not in src('api/app/models/portfolio.rb'),
    'Any role-approved actor may be able to read portfolios outside their tenant via direct IDs; need DB-backed two-tenant test.',
    ['api/app/controllers/api/v1/portfolios_controller.rb:82,104,130,156','api/app/models/portfolio.rb:3-8'])
add('FIND-004','editing vacancy should invalidate cached fit/gap',
    'FitGapReport' not in src('api/app/controllers/api/v1/vacancies_controller.rb') and
    'return json_response(report: fit_gap_json(existing))' in src('api/app/controllers/api/v1/portfolios_controller.rb'),
    'Cached comparison can continue showing the previous expected level after an edited vacancy.',
    ['api/app/controllers/api/v1/vacancies_controller.rb:37-44','api/app/controllers/api/v1/portfolios_controller.rb:116-120'])
add('FIND-007','coverage websocket assessor authentication checks role',
    'JsonWebToken.decode(token)' in src('api/app/channels/coverage_websocket_middleware.rb') and
    'payload[:role]' not in src('api/app/channels/coverage_websocket_middleware.rb'),
    'Signed non-assessor JWT of the same tenant may subscribe to assessor coverage.',
    ['api/app/channels/coverage_websocket_middleware.rb:125-135'])
add('FIND-008','invitation token lifecycle expiration/revocation policy is absent',
    'invite_token' in src('api/db/schema.rb') and 'invite_expires_at' not in src('api/db/schema.rb') and
    'invite_token' in src('api/app/controllers/api/v1/sessions_controller.rb') and 'expired_at' not in src('api/app/controllers/api/v1/sessions_controller.rb'),
    'Invite tokens are long lived absent an externally implemented lifecycle; business policy ambiguous.',
    ['api/db/schema.rb:133-150','api/app/models/session.rb:14-18,35-37','api/app/controllers/api/v1/sessions_controller.rb:118-153'])
add('FIND-009','source snapshot has no automated test suite or CI quality gate',
    not any((root/p).exists() for p in ('api/spec','api/test','web/tests','web/src/__tests__','.github/workflows')) and
    '"test"' not in src('web/package.json'),
    'Cannot prove code is tested or PR/release validation is enforced.',
    ['web/package.json','api/Gemfile','source tree inventory'])
add('FIND-010','no traceable spec and design artifacts included with source snapshot',
    not any((root/p).exists() for p in ('assessment/PRD.md','docs/PRD.md','docs/acceptance-criteria.md','.github/pull_request_template.md')),
    'DoR cannot be substantiated from checked-in files alone; linked wiki may hold specification, not downloaded/verified.',
    ['README.md','assessment/PHASE_0_FILE_INVENTORY.json'])
add('FIND-011','caller-provided tenant choice used during login without membership verification',
    "request.headers['X-Tenant-Scheme'].presence" in src('api/app/controllers/api/v1/authentication_controller.rb') and
    'user.organizations' not in src('api/app/controllers/api/v1/authentication_controller.rb'),
    'Tenant membership policy must be confirmed; cross-tenant token issuance is possible if the header controls scheme.',
    ['api/app/controllers/api/v1/authentication_controller.rb:9-28','api/app/models/user.rb'])
add('FIND-012','README and sample env disagree on backend port and source path',
    'localhost:3000' in src('web/.env.example') and 'localhost:3001' in src('README.md') and '../ai-interview-web' in src('api/README.md'),
    'New developer setup can fail without manual correction.',
    ['web/.env.example:1-5','README.md','api/README.md'])
add('FIND-013','signup implementation exists without reachable UI or backend route',
    'authApi.signup' in src('web/src/pages/auth/SignupPage.tsx') and
    'path="/signup"' not in src('web/src/App.tsx') and 'post \'signup\'' not in src('api/config/routes.rb'),
    'Signup feature appears incomplete/unreachable; clarify whether intended deliverable.',
    ['web/src/pages/auth/SignupPage.tsx:12-34','web/src/App.tsx:19-25','api/config/routes.rb:8-12'])
raw=json.dumps({'generated_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'method':'read-only source contract assertions; not runtime tests', 'checks':checks},indent=2)
out=Path(__file__).with_name('source_contract_checks.json'); out.write_text(raw+'\n');print(raw)
