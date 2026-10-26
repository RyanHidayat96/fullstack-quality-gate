# REQ-FLOW-001 — Generate candidate invite URLs using the frontend origin
- Requirement ID: REQ-FLOW-001
- Status: PROPOSED
- Source: audit FIND-006 and source invariant in api/app/models/session.rb
- Problem / affected actor: Generate candidate invite URLs using the frontend origin; assessor/candidate data trust
- Expected behavior / business rule: A generated invite must take the candidate to the web interview route, not the API host
- In scope / out of scope: affected endpoint/worker/test; unrelated product scope excluded
- Owner: engineering reviewer and product owner for assumptions
- Unknowns / assumptions: Configure externally for staging/prod; do not assert localhost as production URL

These are evidence-based engineering proposals, **not externally approved product specifications**.
