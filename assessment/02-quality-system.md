> **Reader update (Phase 8):** The `REGRESSIONS_INTENTIONALLY_RED` label immediately below documents the historical **Phase 4 baseline**. The same original assertions now pass in Phase 5–8 local Ruby contracts (12 tests / 40 assertions), but API/database and browser verification remain unavailable. The remote PR gate, release tag and production readiness remain **BLOCKED**. See [Reviewer Start Here](08-reviewer-start-here.md) and [Independent Review](08-independent-review.md).

# 02 — Engineering Quality System: Phase 4 Implementation

> **Status:** LOCAL_IMPLEMENTATION / REMOTE_UNVERIFIED / REGRESSIONS_INTENTIONALLY_RED.  
> **Date:** 2026-10-22 (Asia/Jakarta). **Release:** **BLOCKED**.  
> The application source was not repaired during Phase 4. All **188** original files from the user-supplied clone still match their Phase 0 SHA256 values. Independent repository and GitHub PRs remain user-deferred.

## 1. Executive summary

This phase turns the Phase 3 quality architecture into executable PR-policy tests, genuine failing application regressions, DB-backed test scaffolding, frontend configuration contracts, and a GitHub Actions CI blueprint. The tests intentionally fail against original product behavior and **must not** be deleted, skipped, or weakened to make CI green. Real remote GitHub enforcement has NOT yet been observed.

**Measured, as executed**:

| Check | Exact executed command | Result | Evidence |
|---|---|---|---|
| Adversarial PR+CI-validator tests | `python3 -m unittest discover -s scripts -p 'test_*.py' -v` | **PASS: 25 tests, exit 0** | `evidence/phase-4/policy-unittest.log` |
| Ruby product method regressions | `ruby api/spec/regression/critical_contract_test.rb` | **RED: 5 runs, 5 failures, 0 errors, exit 1** | `evidence/phase-4/source-regressions-red.log` |
| Web config contracts | `node --test web/tests/*.test.mjs` | **RED: 2 tests fail, exit 1** | `evidence/phase-4/frontend-contract-red.log` |
| New Rails RSpec specs | `ruby -c api/spec/**/*.rb` (each newly added file) | **SYNTAX PASS**, **NOT EXECUTED** | `evidence/phase-4/phase4-summary.json` |
| Source integrity | SHA256 manifest of original 188 files | **PASS: 188/188 unchanged** | `evidence/phase-4/phase4-summary.json` |
| Live CI & PR statuses | GitHub Actions events (independent repo) | **NOT RUN** (user-deferred) | No CI run links exist |

**Evidence limitation:** the Ruby contract suite loads unmodified production Ruby methods with minimal stand-ins for Rails/DB/network effects. It proves method-level behavior, **not** HTTP, persisted tenant isolation, or real concurrency. The RSpec tests for persistence exist but cannot be executed until Rails 3.3.2, PostgreSQL/Redis and a test environment are available.

## 2. Files implemented (new files only)

- `scripts/validate_pr_inputs.py` — fail-closed PR metadata/changed-file validator; uses Python stdlib, untrusted text not evaluated.
- `scripts/test_validate_pr_inputs.py` — adversarial fixtures including missing inputs, invalid refs, symlinks/traversal, broken IDs, absent/irrelevant test ID, actual temporary Git diff, positive and negative CLI.
- `scripts/test_ci_contract.py` — fail-open CI YAML-pattern guard; real YAML parser still needed for full workflow semantics.
- `.github/pull_request_template.md` — reviewable DoR/DoD fields and evidence placeholders.
- `.github/workflows/quality.yml` — PR and main quality net: `policy-unit`, `pr-inputs`, `api-contract`, `api-critical`, `web-quality`, and `quality-summary`.
- `api/spec/regression/critical_contract_test.rb` — 5 failing original-source method regressions, no external services.
- `api/spec/rails_helper.rb`, `api/spec/support/synthetic_records.rb` — isolated Rails request/service/model test scaffolding.
- `api/spec/requests/session_completion_spec.rb` — persisted pending-state and no-job behavior.
- `api/spec/services/fit_gap_engine_spec.rb` — persisted duplicate vacancy skill comparisons.
- `api/spec/services/portfolio_level_spec.rb` — reject malformed AI levels before storing.
- `api/spec/models/fit_gap_freshness_spec.rb` — cache/report freshness after vacancy update.
- `web/tests/api_config.test.mjs` — deterministic source-level frontend env/client contract (not DOM test).
- `assessment/requirements/REQ-*.md`, `assessment/criteria/AC-*.md`, `assessment/designs/DES-*.md` — **9** linked engineering input sets, `Status: PROPOSED`; no product sign-off claimed.
- `assessment/design/phase-4-implementation-map.json` — per-ID implementation status for all 41 Phase 3 plans.

