# Engineering Delivery & Quality Net Master Plan

> **Scope:** Fullstack Quality Architecture, End-to-End Delivery Net & Gated Release Management.  
> **Mission:** Audit an existing API + web platform, implement enforceable engineering quality gates, prove real failures before fixes, correct high-severity defects, and make an evidence-based release decision.  
> **Source of truth:** The provided *Case Study: Fullstack Engineer (SDET Depth)* brief, the actual repository, and observed runtime behavior.  
> **Execution mode:** Stage-gated, evidence-first, small focused changes, reproducible results.  

## 0. Engineering Principles & Quality Bar

1. **Read before editing.** Inspect both `api/` and `web/`, both READMEs, existing scripts/tests, project documentation, tickets/notes/release notes, workflows, configs, and git state. Do not assume language, frameworks, package manager, database, auth, or deployment model until verified.
2. **Do not invent evidence.** Never claim a test ran, bug reproduced, CI passed, PR was created, or tag was pushed unless confirmed by actual command output or platform evidence. Distinguish `VERIFIED`, `INFERRED`, `ASSUMED`, `NOT TESTED`, and `BLOCKED`.
3. **Preserve provenance.** Do not silently rewrite business requirements. Separate `missing/ambiguous specification` from `implementation violates a known specification` and `observed behavior with no established expected outcome`.
4. **Protect data.** Do not commit secrets, tokens, credentials, personal data, client names, or confidential materials. Respect the brief's rule not to name the hiring company, product, or any client **anywhere in the public candidate repository**, including README, PR text, release notes, branch names, or commit messages. Use a neutral repository name. Do not publish material that appears confidential just because it exists in the supplied repo; sanitize and document the handling.
5. **Never game quality checks.** Never skip, delete, weaken, mark `xfail`, or replace meaningful assertions with trivial ones just to get green. If a test is flawed, explain and demonstrate why before correcting it, with evidence of preserved intent.
6. **Work in your own independent public repository.** Do **not** fork. Follow the case brief's clean-history import procedure. Obtain authorization/access and repository URL before attempting remote operations. Never overwrite an existing remote.
7. **CI is the authority, not a screenshot.** Local checks are necessary but not a substitute for actual GitHub/GitLab CI runs. Verify remote run links, PR checks, and release-tag checks where access permits.
8. **Keep scope risk-based.** Prioritize P0/P1, cross-service data integrity, auth/authorization if present, persistence, critical paths, and edge/error handling. Avoid broad refactors and superficial coverage inflation.
9. **Discipline over requirements.** Preserve traceability between problems, requirements, and actual code changes.
10. **Document each decision.** Record alternatives, trade-offs, assumptions, residual risks, owners, and supporting evidence.
11. **Do not misrepresent completion.** A local simulated gate is not equivalent to an actual blocked PR. A local tag is not equivalent to a remotely validated release. Never fabricate run URLs.
12. **Rigorous verification:** Review all changes, dependencies, tests, and security-sensitive decisions with senior engineering scrutiny.

### Required status protocol

At the beginning and end of **every phase**, write a concise checkpoint in `assessment/EXECUTION_LOG.md`:

```md
## Phase N — <name>
- Status: NOT_STARTED | IN_PROGRESS | PASS | FAIL | BLOCKED
- Started/finished: <timestamp>
- Verified facts: ...
- Assumptions: ...
- Commands run and exit codes: ...
- Evidence links/paths: ...
- Files changed: ...
- Risks and unresolved questions: ...
- Exit criteria: PASS/FAIL and why
- Next action: ...
```

**Do not advance past a failed mandatory phase gate.** Fix the issue or explicitly document a justified, non-deceptive exception and its impact on later phases. A blocked release must remain blocked.

---

## Phase 0 — Intake, repository isolation, and baseline safety

**Goal:** Establish a trustworthy working environment and a clean independent repo without changing application behavior.

### Tasks
- [ ] Read the entire case brief, record the actual platform deadline, and map every required deliverable to a phase.
- [ ] Confirm access to the source repository and verify that `api/` and `web/` exist. Inspect both README files and available project context.
- [ ] Inventory directories, scripts, configuration, dependencies, lockfiles, tests, workflows, infrastructure, migration files, and data stores.
- [ ] Identify the actual framework/runtime versions and platform prerequisites from manifests and lockfiles.
- [ ] Create an **empty, neutrally named public repository** under the candidate's account, only after authorization. Do not use GitHub Fork.
- [ ] Clone source into a working directory, remove original `.git` metadata, initialize clean git history, and connect to the new empty remote. Ensure no upstream/source reference is embedded in published repo metadata or documentation.
- [ ] Check tracked and untracked files for secrets and confidential/client-identifying content before first public push. Remove or redact sensitive items without breaking the runnable project; record sanitized files and reasons privately if needed.
- [ ] Establish a clean initial import commit and verify `git status`, branch, remote, and commit history.
- [ ] Record baseline environment details and how to reproduce setup; avoid committing `.env` values.

