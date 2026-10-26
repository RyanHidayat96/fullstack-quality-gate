# AC-AUTH-001 — Authenticate within approved tenant scope

- Acceptance ID: AC-AUTH-001
- Requirement: REQ-AUTH-001
- Test IDs: AUTH-TENANT-04, AUTH-TENANT-05, AUTH-TENANT-06
- Given: Two synthetic organizations and an admin registered with one organization.
- When: The admin requests a login token for an organization.
- Then: Token issuance succeeds only for the organization with a recorded membership.
- Negative/boundary scenario: Unknown organizations, ambiguous memberships and unenrolled admins receive no scoped token.
