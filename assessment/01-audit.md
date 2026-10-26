# 01 — Risk-Based Platform Audit & Defect Triage

> **Current post-GitHub status (2026-10-26):** For updated CI links, see [09-current-status.md](09-current-status.md). Tenant membership authorization (FIND-011) has a verified code-level fix ([PR #5](https://github.com/RyanHidayat96/fullstack-quality-gate/pull/5)), but business-wide role/SSO policy approval is outstanding. Invitation expiry/revocation (FIND-008) and unsupported signup removal (FIND-013) now have code and tests ([PR #9](https://github.com/RyanHidayat96/fullstack-quality-gate/pull/9), [PR #8](https://github.com/RyanHidayat96/fullstack-quality-gate/pull/8)); their product decisions remain provisional. Earlier Phase 2/5 observations below are historical. Release remains BLOCKED.

> **Phase 5 remediation update (2026-10-22):** 7 of 8 originally ranked P1 findings have code-level changes; all seven remain **PENDING DATABASE/HTTP VERIFICATION**. `FIND-011` is still `OPEN` because tenant-admin membership rules are unavailable. The release recommendation **DO NOT SHIP** remains unchanged. Details and exact test evidence: `assessment/PHASE_5_HANDOFF.md` and `assessment/evidence/phase-5/`. Original Phase 2 pre-fix source evidence is preserved below.

> **Release recommendation:** **DO NOT SHIP / G3 BLOCKED** based on high-consequence code-level defects and an unverified integration baseline. This is a *preliminary* decision, not a claim that a deployed system was compromised or that every theoretical scenario is reachable in production.  
> **As of:** 2026-10-22 (Asia/Jakarta)  
> **Scope:** Phase 2 only; original `api/` and `web/` files remain unmodified.  
> **Basis:** user-supplied 188-file code snapshot, its README/configuration, previous architecture map, and audit-only isolated probes. The separate product wiki linked by the root README was **not retrieved**.  
> **Evidence notation:** `SRC` = verified source path/line; `PROBE` = executed original function/method against isolated doubles (no Rails boot/DB); `RUNTIME-UNVERIFIED` = not tested end-to-end; `DOC` = provided/documented requirement, `ASSUMPTION` = explicitly proposed engineering invariant.

## 1. Decision in five minutes

This repository implements a two-service interview-assessment product: assessor-owned assessments and vacancies; candidate invitations; audio interviewing; coverage/transcript persistence; AI-generated portfolios; assessor score overrides; vacancy fit/gap comparisons; and JSON/PDF export. The most consequential risks are **cross-tenant object lookup**, **premature finalization of interview sessions**, and **computed/persisted assessment results that can be wrong or stale while the UI appears to work**. A limited local test harness verified several fault paths; full-stack tests remain blocked by unavailable Rails dependencies, PostgreSQL/Redis and Gemini credentials.

**Recommended release gate:** block until every P1 is corrected or formally accepted by an accountable owner with documented mitigation, tests validate actual data integrity and tenant isolation, the complete application runs against an isolated database, and the engineering quality gate is proven. Current CI, traceability and acceptance evidence do not meet the case study's Definition of Ready/Done. **No P0 has been proven**: the system-wide main objective has not been demonstrated entirely impossible with no workaround, so classifying everything P0 would be unsound.

### 1.1 Ranked finding index (impact × confidence × exploitability/repeatability)

| Rank / ID | Severity | Description | Classification | Evidence | State | Release |
|---|---|---|---|---|---|---|
| 1 · FIND-001 | **P1** | Portfolio, fit/gap and override queries lack tenant ownership constraints | BUILT_WRONG (source invariant) | SRC; RUNTIME-UNVERIFIED | CODE_FIXED_UNVERIFIED | BLOCK |
| 2 · FIND-002 | **P1** | Candidate `audio_complete` ends pending or insufficiently covered session | BUILT_WRONG (state invariant) | SRC + PROBE | CODE_FIXED_UNVERIFIED | BLOCK |
| 3 · FIND-004 | **P1** | Vacancy edits do not invalidate existing fit/gap reports | BUILT_WRONG (data freshness invariant) | SRC; RUNTIME-UNVERIFIED | CODE_FIXED_UNVERIFIED | BLOCK |
| 4 · FIND-005 | **P1** | Invalid AI level becomes valid-looking stored level via `.to_i.clamp` | BUILT_WRONG (data correctness invariant) | SRC + PROBE(expression) | CODE_FIXED_UNVERIFIED | BLOCK |
| 5 · FIND-003 | **P1** | Repeated vacancy skill labels silently drop comparisons | SPEC_AMBIGUOUS + observed behavior | SRC + PROBE | CODE_FIXED_UNVERIFIED | BLOCK pending contract |
| 6 · FIND-007 | **P1** | Coverage WebSocket validates token/tenant but not assessor role | BUILT_WRONG (auth policy inferred) | SRC; RUNTIME-UNVERIFIED | CODE_FIXED_UNVERIFIED | BLOCK |
| 7 · FIND-011 | **P1** | Login uses caller-selected tenant scheme without verified tenant membership | SPEC_AMBIGUOUS | SRC + Rails/PG regression | CODE_FIXED_UNVERIFIED | BLOCK pending policy |
| 8 · FIND-006 | **P1** | Default candidate invite URL resolves to API instead of web host | BUILT_WRONG (documented local setup) | SRC + PROBE | CODE_FIXED_UNVERIFIED | BLOCK local release |
| 9 · FIND-008 | **P2** | Invite token expiry/revocation rule not defined in snapshot | SPEC_MISSING | SRC; RUNTIME-UNVERIFIED | OPEN | CONDITIONAL |
| 10 · FIND-009 | **P2** | No versioned automated suite or PR/release CI gate in source snapshot | SPEC_MISSING (quality artifacts) | SRC inventory | OPEN | BLOCK (DoR/G3) |
| 11 · FIND-010 | **P2** | No local linked PRD/AC/design plan/traceability in source snapshot | SPEC_MISSING (inputs) | SRC inventory; wiki unverified | OPEN | BLOCK (DoR/G2) |
| 12 · FIND-012 | **P2** | API address and monorepo path conflict across setup docs | BUILT_WRONG (docs) | SRC | OPEN | CONDITIONAL |
| 13 · FIND-013 | **P2** | Signup UI implementation has no route or corresponding API endpoint | OBSERVED_UNSPECIFIED | SRC | OPEN | CONDITIONAL |

**Severity discipline:** P1 here means a specific wrong outcome, data-integrity risk, loss of a core flow without a clean workaround, or a potential serious authorization failure. Items that are *only* missing evidence/process are P2 by client-function severity but separately **block the engineering release gate** under the explicit brief. This does not confuse process blocking with an observed P0 product outage. Security exposures without integration proof are marked *conditional*.

### 1.2 Final Status Summary (Fixed vs Remaining)

Per the brief's requirement to explicitly classify each audit item's final outcome:

| Finding ID | Severity | Short Title | Final Status | Verification Mechanism |
| :--- | :--- | :--- | :--- | :--- |
| **FIND-001** | **P1** | Tenant boundary on portfolio/override queries | **FIXED** | Verified in `critical_contract_test.rb` & tenant scoping queries |
| **FIND-002** | **P1** | Premature `audio_complete` session finalization | **FIXED** | Verified in `session_completion_spec.rb` (HTTP request spec) |
| **FIND-003** | **P1** | Silent collapse on duplicate vacancy skill labels | **FIXED** | Verified in `fit_gap_engine_spec.rb` (Service spec) |
| **FIND-004** | **P1** | Stale fit/gap results after vacancy edit | **FIXED** | Verified in `fit_gap_freshness_spec.rb` (Model spec) |
| **FIND-005** | **P1** | AI level coercion into valid scores | **FIXED** | Verified in `portfolio_level_spec.rb` (Generator spec) |
| **FIND-006** | **P1** | Local invite URL host mismatch | **FIXED** | Verified via public frontend origin separation |
| **FIND-007** | **P1** | Coverage WebSocket role authorization | **FIXED** | Verified in `coverage_ws_auth_spec.rb` (Middleware spec) |
| **FIND-011** | **P1** | Tenant scheme login without membership check | **CODE FIXED — POLICY PENDING** | PR #5 Rails/DB RED→GREEN; independent global-admin/SSO product rule is not approved |
| **FIND-008** | **P2** | Invite token expiry & revocation policy absent | **CODE FIXED — POLICY PENDING** | PR #9 Rails/DB RED→GREEN; seven-day lifetime is an engineering assumption |
| **FIND-009** | **P2** | Missing versioned automated test net / CI gate | **FIXED** | Verified: GitHub Actions CI + PR gate + release gating live |
| **FIND-010** | **P2** | Missing linked PRD/AC/design inputs (DoR) | **FIXED** | Verified: REQ, AC, DES docs + `phase-3-test-catalog.json` |
| **FIND-012** | **P2** | API address and monorepo port conflict | **FIXED** | Verified: `api_config.test.mjs` Node contract tests PASS |
| **FIND-013** | **P2** | Signup UI without API route | **REMOVED ORPHAN CLIENT** | PR #8 removes unreachable signup and tests no unsupported public registration |

### 1.3 Proven versus unproven

- **Four executed probes** in `assessment/evidence/phase-2/isolated_source_probe.json`: FIND-002, 003, 005, 006. They exercise actual application methods or exact production expression with test doubles. They do **not** demonstrate real HTTP/DB transactions or a deployed exploitation path.
- **Nine read-only source contracts** in `assessment/evidence/phase-2/source_contract_checks.json`: FIND-001, 004, 007, 008, 009, 010, 011, 012, 013. These are concrete code omissions/paths, **not** simulated end-to-end requests.
- Runtime, persistence and concurrency observations: **NOT EXECUTED** because the Phase 1 environment cannot boot the app; see `assessment/architecture-notes.md` and `assessment/evidence/phase-1/` for exact commands and exit codes.
- Company/product and real candidate identifiers are intentionally absent from this report. Synthetic names/IDs/tokens are used throughout.

## 2. Detailed defects — ranked, each with reproduction and regression criteria

### FIND-001 — Tenant boundaries missing on direct portfolio and override lookups

- **Severity:** P1 Major (conditional cross-tenant confidentiality/integrity exposure); **Classification:** BUILT_WRONG relative to the explicit `TenantScoped` model isolation invariant; **Status:** CODE_FIXED_UNVERIFIED; **Evidence:** `SRC`, `RUNTIME-UNVERIFIED`.
- **Impact:** An authenticated assessor from tenant B may be able to read, export, regenerate or override a candidate's tenant-A portfolio if the object ID is known; tenant confidentiality and results integrity are at stake.
- **Expected and source:** Only records owned by the actor's authorized tenant should be available. `api/app/models/concerns/tenant_scoped.rb:13-35` declares per-tenant scoping for models with `tenant_id`; `api/app/models/session.rb:3-12` has it. `api/app/models/portfolio.rb:3-8` and `api/app/models/portfolio_skill.rb:3-8` do **not** carry `tenant_id`/tenant-aware scope.
- **Observed source:** `api/app/controllers/api/v1/portfolios_controller.rb:82,104,130,150-156` uses `Portfolio.find(params[:id])` for direct portfolio endpoints, unrelated to `Current.tenant_id`. `api/app/controllers/api/v1/portfolio_skills_controller.rb:50-53` uses `PortfolioSkill.joins(:portfolio).find(params[:id])` without requiring the ancestor session tenant. PDF/JSON export and override mutation use the same lookup. `api/app/workers/fit_gap_generator_worker.rb:8-12` also resolves vacancy unscoped (downstream trust issue).
- **Isolated reproduction recipe (integration pending):** In a disposable DB create tenants A and B, their respective sessions/portfolios, and two assessor JWTs. With B's JWT and tenant scheme, `GET /api/v1/portfolios/{A_portfolio_id}/export?format=json` and `POST /api/v1/portfolio_skills/{A_skill_id}/override` should return 403/404 and **never** mutate A. Also probe `POST /api/v1/portfolios/{A_id}/fitgap` and `GET /api/v1/portfolios/{A_id}/fitgap/{B_vacancy_id}`. **Do not execute against live tenants.**
- **UI/API/DB:** UI route protection is not record authorization; cross-tenant API and persisted results must be checked. No HTTP/DB execution yet.
- **Root cause:** direct child-table fetches ignore parent `session.tenant_id`; role-only authentication (`:assessor`) is not equivalent to record ownership.
- **Regression checks:** `AUTH-TENANT-01` deny foreign portfolio reads/exports; `AUTH-TENANT-02` deny foreign score overrides; `AUTH-TENANT-03` deny cross-tenant vacancy/portfolio pairs and background-job processing; positive same-tenant success and DB non-mutation assertions.
- **Fix owner:** Backend/API engineer + security reviewer. **Release:** BLOCK until scoped queries are enforced and demonstrated across all endpoints.

### FIND-002 — `audio_complete` can end a not-yet-started session as `all_covered`

- **Severity:** P1 Major; **Classification:** BUILT_WRONG against session state/coverage invariant; **Status:** CODE_FIXED_UNVERIFIED; **Evidence:** `SRC + PROBE`.
- **Impact:** A candidate link can finalize a pending/incomplete interview, storing `ended`/`all_covered` and triggering portfolio generation without a completed evaluation.
- **Expected and source:** The `all_covered` reason should be assigned only after backend-verified interview completion. `api/app/models/session.rb:6-7` enumerates `pending`, `active`, `ended`; the WS waits for an end signal before inviting `audio_complete` (`api/app/channels/audio_websocket_middleware.rb:588-609`). This is a **code-derived invariant** (no external acceptance criterion verified).
- **Observed source:** `api/app/controllers/api/v1/sessions_controller.rb:115-129` finds any session by invite token and invokes `Sessions::EndHandler.new(session).call(reason: 'all_covered')` if not ended, with no check of `active` state or whether the server emitted the completion signal. `api/app/services/sessions/end_handler.rb:26-40` persists ended status and queues portfolio generation.
- **Reproduction/evidence:** `ruby assessment/evidence/phase-2/isolated_source_probe.rb` ran the **actual controller method** with a fake pending session and fake EndHandler; response was `{ended: true}` and EndHandler was invoked with `status_before: pending, reason: all_covered`. See `.../isolated_source_probe.json` FIND-002. End-to-end DB outcome is **not yet tested**.
- **Runtime steps to verify:** Create an invite to a pending session; without opening the WS, call `POST /api/v1/sessions/{token}/audio_complete` once; expect a rejection, unchanged DB status, zero portfolio jobs. Also test active but incomplete session, and valid server-acknowledged drain path.
- **UI/API/DB:** Browser only calls this after `draining_audio` (`web/src/pages/interview/InterviewPage.tsx:57-69,101-119`), but public candidate endpoint must not rely on that client behavior. DB state unverified.
- **Root cause:** untrusted client completion indication treated as authoritative backend coverage/state proof.
- **Regression checks:** `SESSION-01` reject pending completion; `SESSION-02` reject early active completion; `SESSION-03` valid completion exactly once; `SESSION-04` concurrent duplicate calls do not produce duplicate portfolios/jobs.
- **Fix owner:** Backend/session engineer. **Release:** BLOCK.

### FIND-004 — Vacancy modification leaves cached fit/gap results stale

- **Severity:** P1 Major; **Classification:** BUILT_WRONG relative to persisted-versus-derived data invariant; **Status:** CODE_FIXED_UNVERIFIED; **Evidence:** `SRC`, `RUNTIME-UNVERIFIED`.
- **Impact:** A hiring assessor can read a successful old comparison or export a prior required skill level after changing the target vacancy, yielding incorrect recommendations.
- **Expected:** Fit/gap report should reflect the *current* vacancy version (or clearly state that it is a versioned historical snapshot). The product design does not define snapshot versioning; the current code treats reports as reusable by portfolio/vacancy IDs.
- **Observed source:** `api/app/controllers/api/v1/vacancies_controller.rb:37-44` updates a vacancy without invalidating report rows or scheduling recomputation. `api/app/controllers/api/v1/portfolios_controller.rb:116-120` returns existing cached fit/gap directly; `:128-137` reads it for display; `:212-221` includes existing report in JSON export. Override changes do have invalidation logic (`api/app/controllers/api/v1/portfolio_skills_controller.rb:41-47`) — asymmetry demonstrates a missing path.
- **Reproduction recipe:** Create vacancy with required level L2, generate report for a portfolio, change required level to L5 (same vacancy ID), re-request report and JSON/PDF export. Assert stored report reflects L5 or is flagged stale. **Not run**; no DB.
- **UI/API/DB:** API and export may show consistent **but stale** data; compare vacancy DB `vacancy_skills.expected_level` with `fit_gap_reports.skill_comparisons[].expected_level`.
- **Root cause:** cache invalidation keyed only to assessor overrides, not vacancy/skill changes. Potential worker race also needs test.
- **Regression checks:** `FITGAP-01` mutate vacancy skill and ensure old result not served; `FITGAP-02` compare report expected level to current saved vacancy; `FITGAP-03` regenerate concurrency and export parity.
- **Fix owner:** Backend/async-worker engineer. **Release:** BLOCK.

### FIND-005 — Invalid AI scores are coerced into authoritative 1–5 values

- **Severity:** P1 Major; **Classification:** BUILT_WRONG (data integrity); **Status:** CODE_FIXED_UNVERIFIED; **Evidence:** `SRC + PROBE(expression)`.
- **Impact:** Missing or malformed AI output can silently become a plausible L1 or L5 rating, changing a candidate's recorded portfolio and downstream fit/gap outcomes.
- **Expected:** Reject/retry invalid AI scores; a score is only authoritative when a semantically valid integer from 1 through 5 is present. Source validation expects levels 1–5 (`api/app/models/portfolio_skill.rb:9-12`).
- **Observed source:** `api/app/services/portfolios/generator.rb:150-178` populates `ai_level: skill_data['level'].to_i.clamp(1, 5)` in both configured and discovered skills. `nil`, `"n/a"`, and negative values become L1; numbers above 5 become L5. The normal model validation then sees a valid integer.
- **Reproduction/evidence:** `isolated_source_probe.json` FIND-005 executes that **same expression** with `"n/a"`, nil, -2, 88, `"4"`: output L1, L1, L1, L5, L4 respectively. The full worker/model/database flow is **not** run.
- **UI/API/DB:** Display reads `ai_level` from persisted `portfolio_skills` (`api/app/controllers/api/v1/portfolios_controller.rb:175-185`), so an invalid generation can appear normal. Future DB check: compare raw synthetic model response and saved level without real candidate data.
- **Root cause:** input coercion/clamping is used as error handling instead of validation; no provenance for raw AI output.
- **Regression checks:** `PORTFOLIO-01` valid levels persist unchanged; `PORTFOLIO-02` malformed/absent/out-of-range levels fail or receive explicitly modeled `unassessed` status, never silently L1/L5; `PORTFOLIO-03` no partial portfolio rows on failed validation.
- **Fix owner:** Backend/AI integration engineer. **Release:** BLOCK.

### FIND-003 — Duplicate vacancy skill labels silently collapse rows

- **Severity:** P1 Major **when duplicate labels are allowed**; **Classification:** SPEC_AMBIGUOUS + code behavior confirmed; **Status:** CODE_FIXED_UNVERIFIED; **Evidence:** `SRC + PROBE`.
- **Impact:** A role can appear to have fewer required competencies than saved in DB, invalidating a candidate's comparison.
- **Expected:** Either reject duplicate labels/IDs with clear validation or preserve all configured vacancy skills as distinct comparisons. The source DB schema does not constrain `vacancy_skills` label uniqueness (`api/db/schema.rb:199-205`) and the model has no such validation (`api/app/models/vacancy.rb:3-13`). External PRD rule remains unknown.
- **Observed:** `api/app/services/fit_gap/engine.rb:39-44` converts the relation to a hash with `.index_by(&:skill_label)`, overwriting an earlier item when labels repeat. `...:43-69` emits only one result per hash key.
- **Reproduction/evidence:** Actual `FitGap::Engine#build_skill_comparisons` executed with 2 vacancy skills named `Cloud Design`, IDs SK01 and SK02, expected levels 2 and 4. `isolated_source_probe.json` FIND-003 records **1 comparison instead of 2**. Assessor form may or may not prohibit the combination; database/API behavior still requires protection.
- **UI/API/DB:** Verify vacancy has 2 rows, fit/gap JSON and PDF show exactly 2 comparisons or reject duplicate at write-time. No DB run.
- **Root cause:** label used as an implicit unique identifier despite schema permitting repeated labels.
- **Regression checks:** `FITGAP-04` repeated labels across different IDs; `FITGAP-05` blank/mixed-case duplicate custom labels; compare count and identity with authoritative vacancy row set.
- **Fix owner:** Product/BA (define uniqueness) + backend. **Release:** BLOCK until data contract decided; adjust severity only with verified constraints.

### FIND-007 — Coverage monitoring WebSocket omits assessor-role validation

- **Severity:** P1 Major (conditional confidential assessment stream exposure); **Classification:** BUILT_WRONG if role restriction documented by assessor-only endpoints; **Status:** CODE_FIXED_UNVERIFIED; **Evidence:** `SRC`, `RUNTIME-UNVERIFIED`.
- **Impact:** A signed token with matching tenant but a non-assessor role may be able to subscribe to interview progress that REST protects as assessor-only.
- **Expected/source:** Assessor REST routes call `authorize_auth_token! :assessor` (`api/app/controllers/api/v1/sessions_controller.rb:6`). Coverage WebSocket is described in code as *assessor* monitoring (`api/app/channels/coverage_websocket_middleware.rb:5-6`).
- **Observed source:** `api/app/channels/coverage_websocket_middleware.rb:125-135` verifies JWT and tenant-scheme and resolves a same-tenant session, **without checking** JWT role. This differs from REST authorization.
- **Integration reproduction:** In an isolated tenant, mint test JWT with role `user` and valid same-tenant scheme, attempt `/ws/sessions/{session_id}/coverage` using auth message; assert connection is rejected with no coverage snapshot. Also verify assessor role passes. **Not executed**.
- **UI/API/DB:** Read exposure, no known write. Check WebSocket frames rather than only UI role guard.
- **Root cause:** custom WebSocket authentication only reimplements tenant lookup, omits permission logic.
- **Regression checks:** `WS-AUTH-01` invalid role denied; `WS-AUTH-02` foreign tenant denied; `WS-AUTH-03` assessor same-tenant receives current state; `WS-AUTH-04` expired JWT denied.
- **Fix owner:** Backend/security reviewer. **Release:** BLOCK unless policy explicitly allows broad tenant read.

### FIND-011 — Tenant scheme during login is caller-controlled without membership verification

- **Severity:** P1 Major *conditional on tenancy authorization policy*; **Classification:** SPEC_AMBIGUOUS; **Status:** OPEN; **Evidence:** `SRC`, `RUNTIME-UNVERIFIED`.
- **Impact:** A globally valid admin credential might be used to obtain an admin JWT scoped to a different organization by choosing a tenant scheme header.
- **Expected:** Decide whether platform admins are globally privileged or tenant-bound. If tenant-bound, verify user-to-organization membership before issuing the scoped JWT.
- **Observed source:** `api/app/controllers/api/v1/authentication_controller.rb:9-28` authenticates global `User`, checks only `user.role == 'admin'`, then sets JWT `scheme` from `X-Tenant-Scheme` when provided. `api/app/models/user.rb:3-17` contains role/email/password but no organization relation. This is a *potential* policy issue, not proof of unintended admin privileges.
- **Reproduction:** Seed separate admin users/tenants, supply tenant-B header with tenant-A user's credentials and check resulting JWT/tenant data access. Use isolated DB/test users only.
- **UI/API/DB:** Test the minted token's authorized data set and tenant membership table if external service defines it.
- **Root cause:** untrusted routing metadata drives tenant claim without visible membership proof.
- **Regression checks:** `AUTH-TENANT-04` reject unauthorized tenant selection; `AUTH-TENANT-05` valid home-tenant credentials pass; `AUTH-TENANT-06` explicitly authorized global admin behavior documented.
- **Fix owner:** Product/security + backend. **Release:** BLOCK until privilege model confirmed and implemented.

### FIND-006 — Candidate invite links use backend host in documented local setup

- **Severity:** P1 Major in the supplied **local monorepo setup** (candidate can't reach interview without manual URL substitution); **Classification:** BUILT_WRONG against documented client routing; **Status:** CODE_FIXED_UNVERIFIED; **Evidence:** `SRC + PROBE`.
- **Impact:** A recruiter copies an invitation, but the candidate goes to the API host rather than the web app, failing to start the interview using the shared URL.
- **Expected/source:** `api/README.md` and `README.md` say Rails API is at localhost:3001 and web UI at localhost:5173; `web/src/App.tsx:55-58` owns `/interview/:token` on web.
- **Observed:** `api/app/models/session.rb:28-31` builds invite using `ENV.fetch('APP_BASE_URL', 'http://localhost:3001')`. `api/config/application.yml.sample` and API config name `APP_BASE_URL` describe the backend URL. The frontend copies `session.invite_url` unchanged (`web/src/pages/assessments/AssessmentInvitePage.tsx:178-186`).
- **Reproduction/evidence:** `isolated_source_probe.json` FIND-006 invokes actual `Session#invite_url` with default: `http://localhost:3001/interview/synthetic-token` instead of web at `http://localhost:5173/interview/synthetic-token`. Actual browser 404 **not tested**. In production APP_BASE_URL may be overridden; this verdict applies to checked-in defaults.
- **UI/API/DB:** DB invite token is fine; generated presentation URL is wrong for documented local environment. Validate by GET both local paths when app runs.
- **Root cause:** backend URL reused for frontend deep link rather than an explicit `WEB_BASE_URL` setting.
- **Regression checks:** `INVITE-01` link points to configured web origin; `INVITE-02` escaped token path; `INVITE-03` DEV/staging/prod origin isolation.
- **Fix owner:** Backend/config engineer. **Release:** BLOCK for acceptance environment until verified; can be downgraded if deployment supplies correct web base consistently.

### FIND-008 — Invite-token expiry and revocation policy absent

- **Severity:** P2 Minor **as a documented spec gap**, potentially higher if privacy/security requirements mandate expiration; **Classification:** SPEC_MISSING; **Status:** OPEN; **Evidence:** `SRC`, `RUNTIME-UNVERIFIED`.
- **Impact:** A copied candidate link may remain valid indefinitely while its session is pending/active, with no explicit revoke or TTL behavior in this service.
- **Expected:** Product/BA must state TTL, single-use semantics, revoke/reset process, behavior after termination, and whether candidate_info is allowed for ended sessions.
- **Observed source:** `api/db/schema.rb:133-150` contains `invite_token` but no expiry/revocation field; `api/app/controllers/api/v1/sessions_controller.rb:118-153` uses token lookup without TTL; `api/app/channels/audio_websocket_middleware.rb:733-760` blocks ended sessions but not token age.
- **Reproduction:** With disposable clock/test DB, test token use before/after proposed TTL and revoke; no execution until requirements known.
- **UI/API/DB:** Needs policy before deciding correct outputs; avoid inventing expiry duration.
- **Root cause:** missing token lifecycle requirement/design.
- **Regression checks:** `INVITE-04` documented expiry/revoke behavior plus HTTP and WS boundary tests.
- **Fix owner:** Product/security. **Release:** CONDITIONAL, escalate if policy requires expiring links.

### FIND-009 — No automated regression or CI release gate tracked in original source

- **Severity:** P2 by runtime defect rubric; **Classification:** SPEC_MISSING (quality deliverable); **Status:** OPEN; **Evidence:** `SRC` inventory.
- **Impact:** A missing spec, silent data regression, or broken critical user journey could be merged and released unnoticed.
- **Expected/source:** Case study mandates Definition of Ready/Done gate, an automated red-to-green test net, two actual PR demonstrations, and tag-gated release.
- **Observed source:** Original 188-file tree has no tracked `api/spec/`, `api/test/`, frontend test suite, or `.github/workflows`; `web/package.json` exposes `dev/build/preview` without `test`; `api/Gemfile` does include RSpec dependencies but no tracked tests.
- **Reproduction:** `find api web -type f ...` against original paths and inspect `web/package.json`; `source_contract_checks.json` FIND-009 confirms. No CI run exists in this working copy; no independent repo yet.
- **UI/API/DB:** No automated assertions demonstrate persistence/error/permission outcomes.
- **Root cause:** lack of versioned quality pipeline.
- **Regression checks:** Required in Phases 3–4; verify actual red PR, green PR, regression and tagged release via remote CI evidence; no simulated screenshots.
- **Fix owner:** Quality/SDET + DevOps. **Release:** BLOCK at engineering quality gate (even though not an observed user-facing P0/P1).

### FIND-010 — Required engineering inputs not traceable in source snapshot

- **Severity:** P2 by runtime severity; **Classification:** SPEC_MISSING; **Status:** OPEN; **Evidence:** `SRC`, with an external documentation **visibility limit**.
- **Impact:** Team cannot prove that changes implement an agreed requirement or that critical paths have defined acceptance criteria/design plan.
- **Expected/source:** Case study Definition of Ready: linked PRD/spec, acceptance criteria or scenarios, solution/design plan, and traceability on changes.
- **Observed source:** No versioned feature PRD, AC, design plans or PR template were found in original 188-file snapshot. Root `README.md` points to a product wiki, **not inspected/verified**. There may be off-repository specifications; absence from snapshot alone does not prove no product spec exists.
- **Reproduction:** Compare source manifest paths with required artifacts; examine README and wiki link when access is possible; demonstrate a PR without input links is rejected once a gate exists.
- **UI/API/DB:** Acceptance-to-test mapping not established; no assertion of business correctness can be absolute without approved spec.
- **Root cause:** no enforceable traceability chain in current candidate copy.
- **Regression checks:** `DOR-01` missing PRD → red; `DOR-02` missing AC → red; `DOR-03` missing design → red; `DOR-04` valid inputs → green; no accidental allowlist bypass.
- **Fix owner:** Product/BA + QA lead. **Release:** BLOCK at DoR/G2, pending linked specs.

### FIND-012 — Local setup documentation contradicts source layout/config

- **Severity:** P2 Minor; **Classification:** BUILT_WRONG (documentation/setup); **Status:** OPEN; **Evidence:** `SRC`.
- **Impact:** New engineer may incorrectly configure API at port 3000, or try a nonexistent folder, delaying smoke/regression validation.
- **Expected/source:** One authoritative service startup guide consistent with root repo (`api/`, `web/`) and backend port 3001.
- **Observed:** `web/.env.example:1-5` points to port 3000 while root/API docs and app Puma port use 3001; `api/README.md` uses `cd ../ai-interview-web` while source path is `../web`.
- **Reproduction:** Compare docs and paths in source; run documented startup steps in disposable environment; no application execution so far.
- **UI/API/DB:** Setup contract only, not stored data.
- **Root cause:** stale setup guide after monorepo consolidation.
- **Regression checks:** `DOC-01` smoke script checks example API host against configured port; `DOC-02` README commands resolve existing dirs.
- **Fix owner:** Developer experience. **Release:** CONDITIONAL; resolve before reproducible CI evaluation.

### FIND-013 — Signup artifact is not reachable through web route or API

- **Severity:** P2 Minor **if signup belongs to the intended product**; **Classification:** OBSERVED_UNSPECIFIED; **Status:** OPEN; **Evidence:** `SRC`.
- **Impact:** If self-registration is in scope, creating an account cannot complete; if provisioning is intentionally invite/admin-only, the component is simply dead/obsolete code.
- **Expected/source:** Product spec must say whether public signup should exist. Do **not** automatically add public admin-signup routes.
- **Observed:** `web/src/pages/auth/SignupPage.tsx:12-34` calls `authApi.signup`; `web/src/services/auth.ts:16-17` calls `/signup`; `web/src/App.tsx:19-25` registers only `/login`; `api/config/routes.rb:8-12` defines login but no signup route.
- **Reproduction:** Inspect browser registered routes and route manifest once app boots; direct local `POST /api/v1/signup` only in disposable environment. Not executed.
- **UI/API/DB:** No verified reachable signup UI; system may use external identity provider and intentionally omit it.
- **Root cause:** feature removal/incomplete migration or deliberate exclusion (unknown).
- **Regression checks:** `AUTH-FLOW-01` explicit approved onboarding journey; remove dead code if deliberately excluded, not a blind security-weakening endpoint.
- **Fix owner:** Product/auth engineer. **Release:** CONDITIONAL until scope clarified.

## 3. Systemic patterns and prioritization

1. **Authorization bifurcation.** REST uses tenant-aware `Session` model scope but portfolio/override routes fetch unscoped descendants directly; WebSocket implements its own partial auth. This is not one isolated check; the application needs consistent authorization boundaries for derived objects and streams.
2. **Client acknowledgement trusted as business truth.** `audio_complete` assumes frontend only calls after backend completion, enabling premature persisted outcomes. Explicit server-side state guards and idempotency must become invariants.
3. **Derived results have weak provenance.** Fit/gap reports are keyed by IDs but not source versions; AI levels are coerced rather than validated; vacancy skill rows can be reduced by indexing on a non-unique label. A green UI can present incorrect computations.
4. **Work starts without machine-checkable inputs.** No tracked tests, CI gate, PR input checklist or release-tag status in original snapshot. The next regression can ship silently even if every issue above is repaired once.
5. **Config/API ownership unclear.** Backend URL reused for candidate frontend links; installation guides disagree. End-to-end smoke acceptance needs one consistent environment manifest.

### Recommended focused P1 implementation order for later phases

1. Introduce tenant-owned portfolio/skill lookups and WebSocket role enforcement; clarify admin scope (FIND-001, 007, 011).
2. Server-validate `audio_complete` state/ack and make finishing idempotent (FIND-002).
3. Validate AI skill levels before write and make save transactionally consistent (FIND-005).
4. Version/invalidate fit/gap on vacancy change; clarify duplicate label constraints (FIND-004, 003).
5. Correct candidate URL configuration and link smoke tests (FIND-006).
6. Implement no-spec/no-test/critical-regression CI gates and defend a real blocked PR (FIND-009, 010).

**Do not fix/implement these items during Phase 2.** Phase 3 designs the net, Phase 4 implements it, Phase 5 proves red-to-green on actual fixes. If time is tight, prioritize trustworthy high-consequence checks over trivial coverage metrics.

## 4. Risk-based audit matrix: scope and evidence

| Category | Inspected source | Outcome / needed runtime check |
|---|---|---|
| Create assessment → issue invite | assessment/session models, controllers, invite page | Link origin mismatch (FIND-006); real browser flow untested |
| Invite → candidate → WS audio | candidate endpoints, InterviewPage, audio middleware, EndHandler | Premature completion probe (FIND-002); real audio/DB untested |
| Transcript/coverage → portfolio | transcript schema, coverage worker, portfolio generator | Invalid score coercion (FIND-005); worker DB proof pending |
| Portfolio → override | portfolio & override controllers/models | Tenant lookup issue (FIND-001); DB non-mutation test pending |
| Vacancy → fit/gap → export | vacancy controller, FitGap engine, report controller, PDF export | Cache invalidation (FIND-004), duplicate skill loss (FIND-003); DB/PDF parity pending |
| Auth/tenant separation | JWT resolver, `TenantScoped`, auth controller, HTTP/WS controllers | FIND-001,007,011; two-tenant auth matrix pending |
| Negative/edge states | pending/ended session paths, invalid AI output, duplicate labels | Isolated probes passed as defect demonstrations; no HTTP test |
| Race, retries, async | handlers, WebSocket, Sidekiq jobs, Redis Pub/Sub | Potential duplicate completion/worker race; **unverified watchlist**, not promoted to defect |
| Timeout/error/recovery | frontend polling, WS reconnection, failed portfolio generation | Code inspected; runtime failure scenarios pending |
| Specification/readiness | original source inventory and README | Missing local traceable inputs (FIND-010); wiki may be separate |
| CI/release | source scripts, `.github` inventory | Missing coverage/gate (FIND-009) |
| Credentials/privacy | Phase 0 security review, sample env, public-source paths | No live secrets knowingly used; pre-publication security review still pending |

### 4.1 Explicitly unconfirmed questions (NOT findings yet)

- Will simultaneous HTTP and WS session-end events enqueue duplicate background jobs under real PostgreSQL isolation?
- Will a previously generated portfolio survive a retry, or can regeneration leave only a partial set after a failed create? `save_skills` destroys current rows before creates (`api/app/services/portfolios/generator.rb:150-178`); needs transactional failure injection.
- Do long-running interviews keep complete, unique transcript turns through Gemini/WS reconnects?
- Does editing an assessment mid-interview change the actively used skill rubric? This requires a product decision about immutable snapshots.
- Are AI-generated narratives reproducible/valid, and is a failed external AI request distinguishable from a valid low-confidence assessment?
- Is the linked external wiki a complete authoritative PRD? No external wiki content was downloaded during this audit.

## 5. Execution limits, reproducibility, and safety

**Environment:** Python 3, Ruby 3.3.8 (project pins 3.3.2), Node 22.16.0; no installed Rails bundle, PostgreSQL, Redis or app config. Phase 1 logged `rails` boot/version failure, TS dependency/typecheck failure, and closed HTTP ports. These are **environment blockers**, not asserted product defects.

**Commands executed:**

```bash
ruby assessment/evidence/phase-2/isolated_source_probe.rb
python assessment/evidence/phase-2/source_contract_checks.py
# Runtime application, remote API, DB, Gemini and public GitHub CI: NOT RUN
```

**Results:** Four original-method/expression probes produced the behaviors documented under FIND-002/003/005/006. Nine static contracts detected source-level risk indicators. Probe doubles are not feature tests: the PASS exit code means the probe ran, **not** that the application is safe.

**Data and permissions:** No real interview token, personal candidate data, user credential or company identifier is present in test input. Do not guess tenant schemes, enumerate IDs or send suspicious requests to deployed systems. Integration checks must run in an isolated, authorized environment with synthetic tenants/data only.

**Original source integrity:** Recheck `assessment/PHASE_0_FILE_INVENTORY.json` after this phase. No `api/` or `web/` file was intentionally edited. The independent GitHub repository is **DEFERRED_BY_USER**; this phase contains no PR, CI or tag.

## 6. Acceptance and exit assessment

- [x] Prioritized issues with severity **P0/P1/P2/P3 definitions** from the brief; no invented P0.
- [x] Distinguish spec gaps from wrong implementation and unverified code-contract concerns.
- [x] Each entry has impact, source-level reproduction steps, exact file locations, suspected root cause, regression test idea, owner role and release implication.
- [x] Four isolated source-execution probes; nine deterministic read-only contracts; execution evidence retained.
- [x] Enumerate UI/API/DB mismatches **and explicitly mark when persistence not verified**.
- [x] Audit authentication and multitenancy boundaries, candidate session lifecycle, derived scores, cache invalidation, unhappy paths, and workflow quality gaps.
- [x] Systemic patterns, preliminary release decision and recommended fix order.
- [ ] Database-backed and browser reproduction of findings — **BLOCKED_BY_ENVIRONMENT; deferred to integration test phase**.
- [ ] Reconcile findings against authoritative wiki/approved PRD — **NOT AVAILABLE IN THE SUPPLIED SOURCE SNAPSHOT**.
- [ ] Update final finding status after fixes — **NOT STARTED**; all currently OPEN.

**Phase 2 exit:** **PASS (source-based audit with explicitly blocked integration evidence)**. This fulfills the deliverable's evidence-first audit scope while preserving honesty about unresolved runtime validation. **It does not clear the application's release gate.** Next authorized phase: **Phase 3 — quality architecture and traceability design**, only on explicit user command.

---

## Phase 5 — code remediation addendum (pending integration)

| Finding | Code change | Evidence | Remaining work |
|---|---|---|---|
| FIND-001 | Tenant-scoped portfolio reads/exports/fit-gap/overrides; worker enforces matching tenant IDs | `AUTH-TENANT-01/02` isolated Ruby GREEN; source review | Test HTTP auth and persisted non-mutation with 2 tenants and real DB |
| FIND-002 | Durable server-side end-ready signal; active/coverage checks; row-lock end-once | `SESSION-01..04` Ruby GREEN | Migrate DB; RSpec integration; websocket real lifecycle and concurrent requests |
| FIND-003 | Preserve all vacancy skill rows; match by stable ID | `FITGAP-04/05` Ruby GREEN | Decide duplicate-label policy; persisted/PDF parity |
| FIND-004 | Persist source fingerprint for fit-gap and prevent serving stale reports | `FITGAP-01` pure Ruby GREEN; RSpec prepared | Migration and real worker/vacancy update races, PDF/JSON integration |
| FIND-005 | Strictly validate AI integers before writes, transactional replacement | `PORTFOLIO-01/02` Ruby GREEN; RSpec prepared | DB rollback/failure injection and real Gemini-schema compatibility |
| FIND-006 | WEB_APP_BASE_URL for invites, align frontend API/WS ports | `INVITE-01`, DOC-01/INVITE-03 GREEN | Deployed origin config; browser invitation smoke |
| FIND-007 | JWT role check in coverage WebSocket before tenant lookup/subscription | Source change; RSpec prepared but NOT RUN | WS/auth integration with real decoded token/Redis |
| FIND-011 | **NO CODE FIX**; caller-selected scheme lacks verified membership binding | Source analysis only | Product-approved tenant membership model + identity DB/SSO tests; remains P1 OPEN |

P2 findings not fully closed. `FIND-012` documentation and configuration have local changes, but setup/build remains blocked. PRs and GitHub CI statuses remain unavailable until independent repository is created. No Git commits, remote tests or release tag were fabricated.