### Suggested inspection commands (adapt to OS and repo)

```bash
git status --short
git remote -v
git log --oneline -5
find . -maxdepth 3 -type f | sort | head -200
```

**Important:** The brief shows Unix-style commands (`rm -rf .git`). On Windows use a suitable shell or equivalent commands carefully. Never delete `.git` outside the intended copied source directory.

**Deliverables:** independent repository, clean initial commit, `assessment/EXECUTION_LOG.md`, environment inventory (can live in the log).

**Exit gate:** repo is independently owned, sanitized, reproducible to initialize, and has no accidental upstream link. If source access or public-repo permission is unavailable, mark remote tasks `BLOCKED`; do not pretend they are complete.

---

## Phase 1 — Architecture discovery and executable baseline

**Goal:** Understand the full request/data lifecycle before asserting defects.

### Tasks
- [ ] Read startup instructions and boot API + web together, using the documented method.
- [ ] Identify API endpoints, routing, controllers/services, persistence models, migrations, data validation, error handling, authentication/authorization, and third-party integrations **if present**.
- [ ] Identify web routes, state management, forms, API client, caching, loading/error states, and environment configuration **if present**.
- [ ] Draw the data flow for core business journeys: `UI action → HTTP request → API validation/business logic → database write/read → API response → UI render`.
- [ ] Inspect migrations/schema and test fixtures. Use isolated disposable test data, never destructive operations against a real/shared environment.
- [ ] Identify critical paths by user/business impact, not code volume.
- [ ] Run existing lint/typecheck/build/unit/integration/E2E scripts **if they exist**. Capture exact commands, versions, exit codes, and failure excerpts.
- [ ] Validate a minimum smoke path through both services, including persisted data if a safe test environment is available.
- [ ] Document limitations such as unavailable secrets, external APIs, missing database, inaccessible routes, or incomplete docs.

### Architecture artifacts
Create `assessment/architecture-notes.md` with:
- Verified stack and startup commands.
- Module/component and endpoint inventory.
- Key workflows and trust boundaries.
- Storage model and persistence risks.
- Current test/CI baseline and gaps.
- A compact Mermaid sequence/flow diagram if useful.

**Exit gate:** both services run or concrete blockers are documented; core paths, persistence points, and current checks are understood. Do not write speculative bug claims as verified findings.

---

## Phase 2 — Risk-based audit and defect triage (Task 1)

**Goal:** Produce a ranked, reproducible assessment of real client-facing risk.

### Severity rules — use exactly the brief's meaning

| Severity | Decision rule |
|---|---|
| **P0 Blocker** | Main objective cannot be achieved at all; no workaround. |
| **P1 Major** | UI appears to work but stored/computed data or logic is wrong; or objective requires manual workaround. **Any data-integrity issue is at least P1.** |
| **P2 Minor** | Feature works and data is correct, but there is a limited non-blocking defect. |
| **P3 Cosmetic** | Visual/copy-only issue without functional or data impact. |

Apply from P0 downward, stopping at first match. Do not inflate severity for aesthetics.

### Audit matrix (investigate applicable categories)
- [ ] Core end-to-end workflows and business invariants.
- [ ] Web/API contract consistency (types, status codes, field naming, validation).
- [ ] Data integrity: persisted vs displayed values; computed totals/statuses; duplicate writes; rounding/timezones where applicable.
- [ ] Negative/edge states: empty, malformed, boundary, duplicate, expired, unavailable dependency, network timeout, partial failure.
- [ ] Authorization and data isolation where applicable; never perform intrusive tests outside owned environment.
- [ ] Race conditions/idempotency where operations can be repeated or concurrent.
- [ ] Errors, retries, loading states, stale state/cache, and UI consistency after mutation.
- [ ] Missing PRD/spec, acceptance criteria, test scenarios, solution/design plan, and ambiguous behavior.
- [ ] Existing tests: meaningful assertions vs false positives; missing critical-path coverage.
- [ ] CI/release gaps: absent PR checks, missing release gate, no traceability, ignored failures.

