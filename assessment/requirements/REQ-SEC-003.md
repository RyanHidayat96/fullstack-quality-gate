# REQ-SEC-003 — Tenant-bound admin login
- Requirement ID: REQ-SEC-003
- Status: PROPOSED / SECURITY-FAIL-CLOSED
- Source: FIND-011, existing login path accepts tenant selection without membership verification
- Problem / affected actor: A signed-in admin must not choose an unrelated tenant.
- Expected behavior / business rule: Issue a tenant-scoped session only when there is an explicit membership for that user and organization.
- In scope / out of scope: Local admin login and JWT request authorization; externally managed SSO and global-admin roles require independent specification.
- Owner: Engineering for default-deny proposal; product/security decision pending
- Unknowns / assumptions: No universal admin access exists without a separate explicit policy. An account with one membership can log in without selecting a tenant.

Provision access explicitly; never silently grant old accounts all tenants.
