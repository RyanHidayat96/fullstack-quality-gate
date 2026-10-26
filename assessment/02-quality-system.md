# 02 — Engineering Quality System

**Purpose:** Make missing engineering inputs and critical regressions visible before merge, reproduce defects with executable tests, and independently block an unsafe release. **Product release: BLOCKED / DO NOT SHIP.**

## Definition of Ready / Done

A code-changing pull request must link a **spec/PRD**, **acceptance criteria or test scenarios**, and a **solution/design plan**, all checked into this repository. It must also list a known regression test ID, risk, findings (where relevant) and every changed code/test/policy file.

The required PR fields are:

```text
Spec: assessment/requirements/REQ-...md
Acceptance: assessment/criteria/AC-...md
Design: assessment/designs/DES-...md
Findings: FIND-...
Tests: TEST-ID
Risk: high | medium | low
Affected paths: path/to/source, path/to/executable_test
Exemption: none
Justification: scope and evidence
```

Files in `assessment/requirements/`, `assessment/criteria/` and `assessment/designs/` are traceable engineering inputs, **not automatically approved business specifications**. The baseline test catalog is `assessment/design/phase-3-test-catalog.json`. `scripts/validate_pr_inputs.py` verifies document IDs, linked requirements, path safety, test references and changed executable test files. Missing spec, acceptance/design, valid test, or critical regression **fails the PR gate**. A genuinely docs-only PR can use the narrowly defined `DOCS_ONLY` exemption.

The `pr-inputs` job checks PR inputs using the **target branch's trusted validator**, not a policy script modified by the PR itself. This prevents an author from changing the validator in the same PR and silently bypassing it. Automated structural validation does **not** replace a reviewer's judgment about requirements, test usefulness, acceptance or risk.

## Quality net and exact commands

| CI job | What runs | Failure it prevents |
| --- | --- | --- |
| `policy-unit` | `python -m unittest discover -s scripts -p 'test_*.py' -v` | Accidental or adversarial bypass of metadata, CI and release policies |
| `pr-inputs` | `python .trusted-policy/scripts/validate_pr_inputs.py --repo . --event "$GITHUB_EVENT_PATH"` | PR proceeds without linked spec/AC/design, modified test and affected-file traceability |
| `api-contract` | `ruby api/spec/regression/critical_contract_test.rb` | Regression in critical Ruby behaviors independent of Rails test services |
| `api-critical` | `bundle exec rails db:migrate`; `bundle exec rspec spec --format documentation` from `api/` | HTTP, PostgreSQL persistence, service, model, middleware and worker regressions |
| `web-quality` | `npm ci --ignore-scripts --no-audit --no-fund`; `npm run build`; `node --test tests/*.test.mjs` from `web/` | Unrepeatable dependency/build, TypeScript, frontend configuration and component rendering regressions |
| `quality-summary` | Requires every relevant upstream job to succeed, including `pr-inputs` for PR events | A failed or skipped mandatory job presented as green |
| `release-decision` | On version tags, `python scripts/release_gate.py` validates the exact tag commit and release-risk ledger | A releasable badge with open P1 risks, missing checks, incomplete acceptance or no owner |

GitHub Actions is in `.github/workflows/quality.yml`, and the human-facing PR inputs are in `.github/pull_request_template.md`. The pipeline runs on pull requests, pushes to `main`, and `v*` tags. Rails CI uses isolated PostgreSQL and Redis service containers and synthetic fixtures; it does not run against a customer environment.

### Repeatable local verification

```bash
# From repository root:
python -m unittest discover -s scripts -p 'test_*.py' -v
ruby api/spec/regression/critical_contract_test.rb

# In api/ with PostgreSQL/Redis and test environment configured:
bundle exec rails db:migrate
bundle exec rspec spec --format documentation

# In web/:
npm ci --ignore-scripts --no-audit --no-fund
npm run build
node --test tests/*.test.mjs
```

Follow `api/README.md` and `web/README.md` for environment setup. Tests that use a browser/UI integration or live WebSocket upgrade must be reported separately; a static render test is not equivalent.

## Real RED → GREEN evidence

| Scenario | Before — CI RED | Fix and after — CI GREEN |
| --- | --- | --- |
| Missing Definition-of-Ready inputs | [PR #1](https://github.com/RyanHidayat96/fullstack-quality-gate/pull/1) deliberately blocked by `pr-inputs` | [PR #2](https://github.com/RyanHidayat96/fullstack-quality-gate/pull/2) has linked engineering inputs and a passing gate |
| FIND-011: unauthorized tenant selection | [Test-only run 40295447111](https://github.com/RyanHidayat96/fullstack-quality-gate/actions/runs/40295447111): 14 Rails examples, **4 failures** | [Run 40297012832](https://github.com/RyanHidayat96/fullstack-quality-gate/actions/runs/40297012832): tenant membership/token/WS fixes and all mandatory jobs PASS |
| Audio WebSocket JWT without grant | [Run 40299313986](https://github.com/RyanHidayat96/fullstack-quality-gate/actions/runs/40299313986): 24 Rails examples, **1 failure** | [Run 40299543911](https://github.com/RyanHidayat96/fullstack-quality-gate/actions/runs/40299543911): signed-audio access verified against grants, mandatory CI PASS |
| FIND-008: expiring/revoking invitation tokens | [Run 40300922243](https://github.com/RyanHidayat96/fullstack-quality-gate/actions/runs/40300922243): 27 Rails examples, **3 failures** | [Run 40301673841](https://github.com/RyanHidayat96/fullstack-quality-gate/actions/runs/40301673841): 27 examples, **0 failures**, all required jobs PASS |

The RED and GREEN runs above correspond to **real GitHub commits**, with production fixes between them. Earlier local Phase 0–8 notes were interim development records, not substitutes for these remote test results.

## What the net catches, and what it does not

**Covered by executable checks:** syntactic policy bypass, absent PR inputs/tests, test execution being reduced to file-presence checks, tenant JWT membership and revocation, selected cross-tenant HTTP/DB mutations, session completion state, stale fit/gap data, malformed portfolio scoring, invitation origin/expiry/revocation, Ruby contracts and React rendering/configuration.

**Not fully demonstrated:** actual browser-driven journeys through an interactive UI, WebSocket upgrade and audio streaming over a real network connection, realistic concurrent requests and jobs, all 41 originally planned test IDs, the exact behavior of external AI services, and product-approved global-admin/SSO semantics. The seven-day candidate invitation lifetime is a provisional security assumption.

**Repository enforcement gap:** CI may run on every PR, but GitHub currently reports `main` as **unprotected**, with no active repository ruleset. A direct push could bypass the PR gate. The repository administrator must activate rules requiring PRs and `quality-summary` plus relevant critical job checks; passing workflow runs are not proof this setting exists.

## Fail-closed tagged release

The repository has a real annotated `v1.0.0` tag. Its [tag-specific workflow run](https://github.com/RyanHidayat96/fullstack-quality-gate/actions/runs/40277694610) passed technical quality jobs but **blocked release** because risk/approval gates were not satisfied. The improvements in later PRs are **not included** in the tagged commit.

Release readiness is evaluated from `assessment/release-readiness.json` and the actual tag/check states; `assessment/submission-evidence.json` records independent-repository/PR/tag evidence for preflight. These machine-readable inputs are retained because the gate uses them, even though their filenames are not standalone PDF deliverables.

Read [01 — Audit](01-audit.md) for ranked risks and [03 — Release Decision](03-release-decision.md) for what must happen before shipping. **Never make a red gate green by weakening or deleting its checks.**