### Reproduction procedure for each candidate finding
1. Identify **observed** behavior and the expected outcome source (spec, code invariant, documented business rule, or explicitly marked assumption).
2. Capture environment, setup/preconditions, sanitized input/test data, exact steps/requests, actual output, persisted DB/API outcome, and timestamp.
3. Repeat to distinguish deterministic failure from flaky/environmental behavior.
4. Inspect the relevant frontend, API, and persistence path; propose a likely root cause, labeling hypotheses as hypotheses.
5. Assign severity using the table, describe user/business impact, and classify `SPEC_MISSING`, `SPEC_AMBIGUOUS`, `BUILT_WRONG`, or `OBSERVED_UNSPECIFIED`.
6. Propose the smallest reliable automated regression check that would have caught the issue.
7. Rank by severity, impact, reproducibility, and release risk; identify systemic patterns across findings.

### Required defect record template

```md
### FIND-001 — <neutral title>
- Severity: P0/P1/P2/P3
- Classification: SPEC_MISSING | SPEC_AMBIGUOUS | BUILT_WRONG | OBSERVED_UNSPECIFIED
- Status: OPEN | FIXED | ACCEPTED_RISK | BLOCKED
- Business impact: <who/what is affected in one sentence>
- Expected behavior and source: <link to requirement, invariant, or labeled assumption>
- Actual behavior: <precise observation>
- Preconditions and reproduction: <numbered steps or HTTP request>
- Evidence: <safe relative paths, CI/test logs, screenshots where useful>
- UI/API/DB consistency check: <results, or why unavailable>
- Suspected root cause: <hypothesis, until verified>
- Proposed regression test: <test ID/path and assertions>
- Fix owner: <role or named owner if actually known>
- Release implication: BLOCK | CONDITIONAL | NONBLOCKING + rationale
```

**Deliverable:** `assessment/01-audit.md` containing executive summary, severity-ranked findings, systemic causes, specification gaps, scope/limitations, a preliminary **ship vs do-not-ship** call, and eventual final `FIXED/REMAINING` statuses.

**Exit gate:** every risk has severity, impact, reproducible evidence, spec-vs-build classification, and clear ranking. Findings without evidence must remain labeled unverified.

---

## Phase 3 — Quality architecture and traceability design (Task 2, design)

**Goal:** Design the smallest durable system that prevents missing inputs and catches real regressions.

### Definition of Ready / Done (enforceable)
Every non-exempt code-changing PR must link **all three**:
1. A spec/PRD (or an explicitly documented, reviewable requirement).
2. Acceptance criteria or test scenarios (prefer Given/When/Then where useful).
3. A short solution/design plan explaining approach and impact.

Also require:
- Affected code paths and risk level.
- Test evidence and traceability to requirements/acceptance criteria.
- A meaningful automated test for behavior changes; for non-behavioral changes, a narrowly defined documented exemption with justification and review, **not** an unconditional bypass.
- Passing required CI checks, no unresolved P0/P1 unless formally blocked or documented risk acceptance with owner.

### Design tasks
- [ ] Map each P0/P1 finding to one or more targeted regression tests and relevant requirements.
- [ ] Select test layers based on actual stack: unit for deterministic rules, API/integration for contracts and persistence, browser E2E for critical user journeys.
- [ ] Choose a minimal, maintainable framework consistent with existing tooling; avoid introducing Playwright or other tools merely by preference.
- [ ] Define deterministic test fixtures, isolated DB/test environment, seed/cleanup, stable selectors, and API mocking boundaries.
- [ ] Design a PR template with required fields and links to repository-local artifacts where possible.
- [ ] Design a **machine-enforced** PR metadata validator: fail if required linked documents are absent, empty, invalid, or do not resolve; check content minimally, not just checkbox strings.
- [ ] Design a code-change/test-change gate that catches missing meaningful tests, with explicit controlled exceptions where warranted.
- [ ] Design CI jobs for setup, static checks, tests, integration/E2E where feasible, and gate evaluation.
- [ ] Define branch protection/required status checks if the candidate controls repository settings; if settings cannot be enforced, disclose that CI failure alone may not technically prevent merges.
- [ ] Define requirement-to-test-to-finding traceability table and release-blocking policy.
- [ ] Define anti-flakiness controls (timeouts, deterministic data, service readiness, retries only with diagnosis, artifacts on failure).

### Traceability example

