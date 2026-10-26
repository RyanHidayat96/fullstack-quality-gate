# AC-FLOW-002 — No unsupported public signup
- Acceptance ID: AC-FLOW-002
- Requirement: REQ-FLOW-002
- Test IDs: SIGNUP-01
- Given: The current web application routes and API client.
- When: Frontend regression tests inspect available authentication actions.
- Then: The application has a working login route, but no orphan SignupPage import, public signup route, or unavailable signup client method.
- Negative/boundary scenario: Future public registration must be introduced with backend authorization, role assignment and tenant membership tests.
