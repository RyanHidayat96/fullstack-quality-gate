# AC-FLOW-001 — Generate candidate invite URLs using the frontend origin
- Acceptance ID: AC-FLOW-001
- Requirement: REQ-FLOW-001
- Test IDs: INVITE-01, INVITE-02, INVITE-03
- Given: isolated synthetic tenant, candidate, assessment and/or changed code with documented baseline
- When: the known defect path or engineering change is exercised in a repeatable regression test
- Then: Default local invite URL must use http://localhost:5173/interview/:token
- Negative/boundary scenario: reject invalid input or foreign ownership; preserve persisted records and do not silently claim success

Expected semantics are **provisional**, subject to product review where described in REQ-FLOW-001.