| Requirement / acceptance criterion | Risk / finding | Automated test | Gate | Status |
|---|---|---|---|---|
| AC-001 | FIND-001 | `path/to/test` | integration CI | RED/GREEN |

**Exit gate:** every planned check protects a named failure mode, every high-priority finding has a test strategy, and DoR/DoD is technically enforceable rather than documentation-only.

---

## Phase 4 — Implement workflow gate and automated quality net (Task 2, build)

**Goal:** Make CI fail automatically on missing engineering inputs and real critical-path defects.

### Implementation order
1. [ ] Add required documentation/acceptance-criteria conventions and PR template.
2. [ ] Implement a robust PR gate script using the platform's PR event payload and changed files; validate spec, acceptance criteria, and design plan links/content.
3. [ ] Implement test-presence/change-impact checks with narrowly reviewed exceptions. Avoid superficial rules that reward meaningless tests.
4. [ ] Add focused tests that **fail against verified existing defects** before fixing production code.
5. [ ] Add deterministic integration checks for data persistence and UI/API agreement.
6. [ ] Add lint/typecheck/build as appropriate and ensure commands fail on nonzero exits.
7. [ ] Add CI for PRs and relevant pushes; use least-privilege permissions, pinned or trusted actions, lockfile installs, concurrency controls, and no secrets on untrusted PR code.
8. [ ] Provide artifacts/logs sufficient to diagnose failures; never upload secrets or sensitive test data.
9. [ ] Document exact local and CI run commands, requirements, scope, and known limitations.
10. [ ] Validate the gate against negative and positive cases, not only the happy path.

### Required negative gate scenarios
- [ ] PR missing linked spec/PRD → **FAIL**.
- [ ] PR missing acceptance criteria/scenarios → **FAIL**.
- [ ] PR missing solution/design plan → **FAIL**.
- [ ] Behavior-changing PR without meaningful test or valid reviewed exemption → **FAIL**.
- [ ] Known critical regression → **FAIL**.
- [ ] Properly linked PR with required tests and no critical regression → **PASS**.

### Mandatory real PR demonstration
- [ ] Open **PR A** against the independent public repository with intentionally missing required inputs (or tests); capture actual failing required check and URL.
- [ ] Open **PR B** with complete inputs and passing checks; capture actual successful check and URL.
- [ ] Leave both PRs visible, whether open/closed/merged, per the brief.
- [ ] Verify checks actually run on PR events; do not rely on locally simulated logs.
- [ ] Keep demonstration changes safe and isolated; do not merge a deliberately invalid change.

**Deliverable:** quality-system code and CI, PR template, `assessment/02-quality-system.md` with architecture, instructions, covered risks, deliberately excluded risks, and actual PR evidence.

**Exit gate:** automated checks reproducibly fail for missing inputs/real defects, pass for valid changes, and both actual PR statuses are visible. If remote permissions prevent PR creation, mark demonstration `BLOCKED`, not complete.

---

## Phase 5 — Fix P0/P1 defects and prove RED → GREEN (Task 3)

**Goal:** Correct the root cause in real code and preserve evidence that the quality net catches the defect.

### Per-defect loop (repeat in priority order)
1. [ ] Confirm original bug reproduction and write/finalize failing regression test.
2. [ ] Execute test against **unfixed** baseline and record command, output, failure assertion, commit SHA, and CI run if available.
3. [ ] Trace root cause across UI/API/database rather than treating symptoms.
4. [ ] Make the smallest correct production fix, with data migration or compatibility plan if needed.
5. [ ] Re-run focused regression test; assert persisted/computed values, not just rendered UI.
6. [ ] Run adjacent unit/integration/E2E checks, static checks, and both-service smoke tests.
7. [ ] Inspect diff for unrelated changes, security regressions, new dependencies, and accidental test weakening.
8. [ ] Commit with clear message and link to finding/test ID; preserve red and green evidence in history.
9. [ ] Update audit finding status, root cause, and remaining risk.

### Strict red-to-green evidence

```md
| Finding | Failing commit/run | Failure assertion | Fix commit | Passing commit/run | Data/API/UI verified | Residual risk |
|---|---|---|---|---|---|---|
| FIND-001 | <SHA/URL> | <specific assertion> | <SHA> | <SHA/URL> | <details> | <none/description> |
```

**Rules:** Do not manufacture a red result by introducing a new artificial bug. The red check must catch a genuine baseline defect. Do not claim a CI run happened unless it did. If a finding depends on an unresolved specification, record the assumption and avoid pretending an arbitrary fix is confirmed correct.

