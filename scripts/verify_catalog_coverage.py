#!/usr/bin/env python3
"""Review every baseline scenario against runnable assertions, without inventing results.

EXECUTABLE means the ID occurs in an actual test declaration with an assertion.
PARTIAL means a runnable assertion exists, but not the full planned integration
boundary. MISSING means no matching executable assertion. Evidence of a passed
CI run is a separate condition; this script cannot impersonate a live run.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "assessment/design/phase-3-test-catalog.json"
TEST_PATTERNS = (
    "api/spec/**/*_spec.rb", "api/spec/**/*_test.rb",
    "web/tests/*.test.mjs", "web/tests/*.test.js",
    "scripts/test_*.py",
)
DECLARATION = re.compile(
    r"""(?mx)
    ^\s*(?:it|specify|test)\s*\(?(?:['"])(?P<title>[^'"\n]+)['"]
    |
    ^\s*def\s+test_(?P<method>[A-Za-z0-9_]+)\b
    """
)
ASSERTION = re.compile(r"\b(?:expect\s*\(|assert(?:_|\.|\s*\()|refute(?:_|\.|\s*\())")
SPECIAL_SCOPE = {
    "SESSION-04": "Only sequential completion demonstrated; real concurrent requests not established.",
    "FITGAP-01": "Model-level fingerprint evidence exists; full HTTP stale-response path not independently exercised.",
    "FITGAP-02": "DB/model staleness check exists; API JSON/PDF parity remains untested.",
    "FITGAP-03": "Concurrent worker and vacancy-update race is not independently verified.",
    "PORTFOLIO-03": "Failed/retry background worker state and partially persisted output need isolated DB tests.",
    "FITGAP-05": "Method-level stable IDs checked; missing full DB custom/blank/case-variant test.",
    "SESSION-03": "Server acknowledgement/coverage DB test exists; real AI completion flow remains out of scope.",
    "WS-AUTH-01": "Middleware helper tested, not a full live upgraded WebSocket with forged role.",
    "WS-AUTH-02": "Middleware helper tested; live socket test is tracked separately.",
    "WS-AUTH-03": "Middleware helper tested; live socket test is tracked separately.",
    "WS-AUTH-04": "Middleware helper tested; live socket test is tracked separately.",
    "TEST-GATE-04": "CI policy fixture cannot establish that an independent human actually reviewed a PR.",
    "RELEASE-GATE-03": "A synthetic releasable fixture cannot replace real cleared risks, tag-specific CI and owner approval.",
}


def extract_tests(path: Path) -> list[tuple[str, bool]]:
    content = path.read_text(encoding="utf-8")
    declarations = list(DECLARATION.finditer(content))
    result = []
    for index, match in enumerate(declarations):
        title = match.group("title")
        method = match.group("method")
        name = title if title is not None else method.replace("_", "-")
        end = declarations[index + 1].start() if index + 1 < len(declarations) else len(content)
        snippet = content[match.end():min(end, match.end() + 2500)]
        result.append((name, bool(ASSERTION.search(snippet))))
    return result


def evidence_index(root: Path) -> dict[str, list[str]]:
    index: dict[str, list[str]] = {}
    for pattern in TEST_PATTERNS:
        for path in root.glob(pattern):
            rel = path.relative_to(root).as_posix()
            for name, has_assertion in extract_tests(path):
                if not has_assertion:
                    continue
                for found in re.findall(r"[A-Z]+(?:-[A-Z0-9]+)+", name):
                    index.setdefault(found, []).append(rel)
    return {id_: sorted(set(paths)) for id_, paths in index.items()}


def build_report(root: Path = ROOT) -> dict:
    catalog = json.loads((root / "assessment/design/phase-3-test-catalog.json").read_text(encoding="utf-8"))
    tests = [dict(finding=f["finding"], **entry) for f in catalog["findings"] for entry in f["tests"]]
    ids = [entry["id"] for entry in tests]
    if len(ids) != 41 or len(set(ids)) != 41:
        raise ValueError(f"Expected exactly 41 distinct baseline scenarios, found {len(ids)}")
    index = evidence_index(root)
    rows = []
    for scenario in tests:
        identifier = scenario["id"]
        paths = index.get(identifier, [])
        if not paths:
            status = "MISSING"
        elif identifier in SPECIAL_SCOPE:
            status = "PARTIAL"
        elif scenario.get("layer", "").startswith("request") and all("regression/" in p for p in paths):
            status = "PARTIAL"
        else:
            status = "EXECUTABLE"
        rows.append({
            "id": identifier,
            "finding": scenario["finding"],
            "planned_layer": scenario["layer"],
            "expected_assertion": scenario["assertion"],
            "status": status,
            "test_paths": paths,
            "limitation": SPECIAL_SCOPE.get(identifier, "") if status != "EXECUTABLE" else "",
        })
    return {
        "schema_version": 1,
        "total": 41,
        "counts": {status: sum(row["status"] == status for row in rows)
                   for status in ("EXECUTABLE", "PARTIAL", "MISSING")},
        "interpretation": "Static traceability of runnable assertions; GitHub Actions outcomes and scenario semantics require independent review.",
        "scenarios": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--require-full-coverage", action="store_true",
                        help="fail closed if any scenario is missing or partial")
    args = parser.parse_args()
    report = build_report()
    output = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(output, encoding="utf-8")
    else:
        print(output, end="")
    print(f"Traceability: {report['total']} scenarios; {report['counts']}")
    return 1 if args.require_full_coverage and (report["counts"]["PARTIAL"] or report["counts"]["MISSING"]) else 0


if __name__ == "__main__":
    raise SystemExit(main())
