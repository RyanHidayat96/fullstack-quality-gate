# REQ-SESSION-001 — Finalize interviews only after verifiable server readiness
- Requirement ID: REQ-SESSION-001
- Status: PROPOSED
- Source: audit FIND-002 and source invariant in api/app/controllers/api/v1/sessions_controller.rb
- Problem / affected actor: Finalize interviews only after verifiable server readiness; assessor/candidate data trust
- Expected behavior / business rule: An invite-token request must not finalize a pending session or fabricate all_covered completion
- In scope / out of scope: affected endpoint/worker/test; unrelated product scope excluded
- Owner: engineering reviewer and product owner for assumptions
- Unknowns / assumptions: Need product decision on signed completion proof and concurrent request semantics

These are evidence-based engineering proposals, **not externally approved product specifications**.
