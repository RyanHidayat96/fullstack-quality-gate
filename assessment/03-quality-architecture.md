# Phase 3 — Quality Architecture & Traceability Design

> **Status:** DESIGN COMPLETE; **implementation: NOT STARTED**; **running CI / GitHub PR proof: NOT AVAILABLE**.  
> **Date:** 2026-10-22 (Asia/Jakarta)  
> **Inputs:** `PLAN.md` Phase 3, `assessment/01-audit.md` (13 findings: 8 P1, 5 P2), `assessment/architecture-notes.md`, and original source in `api/` + `web/`.  
> **Source-of-truth boundary:** These are *proposed engineering controls*, **not** approved product requirements. The product wiki/acceptance rules have not been obtained. The owned independent repository was deferred by the user.  
> **Naming:** Newly written documents use neutral identifiers and contain no employer/product/customer names so they can later be reviewed for safe publication. The original source still requires separate confidentiality review before any public push.

## 1. Objective, constraints and non-goals

**Objective:** an automated, explainable, inexpensive quality net that enforces G2 (ready to build) and G3 (ready to release), ties each high-severity finding to a reproducible regression and persistent-data assertions, and leaves real red → green evidence on code fixes.

**Case-study quality bar:** (1) a code-changing PR cannot proceed without a linked spec/PRD, AC/test scenarios and short solution/design plan; (2) a change without a meaningful test or a tightly controlled, reasoned exemption is rejected; (3) critical regressions cause CI to fail without human intervention; (4) release tags run the same checks; (5) no check is weakened to force green; (6) any unresolved P0/P1 blocks release unless a real owner explicitly accepts risk.

**Verified baseline:** Rails 7.0.x + Ruby 3.3.2 (`api/Gemfile`, `api/.ruby-version`), RSpec dependency already declared (`api/Gemfile`); PostgreSQL with an application schema plus `public` search path, Sidekiq/Redis, HTTP+WebSocket service; React 18/TypeScript/Vite (`web/package.json`). No committed `api/spec`, frontend test runner, GitHub workflow or frontend lockfile was present in the supplied snapshot. API and browser not started; isolated Ruby method probes are not API/DB tests. Do not assert a green baseline.

**Non-goals in Phase 3:** no tests/workflow scripts/PR templates added to production tree; no P1 code fixes; no claims of executed full integration/E2E tests; no GitHub repository, PR, tag, release or secrets; no live AI calls or cross-tenant activity against real data.

## 2. Architecture decisions (ADRs)

| Decision | Rationale | Trade-off / verification in Phase 4 |
|---|---|---|
| **QA-ADR-01 — Rails RSpec request/model/service tests first** | RSpec 6 is declared; controllers + models + DB-backed calculation errors carry the audited risk. | Boot Rails test env with a disposable PostgreSQL service and deterministic factories; check initialization/schema before writing assumptions into assertions. |
| **QA-ADR-02 — Small JS/React test layer** | No frontend test tooling exists; TypeScript and Vite make Vitest + React Testing Library a compatible *proposed* addition. | Pin versions compatible with existing Vite/Node; add `vitest`, `@testing-library/react`, `jsdom`, `@testing-library/jest-dom` **only if** real UI contract tests justify them. Do not pretend installed. |
| **QA-ADR-03 — API integration as the default authority** | UI may be correct while persisted/derived DB values are wrong; auth filters and worker state must be checked server-side. | Assert HTTP status/body, before/after DB rows, enqueued jobs and idempotence; for concurrency isolate transactions deliberately. |
| **QA-ADR-04 — Thin browser E2E, gated by availability** | Critical web-to-API flow needs end-user proof, but browser setup is costly and real audio/Gemini cannot be deterministic. | Consider Playwright only for 1–2 stable non-audio journeys after API+web boot. Exclude live audio/AI from mandatory CI; stub at external boundary. |
| **QA-ADR-05 — Offline AI and queue** | No real Gemini credentials or network assumptions in CI. | Stub `Gemini::HttpClient`, fake media/WebSocket frames and Sidekiq jobs for most checks. Test one Sidekiq/Redis path if service boot permits; never equate job enqueue with successful persistence. |
| **QA-ADR-06 — GitHub PR gate with structured in-repo docs** | Required inputs must be verifiable *by a machine*, not merely a filled checkbox. | `pull_request` workflow calls script against PR event+HEAD checkout; validates repo-local links and schema/content; least privilege (`contents: read`, `pull-requests: read`). No `pull_request_target` execution of PR code. |
| **QA-ADR-07 — Branch protections are separately required** | A failed CI status alone does not guarantee merge prevention. | After user creates repo, require quality check on `main` via ruleset/branch protection if account permits. Mark **NOT ENFORCED** until verified remotely. |
| **QA-ADR-08 — Timeboxed tests and fail closed** | A slow/brittle net invites bypasses. | Separate quick PR checks from DB tests, cap job timeout, collect safe failure logs; no blanket retries or `continue-on-error`. |
| **QA-ADR-09 — Explicit spec uncertainty** | Several audited outcomes depend on unavailable business policy. | Test security/integrity invariants as provisional; do not turn assumed duplicate-label policy, tenant admin grants or invite TTL into purported approved requirements. |
| **QA-ADR-10 — Release on exact commit/tag** | Build success or green on an unrelated commit cannot make a version releasable. | Run required verification on `v*` tag, record immutable SHA/result; P1 register checked independently of test status. |

