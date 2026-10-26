# Phase 6 — Remaining Isolated Runtime Verification Runbook

This document specifies the **missing checks**, not checks already passed. Never use production credentials, databases or live candidate data for this exercise.

## 1. Trusted prerequisites

Use a disposable workstation or container with Ruby **3.3.2** (per `api/.ruby-version`), Bundler, Node.js compatible with `web/package.json`, PostgreSQL 16, Redis 7, and sufficient access to an approved package registry. Keep all credentials local/ignored. The supplied CI uses test-only PostgreSQL credentials and does not prove the deployment environment.

Before any remote publication, review `assessment/evidence/phase-6/publication-readiness.json`; the current source is **not cleared for public upload**. GitHub repository creation stays the user's responsibility.

## 2. Backend isolated verification (NOT RUN here)

From the repository root, with a **dedicated empty test database** and non-production Redis:

```bash
cd api
ruby --version                    # must match 3.3.2
bundle install
# Configure ONLY isolated test DB and Redis; never reuse an existing client DB.
RAILS_ENV=test bundle exec rails db:create
RAILS_ENV=test bundle exec rails db:migrate
RAILS_ENV=test bundle exec rspec spec/requests spec/services spec/models spec/middleware spec/workers --format documentation --fail-if-no-examples
```

Run a second time after the isolated database has been reset and seeded with synthetic fixtures. Verify database row values after each mutation using Rails and query logs. Inspect exact `spec/rails_helper.rb` and generated schema if migrations fail; never weaken fixtures or skip a failing spec to make CI green. For session idempotency, exercise parallel HTTP and WebSocket callbacks and check one persisted session closure and one queued portfolio worker.

## 3. Frontend reproducible build and UI verification (NOT RUN here)

```bash
cd web
npm install --package-lock-only --ignore-scripts --no-audit
# Review and commit the generated package-lock.json after verifying it represents approved dependencies.
npm ci --ignore-scripts --no-audit --no-fund
npm run build
node --test tests/*.test.mjs
```

Add **substantive** React component/API mocked tests before satisfying the `web-quality` job: cover the candidate invitation route, login errors, interview termination, and rendered fit-gap freshness errors. Inspect actual DOM, API mocks, and navigation; simply creating a file named `*.test.tsx` does not constitute coverage. Use a browser test environment only on synthetic data and while both disposable services are running.

## 4. Cross-layer parity to demonstrate

| Workflow | UI expectation | API response | Persisted database assertion |
|---|---|---|---|
| Tenant B opens tenant A portfolio | Access denied | 403/404 with no sensitive data | No tenant A row touched |
| Pending interview gets `audio_complete` | Not ended | 4xx; no generation scheduled | Status remains pending, no portfolio |
| Active interview without WS readiness | Not ended | 4xx | No status or coverage mutation |
| Fully covered/acknowledged interview | Ended once | Successful idempotent closure | Exactly one portfolio + one job |
| Invalid AI level in result payload | No published score | No successful completion | Existing skill rows preserved |
| Vacancy skill edited after fit-gap | Old report not presented as current | Stale/recompute response | Fingerprint differs; no stale export |
| Duplicate skill labels with distinct IDs | Both rows visible | Both comparisons present | Two separate correct entries |
| WS candidate token used on assessor channel | Authorization denied | No coverage stream | No data leak and no worker mutation |

## 5. Real repository gates (NOT RUN here)

After **you** create and clear an independent neutral public repository, configure required checks and protected main branch *outside PR control*. Open a deliberately invalid PR (missing test or linked spec) and retain its actual failing CI URL. Open another valid PR with linked inputs and changed executable test and retain its real passing CI URL. Recheck that editing the gate implementation or workflow cannot bypass repository policy without trusted approval. Branch rules/check IDs must be verified in GitHub, not presumed from YAML.

## 6. Unresolved policy signoff

`FIND-011`: Determine from the actual product owner or SSO owner whether admins are tenant-bound, globally scoped, or explicitly granted a per-tenant membership. Document both allowed and denied paths before implementing a fix. Until then the P1 remains **OPEN** and the release should remain **BLOCKED**.
