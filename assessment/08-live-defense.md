# Live technical defense — 60–90 minutes

**Current verified state:** GitHub PRs, CI, Rails/PostgreSQL test runs and a real blocked tag exist. Do not repeat older Phase 8 statements that no remote repository or executable RSpec was available.

## Suggested CTO review flow

| Time | Topic | Evidence |
| --- | --- | --- |
| 0–10 min | Application risks and severity choices | [01-audit](01-audit.md) |
| 10–25 min | Requirement → AC → design → test → PR traceability | [02-quality-system](02-quality-system.md), [PR #1](https://github.com/RyanHidayat96/fullstack-quality-gate/pull/1), [PR #2](https://github.com/RyanHidayat96/fullstack-quality-gate/pull/2) |
| 25–45 min | Tenant grants, ownership and real RED→GREEN | [PR #5](https://github.com/RyanHidayat96/fullstack-quality-gate/pull/5), [PR #7](https://github.com/RyanHidayat96/fullstack-quality-gate/pull/7) |
| 45–60 min | Interview session integrity, invites and derived data | [PR #9](https://github.com/RyanHidayat96/fullstack-quality-gate/pull/9), [Rails specs](../api/spec/) |
| 60–75 min | Version-tag CI and release recommendation | [v1.0.0 tagged run](https://github.com/RyanHidayat96/fullstack-quality-gate/actions/runs/40277694610), [03-release-decision](03-release-decision.md) |
| 75–90 min | Remaining assumptions, counterexamples and Q&A | [09-current-status](09-current-status.md), [10-repository-protection](10-repository-protection.md) |

## Questions to be ready for

**1. Why were tenant boundaries and data integrity ranked above UI polish?**  
They can expose other organizations' candidate records or silently alter authoritative outcomes. A misleading fit-gap comparison can be more consequential than an obvious styling defect.

**2. What is genuinely demonstrated by a RED→GREEN chain?**  
[PR #5 RED](https://github.com/RyanHidayat96/fullstack-quality-gate/actions/runs/40295447111) exposed a missing membership boundary before the implementation; its later CI passed. [PR #7 RED](https://github.com/RyanHidayat96/fullstack-quality-gate/actions/runs/40299313986) exposed unauthorized signed audio WebSocket access. [PR #9 RED](https://github.com/RyanHidayat96/fullstack-quality-gate/actions/runs/40300922243) had three missing-lifecycle failures, while [GREEN](https://github.com/RyanHidayat96/fullstack-quality-gate/actions/runs/40301673841) ran 27 passing examples. These runs prove their stated assertions, **not** every production flow.

**3. Why did you choose explicit tenant membership?**  
A caller-supplied tenant scheme must not grant data access merely because a JWT is signed. The conservative engineering default denies unknown memberships and re-checks them when bearer tokens are used. Global-admin/SSO policy is not independently approved.

**4. What happens after tenant membership is revoked?**  
A previously issued signed JWT fails the protected API grant check. Coverage and signed Audio WebSocket authentication enforce equivalent membership restrictions. These are Rails request and helper regressions, not a proof of a live upgraded WebSocket stream.

**5. What protects candidate invitations?**  
PR #9 added expiration and revocation timestamps, server-side validity checks in candidate endpoints and audio token authentication, and a scoped revocation action. Seven days is provisional. Older invitations expire on migration; deployment requires stakeholder approval.

**6. Why was self-service signup removed instead of implemented?**  
The UI had no registered route or backend signup API. Adding open account/admin registration without tenant enrollment requirements would create new risk. PR #8 removed the dead path with a regression test; product must approve onboarding separately.

**7. How do you prevent premature session completion?**  
Server-owned readiness must be persisted, valid session state and coverage must be checked, and the end handler holds a DB row lock before finalizing to avoid duplicate side effects. Current request specs cover sequential idempotency; concurrency load testing is still a gap.

**8. What stops an attacker from editing their own PR validator?**  
The GitHub workflow runs its validator from the trusted base commit against the untrusted PR worktree; adversarial policy tests check bypass attempts. However `main` must also have enforced rules to stop direct pushes. Current repository policy is not verified as protected.

**9. Why is the release gate RED when technical checks pass?**  
Quality jobs test specified behavior. The separate release gate also requires stakeholder acceptance, consistent traceability, publication clearance, an approved candidate and P1 closure. [v1.0.0](https://github.com/RyanHidayat96/fullstack-quality-gate/actions/runs/40277694610) correctly failed closed.

**10. What would you do next before a release?**  
Confirm approved tenant/global-admin grants and invitation policy; complete browser→API→DB and live WebSocket tests, concurrency cases and the remaining design-catalog IDs; enforce repository rules; independently clear licensing/Git-history risks; obtain accountable reviewer signoff; then issue a new tag.

## Evidence boundaries

Never claim that historical Phase 4 logs were produced by commits before the repository existed, that tests performed live browser interaction when they did not, or that passing CI implies publication rights. Describe exactly what is demonstrated, what is a documented engineering assumption, and why the product release remains **BLOCKED / DO NOT SHIP**.