### Rejected shortcuts

- Snapshot-only UI tests for data-integrity defects.
- `if: always()` or `|| true` on required checks, trivial `expect(true).toBe(true)`, low-value coverage targets, fake PR checks, inferred completion from `npm run build` only.
- Trusting base branch docs when a PR replaces them without validation; allowing `../`, external wiki URLs or comments-only placeholders to satisfy required inputs.
- Making every existing code file produce a new test automatically; narrow test mapping is useful only when verified that assertions protect changed behavior.
- Executing real third-party AI calls or needing client-provided auth credentials in CI.

## 3. Quality topology and test ownership

```text
                                      G2 — READY TO BUILD
  PR opened / synchronized / reopened ──────────────────────────────────────────┐
       ├── classify diff: code / docs / gate / data / generated                 │
       ├── require and resolve spec + AC + design in /assessment                │
       ├── verify cross-references, minimum content, test IDs and owner         │
       ├── require changed/linked regression checks for behavior changes       │
       ├── disallow silent exemptions and script-bypass attempts                │
       └── PR metadata validator status (FAIL CLOSED) ──────────────────────────┘

                                 G3 — BUILD/RELEASE
             ┌──────────────┬───────────────────┬───────────────────┐
             │ Ruby lint/   │ RSpec service/API │ Typecheck + build │
             │ syntax       │ + disposable PG  │ + focused UI      │
             └──────┬───────┴─────────┬─────────┴──────────┬────────┘
                    └─────────────────┼────────────────────┘
                           Critical regression net
                             (RED before fixes)
                                 │
                       version tag v* on SHA
                                 │
                     release decision + risk register
                                 │
                       RELEASABLE / BLOCKED
```

### Layer allocation (planned, not installed)

1. **Ruby unit/service tests (fast):** FITGAP-04/05, PORTFOLIO-01/02, end-handler policy checks, candidate invite configuration, JSON validation. No PostgreSQL for pure expressions, but do not incorrectly mock ActiveRecord where persistence is the asserted behavior.
2. **Rails request + PostgreSQL integration:** AUTH-TENANT-01/02/03/04, SESSION-01/02/03, FITGAP-01/02, PORTFOLIO-03, auth negative flows, vacancy edit/cache invalidation, export/current-data parity. Use isolated DB and rollback/cleanup.
3. **Background jobs + database:** FITGAP-03 and PORTFOLIO-03 verify asynchronous generation, updates and nonduplication using inline/fake jobs as appropriate; separately flag race-coverage not achievable in standard CI.
4. **WebSocket protocol tests:** WS-AUTH-01/02/03/04 check real authorization at handshake/message and absence of data frames on deny; use isolated test clients and synthetic JWTs, not real interview streams.
5. **Frontend component tests:** INVITE-01 and status/in-flight response UX; test displayed link and data binding to API contract, but not as substitute for backend link-generation assertions.
6. **Browser E2E (conditional):** create assessment → candidate invite → verify deep-link routing and 202 asynchronous report pending handling; no mandatory real microphone/Gemini test. When environment lacks browser/dependencies, report BLOCKED and keep required server tests strict.
7. **Workflow policy tests:** DOR-01/02/03/04, TEST-GATE-01/02/03/04, RELEASE-GATE-01/02/03 through CLI event/fixture simulations and, after remote setup, actual PR/tag status checks.

