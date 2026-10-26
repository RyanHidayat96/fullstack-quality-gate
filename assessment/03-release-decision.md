# 03 — Release decision: v1.0.0

**Decision: BLOCKED / DO NOT SHIP.**  
**Tag:** `v1.0.0` → commit `ae539d3ef07366f7a7060fc62ae69c47c25b96ea`.  
**Actual evidence:** [v1.0.0 GitHub Actions run](https://github.com/RyanHidayat96/fullstack-quality-gate/actions/runs/40277694610).

## What happened on the tagged commit

The release workflow ran on the real tag. Its technical checks succeeded, including engineering policy, Ruby regression contracts, scoped Rails/PostgreSQL specifications, frontend configuration/build checks and the aggregate quality summary. The **release-decision job deliberately failed closed** because not all P1 conditions, acceptance approvals, end-to-end scenarios and release authority were satisfied.

A passing engineering quality summary is **not** the same thing as an approved product release. No deployed production build or authorized risk acceptance is evidenced.

## Verified work after v1.0.0

The following changes are real and verified, but they **are not part of the older tag**:

| Change | Evidence |
| --- | --- |
| Expanded RSpec and React render checks | [PR #3](https://github.com/RyanHidayat96/fullstack-quality-gate/pull/3) |
| Configuration and source privacy guard | [PR #4](https://github.com/RyanHidayat96/fullstack-quality-gate/pull/4), [PR #6](https://github.com/RyanHidayat96/fullstack-quality-gate/pull/6) |
| Tenant-admin membership authorization | [PR #5](https://github.com/RyanHidayat96/fullstack-quality-gate/pull/5) |
| Tenant HTTP/DB and Audio WS auth tests | [PR #7](https://github.com/RyanHidayat96/fullstack-quality-gate/pull/7) |
| Removed unsupported self-service signup | [PR #8](https://github.com/RyanHidayat96/fullstack-quality-gate/pull/8) |
| Expiring and revocable invitation tokens | [PR #9](https://github.com/RyanHidayat96/fullstack-quality-gate/pull/9), [CI: 27 RSpec / 0 failures](https://github.com/RyanHidayat96/fullstack-quality-gate/actions/runs/40301673841) |

For the current evidence, read [01 — Audit](01-audit.md) and [02 — Quality System](02-quality-system.md). Actual GitHub PR and CI links above take precedence over earlier interim local notes.

## Release blockers

1. **P1 ownership and product approval.** Code-level remediation exists for FIND-011, but entitlement behavior for global admins, tenant membership provisioning and external SSO requires independent product/security approval. Other P1 coverage is not exhaustively validated under realistic concurrency or live integrations.
2. **Invitation policy.** FIND-008 now has test-backed expiry/revocation code, but the seven-day default and customer experience require product approval before rollout. Existing invitations older than that threshold are invalidated by migration.
3. **Integration and traceability.** Rails HTTP/PostgreSQL and React rendering pass scoped tests. A real browser-driven journey and actual WebSocket protocol upgrade/audio streaming have not been independently demonstrated. The entire 41-case plan is not yet proven complete.
4. **Repository enforcement.** CI runs on PRs, but no mandatory protected branch/ruleset was verified on `main`. Direct pushes could bypass pre-merge checks.
5. **Publication and source provenance.** Active app source identifiers are guarded in CI; historical commits and other archived materials may still carry restricted names. `publication_clearance=false` until an authorized rights and complete Git-history review is performed.
6. **Independent sign-off.** There is no named release owner approval or documented risk acceptance.

## Required decision before any new release

The responsible product/security owner must approve the entitlement and invitation policies, reviewers must verify remaining security/integration cases, repository administrators must enforce required PR checks, and publication rights must be cleared. Only then should a **new** candidate tag be pushed and evaluated by the fail-closed release workflow.

Do **not** re-tag `v1.0.0` or claim its historical CI included post-tag fixes. The current decision remains **BLOCKED / DO NOT SHIP**.
