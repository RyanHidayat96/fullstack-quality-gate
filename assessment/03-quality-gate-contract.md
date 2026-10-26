# Phase 3 — Engineering Quality Gate Contract (implementation specification)

> **State:** DRAFT DESIGN, not operational. Validates source-supported structure, not unverified product acceptance. The independent repository and branch protection are deferred.  
> **Related:** `03-quality-architecture.md`, `03-traceability.md`, `design/phase-3-test-catalog.json`, `01-audit.md`.

## 1. Document contract, in-repo only

For every code-changing PR, references are **repository-relative markdown paths** within the PR HEAD (not external URLs). Accepted roots are:

- `assessment/requirements/REQ-<identifier>.md`
- `assessment/criteria/AC-<identifier>.md`
- `assessment/designs/DES-<identifier>.md`

Examples (illustrative only; do not claim these files exist):

```text
Spec: assessment/requirements/REQ-tenant-isolation.md
Acceptance: assessment/criteria/AC-tenant-isolation.md
Design: assessment/designs/DES-tenant-isolation.md
Findings: FIND-001
Tests: AUTH-TENANT-01, AUTH-TENANT-02, AUTH-TENANT-03
Risk: high
Scope: api/app/controllers/api/v1/portfolios_controller.rb, api/spec/requests/tenant_access_spec.rb
```

Machine checks should reject missing fields, empty placeholders (`TODO`, `TBD`, `n/a`, `-`, `none`), invalid roots/extensions, duplicate/conflicting entries, whitespace-only paths, glob paths, absolute paths, external URLs and any file not present in checked-out PR HEAD. Resolve paths with `Path.resolve()` and assert they remain below checkout root, no symlink escapes. Limit file size and count to prevent abuse, parse UTF-8 robustly, never evaluate or execute document contents. Require changed PR tests/inputs to be referenced consistently; do not trust a checkbox alone.

### Minimum requirements template

```md
# REQ-001 — <neutral requirement title>
- Requirement ID: REQ-001
- Status: PROPOSED | APPROVED | UNKNOWN
- Source: <code invariant or approved human artifact; NOT blank>
- Problem / affected actor: ...
- Expected behavior / business rule: ...
- In scope / out of scope: ...
- Owner (role only unless real named individual authorized): ...
- Unknowns / assumptions: ...
```

`Status: PROPOSED` is accepted as a *linked, reviewable input* for the candidate exercise only if the associated PR explicitly marks assumptions and human reviewer approves it. It is **not** treated as external product sign-off. A separate release decision retains policy uncertainty.

### Minimum acceptance-criteria template

```md
# AC-001 — <neutral behavior>
- Acceptance ID: AC-001
- Requirement: REQ-001
- Test IDs: AUTH-TENANT-01
- Given: a signed-in assessor for synthetic tenant B
- When: the assessor requests a portfolio from synthetic tenant A
- Then: the API rejects without returning cross-tenant data and no stored row changes
- Negative/boundary scenario: same tenant still works; denial does not reveal existence
```

High-risk changes must include a deny/invalid/edge scenario and persisted-state outcome, not only UI text or HTTP 200. Acceptance IDs must be unique among linked files. Verify that at least one test ID maps to catalog / traceability. A short acceptance file containing only a heading or checkbox is invalid.

### Minimum design template

```md
# DES-001 — <neutral change design>
- Design ID: DES-001
- Requirement: REQ-001
- Acceptance IDs: AC-001
- Planned test IDs: AUTH-TENANT-01
- Affected layers: API / database / frontend / queue / workflow
- Proposed solution: ...
- Data migration / backwards compatibility: ...
- Alternatives and trade-offs: ...
- Failure handling and rollback: ...
- Risks and open questions: ...
```

The validator ensures the three docs' identifiers/cross-links agree and the paths exist; reviewers assess semantic quality. Reject unrelated dummy artifacts used just to turn checks green.

## 2. PR template contract

Suggested fixed sections/fields:

```md
## Change summary
<problem and behavioral scope>

## Linked engineering inputs
Spec: assessment/requirements/REQ-...md
Acceptance: assessment/criteria/AC-...md
Design: assessment/designs/DES-...md

## Traceability
Findings: FIND-...
Tests: TEST-ID-..., ...
Risk: high | medium | low
Affected paths: api/..., web/...

## Evidence
- Negative case / previous RED: <path or link; or reason not yet available>
- Test command: <exact command>
- Expected saved/API/UI effect: ...
- Limitations / known risks: ...

## Non-behavioral test exemption (if applicable)
Exemption: none | DOCS_ONLY | COMMENT_ONLY | FORMATTING_ONLY
Justification: <why no code behavior can change>
```

