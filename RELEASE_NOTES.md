# Release notes — v1.0.0 (candidate, blocked)

**Tag:** `v1.0.0` at commit `ae539d3ef07366f7a7060fc62ae69c47c25b96ea`.  
**Decision:** **BLOCKED / DO NOT SHIP**. The tag was created and evaluated; it was **not deployed**.

## Changes in the tagged candidate

- Tenant-scoped portfolio, override and fit-gap queries.
- Server-owned interview completion readiness and duplicate-completion handling.
- Strict AI skill score parsing, stable skill IDs, and transactional portfolio writes.
- Fit-gap fingerprints to reject stale computed reports.
- Scoped coverage authorization, corrected candidate invitation origin, and deterministic sample frontend configuration.
- Definition-of-Ready PR validator, Ruby/Rails regression tests, Python policy tests and a tag-specific release gate.

## Real GitHub evidence

- [PR #1 — rejected inputs](https://github.com/RyanHidayat96/fullstack-quality-gate/pull/1).
- [PR #2 — accepted inputs](https://github.com/RyanHidayat96/fullstack-quality-gate/pull/2).
- [Tag-specific CI run](https://github.com/RyanHidayat96/fullstack-quality-gate/actions/runs/40277694610): technical jobs succeeded; release-decision failed closed with a BLOCKED verdict.

## Known limitations and residual risk

- FIND-011 remains OPEN: tenant access has no approved membership/identity policy.
- Seven original P1 fixes have narrower technical evidence; full application and cross-tenant authorization review remains necessary.
- No end-to-end browser/WebSocket verification or real deployment authorization is recorded.
- The tagged commit predates [PR #3](https://github.com/RyanHidayat96/fullstack-quality-gate/pull/3) which expanded RSpec and React render checks. Those improvements are **not included** in the `v1.0.0` tag.
- No release owner or product stakeholder has accepted outstanding risk.

See [the current verification index](assessment/09-current-status.md) and [the release decision](assessment/03-release-decision.md). A subsequent candidate must have its own tag and evidence; do not rewrite or recycle `v1.0.0`.
