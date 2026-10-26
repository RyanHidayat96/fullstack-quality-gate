# DES-SEC-001 — Protect owned portfolio data across tenant boundaries
- Design ID: DES-SEC-001
- Requirement: REQ-SEC-001
- Acceptance IDs: AC-SEC-001
- Planned test IDs: AUTH-TENANT-01, AUTH-TENANT-02, AUTH-TENANT-03
- Affected layers: backend and frontend boundaries, persistence and delivery pipeline where applicable
- Proposed solution: add deterministic assertions on api/app/controllers/api/v1/portfolios_controller.rb and the observed failure mode; fix root cause during Phase 5
- Data migration / backwards compatibility: avoid schema changes in Phase 4; preserve existing rows and APIs until product decision
- Alternatives and trade-offs: fail-closed validation vs asynchronous recovery; choose after evaluating error handling and product decisions
- Failure handling and rollback: reject unsafe changes; keep the baseline failing test with evidence and a reversible code change
- Risks and open questions: Tenant association through session is an authoritative ownership link; role policy remains provisional

Implementation and remediation are separate; a test design never demonstrates approval.
