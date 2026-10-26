# Fullstack Quality Gate

This repository documents the engineering work behind an interview-assessment platform built with Rails and React. The focus wasn't to rebuild the product. It was to find the failure points that mattered, fix them, and put checks in place so the same issues would be caught earlier next time.

The most important areas were tenant isolation, interview-session integrity, AI-generated portfolio data, background processing, and the handoff between the API and frontend.

## Architecture

```text
React / TypeScript / Vite
    ├── REST API ──────────── Rails 7 ───── PostgreSQL
    └── WebSocket ─────────── Rails middleware
                                  │
                                  └── Sidekiq / Redis ── AI processing
```

- **`api/`** — Authentication, tenant-scoped assessments, invitations, interview sessions, portfolio generation, fit/gap analysis, and WebSocket endpoints.
- **`web/`** — Assessor and candidate flows, including interview UI and assessment management.
- **`assessment/`** — Risk-based audit, engineering quality system, release decision, and linked requirements/acceptance/design documents.
- **`scripts/` and `.github/`** — Automated regression checks, PR validation, and release gates.

For service-specific setup, see [API setup](api/README.md) and [web setup](web/README.md).

## Engineering decisions

A few changes illustrate the approach taken in this project:

| Area | Problem | Approach |
| --- | --- | --- |
| Tenant access | A valid login could select a tenant without proving membership. | Store explicit user-to-tenant grants and recheck access on protected API and WebSocket requests. |
| Interview lifecycle | Completion and invitation handling needed stronger server-side rules. | Validate persisted session state; make invitations expirable and revocable. |
| AI-generated results | Invalid scores or an interrupted worker could leave misleading portfolio data. | Validate inputs and protect database writes against partial updates. |
| Fit/gap reports | A vacancy could change while a report was being generated. | Recheck the source fingerprint before writing the result. |
| Delivery process | A passing build alone didn't show whether a change was ready. | Require a spec, acceptance criteria, design notes, and executable regressions in the PR workflow. |

These decisions are backed by code, tests, and reviewable CI runs rather than screenshots alone.

## Run locally

You'll need Ruby 3.3, Node.js, PostgreSQL, and Redis. Configure the Rails environment and an authorized test tenant following the [API setup guide](api/README.md), then configure `web/.env` from [`web/.env.example`](web/.env.example).

Start Rails and the frontend in separate terminals:

```bash
# Terminal 1 — from api/
bundle install
bundle exec rails db:prepare
bundle exec rails server

# Terminal 2 — from web/
npm ci
npm run dev
```

Rails uses port **3001** and Vite uses port **5173** in the local setup. Redis and Sidekiq must also be running for background jobs; see the API guide for those commands.

### Run the tests

```bash
# From the repository root
python -m unittest discover -s scripts -p 'test_*.py' -v
ruby api/spec/regression/critical_contract_test.rb

# From api/ — use an isolated test database
RAILS_ENV=test bundle exec rails db:prepare
RAILS_ENV=test bundle exec rspec spec --format documentation

# From web/
npm ci --ignore-scripts --no-audit --no-fund
npm run build
node --test tests/*.test.mjs
```

GitHub Actions also runs a Chromium-based end-to-end flow against Rails/PostgreSQL and checks real WebSocket connections. The [live E2E workflow](.github/workflows/live-e2e.yml) contains the isolated CI setup.

## Review the evidence

| What to review | Links |
| --- | --- |
| Required assessment reports | [Audit](assessment/01-audit.md) · [Quality system](assessment/02-quality-system.md) · [Release decision](assessment/03-release-decision.md) |
| PR gate rejecting and accepting changes | [Blocked PR #1](https://github.com/RyanHidayat96/fullstack-quality-gate/pull/1) · [Passing PR #2](https://github.com/RyanHidayat96/fullstack-quality-gate/pull/2) |
| Tenant and WebSocket security fixes | [PR #5](https://github.com/RyanHidayat96/fullstack-quality-gate/pull/5) · [PR #7](https://github.com/RyanHidayat96/fullstack-quality-gate/pull/7) |
| Invitation expiry and revocation | [PR #9](https://github.com/RyanHidayat96/fullstack-quality-gate/pull/9) |
| Browser E2E and later integrity regressions | [PR #12](https://github.com/RyanHidayat96/fullstack-quality-gate/pull/12) · [PR #13](https://github.com/RyanHidayat96/fullstack-quality-gate/pull/13) · [PR #14](https://github.com/RyanHidayat96/fullstack-quality-gate/pull/14) |
| CI on the reviewed source | [Quality Net](https://github.com/RyanHidayat96/fullstack-quality-gate/actions/runs/40329587279) · [Browser/WebSocket E2E](https://github.com/RyanHidayat96/fullstack-quality-gate/actions/runs/40329587265) |
| Tagged release | [`v1.0.0` gate](https://github.com/RyanHidayat96/fullstack-quality-gate/actions/runs/40277694610) · [Release notes](RELEASE_NOTES.md) |

## Release status

**BLOCKED / DO NOT SHIP.** The tagged `v1.0.0` candidate was evaluated before the later fixes and was deliberately blocked. Passing CI on `main` does not change that historical result.

The current checks cover selected Rails/database, frontend, browser, and WebSocket flows. They do not prove every planned scenario or a live external AI audio stream. The branch is not protected by enforced GitHub rules, and older Git commits still contain imported material that requires a separate publication review. See the [release decision](assessment/03-release-decision.md) for the remaining risks.
