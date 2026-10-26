# Phase 3 — Requirement / Finding / Acceptance / Automated-Test Traceability

> **DESIGN-ONLY** — all tests below are **PLANNED, NOT IMPLEMENTED OR EXECUTED**. Requirement/AC IDs are proposed engineering invariants, not approved product spec. Run status is **NOT RUN**, never green. See `design/phase-3-test-catalog.json` for structured source and `03-quality-architecture.md` for the planned gate.

## A. Full finding coverage (source-grounded)

| Finding | Severity | Proposed requirement | Proposed AC | Planned test IDs | Decision prerequisite |
|---|---|---|---|---|---|
| FIND-001 | P1 | REQ-SEC-001 | AC-SEC-001 | AUTH-TENANT-01, AUTH-TENANT-02, AUTH-TENANT-03 | Code-derived parent-tenant invariant; independently validate with request/DB tests |
| FIND-002 | P1 | REQ-SESSION-001 | AC-SESSION-001 | SESSION-01, SESSION-02, SESSION-03, SESSION-04 | Completion semantics require server-issued readiness proof; exact mechanism proposed, not approved |
| FIND-004 | P1 | REQ-DATA-001 | AC-DATA-001 | FITGAP-01, FITGAP-02, FITGAP-03 | Decide invalidate/recompute vs explicit historical snapshot; current unversioned cache implies freshness |
| FIND-005 | P1 | REQ-DATA-002 | AC-DATA-002 | PORTFOLIO-01, PORTFOLIO-02, PORTFOLIO-03 | Decide reject/retry/unassessed policy; silently authoritative L1/L5 is disallowed |
| FIND-003 | P1 | REQ-DATA-003 | AC-DATA-003 | FITGAP-04, FITGAP-05 | PENDING product choice: reject duplicates or retain distinct skills by stable identity |
| FIND-007 | P1 | REQ-SEC-002 | AC-SEC-002 | WS-AUTH-01, WS-AUTH-02, WS-AUTH-03, WS-AUTH-04 | Assessor-only inferred from protected REST/monitoring purpose, confirm policy |
| FIND-011 | P1 | REQ-SEC-003 | AC-SEC-003 | AUTH-TENANT-04, AUTH-TENANT-05, AUTH-TENANT-06 | PENDING global-admin vs tenant-admin privilege model and tenant-membership source |
| FIND-006 | P1 | REQ-FLOW-001 | AC-FLOW-001 | INVITE-01, INVITE-02, INVITE-03 | Frontend owns interview route; define WEB_BASE_URL or equivalent explicit public origin |
| FIND-008 | P2 | REQ-SEC-004 | AC-SEC-004 | INVITE-04 | PENDING defined TTL, revocation, use after end, replay and WS validation |
| FIND-009 | P2 | REQ-QUALITY-001 | AC-QUALITY-001 | TEST-GATE-01, TEST-GATE-02, TEST-GATE-04, TEST-GATE-06, RELEASE-GATE-01, RELEASE-GATE-02, RELEASE-GATE-03 | Case-study mandatory engineering input; release blocker even though P2 user-facing severity |
| FIND-010 | P2 | REQ-QUALITY-002 | AC-QUALITY-002 | DOR-01, DOR-02, DOR-03, DOR-04, TEST-GATE-03, TEST-GATE-05 | Case-study mandatory engineering input; wiki external not audited |
| FIND-012 | P2 | REQ-DOC-001 | AC-DOC-001 | DOC-01 | Choose monorepo-relative commands and one canonical API/web port contract |
| FIND-013 | P2 | REQ-FLOW-002 | AC-FLOW-002 | SIGNUP-01 | PENDING product decision whether self-signup is in/out of scope |

**Coverage totals:** 13 audited findings mapped; 8 P1; 5 P2; 41 planned executable test cases, **0 implemented / 0 run**. P1 trace coverage = 8/8 **planned**, not tested.

## B. Per-case assertion and target test file

