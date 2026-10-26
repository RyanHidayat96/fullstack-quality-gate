# Reviewer Start Here — Candidate Submission Guide

> **Candidate Repository:** `RyanHidayat96/fullstack-quality-gate`  
> Welcome. This repository contains the complete case study submission for the Fullstack Engineer (SDET Depth) role. This guide outlines the evidence-backed deliverables across the platform audit, engineering quality net, defect fixes, and automated release gating.

## Five-minute evidence tour

| Minute | Inspect | What it establishes | What it does not establish |
|---|---|---|---|
| 0–1 | [`01-audit.md`](01-audit.md) | 13 ranked findings: eight P1, five P2; impact, provenance, and final status (Fixed vs Remaining) | No live production penetration testing |
| 1–2 | [`02-quality-system.md`](02-quality-system.md), [PR Gate](../scripts/validate_pr_inputs.py) | Required spec/acceptance/design/test links (DoR); demonstrated live in [PR #1](https://github.com/RyanHidayat96/fullstack-quality-gate/pull/1) & [PR #2](https://github.com/RyanHidayat96/fullstack-quality-gate/pull/2) | Does not replace human code review |
| 2–3 | [Phase 4 RED log](evidence/phase-4/source-regressions-red.log), [Phase 5 GREEN log](evidence/phase-5/ruby-after-green.log) | Five initially failing source assertions; 12 passing contract tests and passing RSpec suite in CI | Multi-tenant live cluster stress testing |
| 3–4 | [`06-independent-verification.md`](06-independent-verification.md), [`06-traceability-verification.md`](06-traceability-verification.md) | Repeated/mutation checks and transparent coverage traceability | Missing end-to-end browser video recordings |
| 4–5 | [`03-release-decision.md`](03-release-decision.md), [`RELEASE_NOTES.md`](../RELEASE_NOTES.md), [Tag v1.0.0 CI Run](https://github.com/RyanHidayat96/fullstack-quality-gate/actions/runs/40277694610) | Honest fail-closed BLOCKED release decision; verified tag binding and risk ledger | Commercial release authorization |

## Verified system snapshot

- API: Ruby 3.3.2 specified, Rails 7, PostgreSQL, Redis/Sidekiq; REST, WebSocket audio and monitoring; AI-dependent processing.
- Web: React 18, TypeScript, Vite, API and WebSocket clients.
- Relevant journeys: assessor configures vacancy/assessment; candidate interview lifecycle; transcript/portfolio generation; fit-gap calculations/exports.
- Trust boundaries: JWT/user role/tenant context; session state, async worker persistence, AI input validation, computed report freshness.
- Important open issue: `FIND-011`, tenant-admin membership authorization: **P1 OPEN**, needs product-approved contract.
- All other seven audited P1s are `CODE_FIXED_UNVERIFIED`; no P1 is claimed integration-verified.

## Reproduce the executable checks (run from repository root)

```bash
python3 -m unittest discover -s scripts -p 'test_*.py' -v
ruby api/spec/regression/critical_contract_test.rb
node --test web/tests/*.test.mjs
python3 scripts/release_gate.py --repo . --output assessment/evidence/local-release-verdict.json
python3 scripts/submission_preflight.py --repo . --output assessment/evidence/local-submission-preflight.json
```

**Expected with this snapshot:** Python/Ruby/Node local tests PASS; both gate commands **exit nonzero with `BLOCKED`** because required remote, integration, business-approval and publication evidence does not exist. An exit code 1 for the last two is *correct*, not an execution mistake. Run logs are preserved under [`evidence/phase-8/`](evidence/phase-8/).

Full Rails/PostgreSQL/Redis and web build commands plus missing prerequisites are recorded in [`06-local-verification-runbook.md`](06-local-verification-runbook.md); do not claim they ran merely because a CI workflow has been written.

## Evidence provenance and defensibility

1. **Repository & Commits:** Clean independent repository initialized with clean history on branch `main` and all CI workflows passing.
2. **Defect Regressions:** RED proof captured in `assessment/evidence/phase-4/source-regressions-red.log`; GREEN proof established in `assessment/evidence/phase-5/ruby-after-green.log` and executed in CI via RSpec and contract tests.
3. **Definition of Ready (DoR):** Linked specifications (`REQ-*`), criteria (`AC-*`), and design documents (`DES-*`) in `/assessment` structure every change.
4. **Live Pull Request Demonstrations:**
   - [PR #1 (BLOCKED)](https://github.com/RyanHidayat96/fullstack-quality-gate/pull/1): Code change without required DoR inputs triggers automated exit 1 on `pr-inputs`.
   - [PR #2 (PASSING)](https://github.com/RyanHidayat96/fullstack-quality-gate/pull/2): Code change with linked spec/criteria/design and matching test ID passes `pr-inputs` and CI quality net.
5. **Gated Version Tag:** Annotated tag `v1.0.0` pushed to GitHub; triggered release evaluation pipeline ([Run #40277694610](https://github.com/RyanHidayat96/fullstack-quality-gate/actions/runs/40277694610)), outputting a fail-closed `BLOCKED` decision due to open tenant membership policy.

## Technical review and live defense

See [`08-independent-review.md`](08-independent-review.md) for a claim-by-claim inspection checklist and [`08-live-defense.md`](08-live-defense.md) for a 60–90 minute defense agenda and evidence-grounded answers.

**Review decision for this submission: `SUBMISSION_READY`, `RELEASE_GATED_BLOCKED` (DO NOT SHIP without PO authorization for FIND-011).**
