# Phase 0 — Pre-Publication Security & Confidentiality Review

**Status:** REVIEWED (automated source text screening), **NOT CLEARED FOR PUBLICATION**  
**Date:** 2026-10-22 (Asia/Jakarta)  
**Source:** user-supplied extracted GitHub working-copy ZIP. Source code remains unchanged.

## Scope & evidence

- Exactly **188 files** from ZIP, **55 directory entries**. All paths passed basic zip-slip, duplicate-entry, and symlink checks.
- No `.git/` metadata and no non-sample `.env` or application secrets configuration files in the supplied tree.
- Examined all readable UTF-8 files for common hardcoded token shapes, private-key delimiters, email addresses, secret-related assignments, and organization/product identity markers. This **does not** replace a dedicated secret scanner or manual content review.
- Original ZIP SHA256: `88da860d806be3c256495f3816ccb5f25f2720bc12a0c0f84951bd8337de1e46`. Individual original file hashes: `assessment/PHASE_0_FILE_INVENTORY.json`.

## Scan results (do not interpret zeros as proof of safety)

| Rule | Matching lines | Distinct files | Interpretation |
|---|---:|---:|---|
| Upstream company/product identity markers | 122 | 40 | **Publication blocker:** the brief prohibits identifying the organization/product/client in public candidate work. Many matches are functional identifiers. |
| Secret-key/password/token assignment vocabulary | 10 | 7 | Requires contextual review; generally config samples, auth handling, and seed instructions. |
| Common token shape signatures | 0 | 0 | No signatures matched; other formats may exist. |
| Private key block delimiters | 0 | 0 | No literal private-key PEM blocks matched. |
| Email address shapes | 0 | 0 | No email-address shaped strings detected. |

### Upstream-identity occurrences requiring review

This table lists paths and line numbers only; no upstream values or credential values are reproduced.

| Source path | Matching lines | Sample line numbers |
|---|---:|---|
| `README.md` | 1 | 2 |
| `api/.irbrc` | 1 | 9 |
| `api/Dockerfile` | 3 | 11, 29, 32 |
| `api/README.md` | 3 | 22, 81, 97 |
| `api/app/auth/authorize_api_request.rb` | 4 | 5, 6, 10, 11 |
| `api/app/controllers/application_controller.rb` | 1 | 9 |
| `api/app/controllers/concerns/exception_handler.rb` | 3 | 3, 7, 13 |
| `api/app/controllers/concerns/response.rb` | 1 | 3 |
| `api/app/lib/json_web_token.rb` | 2 | 3, 4 |
| `api/app/lib/message.rb` | 1 | 3 |
| `api/app/middlewares/application_middleware.rb` | 1 | 3 |
| `api/app/middlewares/auth_token_middleware.rb` | 1 | 3 |
| `api/app/middlewares/tenant_resolver_middleware.rb` | 3 | 3, 7, 12 |
| `api/app/models/concerns/tenant_scoped.rb` | 1 | 4 |
| `api/app/models/current.rb` | 2 | 3, 40 |
| `api/app/models/organization.rb` | 3 | 3, 4, 11 |
| `api/config/application.yml.sample` | 5 | 4, 7, 10, 14, 23 |
| `api/config/database.yml` | 5 | 1, 3, 15, 19, 23 |
| `api/db/migrate/20240101000000_create_ai_interview_schema.rb` | 25 | 3, 8, 10, 11, 19, 23, 28, 32, 36, 40, 44, 62 … |
| `api/db/migrate/20260320000000_create_skill_taxonomies.rb` | 1 | 5 |
| `api/db/migrate/20260320000001_create_ai_interview_users.rb` | 2 | 5, 14 |
| `api/db/schema.rb` | 1 | 185 |
| `api/db/seeds.rb` | 5 | 14, 18, 19, 22, 30 |
| `api/k8s/configmap.yaml` | 2 | 4, 20 |
| `api/k8s/deploy-sidekiq.yaml` | 12 | 4, 13, 22, 36, 42, 50, 57, 58, 65, 88, 97, 109 |
| `api/k8s/deployment.yaml` | 11 | 1, 10, 11, 15, 24, 33, 45, 52, 61, 62, 73 |
| `api/k8s/ingress.yml` | 3 | 15, 23, 30 |
| `api/k8s/nodepool.yaml` | 4 | 4, 5, 27, 28 |
| `api/k8s/service.yaml` | 2 | 4, 9 |
| `web/README.md` | 1 | 28 |
| `web/index.html` | 1 | 7 |
| `web/package.json` | 1 | 2 |
| `web/src/components/layout/AssessorLayout.tsx` | 1 | 35 |
| `web/src/components/layout/CandidateLayout.tsx` | 1 | 9 |
| `web/src/index.css` | 2 | 16, 20 |
| `web/src/pages/auth/LoginPage.tsx` | 1 | 40 |
| `web/src/pages/auth/SignupPage.tsx` | 1 | 42 |
| `web/src/pages/interview/InterviewPage.tsx` | 2 | 195, 252 |
| `web/src/pages/transcript/TranscriptPage.tsx` | 1 | 106 |
| `web/vercel.json` | 1 | 14 |

## Review findings & mitigations

1. **PUBLISH-BLOCK-01 — Upstream identifiers in source content.** Risk: publishing the original code unchanged may violate the case brief, even under a neutral repo name. Identity references are also embedded into SQL schema naming, JWT auth coordination, application metadata, Docker/Kubernetes resources, and other functional areas. **Do not bulk replace** identifiers until dependency impacts are mapped, migration compatibility is addressed, and the app can be rerun. Owner: candidate/publication reviewer. Status: OPEN.
2. **PUBLISH-BLOCK-02 — No verified full-content dedicated secret scan.** No obvious common token shapes or private-key blocks were found in preliminary checks. This is **not a safety certification**. Before the first public push, review sample configuration, seeds, docs, deployment manifests, and any generated binaries with a reputable scanner; check for internal endpoints and confidential material. Owner: candidate/publication reviewer. Status: OPEN.
3. **PUBLISH-BLOCK-03 — Remote public repository and clean-history import intentionally deferred.** Candidate will create the independent public repository later. No remote is configured and no git commit/push has been attempted. Owner: candidate. Status: DEFERRED BY USER.
4. **Environment/sample-only configurations.** Template files include placeholder credentials, and a development auth-token environment variable is blank. A preliminary check did not find committed production secret files. Do not place real tokens inside tracked files.
5. **Potential scope conflict.** The case study explicitly requires working in a public copy but forbids naming the company/product/client within it. A safe release strategy must reconcile functional in-code identifiers and the policy **before** publication. This cannot be resolved solely by renaming the repository.

## Exit decision

**NOT SAFE TO PUSH TO PUBLIC GITHUB AS-IS.** Preserve the source working copy privately, carry these findings into the pre-publication checklist, and confirm no sensitive material or identifying disclosures remain before the candidate imports and pushes a new clean-history repo.
