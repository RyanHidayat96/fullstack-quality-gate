# Release notes — v1.0.0

> **Candidate version only.** No remote Git tag, GitHub release, deployment or tag-scoped CI run exists at the time of this document (2026-10-22). **Status: BLOCKED — DO NOT SHIP.** The proposed tag `v0.1.0-rc1` is a planning label, not evidence of an actual release.

## Intended scope

An interview-assessment application with separate API and web frontends. This candidate attempts to strengthen record authorization, interview lifecycle integrity, portfolio scoring and fit/gap consistency, candidate invitation origins, and automated engineering change gates. These are **implementation claims awaiting full-stack verification**, not claims of production readiness.

## Changes prepared in the candidate source

- Added tenant ownership constraints for portfolio read/export/override/fit-gap and associated background processing.
- Added server-validated interview end readiness and guarded duplicate session finalization.
- Preserved duplicate-label vacancy skills by stable row ID, tightened invalid AI-derived level handling, and added atomic portfolio skill replacement.
- Added fit/gap source fingerprints and stale-report handling.
- Hardened coverage WebSocket role validation and separated frontend invitation origin from API host.
- Introduced a PR metadata/Definition-of-Ready validator, regression contracts and an integration-test scaffold.
- Added fail-closed, **tag-specific release decision** workflow, independent `release_gate.py` policy, release-readiness ledger, and offline adversarial tests.

## Local evidence available (not remote CI)

- Ruby source-level contract regressions: 12 tests / 40 assertions PASS in Phase 6; mutation probes: 4 expected assertion failures on broken disposable code.
- Python PR policy tests: 32 PASS at Phase 6; Phase 7 adds release-gate policy unit tests (see `assessment/evidence/phase-7/`).
- Node static URL contracts: 2 PASS. These checks do **not** exercise a real browser session.
- Rails/RSpec database suites, PostgreSQL/Redis/Sidekiq workflows, TypeScript build and browser E2E: **NOT VERIFIED**.
- GitHub Actions: workflow is authored and syntax/structure checked only. No remotely observed PR or release-tag run.

## Known release blockers

1. **P1 FIND-011 OPEN**: tenant-admin membership/SSO authorization rules and implementation remain undefined.
2. **Seven other P1s CODE_FIXED_UNVERIFIED**: application edits pass narrow source-level contracts, but not real HTTP/database/WS integrity checks.
3. No successful database-backed and browser integration run; missing frontend dependency lockfile and substantive component tests.
4. 41 planned scenarios were assessed in Phase 6: 22 with partial local evidence, 3 RSpec files authored but not run, 16 not implemented as matching tests.
5. No two actual blocked/approved PR demonstrations, no branch protection or tag-run evidence; user will create the independent repository separately.
6. Public distribution is **not cleared**: identifier-bearing paths and dependency/secrets/licensing/history review require repository-owner verification.

## Operational release rule

The tag-triggered workflow must emit **RELEASABLE** only if all mandatory jobs succeed, the run is bound to the exact triggering tag commit, every audited P1 has documented verified disposition or explicit named acceptance, and all required verification evidence including a real release-owner signoff is present. Otherwise it must emit **BLOCKED** and fail the release-decision job.

**Decision:** `BLOCKED / DO_NOT_SHIP`. No risk acceptance has been granted or owner invented. See `assessment/03-release-decision.md`.
