# AC-DATA-002 — Reject malformed AI competency-level values
- Acceptance ID: AC-DATA-002
- Requirement: REQ-DATA-002
- Test IDs: PORTFOLIO-01, PORTFOLIO-02, PORTFOLIO-03
- Given: isolated synthetic tenant, candidate, assessment and/or changed code with documented baseline
- When: the known defect path or engineering change is exercised in a repeatable regression test
- Then: Non-numeric AI level must fail validation before creating rows
- Negative/boundary scenario: reject invalid input or foreign ownership; preserve persisted records and do not silently claim success

Expected semantics are **provisional**, subject to product review where described in REQ-DATA-002.
