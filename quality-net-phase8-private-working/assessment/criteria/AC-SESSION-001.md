# AC-SESSION-001 — Finalize interviews only after verifiable server readiness
- Acceptance ID: AC-SESSION-001
- Requirement: REQ-SESSION-001
- Test IDs: SESSION-01, SESSION-02, SESSION-03, SESSION-04
- Given: isolated synthetic tenant, candidate, assessment and/or changed code with documented baseline
- When: the known defect path or engineering change is exercised in a repeatable regression test
- Then: Reject pending completion without changing state or enqueuing a portfolio job
- Negative/boundary scenario: reject invalid input or foreign ownership; preserve persisted records and do not silently claim success

Expected semantics are **provisional**, subject to product review where described in REQ-SESSION-001.