**No production `.rb`, `.tsx`, `.ts`, migrations or config files were fixed in this phase.**

## 3. Workflow gate: exact enforced vs review responsibilities

PR inputs are parsed from its body with exact fields `Spec`, `Acceptance`, `Design`, `Findings` (when applicable), `Tests`, `Risk`, `Affected paths`, and `Exemption`/`Justification`. For code changes, existing repo-relative docs must match prefixes and file IDs, contain required substantive sections, cross-link the same IDs, and reference known catalog test IDs. Code-changing PRs must include a changed executable test file containing the linked ID. Policy/workflow edits need a high-risk label and updated validator tests.

**Negative outcomes reproduced locally**: no spec, no AC, no design, no test, unknown test ID, path escape, external link, symlink, malformed input, incorrect requirement relationships, forged changed paths, and missing policy fixture on a workflow edit — blocked as designed. **Positive**: complete structural PR event with changed code + test passes metadata validation. These are synthetic Git repositories; NOT actual GitHub PR statuses.

Docs-only changes are narrowly exempt from adding an executable test if `Exemption: DOCS_ONLY` and meaningful justification are present. Changed structured docs are still validated. All ambiguous paths default to code impact. The script cannot establish whether an assertion is intellectually useful, whether business rules are approved, or whether a human reviewer actually approved the PR. Real branch rules and reviewer requirements must be configured on the future independent repository.

The gate never reads secrets or arbitrary filesystem paths outside checkout; linked docs have size bounds and reject symlinks. No PR code runs under `pull_request_target`; job permissions are read-only. Official trusted action major tags are used; converting to verified immutable action SHAs is still a hardening item.

## 4. Actual RED evidence (before fixing anything)

| Finding / test ID | Source method/layer | Actual RED proof | Phase 5 remedy required |
|---|---|---|---|
| FIND-001 / `AUTH-TENANT-01` | `PortfoliosController#fitgap` with foreign record double | Handler returns fit-gap success without controller-level tenant ownership guard | Enforce parent tenant ownership for direct portfolio, overrides, report read/write; confirm with tenant-separated HTTP/DB tests |
| FIND-002 / `SESSION-01` | `SessionsController#audio_complete` | Synthetic pending session changes to ended via termination handler | Require persisted server-verifiable readiness & idempotent state transition |
| FIND-003 / `FITGAP-04` | `FitGap::Engine#build_skill_comparisons` | Two same-label rows become one comparison | Preserve each row by stable key, or reject duplicate at write depending on product decision |
| FIND-005 / `PORTFOLIO-01` | `Portfolios::Generator#save_skills` | Invalid `'not_a_level'` accepted/coerced; no error | Validate raw AI response and transactionally preserve prior valid data on failure |
| FIND-006 / `INVITE-01` | `Session#invite_url` | Local invite points to API `:3001` rather than frontend `:5173` | Separate frontend public origin from backend base address |
| FIND-012 / `DOC-01`, `INVITE-03` | `web/.env.example`, `web/src/services/api.ts` | Default REST and WS ports `:3000` disagree with API `:3001` | Align documented env/fallback with application actual address |

Source probes intentionally do not provide a database tenant identity or execute HTTP middleware; `AUTH-TENANT-01` is a **source-method trust-boundary demonstration**, not evidence of actual unauthorized production access.

