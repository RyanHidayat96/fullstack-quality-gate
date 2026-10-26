# REQ-SEC-004 — Expiring and revocable candidate invitations
- Requirement ID: REQ-SEC-004
- Status: PROPOSED / SECURITY-FAIL-CLOSED
- Source: FIND-008, candidate invitation tokens have no defined expiry or revocation.
- Problem / affected actor: Anyone retaining a candidate invitation can continue using it indefinitely unless the session ends.
- Expected behavior / business rule: Tokens expire after a configurable bounded lifetime (default 7 days). An authorized assessor can revoke an invitation. Expired or revoked tokens must not access candidate HTTP endpoints or audio connections.
- In scope / out of scope: Token-based candidate read, completion, WebSocket authentication, revocation, persistence and automated checks. Existing JWT expiration and external identity providers are unaffected.
- Owner: Engineering proposal pending product/security approval.
- Unknowns / assumptions: Seven-day lifetime is provisional; product may require a different invitation schedule. Existing tokens older than seven days are invalidated on migration rather than silently grandfathered.
