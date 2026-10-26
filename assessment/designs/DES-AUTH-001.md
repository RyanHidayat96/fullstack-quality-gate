# DES-AUTH-001 — Tenant-scoped authentication

- Design ID: DES-AUTH-001
- Requirement: REQ-AUTH-001
- Acceptance IDs: AC-AUTH-001
- Planned test IDs: AUTH-TENANT-04, AUTH-TENANT-05, AUTH-TENANT-06
- Affected layers: API authentication, membership records, database schema and request tests.
- Proposed solution: Store unique user-to-tenant memberships and validate a selected tenant against them before signing a scoped token.
- Data migration / backwards compatibility: Do not grant all existing admins universal membership; enroll users explicitly.
- Alternatives and trade-offs: A global-admin bypass may be needed, but is not approved and is unsafe as a default.
- Failure handling and rollback: Reject access if membership cannot be established and keep release blocked until policy is reviewed.
- Risks and open questions: Product owner must approve enrollment and external SSO mapping.