## 4. Deterministic test-data and infrastructure design

**Disposable tenant fixture set:** `tenant_alpha`, `tenant_beta`; assessor_A, assessor_B, non_assessor_A; assessments_A/B; sessions_A_pending, A_active, A_ended; two portfolios with overlapping human-readable labels and distinct UUIDs; vacancy_A with two similarly labeled but distinct skill identities, vacancy_B; one deliberately stale report; one synthetic AI response with invalid levels. All test entities must be synthetic and created within a disposable `RAILS_ENV=test` database. **Never reuse a shared development database or seeded real account**.

**DB setup prerequisite:** `api/config/database.yml` specifies a fixed local database name in the Rails `test:` section and uses an application schema plus `public` schema search path; seeds reference a shared `organizations` table. The independent repo's CI must initialize its **own test database** and required schemas; check migrations and `api/db/schema.rb` before selecting `db:prepare` vs `schema:load`. Do not require the external platform's database. `DB_USERNAME/DB_PASSWORD` are generated for CI service containers, never copied from committed examples. Verify migrations + model associations on a fresh DB; do not report persistence verified until real queries pass.

**HTTP auth:** create test user/JWT with well-scoped tenant grants; do not use real service tokens. Cover same-tenant positive, other-tenant negative and invalid/expired role variations. REST must not rely on UI role guard. `User` lacks tenant membership in snapshot, so AUTH-TENANT-04/06 acceptance is **pending explicit policy**; no guess of user-to-org table.

**Async & AI:** stub external AI at client boundary with deterministic payloads (`valid level`, `nil`, `n/a`, `out of range`), use Sidekiq testing mode for enqueue checks, and DB assertions for job completion separately. Verify serialized JSONB maps and exports against DB source values; compare after reload rather than in-memory Ruby objects. Test update before/after cache invalidation with a stable clock; for concurrency use explicit transaction interleaving where supported, not `sleep`.

**Web & audio:** `VITE_API_BASE_URL=http://localhost:3001/api/v1`, `VITE_WS_BASE_URL=ws://localhost:3001`, `WEB_BASE_URL=http://localhost:5173` **proposed new configuration** for correct invite origin; `WEB_BASE_URL` does not currently exist as verified env contract and must not be marked implemented. Prefer `data-testid` only if role/name selectors are insufficient. Never invoke live microphone or real AI in core CI.

**Isolation:** one run cannot modify another run's DB; run migrations once per isolated DB, unique test UUIDs, clear Redis keys scoped to test run, stub background work, ensure no tests depend on order. Capture sanitized HTTP status/code/JSON, DB diffs (without names or tokens), relevant worker invocations, CI logs. No broad `before(:all)` writes outside transaction teardown.

**Flake policy:** deterministic fake clock; explicit readiness checks rather than sleeps; predictable queue mode; isolated ports; CI service health checks; timeout per task; no automatic retry to turn legitimate RED into GREEN. If a test is flaky, report and correct root cause before making it required. Do not remove critical assertions.

## 5. DoR / DoD contract

| Required element | Machine check in Phase 4 | Human meaning/review |
|---|---|---|
| Spec / PRD | Existing repository-relative markdown file under `assessment/requirements/` contains nonempty `Requirement ID`, user/problem, behavior, scope and out-of-scope. | Does it state the correct business problem and owner approval? |
| Acceptance criteria / scenarios | Existing file under `assessment/criteria/` contains at least one uniquely identified `AC-...` with Given/When/Then or explicit machine-verifiable assertions, plus negative/edge scenario for high-risk changes. | Are the scenarios right, not contrived to match implementation? |
| Solution / design plan | Existing file under `assessment/designs/` contains approach, data/API/UI impact, alternatives, risks/rollback, and planned test ID(s). | Is the plan sound, sufficiently scoped, and reviewable? |
| Traceability | PR metadata references `FIND-...` when fixing audit issues and test IDs; each high-severity case appears in traceability matrix. | Do tests actually assert both displayed and stored outcomes? |
| Test or narrowly permitted exemption | For behavior-changing PRs, require at least one changed test file linked to a test ID and run. For non-behavioral-only diffs, require category+reason and reviewer permission, not a universal opt-out. | Is the test meaningful and does it reproduce the actual class of defect? |
| Required green checks | PR gate, RSpec critical paths, frontend typecheck/build and focused UI tests (once set up) complete successfully; critical regressions never `continue-on-error`. | Does any open P0/P1 demand BLOCK independent of green pipeline? |

