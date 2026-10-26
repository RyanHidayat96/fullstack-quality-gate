# Fullstack Quality Gate

This repository contains a two-service interview-assessment platform and the engineering quality net built around it for a Fullstack Engineer (SDET Depth) case study.

**Release decision: BLOCKED / DO NOT SHIP.** Passing CI is not production approval.

## Case-study deliverables

| Requested deliverable | Evidence |
| --- | --- |
| Risk-based audit | [01 — Audit](assessment/01-audit.md) |
| Quality system, Definition of Ready, executable checks and RED → GREEN | [02 — Quality System](assessment/02-quality-system.md) |
| Tagged release gate and ship/block decision | [03 — Release Decision](assessment/03-release-decision.md), [release notes](RELEASE_NOTES.md) |
| Blocked and passing PR demonstrations | [PR #1 — blocked](https://github.com/RyanHidayat96/fullstack-quality-gate/pull/1), [PR #2 — passed](https://github.com/RyanHidayat96/fullstack-quality-gate/pull/2) |
| Remediation with real GitHub CI evidence | [PR #5 — tenant authorization](https://github.com/RyanHidayat96/fullstack-quality-gate/pull/5), [PR #7 — API/WS authorization](https://github.com/RyanHidayat96/fullstack-quality-gate/pull/7), [PR #9 — invitation lifecycle](https://github.com/RyanHidayat96/fullstack-quality-gate/pull/9) |
| Tag-specific release CI | [v1.0.0 — blocked](https://github.com/RyanHidayat96/fullstack-quality-gate/actions/runs/40277694610) |

The repository includes the required linked engineering inputs in `assessment/requirements/`, `assessment/criteria/`, and `assessment/designs/`. They are used by the PR validator; these are not independently approved business specifications.

## Platform

```text
api/         Rails 7, PostgreSQL, Redis / Sidekiq, REST and WebSocket
web/         React, TypeScript, Vite
assessment/  Audit, quality system, release decision, linked engineering inputs
scripts/     Quality policy, release and submission verification
.github/     Pull request template and GitHub Actions
```

The web app calls the Rails REST API and WebSocket middleware.

## Run and verify

1. Follow [api/README.md](api/README.md) to configure a disposable PostgreSQL database, Redis, credentials, migrations and tenant memberships. By default Rails serves at `http://localhost:3001`.
2. Follow [web/README.md](web/README.md). Copy `web/.env.example` into your local untracked `.env`; Vite serves at `http://localhost:5173`.
3. Verify the quality net:

```bash
python -m unittest discover -s scripts -p 'test_*.py' -v
ruby api/spec/regression/critical_contract_test.rb

cd api
bundle exec rails db:migrate RAILS_ENV=test
bundle exec rspec spec --format documentation

cd ../web
npm ci --ignore-scripts --no-audit --no-fund
npm run build
node --test tests/*.test.mjs
```

CI executes the same core checks on pull requests and `main`. A separate tag-triggered release decision blocks on unresolved risks even when technical tests pass.

## Known limits

PostgreSQL-backed request coverage and component rendering are verified, but actual browser-to-API-to-DB journeys, upgraded WebSocket streaming, exhaustive test catalog coverage and realistic concurrency still need further verification. The `main` branch has not been verified as protected. Historical Git objects and redistribution rights are not cleared even though the active application source passes a naming guard.

The [release decision](assessment/03-release-decision.md) records why the product remains blocked and which approvals are missing. No secret, publication clearance or production sign-off is implied.
