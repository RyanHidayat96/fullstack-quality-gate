# REQ-AUTH-001 — Tenant membership policy

- Requirement ID: REQ-AUTH-001
- Status: PROPOSED
- Source: FIND-011
- Problem / affected actor: Tenant selection during authentication must not grant access to unrelated tenant data.
- Expected behavior / business rule: Validate an explicit user-to-tenant membership before issuing a tenant-scoped token.
- In scope / out of scope: Login and membership validation; external identity providers remain out of scope.
- Owner: Engineering implementation; product approval pending.
- Unknowns / assumptions: Accounts have tenant-specific access; unknown memberships are rejected. No global privileges are inferred.

Product approval is still required before a production release.