**Scope rule:** code-changing includes `api/**`, `web/src/**`, package/gem deps, DB migrations, `api/config/**`, deployment, test harness, and `.github/**`. A docs-only PR with no code modifications can be exempt from *new code test* requirement by a limited recorded policy, **but never from evaluating changed document validity**. PR template fields/links are required for code-changing PRs. On uncertain file classification: **fail closed**, request explicit review.

**Enforcement limit:** automation can establish existence, structure, cross-reference, test execution, CI status, and coarse change-to-test mapping. It cannot reliably establish that a PRD is product-approved or tests are sufficiently insightful. Set required reviewer/branch rules where permissions allow. Until those settings and remote runs are confirmed, G2/G3 **are NOT operational**.

## 6. CI / PR / release workflow blueprint

### CI events and jobs

| Trigger | Job / dependency | Required outcome |
|---|---|---|
| `pull_request` on opened/synchronize/reopened/ready_for_review | `pr-inputs` → `policy-validator` | Missing/invalid input links, missing tests, invalid exemption or missing risk trace => nonzero exit. |
| `pull_request` / `push` to `main` | `api-spec` (with PostgreSQL test service) | RSpec request/model/service + migration/setup succeeds; critical regression failures red. |
| `pull_request` / `push` to `main` | `web-check` | `npm ci` with committed lockfile, `tsc --noEmit`/`npm run build`, UI tests. |
| `pull_request` / `push` to `main` | `quality-summary` `needs: [pr-inputs,api-spec,web-check]` where applicable | Fails if any required job fails, skips unexpectedly, or times out. |
| `push` tags `v*` | `api-spec`, `web-check`, `release-quality-summary` | Exact tag SHA checked; release status BLOCKED unless all mandatory checks pass and risk register has no unaccepted P0/P1. |

`pr-inputs` is not applicable to non-PR push/tag, so `quality-summary` must distinguish **not-applicable** from suspicious skipped critical job rather than silently green. Use separate summary for release tags. No `pull_request_target` running PR code. Checkout a pinned/untrusted PR HEAD under read-only permissions, avoid exposing deployment secrets or write tokens to PR code, bound artifact uploads and sanitize logs. Use pinned action SHAs after verifying official versions (specific versions intentionally not invented in this design).

**DB jobs:** GitHub-hosted Linux runner with Ruby setup and PostgreSQL service credentials restricted to that job. Redis service only where actual test path uses it; fake jobs otherwise. `bundle config` install consistent with Gemfile.lock. Ruby 3.3.2; Node >=18 matching Vite build requirements, record final selected version after `npm ci` passes. Frontend presently has **no lockfile**, so `npm ci` is designed to fail until Phase 4 deliberately generates and commits `web/package-lock.json` from resolved dependencies.

**Required-status caveat:** the user deferred independent repository creation. G2/G3 cannot be certified enforced by GitHub until the repository exists, ruleset/branch protection is configured, and real failing/passing PR checks are observed. Local fixture results in Phase 4 will be labeled `LOCAL_ONLY`.

### Test-first chronology and true positive PR problem

The case study wants CI to prove existing bugs are RED **before** the engineer fixes them. Consequently `api-spec` might fail for *every* PR while P1 regressions are still present, making a positive-PR demo impossible during that period. **Do not disable regression jobs merely to get the green PR.** Choreography:

1. Phase 4 writes meaningful regressions and captures failing checks on unfixed baseline; builds the input gate and unit-tests its policy. `PR blocked` local simulation possible but remote PR evidence deferred.
2. Phase 5 fixes genuine P1 defects, gets regression RED→GREEN without weakening asserts; risk/spec blockers remain explicit.
3. Phase 6 uses independent repository (once created by user) for required **real** blocked PR and successful PR demonstrations. The successful PR must satisfy every mandatory job legitimately.
4. Phase 7 runs version tag gate and writes final decision.

