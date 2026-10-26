# DES-SEC-003 — Enforce admin membership before token issue
- Design ID: DES-SEC-003
- Requirement: REQ-SEC-003
- Acceptance IDs: AC-SEC-003
- Planned test IDs: AUTH-TENANT-04, AUTH-TENANT-05, AUTH-TENANT-06
- Affected layers: PostgreSQL membership relation, Rails login controller, bearer-token authorizer, coverage WebSocket and regression requests
- Proposed solution: Add unique user-to-organization grants; look up the authorized membership before signing or accepting any tenant-scoped admin token
- Data migration / backwards compatibility: No automatic backfill; explicitly enroll existing admins before deployment
- Alternatives and trade-offs: Deny by default for existing users until provisioned rather than retaining a cross-tenant authorization hole
- Failure handling and rollback: Reject invalid role, missing membership and tenant mismatch; keep release blocked without product review
- Risks and open questions: External SSO grants and global operations access are not defined and must be approved separately

This is a conservative engineering assumption for assessment, not evidence of business signoff.
