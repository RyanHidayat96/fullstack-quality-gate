#!/usr/bin/env python3
"""Authoring aid for Phase 4 proposed, unapproved, code-derived engineering inputs.

This script does NOT establish product-owner approval. It is kept for repeatable
artifact generation; only run deliberately, never as part of PR validation.
"""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
CATALOG = json.loads((ROOT/'assessment/design/phase-3-test-catalog.json').read_text())
DECISIONS = {
 'FIND-001': ("Protect owned portfolio data across tenant boundaries", "An assessor cannot read or modify another tenant's portfolio, even by guessing its direct ID", "Reject foreign portfolio, skill override and fit-gap requests with no persisted changes", "Tenant association through session is an authoritative ownership link; role policy remains provisional"),
 'FIND-002': ("Finalize interviews only after verifiable server readiness", "An invite-token request must not finalize a pending session or fabricate all_covered completion", "Reject pending completion without changing state or enqueuing a portfolio job", "Need product decision on signed completion proof and concurrent request semantics"),
 'FIND-003': ("Do not silently drop same-name vacancy skills", "Each persisted vacancy skill must have a corresponding comparison or deliberate validation rejection", "Two rows with the same label must not silently become one comparison", "Product must decide whether to preserve distinct IDs or reject duplicates on write"),
 'FIND-004': ("Keep saved fit-gap reports consistent with vacancy revisions", "A cached report must not represent stale vacancy data as fresh after an edit", "Updating a compared vacancy invalidates or explicitly versions the prior report", "Product must choose recomputation vs versioned historical snapshot"),
 'FIND-005': ("Reject malformed AI competency-level values", "AI responses that cannot be interpreted as valid L1-L5 scores must not be persisted as valid-looking levels", "Non-numeric AI level must fail validation before creating rows", "Product decides retry/fallback behavior but must not auto-clamp invalid text"),
 'FIND-006': ("Generate candidate invite URLs using the frontend origin", "A generated invite must take the candidate to the web interview route, not the API host", "Default local invite URL must use http://localhost:5173/interview/:token", "Configure externally for staging/prod; do not assert localhost as production URL"),
 'FIND-009': ("Enforce automated quality checks on code and release changes", "A code change cannot be considered green without meaningful test execution and change-to-test traceability", "Missing changed regression test or disabled CI blocks a behavioral PR", "Metadata lint alone is not meaningful test validation; require review and real CI statuses"),
 'FIND-010': ("Require an auditable engineering Definition of Ready", "Every behavioral change carries a spec, Given/When/Then criteria, design and risk traceability", "Missing/invalid doc link or mismatch in cross references causes PR gate to fail", "Proposed approval is not stakeholder sign-off; reviewer must vet semantics"),
 'FIND-012': ("Ensure local setup instructions and ports agree", "Example URLs, README and actual service ports should not conflict", "Frontend sample connects to correct Rails port 3001 for REST and WebSocket", "Ports are local defaults only; production environment uses injected configuration"),
}
for entry in CATALOG['findings']:
    fid = entry['finding']
    if fid not in DECISIONS:
        continue
    title, rule, expected, assumption = DECISIONS[fid]
    requirement = entry['requirement']
    acceptance = entry['acceptance']
    design = 'DES-' + requirement.removeprefix('REQ-')
    tests = ', '.join(t['id'] for t in entry['tests'])
    src = entry['source']
    file = ROOT/'assessment/requirements'/f'{requirement}.md'
    file.write_text(f'''# {requirement} — {title}
- Requirement ID: {requirement}
- Status: PROPOSED
- Source: audit {fid} and source invariant in {src}
- Problem / affected actor: {title}; assessor/candidate data trust
- Expected behavior / business rule: {rule}
- In scope / out of scope: affected endpoint/worker/test; unrelated product scope excluded
- Owner: engineering reviewer and product owner for assumptions
- Unknowns / assumptions: {assumption}

These are evidence-based engineering proposals, **not externally approved product specifications**.
''')
    ac = ROOT/'assessment/criteria'/f'{acceptance}.md'
    ac.write_text(f'''# {acceptance} — {title}
- Acceptance ID: {acceptance}
- Requirement: {requirement}
- Test IDs: {tests}
- Given: isolated synthetic tenant, candidate, assessment and/or changed code with documented baseline
- When: the known defect path or engineering change is exercised in a repeatable regression test
- Then: {expected}
- Negative/boundary scenario: reject invalid input or foreign ownership; preserve persisted records and do not silently claim success

Expected semantics are **provisional**, subject to product review where described in {requirement}.
''')
    des = ROOT/'assessment/designs'/f'{design}.md'
    des.write_text(f'''# {design} — {title}
- Design ID: {design}
- Requirement: {requirement}
- Acceptance IDs: {acceptance}
- Planned test IDs: {tests}
- Affected layers: backend and frontend boundaries, persistence and delivery pipeline where applicable
- Proposed solution: add deterministic assertions on {src} and the observed failure mode; fix root cause during Phase 5
- Data migration / backwards compatibility: avoid schema changes in Phase 4; preserve existing rows and APIs until product decision
- Alternatives and trade-offs: fail-closed validation vs asynchronous recovery; choose after evaluating error handling and product decisions
- Failure handling and rollback: reject unsafe changes; keep the baseline failing test with evidence and a reversible code change
- Risks and open questions: {assumption}

Implementation and remediation are separate; a test design never demonstrates approval.
''')
print(f'Created {len(DECISIONS)} sets of proposed REQ/AC/DES inputs.')
