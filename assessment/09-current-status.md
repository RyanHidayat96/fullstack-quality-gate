# Current verification status

This page is the current index for repository evidence. Phase handoff notes and their saved logs describe **historical snapshots** and should not be read as live CI status.

## Evidence available on GitHub

| Check | Verified observation | Limitation |
| --- | --- | --- |
| PR gate negative case | [PR #1](https://github.com/RyanHidayat96/fullstack-quality-gate/pull/1) rejected missing inputs | Demonstrates one type of rejection |
| PR gate positive case | [PR #2](https://github.com/RyanHidayat96/fullstack-quality-gate/pull/2) passed required checks | Metadata check does not replace review |
| Expanded CI coverage | [PR #3](https://github.com/RyanHidayat96/fullstack-quality-gate/pull/3) ran 10 Rails examples and 9 Node tests successfully | Does not prove browser-to-database or actual WebSocket connections |
| Tagged release | [v1.0.0 tag workflow](https://github.com/RyanHidayat96/fullstack-quality-gate/actions/runs/40277694610) ran checks and **blocked** deployment | Tag identifies an older commit; later changes are not part of v1.0.0 |
| RED to GREEN | Saved Phase 4 RED / Phase 5 GREEN source-regression logs | Initial import already included the fixed code; not a GitHub-native two-commit reproduction |

## Verified updates after the first reviewer tour

- [PR #4](https://github.com/RyanHidayat96/fullstack-quality-gate/pull/4): CI-validated sample configuration and evidence updates, merged.
- [PR #5](https://github.com/RyanHidayat96/fullstack-quality-gate/pull/5): reproduced a tenant-authorization defect on a test-only commit ([RED run](https://github.com/RyanHidayat96/fullstack-quality-gate/actions/runs/40295447111), 14 RSpec / 4 failures), then enforced persisted tenant grants, token re-validation and coverage subscription checks ([GREEN run](https://github.com/RyanHidayat96/fullstack-quality-gate/actions/runs/40297012832), all mandatory jobs passed); merged.
- FIND-011: **code remediation and Rails/PostgreSQL regression evidence now exist**, but the fail-closed cross-tenant-admin policy is still a **provisional engineering rule**, not approved production entitlement semantics.
- This branch adds a source-identifier regression check and removes references from active application files. It **does not rewrite past commits** or establish legal permission to publish proprietary material.

## Remaining blockers

- FIND-011: code-level checks for tenant memberships exist and passed CI, but externally approved role/SSO policy is still missing; production release remains blocked.
- Other code-level P1 fixes require expanded negative-path API and persisted-data checks before release clearance.
- Real browser-to-API-to-database journeys and actual WebSocket connection tests have not been demonstrated.
- The public repository currently has legacy identifiers in source/configuration and **historical Git objects**. Cleaning a working tree cannot remove old commits or previously uploaded assessment materials.
- Branch `main` has not been confirmed to enforce required checks at repository-rule level. Workflow success alone does not prevent direct pushes.
- Original Phase 0–8 documents were drafted before real GitHub runs and can contain dated environment observations. Use this page plus the linked live runs for current claims.

## Decision

**Product release: BLOCKED / DO NOT SHIP.** No independent reviewer approved residual P1 risks or accepted production responsibility. Keep release approval distinct from whether a candidate's engineering work is ready for assessment. Never change a blocked release to green merely to improve the submission presentation.

The technical improvements in `fix/release-hardening` are proposed until their PR checks pass and they are merged.