| Test ID | Finding | Layer | Intended assertion (DB/API/output) | Planned target path | State |
|---|---|---|---|---|---|
| `AUTH-TENANT-01` | FIND-001 | request+db | Tenant B JWT receives 404/403 for tenant A portfolio read/export; zero foreign data returned; owner A access succeeds | `api/spec/requests/portfolio_access_spec.rb` | NOT RUN |
| `AUTH-TENANT-02` | FIND-001 | request+db | Tenant B override request denied; original portfolio skill, override and downstream report unchanged | `api/spec/requests/portfolio_skill_override_spec.rb` | NOT RUN |
| `AUTH-TENANT-03` | FIND-001 | request+worker+db | Foreign vacancy/portfolio combinations denied in request and worker; no report persisted, same-tenant succeeds | `api/spec/requests/fitgap_tenant_isolation_spec.rb` | NOT RUN |
| `SESSION-01` | FIND-002 | request+db | Pending invite audio_complete denied; status remains pending; no portfolio job | `api/spec/requests/session_completion_spec.rb` | NOT RUN |
| `SESSION-02` | FIND-002 | request+db | Active uncovered interview cannot be declared all_covered by candidate-only call; no final row/job | `api/spec/requests/session_completion_spec.rb` | NOT RUN |
| `SESSION-03` | FIND-002 | request+db | Server-confirmed completed session ends exactly once and queues a single portfolio job | `api/spec/requests/session_completion_spec.rb` | NOT RUN |
| `SESSION-04` | FIND-002 | request+db | Repeated/concurrent completion does not duplicate state transitions, jobs or portfolio rows | `api/spec/requests/session_completion_spec.rb` | NOT RUN |
| `FITGAP-01` | FIND-004 | request+db | After vacancy required level edit, stale report not returned as current | `api/spec/requests/vacancy_fitgap_freshness_spec.rb` | NOT RUN |
| `FITGAP-02` | FIND-004 | request+db | Recomputed report and API JSON/PDF export expected_level match DB vacancy skills | `api/spec/requests/vacancy_fitgap_freshness_spec.rb` | NOT RUN |
| `FITGAP-03` | FIND-004 | worker+db | Concurrent edit/queued jobs do not expose wrong-version report or preserve stale cache | `api/spec/workers/fitgap_regeneration_spec.rb` | NOT RUN |
| `PORTFOLIO-01` | FIND-005 | service+db | Valid integer 1..5 stored precisely, evidence and portfolio association preserved | `api/spec/services/portfolio_generator_spec.rb` | NOT RUN |
| `PORTFOLIO-02` | FIND-005 | service+db | nil, n/a, noninteger and out-of-range never persisted as plausible L1/L5 | `api/spec/services/portfolio_generator_spec.rb` | NOT RUN |
| `PORTFOLIO-03` | FIND-005 | worker+db | Invalid generated data does not leave complete portfolio with partial/false saved skills; explicit failed/retry state | `api/spec/workers/portfolio_generator_spec.rb` | NOT RUN |
| `FITGAP-04` | FIND-003 | service+db | Two stored rows with same label never silently collapse into one: either both compared or write rejected explicitly | `api/spec/services/fitgap_engine_spec.rb` | NOT RUN |
| `FITGAP-05` | FIND-003 | service+db | Blank/case-variant/custom labels follow explicitly chosen uniqueness rule; compare count/IDs/levels to DB | `api/spec/services/fitgap_engine_spec.rb` | NOT RUN |
| `WS-AUTH-01` | FIND-007 | websocket | Signed non-assessor JWT denied before coverage payload is emitted | `api/spec/requests/websocket/coverage_authorization_spec.rb` | NOT RUN |
| `WS-AUTH-02` | FIND-007 | websocket | Assessor JWT from tenant B denied tenant A coverage frames | `api/spec/requests/websocket/coverage_authorization_spec.rb` | NOT RUN |
| `WS-AUTH-03` | FIND-007 | websocket | Assessor from owner tenant receives permitted current coverage state | `api/spec/requests/websocket/coverage_authorization_spec.rb` | NOT RUN |
| `WS-AUTH-04` | FIND-007 | websocket | Expired/invalid JWT denied and no coverage bytes leaked | `api/spec/requests/websocket/coverage_authorization_spec.rb` | NOT RUN |
| `AUTH-TENANT-04` | FIND-011 | request+db | Tenant-bound admin must not mint another tenant JWT from arbitrary scheme header; behavior conditional on decided policy | `api/spec/requests/login_tenant_policy_spec.rb` | NOT RUN |
| `AUTH-TENANT-05` | FIND-011 | request+db | Authorized home-tenant login succeeds and JWT claims match resolved permitted tenant | `api/spec/requests/login_tenant_policy_spec.rb` | NOT RUN |
| `AUTH-TENANT-06` | FIND-011 | request+db | If global admin is designed, privileged tenant switch requires explicit grant with corresponding positive/negative tests | `api/spec/requests/login_tenant_policy_spec.rb` | NOT RUN |
| `INVITE-01` | FIND-006 | model+config | Generated invite URL has configured frontend origin/route, not API host | `api/spec/models/session_invite_url_spec.rb` | NOT RUN |
| `INVITE-02` | FIND-006 | model | Path uses encoded invite token and no malformed slash/unsafe route concatenation | `api/spec/models/session_invite_url_spec.rb` | NOT RUN |
| `INVITE-03` | FIND-006 | config+component | DEV/staging/prod public origin injection and rendered copied link consistent with backend value | `web/src/pages/assessments/AssessmentInvitePage.test.tsx` | NOT RUN |
| `INVITE-04` | FIND-008 | request+websocket+db | When policy specified, HTTP/WS reject expired/revoked token and define valid-before behavior without inventing TTL | `api/spec/requests/invite_token_lifecycle_spec.rb` | NOT RUN |
| `TEST-GATE-01` | FIND-009 | policy-fixture | Behavior-changing code without linked executable tests is blocked | `scripts/test_validate_pr_inputs.py` | NOT RUN |
| `TEST-GATE-02` | FIND-009 | policy+human-review | Presence of vacuous test cannot be accepted as meaningful; machine ensures execution, human reviews semantics | `scripts/test_validate_pr_inputs.py` | NOT RUN |
| `TEST-GATE-04` | FIND-009 | policy-fixture | Workflow/validator change triggers regression policy tests and explicit human review | `scripts/test_validate_pr_inputs.py` | NOT RUN |
| `TEST-GATE-06` | FIND-009 | ci-fixture | Required test or job skipped/failed/zero discovered cases cannot yield green status | `scripts/test_validate_pr_inputs.py` | NOT RUN |
| `RELEASE-GATE-01` | FIND-009 | ci-fixture | Tag with failing/missing check is BLOCKED | `scripts/test_release_quality.py` | NOT RUN |
| `RELEASE-GATE-02` | FIND-009 | ci-fixture | Tag with unresolved unaccepted P0/P1 is BLOCKED independent of green builds | `scripts/test_release_quality.py` | NOT RUN |
| `RELEASE-GATE-03` | FIND-009 | ci-remote | Actual tested version SHA with passing gates and cleared/accepted risk is eligible; remote proof required | `scripts/test_release_quality.py` | NOT RUN |
| `DOR-01` | FIND-010 | policy-fixture | Missing/invalid spec link causes nonzero exit | `scripts/test_validate_pr_inputs.py` | NOT RUN |
| `DOR-02` | FIND-010 | policy-fixture | Missing/invalid acceptance criteria causes nonzero exit | `scripts/test_validate_pr_inputs.py` | NOT RUN |
| `DOR-03` | FIND-010 | policy-fixture | Missing/invalid solution design causes nonzero exit | `scripts/test_validate_pr_inputs.py` | NOT RUN |
| `DOR-04` | FIND-010 | policy-fixture | Well-linked coherent docs+test mapping pass metadata gate only; not proof overall CI green | `scripts/test_validate_pr_inputs.py` | NOT RUN |
| `TEST-GATE-03` | FIND-010 | policy-fixture | External, traversed or placeholder doc path fails even if text includes checkbox | `scripts/test_validate_pr_inputs.py` | NOT RUN |
| `TEST-GATE-05` | FIND-010 | policy-fixture | Strict docs-only exemption does not exempt malformed docs or hidden code changes | `scripts/test_validate_pr_inputs.py` | NOT RUN |
| `DOC-01` | FIND-012 | static+smoke | README startup paths, ports and env variable names agree with actual config and service startup | `scripts/test_documented_setup.py` | NOT RUN |
| `SIGNUP-01` | FIND-013 | component+request | If in scope, route+API success/error/auth tests; otherwise document intentional absence and remove orphan consumer | `web/src/pages/auth/SignupPage.test.tsx` | NOT RUN |

