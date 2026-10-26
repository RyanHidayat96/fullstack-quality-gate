# DES-DOC-001 — Ensure local setup instructions and ports agree
- Design ID: DES-DOC-001
- Requirement: REQ-DOC-001
- Acceptance IDs: AC-DOC-001
- Planned test IDs: DOC-01
- Affected layers: backend and frontend boundaries, persistence and delivery pipeline where applicable
- Proposed solution: add deterministic assertions on api/README.md and the observed failure mode; fix root cause during Phase 5
- Data migration / backwards compatibility: avoid schema changes in Phase 4; preserve existing rows and APIs until product decision
- Alternatives and trade-offs: fail-closed validation vs asynchronous recovery; choose after evaluating error handling and product decisions
- Failure handling and rollback: reject unsafe changes; keep the baseline failing test with evidence and a reversible code change
- Risks and open questions: Ports are local defaults only; production environment uses injected configuration

Implementation and remediation are separate; a test design never demonstrates approval.
