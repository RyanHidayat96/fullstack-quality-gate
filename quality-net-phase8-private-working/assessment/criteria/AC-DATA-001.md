# AC-DATA-001 — Keep saved fit-gap reports consistent with vacancy revisions
- Acceptance ID: AC-DATA-001
- Requirement: REQ-DATA-001
- Test IDs: FITGAP-01, FITGAP-02, FITGAP-03
- Given: isolated synthetic tenant, candidate, assessment and/or changed code with documented baseline
- When: the known defect path or engineering change is exercised in a repeatable regression test
- Then: Updating a compared vacancy invalidates or explicitly versions the prior report
- Negative/boundary scenario: reject invalid input or foreign ownership; preserve persisted records and do not silently claim success

Expected semantics are **provisional**, subject to product review where described in REQ-DATA-001.
