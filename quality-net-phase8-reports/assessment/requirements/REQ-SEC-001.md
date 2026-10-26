# REQ-SEC-001 — Protect owned portfolio data across tenant boundaries
- Requirement ID: REQ-SEC-001
- Status: PROPOSED
- Source: audit FIND-001 and source invariant in api/app/controllers/api/v1/portfolios_controller.rb
- Problem / affected actor: Protect owned portfolio data across tenant boundaries; assessor/candidate data trust
- Expected behavior / business rule: An assessor cannot read or modify another tenant's portfolio, even by guessing its direct ID
- In scope / out of scope: affected endpoint/worker/test; unrelated product scope excluded
- Owner: engineering reviewer and product owner for assumptions
- Unknowns / assumptions: Tenant association through session is an authoritative ownership link; role policy remains provisional

These are evidence-based engineering proposals, **not externally approved product specifications**.