## 5. RSpec persistence and CI architecture

The DB suite declares synthetic assessments, sessions, portfolios and vacancies only. RSpec transaction fixtures isolate tests. The request spec expects a rejected completion, no changed session state, no new portfolio, and no queued background job. Service/model specs verify DB-visible comparison cardinality, AI-level input rejection and fit-gap freshness. All four new RSpec spec files passed `ruby -c`; **0 live DB-backed examples have run locally**.

CI job independence prevents a RED source contract job from suppressing DB-backed test execution. `quality-summary` runs on `always()` and checks each required job's exact success state; `pr-inputs` may be skipped only for non-PR `push` events. There is no `continue-on-error`, no bypass for intentional RED, no privileged PR execution, and nonzero check results block overall success. `rspec --fail-if-no-examples` prevents a fake green empty suite.

### Reproducible local commands

```bash
# Run from repository root
python3 -m unittest discover -s scripts -p 'test_*.py' -v
ruby api/spec/regression/critical_contract_test.rb    # expected exit 1, not a test harness error
node --test web/tests/*.test.mjs                         # expected exit 1 until config fixed

# Once Ruby 3.3.2 + bundle + local isolated PostgreSQL + Redis exist:
cd api
bundle install
RAILS_ENV=test bundle exec rails db:migrate
RAILS_ENV=test bundle exec rspec spec/requests spec/services spec/models --fail-if-no-examples

# Once network/dependencies accessible and *no* real secrets used:
cd web
npm install --package-lock-only --ignore-scripts --no-audit --no-fund
npm ci --ignore-scripts --no-audit --no-fund
npm run build
```

The frontend `web/package-lock.json` **does not exist** yet: npm registry access from this environment failed, so the frontend CI intentionally fails closed. A real React/component test suite and isolated browser test environment still need to be built, then run as mandatory CI jobs; a static config test is not a replacement. Do not auto-skip those requirements just to get GREEN.

## 6. Traceability and gaps

**Original plan:** 41 Phase 3 test IDs. Phase 4 implements targeted native method regressions, four RSpec files, two frontend config checks and policy fixture tests. See `design/phase-4-implementation-map.json` for each ID's exact `EXECUTED_*`, `DB_SPEC_WRITTEN_NOT_RUN`, `PARTIAL_*` or `PLANNED_NOT_IMPLEMENTED` status; do not equate implementation coverage with passing application behavior.

Remaining high-impact scenarios: role/tenant membership identity and WebSocket boundary (`WS-AUTH-*`, `AUTH-TENANT-04..06`), race-safe end-once completion (`SESSION-03/04`), cache invalidation from overrides, browser component behavior and expired/revoked invite policies; none are claimed proven. Product approval is needed for tenant admin scope, duplicate-skill semantics, invite token TTL/revocation, and server-side completion handshake. Source/reference evidence and exception rationale live in `01-audit.md` and `03-quality-gate-contract.md`.

## 7. Next-phase red-to-green ledger (do not fill early)

| Finding | RED captured | Fix commit SHA | GREEN retest | Remaining risk |
|---|---|---|---|---|
| FIND-001 | `evidence/phase-4/source-regressions-red.log` | **NONE** | **NOT EXECUTED** | Full tenant request/DB boundary unknown |
| FIND-002 | same | **NONE** | **NOT EXECUTED** | Server readiness/race policy unresolved |
| FIND-003 | same | **NONE** | **NOT EXECUTED** | Duplicate skill contract unresolved |
| FIND-004 | RSpec written, not run | **NONE** | **NOT EXECUTED** | DB cache stale behavior unverified |
| FIND-005 | `evidence/phase-4/source-regressions-red.log` | **NONE** | **NOT EXECUTED** | Existing valid data must be preserved |
| FIND-006 | source + frontend config RED | **NONE** | **NOT EXECUTED** | Public frontend domain injection needed |

**Gate outcome**: policy validation locally PASS; app regression suite RED by design; backend DB/DOM test runtime BLOCKED; frontend lockfile missing; remote checks and branch protection not configured. **The app is DO NOT SHIP.** Phase 4 is **partially verified** and the final mandatory PR demonstrations remain deferred until the user creates the independent GitHub repository and the underlying defects are fixed.

