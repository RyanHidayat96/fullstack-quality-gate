# DES-FLOW-001 — Generate candidate invite URLs using the frontend origin
- Design ID: DES-FLOW-001
- Requirement: REQ-FLOW-001
- Acceptance IDs: AC-FLOW-001
- Planned test IDs: INVITE-01, INVITE-02, INVITE-03
- Affected layers: backend and frontend boundaries, persistence and delivery pipeline where applicable
- Proposed solution: add deterministic assertions on api/app/models/session.rb and the observed failure mode; fix root cause during Phase 5
- Data migration / backwards compatibility: avoid schema changes in Phase 4; preserve existing rows and APIs until product decision
- Alternatives and trade-offs: fail-closed validation vs asynchronous recovery; choose after evaluating error handling and product decisions
- Failure handling and rollback: reject unsafe changes; keep the baseline failing test with evidence and a reversible code change
- Risks and open questions: Configure externally for staging/prod; do not assert localhost as production URL

Implementation and remediation are separate; a test design never demonstrates approval.
