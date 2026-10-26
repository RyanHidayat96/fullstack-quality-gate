# DES-DATA-001 — Keep saved fit-gap reports consistent with vacancy revisions
- Design ID: DES-DATA-001
- Requirement: REQ-DATA-001
- Acceptance IDs: AC-DATA-001
- Planned test IDs: FITGAP-01, FITGAP-02, FITGAP-03
- Affected layers: backend and frontend boundaries, persistence and delivery pipeline where applicable
- Proposed solution: add deterministic assertions on api/app/controllers/api/v1/vacancies_controller.rb and the observed failure mode; fix root cause during Phase 5
- Data migration / backwards compatibility: avoid schema changes in Phase 4; preserve existing rows and APIs until product decision
- Alternatives and trade-offs: fail-closed validation vs asynchronous recovery; choose after evaluating error handling and product decisions
- Failure handling and rollback: reject unsafe changes; keep the baseline failing test with evidence and a reversible code change
- Risks and open questions: Product must choose recomputation vs versioned historical snapshot

Implementation and remediation are separate; a test design never demonstrates approval.
