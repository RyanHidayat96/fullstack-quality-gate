# AC-SEC-003 — Validate tenant selection
- Acceptance ID: AC-SEC-003
- Requirement: REQ-SEC-003
- Test IDs: AUTH-TENANT-04, AUTH-TENANT-05, AUTH-TENANT-06
- Given: Synthetic admin and two organizations with distinct recorded memberships
- When: The admin signs in with a selected tenant or no tenant selection
- Then: Only explicitly authorized tenant tokens are issued; a unique membership is automatically selected when none was specified
- Negative/boundary scenario: Reject unknown, unrelated or ambiguous tenant selection without issuing a signed token

The globally privileged admin behavior remains out of scope until approved by a product owner.
