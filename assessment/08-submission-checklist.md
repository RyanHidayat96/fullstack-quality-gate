# Final Submission Checklist — OWNER CONTROLLED, NOT YET SUBMITTED

**Current verdict:** `BLOCKED / NOT SUBMISSION READY` (2026-10-22 Asia/Jakarta). The repository owner expressly deferred independent repo creation; no GitHub repository/tag/PR or hiring-platform submission is claimed. The actual platform deadline has not been supplied or verified. Do not assume the brief's multi-day estimate is the deadline.

## A. Deliverables and reviewability

- [x] `assessment/01-audit.md` contains 13 severity-ranked findings and updated dispositions.
- [x] `assessment/02-quality-system.md` documents quality checks and a *local* RED→GREEN story.
- [x] `assessment/03-release-decision.md` records current `BLOCKED` decision and P1 register.
- [x] `RELEASE_NOTES.md` describes a **proposed** candidate, not a tagged/published version.
- [x] Local PR policy and source regressions have saved command logs.
- [x] Reviewer map and live-defense outline prepared for current evidence scope.
- [ ] Product-facing acceptance criteria / tenant authorization policy approved by a real product owner.
- [ ] Every P1 genuinely fixed and verified in realistic integration/DB tests, or explicitly accepted by named independent approver with mitigation.
- [ ] All required integration, frontend component/build and browser-to-DB checks have real passing evidence.
- [ ] 41 planned scenarios reconciled to actual executable, evidence-backed coverage; deficiencies explicitly dispositioned.
- [ ] Root setup instructions independently proven in a fresh machine/environment.

## B. Confidentiality and clean-history import (owner only)

- [ ] Obtain/confirm permission and license to publish every included source file, migration, fixture, and infrastructure manifest.
- [ ] Inspect and remove/replace all prohibited organization/product/client identifiers **in a controlled, reviewed manner**. Do not break DB namespaces, environment variables, API routes or authentication via blind global replacements.
- [ ] Scan tracked/untracked content and future commit history for actual secrets, tokens, personal data and credentials. Include screenshots/logs/PR content and hidden files; never copy confidential assessment brief into public repo.
- [ ] Run complete tests **after** sanitization; ensure output still fulfills the expected business scope.
- [ ] Create empty **public** repo with neutral name, independently owned, **not a GitHub Fork**.
- [ ] Initialize fresh `.git` history from vetted files, verify clean `main`, inspect `git log`, `git remote -v`, `git status`, and confirm `origin` only points to owner's repo. Never push before prior checks are done.

## C. Required real PR / CI proof

- [ ] Enable branch protection / required checks and restrict ability to edit or bypass workflows without trusted review.
- [ ] Open and retain a **real blocked PR** with missing required spec/AC/test; record exact URL, head SHA, check run and blocking status.
- [ ] Open and retain a **real passing PR** with required spec/AC/design, relevant changed tests and independently reviewed result; record exact URL, head SHA, check run and green status.
- [ ] Confirm untrusted PR changes cannot weaken the gate (independent branch rule protection and reviewer ownership; local checks alone are insufficient).
- [ ] Verify intended fixes and RED→GREEN progression in immutable Git commits and remote CI logs, not just unversioned local ZIP evidence.

## D. Release proof and decision

- [ ] Reconcile `assessment/release-readiness.json` with **real** evidence and approvals. Never change states solely to obtain green.
- [ ] Inspect intended HEAD/release notes, record SHA, confirm policy owner authorization and exact tag name.
- [ ] Create/push an **annotated tag** from approved commit (do not reuse a proposed label if already occupied).
- [ ] Capture **actual tag-specific GitHub Actions URL**, SHA, mandatory job statuses and released/blocked verdict. A blocked release can be honestly demonstrated; do not describe it as releasable.
- [ ] Update `assessment/03-release-decision.md` with actual tag, statuses, risk owner, mitigation/approval or continued BLOCK. If still P1 OPEN, prefer BLOCK.
- [ ] Recheck all repository-relative and external links; ensure no placeholders/pseudo run references remain.

## E. Hiring platform handoff (owner only)

- [ ] Verify actual deadline and timezone in hiring portal before final submission.
- [ ] Review repo in a private browsing session as an independent evaluator without account invitations.
- [ ] Confirm first five minutes of reviewer journey via `assessment/08-reviewer-start-here.md`.
- [ ] Copy the **actual public repo URL** into the hiring platform and submit before the platform deadline; retain platform confirmation.
- [ ] Populate `assessment/submission-evidence.json` **only with observed external identifiers**, and rerun local `scripts/submission_preflight.py`. Store any sensitive confirmation privately if platform terms require it.

## Owner-controlled sequence (do not automate submission)

1. Resolve confidentiality/licensing and no-sensitive-data checks **before any public GitHub push**.
2. Obtain missing product/tenant policy and executable test environment; finish P1/integration validation.
3. Create public independent repo with reviewed source and clean history; enable branch checks and preserve two real PR demonstrations.
4. Obtain release approval, create tag, preserve tag-bound verdict, update release decision.
5. Check portal deadline and manually submit repository URL.

**Current owner-provided external proof:** NONE. `assessment/submission-evidence.json` intentionally contains null/false values; not an invitation to fabricate entries.
