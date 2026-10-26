# AC-SEC-004 — Candidate invitation lifecycle
- Acceptance ID: AC-SEC-004
- Requirement: REQ-SEC-004
- Test IDs: INVITE-04
- Given: An invitation belonging to a synthetic tenant and candidate.
- When: A valid, expired, or revoked invitation is used.
- Then: Valid pending invitations allow candidate metadata; expired and revoked invitations are rejected by candidate HTTP, audio completion, and audio WebSocket authentication.
- Negative/boundary scenario: Unauthorized assessors cannot revoke foreign invitations; the issuer can revoke its own invitation and no plaintext token is exposed by the revocation response.
- Data integrity: Expiry is persisted; revocation is idempotent.