**Deliverable:** code fixes in `api/` and/or `web/`, preserved regression tests, updated `01-audit.md`, and red-to-green section in `02-quality-system.md`.

**Exit gate:** targeted P0/P1 fixes are supported by failing-before/passing-after evidence, critical regression tests remain enabled, and no new blocker was introduced. Unfixed P0/P1 must be explicitly retained as release risks.

---

## Phase 6 — Harden the system and independently verify

**Goal:** Catch false positives, flaky tests, and integration gaps before making a release decision.

### Verification tasks
- [ ] Fresh clean checkout/install/startup test using documented commands.
- [ ] Run full relevant lint/typecheck/build/unit/integration/E2E suite; record exact results.
- [ ] Re-run key tests to assess determinism; investigate flakes instead of hiding them with retries.
- [ ] Confirm API responses and persisted data match UI state for critical workflows.
- [ ] Exercise at least representative negative/error and boundary cases.
- [ ] Validate test isolation, teardown, no dependence on execution order, and no shared-state pollution.
- [ ] Verify gate behavior on both failing and passing PRs.
- [ ] Review security-sensitive changes, secrets handling, authorization, dependencies, and logs, where applicable.
- [ ] Audit requirement ↔ test ↔ finding ↔ fix traceability in both directions.
- [ ] Review residual P0/P1 and ambiguous requirements; do not infer acceptance from passing checks.
- [ ] Check all docs and git history for prohibited names or confidential content before public submission.

**Exit gate:** clean reproducible verification results and honest residual-risk inventory. Any failed required check remains visible and impacts the release decision.

---

## Phase 7 — Tag, release gate, and ship/block decision (Task 4)

**Goal:** Make a version-specific release decision backed by actual CI.

### Tasks
- [ ] Create `RELEASE_NOTES.md` or `CHANGELOG.md` stating what the version claims to deliver, notable fixes, tests, and known limitations.
- [ ] Add CI trigger for release tag or release event; execute the same critical quality net with correct permissions and deterministic setup.
- [ ] Ensure the release result is tied to the specific tag/commit, not an unrelated `main` run.
- [ ] Define an unambiguous `RELEASABLE` vs `BLOCKED` status from mandatory checks and unresolved risk.
- [ ] Create an annotated version tag (e.g. `v1.0.0`) after verifying the intended commit and pipeline configuration.
- [ ] Push the tag only when authorized; capture remote CI run URL and result.
- [ ] Decide `SHIP`, `BLOCK`, or `SHIP WITH EXPLICIT RISK ACCEPTANCE` only if the brief's conditions are met.
- [ ] If any P0/P1 remains, default to `BLOCKED`; exception requires explicit documented acceptance, mitigation, and a **real named owner**. Never invent an owner or acceptance.
- [ ] Record exact tested tag/SHA, test results, unresolved findings, recommendation, and rationale.

### Decision template — `assessment/03-release-decision.md`

```md
# Release decision — <tag>
- Release tag / commit SHA:
- Status: RELEASABLE | BLOCKED
- Decision: SHIP | BLOCK | CONDITIONAL (explicit approval required)
- CI run URL and outcome:
- Gates executed and what each protects:
- Verified tests and data-integrity checks:
- Outstanding P0/P1 (or NONE, if verified):
- Other known limitations and assumptions:
- Risk acceptance: approver, named owner, mitigation, expiration (if applicable)
- Recommendation and rationale:
- Evidence links:
```

**Deliverables:** tag, release notes, tag-triggered CI, and `assessment/03-release-decision.md`.

**Exit gate:** remote tag and tag-specific release check are verified, or limitations are explicitly reported. Release status cannot be green merely because the build succeeds when known major risks remain.

---

## Phase 8 — Submission, independent review, and live-defense preparation (Task 5)

**Goal:** Make the work easy to evaluate and defend in a 60–90-minute technical discussion.

### Final submission checklist
- [ ] Public independent repo has neutral name, no fork relationship, no prohibited company/product/client references.
- [ ] `main` contains the quality system and all intended fixes.
- [ ] `assessment/01-audit.md` has ranked findings and final `FIXED`/`REMAINING` statuses.
- [ ] `assessment/02-quality-system.md` explains checks, commands, scope, PR evidence, and red-to-green story.
- [ ] `assessment/03-release-decision.md` explains actual tag, checks, risks, and ship/block decision.
- [ ] At least two real PRs remain visible: one blocked, one passing.
- [ ] Red-to-green progression is verifiable via commits and CI/log evidence.
- [ ] Tag and release notes exist; release CI status is tied to that tag.
- [ ] A fresh reviewer can reproduce setup and meaningful checks from the README.
- [ ] All links work; no placeholder SHAs, fake screenshots, or fabricated evidence.
- [ ] Repo URL is submitted through the hiring platform before its actual deadline.

