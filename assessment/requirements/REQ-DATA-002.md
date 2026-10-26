# REQ-DATA-002 — Reject malformed AI competency-level values
- Requirement ID: REQ-DATA-002
- Status: PROPOSED
- Source: audit FIND-005 and source invariant in api/app/services/portfolios/generator.rb
- Problem / affected actor: Reject malformed AI competency-level values; assessor/candidate data trust
- Expected behavior / business rule: AI responses that cannot be interpreted as valid L1-L5 scores must not be persisted as valid-looking levels
- In scope / out of scope: affected endpoint/worker/test; unrelated product scope excluded
- Owner: engineering reviewer and product owner for assumptions
- Unknowns / assumptions: Product decides retry/fallback behavior but must not auto-clamp invalid text

These are evidence-based engineering proposals, **not externally approved product specifications**.
