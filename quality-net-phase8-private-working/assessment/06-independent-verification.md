# Phase 6 — Harden the System and Independently Verify

**Date:** 2026-10-22 (Asia/Jakarta)  
**Scope:** Phase 6 ONLY. Private ZIP workspace derived from the Phase 5 handoff.  
**Decision:** **PHASE 6 EXIT GATE BLOCKED / DO NOT SHIP.** The available local test layers passed; runtime and remote-required layers did not run successfully.

## 1. Executive assessment

Phase 5's result was independently reproduced before any Phase 6 edits: 12 Ruby/Minitest source-contract tests (40 assertions), 25 Python quality-policy tests, and 2 Node URL configuration tests all passed. Post-hardening: **12 Ruby contracts (40 assertions), 32 policy tests, and 2 Node contracts** passed on each of three separately invoked runs. **Four deliberate Ruby production-code mutations were detected as assertion failures rather than harness errors**. This gives meaningful confidence in those four targeted source guards, **not** in the full Rails application.

The Phase 6 review uncovered and corrected two quality-net weaknesses:

1. **PR-controlled gate code:** `.github/workflows/quality.yml` originally executed `scripts/validate_pr_inputs.py` from the untrusted PR head. A PR could edit that script to always exit successfully. The PR job now checks out the **base SHA** into `.trusted-policy` and executes that validator while validating the PR-head checkout. A real local adversarial Git fixture demonstrates the untrusted runner exits `0` while the base validator exits `1`.
2. **False-positive contract:** Removing the readiness guard originally caused `SESSION-02` to error due to an incomplete test double, rather than failing its actual assertion. The fixture now includes an otherwise complete coverage map. The mutated app fails the intended assertion without any harness error.

Additionally, the PR policy now counts **deleted** files, rejects undeclared changed code/test/policy paths and duplicate path declarations, and recognizes actual `web/**/*.test.mjs` Node test files. These controls are backed by new tests. No P1 product-code implementation was altered during Phase 6.

## 2. Repeatability and exact results

| Check / command | Result | Evidence | Interpretation |
|---|---|---|---|
| `ruby api/spec/regression/critical_contract_test.rb --seed {11,424,837}` | **3 × exit 0**, each **12 runs / 40 assertions** | `evidence/phase-6/repeat-{1,2,3}-ruby.log` | Narrow real-source method contract only |
| `python3 -m unittest discover -s scripts -p 'test_*.py' -q` | **3 × exit 0**, each **32 tests** | `evidence/phase-6/repeat-{1,2,3}-policy.log` | Local metadata gate fixture validation, not actual GitHub PR |
| `node --test web/tests/api_config.test.mjs` | **3 × exit 0**, each **2 tests** | `evidence/phase-6/repeat-{1,2,3}-web.log` | Static frontend URL contract, not rendered UI |
| `python3 assessment/evidence/phase-6/run_mutation_probes.py` | **exit 0**, 4/4 mutants cause targeted test assertion failures, 0 harness errors | `evidence/phase-6/mutation-probes.json` | Mutants use disposable copies; real source unchanged |
| `ruby -c` all Ruby files under `api/` | **89 files pass** | `evidence/phase-6/all-ruby-syntax.json` | Syntax only, not load/boot |
| `node --check` web `.js`/`.mjs` files | **4 files pass** | `evidence/phase-6/node-js-syntax.json` | Syntax only, not TS/TSX |
| PyYAML parse of `.github/workflows/quality.yml` | **PASS**, six jobs | `evidence/phase-6/workflow-yaml-parse.json` | Not real Actions execution |
| `tsc --noEmit --project web/tsconfig.json` | **exit 2 / BLOCKED**: `vite/client` type absent | `evidence/phase-6/web-typecheck.log` | Frontend dependencies unavailable |
| `npm run build` (in `web/`) | **exit 2 / BLOCKED**: same missing Vite dependency | `evidence/phase-6/web-build.log` | **Do not claim a successful frontend build** |
| `npm ci --offline --ignore-scripts --no-audit --no-fund` | **exit 1 / BLOCKED**: `package-lock.json` absent | `evidence/phase-6/web-offline-install.log` | Reproducible install not possible |
| Rails gem availability and RSpec require probe | **exit 1 each / BLOCKED** | `evidence/phase-6/rails-bundle-check.log`, `rails-rspec-attempt.log` | No local Rails/`rspec/core` gems or running DB/Redis |

`assessment/evidence/phase-6/phase-6-checks.json` records the command list and statuses in machine-readable form. Repeated local success is **not proof against CI environment failures or DB races**.

## 3. Mandatory Phase 6 tasks vs actual execution

