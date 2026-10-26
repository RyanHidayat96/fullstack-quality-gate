# 01 — Risk-based audit

**Scope:** Ruby on Rails API + React web app, cross-service behavior, persistence, authorization, candidate interview lifecycle, workflow inputs and release readiness.

**Recommendation: BLOCKED / DO NOT SHIP.** A successful technical build does not establish approved business policy, historical source clearance or production sign-off. Findings are ranked using the brief's first-match P0–P3 definitions; no P0 was demonstrated.

## Ranked findings and final status

| Rank | Finding | Severity | Classification | Impact, evidence and current state |
| --- | --- | --- | --- | --- |
| 1 | FIND-001 — Foreign portfolio and assessor override access | **P1** | BUILT_WRONG | Cross-tenant candidate disclosure or score mutation; scoped lookups fixed; negative API/DB assertions in `api/spec/requests/tenant_api_journey_spec.rb`. **CODE_FIXED_UNVERIFIED** end-to-end. |
| 2 | FIND-002 — Premature interview completion | **P1** | BUILT_WRONG | Pending or insufficiently evaluated session could be ended and queued for generation; server readiness, coverage guard and row-locked termination added. `api/spec/requests/session_completion_spec.rb`. **CODE_FIXED_UNVERIFIED** concurrency. |
| 3 | FIND-004 — Stale fit/gap results | **P1** | BUILT_WRONG | An edited vacancy could retain old comparison results; fingerprint validation added. `api/spec/models/fit_gap_freshness_spec.rb` plus [PR #13](https://github.com/RyanHidayat96/fullstack-quality-gate/pull/13) (vacancy change during generation, real database). **CODE FIXED, focused race regression PASS**; broader distributed concurrency not proven. |
| 4 | FIND-005 — Invalid AI scores coerced to valid values | **P1** | BUILT_WRONG | Authoritative portfolio data could store a plausible but false score; strict validation and transactional replacement. `api/spec/services/portfolio_level_spec.rb` plus [PR #14](https://github.com/RyanHidayat96/fullstack-quality-gate/pull/14) (invalid AI payload/rollback/retry regression). **CODE FIXED, focused worker integrity checks PASS**; live external AI outputs not verified. |
| 5 | FIND-003 — Duplicate skill labels collapse comparisons | **P1** | SPEC_AMBIGUOUS + BUILT_WRONG behavior | Distinct skill records could be silently lost; stable IDs now preserve comparisons. `api/spec/services/fit_gap_engine_spec.rb`. **CODE_FIXED_UNVERIFIED** broader PDF parity. |
| 6 | FIND-007 — Coverage WebSocket role check | **P1** | BUILT_WRONG | A signed token could access monitoring without correct role/tenant grant; checks enforced. `api/spec/middleware/coverage_ws_auth_spec.rb`. **CODE_FIXED_UNVERIFIED** actual upgraded WS stream. |
| 7 | FIND-011 — Caller-selected tenant on login | **P1** | SPEC_AMBIGUOUS | Admin JWT could target a tenant without membership. Explicit persisted grants, JWT rechecks and HTTP/WS tests added in [PR #5](https://github.com/RyanHidayat96/fullstack-quality-gate/pull/5) and [PR #7](https://github.com/RyanHidayat96/fullstack-quality-gate/pull/7). **CODE_FIXED_UNVERIFIED** approved global-admin/SSO policy. |
| 8 | FIND-006 — Invite link uses API origin | **P1** | BUILT_WRONG | Candidate sent to wrong host in documented local setup; frontend origin separated from API. `web/tests/api_config.test.mjs`; [PR #7](https://github.com/RyanHidayat96/fullstack-quality-gate/pull/7) validates persisted invite route. **CODE_FIXED_UNVERIFIED** deployed frontend. |
| 9 | FIND-008 — No invitation expiry or revocation | **P2** | SPEC_MISSING | Old invitations could remain usable indefinitely; seven-day provisional expiry, revoke API and HTTP/WS tests added in [PR #9](https://github.com/RyanHidayat96/fullstack-quality-gate/pull/9). **CODE FIXED; PRODUCT POLICY PENDING**. |
| 10 | FIND-009 — No versioned quality / CI net | **P2** | SPEC_MISSING | Defects could bypass checks; PR metadata gate, RSpec, policy tests and tagged release gate added. **FIXED IN CODE**, but branch protection remains unenforced. |
| 11 | FIND-010 — Missing traceable PRD, AC and design inputs | **P2** | SPEC_MISSING | Developers could merge unreviewed requirements; linked `REQ-*`, `AC-*`, `DES-*` docs and PR validation added. **FIXED IN WORKFLOW**. |
| 12 | FIND-012 — Setup/API/web origin mismatch | **P2** | BUILT_WRONG | Local integration failed to use the Rails endpoint consistently; examples and frontend fallbacks aligned. **FIXED IN CODE**, checked by `web/tests/api_config.test.mjs`. |
| 13 | FIND-013 — Orphan public signup | **P2** | OBSERVED_UNSPECIFIED | UI hinted at self-registration without a registered route/API; removed unimplemented consumer in [PR #8](https://github.com/RyanHidayat96/fullstack-quality-gate/pull/8). **FIXED BY REMOVAL** pending any future onboarding spec. |

**Severity and confidence:** P1 covers consequential data/logic errors or unauthorized access; P2 covers limited defects and missing-process inputs that still block the separately defined quality gate; P3 is cosmetic. No confirmed total platform outage warrants P0. Initial findings arose from original code inspection and isolated probes; subsequent PR tests support specified corrections, not a claim of production exploitation.

## Reproduction and regression approach

All tests use synthetic records in a disposable environment, never customer/candidate data.

| Risk / action | Negative reproduction and expected outcome | Verification |
| --- | --- | --- |
| Tenant record ownership | Create tenants A and B with distinct portfolios; use B's JWT to read/export or override A's portfolio. API must return 403/404 and persist no mutation. | `api/spec/requests/tenant_api_journey_spec.rb` |
| Caller-selected tenant | Sign in an admin without B membership using B's scheme. No B-scoped JWT may be issued; revoked grants must invalidate formerly signed tokens. | `api/spec/requests/login_tenant_policy_spec.rb`; [RED→GREEN CI](https://github.com/RyanHidayat96/fullstack-quality-gate/actions/runs/40297012832) |
| WebSocket token authorization | A signed admin token without tenant membership must not access audio monitoring; a valid tenant member must still work. | `api/spec/middleware/audio_ws_auth_spec.rb` and coverage middleware specs; [PR #7 CI](https://github.com/RyanHidayat96/fullstack-quality-gate/actions/runs/40299543911) |
| Candidate invitation | Expire or revoke a token, then request candidate metadata/audio completion or an audio WS connection. All must reject it. | `api/spec/requests/invite_token_lifecycle_spec.rb`; [RED](https://github.com/RyanHidayat96/fullstack-quality-gate/actions/runs/40300922243) → [GREEN](https://github.com/RyanHidayat96/fullstack-quality-gate/actions/runs/40301673841) |
| Interview completion | Attempt `audio_complete` on pending/incomplete session. Preserve state and do not enqueue a generated portfolio; repeat completion should not duplicate results. | `api/spec/requests/session_completion_spec.rb` and Ruby method contracts |
| Derived data | Edit vacancy inputs after report generation, include duplicate labels with distinct IDs, and supply malformed AI levels. Detect stale output, preserve both rows, reject corrupt writes. | `api/spec/models/fit_gap_freshness_spec.rb`; `api/spec/services/*_spec.rb` |

## Root-cause themes

1. **Authority inferred from input:** role-only checks and caller-supplied tenant claims were not equivalent to verified record ownership. The fix binds scoped operations to persisted grants and tenant ancestry.
2. **Plausible UI masking incorrect persistence:** AI score coercion, stale fit/gap reports and duplicate-label map keys could present credible but wrong outcomes. The net checks stored state and computed values.
3. **Underspecified lifecycle:** session readiness, candidate invitations and self-service onboarding require explicit contracts; unknowns should fail closed instead of being invented as approved product rules.
4. **Workflow drift:** absent spec/AC/design links and no executable checks made regressions easy to miss. Mandatory PR policy plus tagged release evaluation now provide concrete evidence, though GitHub branch rules still require administrative enforcement.

## Release boundary and remaining work

- Rails/PostgreSQL requests, Ruby contracts, frontend and policy checks pass. [Quality Net on final `main`](https://github.com/RyanHidayat96/fullstack-quality-gate/actions/runs/40323669757) is **SUCCESS**. [Live browser/WebSocket CI](https://github.com/RyanHidayat96/fullstack-quality-gate/actions/runs/40323669835) also **SUCCESS**: Chromium UI login/invite, persisted HTTP data, real coverage WS upgrade and revoked audio-token refusal. Live external AI audio streaming remains untested.
- Real browser/DB and selected WebSocket handshakes are verified. The [catalog-audit job](https://github.com/RyanHidayat96/fullstack-quality-gate/actions/runs/40323669835) reconciles **41 scenarios: 22 executable, 12 partial, 7 missing**; executable labeling does not itself establish independent E2E proof. Realistic concurrency, external AI streaming and remaining scenarios require follow-up.
- FIND-011 global-admin/SSO entitlements and FIND-008 default seven-day token lifetime are **engineering assumptions**, not product/security sign-off.
- The public repository still needs enforced PR/branch protection and historical Git-object/publication review (original brief and an old copied working tree remain accessible by commit SHA). A named release risk owner is not recorded. These risks are disclosed rather than represented as approvals.
- A real tagged candidate `v1.0.0` ran CI and was correctly **BLOCKED**; later fixes are not retroactively part of that tag. See [03 — Release Decision](03-release-decision.md).

**Final decision: BLOCKED / DO NOT SHIP** until those verifications and approvals are complete. An intentionally blocked release is an evidence-based decision, not a failed attempt to force an artificial green badge.