## C. Evidence and requirement authority

1. **Observed source evidence**: For each finding refer to the corresponding section in `01-audit.md` and the source file given in the catalog. Probes are isolated, not real DB/UI tests.
2. **Proposed requirement**: `REQ-...` identifiers are engineering inputs to be instantiated in `assessment/requirements` in Phase 4. They **do not currently resolve to approved files**.
3. **Proposed acceptance**: `AC-...` identifiers map to behavioral assertions; AC documents must be authored, linked and reviewed for product-policy ambiguities.
4. **Test path**: Every proposed path is a **future target**, not a discovered tracked suite; some tests may be split/refactored as implementation clarifies controller boundaries. Update this matrix when a planned test is implemented and cite an actual executable test identifier.
5. **Release dependency**: P1 issues stay OPEN/UNVERIFIED until fixed and demonstrated red→green; G3 remains blocked. A checked box/green metadata validator is not proof of data correctness.

## D. Incomplete specifications and alternate contract handling

- **FIND-003**: do not choose duplicate labels silently. Both "reject on write" and "persist both rows uniquely" are possible product contracts; either must prevent silent row loss.
- **FIND-011**: admin scope and org-membership source are not documented; tests for cross-tenant privilege are conditional on a reviewed role policy.
- **FIND-008**: expiry duration and revocation semantics are unknown; `INVITE-04` is blocked until decided, never assume a specific number of hours.
- **FIND-013**: self-signup may be deliberately out of scope; `SIGNUP-01` does not demand a new route without product approval.
- **FIND-002**: choose a server-verifiable completion condition resistant to client-only calls/races; no implementation is approved just because a probe demonstrated a bad outcome.

