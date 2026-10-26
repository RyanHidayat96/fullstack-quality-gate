# Independent Review — Phase 8 Final Evidence Assessment

**Scope:** user-supplied Phase 7 ZIP, freshly extracted. No online build/production environment, Git history or owner-controlled independent public repo is present in this working directory. This review judges evidence quality and submission readiness separately.

## Reviewed claims and evidence status

| Claim | Independent check | Outcome / confidence |
|---|---|---|
| Phase 7 package can be unpacked without path escape | validate ZIP entry paths and extracted paths | PASS, local artifact only |
| Required assessment trilogy exists | check three files in `assessment/` | PASS, contents reviewed; two include historical phase descriptions |
| Ruby source contracts still pass | `ruby api/spec/regression/critical_contract_test.rb` | PASS: 12 tests/40 assertions; method-level only |
| PR/release policy suite passes | `python3 -m unittest discover -s scripts -p 'test_*.py'` | PASS: see `evidence/phase-8/python-with-preflight.log` for updated total |
| Frontend configuration contracts | `node --test web/tests/*.test.mjs` | PASS: 2; static contract only |
| Actual release readiness | `scripts/release_gate.py --repo .` | BLOCKED (nonzero exit, expected) |
| All P1s independently resolved | inspect `release-readiness.json`, `01-audit.md`, DB/WS/browser evidence | FAIL: eight unverified/OPEN; one explicitly OPEN |
| Full stack end-to-end verified | check Rails DB, frontend lockfile, component tests, browser/WS logs | NOT VERIFIED / BLOCKED |
| GitHub owner created independent repo | inspect real origin/history | NO `.git`, no repo evidence; owner deferred |
| Real failed and passed PRs | require canonical GitHub PR URLs and check status | NOT AVAILABLE |
| Tag-specific CI linked to version | require annotated tag, SHA, real GitHub run URL | NOT AVAILABLE |
| Publication conditions cleared | review identifiers, legal permissions, secrets/history | NOT CLEARED |
| Application changes since Phase 7 | compare SHA-256 across `api/` and `web/` | **NO APP SOURCE CHANGES** in Phase 8 |

## Correctness of scope labels

1. `01-audit.md` is **ranked risk assessment**. Severity P1 is based on integrity/security impact; some issues were source-inferred rather than end-to-end reproduced. A future reviewer should distinguish probable implementation risk from demonstrated exploit.
2. `02-quality-system.md` begins with a historical Phase 4 status `REGRESSIONS_INTENTIONALLY_RED`, followed by later Phase 5–7 updates. The Phase 8 navigation clarifies that the **current** local regression tests are GREEN; the heading is not evidence of a still-failing suite.
3. `03-release-decision.md` correctly says `BLOCKED` and explicitly labels `v0.1.0-rc1` as **proposed, not tagged**.
4. A structured PR metadata validator prevents silent omissions **only when a trusted externally enforced workflow and branch protection exist**. The local tests do not prove mandatory remote enforcement.
5. Phase 5's seven code-fixed P1s await DB/HTTP/WS/browser checks; the eighth P1 (`FIND-011`) is OPEN pending approved admin→tenant authorization policy.
6. Test catalog of 41: 22 with *partial* local evidence, 3 with DB specs written but not run, and 16 without matching test implementation (per Phase 6 verification). Not 41/41 runtime coverage.
7. The app's real business correctness and confidentiality cannot be established from source-only analysis or a private ZIP.

## Reproduction / negative evidence

Run the commands in [`08-reviewer-start-here.md`](08-reviewer-start-here.md). For release and submission gate commands, the **expected correct state is BLOCKED**, with nonzero exit code. A reviewer should keep both local PASS and release BLOCKED outputs in view instead of merging them into an “all-green” narrative.

## Independent concerns requiring follow-up

- **Critical specification:** obtain and test explicit tenant-role membership and cross-tenant admin allowance (`FIND-011`), with two independent synthetic tenants.
- **Critical runtime:** provision Ruby 3.3.2 + matching bundle, disposable PostgreSQL, Redis/Sidekiq and a usable web build. Run server-side multi-tenant request tests, state transitions, websocket role and worker idempotency.
- **Coverage:** finish or explicitly de-scope missing regression scenarios; substantive React component/browser validation is not equivalent to API URL fallback checks.
- **Workflow:** controlled trusted PR checks should not be mutable by untrusted PRs; configure real branch rule protection and document ownership of the approval process.
- **Public source:** static identifier scan found multiple references; review permission, exact locations, hidden files, historical blobs, generated artifacts, logs and license. Do not bulk-delete source references without verifying behavior.
- **Operational handoff:** public repo owner must control clean import, real PRs, tag, approval, exact deadline and submission; none have happened locally.

## Verdict

- **Local evidence package:** reviewable (subject to runtime limitations).
- **Product release:** **DO NOT SHIP / BLOCKED**.
- **Public distribution:** **NOT CLEARED**.
- **Final submission:** **NOT READY / NOT SUBMITTED**.
- **Phase 8 status:** documentation and local preflight work can be completed; mandatory remote/publication/submission exit criteria remain blocked for owner action and missing runtime verification.
