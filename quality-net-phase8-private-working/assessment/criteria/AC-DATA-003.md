# AC-DATA-003 — Do not silently drop same-name vacancy skills
- Acceptance ID: AC-DATA-003
- Requirement: REQ-DATA-003
- Test IDs: FITGAP-04, FITGAP-05
- Given: isolated synthetic tenant, candidate, assessment and/or changed code with documented baseline
- When: the known defect path or engineering change is exercised in a repeatable regression test
- Then: Two rows with the same label must not silently become one comparison
- Negative/boundary scenario: reject invalid input or foreign ownership; preserve persisted records and do not silently claim success

Expected semantics are **provisional**, subject to product review where described in REQ-DATA-003.