A PR is **not merge-ready** while actual tests are RED; evidence of intentional RED before a fix is for investigation/history, not a bypass. `Exemption` is only legitimate if the computed diff is entirely within a strict non-behavioral class (documentation or whitespace/comments confirmed by reviewer). Any production-file change with unclear semantics requires tests. For docs-only changes the spec/AC/design inputs can be skipped if policy explicitly allows, but any changed docs still must have meaningful content validation. For CI validator or other workflow changes, run validator's own negative+positive fixture tests and code-owner review; no self-exemption.

## 3. Fail-closed validation algorithm

```text
read event.json (only pull_request events; reject unexpected type)
read PR body as untrusted text, changed paths from git diff merge-base against trusted base
classify affected paths; reject ambiguous or dangerous file types
if no code-impact paths:
    validate modified documents; enforce documented docs-only policy
else:
    parse exactly one of each Spec/Acceptance/Design/Tests/Risk fields
    canonicalize all paths; require proper allowed directory and existing HEAD file
    parse document structural IDs, nonempty required sections and cross-references
    ensure finding IDs exist in audited catalog (when a finding is claimed)
    ensure each named test ID exists in catalog and is linked by AC and design
    require changed or newly created executable test(s) matching affected behavior
    forbid unreviewed exemption and mismatched high-risk category
    evaluate independent CI jobs (not merely mark checkbox complete)
report machine-readable validation errors with paths (no sensitive content)
exit 1 on ANY failure; exit 0 only on fully valid structure/links
```

### Threat/negative-case table

| Scenario / ID | Expected result | Why |
|---|---|---|
| DOR-01 | FAIL | `Spec` missing or nonexistent. |
| DOR-02 | FAIL | `Acceptance` missing, blank, inconsistent with `REQ`. |
| DOR-03 | FAIL | `Design` missing, no risk/solution or inconsistent IDs. |
| DOR-04 | PASS on **metadata validator only** | Valid links + IDs + test mapping + content; CI tests may still legitimately RED. |
| TEST-GATE-01 | FAIL | Behavior code changed but no real linked test artifact. |
| TEST-GATE-02 | FAIL | Test file present but missing or trivial assertions; review needed for semantic quality. |
| TEST-GATE-03 | FAIL | `../`, absolute/external/symlink path, or `TODO` placeholder link. |
| TEST-GATE-04 | FAIL | CI workflow / validator self-change without fixture checks and required human review. |
| TEST-GATE-05 | PASS (subject to review) | Truly docs-only, valid edited docs and correctly scoped exemption policy. |
| TEST-GATE-06 | FAIL | CI skip, empty test discovery, `continue-on-error`, or intentionally missing required job. |
| RELEASE-GATE-01 | FAIL | Tag points to commit with required job failure or unknown/skipped result. |
| RELEASE-GATE-02 | FAIL | All checks pass but unresolved P0/P1 lacks explicit real owner and approved risk acceptance. |
| RELEASE-GATE-03 | PASS only if real | Correct tag SHA, required checks pass and risk sign-off policy satisfied. |

### Limits to the machine gate

A script cannot prove a test is useful solely by finding `expect(` or `assert` text. It **must** run tests to prove discovery/execution, check coverage of named regression IDs, and rely on review for whether assertions are meaningful. Avoid pretending a regex check prevents intentionally vacuous tests. In Phase 4 implement unit tests for the validator itself and check both invalid and valid fixtures. Keep branch protection separate; do not claim a YAML file alone prevents merging.

## 4. Required checks, status names and dependencies

- `pr-inputs`: structured DoR/DoD validator; only for PR events.
- `api-critical`: RSpec request, model, service, worker and WebSocket focused regression suite with isolated Postgres; blocks on any failure.
- `web-quality`: typecheck, production build and meaningful frontend component checks; blocks on any failure.
- `quality-summary`: required aggregate; blocks when a required job failed or did not execute on an eligible event.
- `release-quality-summary`: exact `v*` tag, same actual quality net, outstanding-risk check, human-readable BLOCKED/RELEASABLE result.

Use stable check names for branch protection; verify exact names in real GitHub UI after repository creation. GitHub Actions permission recommendation: read-only except the minimum explicitly justified permissions to post check/report; PR code must never receive privileged credentials. Do not install or require third-party services for core tests.

**Branch restrictions after independent repo exists (user-managed):** ruleset protecting `main`, required `quality-summary` plus relevant jobs, force-push prevention, PR reviews as feasible. If available on the account, require review of workflow/validator edits; GitHub environment/plan limitations are recorded as `BLOCKED` rather than bypassed.

## 5. Handling known risk vs green build

`assessment/01-audit.md` currently shows eight OPEN P1 findings. A green build cannot overrule them. The release gate has an independent reviewed risk register with finding IDs/status; invalid or missing risk statuses block. Only `FIXED` supported by red→green evidence, or **exceptionally** documented accepted risk with real owner + mitigation + approval, clears release-specific P1 criteria. Do not invent approvers or silently downgrade P1 severity to pass release.

**Implementation handoff:** Phase 4 adds actual files, tests and execution evidence. Before Phase 4, every case in this document is a specification / expected outcome, not a functioning gate.
