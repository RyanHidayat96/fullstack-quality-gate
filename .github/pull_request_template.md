## Change summary
Describe the user-facing problem, expected behavior and deliberate non-goals.

## Linked engineering inputs
Spec: assessment/requirements/REQ-QUALITY-001.md
Acceptance: assessment/criteria/AC-QUALITY-001.md
Design: assessment/designs/DES-QUALITY-001.md

## Traceability
Findings: FIND-009
Tests: TEST-GATE-01
Risk: high
Affected paths: scripts/validate_pr_inputs.py, scripts/test_validate_pr_inputs.py

## Evidence
- Previous RED / negative result (path, commit, CI job):
- Exact test command and exit code:
- Saved data and API/UI impact (where applicable):
- Limitations / unresolved decisions:

## Non-behavioral test exemption (docs-only only)
Exemption: none
Justification: Test coverage applies to every behavior-changing PR.

> Replace ALL example values with accurate repo-relative paths and test IDs. For
> DOCS_ONLY PRs, supply `Exemption: DOCS_ONLY` and an actual justification.
> A passing metadata validator is not an approval, green regression suite, or
> proof that requirements have product-owner sign-off.
