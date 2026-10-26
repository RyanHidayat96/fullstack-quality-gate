#!/usr/bin/env python3
"""Fail-closed, stdlib-only PR Definition-of-Ready validator.

Untrusted PR bodies and checked-out repository files are never executed.
The validator proves structural traceability and changed-test presence only;
semantic acceptance and branch-protection are independent review duties.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

FIELDS = ("Spec", "Acceptance", "Design", "Findings", "Tests", "Risk", "Affected paths", "Exemption", "Justification")
INPUTS = {
    "Spec": ("assessment/requirements/", "REQ-", "Requirement ID"),
    "Acceptance": ("assessment/criteria/", "AC-", "Acceptance ID"),
    "Design": ("assessment/designs/", "DES-", "Design ID"),
}
REJECT_VALUES = {"", "n/a", "na", "none", "todo", "tbd", "-", "null", "unknown", "..."}
TEST_RE = re.compile(r"(?:^api/spec/.+_spec\.rb$|^web/.+\.(?:test|spec)\.(?:[jt]sx?|[cm]js)$|^scripts/test_[^/]+\.py$|^api/test/[^/]+\.rb$)")
FIELD_RE = re.compile(r"^\s*(?:[-*]\s*)?(Spec|Acceptance|Design|Findings|Tests|Risk|Affected paths|Exemption|Justification)\s*:\s*(.*?)\s*$", re.I)
IDENT_RE = re.compile(r"^[A-Z]+(?:-[A-Z0-9]+)+$")
DOC_FIELDS = {
    "Spec": ["Requirement ID", "Status", "Source", "Problem / affected actor", "Expected behavior / business rule", "In scope / out of scope", "Owner", "Unknowns / assumptions"],
    "Acceptance": ["Acceptance ID", "Requirement", "Test IDs", "Given", "When", "Then", "Negative/boundary scenario"],
    "Design": ["Design ID", "Requirement", "Acceptance IDs", "Planned test IDs", "Affected layers", "Proposed solution", "Data migration / backwards compatibility", "Alternatives and trade-offs", "Failure handling and rollback", "Risks and open questions"],
}

class GateError(Exception):
    pass


def invalid(value: str) -> bool:
    v = value.strip().strip("`'").strip('"').strip().lower()
    return v in REJECT_VALUES or v.startswith(("todo ", "tbd ", "placeholder", "<"))


def parse_fields(body: str) -> dict[str, str]:
    result = {}
    for line in body.splitlines():
        match = FIELD_RE.match(line)
        if not match:
            continue
        canonical = next(k for k in FIELDS if k.lower() == match.group(1).lower())
        if canonical in result:
            raise GateError(f"duplicate PR field: {canonical}")
        result[canonical] = match.group(2).strip()
    return result


def safe_path(root: Path, value: str, prefix: str) -> tuple[Path, str]:
    value = value.strip().strip('`')
    if invalid(value) or not value.startswith(prefix) or not value.endswith(".md"):
        raise GateError(f"invalid linked document path ({prefix}*.md)")
    if any(c in value for c in ('*', '?', '\\', '%', '\x00', ' ', '#')) or '..' in Path(value).parts or Path(value).is_absolute():
        raise GateError("unsafe linked document path")
    candidate = root / value
    if candidate.is_symlink():
        raise GateError("linked document may not be a symlink")
    if not candidate.resolve().is_relative_to(root.resolve()) or not candidate.is_file():
        raise GateError(f"linked document missing or escapes checkout: {value}")
    if candidate.stat().st_size > 32_768:
        raise GateError("linked document too large")
    return candidate, value


def document_data(path: Path, field: str) -> dict[str, str]:
    try:
        s = path.read_text(encoding="utf-8", errors="strict")
    except (UnicodeError, OSError) as e:
        raise GateError(f"invalid UTF-8 document {path.name}: {type(e).__name__}") from e
    if not s.startswith("# "):
        raise GateError(f"{path.name}: meaningful heading required")
    parsed: dict[str, str] = {}
    for line in s.splitlines():
        m = re.match(r"^\s*[-*]\s*([^:]+):\s*(.*?)\s*$", line)
        if m:
            key, value = m.group(1).strip(), m.group(2).strip()
            if key in parsed:
                raise GateError(f"{path.name}: duplicate key {key}")
            parsed[key] = value
    for key in DOC_FIELDS[field]:
        if key not in parsed or invalid(parsed[key]) or len(parsed[key].strip()) < 3:
            raise GateError(f"{path.name}: {key} is missing or placeholder")
    return parsed


def changed_files(root: Path, base: str, head: str) -> list[str]:
    for sha in (base, head):
        if not re.fullmatch(r"[0-9a-fA-F]{40}", sha):
            raise GateError("expected exact 40-digit base/head SHA")
    cmd = ["git", "-C", str(root), "diff", "--name-only", "--diff-filter=ACDMRT", "-z", base, head, "--"]
    r = subprocess.run(cmd, capture_output=True, check=False)
    if r.returncode:
        raise GateError("cannot calculate verified git change set")
    return sorted(set(p.decode("utf-8") for p in r.stdout.split(b"\0") if p))


def classify(path: str) -> str:
    if path.endswith(('.md', '.txt')) and (path.startswith('assessment/') or path in ('README.md',)):
        return "docs"
    if path.startswith('assessment/evidence/'):
        return "evidence"
    return "code"


def load_catalog(root: Path) -> tuple[dict[str, dict], set[str]]:
    try:
        data = json.loads((root / "assessment/design/phase-3-test-catalog.json").read_text(encoding="utf8"))
        findings = {f["finding"]: f for f in data["findings"]}
        tests = {t["id"] for f in data["findings"] for t in f["tests"]}
        if not findings or not tests:
            raise ValueError("empty catalog")
        return findings, tests
    except (KeyError, ValueError, OSError, TypeError) as e:
        raise GateError("missing/malformed approved baseline test catalog") from e


def validate(root: Path, body: str, changed: list[str]) -> dict:
    """One code-changing PR requires freshly changed test artifacts and linked inputs."""
    root = root.resolve()
    if not root.is_dir() or not (root / "assessment/design/phase-3-test-catalog.json").is_file():
        raise GateError("not the expected repository checkout")
    if not changed or len(changed) > 1000:
        raise GateError("empty or oversized change set")
    for name in changed:
        if Path(name).is_absolute() or '..' in Path(name).parts or '\x00' in name:
            raise GateError("invalid changed path")
    fields = parse_fields(body)
    impacted = [p for p in changed if classify(p) == 'code']
    if not impacted:
        # Deliberately narrow exemption; no CI policy or source changes allowed.
        if fields.get('Exemption', '').strip() != "DOCS_ONLY" or invalid(fields.get('Justification', '')):
            raise GateError("documentation-only PR requires explicit DOCS_ONLY justification")
        for name in changed:
            if not (root / name).is_file() or (root / name).is_symlink():
                raise GateError("documentation path missing or unsafe")
            if name.startswith(('assessment/requirements/', 'assessment/criteria/', 'assessment/designs/')):
                kind = next((k for k, (prefix, _, __) in INPUTS.items() if name.startswith(prefix)), None)
                if kind:
                    document_data(root/name, kind)
        return {"result": "METADATA_PASS", "scope": "DOCS_ONLY", "affected": changed, "human_review_required": True}

    for key in ("Spec", "Acceptance", "Design", "Tests", "Risk", "Affected paths"):
        if key not in fields or invalid(fields[key]):
            raise GateError(f"required PR field missing/placeholder: {key}")
    if fields["Risk"] not in {"high", "medium", "low"}:
        raise GateError("Risk must be high, medium or low")
    if fields.get("Exemption", "none") not in ("none", ""):
        raise GateError("code change cannot claim exemption")
    findings, known_tests = load_catalog(root)
    doc_values = {}
    doc_paths = {}
    for field, (prefix, name_prefix, id_key) in INPUTS.items():
        path, relative = safe_path(root, fields[field], prefix)
        d = document_data(path, field)
        doc_id = d[id_key]
        if not doc_id.startswith(name_prefix) or not IDENT_RE.fullmatch(doc_id):
            raise GateError(f"invalid {id_key}")
        if Path(relative).stem != doc_id:
            raise GateError(f"{field} path/name does not match document ID")
        doc_values[field], doc_paths[field] = d, relative
    req = doc_values['Spec']['Requirement ID']
    ac = doc_values['Acceptance']['Acceptance ID']
    if doc_values['Acceptance']['Requirement'] != req or doc_values['Design']['Requirement'] != req:
        raise GateError("requirement IDs do not agree across docs")
    if ac not in split_ids(doc_values['Design']['Acceptance IDs']):
        raise GateError("design references wrong acceptance ID")
    specified = split_ids(fields["Tests"])
    if not specified or not specified.issubset(known_tests):
        raise GateError("PR test IDs missing/unknown in baseline catalog")
    for k in ('Test IDs', 'Planned test IDs'):
        owner = 'Acceptance' if k == 'Test IDs' else 'Design'
        if not specified.issubset(split_ids(doc_values[owner][k])):
            raise GateError(f"PR tests not traceable via {owner}")
    if fields.get("Findings") and not invalid(fields['Findings']):
        claimed = split_ids(fields['Findings'])
        if not claimed.issubset(findings):
            raise GateError("unknown finding ID")
        if not all(findings[f]['requirement'] == req and findings[f]['acceptance'] == ac for f in claimed):
            raise GateError("finding does not match linked documents")
    affected = [x.strip() for x in fields['Affected paths'].split(',')]
    if not affected or len(set(affected)) != len(affected) or any(invalid(p) for p in affected):
        raise GateError("Affected paths must be nonempty, unique changed files")
    if set(affected) != set(impacted):
        raise GateError("Affected paths must enumerate every changed code/test/policy file")
    changed_tests = [name for name in changed if TEST_RE.fullmatch(name)]
    if not changed_tests:
        raise GateError("code change without changed executable test")
    matches = set()
    for path in changed_tests:
        test_path = root / path
        if test_path.is_symlink() or not test_path.is_file() or test_path.stat().st_size > 128_000:
            raise GateError("invalid changed test file")
        content = test_path.read_text(encoding="utf-8")
        for tid in specified:
            if re.search(r'(?<![A-Z0-9-])'+re.escape(tid)+r'(?![A-Z0-9-])', content):
                matches.add(tid)
    if not specified.issubset(matches):
        raise GateError("linked test IDs not present in changed executable test files")
    policy_change = any(p.startswith('.github/') or p.startswith('scripts/validate_pr_inputs') or p.startswith('scripts/test_validate_pr_inputs') for p in impacted)
    if policy_change:
        if fields['Risk'] != 'high' or 'scripts/test_validate_pr_inputs.py' not in changed_tests:
            raise GateError("CI/policy change requires high risk and updated policy fixture tests")
    return {"result": "METADATA_PASS", "scope": "CODE", "affected": impacted,
            "tests": sorted(specified), "linked_documents": doc_paths,
            "human_review_required": True,
            "tests_executed": False}


def split_ids(value: str) -> set[str]:
    parts = [p.strip() for p in value.split(',')]
    if any(not IDENT_RE.fullmatch(p) for p in parts):
        raise GateError("invalid comma-separated identifier list")
    if len(set(parts)) != len(parts) or len(parts) > 40:
        raise GateError("duplicate or excessive identifiers")
    return set(parts)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo', default='.')
    parser.add_argument('--event', help='GitHub pull_request event JSON (read-only)')
    parser.add_argument('--base', help='exact git SHA for trusted base')
    parser.add_argument('--head', help='exact git SHA for checked out PR HEAD')
    parser.add_argument('--body-file', help='local test only, alternate PR body')
    args = parser.parse_args(argv)
    try:
        root = Path(args.repo)
        if args.event:
            event = json.loads(Path(args.event).read_text(encoding='utf-8'))
            pr = event.get('pull_request')
            if not isinstance(pr, dict) or not isinstance(pr.get('body'), (str, type(None))):
                raise GateError('not a valid pull_request event')
            base = pr['base']['sha']
            head = pr['head']['sha']
            if args.base and args.base != base or args.head and args.head != head:
                raise GateError('event base/head differ from supplied SHA')
            body = pr.get('body') or ''
        elif args.base and args.head and args.body_file:
            base, head = args.base, args.head
            body = Path(args.body_file).read_text(encoding='utf-8')
        else:
            raise GateError('require PR event or explicit base/head/body-file')
        head_actual = subprocess.run(['git', '-C', str(root), 'rev-parse', 'HEAD'], capture_output=True, text=True)
        if head_actual.returncode or head_actual.stdout.strip() != head:
            raise GateError('checkout HEAD does not match PR event HEAD')
        payload = validate(root, body, changed_files(root, base, head))
        print(json.dumps(payload, sort_keys=True))
        return 0
    except (GateError, ValueError, KeyError, OSError, UnicodeError) as exc:
        print(json.dumps({'result': 'BLOCKED', 'error': str(exc)}, sort_keys=True), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
