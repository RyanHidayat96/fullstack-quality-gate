# Phase 5 — Fix P0/P1 and prove source-level RED → GREEN

**Date:** 2026-10-22 (Asia/Jakarta)  
**State:** CODE FIXES APPLIED; **INTEGRATION AND RELEASE GATES BLOCKED**  
**Decision:** DO NOT SHIP  
**Authorized phase:** Phase 5 only. Phase 6 NOT started.

## Executive summary

Seven of eight P1 items have concrete, targeted source changes. All seven are **CODE_FIXED_UNVERIFIED** (not yet certified against real Rails/PostgreSQL/Redis/HTTP/WS). FIND-011 is P1 OPEN pending authoritative tenant membership policy. Baseline test failure is preserved and original assertion sets are unchanged. No GitHub repository/commit/PR created at user's request.

## Changes with evidence and residual risk

| Finding | Root cause and remedial code | Pre-fix RED | Post-fix GREEN | Incomplete verification |
|---|---|---|---|---|
| FIND-001 | `PortfoliosController` and `PortfolioSkillsController` now derive child records through tenant-owned session; fitgap worker refuses mismatched portfolio/vacancy tenant | `AUTH-TENANT-01` succeeds for foreign stub | `AUTH-TENANT-01/02` source-method contract | HTTP 2-tenant API, export and override, ORM joins, persisted data |
| FIND-002 | Session's durable `ready_to_end_at` set by websocket after wrap-up; candidate callback checks active + flag + actual coverage. `EndHandler` row-locks transition to prevent duplicate enqueue | `SESSION-01` ends pending session | `SESSION-01..04` isolated source check | migration, live WS/timer, concurrent DB races, Sidekiq queue |
| FIND-003 | Iterate all vacancy rows and match by stable ID (not label-keyed hash), avoid borrowing score across IDs | `FITGAP-04` loses one of two rows | `FITGAP-04/05` isolated source | persisted skill constraints; product uniqueness rule and PDF parity |
| FIND-004 | Vacancy comparison fingerprint persisted to `fit_gap_reports`, stale detection in API and export, worker captures fingerprint before calculation | original RSpec written but not runnable; source stale path | `FITGAP-01` isolated fingerprint changed and report reports stale | DB worker race, migration, stale JSON/PDF behaviors |
| FIND-005 | Strict integer level validation before destructive writes and transactional replacement | `PORTFOLIO-01` silently accepts invalid score | `PORTFOLIO-01/02` isolated contract | DB rollback and Gemini payload compatibility |
| FIND-006 | Separate `WEB_APP_BASE_URL` from API origin; update web REST/WS defaults | `INVITE-01` API :3001; 2 frontend contract failures | `INVITE-01`, DOC-01, INVITE-03 source contracts | deployed origins, browser invite navigation |
| FIND-007 | Coverage WS now rejects JWT without assessor/admin role and user ID | source gate missing; no executable baseline JWT probe | code-level enforcement written; Rails WS spec NOT RUN | real WebSocket tokens and Redis subscription auth |
| FIND-011 | **No safe fix without a tenant membership contract** | code-level ambiguity | **NO GREEN CLAIM** | approved IAM data model / per-user organization membership, role token policy |

## Exact local test results

| Command (repo root) | Exit | Observed | Evidence |
|---|---:|---|---|
| `ruby api/spec/regression/critical_contract_test.rb` before production edits | 1 | 5 tests, 5 failures, 0 errors | `evidence/phase-5/ruby-before-red.log` |
| same command after edits | 0 | 12 tests, 40 assertions, 0 failures | `evidence/phase-5/ruby-after-green.log` |
| `node --test web/tests/*.test.mjs` | 0 | 2 tests passed | `evidence/phase-5/web-contract-after.log` |
| `python3 -m unittest discover -s scripts -p 'test_*.py' -v` | 0 | 25 tests passed | `evidence/phase-5/policy-after.log` |
| Ruby syntax check for `api/app api/db/migrate api/spec` | 0 | All tested Ruby files syntax OK | `evidence/phase-5/ruby-syntax-after.log` |
| `(cd api && bundle check)` | 127 | `bundle: command not found` | `evidence/phase-5/bundle-check.log` |
| `(cd api && RAILS_ENV=test bundle exec rspec ...)` | 127 | `bundle: command not found`, no tests run | `evidence/phase-5/rspec-attempt.log` |
| `(cd web && npm run build)` | 2 | Missing `vite/client` dependency | `evidence/phase-5/web-build.log` |

**Interpretation:** A RED→GREEN progression is proven *only at source-method/config-contract level*. No real Rails database, browser, application server, CI or release-stage check has been verified. The tests use synthetic inputs only.

## New persistent database schema changes (NOT applied)

- `api/db/migrate/20261022000000_add_server_end_readiness_to_sessions.rb` adds `sessions.ready_to_end_at`.
- `api/db/migrate/20261022000001_add_fit_gap_source_fingerprint.rb` adds `fit_gap_reports.source_fingerprint`.
- `api/db/schema.rb` manually synchronized to represent intended schema; **migration execution is unverified**.
- On an isolated local test database only: apply migrations, then test negative/positive session completion, backwards compatibility for old reports, tenant isolation, row-level locking, worker duplicate conditions and stale source fingerprint. Never run migrations against client/production data for this assessment.

## Git / integrity

- Phase 4 archive snapshot comparison: `evidence/phase-5/phase5-production-diff.json`.
- All 5 original regression assertion sets unchanged: `evidence/phase-5/original-assertion-preservation.json`.
- **NO GIT COMMITS / SHA / REAL PR / REMOTE CI**. Independent GitHub repo creation remains user-deferred. Do not fabricate references to such artifacts.
- Existing source includes identity/product strings; this is a **private working copy**, not cleared for public GitHub disclosure.

## Residual release blockers and Phase 5 gate

1. **P1 OPEN — FIND-011:** admin tenant membership binding/SSO contract not specified; cannot safely authorize caller-selected scheme.
2. **P1 code-fixed-but-unverified — FIND-001/002/003/004/005/006/007:** authentic Rails+DB/WS/HTTP E2E evidence is missing; reclassify only after actual integration tests.
3. **Build/gate issues:** no node lockfile, no component suite, no Rails bundle, no fully working service and no two actual gated PRs.
4. **External PRD/AC approvals:** proposed engineering decisions not accepted by product/BA.
5. **No commit/run IDs:** red/green recorded with local command logs, but cannot demonstrate commit-history RED→GREEN until independent repo exists.

**Phase 5 final gate: NOT PASSED** because one P1 remains open and runtime/release checks are blocked. Targeted code implementation and local source regression objective are satisfied. **STOP** here until the user authorizes Phase 6.
