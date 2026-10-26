# Reviewer quick tour — Fullstack Quality Gate

**Engineering verdict:** Substantial remediation and CI evidence exist. **Production release: BLOCKED / DO NOT SHIP.**  
**Latest evidence index:** [09-current-status.md](09-current-status.md). Historical Phase 0–8 logs reflect their own point in time and should not be used as current CI status.

## 1. The application and risk

The repository contains a Ruby on Rails/PostgreSQL/Sidekiq API under `api/` and a React/TypeScript/Vite frontend under `web/`. The workflow covers assessor assessments and invitations, candidate interview sessions, portfolios, skill analysis and vacancy fit-gap outputs.

The highest-consequence defects involve cross-tenant identity/ownership, premature interview completion, untrustworthy AI score parsing, stale derived reports and tenant-scoped WebSocket access. Read [01-audit.md](01-audit.md) first; all severity and speculative requirements are explicitly distinguished from observed source defects.

## 2. PDF case-study requirements and evidence

| Assignment stage | Where to look |
| --- | --- |
| Assess the platform | [Risk-based audit](01-audit.md), finding index and source probes |
| Build the Net | [Quality system](02-quality-system.md), [PR policy](../scripts/validate_pr_inputs.py), [GitHub Actions](../.github/workflows/quality.yml), regression tests |
| Fix to Green | [PR #5](https://github.com/RyanHidayat96/fullstack-quality-gate/pull/5) and [PR #7](https://github.com/RyanHidayat96/fullstack-quality-gate/pull/7) show true security test failure → fix → passing CI |
| Cut a Release | [Real v1.0.0 tag workflow](https://github.com/RyanHidayat96/fullstack-quality-gate/actions/runs/40277694610), [release decision](03-release-decision.md), [release notes](../RELEASE_NOTES.md) |
| Defend It Live | [Technical defense outline](08-live-defense.md), [current verification](09-current-status.md) |

The explicit Definition-of-Ready demonstration uses [blocked PR #1](https://github.com/RyanHidayat96/fullstack-quality-gate/pull/1) and [passing PR #2](https://github.com/RyanHidayat96/fullstack-quality-gate/pull/2). Do not confuse that demonstration with proving all application behavior.

## 3. Latest real remote evidence

- [PR #9 green](https://github.com/RyanHidayat96/fullstack-quality-gate/actions/runs/40301673841): **27 Rails examples, 0 failures**, with all mandatory jobs passing.
- [PR #9 red](https://github.com/RyanHidayat96/fullstack-quality-gate/actions/runs/40300922243): **27 Rails examples, 3 failures** before token lifecycle implementation.
- [PR #5 red](https://github.com/RyanHidayat96/fullstack-quality-gate/actions/runs/40295447111): **14 examples, 4 failures**; [subsequent green](https://github.com/RyanHidayat96/fullstack-quality-gate/actions/runs/40297012832).
- [PR #6](https://github.com/RyanHidayat96/fullstack-quality-gate/pull/6): vendor-name cleanup of active application code and a Python regression guard.
- [PR #8](https://github.com/RyanHidayat96/fullstack-quality-gate/pull/8): unsupported signup consumer removed; public self-registration was **not** implemented.

## 4. Local validation entry points

From `api/`, run `bundle exec rails db:migrate` against an isolated test database, then `bundle exec rspec spec --format documentation`. From `web/`, run `npm ci`, `npm run build` and `node --test tests/*.test.mjs`. From the repository root, run `python -m unittest discover -s scripts -p 'test_*.py' -v`. See [api/README](../api/README.md) for the supported environment and tenant grant provisioning requirements.

No production credentials, externally managed identities or live interview service keys are required for synthetic CI regressions.

## 5. Limitations reviewers should notice

The passing test suite does **not** fully demonstrate a real browser clicking through to persisted application workflows or an actual audio/coverage WebSocket upgrade. Branch rules are not verified as enforced, the 41-case original design catalog is not exhaustively certified, and historical public Git objects/redistribution rights are not cleared. Tenant-admin entitlement and seven-day invitation lifetime are conservative **unapproved product assumptions**.

See [submission checklist](08-submission-checklist.md), [repository protection](10-repository-protection.md), and [release risk ledger](release-readiness.json). Keeping a defensible release BLOCK is intentional, not an unsuccessful attempt to force a green deployment.
