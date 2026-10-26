# Live Defense Preparation — Evidence-Led Technical Discussion

> This preparation document is for a 60–90 minute conversation. Speak to **what was actually verified**, not what the pipeline ought to have done in an uncreated repository. Do not present hypothetical demonstrations as remote evidence.

## Suggested 75-minute walkthrough

| Time | Segment | Evidence to open |
|---|---|---|
| 0–5 min | Executive summary, goal and current `DO NOT SHIP` decision | [`08-reviewer-start-here.md`](08-reviewer-start-here.md); [`03-release-decision.md`](03-release-decision.md) |
| 5–20 min | Show ranked risks and observed-vs-unknown separation | [`01-audit.md`](01-audit.md); Phase 2 source probes |
| 20–35 min | Walk through one data-integrity defect, unit RED → fix → GREEN | Phase 4/5 evidence and corresponding Ruby services |
| 35–50 min | Show PR DoR/DoD validator, CI fail-closed path, adversarial coverage | [`02-quality-system.md`](02-quality-system.md); quality workflow and policy tests |
| 50–60 min | Release gate, P1 register, accepted-vs-unverified risk | [`03-release-decision.md`](03-release-decision.md); release readiness JSON |
| 60–75 min | Remaining gaps, product-policy questions, AI verification, next-sprint plan | [`06-traceability-verification.md`](06-traceability-verification.md); [`08-independent-review.md`](08-independent-review.md) |

For a 60-minute meeting shorten the demo; for 90 minutes allocate more time to question-driven investigation.

## Ten questions from the brief and defensible answer outlines

### 1. Why the top three risks?

**Tenant boundary** (`FIND-001`, `FIND-011`): assessment and candidate information may be incorrectly accessible across tenants if ownership/membership checks are absent. **Session completion** (`FIND-002`): an incomplete session can lead to a prematurely generated portfolio. **Data integrity** (`FIND-003`/`FIND-005`): skill comparisons silently lose records, or malformed AI outputs are coerced to plausible scores. These outrank cosmetic issues because they alter authorization and authoritative stored outcomes. The observed proof is source/method-level; actual cross-tenant exploitation remains unverified.

### 2. What was unspecified vs implemented incorrectly?

`FIND-011` is chiefly **SPEC_MISSING / policy unresolved**: which user/role can select which tenant? Duplicate-skill semantics under `FIND-003` also need a product contract: reject duplicate labels versus preserve distinct IDs. Clearly incorrect source behavior relative to known data invariants includes coercing an invalid AI score into L1/L5 (`FIND-005`) and a backend-origin invitation URL (`FIND-006`). Proposed REQ/AC files are not product sign-off.

### 3. Trace one UI → API → persistence defect.

Use `FIND-003` as an explainable example: assessor configures multiple required skill rows; vacancy API/model persists those rows; the fit-gap service previously converted vacancy skills into a hash keyed by `skill_label` and could lose one when labels matched; the computed comparison subsequently displayed fewer requirements. Phase 2 executed the actual service method with doubles and observed two inputs collapse into one; Phase 5 preserved distinct IDs and introduced regression assertions. **The full browser→API→PostgreSQL journey was not executed** and must not be described as proven.

### 4. Why these test layers?

- Python policy unit tests guard metadata parsing, changed-file enumeration, fake input paths and tampering.
- Ruby method-level contracts efficiently capture failure semantics before Rails starts.
- RSpec request/service/model tests were drafted for actual data/tenant persistence and concurrency checks but have **not** run.
- Node static tests protect frontend API/WS configuration only, not DOM behavior.
- Browser-level end-to-end journeys remain a high-priority missing layer. 41 planned scenarios were reconciled: 22 partial local, 3 authored-but-not-executed Rails, 16 without matching test implementation.

### 5. How do DoR and DoD gates work beyond checkboxes?

Changes must link an existing spec, acceptance criteria and design, declare affected paths and associated executable tests. Local policy checks compare real changed files against declarations, reject missing/unrelated test IDs, path traversal, missing documents and suspicious policy edits. Workflow intends to use validator code from the trusted PR base SHA. **Limit:** structural validity does not guarantee substantive acceptance criteria, reviewer approval, or real enforcement until GitHub branch rules are enabled.

### 6. Show blocked and passing PR evidence.

**No actual GitHub PRs exist.** Demonstrate local synthetic PR fixtures only, clearly named simulations. An owner-created independent GitHub repository, real blocked PR, real passing PR, and preserved CI URLs/SHA are still required. Do not suggest screenshots or invented PR numbers as substitutes.

### 7. Show RED → GREEN and why the fix is causal.

Open `assessment/evidence/phase-4/source-regressions-red.log` (five failing assertions before changes), Phase 5 `ruby-after-green.log` (12 runs, 40 assertions PASS), and `original-assertion-preservation.json`. Explain root-cause changes: stable skill IDs, raw input validation before persistence, server-owned readiness/state transition, tenant scoping and correct invite origin. Phase 6 mutation probes demonstrated four deliberately reintroduced defects make assertions fail; they are **isolated**, not transaction/HTTP proofs.

### 8. Why was release blocked and who owns residual risks?

There are eight P1 findings: seven code-fixed pending integration, one still OPEN (`FIND-011`). Rails/DB/Redis, build/browser test evidence, product sign-off, two real PRs, tagged CI and publication clearance are missing. `assessment/03-release-decision.md` therefore states **DO NOT SHIP**. No real risk owner or approver has accepted these deficiencies; ownership must be assigned by the future project/release sponsor, not invented here.

### 9. How was AI used responsibly?

AI-assisted code/document drafting is permitted by the brief. Verification is demonstrated by read-only source inspection, preserved RED logs, local unit/mutation checks, repeated validation and explicit failure to claim unrun integration coverage. A Phase 6 mutation exposed a faulty test double that caused a misleading failure; the fixture was corrected and mutation verification repeated. Do not claim that a named AI tool produced or corrected a particular change without contemporaneous evidence.

### 10. What changes in the next sprint?

First obtain approved tenant membership and ownership policy, then implement/review `FIND-011`. Provision disposable PostgreSQL/Redis and supported Ruby; execute DB/WS/async concurrency tests. Build web deterministically using a reviewed lockfile, add component tests and one browser→API→DB path. After confidentiality clearance, create clean independent Git history, configure protected checks, demonstrate real failing/passing PRs, then tag and gate an actual release. No skip of P1 or test weakening to force a green badge.

## Honest phrases during discussion

- “That result is reproduced at method level; the HTTP/database integration remains an explicitly blocked item.”
- “Those requirements are proposed, not yet product-approved; I would block the related release decision.”
- “The automated validator enforces traceable inputs, but human review is still required for semantic correctness.”
- “I cannot show real GitHub PR/CI links yet; the controlled GitHub import belongs to the repository owner.”
- “A blocked release with evidence is safer than misrepresenting an unverified version as production-ready.”

## Demonstration discipline

Only open recorded evidence and rerun local checks when dependencies are present. Never expose real candidate data, secrets, production account cookies or credentials during screen share. Do not run migration/seed commands against any shared database. Keep logs from synthetic fixtures separate from live-environment verification.