**Stop line:** Do not start Phase 5 or modify production business logic until the user explicitly authorizes the next phase.


---

## Phase 5 — RED → GREEN evidence (2026-10-22)

**Source-method CI contract:** Original 5 tests RED: `assessment/evidence/phase-5/ruby-before-red.log` (5 assertions failed). Same original 5 assertions after production remediation GREEN. Extended suite 12 tests / 40 assertions GREEN: `assessment/evidence/phase-5/ruby-after-green.log`. Original assertions unchanged, machine-verified in `original-assertion-preservation.json`.

**Frontend static config:** 2/2 GREEN (`web-contract-after.log`), previously 2/2 RED (`assessment/evidence/phase-4/frontend-contract-red.log`). **CI metadata policy:** 25/25 GREEN (`policy-after.log`). **Syntax:** 72 Ruby files PASS (`ruby-syntax-after.log`). Neither Ruby isolated probes nor static JS checks replace browser/DB validation.

**Missing:** `bundle` executable, Rails/Postgres, npm dependencies, independent GitHub repository/PRs, actual commit SHA and CI run. The application remains **BLOCKED FOR RELEASE**; see `PHASE_5_HANDOFF.md` for full remediation ledger and exact limits.


## Phase 6 verification amendment (2026-10-22)

This does not replace the Phase 4 RED or Phase 5 GREEN original evidence. Independent local repeatability verification: **three** runs of 12 Ruby tests/40 assertions, 32 Python quality-gate tests, and 2 Node config tests passed. A deliberate missing-readiness-guard mutation exposed an incomplete test double; the fixture was repaired without changing its business assertions. **4/4** isolated mutations now fail as actual assertions without runtime errors. See `assessment/06-independent-verification.md` and `assessment/evidence/phase-6/`.

CI security improvement: PR metadata validation now runs a checker copied from the trusted target **base SHA**, not a PR-editable Python script. Additional tests cover gate self-modification, undeclared/deleted code and Node `.test.mjs` files. This is local-only; real PR checks and externally enforced branch protection remain **UNVERIFIED**. Full application integration, `npm ci`, frontend build and Rails RSpec remain **BLOCKED**; no green claim extends to those layers.

## Phase 7 — Fail-closed version-tag release gate (2026-10-22)

Added version tag push trigger `v*` and a dedicated `release-decision` job in `.github/workflows/quality.yml`. The job uses `if: always()` after all critical checks so failures/skips still lead to an explicit blocked decision. It reads the exact tag and checked-out commit, verifies `git rev-parse "${GITHUB_REF}^{commit}"` equals the workflow SHA, then passes that evidence and `needs.*.result` statuses to `scripts/release_gate.py`. The check intentionally returns nonzero on `BLOCKED`, writes a job summary and attempts to upload `release-verdict.json` even when blocked.

The independent release policy reconciles all P1s from the original ranked audit against the machine-readable `assessment/release-readiness.json` register. A P1 is not cleared by a code change alone: it requires documented verified evidence or a real named risk acceptance (and an independent reviewer). Other mandatory checks cover integrated Rails/PostgreSQL/Redis execution, reproducible web build, component and browser-to-database behavior, traceability, accepted specs, publication clearance, two real PR demonstrations and release-owner signoff.

Phase 7 local results: **57 Python policy/release/workflow unit tests PASS; 12 Ruby contracts/40 assertions PASS; 2 Node static checks PASS**. Workflow YAML parses with 7 jobs and a tag trigger. Fail-closed local dry-run (no CI credentials) exits `1` with `BLOCKED`; a second clearly **synthetic** input with all CI statuses `success` and a fictitious SHA **still** exits `1` with `BLOCKED` due to P1/evidence gaps. Both reports are in `assessment/evidence/phase-7/`; neither is a real GitHub run. **No independent repo, actual PRs, annotated tag or remote release CI exists. Release remains DO NOT SHIP.**
