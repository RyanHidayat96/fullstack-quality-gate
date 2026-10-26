# REQ-FLOW-002 — Define account onboarding surface
- Requirement ID: REQ-FLOW-002
- Status: PROPOSED / SECURITY-FIRST ASSUMPTION
- Source: FIND-013
- Problem / affected actor: An unused self-service signup UI and API client suggest a registration path that the backend does not support.
- Expected behavior / business rule: No public signup surface is advertised until an authorized enrollment workflow, roles and tenant membership policy are specified.
- In scope / out of scope: Remove unreachable UI and unused API method; authorized operator provisioning remains the supported development path.
- Owner: Engineering proposal pending product/security review.
- Unknowns / assumptions: Public self-signup is out of scope. Never allow unauthenticated callers to grant themselves admin privileges.

This resolves an orphan code path, not the product decision to create future self-service registration.
