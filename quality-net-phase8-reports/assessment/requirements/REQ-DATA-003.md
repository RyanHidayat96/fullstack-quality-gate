# REQ-DATA-003 — Do not silently drop same-name vacancy skills
- Requirement ID: REQ-DATA-003
- Status: PROPOSED
- Source: audit FIND-003 and source invariant in api/app/services/fit_gap/engine.rb
- Problem / affected actor: Do not silently drop same-name vacancy skills; assessor/candidate data trust
- Expected behavior / business rule: Each persisted vacancy skill must have a corresponding comparison or deliberate validation rejection
- In scope / out of scope: affected endpoint/worker/test; unrelated product scope excluded
- Owner: engineering reviewer and product owner for assumptions
- Unknowns / assumptions: Product must decide whether to preserve distinct IDs or reject duplicates on write

These are evidence-based engineering proposals, **not externally approved product specifications**.