## E. Exit gates for implementation phases

- **Phase 4**: real tests exist under planned or revised paths, run against unfixed source to show authentic RED, policy validator fails defined negative fixtures, CI wiring committed.
- **Phase 5**: correct production root causes, show tests GREEN without weakening; link actual failure and success logs/commits to each finding.
- **Phase 6**: actual PR gate FAIL/PASS demonstrations, integration parity (UI/API/DB) and rerun for deterministic results.
- **Phase 7**: tag-bound CI and verified risk register; clear BLOCKED/RELEASABLE decision.

## F. Follow-through ledger (fill only with evidence)

| Test ID | Actual test path | Baseline RED evidence | Fix SHA | GREEN evidence | Reviewer |
|---|---|---|---|---|---|
| `AUTH-TENANT-01` | NOT IMPLEMENTED | NONE | NONE | NONE | UNASSIGNED |
| `AUTH-TENANT-02` | NOT IMPLEMENTED | NONE | NONE | NONE | UNASSIGNED |
| `AUTH-TENANT-03` | NOT IMPLEMENTED | NONE | NONE | NONE | UNASSIGNED |
| `SESSION-01` | NOT IMPLEMENTED | NONE | NONE | NONE | UNASSIGNED |
| `SESSION-02` | NOT IMPLEMENTED | NONE | NONE | NONE | UNASSIGNED |
| `SESSION-03` | NOT IMPLEMENTED | NONE | NONE | NONE | UNASSIGNED |
| `SESSION-04` | NOT IMPLEMENTED | NONE | NONE | NONE | UNASSIGNED |
| `FITGAP-01` | NOT IMPLEMENTED | NONE | NONE | NONE | UNASSIGNED |
| `FITGAP-02` | NOT IMPLEMENTED | NONE | NONE | NONE | UNASSIGNED |
| `FITGAP-03` | NOT IMPLEMENTED | NONE | NONE | NONE | UNASSIGNED |
| `PORTFOLIO-01` | NOT IMPLEMENTED | NONE | NONE | NONE | UNASSIGNED |
| `PORTFOLIO-02` | NOT IMPLEMENTED | NONE | NONE | NONE | UNASSIGNED |
| `PORTFOLIO-03` | NOT IMPLEMENTED | NONE | NONE | NONE | UNASSIGNED |
| `FITGAP-04` | NOT IMPLEMENTED | NONE | NONE | NONE | UNASSIGNED |
| `FITGAP-05` | NOT IMPLEMENTED | NONE | NONE | NONE | UNASSIGNED |
| `WS-AUTH-01` | NOT IMPLEMENTED | NONE | NONE | NONE | UNASSIGNED |
| `WS-AUTH-02` | NOT IMPLEMENTED | NONE | NONE | NONE | UNASSIGNED |
| `WS-AUTH-03` | NOT IMPLEMENTED | NONE | NONE | NONE | UNASSIGNED |
| `WS-AUTH-04` | NOT IMPLEMENTED | NONE | NONE | NONE | UNASSIGNED |
| `AUTH-TENANT-04` | NOT IMPLEMENTED | NONE | NONE | NONE | UNASSIGNED |
| `AUTH-TENANT-05` | NOT IMPLEMENTED | NONE | NONE | NONE | UNASSIGNED |
| `AUTH-TENANT-06` | NOT IMPLEMENTED | NONE | NONE | NONE | UNASSIGNED |
| `INVITE-01` | NOT IMPLEMENTED | NONE | NONE | NONE | UNASSIGNED |
| `INVITE-02` | NOT IMPLEMENTED | NONE | NONE | NONE | UNASSIGNED |
| `INVITE-03` | NOT IMPLEMENTED | NONE | NONE | NONE | UNASSIGNED |
| `INVITE-04` | NOT IMPLEMENTED | NONE | NONE | NONE | UNASSIGNED |
| `TEST-GATE-01` | NOT IMPLEMENTED | NONE | NONE | NONE | UNASSIGNED |
| `TEST-GATE-02` | NOT IMPLEMENTED | NONE | NONE | NONE | UNASSIGNED |
| `TEST-GATE-04` | NOT IMPLEMENTED | NONE | NONE | NONE | UNASSIGNED |
| `TEST-GATE-06` | NOT IMPLEMENTED | NONE | NONE | NONE | UNASSIGNED |
| `RELEASE-GATE-01` | NOT IMPLEMENTED | NONE | NONE | NONE | UNASSIGNED |
| `RELEASE-GATE-02` | NOT IMPLEMENTED | NONE | NONE | NONE | UNASSIGNED |
| `RELEASE-GATE-03` | NOT IMPLEMENTED | NONE | NONE | NONE | UNASSIGNED |
| `DOR-01` | NOT IMPLEMENTED | NONE | NONE | NONE | UNASSIGNED |
| `DOR-02` | NOT IMPLEMENTED | NONE | NONE | NONE | UNASSIGNED |
| `DOR-03` | NOT IMPLEMENTED | NONE | NONE | NONE | UNASSIGNED |
| `DOR-04` | NOT IMPLEMENTED | NONE | NONE | NONE | UNASSIGNED |
| `TEST-GATE-03` | NOT IMPLEMENTED | NONE | NONE | NONE | UNASSIGNED |
| `TEST-GATE-05` | NOT IMPLEMENTED | NONE | NONE | NONE | UNASSIGNED |
| `DOC-01` | NOT IMPLEMENTED | NONE | NONE | NONE | UNASSIGNED |
| `SIGNUP-01` | NOT IMPLEMENTED | NONE | NONE | NONE | UNASSIGNED |

Any status claim must refer to actual local commands/logs or a real CI run. Leave evidence as `NONE` when it does not exist.


## Phase 6 evidence reconciliation

The original **Phase 3 design ledger above** is a historical PLAN-only baseline and uses `NOT IMPLEMENTED` placeholders. **Do not read it as the current implementation status.** The current machine-reconciled catalog is `assessment/06-traceability-verification.md` and `assessment/evidence/phase-6/traceability-verification.json`, which distinguish executed local contracts, authored but unrun Rails specs, and missing test scenarios. The source-only tests are **partial coverage**; no actual Rails+DB/browser integration is certified.
