# 03 — Release Decision: v0.1.0-rc1 (Proposed; NOT TAGGED)

**Decision:** **BLOCK / DO NOT SHIP**  
**Release status:** **BLOCKED**  
**Decision date:** 2026-10-22 (Asia/Jakarta)  
**Evidence scope:** independent local Phase 6 checks and Phase 7 *release-policy* checks, **not remote GitHub Actions**.

## 1. Identity and constraints

| Field | Actual state |
|---|---|
| Proposed release tag | `v0.1.0-rc1` (candidate label only; **no tag created**) |
| Release tag SHA | **NOT AVAILABLE**; working copy is an extracted ZIP without `.git` history |
| Remote repo URL | **NOT AVAILABLE**; creation expressly deferred to repository owner |
| Actual GitHub Actions release run URL | **NONE — NOT RUN** |
| GitHub Actions job result for the proposed tag | **NOT VERIFIED** |
| Deployment/production | **NONE; NOT AUTHORIZED** |
| Local workflow contract and policy tests | Executed with logs linked below; **not a substitute for remote runs** |

No real GitHub commit, tagged release, approval, or accepted risk is represented here. Do not treat this report as a shipping authorization.

## 2. Release-gate checks

| Gate | Expected condition | Current state | Release impact |
|---|---|---|---|
| Tag identity | Actual annotated version tag resolves to the workflow's exact commit | NO TAG / SHA | BLOCK |
| CI requirements | PR policy unit, Ruby source contracts, API/DB, frontend and aggregate jobs succeeded on tag | ONLY LOCAL LAYERS VERIFIED | BLOCK |
| API/data integrity | Multi-tenant authorization, session states, portfolio and fit-gap persisted semantics proven using test DB | NO RAILS/PG/REDIS INTEGRATION | BLOCK |
| Web build/UI | Lockfile-based reproducible build, component regressions, browser/API/DB journeys | MISSING LOCKFILE / SUITE | BLOCK |
| P1 register | Every ranked P1 independently verified fixed or explicitly accepted by named owner | 7 `CODE_FIXED_UNVERIFIED`, 1 `OPEN` | BLOCK |
| Traceability | Critical planned test scenarios executable and linked to evidence | 22 partial / 3 unexecuted / 16 missing | BLOCK |
| Engineering inputs | Proposed spec, AC and design receive independent product approval | APPROVAL UNCONFIRMED | BLOCK |
| Change control | Real failed and passing PR gate runs reviewed | NOT AVAILABLE | BLOCK |
| Publication | Public name/secret/legal/privacy/history review completed | NOT CLEARED | BLOCK |
| Release approval | Real owner/reviewer must approve the exact tag and evidence | NOT PROVIDED | BLOCK |

**Gate implementation:** `.github/workflows/quality.yml` now listens for version tag pushes, runs existing mandatory quality jobs, then runs `release-decision` with `if: always()` and a non-optional fail-closed verdict. `scripts/release_gate.py` reconciles the severity-ranked audit with `assessment/release-readiness.json`, checks all critical status inputs, checks evidence references, and validates tag/commit binding passed from the workflow. It writes a JSON verdict and GitHub job summary when running on GitHub. A `BLOCKED` verdict exits nonzero.

## 3. Outstanding severity-ranked risks

| ID | Severity | Disposition | Consequence |
|---|---|---|---|
| FIND-001 | P1 | CODE_FIXED_UNVERIFIED | Cross-tenant portfolio and override access must be DB/API tested |
| FIND-002 | P1 | CODE_FIXED_UNVERIFIED | Premature/duplicate session completion must be concurrency tested |
| FIND-003 | P1 | CODE_FIXED_UNVERIFIED | Duplicate skill identity and outcomes require data-backed verification |
| FIND-004 | P1 | CODE_FIXED_UNVERIFIED | Stale fit-gap results require DB/worker tests |
| FIND-005 | P1 | CODE_FIXED_UNVERIFIED | Invalid AI level, atomic persistence and rollback require real DB tests |
| FIND-006 | P1 | CODE_FIXED_UNVERIFIED | Invitation URL must be exercised through web host and browser |
| FIND-007 | P1 | CODE_FIXED_UNVERIFIED | Coverage WebSocket role and tenant constraints need real WS tests |
| FIND-011 | P1 | **OPEN** | Tenant-admin membership binding lacks approved spec and safe implementation |

**Risk acceptance:** NONE. No real person approved an exception and no accountable risk owner was assigned; therefore there is no conditional ship route. Remaining P2/process issues are recorded in `assessment/01-audit.md` and Phase 6 verification.

## 4. Evidence and interpretation

- `assessment/evidence/phase-6/repeat-1-ruby.log` and `repeat-2-ruby.log` / `repeat-3-ruby.log`: Ruby source-level regressions, 12 runs / 40 assertions, local PASS.
- `assessment/evidence/phase-6/repeat-1-policy.log`: 32 local PR validator tests PASS before release-policy additions.
- `assessment/evidence/phase-6/repeat-1-web.log`: 2 static URL contracts PASS, not browser tests.
- `assessment/evidence/phase-6/phase-6-checks.json`: failed/blocked dependency and integration checks.
- `assessment/evidence/phase-6/traceability-verification.json`: scenario-to-evidence reconciliation.
- `assessment/evidence/phase-7/`: release policy unit tests, local workflow validation and fail-closed simulated verdicts.

**Interpretation:** Passing isolated contract and policy tests validates only their asserted behavior. The product's actual release correctness and data integrity are not established. The nonzero gate is intended, not a passing release test.

## 5. Required before any proposed SHIP decision

1. Obtain authoritative tenant membership/role policy for FIND-011; implement and test with two independent tenants and synthetic identities.
2. Run and preserve successful Rails/PostgreSQL/Redis/Sidekiq API/integration tests, and verify migrations, data integrity, duplicate jobs and error paths.
3. Generate a reviewed frontend lockfile, run build/typecheck/component tests, and independently execute core browser-to-DB journeys.
4. Complete missing critical test paths and review traceability; reconcile each P1 audit state with direct evidence.
5. Resolve outstanding spec/acceptance ambiguity and publication confidentiality review without indiscriminate source rewriting.
6. Once the owner has created a genuinely independent repo, demonstrate one **real failed** and one **real passed** PR; establish required branch/status protections.
7. Review the intended commit; create/push the annotated tag only when authorized, then capture an actual tag-specific CI run URL and SHA. Do not call a failing release gate green by weakening checks.
8. Reassess the release decision with a documented reviewer. Any unresolved P1 requires formally recorded, time-bounded risk acceptance with a real owner and approver, otherwise continue to BLOCK.

## 6. Owner and conclusion

- Technical recommendation: **BLOCK**.
- Product/security acceptance owner: **NOT NOMINATED / approval unavailable**.
- Release reviewer/approver: **NOT NOMINATED**.
- Scope: this decision is final for the **current candidate snapshot**, not a permanent judgment on future corrected versions.

**Final: BLOCKED — DO NOT SHIP.**
