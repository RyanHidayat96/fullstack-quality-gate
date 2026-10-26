# AC-DOC-001 — Ensure local setup instructions and ports agree
- Acceptance ID: AC-DOC-001
- Requirement: REQ-DOC-001
- Test IDs: DOC-01
- Given: isolated synthetic tenant, candidate, assessment and/or changed code with documented baseline
- When: the known defect path or engineering change is exercised in a repeatable regression test
- Then: Frontend sample connects to correct Rails port 3001 for REST and WebSocket
- Negative/boundary scenario: reject invalid input or foreign ownership; preserve persisted records and do not silently claim success

Expected semantics are **provisional**, subject to product review where described in REQ-DOC-001.
