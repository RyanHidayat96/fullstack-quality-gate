# Current verification and release status

**Source of truth:** this page lists current GitHub evidence. All Phase 0–8 handoffs, archived logs and earlier release notes are historical, not assertions about today's `main`.

**Recommendation:** **DO NOT SHIP**. Automated CI passing proves scoped technical checks, not product acceptance, permission to publish third-party assets, or authorization for production.

## Verified change and CI evidence

| Evidence | Outcome | Actual scope |
| --- | --- | --- |
| [PR #1](https://github.com/RyanHidayat96/fullstack-quality-gate/pull/1) | Rejected | Definition-of-Ready/PR-input quality gate demo |
| [PR #2](https://github.com/RyanHidayat96/fullstack-quality-gate/pull/2) | Passed | PR-input quality gate demo; passing diff is not proof of a functional fix |
| [PR #3](https://github.com/RyanHidayat96/fullstack-quality-gate/pull/3) | Merged, checks passed | All RSpec directories and executable React render regressions |
| [PR #4](https://github.com/RyanHidayat96/fullstack-quality-gate/pull/4) | Merged, checks passed | Configuration consistency, partial vendor-name cleanup, live evidence index |
| [PR #5](https://github.com/RyanHidayat96/fullstack-quality-gate/pull/5) | Merged, checks passed | Tenant grants, login/access/WS membership checks and actual RED→GREEN |
| [PR #6](https://github.com/RyanHidayat96/fullstack-quality-gate/pull/6) | Merged, checks passed | Active application source-name cleanup plus executable regression guard |
| [PR #7](https://github.com/RyanHidayat96/fullstack-quality-gate/pull/7) | Merged, checks passed | Tenant HTTP/DB request journey and Audio WebSocket JWT authorization |
| [PR #8](https://github.com/RyanHidayat96/fullstack-quality-gate/pull/8) | Merged, checks passed | Remove unsupported public signup route consumer |
| [PR #9](https://github.com/RyanHidayat96/fullstack-quality-gate/pull/9) | Merged, checks passed | Candidate invitation expiry/revocation; [27 RSpec, 0 failures](https://github.com/RyanHidayat96/fullstack-quality-gate/actions/runs/40301673841) |
| [Tagged release v1.0.0](https://github.com/RyanHidayat96/fullstack-quality-gate/actions/runs/40277694610) | **BLOCKED** | Real tag-specific CI; predates PR #3–#9 |

## Actual RED → GREEN chain

**FIND-011:** [PR #5 RED](https://github.com/RyanHidayat96/fullstack-quality-gate/actions/runs/40295447111) ran 14 Rails examples, 4 failures, before explicit tenant memberships existed; [PR #5 GREEN](https://github.com/RyanHidayat96/fullstack-quality-gate/actions/runs/40297012832) passed subsequent mandatory checks.

**Audio WebSocket security:** [PR #7 RED](https://github.com/RyanHidayat96/fullstack-quality-gate/actions/runs/40299313986) exposed signed JWT access without membership; [PR #7 GREEN](https://github.com/RyanHidayat96/fullstack-quality-gate/actions/runs/40299543911) passed after authorization was enforced.

**Candidate invitations:** [PR #9 RED](https://github.com/RyanHidayat96/fullstack-quality-gate/actions/runs/40300922243) produced 27 Rails examples, 3 failures; [PR #9 GREEN](https://github.com/RyanHidayat96/fullstack-quality-gate/actions/runs/40301673841) passed 27 examples with zero failures and mandatory CI.

The original Phase 4 RED and Phase 5 GREEN local logs are retained as **local evidence**, not falsely represented as two historical Git commits before the repository was created.

## Open engineering and approval boundaries

- The FIND-011 policy (tenant admin membership and global-admin/SSO grant source) was conservatively implemented as default-deny, **but remains a product/security approval assumption**, not signed off.
- FIND-008's seven-day invite expiry and explicit revoke behavior also use a **provisional** policy. Existing old invitations expire on migration and may affect operational rollout.
- FIND-013 removes an unreachable signup flow rather than inventing public admin self-registration; future onboarding requirements need approval.
- Real browser-driven end-to-end interactions, actual WebSocket upgrade/streaming, concurrency/load scenarios and all 41 planned test IDs are **not fully demonstrated** by current CI.
- Branch `main` lacks verified enforced branch protection / repository rules, so passing workflow checks alone do not prevent direct push.
- The current `api/` and `web/` files have a CI guard against original organization naming. That does **not** sanitize Git history, older copied assessment evidence, or independently establish publication rights. `publication_clearance` remains false.
- No independent product owner/security signoff or production release authorization has been provided.

## Release rule

Do not change `v1.0.0` history, backdate approvals, fabricate test evidence, or turn the gate green to improve the case-study appearance. A new release candidate requires a **new tag**, passed mandatory CI, approved role/tenant and invite policies, appropriate integration tests, public-source clearance, and an accountable named release reviewer.

The submission repository may be reviewed as engineering evidence while the **product release decision remains BLOCKED / DO NOT SHIP**.
