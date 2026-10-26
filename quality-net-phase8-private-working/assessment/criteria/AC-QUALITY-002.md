# AC-QUALITY-002 — Require an auditable engineering Definition of Ready
- Acceptance ID: AC-QUALITY-002
- Requirement: REQ-QUALITY-002
- Test IDs: DOR-01, DOR-02, DOR-03, DOR-04, TEST-GATE-03, TEST-GATE-05
- Given: isolated synthetic tenant, candidate, assessment and/or changed code with documented baseline
- When: the known defect path or engineering change is exercised in a repeatable regression test
- Then: Missing/invalid doc link or mismatch in cross references causes PR gate to fail
- Negative/boundary scenario: reject invalid input or foreign ownership; preserve persisted records and do not silently claim success

Expected semantics are **provisional**, subject to product review where described in REQ-QUALITY-002.
