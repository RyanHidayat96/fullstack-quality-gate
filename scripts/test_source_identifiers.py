"""Prevent source-specific identifiers from returning to public application files.

Only checks the current api/ and web/ source tree. Git history, older
assessment evidence, licensing and external screenshots need a separate review.
"""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEXT_EXTENSIONS = {".rb", ".ts", ".tsx", ".js", ".mjs", ".json", ".yml", ".yaml", ".css", ".md", ".txt"}
SKIP_DIRS = {"node_modules", "dist", "coverage", "tmp", "vendor", "log", ".git"}
SOURCE_SPECIFIC_NAME = re.compile(r"rakamin", re.IGNORECASE)


def active_source_identifiers():
    findings = []
    for dirname in ("api", "web"):
        for path in (ROOT / dirname).rglob("*"):
            if not path.is_file() or path.suffix not in TEXT_EXTENSIONS:
                continue
            if any(segment in SKIP_DIRS for segment in path.relative_to(ROOT).parts):
                continue
            try:
                body = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            if SOURCE_SPECIFIC_NAME.search(body):
                findings.append(path.relative_to(ROOT).as_posix())
    return sorted(findings)


class PublicationSourceTests(unittest.TestCase):
    # TEST-GATE-06: source-level confidentiality guard, not a history scan.
    def test_current_application_sources_do_not_include_prohibited_names(self):
        self.assertEqual([], active_source_identifiers(), "Review these application files before publishing")


if __name__ == "__main__":
    unittest.main()
