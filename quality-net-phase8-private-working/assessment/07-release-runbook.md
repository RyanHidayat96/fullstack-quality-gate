# Phase 7 Release Gate — Execution Runbook (owner-controlled operations)

**Status as authored:** design and offline checks only; `BLOCKED`. This runbook is not authorization to publish.

## Local checks (safe and repeatable)

```bash
python3 -m unittest discover -s scripts -p 'test_*.py' -v
ruby api/spec/regression/critical_contract_test.rb
node --test web/tests/*.test.mjs
python3 scripts/release_gate.py --repo . --output assessment/evidence/phase-7/local-verdict.json
```

`release_gate.py` is expected to exit `1` in a local ZIP without GitHub tag/CI environment variables. Its JSON `BLOCKED` verdict is the **correct** result. Supply no invented GitHub statuses.

The workflow is triggered by pushes to refs/tags matching `v*`; the release job checks that the tag is bound to the actual workflow SHA. On the tag, it requires green CI policy, Ruby contracts, Rails test service, frontend quality and summary, plus reviewed P1 and verification evidence. It fails nonzero on blockers. The exact tag SHA and run URL must come from the remote service itself, not a local mock.

## Before any public repository (owner action; deferred)

1. Review/sanitize organization and product names in **all** files, including original README, config, fixtures, documentation, script comments and Git history. Refuse public upload until confidentiality, permissions and licensing are approved. Re-run all tests after **any** controlled modifications.
2. Create an **empty** independent repository in the owner's account. Avoid Fork (case brief). Use a neutral quality-engineering name; do not name any source organization, company, product or client.
3. Initialize clean history only with owner-approved files. Do **not** commit secrets, `.env`, tokens, production credentials, real candidate data, or inherited `.git` metadata.
4. Configure required status checks and owner approval of workflow/policy changes. A PR validator stored in the same repository is insufficient if a PR can bypass its own required checks via edited workflow YAML or disabled branch rules.
5. Demonstrate two **real** PRs: one missing required inputs/test and **BLOCKED**, one fully specified and actually **PASSED**. Record URLs, SHA and CI outcomes, not screenshots alone.
6. Set up test-only PostgreSQL/Redis, Ruby 3.3.2/Rails bundle, deterministic fixtures, frontend lockfile, component and browser tests. Execute all DB/HTTP/WS/e2e checks and attach results to the readiness ledger. Full build and runtime parity are mandatory.
7. Obtain product rules and implement the remaining tenant membership P1. Verify all eight P1 dispositions with evidence; reconcile both the audit index and `release-readiness.json`. An unresolved P1 blocks unless there is explicit and reviewable acceptance with real named owner, mitigation, expiry/review time, and proof.
8. Record approval for publication and acceptance criteria. Update the release ledger **only after evidence exists and is reviewed**.

## Annotated tag / remote tag CI (not yet run)

Only after approval and inspecting `git status`, `git log -1 --oneline`, configured `origin`, branch protection and exact commit:

```bash
# Do not execute before the owner authorizes the release attempt.
git status --porcelain
# Confirm clean tree and exact hash reviewed by owner:
git rev-parse HEAD
# Confirm proposed tag does not already exist:
git show-ref --tags --verify --quiet refs/tags/v0.1.0-rc1 && echo 'Already exists; STOP'
# If fully approved, owner manually runs:
# git tag -a v0.1.0-rc1 -m 'Candidate release for gated verification'
# git push origin refs/tags/v0.1.0-rc1
# Then record remote run URL and check release-decision status.
```

The script/workflow will normally report **BLOCKED** given the current readiness state. No local tag or remote release is included in the Phase 7 package; the owner explicitly deferred independent repository creation.

## Required final evidence

- Exact annotated tag and resolved commit SHA (`git rev-parse refs/tags/v0.1.0-rc1^{commit}`).
- GitHub Actions tag-specific run URL, run ID, all mandatory checks, and uploaded `release-verdict.json`.
- Two real PR URLs with red/green statuses, traceability and review.
- All P1 states and approvals independently audited; database and browser test artifacts.
- Final reviewer signoff on the release decision, with mitigation and real owner if any accepted risk remains.

Never claim `RELEASABLE` based on a local simulated CI success or an unverified JSON field.
