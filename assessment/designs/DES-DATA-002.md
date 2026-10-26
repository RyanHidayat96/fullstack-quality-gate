# DES-DATA-002 — Reject malformed AI competency-level values
- Design ID: DES-DATA-002
- Requirement: REQ-DATA-002
- Acceptance IDs: AC-DATA-002
- Planned test IDs: PORTFOLIO-01, PORTFOLIO-02, PORTFOLIO-03
- Affected layers: backend and frontend boundaries, persistence and delivery pipeline where applicable
- Proposed solution: add deterministic assertions on api/app/services/portfolios/generator.rb and the observed failure mode; fix root cause during Phase 5
- Data migration / backwards compatibility: avoid schema changes in Phase 4; preserve existing rows and APIs until product decision
- Alternatives and trade-offs: fail-closed validation vs asynchronous recovery; choose after evaluating error handling and product decisions
- Failure handling and rollback: reject unsafe changes; keep the baseline failing test with evidence and a reversible code change
- Risks and open questions: Product decides retry/fallback behavior but must not auto-clamp invalid text

Implementation and remediation are separate; a test design never demonstrates approval.
