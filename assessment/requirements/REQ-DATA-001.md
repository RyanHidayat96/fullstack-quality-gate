# REQ-DATA-001 — Keep saved fit-gap reports consistent with vacancy revisions
- Requirement ID: REQ-DATA-001
- Status: PROPOSED
- Source: audit FIND-004 and source invariant in api/app/controllers/api/v1/vacancies_controller.rb
- Problem / affected actor: Keep saved fit-gap reports consistent with vacancy revisions; assessor/candidate data trust
- Expected behavior / business rule: A cached report must not represent stale vacancy data as fresh after an edit
- In scope / out of scope: affected endpoint/worker/test; unrelated product scope excluded
- Owner: engineering reviewer and product owner for assumptions
- Unknowns / assumptions: Product must choose recomputation vs versioned historical snapshot

These are evidence-based engineering proposals, **not externally approved product specifications**.
