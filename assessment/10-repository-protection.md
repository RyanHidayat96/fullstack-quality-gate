# Repository protection and history risk register

This document distinguishes **implemented CI** from **server-enforced repository policy**. It must not be presented as proof that GitHub branch protection is active.

## Currently verified

- The repository's `main` branch was reported as `protected: false` by GitHub during the review.
- No active GitHub repository ruleset was returned in the same review.
- GitHub Actions does execute policy, API/PostgreSQL, Ruby contracts, frontend checks and `quality-summary` when a pull request is opened.
- The implementation uses a **trusted base commit** for PR policy evaluation. This does not prevent a privileged direct push that bypasses PR review.

## Required repository administrator configuration

Using repository **Settings → Rules → Rulesets** (or Branches → Branch protection), create an active rule matching the default branch `main`:

- Require a pull request before merge; disallow direct pushes for ordinary contributors.
- Require GitHub Actions status check **quality-summary** and the critical checks **pr-inputs**, **policy-unit**, **api-contract**, **api-critical**, and **web-quality** on the exact proposed commit.
- Require the branch to be up to date before merge; reject failed, missing, or skipped critical checks.
- Require resolved conversations and at least one independent reviewer for security-sensitive changes when an authorized reviewer is available.
- Prevent force pushes and branch deletion, and document any organization administrator bypass.
- Confirm the ruleset is **Active**, check it matches `main`, then exercise a small disposable PR to prove direct-push and failed-check enforcement.

A CI badge or passing PR alone is insufficient evidence. Preserve a screenshot or exported ruleset configuration and a rejected direct-push/failed-check demonstration.

## Publication and history cleanup

Removing names from `api/` and `web/` **does not** remove names and files in existing Git commits, PR refs, tags, forks, CI artifacts, cached copies, or externally downloaded versions.

- Obtain the source owner's redistribution permission and determine which source files/branding or assessment materials are allowed in a public submission.
- Privately inventory current-tree and historical restricted identifiers, binary/PDF attachments, URLs and credentials; never publish the raw sensitive findings.
- If a **history rewrite** is authorized, use an audited local Git cleanup tool, validate all rewritten references, and coordinate collaborator clones and protected tags. A force push can invalidate PR/tag evidence and cannot retract previously downloaded data.
- Rotate any real secret that was exposed. A string-scan alone is not credential clearance.
- Do not declare `publication_clearance=true` until historical and current assets, repository permissions and external licenses are independently verified.

## Open work and release state

The GitHub integration available to this engineering workflow can edit source, open PRs, and merge PRs, but has no supported operation to create/update repository rulesets. This page is a runbook, **not an applied settings change**.

**Branch enforcement: NOT VERIFIED. Publication/history clearance: NOT VERIFIED. Product release: BLOCKED.**
