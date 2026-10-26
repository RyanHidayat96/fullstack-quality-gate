#!/usr/bin/env python3
"""Fail-closed, tag-specific release verdict using CI results + reviewed risk inventory.

This is a release policy check, not a substitute for an actual CI run,
release-owner signoff or verification of remote PR links.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

TAG = re.compile(r'^refs/tags/v\d+\.\d+\.\d+(?:-[A-Za-z0-9][A-Za-z0-9.-]*)?$')
SHA = re.compile(r'^[0-9a-f]{40}$')
REQUIRED_JOBS = ('policy-unit', 'api-contract', 'api-critical', 'web-quality', 'quality-summary')
EVIDENCE_KEYS = (
    'api_db_integration', 'frontend_build', 'component_regression',
    'browser_api_db_journey', 'traceability_complete',
    'spec_acceptance_approved', 'publication_clearance',
    'two_real_pr_demonstrations', 'release_owner_signoff',
)
ACTIVE = {'OPEN', 'CODE_FIXED_UNVERIFIED', 'UNVERIFIED'}
CLOSED = {'VERIFIED_FIXED', 'ACCEPTED_RISK'}


def audit_p1_states(text: str) -> dict[str, str]:
    states = {}
    for line in text.splitlines():
        match = re.match(r'^\|\s*\d+\s*·\s*(FIND-\d+)\s*\|\s*\*\*P1\*\*\s*\|', line)
        if not match:
            continue
        columns = [c.strip() for c in line.split('|')]
        if len(columns) < 9:
            raise ValueError(f'incomplete audit row for {match.group(1)}')
        key = match.group(1)
        if key in states:
            raise ValueError(f'duplicate P1 finding: {key}')
        states[key] = columns[6].replace('`', '')
    if not states:
        raise ValueError('no P1 finding index detected: fail closed, do not assume zero')
    return states


def check_evidence_file(root: Path, value: str) -> bool:
    if not isinstance(value, str) or not value or value.startswith(('/', 'https:', 'http:')):
        return False
    try:
        path = (root / value).resolve(strict=True)
        path.relative_to(root.resolve())
        return path.is_file() and path.stat().st_size > 0 and not (root / value).is_symlink()
    except (OSError, ValueError):
        return False


def evaluate(root: Path, ref: str, commit: str, results: dict[str, str], tag_binding: str = 'unverified') -> dict:
    failures: list[str] = []
    risk_summary = []
    if not TAG.fullmatch(ref or ''):
        failures.append('Release tag not verified (expected refs/tags/vX.Y.Z[-suffix])')
    if not SHA.fullmatch(commit or '') or set(commit) == {'0'}:
        failures.append('Release commit SHA is missing or invalid')
    if tag_binding != 'verified':
        failures.append('Tag-to-commit binding not verified against git ref')

    for job in REQUIRED_JOBS:
        if results.get(job, 'missing') != 'success':
            failures.append(f'Required CI job {job} not successful: {results.get(job, "missing")}')
    if results.get('pr-inputs', 'missing') != 'skipped':
        failures.append(f'Non-PR release must skip pr-inputs: {results.get("pr-inputs", "missing")}')

    try:
        audited = audit_p1_states((root / 'assessment/01-audit.md').read_text(encoding='utf-8'))
    except (OSError, UnicodeError, ValueError) as exc:
        audited = {}
        failures.append(f'Unable to verify severity-ranked audit: {exc}')

    try:
        controls = json.loads((root / 'assessment/release-readiness.json').read_text(encoding='utf-8'))
        if not isinstance(controls, dict) or controls.get('schema_version') != 1:
            raise ValueError('unsupported readiness schema')
    except (OSError, UnicodeError, ValueError) as exc:
        controls = {}
        failures.append(f'Unable to verify release readiness: {exc}')

    if controls:
        if ref and TAG.fullmatch(ref) and controls.get('candidate_tag') != ref.removeprefix('refs/tags/'):
            failures.append('Readiness candidate_tag does not match the actual triggering tag')
        risks = controls.get('p1_findings', [])
        if not isinstance(risks, list) or any(not isinstance(r, dict) for r in risks):
            failures.append('Invalid P1 register')
            risks = []
        by_id = {r.get('id'): r for r in risks}
        if len(risks) != len(by_id):
            failures.append('Duplicate P1 IDs in readiness register')
        if set(by_id) != set(audited):
            failures.append(f'P1 register/audit disagreement: register={sorted(by_id)}, audit={sorted(audited)}')
        for identifier in sorted(set(by_id) | set(audited)):
            risk = by_id.get(identifier, {})
            state = risk.get('state')
            risk_summary.append({'id': identifier, 'state': state or 'MISSING'})
            if state != audited.get(identifier):
                failures.append(f'{identifier}: risk state differs from audit index ({state} vs {audited.get(identifier)})')
            if state not in CLOSED:
                failures.append(f'{identifier}: P1 not closed/accepted ({state or "missing"})')
                continue
            evidence = risk.get('evidence_paths', [])
            if not isinstance(evidence, list) or not evidence or any(not check_evidence_file(root, p) for p in evidence):
                failures.append(f'{identifier}: no valid repository-local evidence for disposition')
            if state == 'ACCEPTED_RISK':
                approval = risk.get('risk_acceptance') or {}
                required = ('owner', 'approver', 'mitigation', 'approval_evidence', 'review_by')
                if any(not isinstance(approval.get(k), str) or len(approval[k].strip()) < 4 for k in required):
                    failures.append(f'{identifier}: incomplete named risk acceptance')
                elif not check_evidence_file(root, approval['approval_evidence']):
                    failures.append(f'{identifier}: risk approval evidence unavailable')

        controls_gates = controls.get('mandatory_verifications', {})
        if not isinstance(controls_gates, dict):
            controls_gates = {}
            failures.append('Invalid mandatory verification ledger')
        for check in EVIDENCE_KEYS:
            record = controls_gates.get(check) or {}
            status = record.get('status') if isinstance(record, dict) else None
            evidence = record.get('evidence_paths', []) if isinstance(record, dict) else []
            if status != 'VERIFIED' or not isinstance(evidence, list) or not evidence or any(
                not check_evidence_file(root, p) for p in evidence
            ):
                failures.append(f'{check}: mandatory evidence not VERIFIED with local file references')

    verdict = 'RELEASABLE' if not failures else 'BLOCKED'
    return {
        'release_status': verdict,
        'decision': 'SHIP' if verdict == 'RELEASABLE' else 'DO_NOT_SHIP',
        'ref': ref or 'NOT_TAGGED',
        'commit_sha': commit or 'NOT_AVAILABLE',
        'ci_checks': {k: results.get(k, 'missing') for k in (*REQUIRED_JOBS, 'pr-inputs')},
        'tag_binding': tag_binding,
        'p1_risks': risk_summary,
        'blockers': failures,
        'scope': 'tag-specific CI result and repository-authored readiness policy; human approval still required',
    }


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[1])
    p.add_argument('--ref', default=os.getenv('GITHUB_REF', ''))
    p.add_argument('--sha', default=os.getenv('GITHUB_SHA', ''))
    p.add_argument('--output', type=Path)
    args = p.parse_args(argv)
    results = {k: os.getenv('RELEASE_JOB_' + k.upper().replace('-', '_'), 'missing') for k in (*REQUIRED_JOBS, 'pr-inputs')}
    verdict = evaluate(args.repo, args.ref, args.sha, results, os.getenv('RELEASE_TAG_BINDING', 'unverified'))
    print(json.dumps(verdict, indent=2))
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(verdict, indent=2) + '\n', encoding='utf-8')
    summary = os.getenv('GITHUB_STEP_SUMMARY', '')
    if summary:
        with open(summary, 'a', encoding='utf-8') as fh:
            fh.write(f"## Release: {verdict['release_status']}\n\n")
            fh.write(f"Tag: `{verdict['ref']}` · commit: `{verdict['commit_sha']}`\n\n")
            fh.write(f"Decision: **{verdict['decision']}**\n\n")
            fh.write(f"Blocking reasons ({len(verdict['blockers'])}):\n")
            for reason in verdict['blockers']:
                fh.write(f'- {reason}\n')
    return 0 if verdict['release_status'] == 'RELEASABLE' else 1


if __name__ == '__main__':
    sys.exit(main())
