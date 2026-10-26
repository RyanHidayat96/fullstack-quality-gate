# DES-DATA-003 — Do not silently drop same-name vacancy skills
- Design ID: DES-DATA-003
- Requirement: REQ-DATA-003
- Acceptance IDs: AC-DATA-003
- Planned test IDs: FITGAP-04, FITGAP-05
- Affected layers: backend and frontend boundaries, persistence and delivery pipeline where applicable
- Proposed solution: add deterministic assertions on api/app/services/fit_gap/engine.rb and the observed failure mode; fix root cause during Phase 5
- Data migration / backwards compatibility: avoid schema changes in Phase 4; preserve existing rows and APIs until product decision
- Alternatives and trade-offs: fail-closed validation vs asynchronous recovery; choose after evaluating error handling and product decisions
- Failure handling and rollback: reject unsafe changes; keep the baseline failing test with evidence and a reversible code change
- Risks and open questions: Product must decide whether to preserve distinct IDs or reject duplicates on write

Implementation and remediation are separate; a test design never demonstrates approval.