### Live-defense talking points
Prepare to explain with real evidence:
1. Why the top three risks mattered more than lower-priority issues.
2. Which findings were missing specifications versus incorrect implementations.
3. One complete UI → API → persistence defect and how it was reproduced.
4. Why each chosen test layer was necessary; what remains uncovered.
5. How the DoR/DoD gate enforces requirements, not just checkbox theater.
6. The actual blocked PR and passing PR, including gate output.
7. The exact failing-before and passing-after test evidence and root-cause fix.
8. Why the tagged release was allowed or blocked, and who owns residual risks.
9. Which AI-generated suggestions were rejected/corrected and how they were verified.
10. What to improve next with another sprint, without pretending it is already done.

**Exit gate:** reviewer can independently navigate repo, reproduce meaningful tests, inspect actual PR/CI evidence, and understand the release decision in five minutes.

---

## Suggested execution schedule (adapt to actual deadline)

| Window | Focus | Mandatory checkpoint |
|---|---|---|
| Day 1 | Phase 0–2: setup, architecture, audit | Evidence-backed ranked findings |
| Day 2 | Phase 3–4: design and build quality net | Genuine red checks and blocked PR |
| Day 3 | Phase 5–6: P0/P1 fixes, passing PR, hardening | Verified red→green, regression green |
| Day 4 | Phase 7–8: release tag, decision, submission | Tag-specific CI, docs, working repo URL |

If the deadline is shorter, **reduce scope, not honesty**: prioritize critical paths, minimal enforceable gate, genuine red-to-green proof, and transparent blocked status where necessary.

## Priority order when time is constrained

1. Reproduce and rank real P0/P1 risks, especially persistence/data integrity.
2. Build a minimal *real* PR input gate and critical regression check.
3. Demonstrate actual blocked and passing PRs.
4. Fix the highest-risk defects with verifiable red→green evidence.
5. Run release gate on a real tag and document an honest decision.
6. Improve noncritical coverage, documentation polish, and P2/P3 only if time remains.

## Recommended artifact layout (adapt to discovered stack)

```text
/
├── api/                          # Existing service; change only as justified
├── web/                          # Existing service; change only as justified
├── assessment/
│   ├── 01-audit.md               # Required
│   ├── 02-quality-system.md      # Required
│   ├── 03-release-decision.md    # Required
│   ├── EXECUTION_LOG.md          # Additional execution checkpoints
│   └── architecture-notes.md     # Additional verified context
├── .github/
│   ├── PULL_REQUEST_TEMPLATE.md  # If using GitHub
│   └── workflows/               # PR and tag gates, if using GitHub
├── RELEASE_NOTES.md              # Or CHANGELOG.md
├── README.md                     # Reviewer quick start
└── PLAN.md                       # This plan
```

> The layout above is **proposed**, not a claim about the source repository's existing files. Use the actual hosting platform's equivalents if necessary.

## Delivery Cadence and Reporting Protocol

At the start of a working session, output:

```text
PHASE: <N/name>
OBJECTIVE: <one sentence>
VERIFIED REPO FACTS: <brief>
PLANNED ACTIONS: <brief>
DEPENDENCIES/BLOCKERS: <brief>
```

At the end of the phase, output:

```text
PHASE RESULT: PASS | FAIL | BLOCKED
CHANGED FILES: ...
COMMANDS / EXIT CODES: ...
EVIDENCE: ...
RISKS / ASSUMPTIONS: ...
NEXT PHASE: ...
```

**Before destructive commands, remote pushes, repo visibility changes, dependency upgrades with broad impact, or release publication:** confirm scope and authorization where not already granted. Do not ask unnecessary questions for normal local inspection and reversible development.

## Final definition of success

Success is **not** a large test suite or a green badge alone. It is an independently reproducible chain of evidence:

`verified audit → ranked real risks → enforced inputs → failing regression → correct fullstack fix → passing regression → actual blocked/passing PRs → tagged release gate → honest release decision`.

If a link in this chain cannot be verified, disclose it clearly and keep the relevant item incomplete. That is senior-level engineering judgment.
