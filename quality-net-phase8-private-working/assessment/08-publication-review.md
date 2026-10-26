# Publication, Provenance and Confidentiality Review — PRIVATE

**Decision: DO NOT UPLOAD PUBLICLY.** This snapshot includes original code and documentation obtained for a technical assessment. The existence of a readable source repository or a requirement for a public submission does **not** itself establish rights to redistribute every file or disclose embedded names or third-party/client information.

## Confirmed in the current private archive

- The previous Phase 6 static string scan flagged **45 identifier-bearing file paths** (see `assessment/evidence/phase-6/publication-readiness.json`). This is not a count of secrets or a copyright determination. The Phase 8 private scan should be consulted for the current count.
- Identifiers are spread across source code, migrations, database schema, infrastructure manifests, README/docs and UI text. Some also appear in filenames/paths and URLs, not only in prose.
- Earlier pattern scanning did not detect PEM private-key blocks or obvious non-placeholder credential assignments, but this **does not certify secret-free source**. Test values and samples still require review.
- The working copy has no `.git` history; scanning historical commits and remotes is therefore impossible here.
- `RELEASE_NOTES.md` is a candidate document only, not a permission to publish or release.
- The original product-specification link in root README points back to the upstream organization; that link and any copied public citations must be reviewed prior to publication.

## Mandatory safe handling before creating the public candidate repo

1. Obtain written or otherwise verifiable permission and licensing terms for publication of the *entire* source package, including infrastructure, database schema, and documentation. Clarify what use the case study's public-copy instruction authorizes.
2. Privately identify restricted names, domains, tenants, customer identifiers, logos, real candidate data, API tokens, credentials, chat/email content, and embedded screenshots. Review each occurrence with authorized owner context.
3. Sanitize with **surgical edits**. Do not blindly rename DB schema namespaces, Rails classes, cookie prefixes, deploy selectors, JWT identifiers, routes, or environment variables; those changes can break functionality. Record and test every required replacement.
4. Keep case brief, private assessments, identity/reference manifests and sensitive scan outputs out of any public copy if they disclose prohibited company/product/client identity.
5. Use a secret scanner on vetted filesystem and new Git history; inspect staged contents before *every* push. Never publish `.env`, Rails secrets, service accounts, real API keys, recordings, or test fixtures based on real people.
6. Run meaningful Ruby/Rails/DB/web integration checks **after** sanitization. A renamed reference can invalidate a migration or serializer while static tests stay green.
7. Only then create the owner's clean independent public repository and configure the required PR and CI policies.

## Evidence hierarchy

- **Verified:** the ZIP includes source-derived name strings and there is no local Git history; project settings contain integration-sensitive identifiers.
- **Provisional:** a narrow pattern scan found no obvious private key markers; not a full credential audit.
- **Unverified:** legal redistribution permission, API credential validity, third-party licensing, historical Git-object safety, impact of sanitization on runtime.

**Owner action required:** approve publication scope and record clearance only after steps above are complete. For now `assessment/submission-evidence.json` deliberately has `publication_clearance=false`.
