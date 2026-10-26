# AC-SEC-001 — Protect owned portfolio data across tenant boundaries
- Acceptance ID: AC-SEC-001
- Requirement: REQ-SEC-001
- Test IDs: AUTH-TENANT-01, AUTH-TENANT-02, AUTH-TENANT-03
- Given: isolated synthetic tenant, candidate, assessment and/or changed code with documented baseline
- When: the known defect path or engineering change is exercised in a repeatable regression test
- Then: Reject foreign portfolio, skill override and fit-gap requests with no persisted changes
- Negative/boundary scenario: reject invalid input or foreign ownership; preserve persisted records and do not silently claim success

Expected semantics are **provisional**, subject to product review where described in REQ-SEC-001.
