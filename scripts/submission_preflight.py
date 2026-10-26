#!/usr/bin/env python3
"""Read-only, fail-closed submission evidence preflight.

Checks reproducible artifacts and *external evidence references*. Does not create
repos, PRs, tags, approvals or submissions and does not confer publication clearance.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from urllib.parse import urlparse

REQUIRED = (
    'README.md', 'RELEASE_NOTES.md', '.github/workflows/quality.yml',
    'assessment/01-audit.md', 'assessment/02-quality-system.md',
    'assessment/03-release-decision.md', 'assessment/EXECUTION_LOG.md',
    'assessment/08-reviewer-start-here.md', 'assessment/08-live-defense.md',
    'assessment/08-submission-checklist.md',
)
REMOTE_FIELDS = ('public_independent_repo', 'blocked_pr', 'passing_pr', 'tag_commit',
                 'tag_ci_run', 'hiring_platform_submission')
MANDATORY_PROOFS = ('api_db_integration', 'frontend_build', 'component_regression',
                    'browser_api_db_journey', 'traceability_complete',
                    'spec_acceptance_approved', 'publication_clearance',
                    'two_real_pr_demonstrations', 'release_approval')


def _git(root: Path, *args: str) -> str | None:
    try:
        p = subprocess.run(['git', '-C', str(root), *args], text=True,
                           capture_output=True, timeout=10, check=False)
        return p.stdout.strip() if p.returncode == 0 else None
    except (FileNotFoundError, OSError, subprocess.TimeoutExpired):
        return None


def _github_html_url(value: object, path_kind: str) -> bool:
    if not isinstance(value, str) or not value or 'example' in value.lower():
        return False
    parsed = urlparse(value)
    if parsed.scheme != 'https' or parsed.hostname != 'github.com':
        return False
    parts = [p for p in parsed.path.split('/') if p]
    if len(parts) < 2:
        return False
    if path_kind == 'repo':
        return len(parts) == 2
    if path_kind == 'pr':
        return len(parts) == 4 and parts[2] == 'pulls' and parts[3].isdigit() or (
            len(parts) == 4 and parts[2] == 'pull' and parts[3].isdigit())
    if path_kind == 'run':
        return len(parts) >= 5 and parts[2:4] == ['actions', 'runs'] and parts[4].isdigit()
    return False


def _local_md_links(root: Path) -> list[dict[str, str]]:
    """Only explicit Markdown relative links; not code samples or plain paths."""
    bad = []
    md_link = re.compile(r'(?<!!)\[[^\]]+\]\((<?[^\s)]+>?)(?:\s+"[^"]+")?\)')
    for doc in root.rglob('*.md'):
        if any(p in {'node_modules', '.git', '__pycache__', 'docs'} for p in doc.parts):
            continue
        raw = doc.read_text(encoding='utf-8', errors='replace')
        outside_fence = re.sub(r'(?ms)^```[^\n]*\n.*?^```[^\n]*$', '', raw)
        for match in md_link.finditer(outside_fence):
            target = match.group(1).strip('<>').split('#', 1)[0]
            if not target or target.startswith(('https://', 'http://', 'mailto:', '#')):
                continue
            if target.startswith('/'):
                bad.append({'file': doc.relative_to(root).as_posix(), 'target': target,
                            'reason': 'absolute local link'})
                continue
            resolved = (doc.parent / target).resolve()
            if not resolved.is_relative_to(root.resolve()) or not resolved.exists():
                bad.append({'file': doc.relative_to(root).as_posix(), 'target': target,
                            'reason': 'outside checkout or target missing'})
    return bad


def run_preflight(root: Path, manifest: Path) -> dict:
    root = root.resolve()
    missing_files = [f for f in REQUIRED if not (root / f).is_file()]
    links = _local_md_links(root)
    try:
        supplied = json.loads(manifest.read_text(encoding='utf-8'))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        supplied = {}
    try:
        ledger = json.loads((root / 'assessment/release-readiness.json').read_text())
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        ledger = {}
    p1 = [f for f in ledger.get('p1_findings', []) if f.get('state') not in
          ('VERIFIED_FIXED', 'RISK_ACCEPTED_APPROVED')]
    verifications = ledger.get('mandatory_verifications', {})
    unverified = {k: verifications.get(k, {}).get('status', 'MISSING') for k in MANDATORY_PROOFS
                  if verifications.get(k, {}).get('status') != 'VERIFIED'}

    repo = supplied.get('public_independent_repo', {}) or {}
    blocked = supplied.get('blocked_pr', {}) or {}
    passed = supplied.get('passing_pr', {}) or {}
    tag = supplied.get('tag_commit', {}) or {}
    run = supplied.get('tag_ci_run', {}) or {}
    submission = supplied.get('hiring_platform_submission', {}) or {}
    git_sha = _git(root, 'rev-parse', 'HEAD')
    tag_name = tag.get('name')
    local_tag_sha = _git(root, 'rev-parse', f'refs/tags/{tag_name}^{{commit}}') if tag_name else None

    checks = {
        'required_documents': not missing_files,
        'markdown_links_local': not links,
        'independent_public_repo_verified': bool(_github_html_url(repo.get('url'), 'repo')
              and repo.get('independent_not_fork') is True and repo.get('owner_verified') is True
              and git_sha and _git(root, 'remote', 'get-url', 'origin')),
        'blocked_pr_remote_verified': bool(_github_html_url(blocked.get('url'), 'pr')
              and blocked.get('blocked_ci_verified') is True and blocked.get('reviewed_sha')),
        'passing_pr_remote_verified': bool(_github_html_url(passed.get('url'), 'pr')
              and passed.get('green_ci_verified') is True and passed.get('reviewed_sha')),
        'tag_commit_bound': bool(git_sha and local_tag_sha and local_tag_sha == git_sha
              and tag.get('sha') == git_sha),
        'tag_specific_remote_ci_verified': bool(_github_html_url(run.get('url'), 'run')
              and run.get('tag') == tag_name and run.get('sha') == local_tag_sha
              and run.get('outcome') in ('BLOCKED', 'RELEASABLE')
              and run.get('verified_by_human') is True),
        'known_p1s_disposed': not p1 and bool(ledger.get('p1_findings')),
        'mandatory_integrations_verified': not unverified and bool(verifications),
        'publication_clearance_approved': bool(supplied.get('publication_clearance') is True),
        'platform_submission_verified': bool(submission.get('completed') is True
              and isinstance(submission.get('submitted_at'), str)
              and isinstance(submission.get('confirmation_reference'), str)
              and submission['confirmation_reference']),
    }
    outcome = 'READY_FOR_INDEPENDENT_REVIEW' if all(checks.values()) else 'BLOCKED'
    return {
        'schema_version': 1, 'status': outcome,
        'checks': checks,
        'document_count': len(REQUIRED), 'missing_documents': missing_files,
        'broken_relative_markdown_links': links,
        'unresolved_p1_ids': [f.get('id') for f in p1],
        'unverified_mandatory_integrations': unverified,
        'git_head_sha': git_sha,
        'candidate_tag': ledger.get('candidate_tag'),
        'warnings': [
            'Static inspection does not replace independent GitHub/browser/DB verification.',
            'User-supplied URLs/statuses are declarations and must be checked against GitHub by a human.',
            'This preflight does not scan historic Git blobs, grant publication approval, or submit anything.'
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', default='.', help='root of candidate workspace')
    parser.add_argument('--manifest', default='assessment/submission-evidence.json')
    parser.add_argument('--output', default=None)
    args = parser.parse_args()
    repo = Path(args.repo).resolve()
    manifest = Path(args.manifest)
    if not manifest.is_absolute():
        manifest = repo / manifest
    result = run_preflight(repo, manifest)
    text = json.dumps(result, indent=2) + '\n'
    if args.output:
        target = Path(args.output)
        if not target.is_absolute():
            target = repo / target
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding='utf-8')
    print(text, end='')
    return 0 if result['status'] == 'READY_FOR_INDEPENDENT_REVIEW' else 1


if __name__ == '__main__':
    raise SystemExit(main())
