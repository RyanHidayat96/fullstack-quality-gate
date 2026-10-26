# Phase 0 — Repository Intake & Environment Inventory

**Date:** 2026-10-22 (WIB)  
**Status:** PARTIAL COMPLETE; independent GitHub publication intentionally deferred by candidate.

## Purpose and completed scope

This report documents **Phase 0 only** of the supplied master execution plan. The original source archive has been inspected and extracted into a private working directory. **No architecture baseline test, end-to-end test, implementation audit, bug fix, release tag, or CI workflow execution was performed.** These are future phases.

## Source acquisition and provenance

- Source obtained from the user as an uploaded GitHub working-copy ZIP, not cloned through the runtime terminal.
- Archive SHA256: `88da860d806be3c256495f3816ccb5f25f2720bc12a0c0f84951bd8337de1e46`.
- Extraction verification: 188 files / 55 directories; no duplicate paths, traversal paths, or symlinks.
- No embedded `.git` metadata (expected for an exported archive). No original remote or branch can be inferred from the ZIP itself.
- GitHub source repository was readable through the GitHub connector earlier in the session. The remote recursive main tree contained **188 blobs and 55 tree entries** with tree SHA `b836d02f45c6300b238b98ad50e66ead706723b6`.
- **Line ending caveat:** 187 of 188 source files contain CRLF (Windows-style line endings). Normalizing CRLF → LF reproduced GitHub's exact blob SHA for four verified reference files: root `README.md`, `api/README.md`, `api/Gemfile`, and `api/.ruby-version`. **This is a spot-check, not verification that all 188 remote files are byte-identical.** The normalized full-tree hash did not match the referenced remote tree SHA, so complete provenance equivalence remains unverified and should not be claimed.

## Verified source layout and technology

| Area | Verified from files | Notes |
|---|---|---|
| Root | README, `.gitignore`, `api/`, `web/` | Two services in one source tree |
| Backend runtime | Ruby 3.3.2 requested in `.ruby-version`; Rails 7.0.10 locked | Local Ruby 3.3.8 differs from requested patch |
| Backend infrastructure | PostgreSQL, Redis, Sidekiq | DB migrations, schema and Kubernetes manifests included |
| Backend testing dependencies | `rspec-rails`, FactoryBot, Faker, DatabaseCleaner, Timecop | Dependency declarations do not constitute tests |
| Frontend runtime | React 18, TypeScript, Vite 6.4.2, npm | React Router, Axios, Jotai, RHF, Zod, Tailwind |
| Frontend lockfile | No `web/package-lock.json` or yarn/pnpm lockfile in supplied tree | Reproducibility gap; prioritize after Phase 0 |
| Tracked tests | No conventional `spec/`, `test/`, or `*.test.*` source files | Not proof of zero informal/manual testing |
| CI | No `.github/workflows/` files in supplied tree | No configured GitHub Actions found |
| Documents | Root and API/web READMEs, sample env | Root README points to additional wiki context |
| Auth/integration prerequisites | JWT secret compatibility, separate platform schema, Gemini integration | Safe local substitutions or mocks may be needed after code inspection |

## Runtime prerequisites documented by source

- Ruby 3.3.2 with Bundler and Rails toolchain; PostgreSQL with isolated development/test database.
- Redis with Sidekiq worker; Node.js + npm for web.
- Local environment vars for Rails, database, Redis, origins, and external Gemini API. Never store real keys in the public repo.
- API documented at `http://localhost:3001`; web at `http://localhost:5173`. The web env sample uses port 3000, which conflicts with the documented 3001; classify as **CONFIG-DOC INCONSISTENCY / UNTESTED**, not a reproduced product bug.
- Backend README includes a frontend directory-navigation example that refers to a different folder name than the actual monorepo. Use the root `web/` path instead, to be verified when running the project in Phase 1.

## Available local tools at Phase 0

| Tool | Observed | Impact |
|---|---|---|
| Git | 2.47.3 | Available for later clean-history import |
| Node | 22.16.0 | Available |
| npm | 10.9.2 | Available |
| Ruby | 3.3.8 | Installed, project expects 3.3.2 |
| Bundler (`bundle`) | Not found | Rails cannot be fully bootstrapped in this environment yet |
| Docker | Not found | Containers unavailable |
| PostgreSQL `psql` | Not found | DB client unavailable |
| Redis server | Not found | Job/cache prerequisite unavailable |

**Runtime was not attempted** because that belongs to Phase 1, and source-only verification does not prove startability.

## Compliance and release policy

- The candidate explicitly requested **not** to create the public GitHub repository yet and will handle that step later.
- Do not initialize a remote, push, create PRs, tag, or publish anything unless the candidate explicitly resumes those tasks.
- The working copy is **private preparation only, not sanitized for public release**. See `assessment/PHASE_0_SECURITY_REVIEW.md`.
- Exact case-study deadline remains unknown; the provided brief says the hiring platform is authoritative.

## Delivery-to-phase map

| Required submission | Planned phase |
|---|---|
| Source intake / independent clean history | 0 (remote deferred) |
| Architecture / executable baseline | 1 |
| Ranked evidence-backed audit `01-audit.md` | 2 |
| Test strategy, DoR/DoD gating design | 3 |
| Machine enforced gates, blocked/passing PR | 4 |
| P0/P1 fixes + verified red to green | 5 |
| Full regression hardening | 6 |
| Release tag, notes, decision `03-release-decision.md` | 7 |
| Submission & live defense preparation | 8 |

## Phase 0 exit gate

**PARTIAL / BLOCKED BY USER-OWNED REMOTE TASKS.** Source archive received, checked and inventoried; environment and publication risks recorded. The original Phase 0 PASS criteria still require an independently created and sanitized repo with verified new history/remote and publication safety. Those conditions cannot be met until the user chooses to carry out the deferred GitHub work. No false PASS is claimed.

**Boundary:** Do not begin Phase 1 without the user's explicit command.