Phase 4 remote PR demonstration therefore remains **BLOCKED/DEFERRED** until repo creation and regression fixes. This is a dependency, not permission to ignore the requirement.

## 7. Planned file inventory — no file created by this section yet

| Planned path | Responsibility |
|---|---|
| `.github/pull_request_template.md` | Structured PR fields, links and evidence. |
| `.github/workflows/quality.yml` | PR/main critical checks, summary; tag release check may share workflow. |
| `scripts/validate_pr_inputs.*` and `scripts/test_validate_pr_inputs.*` | Diff classifier, safe repo-local document resolver, schema/content and test impact validator; fixture-driven tests. |
| `assessment/requirements/REQ-*.md` | Requirements / decision records; approval status explicit. |
| `assessment/criteria/AC-*.md` | Human+machine-readable scenarios for each change. |
| `assessment/designs/DES-*.md` | Changes' design and risk assessment. |
| `api/spec/requests/` | Auth, tenants, session lifecycle, export and fit/gap request specs. |
| `api/spec/services/`, `api/spec/workers/`, `api/spec/models/` | Data correctness, AI score validation, worker and model regression. |
| `api/spec/support/` / `api/spec/factories/` | Tenant isolation, seeded synthetic data, external AI/queue doubles. |
| `web/src/**/*.test.ts(x)` | Invite and asynchronous-state UI tests; dependency choice conditional. |
| `web/package-lock.json` | Reproducible frontend dependency resolution. |
| `assessment/02-quality-system.md` | Phase 4–5 implementation, red/green, instructions, exact limits. |

The design catalog is machine-readable in `assessment/design/phase-3-test-catalog.json`, and its human readable mirror is in `assessment/03-traceability.md`. Each planned test ID must map to an actual executable test path and assertion *during implementation*; paths in this document are **suggestions, not existing files**.

## 8. Risk register, decisions needed and acceptance

| Risk or unknown | Current status | Decision owner (role, not fictitious sign-off) | Impact |
|---|---|---|---|
| Missing formal product wiki/PRD and approved AC | UNKNOWN / NOT REVIEWED | Product owner / BA | Source invariants must be labeled provisional; G2 cannot honestly claim approved spec. |
| Tenant admin scope: global vs tenant-specific | UNRESOLVED | Product/security | AUTH-TENANT-04/06 depend on explicit policy; deny unauthorized by default until resolved. |
| Duplicate skill labels: reject vs preserve | UNRESOLVED | Product/BA | FITGAP-04/05 expected output has two acceptable designs; must not silently drop. |
| Candidate invite token TTL/revoke | UNRESOLVED | Product/security | INVITE-04 remains spec gap; no arbitrary TTL. |
| Server completion authorization handshake | DESIGN REQUIRED | Backend/security | Must be server-verified and race-safe; don't trust candidate-only signal. |
| CI/test database from shared-schema assumptions | RUNTIME BLOCKED | Backend/DevOps | Verify fresh test DB + migrations/seed before DB assertions. |
| Audio/media/AI dependency availability | EXTERNAL UNAVAILABLE | Backend/QA | Boundary mocks are mandatory; scope limitation in final release report. |
| No independent public repo, no PR/tag, no branch protection | USER-DEFERRED | Candidate | G2/G3 cannot be proven enforced or releasable yet. |
| Confidential source names/identifiers | REVIEW REQUIRED | Candidate + authorized owner | Do not push original source publicly before publication safety review. |

### Phase 3 deliverable decision

- **Architecture / test design:** COMPLETE (source-checked proposed strategy and explicit unknowns).
- **Coverage plan of 8 P1 findings:** COMPLETE as planned IDs in catalog; **0 implemented**.
- **G2 / G3 policy and CI topology:** DESIGNED; **0 scripts/workflows/PRs implemented**.
- **Remote enforcement / real status checks:** **BLOCKED** by deferred repository and missing runtime setup.
- **Phase 3 exit gate:** PASS **for design only**, subject to outstanding product spec decisions and implementation prerequisites. No inference that application is safe, that tests exist or that a public deliverable is ready.

**Next authorized work:** STOP and await explicit permission for Phase 4 implementation. First execute offline policy-validator unit tests and true failing RSpec regressions; do not preemptively fix product defects.