| PLAN.md Phase 6 requirement | Actual result | Decision |
|---|---|---|
| Fresh checkout / install / startup | ZIP extraction/inventory verified; no independent Git repo; Ruby/Node dependencies and infrastructure not available | **BLOCKED** for clean `git clone`, install and service startup |
| Lint / typecheck / build / unit / integration / E2E | Static syntax and source/policy contracts pass; frontend build and Rails integration blocked; browser suite absent | **PARTIAL** |
| Repeated key tests / investigate flakes | Three separate executions, varied Ruby seeds; no observed flakes in the limited suites | **PASS, narrow scope** |
| UI ↔ API ↔ persisted data correctness | Not executed; no authenticated running services or DB | **NOT VERIFIED** |
| Negative/boundary tests | 4 deliberately regressed Ruby behaviors, unauthorized tenant fixture, missing PR documents/tests, deleted code and modified gate | **PASS, isolated source/policy layer** |
| Isolation/teardown/order dependence | Mutants run in automatically removed temp trees; Python policies in temp Git repos; Ruby seeds varied | **PASS for local test harness only** |
| PR failing/passing gates | Local simulated Git diffs positive/negative; real remote PRs **not created at user's request** | **BLOCKED** for actual PRs |
| Security, dependencies, secrets, logs | Source/CI review and identifier/key marker scans; dependency vulnerability audit unavailable offline | **PARTIAL** |
| Bidirectional requirement ↔ test ↔ fix traceability | 41 planned IDs reconciled with existing files; details in `06-traceability-verification.md` | **PASS for evidence inventory, NOT test completion** |
| Residual P0/P1 and ambiguous rules | Seven P1s CODE_FIXED_UNVERIFIED; `FIND-011` P1 OPEN; see audit + below | **BLOCKED for release** |
| Public names/secret/history review | 45 text paths with organization/product references; no `.git` history; no private-key markers in scan | **BLOCKED for public publication** |

### Why the gate remains blocked

- `FIND-011`: the admin's right to select a tenant at login has no approved membership/SSO rule. **P1 OPEN**; cannot safely invent one.
- `FIND-001/002/003/004/005/006/007`: patches and isolated tests exist, but no end-to-end tenant isolation, real persistence, API responses, WebSocket, Sidekiq, migration execution or UI parity has been verified. **CODE_FIXED_UNVERIFIED**.
- `web/package-lock.json` and meaningful component-level frontend tests are still missing. These are mandatory in the authored CI and must **not** be bypassed.
- The repository is not yet an independent public GitHub repository, so no actual branch protection, trusted workflow management, blocked/passing PR checks, Git SHA or histories have been verified.
- Product wiki/acceptance approvals and ambiguous invite/duplicate-skill policies remain unresolved.

## 4. Trust model / residual CI concerns

Using the **base revision's validator** removes a straightforward PR-head Python script bypass. The hardened unit fixture intentionally replaces `scripts/validate_pr_inputs.py` in a disposable Git repository with a no-op and proves **untrusted HEAD returns success while the trusted base validator blocks**.

**Not a complete guarantee:** A PR that modifies the workflow file itself can still affect which GitHub Actions job definition executes, subject to GitHub's actual branch/repository protection and approval settings. Required status checks and policy/branch-rule enforcement must be configured **outside the PR's control** by the repository owner, ideally with approval required for workflow changes. A locally edited YAML file cannot substitute for that protection.

`pr-inputs` checks the presence and structural consistency of proposed requirements, acceptance criteria and designs. It does **not** approve business semantics, authenticate product ownership, prove tests are meaningful, or replace reviewer signoff.

## 5. Additional concerns observed, not certified as new runtime defects

- Sidekiq enqueue occurs after the session-end DB transaction commits; a process interruption in between could leave an ended session with pending work unscheduled. Requires a DB-backed fault/retry or durable-job/outbox design review before declaring reliable delivery.
- AI and fit-gap jobs remain susceptible to timing/race conditions absent real concurrent PostgreSQL and Sidekiq execution evidence; single-method tests do not establish transactional correctness.
- Two new DB migrations and the manually synchronized `api/db/schema.rb` have **not** been applied against a test PostgreSQL database; their runtime correctness is unknown.
- The source includes public-upload-prohibited identifiers and environment-specific names; wholesale string rewrites might change runtime behavior. Sanitization needs a separate controlled diff and regression rerun.
- A sample scan returned **zero private-key blocks** and **zero non-placeholder candidate credential assignments** after distinguishing the disposable CI PostgreSQL password; this is not a comprehensive secret/PII clearance.

## 6. Phase boundary

- Changed in Phase 6: workflow and policy validators/tests, isolated Ruby test fixture, `web/README.md` version description and new verification artifacts.
- **Product implementation `api/app/`, migrations, and `web/src/` unchanged.**
- User-owned independent repository creation remains postponed. No remote Git writes, commits, PRs, release tags, release notes or Phase 7 artifacts created.
- **Final verdict: Phase 6 LOCAL HARDENING COMPLETE, overall exit criteria NOT MET; release BLOCKED. Stop until explicit Phase 7 authorization.**
