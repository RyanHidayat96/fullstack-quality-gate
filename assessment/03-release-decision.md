# 03 — Release decision: v1.0.0

**Decision: BLOCKED / DO NOT SHIP.**  
**Tag:** `v1.0.0` → commit `ae539d3ef07366f7a7060fc62ae69c47c25b96ea`.  
**Actual evidence:** [v1.0.0 GitHub Actions run](https://github.com/RyanHidayat96/fullstack-quality-gate/actions/runs/40277694610).

## What happened on the tagged commit

The release workflow ran on the real tag. Its technical checks succeeded, including engineering policy, Ruby regression contracts, scoped Rails/PostgreSQL specifications, frontend configuration/build checks and the aggregate quality summary. The **release-decision job deliberately failed closed** because not all P1 conditions, acceptance approvals, end-to-end scenarios and release authority were satisfied.

A passing engineering quality summary is **not** the same thing as an approved product release. No deployed production build or authorized risk acceptance is evidenced.

## Verified work after v1.0.0

The following changes are real and verified, but they **are not part of the older tag**:

| Change | Evidence |
| --- | --- |
| Expanded RSpec and React render checks | [PR #3](https://github.com/RyanHidayat96/fullstack-quality-gate/pull/3) |
| Configuration and source privacy guard | [PR #4](https://github.com/RyanHidayat96/fullstack-quality-gate/pull/4), [PR #6](https://github.com/RyanHidayat96/fullstack-quality-gate/pull/6) |
| Tenant-admin membership authorization | [PR #5](https://github.com/RyanHidayat96/fullstack-quality-gate/pull/5) |
| Tenant HTTP/DB and Audio WS auth tests | [PR #7](https://github.com/RyanHidayat96/fullstack-quality-gate/pull/7) |
| Removed unsupported self-service signup | [PR #8](https://github.com/RyanHidayat96/fullstack-quality-gate/pull/8) |
| Expiring and revocable invitation tokens | [PR #9](https://github.com/RyanHidayat96/fullstack-quality-gate/pull/9), [CI: 27 RSpec / 0 failures](https://github.com/RyanHidayat96/fullstack-quality-gate/actions/runs/40301673841) |

For current engineering and security evidence, read [01 — Audit](01-audit.md) and [02 — Quality System](02-quality-system.md). Recent PR and CI results take precedence over earlier interim local notes; the historical release tag is kept intact.

## Final submission snapshot (after historical v1.0.0 tag)

The source on current `main` includes [PR #12](https://github.com/RyanHidayat96/fullstack-quality-gate/pull/12) (real browser/WS protocol checks), [PR #13](https://github.com/RyanHidayat96/fullstack-quality-gate/pull/13) (stale fit-gap generation race), and [PR #14](https://github.com/RyanHidayat96/fullstack-quality-gate/pull/14) (AI worker failure integrity). Their changes are **not part of the `v1.0.0` tag**. The final reviewed `main` SHA before this report update was `19e7839184b8e42c40d1bbcb7833b576f1edcd62`; the [Quality Net](https://github.com/RyanHidayat96/fullstack-quality-gate/actions/runs/40323669757) and [live Chromium E2E](https://github.com/RyanHidayat96/fullstack-quality-gate/actions/runs/40323669835) succeeded for that exact SHA. Subsequent documentation commits require their own CI confirmation.

This document records a **historical tagged release decision** plus the newer untagged source evidence. A new tag must not be claimed unless its Git ref and release-gate run can be verified. An honest BLOCKED verdict is explicitly permitted by the assignment when risks remain, so it is preferable to creating an unverified green release.

## Release blockers

1. **P1 ownership and product approval.** Code-level remediation exists for FIND-011, but entitlement behavior for global admins, tenant membership provisioning and external SSO requires independent product/security approval. Other P1 coverage is not exhaustively validated under realistic concurrency or live integrations.
2. **Invitation policy.** FIND-008 now has test-backed expiry/revocation code, but the seven-day default and customer experience require product approval before rollout. Existing invitations older than that threshold are invalidated by migration.
3. **Integration and traceability.** [Live Chromium/DB/WS CI](https://github.com/RyanHidayat96/fullstack-quality-gate/actions/runs/40323669835) now passes on the current `main` code: real browser login/invitation, persisted HTTP reads, upgraded coverage socket and denial of revoked Audio WebSocket access. Streaming real AI audio is still untested. The 41-case catalog audit found **22 executable, 12 partial and 7 missing** (not a statement that all cases fully passed).
4. **Repository enforcement.** PR and push CI pass, but GitHub currently reports `main` as **unprotected** and zero active repository rulesets. Direct pushes can bypass a workflow-only PR policy. This limitation is disclosed rather than hidden.
5. **Publication and source provenance — the highest submission risk.** The public initial commit `0a0305701ea33428182cd1c34289e5529df19fa9` still contains the original case-study PDF and copies of earlier working files, although the latest tree has removed them. Git history and external copies are **not** cleared. Do not infer publication permission from a passing active-source scan; `publication_clearance=false`.
6. **Independent sign-off.** There is no named release owner approval or documented risk acceptance.

## Required decision before any new release

The responsible product/security owner must approve the entitlement and invitation policies, reviewers must verify remaining security/integration cases, repository administrators must enforce required PR checks, and publication rights must be cleared. Only then should a **new** candidate tag be pushed and evaluated by the fail-closed release workflow.

Do **not** re-tag `v1.0.0` or claim its historical CI included post-tag fixes. The current decision remains **BLOCKED / DO NOT SHIP**.
