# Submission checklist — current verified state

> This checklist supersedes the original Phase 8 *local-only* preflight, which was written before the GitHub repository and CI runs existed. It does not change historical test evidence or grant production release approval.

## Public engineering artifacts and traceability

- [x] Public independent [case-study repository](https://github.com/RyanHidayat96/fullstack-quality-gate), source under `api/` and `web/`, engineering artifacts under `assessment/`.
- [x] Risk-ranked [platform audit](01-audit.md), documented requirements, acceptance criteria and design notes.
- [x] Executable Rails/PostgreSQL, Ruby source contracts, Python gate tests, frontend render/config tests and a Vite/TypeScript build.
- [x] [Blocked PR #1](https://github.com/RyanHidayat96/fullstack-quality-gate/pull/1) and [passing PR #2](https://github.com/RyanHidayat96/fullstack-quality-gate/pull/2).
- [x] [PR #5](https://github.com/RyanHidayat96/fullstack-quality-gate/pull/5), [PR #7](https://github.com/RyanHidayat96/fullstack-quality-gate/pull/7), [PR #9](https://github.com/RyanHidayat96/fullstack-quality-gate/pull/9): authentic CI RED→GREEN for source-level security/flow fixes.
- [x] Real annotated `v1.0.0` tag and [tag-specific release gate](https://github.com/RyanHidayat96/fullstack-quality-gate/actions/runs/40277694610), which intentionally blocked the release.
- [x] Post-tag work clearly separated from [current verification](09-current-status.md) and [release decision](03-release-decision.md).
- [x] Documentation explicitly identifies **DO NOT SHIP** and records unapproved engineering assumptions.

## Unmet controls and open external approvals

- [ ] Branch rules actually require PRs, resolved conversations, and mandatory status checks. See [repository protection](10-repository-protection.md).
- [ ] Full Git history, PR refs, tags, archives and user-supplied source package reviewed for restricted names, rights and secret disclosure; authorized owner records publication clearance.
- [ ] Product/security owner approves FIND-011 multi-tenant admin/SSO grants and FIND-008 token expiry/revocation policy.
- [ ] Browser-to-API-to-DB journeys, actual audio/coverage WebSocket handshakes, concurrency and any remaining high-risk integration paths are verified.
- [ ] All 41 planned test cases reconciled to concrete executed test IDs/assertions. The historic Phase 6 count is not a current comprehensive coverage statement.
- [ ] Release owner or accountable reviewer explicitly approves every outstanding P1 risk on a **new** release candidate.
- [ ] Application submission deadline and hiring portal receipt confirmed. An actual recruitment-platform submission is not asserted by repository contents.

## Final evidence distinction

**Engineering demonstration:** The PR checks, CI runs, remediation commits and release-block mechanism are real.  
**Publication/legal clearance:** NOT VERIFIED.  
**GitHub branch protection:** NOT VERIFIED.  
**Product release:** **BLOCKED / DO NOT SHIP**.  
**Hiring-platform submission:** No confirmation recorded.

The case study is evidence of engineering judgment, not permission to fabricate missing approvals or mark a blocked release as shippable.
